import os
import json
import sys
from argparse import ArgumentParser
from tqdm import tqdm
import concurrent.futures

sys.path.append("./")
from utils.get_response import generate
from utils.basic import extract_and_parse_json

LLM_JUDGE_PROMPT = """You are an expert web developer. Your task is to determine if a given web development task is feasible based on the provided HTML code.

**HTML Code:**
```html
{html_code}
```

**Task Description:**
{task_instruction}

**Expected Result:**
{expected_result}

Based on the code, can the task be completed to achieve the expected result? The result is only achievable if all elements required for the interaction are present in the HTML.

Please begin your response with the analysis. Then provide your answer in the following JSON format. 

```json
{{
  "feasible": <true or false>
}}
```
"""

total_tokens = {
    "prompt_token_count": 0,
    "candidates_token_count": 0,
    "thoughts_token_count": 0
}

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--data_path", type=str, default="webdevjudge_unit/data/webdevjudge_unit.jsonl")
    parser.add_argument("--output_dir", type=str, default="webdevjudge_unit/outputs")
    parser.add_argument("--model", type=str, default="DeepSeek-V3-0324")
    parser.add_argument("--base_dir", type=str, default="/data/WebDevJudgeUnit_test")
    parser.add_argument("--agent", action="store_true")
    parser.add_argument("--path_list", type=str, default="web_unit.txt")
    return parser.parse_args()

def construct_prompt(html_code, task_instruction, expected_result):
    prompt_text = LLM_JUDGE_PROMPT.format(html_code=html_code, task_instruction=task_instruction, expected_result=expected_result)
    return [{"role": "user", "content": prompt_text}]


def process_item(item, model):
    html_code = item["code"]
    task_instruction = item['task']
    expected_result = item['expected']
    web_id = item["web_id"]
    task_id = item['task_id']

    prompt = construct_prompt(html_code, task_instruction, expected_result)
    
    generate_config = {"max_output_tokens": 8192, "temperature": 0.0}
    response = None
    metadata_response = None
    max_retries = 5
    for i in range(max_retries):
        generate_config["temperature"] = 0.0 + 0.1 * i
        response, metadata_response = generate(model=model, messages=prompt, generation_config=generate_config)
        try:
            parsed_response = extract_and_parse_json(response)
            return {
                "web_id": web_id,
                "task_id": task_id,
                "model_response": parsed_response,
                "raw_response": response,
                "metadata": metadata_response
            }
        except Exception as e:
            if i < max_retries - 1:
                print(f"Attempt {i+1} failed to parse JSON for item {web_id}, retrying...")
            else:
                print(f"Item {web_id} failed to parse JSON after {max_retries} attempts.")
                return {
                    "web_id": web_id,
                    "task_id": task_id,
                    "model_response": {"feasible": False, "reasoning": "Failed to parse model output."},
                    "raw_response": response,
                    "metadata": metadata_response
                }

def generate_judge(args):
    with open(args.data_path, "r") as f:
        items = [json.loads(line) for line in f]

    print(f"Processing {len(items)} items")
    os.makedirs(args.output_dir, exist_ok=True)

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=128) as executor:
        future_to_item = {executor.submit(process_item, item, args.model): item for item in items}
        for future in tqdm(concurrent.futures.as_completed(future_to_item), total=len(future_to_item)):
            try:
                result = future.result()
                if result:
                    results.append(result)
                    
                    metadata = result["metadata"]
                    total_tokens["prompt_token_count"] += metadata["prompt_token_count"]
                    total_tokens["candidates_token_count"] += metadata["candidates_token_count"]
                    total_tokens["thoughts_token_count"] += metadata.get("thoughts_token_count", 0)
            except Exception as e:
                print(f"Error processing item: {e}")

    print(f"Total tokens: {total_tokens}")
    output_path = os.path.join(args.output_dir, f"{args.model}_judge.jsonl")
    with open(output_path, "w") as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

