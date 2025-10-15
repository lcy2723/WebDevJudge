import json
import os
from tqdm import tqdm
import concurrent.futures
import pandas as pd

from utils.get_response import generate
from utils.basic import encode_image, extract_and_parse_json
from prompts.rubric_prompt import (
    STATIC_PROMPT_SINGLE, STATIC_OUTPUT_SINGLE,
    DYNAMIC_PROMPT_SINGLE, DYNAMIC_OUTPUT_SINGLE,
    INTENT_PROMPT_SINGLE, INTENT_OUTPUT_SINGLE,
    STATIC_PROMPT_PAIR, STATIC_OUTPUT_PAIR,
    DYNAMIC_PROMPT_PAIR, DYNAMIC_OUTPUT_PAIR,
    INTENT_PROMPT_PAIR, INTENT_OUTPUT_PAIR,
    ALL_PROMPT_SINGLE, ALL_OUTPUT_SINGLE,
    ALL_PROMPT_PAIR, ALL_OUTPUT_PAIR,
    INPUT_SINGLE, INPUT_PAIR, CODE_ONLY_INPUT_SINGLE, CODE_ONLY_INPUT_PAIR
)


def construct_prompt_single(user_query, code, rubric, eval_type="combined", image=None):
    if eval_type == "static":
        PROMPT, OUTPUT = STATIC_PROMPT_SINGLE, STATIC_OUTPUT_SINGLE
    elif eval_type == "dynamic":
        PROMPT, OUTPUT = DYNAMIC_PROMPT_SINGLE, DYNAMIC_OUTPUT_SINGLE
    elif eval_type == "intention":
        PROMPT, OUTPUT = INTENT_PROMPT_SINGLE, INTENT_OUTPUT_SINGLE
    else: # combined
        PROMPT, OUTPUT = ALL_PROMPT_SINGLE, ALL_OUTPUT_SINGLE

    if image is not None:
        content = []
        if eval_type != "combined":
            text = OUTPUT.format(rubric=json.dumps(rubric[eval_type], indent=4))
        else:
            text = OUTPUT.format(
                intention_rubric=json.dumps(rubric["intention"], indent=4),
                static_rubric=json.dumps(rubric["static"], indent=4),
                dynamic_rubric=json.dumps(rubric["dynamic"], indent=4)
            )

        content.append({"type": "text", "text": PROMPT.format(input_type=INPUT_SINGLE, user_query=user_query, code=code)})
        content.append({"type": "text", "text": "\n\n## Initial State\n"})
        content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encode_image(image)}"}})
        content.append({"type": "text", "text": text})
        return [{"role": "user", "content": content}]
    else:
        if eval_type != "combined":
            text_content = PROMPT.format(input_type=CODE_ONLY_INPUT_SINGLE, user_query=user_query, code=code) + OUTPUT.format(rubric=json.dumps(rubric[eval_type], indent=4))
        else:
            text_content = PROMPT.format(input_type=CODE_ONLY_INPUT_SINGLE, user_query=user_query, code=code) + OUTPUT.format(
                intention_rubric=json.dumps(rubric["intention"], indent=4),
                static_rubric=json.dumps(rubric["static"], indent=4),
                dynamic_rubric=json.dumps(rubric["dynamic"], indent=4)
            )
        return [{"role": "user", "content": text_content}]

