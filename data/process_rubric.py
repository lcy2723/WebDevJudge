import json
import concurrent.futures
from argparse import ArgumentParser
import sys
sys.path.append(".")
from prompts.rubric_generation import RUBRIC_GENERATION_PROMPT
from utils.get_response import generate
from utils.basic import extract_and_parse_json
from tqdm import tqdm


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--model", type=str, default="Qwen3-235B-A22B-Instruct-2507")
    parser.add_argument("--data_path", type=str, default="data/all.jsonl")
    parser.add_argument("--rubric_path", type=str, default="data/rubric.jsonl")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--statistics", action="store_true")
    return parser.parse_args()


def process_rubric(item, model):
    prompt = [{"role": "user", "content": RUBRIC_GENERATION_PROMPT.replace("[INSERT USER QUERY HERE]", item["user_query"])}]
    generate_config = {"max_tokens": 16384, "temperature": 0.0}
    response = None
    metadata = None
    rubric = None
    max_retries = 5
    for i in range(max_retries):
        generate_config["temperature"] = 0.0 + 0.1 * i
        response, metadata = generate(model=model, messages=prompt, generation_config=generate_config)
        try:
            rubric = extract_and_parse_json(response)
            break
        except Exception as e:
            if i < max_retries - 1:
                print(f"Attempt {i+1} failed to parse JSON for item {item.get('question_id', 'unknown')}, retrying...")
            else:
                print(f"Item {item.get('question_id', 'unknown')} failed to parse JSON after {max_retries} attempts. Returning last response.")
    return {
        "question_id": item["question_id"],
        "model_response": response,
        "metadata": metadata,
        "rubric": rubric
    }


def generate_rubrics(args):
    total_tokens = {
        "prompt_token_count": 0,
        "candidates_token_count": 0,
        "thoughts_token_count": 0
    }
    with open(args.data_path, "r") as f:
        data = [json.loads(line) for line in f]
    items = []
    for item in data:
        items.append({
            "question_id": item["question_id"],
            "user_query": " ".join([i["content"][0]["text"] for i in item["conversation_a"] if i["role"] == "user"])
        })
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
        future_to_item = {executor.submit(process_rubric, item, args.model): item for item in items}
        for future in tqdm(concurrent.futures.as_completed(future_to_item), total=len(future_to_item)):
            try:
                result = future.result()
                results.append({
                    "question_id": result["question_id"],
                    "metadata": result["metadata"],
                    "rubric_tree": result["rubric"],
                    "model_response": result["model_response"]
                })
                metadata = result["metadata"]
                total_tokens["prompt_token_count"] += metadata["prompt_token_count"]
                total_tokens["candidates_token_count"] += metadata["candidates_token_count"]
                total_tokens["thoughts_token_count"] += metadata["thoughts_token_count"]
            except Exception as e:
                print(f"Error processing item: {e}")
    print(f"Total tokens: {total_tokens}")
    with open(args.rubric_path, "w") as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")


def verify_json_format(rubrics):
    verified_rubrics = []
    for rubric in rubrics:
        if rubric["rubric_tree"] is not None:
            verified_rubrics.append(rubric)
        else:
            print(f"Error processing {rubric['question_id']}: invalid json format")
    return verified_rubrics