def evaluate_llm(args):
    with open(args.data_path, "r") as f:
        items = [json.loads(line) for line in f]
    labels = {f"{item['web_id']}_{item['task_id']}": item["label"] for item in items}

    with open(os.path.join(args.output_dir, f"{args.model}_judge.jsonl"), "r") as f:
        results = [json.loads(line) for line in f]

    res = {}
    for result in results:
        res[f"{result['web_id']}_{result['task_id']}"] = 1 if result["model_response"]["feasible"] else 0
    
    TP = 0
    FP = 0
    TN = 0
    FN = 0
    for key, value in res.items():
        if value == 1 and labels[key] == 1:
            TP += 1
        elif value == 1 and labels[key] == 0:
            FP += 1
        elif value == 0 and labels[key] == 0:
            TN += 1
        elif value == 0 and labels[key] == 1:
            FN += 1
    print(f"TP: {TP}, FP: {FP}, TN: {TN}, FN: {FN}")
    print(f"Precision: {round((TP / (TP + FP)) * 100, 1)}%")
    print(f"Recall: {round((TP / (TP + FN)) * 100, 1)}%")
    print(f"F1-score: {round((2 * TP / (2 * TP + FP + FN)) * 100, 1)}%")
    print(f"Accuracy: {round(((TP + TN) / (TP + TN + FP + FN)) * 100, 1)}%")
    return res

def evaluate_agent(args):
    results_count = {
        "DONE": 0, "FAILED": 0, "PARSING RESPONSE ERROR": 0, "UNRECOGNIZED ACTION TYPE": 0, "SERVER ERROR": 0, "INITIAL_ERROR": 0, "MAX ROUNDS": 0
    }
    path_list = [line.strip() for line in open(args.path_list, "r")]
    res = {}
    for path in tqdm(path_list, desc="Evaluating results"):
        with open(os.path.join(path, "tasks.txt"), "r") as f:
            tasks = [line.strip() for line in f.readlines()]
        for task in tasks:
            with open(os.path.join(task, "messages.json"), "r") as f:
                messages = json.load(f)
            results_count[messages["final_result"]] += 1
            with open(os.path.join(task, "metadata.json"), "r") as f:
                metadata = json.load(f)
            if messages["final_result"] == "DONE":
                res[f"{metadata['web_id']}_{metadata['task_id']}"] = 1
            else:
                res[f"{metadata['web_id']}_{metadata['task_id']}"] = 0
    print(results_count)
    with open(args.data_path, "r") as f:
        items = [json.loads(line) for line in f]
    labels = {f"{item['web_id']}_{item['task_id']}": item["label"] for item in items}
    TP = 0
    FP = 0
    TN = 0
    FN = 0
    for key, value in res.items():
        if value == 1 and labels[key] == 1:
            TP += 1
        elif value == 1 and labels[key] == 0:
            FP += 1
        elif value == 0 and labels[key] == 0:
            TN += 1
        elif value == 0 and labels[key] == 1:
            FN += 1
    print(f"TP: {TP}, FP: {FP}, TN: {TN}, FN: {FN}")
    print(f"Precision: {round((TP / (TP + FP)) * 100, 1)}%")
    print(f"Recall: {round((TP / (TP + FN)) * 100, 1)}%")
    print(f"F1-score: {round((2 * TP / (2 * TP + FP + FN)) * 100, 1)}%")
    print(f"Accuracy: {round(((TP + TN) / (TP + TN + FP + FN)) * 100, 1)}%")

if __name__ == "__main__":
    args = parse_args()
    print("Model: ", args.model)
    print("Output Dir: ", args.output_dir)
    if not args.agent:
        if os.path.exists(os.path.join(args.output_dir, f"{args.model}_judge.jsonl")):
            evaluate_llm(args)
        else:
            generate_judge(args)
            evaluate_llm(args)
    else:
        evaluate_agent(args)