import json
import sys
import os
from tqdm import tqdm
from argparse import ArgumentParser


def process_item(item, base_dir):
    task_base_dir = os.path.join(base_dir, item["web_id"])
    os.makedirs(task_base_dir, exist_ok=True)

    with open(os.path.join(task_base_dir, "web.html"), "w") as f:
        f.write(item["code"])

    task_dir = os.path.join(task_base_dir, f"task_{item['task_id']}")
    os.makedirs(task_dir, exist_ok=True)

    metadata = {
        "web_id": item["web_id"],
        "task_id": item["task_id"],
        "task_type": "dynamic",
        "instruction": f"Task: {item['task']}\nExpected Result: {item['expected']}\n\nNote: The task is only considered successful if the expected result is achieved; otherwise, it is deemed infeasible.",
        "max_steps": 15
    }

    with open(os.path.join(task_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, ensure_ascii=False)
    return task_dir


def main(args):
    with open(args.data_path, "r") as f:
        data = [json.loads(line) for line in f]
    webs = {item["web_id"]: [] for item in data}
    for item in tqdm(data):
        task_dir = process_item(item, args.base_dir)
        webs[item["web_id"]].append(task_dir)
    for web_id, task_dirs in webs.items():
        with open(os.path.join(args.base_dir, web_id, "tasks.txt"), "w") as f:
            for task_dir in task_dirs:
                f.write(task_dir + "\n")
    with open("web_unit.txt", "w") as f:
        for web_id, task_dirs in webs.items():
            item_dir = os.path.join(args.base_dir, web_id)
            f.write(item_dir + "\n")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--data_path", type=str, default="webdevjudge_unit/data/webdevjudge_unit.jsonl")
    parser.add_argument("--base_dir", type=str, default="/data/WebDevJudgeUnit_test")
    args = parser.parse_args()
    main(args)