def construct_prompt_pair(user_query, code_a, code_b, rubric, eval_type="combined", image_a=None, image_b=None):
    if eval_type == "static":
        PROMPT, OUTPUT = STATIC_PROMPT_PAIR, STATIC_OUTPUT_PAIR
    elif eval_type == "dynamic":
        PROMPT, OUTPUT = DYNAMIC_PROMPT_PAIR, DYNAMIC_OUTPUT_PAIR
    elif eval_type == "intention":
        PROMPT, OUTPUT = INTENT_PROMPT_PAIR, INTENT_OUTPUT_PAIR
    else: # combined
        PROMPT, OUTPUT = ALL_PROMPT_PAIR, ALL_OUTPUT_PAIR

    if image_a is not None and image_b is not None:
        content = []
        if eval_type != "combined":
            text = OUTPUT.format(rubric=json.dumps(rubric[eval_type], indent=4))
        else:
            text = OUTPUT.format(
                intention_rubric=json.dumps(rubric["intention"], indent=4),
                static_rubric=json.dumps(rubric["static"], indent=4),
                dynamic_rubric=json.dumps(rubric["dynamic"], indent=4)
            )
        content.append({"type": "text", "text": PROMPT.format(input_type=INPUT_PAIR, user_query=user_query, code_a=code_a, code_b=code_b)})
        content.append({"type": "text", "text": "\n\n## Initial State A\n"})
        content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encode_image(image_a)}"}})
        content.append({"type": "text", "text": "\n\n## Initial State B\n"})
        content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encode_image(image_b)}"}})
        content.append({"type": "text", "text": text})
        return [{"role": "user", "content": content}]
    else:
        if eval_type != "combined":
            text_content = PROMPT.format(input_type=CODE_ONLY_INPUT_PAIR, user_query=user_query, code_a=code_a, code_b=code_b) + OUTPUT.format(rubric=json.dumps(rubric[eval_type], indent=4))
        else:
            text_content = PROMPT.format(input_type=CODE_ONLY_INPUT_PAIR, user_query=user_query, code_a=code_a, code_b=code_b) + OUTPUT.format(
                intention_rubric=json.dumps(rubric["intention"], indent=4),
                static_rubric=json.dumps(rubric["static"], indent=4),
                dynamic_rubric=json.dumps(rubric["dynamic"], indent=4)
            )
        return [{"role": "user", "content": text_content}]


def process_item(item, mode="single", with_image=True, eval_type="combined", model="gpt-4o"):
    if mode == "single":
        if with_image:
            prompt = construct_prompt_single(item['user_query'], item['code'], item['rubric'], eval_type, item['image'])
        else:
            prompt = construct_prompt_single(item['user_query'], item['code'], item['rubric'], eval_type)
    else:
        if with_image:
            prompt = construct_prompt_pair(item['user_query'], item['code_a'], item['code_b'], item['rubric'], eval_type, item['image_a'], item['image_b'])
        else:
            prompt = construct_prompt_pair(item['user_query'], item['code_a'], item['code_b'], item['rubric'], eval_type)
    
    response = None
    metadata = None
    max_retries = 5
    for i in range(max_retries):
        response, metadata = generate(model=model, messages=prompt)
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
    with open(args.rubric_path, "r") as f:
        rubrics = [json.loads(line) for line in f]
    rubrics_map = {item['question_id']: item["rubric_tree"] for item in rubrics}
    items = []
    for item in data:
        if args.mode == "single":
            for model in ["a", "b"]:
                items.append({
                    "question_id": item['question_id'],
                    "model": model,
                    "user_query": " ".join([i['content'][0]["text"] for i in item['conversation_a'] if i['role'] == 'user']),
                    "code": item[f"conversation_{model}"][-1]['object']['code'],
                    "image": os.path.join(args.screenshots_dir, f"{item['question_id']}_{model}.png"),
                    "rubric": rubrics_map[item['question_id']]
                })
        else:
            items.append({
                "question_id": item['question_id'],
                "user_query": " ".join([i['content'][0]["text"] for i in item['conversation_a'] if i['role'] == 'user']),
                "code_a": item['conversation_a'][-1]['object']['code'],
                "code_b": item['conversation_b'][-1]['object']['code'],
                "image_a": os.path.join(args.screenshots_dir, f"{item['question_id']}_a.png"),
                "image_b": os.path.join(args.screenshots_dir, f"{item['question_id']}_b.png"),
                "rubric": rubrics_map[item['question_id']]
            })
    print(f"Processing {len(items)} items")

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        future_to_item = {executor.submit(process_item, item, args.mode, args.with_image, args.rubric_type, args.model): item for item in items}
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
    output_filename = f"rubric_{args.model}_{args.mode}_{args.rubric_type}_{'with_image' if args.with_image else 'no_image'}.jsonl"
    with open(os.path.join(args.output_dir, output_filename), "w") as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")