def verify_tree_structure(rubrics):
    def verify_tree_structure_helper(tree_item):
        def _verify_node_structure(node):
            # Each node must be a dictionary with "description" and "children"
            if not isinstance(node, dict) or "description" not in node or "children" not in node:
                return False
            # Description must be a non-empty string
            if not isinstance(node["description"], str) or not node["description"]:
                return False
            # Children must be a list or None
            if node["children"] is not None and not isinstance(node["children"], list):
                return False
            # If it has children, verify them recursively
            if isinstance(node["children"], list):
                for child in node["children"]:
                    if not _verify_node_structure(child):
                        return False
            return True

        # 1. Verify top-level keys
        basic_keys = ['intention', 'static', 'dynamic']
        if sorted(list(tree_item.keys())) != sorted(basic_keys):
            return False

        # 2. Verify structure for each main branch
        for key in basic_keys:
            branch = tree_item[key]
            if not _verify_node_structure(branch):
                return False
            # For top-level branches, 'children' should be a non-empty list
            if not isinstance(branch.get("children"), list) or not branch.get("children"):
                return False

        # 3. Specific checks for 'dynamic' branch
        dynamic_children = tree_item['dynamic']['children']
        if len(dynamic_children) != 2:
            return False

        # It must have exactly two children: one for "basic" interactions and one for "complex" interactions.

        return True

    verified_rubrics = []
    for index, item in enumerate(rubrics):
        if not verify_tree_structure_helper(item['rubric_tree']):
            print(f"Error processing {item['question_id']}: invalid tree structure")
            continue
        else:
            verified_rubrics.append(item)
    return verified_rubrics

def verify_rubrics(args):
    with open(args.rubric_path, "r") as f:
        rubrics = [json.loads(line) for line in f]
    print(f"Verifying json format")
    verified_rubrics = verify_json_format(rubrics)
    print(f"Found {len(verified_rubrics)} verified rubrics")

    print(f"Verifying tree structure")
    verified_rubrics = verify_tree_structure(verified_rubrics)
    print(f"Found {len(verified_rubrics)} verified rubrics")


def statistics(args):
    def _compute_height(tree_item):
        if not isinstance(tree_item, dict) or "children" not in tree_item or tree_item["children"] is None:
            return 1
        
        children = tree_item["children"]
        if not children:
            return 1
        
        return 1 + max(_compute_height(child) for child in children)
    
    def _compute_num_leaves(tree_item):
        # count '"children": null' in the json string
        return json.dumps(tree_item, indent=4).count('\"children\": null')
    
    height_count = []
    num_leaves_count = []
    static_height_count = []
    intention_height_count = []
    dynamic_height_count = []
    static_num_leaves_count = []
    intention_num_leaves_count = []
    dynamic_num_leaves_count = []

    with open(args.rubric_path, "r") as f:
        rubrics = [json.loads(line) for line in f]

    for index, item in enumerate(rubrics):
        num_leaves = _compute_num_leaves(item['rubric_tree'])
        num_leaves_count.append(num_leaves)
        static_height_count.append(_compute_height(item['rubric_tree']['static']))
        intention_height_count.append(_compute_height(item['rubric_tree']['intention']))
        dynamic_height_count.append(_compute_height(item['rubric_tree']['dynamic']))
        height_count.append(1 + max(static_height_count[-1], intention_height_count[-1], dynamic_height_count[-1]))
        static_num_leaves_count.append(_compute_num_leaves(item['rubric_tree']['static']))
        intention_num_leaves_count.append(_compute_num_leaves(item['rubric_tree']['intention']))
        dynamic_num_leaves_count.append(_compute_num_leaves(item['rubric_tree']['dynamic']))

    print("Average height: ", sum(height_count) / len(height_count))
    print("Average intention height: ", sum(intention_height_count) / len(intention_height_count))
    print("Average static height: ", sum(static_height_count) / len(static_height_count))
    print("Average dynamic height: ", sum(dynamic_height_count) / len(dynamic_height_count))

    print("Average num leaves: ", sum(num_leaves_count) / len(num_leaves_count))
    print("Average intention num leaves: ", sum(intention_num_leaves_count) / len(intention_num_leaves_count))
    print("Average static num leaves: ", sum(static_num_leaves_count) / len(static_num_leaves_count))
    print("Average dynamic num leaves: ", sum(dynamic_num_leaves_count) / len(dynamic_num_leaves_count))


if __name__ == "__main__":
    args = parse_args()
    if args.statistics:
        statistics(args)
    else:
        if args.check:
            verify_rubrics(args)
        else:
            generate_rubrics(args)
            verify_rubrics(args)