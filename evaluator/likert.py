import json
import os
from tqdm import tqdm
import concurrent.futures
import pandas as pd
from utils.get_response import generate
from utils.basic import encode_image, extract_and_parse_json
from prompts.likert_prompt import LIKERT_PROMPT_SINGLE, LIKERT_PROMPT_PAIR, LIKERT_OUTPUT_SINGLE, LIKERT_OUTPUT_PAIR, INPUT_SINGLE, INPUT_PAIR, CODE_ONLY_INPUT_PAIR, CODE_ONLY_INPUT_SINGLE


def construct_prompt_single(user_query, code, image=None):
    if image is not None:
        content = []
        content.append({"type": "text", "text": LIKERT_PROMPT_SINGLE.format(input_type=INPUT_SINGLE, user_query=user_query, code=code)})
        content.append({"type": "text", "text": "\n\n## Initial State\n"})
        content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encode_image(image)}"}})
        content.append({"type": "text", "text": LIKERT_OUTPUT_SINGLE})
        return [{"role": "user", "content": content}]
    else:
        text_content = LIKERT_PROMPT_SINGLE.format(input_type=CODE_ONLY_INPUT_SINGLE, user_query=user_query, code=code) + LIKERT_OUTPUT_SINGLE
        return [{"role": "user", "content": text_content}]


def construct_prompt_pair(user_query, code_a, code_b, image_a=None, image_b=None):
    if image_a is not None and image_b is not None:
        content = []
        content.append({"type": "text", "text": LIKERT_PROMPT_PAIR.format(input_type=INPUT_PAIR, user_query=user_query, code_a=code_a, code_b=code_b)})
        content.append({"type": "text", "text": "\n\n## Initial State A\n"})
        content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encode_image(image_a)}"}})
        content.append({"type": "text", "text": "\n\n## Initial State B\n"})
        content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encode_image(image_b)}"}})
        content.append({"type": "text", "text": LIKERT_OUTPUT_PAIR})
        return [{"role": "user", "content": content}]
    else:
        text_content = LIKERT_PROMPT_PAIR.format(input_type=CODE_ONLY_INPUT_PAIR, user_query=user_query, code_a=code_a, code_b=code_b) + LIKERT_OUTPUT_PAIR
        return [{"role": "user", "content": text_content}]


def process_item(item, mode="single", with_image=True, model="gpt-4o"):
    generate_config = {"max_tokens": 16384, "temperature": 0.0}
    if mode == "single":
        if with_image:
            prompt = construct_prompt_single(item['user_query'], item['code'], item['image'])
        else:
            prompt = construct_prompt_single(item['user_query'], item['code'])
    else:
        if with_image:
            prompt = construct_prompt_pair(item['user_query'], item['code_a'], item['code_b'], item['image_a'], item['image_b'])
        else:
            prompt = construct_prompt_pair(item['user_query'], item['code_a'], item['code_b'])
    
    response = None
    metadata = None
    max_retries = 5
    for i in range(max_retries):
        generate_config["temperature"] = 0.0 + 0.1 * i
        response, metadata = generate(model=model, messages=prompt, generation_config=generate_config)
        try:
            extract_and_parse_json(response)
            break
        except Exception as e:
            if i < max_retries - 1:
                print(f"Attempt {i+1} failed to parse JSON for item {item.get('question_id', 'unknown')}, retrying...")
            else:
                print(f"Item {item.get('question_id', 'unknown')} failed to parse JSON after {max_retries} attempts. Returning last response.")

    if mode == "pair":
        return {
            "question_id": item['question_id'],
            "model_response": response,
            "metadata": metadata,
        }
    else:
        return {
            "question_id": item['question_id'],
            "model": item['model'],
            "model_response": response,
            "metadata": metadata,
        }