def count_scores_pair(rubric_part):
    a, b = 0, 0
    if isinstance(rubric_part, dict):
        if "value" in rubric_part and isinstance(rubric_part["value"], str):
            if rubric_part["value"] == "A":
                a += 1
            elif rubric_part["value"] == "B":
                b += 1
        if "children" in rubric_part and rubric_part["children"] is not None:
            for child in rubric_part["children"]:
                child_a, child_b = count_scores_pair(child)
                a += child_a
                b += child_b
    return a, b

def count_true_values(rubric_result):
    count = 0
    if isinstance(rubric_result, dict):
        if "value" in rubric_result and rubric_result["value"] is True:
            count += 1
        if "children" in rubric_result and rubric_result["children"] is not None:
            for child in rubric_result["children"]:
                count += count_true_values(child)
    return count



def evaluate_binary(args):
    result_path = os.path.join(args.output_dir, f"rubric_{args.model}_{args.mode}_{args.rubric_type}_{'with_image' if args.with_image else 'no_image'}.jsonl")
    weights = {"intention": 1, "static": 1, "dynamic": 1}
    def count_leaf_nodes(rubric_part):
        return json.dumps(rubric_part, indent=4).count('\"children\": null')


    with open(args.data_path, "r") as f:
        data = [json.loads(line) for line in f]

    with open(args.rubric_path, "r") as f:
        rubrics = [json.loads(line) for line in f]
    rubrics_map = {item['question_id']: item["rubric_tree"] for item in rubrics}

    labels = {item["question_id"]: item["label"] for item in data}
    with open(result_path, "r") as f:
        results = [json.loads(line) for line in f]
    
    pred = {}
    error_count = 0
    
    if args.mode == "pair":
        for result in tqdm(results):
            try:
                response = extract_and_parse_json(result["model_response"])
                score_a = {key: 0 for key in ["intention", "static", "dynamic"]}
                score_b = {key: 0 for key in ["intention", "static", "dynamic"]}
                
                if args.rubric_type == "combined":
                    for key in ["intention", "static", "dynamic"]:
                        if key in response:
                            a,b = count_scores_pair(response[key])
                            score_a[key] += a
                            score_b[key] += b
                        else:
                            print(f"Key {key} not in response for question {result['question_id']}")
                            error_count += 1
                else:
                    a, b = count_scores_pair(response)
                    score_a[args.rubric_type] += a
                    score_b[args.rubric_type] += b


                intention_leaves = count_leaf_nodes(rubrics_map[result["question_id"]]["intention"])
                static_leaves = count_leaf_nodes(rubrics_map[result["question_id"]]["static"])
                dynamic_leaves = count_leaf_nodes(rubrics_map[result["question_id"]]["dynamic"])

                total_score_a = 0
                total_score_b = 0
                # default: combined mode
                if args.rubric_type == "combined":
                    if intention_leaves > 0:
                        total_score_a += score_a["intention"] * weights["intention"] / intention_leaves
                        total_score_b += score_b["intention"] * weights["intention"] / intention_leaves
                    if static_leaves > 0:
                        total_score_a += score_a["static"] * weights["static"] / static_leaves
                        total_score_b += score_b["static"] * weights["static"] / static_leaves
                    if dynamic_leaves > 0:
                        total_score_a += score_a["dynamic"] * weights["dynamic"] / dynamic_leaves
                        total_score_b += score_b["dynamic"] * weights["dynamic"] / dynamic_leaves
                else:
                    total_score_a = score_a[args.rubric_type]
                    total_score_b = score_b[args.rubric_type]

                if total_score_a > total_score_b:
                    pred[result["question_id"]] = "model_a"
                elif total_score_b > total_score_a:
                    pred[result["question_id"]] = "model_b"
                else:
                    pred[result["question_id"]] = "tie"
            except Exception as e:
                print(f"Error: {e}")
                pred[result["question_id"]] = "error"
                error_count += 1
                continue
    else: # single mode
         for result in tqdm(results):
            try:
                response = extract_and_parse_json(result["model_response"])
                score = {key: 0 for key in ["intention", "static", "dynamic"]}
                if args.rubric_type == "combined":
                    for key in ["intention", "static", "dynamic"]:
                        if key in response:
                            score[key] += count_true_values(response[key])
                        else:
                            print(f"Key {key} not in response for question {result['question_id']}")
                            error_count += 1
                else:
                    score = count_true_values(response)
                
                intention_leaves = count_leaf_nodes(rubrics_map[result["question_id"]]["intention"])
                static_leaves = count_leaf_nodes(rubrics_map[result["question_id"]]["static"])
                dynamic_leaves = count_leaf_nodes(rubrics_map[result["question_id"]]["dynamic"])
                # default: combined mode
                total_score = 0
                if args.rubric_type == "combined":
                    if intention_leaves > 0:
                        total_score += score["intention"] * weights["intention"] / intention_leaves
                    if static_leaves > 0:
                        total_score += score["static"] * weights["static"] / static_leaves
                    if dynamic_leaves > 0:
                        total_score += score["dynamic"] * weights["dynamic"] / dynamic_leaves
                else:
                    total_score = score

                if result["question_id"] not in pred:
                    pred[result["question_id"]] = {}
                pred[result["question_id"]][result["model"]] = total_score
            except Exception as e:
                print(f"Error: {e}")
                if result["question_id"] not in pred:
                    pred[result["question_id"]] = {}
                pred[result["question_id"]][result["model"]] = "error"
                error_count += 1
                continue
        
         for qid, scores in pred.items():
            if "a" not in scores or "b" not in scores or scores["a"] == "error" or scores["b"] == "error":
                pred[qid] = "error"
                continue
            if scores["a"] > scores["b"]:
                pred[qid] = "model_a"
            elif scores["b"] > scores["a"]:
                pred[qid] = "model_b"
            else:
                pred[qid] = "tie"

    acc = 0
    a_acc = 0
    a_count = 0
    b_acc = 0
    b_count = 0
    tie_acc = 0
    tie_count = 0
    
    for key in pred:
        if key not in labels: 
            print(f"Question {key} not in labels")
            continue
        if pred[key] == "error":
            continue
        if labels[key] == "model_a": a_count += 1
        elif labels[key] == "model_b": b_count += 1
        else: tie_count += 1
        
        if pred[key] == labels[key]:
            acc += 1
            if pred[key] == "model_a": a_acc += 1
            elif pred[key] == "model_b": b_acc += 1
            else: tie_acc += 1

    print(f"Total evaluated: {len(pred)}, error count: {error_count}")
    print(f"Accuracy: {acc / len(pred) if len(pred) > 0 else 0}")
    balanced_acc = (a_acc / a_count + b_acc / b_count + tie_acc / tie_count) / 3
    label_column = []
    pred_column = []
    id_column = []
    for key in pred:
        label_column.append(labels[key])
        pred_column.append(pred[key])
        id_column.append(key)
    df = pd.DataFrame({"question_id": id_column, "label": label_column, "pred": pred_column})
    if not os.path.exists("results"):
        os.makedirs("results")
    df.to_csv(f"results/rubric_{args.model}_{args.mode}_{args.rubric_type}_{'with_image' if args.with_image else 'no_image'}_binary.csv", index=False)

    return acc, balanced_acc
