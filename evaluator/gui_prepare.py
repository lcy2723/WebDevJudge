import os
import json
from tqdm import tqdm
from prompts.agent_prompt import STATIC_CHECKING_PROMPT, INTENTION_CHECKING_PROMPT

def static2prompt(rubric, max_lines=10):
    """
    convert rubric to id based prompt for better processing.
    If the total lines exceed max_lines, it will be split into multiple prompts.
    The split will try to keep the hierarchy.
    """
    def traverse(children, prefix="", indent_level=0):
        lines_with_indent = []
        if not children:
            return []

        for i, node in enumerate(children):
            numbering = f"{prefix}{i + 1}"
            has_children = node.get("children") and len(node.get("children", [])) > 0
            
            indent = "    " * indent_level
            line = f"{indent}{numbering}"
            if has_children:
                line += "."
            line += f" {node['description']}"
            lines_with_indent.append((line, indent_level))

            if has_children:
                lines_with_indent.extend(traverse(node["children"], prefix=f"{numbering}.", indent_level=indent_level + 1))
        return lines_with_indent

    top_level_nodes = rubric.get("children", [])
    if not top_level_nodes:
        return [""]

    lines_with_indent = traverse(top_level_nodes)
    
    if len(lines_with_indent) <= max_lines:
        return [STATIC_CHECKING_PROMPT.format(static_elements="\n".join([line for line, indent in lines_with_indent]))]

    prompts = []
    chunk_start_idx = 0
    while chunk_start_idx < len(lines_with_indent):
        chunk_end_idx = min(chunk_start_idx + max_lines, len(lines_with_indent))
        
        if chunk_end_idx < len(lines_with_indent):

            final_chunk_end_idx = chunk_end_idx
            for i in range(chunk_end_idx - 1, chunk_start_idx, -1):
                current_indent = lines_with_indent[i][1]
                prev_indent = lines_with_indent[i-1][1]
                if current_indent <= prev_indent:
                    final_chunk_end_idx = i
                    break
            

            chunk = lines_with_indent[chunk_start_idx:final_chunk_end_idx]
            prompts.append("\n".join([line for line, indent in chunk]))
            chunk_start_idx = final_chunk_end_idx
        else:
            # This is the last chunk.
            chunk = lines_with_indent[chunk_start_idx:chunk_end_idx]
            prompts.append("\n".join([line for line, indent in chunk]))
            chunk_start_idx = chunk_end_idx
            
    return [STATIC_CHECKING_PROMPT.format(static_elements=prompt) for prompt in prompts]


def dynamic2prompt(rubric):
    """return a list of prompts for each dynamic leaf node"""
    leaf_descriptions = []

    def find_leaves(node):
        if node.get("children") is None:
            if 'description' in node:
                leaf_descriptions.append(node['description'])
        else:
            for child in node.get("children", []):
                find_leaves(child)

    find_leaves(rubric)
    return leaf_descriptions

def intention2prompt(rubric):
    """return a list of prompts for each intention leaf node"""
    leaf_descriptions = []
    def find_leaves(node):
        if node.get("children") is None:
            if 'description' in node:
                leaf_descriptions.append(node['description'])
        else:
            for child in node.get("children", []):
                find_leaves(child)
    find_leaves(rubric)
    return [INTENTION_CHECKING_PROMPT.format(intention=intention) for intention in leaf_descriptions]