def main(args):
    total_tokens = {
        "prompt_token_count": 0,
        "candidates_token_count": 0,
        "thoughts_token_count": 0
    }
    with open(args.data_path, "r") as f:
        data = [json.loads(line) for line in f]
    items = []
    for item in data:
        if args.mode == "single":
            for model in ["a", "b"]:
                items.append({
                    "question_id": item['question_id'],
                    "model": model,
                    "user_query": " ".join([i['content'][0]["text"] for i in item['conversation_a'] if i['role'] == 'user']),
                    "code": item[f"conversation_{model}"][-1]['object']['code'],
                    "image": os.path.join(args.screenshots_dir, f"{item['question_id']}_{model}.png")
                })
        else:
            items.append({
                "question_id": item['question_id'],
                "user_query": " ".join([i['content'][0]["text"] for i in item['conversation_a'] if i['role'] == 'user']),
                "code_a": item['conversation_a'][-1]['object']['code'],
                "code_b": item['conversation_b'][-1]['object']['code'],
                "image_a": os.path.join(args.screenshots_dir, f"{item['question_id']}_a.png"),
                "image_b": os.path.join(args.screenshots_dir, f"{item['question_id']}_b.png")
            })
    print(f"Processing {len(items)} items")

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
        future_to_item = {executor.submit(process_item, item, args.mode, args.with_image, args.model): item for item in items}
        for future in tqdm(concurrent.futures.as_completed(future_to_item), total=len(future_to_item)):
            try:
                result = future.result()
                results.append(result)
                metadata = result["metadata"]
                total_tokens["prompt_token_count"] += metadata["prompt_token_count"]
                total_tokens["candidates_token_count"] += metadata["candidates_token_count"]
                total_tokens["thoughts_token_count"] += metadata["thoughts_token_count"]
            except Exception as e:
                print(f"Error processing item: {e}")
    print(f"Total tokens: {total_tokens}")
    with open(os.path.join(args.output_dir, f"likert_{args.model}_{args.mode}_{'with_image' if args.with_image else 'no_image'}.jsonl"), "w") as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")


def evaluate(args, threshold=1):
    result_path = os.path.join(args.output_dir, f"likert_{args.model}_{args.mode}_{'with_image' if args.with_image else 'no_image'}.jsonl")
    with open(args.data_path, "r") as f:
        data = [json.loads(line) for line in f]
    labels = {item["question_id"]: item["label"] for item in data}
    with open(result_path, "r") as f:
        results = [json.loads(line) for line in f]
    pred = {}
    error_count = 0
    if args.mode == "pair":
        for result in tqdm(results):
            try:
                response = result["model_response"]
                response = extract_and_parse_json(response)
                score_a = []
                score_b = []
                for key, value in response.items():
                    score_a.append(value["A"])
                    score_b.append(value["B"])
                score_a = sum(score_a)
                score_b = sum(score_b)
                if score_a > score_b + threshold:
                    pred[result["question_id"]] = "model_a"
                elif score_a < score_b - threshold:
                    pred[result["question_id"]] = "model_b"
                else:
                    pred[result["question_id"]] = "tie"
            except Exception as e:
                print(f"Error: {e}")
                pred[result["question_id"]] = "error"
                error_count += 1
                continue
    else:
        for result in tqdm(results):
            try:
                response = result["model_response"]
                response = extract_and_parse_json(response)
                score = []
                for key, value in response.items():
                    score.append(value)
                score = sum(score)

                if result["question_id"] in pred:
                    pred[result["question_id"]][result["model"]] = score
                else:
                    pred[result["question_id"]] = {result["model"]: score}
            except Exception as e:
                print(f"Error: {e}")
                pred[result["question_id"]] = "error"
                error_count += 1
                continue
        for key in pred:
            if pred[key] == "error":
                continue
            else:
                try:
                    if pred[key]["a"] > pred[key]["b"] + threshold:
                        pred[key] = "model_a"
                        
                    elif pred[key]["a"] < pred[key]["b"] - threshold:
                        pred[key] = "model_b"
                    else:
                        pred[key] = "tie"
                except KeyError:
                    print(f"KeyError: {key}")
                    pred[key] = "error"
                    error_count += 1
                    continue
    acc = 0
    a_acc = 0
    a_count = 0
    b_acc = 0
    b_count = 0
    tie_acc = 0
    tie_count = 0
    for key in pred:
        if labels[key] == "model_a":
            a_count += 1
        elif labels[key] == "model_b":
            b_count += 1
        else:
            tie_count += 1
        if pred[key] == labels[key]:
            acc += 1
            if pred[key] == "model_a":
                a_acc += 1
            elif pred[key] == "model_b":
                b_acc += 1
            else:
                tie_acc += 1
    print(f"Accuracy: {acc / len(pred)}")
    balanced_acc = (a_acc / a_count + b_acc / b_count + tie_acc / tie_count) / 3

    label_column = []
    pred_column = []
    id_column = []
    for ques_id in labels:
        label_column.append(labels[ques_id])
        pred_column.append(pred[ques_id])
        id_column.append(ques_id)
    df = pd.DataFrame({"question_id": id_column, "label": label_column, "pred": pred_column})
    if not os.path.exists("results"):
        os.makedirs("results")
    df.to_csv(f"results/likert_{args.model}_{args.mode}_{'with_image' if args.with_image else 'no_image'}.csv", index=False)
    return acc, balanced_acc