def process_item(item, rubric, base_dir, add_rubric=True):
    """
    Args:
        item: a dict containing the item information
        rubric: a dict containing the rubric information
        base_dir: a string containing the base directory
    Returns:
        None

    Directory structure:
    base_dir/
        question_id/
            a/
                index.tsx
                intention/
                    part1/
                        metadata.json
                    ...
                static/
                    part1/
                        metadata.json
                    ...
                dynamic/
                    basic/
                        part1/
                            metadata.json
                        ...
                    complex/
                        part1/
                            metadata.json
                        ...
                    ...
                tasks.txt
                metadata.json
            b/
                ... (same structure as a)
    """
    try:
        metadata = {
            "question_id": item["question_id"],
            "model_a": item["model_a"],
            "model_b": item["model_b"],
            "query": " ".join([i['content'][0]["text"] for i in item['conversation_a'] if i['role'] == 'user']),
            "label": item["label"],
            "rubric": rubric,
            "intention": json.dumps(rubric["intention"], indent=4).count('\"children\": null') if rubric else 0,
            "static": json.dumps(rubric["static"], indent=4).count('\"children\": null') if rubric else 0,
            "dynamic": json.dumps(rubric["dynamic"], indent=4).count('\"children\": null') if rubric else 0
        }
    except Exception as e:
        print(e)
        print(item["conversation_a"][0])
        return []
    webs_list = []
    tasks_list = {"a": [], "b": []}
    # Create the directory for the item
    item_dir = os.path.join(base_dir, item["question_id"])
    os.makedirs(item_dir, exist_ok=True)
    # save metadata
    with open(os.path.join(item_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
    # Process model
    for model in ["a", "b"]:
        model_dir = os.path.join(item_dir, model)
        os.makedirs(model_dir, exist_ok=True)
        webs_list.append(model_dir)
        # save code
        code = item[f"conversation_{model}"][-1]["object"]["code"]
        with open(os.path.join(model_dir, "index.tsx"), "w") as f:
            f.write(code)
        # intention can directly check, so all in one file is enough
        if add_rubric:
            os.makedirs(os.path.join(model_dir, "intention"), exist_ok=True)
            intention_parts = intention2prompt(rubric["intention"])
            for (i, part) in enumerate(intention_parts):
                os.makedirs(os.path.join(model_dir, "intention", f"part{i+1}"), exist_ok=True)
                with open(os.path.join(model_dir, "intention", f"part{i+1}", "metadata.json"), "w") as f:
                    json.dump({"instruction": part, "task_type": "intention", "max_steps": 15}, f, indent=4, ensure_ascii=False)
                tasks_list[model].append(os.path.join(model_dir, "intention", f"part{i+1}"))
            # static
            os.makedirs(os.path.join(model_dir, "static"), exist_ok=True)
            static_parts = static2prompt(rubric["static"])
            for (i, part) in enumerate(static_parts):
                os.makedirs(os.path.join(model_dir, "static", f"part{i+1}"), exist_ok=True)
                with open(os.path.join(model_dir, "static", f"part{i+1}", "metadata.json"), "w") as f:
                    json.dump({"instruction": part, "task_type": "static", "max_steps": 6}, f, indent=4, ensure_ascii=False)
                tasks_list[model].append(os.path.join(model_dir, "static", f"part{i+1}"))
            # dynamic
            os.makedirs(os.path.join(model_dir, "dynamic"), exist_ok=True)
            os.makedirs(os.path.join(model_dir, "dynamic", "basic"), exist_ok=True)
            os.makedirs(os.path.join(model_dir, "dynamic", "complex"), exist_ok=True)
            basic_ops = dynamic2prompt(rubric["dynamic"]["children"][0])
            complex_ops = dynamic2prompt(rubric["dynamic"]["children"][1])
            for (i, op) in enumerate(basic_ops):
                os.makedirs(os.path.join(model_dir, "dynamic", "basic", f"part{i+1}"), exist_ok=True)
                with open(os.path.join(model_dir, "dynamic", "basic", f"part{i+1}", "metadata.json"), "w") as f:
                    json.dump({"instruction": op, "task_type": "dynamic", "max_steps": 5}, f, indent=4, ensure_ascii=False)
                tasks_list[model].append(os.path.join(model_dir, "dynamic", "basic", f"part{i+1}"))
            for (i, op) in enumerate(complex_ops):
                os.makedirs(os.path.join(model_dir, "dynamic", "complex", f"part{i+1}"), exist_ok=True)
                with open(os.path.join(model_dir, "dynamic", "complex", f"part{i+1}", "metadata.json"), "w") as f:
                    json.dump({"instruction": op, "task_type": "dynamic", "max_steps": 15}, f, indent=4, ensure_ascii=False)
                tasks_list[model].append(os.path.join(model_dir, "dynamic", "complex", f"part{i+1}"))
            with open(os.path.join(model_dir, "tasks.txt"), "w") as f:
                for task in tasks_list[model]:
                    f.write(task + "\n")
            
    return webs_list
    

def main(args):
    dir_list = []
    os.makedirs(args.base_dir, exist_ok=True)
    with open(args.data_path, "r") as f:
        data = [json.loads(line) for line in f]
    if args.add_rubric:
        with open(args.rubric_path, "r") as f:
            rubric = [json.loads(line) for line in f]
        rubric = {item["question_id"]: item["rubric_tree"] for item in rubric}
        for item in tqdm(data):
            web_list = process_item(item, rubric[item["question_id"]], args.base_dir, args.add_rubric)
            dir_list.extend(web_list)
    else:
        for item in tqdm(data):
            web_list = process_item(item, None, args.base_dir, args.add_rubric)
            dir_list.extend(web_list)
    with open(args.path_list, "w") as f:
        for dir in dir_list:
            f.write(dir + "\n")
