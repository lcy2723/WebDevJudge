import os
import json
import re
from tqdm import tqdm
import pandas as pd


def compute_cost(path_list):
    total_cost = {
        "prompt_token_count": 0,
        "candidates_token_count": 0,
        "thoughts_token_count": 0
    }
    webs_count = len(path_list)
    tasks_count = 0
    for path in tqdm(path_list, desc="Computing cost"):
        with open(os.path.join(path, "tasks.txt"), "r") as f:
            tasks = [line.strip() for line in f.readlines()]
        tasks_count += len(tasks)
        for task in tasks:
            with open(os.path.join(task, "messages.json"), "r") as f:
                messages = json.load(f)
            total_cost["prompt_token_count"] += messages["costs"]["prompt_token_count"]
            total_cost["candidates_token_count"] += messages["costs"]["candidates_token_count"]
            total_cost["thoughts_token_count"] += messages["costs"]["thoughts_token_count"]
    cost = total_cost["prompt_token_count"] * 3.5 / 1e6 + total_cost["candidates_token_count"] * 12 / 1e6 + total_cost["thoughts_token_count"] * 12 / 1e6
    print(f"Total cost: {cost} CNY")
    print(f"Average cost per web: {cost / webs_count} CNY")
    print(f"Average cost per task: {cost / tasks_count} CNY")


def check_result(path_list):

    def extract_static_elements(text):
        """
        extract the static elements id from the text
        """
        regex = r'\b(?<!\.)\d+(?:\.\d+)*(?![\w\.])'
        if not "finished(content=" in text:
            return ["No matching elements"]
        text = text.split("finished(content=)")[-1]
        elements = re.findall(regex, text)
        return elements

    tasks_count = 0
    static_error_count = 0
    results_count = {
        "intention": {
            "DONE": 0, "FAILED": 0, "PARSING RESPONSE ERROR": 0, "UNRECOGNIZED ACTION TYPE": 0, "SERVER ERROR": 0, "INITIAL_ERROR": 0, "MAX ROUNDS": 0
        },
        "static": {
            "DONE": 0, "FAILED": 0, "PARSING RESPONSE ERROR": 0, "UNRECOGNIZED ACTION TYPE": 0, "SERVER ERROR": 0, "INITIAL_ERROR": 0, "MAX ROUNDS": 0
        },
        "dynamic": {
            "basic": {
                "DONE": 0, "FAILED": 0, "PARSING RESPONSE ERROR": 0, "UNRECOGNIZED ACTION TYPE": 0, "SERVER ERROR": 0, "INITIAL_ERROR": 0, "MAX ROUNDS": 0
            },
            "complex": {
                "DONE": 0, "FAILED": 0, "PARSING RESPONSE ERROR": 0, "UNRECOGNIZED ACTION TYPE": 0, "SERVER ERROR": 0, "INITIAL_ERROR": 0, "MAX ROUNDS": 0
            }
        }
    }
    response_error_type = ["UNRECOGNIZED ACTION TYPE", "PARSING RESPONSE ERROR"]
    for path in tqdm(path_list, desc="Checking result"):
        dynamic_count = {
            "basic": 0,
            "complex": 0
        }
        intention_count = 0
        static_elements_list = []
        result_count = {
            "intention": {
                "DONE": 0, "FAILED": 0, "PARSING RESPONSE ERROR": 0, "UNRECOGNIZED ACTION TYPE": 0, "SERVER ERROR": 0, "INITIAL_ERROR": 0, "MAX ROUNDS": 0
            },
            "static": {
                "DONE": 0, "FAILED": 0, "PARSING RESPONSE ERROR": 0, "UNRECOGNIZED ACTION TYPE": 0, "SERVER ERROR": 0, "INITIAL_ERROR": 0, "MAX ROUNDS": 0
            },
            "dynamic": {
                "basic": {
                    "DONE": 0, "FAILED": 0, "PARSING RESPONSE ERROR": 0, "UNRECOGNIZED ACTION TYPE": 0, "SERVER ERROR": 0, "INITIAL_ERROR": 0, "MAX ROUNDS": 0
                },
                "complex": {
                    "DONE": 0, "FAILED": 0, "PARSING RESPONSE ERROR": 0, "UNRECOGNIZED ACTION TYPE": 0, "SERVER ERROR": 0, "INITIAL_ERROR": 0, "MAX ROUNDS": 0
                }
            }
        }
        with open(os.path.join(path, "tasks.txt"), "r") as f:
            tasks = [line.strip() for line in f.readlines()]
        tasks_count += len(tasks)
        for task in tasks:
            with open(os.path.join(task, "messages.json"), "r") as f:
                messages = json.load(f)
            # dynamic checking
            if "intention" in task:
                if messages["final_result"] == "DONE":
                    intention_count += 1
                result_count["intention"][messages["final_result"]] += 1
            elif "dynamic" in task:
                if messages["final_result"] == "DONE":
                    if "basic" in task:
                        dynamic_count["basic"] += 1
                        result_count["dynamic"]["basic"]["DONE"] += 1
                    else:
                        dynamic_count["complex"] += 1
                        result_count["dynamic"]["complex"]["DONE"] += 1
                else:
                    if "basic" in task:
                        result_count["dynamic"]["basic"][messages["final_result"]] += 1
                    else:
                        result_count["dynamic"]["complex"][messages["final_result"]] += 1
            else:
                result_count["static"][messages["final_result"]] += 1
                if messages["final_result"] == "DONE":
                    elements = extract_static_elements(messages["trajectory"][-1]["content"])
                elif messages["final_result"] in response_error_type:
                    elements = extract_static_elements(messages["trajectory"][-1]["content"])
                else:
                    elements = []
                if elements == ["No matching elements"]:
                    static_error_count += 1
                else:
                    static_elements_list.extend(elements)
        with open(os.path.join(path, "result.json"), "w") as f:
            json.dump({"static_elements_list": static_elements_list, "dynamic_count": dynamic_count, "intention_count": intention_count}, f, indent=4)
        for result in result_count["static"]:
            results_count["static"][result] += result_count["static"][result]
        for result in result_count["dynamic"]["basic"]:
            results_count["dynamic"]["basic"][result] += result_count["dynamic"]["basic"][result]
        for result in result_count["dynamic"]["complex"]:
            results_count["dynamic"]["complex"][result] += result_count["dynamic"]["complex"][result]
    # show the results
    print("Total results:")
    print(json.dumps(results_count, indent=4))
    print("Total webs: ", len(path_list))
    print("Total tasks: ", tasks_count)
    print("Total static error: ", static_error_count)


def eval_results(data_path, result_dir, path_list_path, do_check=False):
    def processing_static_ref(static):
        """
        return [{"id": "1.1", "leaf": True}, {"id": "1.2", "leaf": True}]
        """
        nodes_info = []
        def traverse(children, prefix=""):
            if not children:
                return
            
            for i, node in enumerate(children):
                numbering = f"{prefix}{i + 1}"
                has_children = node.get("children") and len(node.get("children", [])) > 0
                
                nodes_info.append({"id": numbering, "leaf": not has_children})

                if has_children:
                    traverse(node["children"], prefix=f"{numbering}.")
        
        if "children" in static and static["children"]:
            traverse(static["children"])

        return nodes_info
    
    with open(path_list_path, "r") as f:
        path_list = [line.strip() for line in f.readlines()]

    with open(data_path, "r") as f:
        labels = [json.loads(line.strip()) for line in f.readlines()]
    labels = {item["question_id"]: item["label"] for item in labels}
    if do_check:
        check_result(path_list)
    label_column = []
    pred_column = []
    id_column = []
    for ques_id in tqdm(labels, desc="Evaluating results"):
        label_column.append(labels[ques_id])
        id_column.append(ques_id)
        with open(os.path.join(result_dir, ques_id, "metadata.json"), "r") as f:
            metadata = json.load(f)
        static_ref = processing_static_ref(metadata["rubric"]["static"])
        leaf_list = [node["id"] for node in static_ref if node["leaf"]]
        static_ref_list = [node["id"] for node in static_ref]
        score = {"a": {"static": 0, "dynamic": 0}, "b": {"static": 0, "dynamic": 0}}
        for model in ["a", "b"]:
            with open(os.path.join(result_dir, ques_id, model, "result.json"), "r") as f:
                result = json.load(f)
            static_elements_list = result["static_elements_list"]
            static_score = len(set(static_elements_list) & set(static_ref_list))
            dynamic_score = result["dynamic_count"]["basic"] + 2 * result["dynamic_count"]["complex"]
            score[model]["static"] = static_score
            score[model]["dynamic"] = dynamic_score
            score[model]["intention"] = result["intention_count"]
        metadata["score"] = score

        intention_score_a = score["a"]["intention"] / metadata["intention"]
        intention_score_b = score["b"]["intention"] / metadata["intention"]
        if metadata["intention"] > 0:
            static_score_a = score["a"]["static"] / len(static_ref_list)
            static_score_b = score["b"]["static"] / len(static_ref_list)
        else:
            static_score_a, static_score_b = 0, 0
        if metadata["dynamic"] > 0:
            dynamic_score_a = score["a"]["dynamic"] / metadata["dynamic"]
            dynamic_score_b = score["b"]["dynamic"] / metadata["dynamic"]
        else:
            dynamic_score_a, dynamic_score_b = 0, 0

        weight = [1, 1, 1]
        score_a = intention_score_a * weight[0] + static_score_a * weight[1] + dynamic_score_a * weight[2]
        score_b = intention_score_b * weight[0] + static_score_b * weight[1] + dynamic_score_b * weight[2]
        
        threshold = 0
        if score_a > score_b + threshold:
            pred_column.append("model_a")
        elif score_b > score_a + threshold:
            pred_column.append("model_b")
        else:
            pred_column.append("tie")
    df = pd.DataFrame({"label": label_column, "pred": pred_column, "question_id": id_column})
    print(df["pred"].value_counts())
    os.makedirs("results", exist_ok=True)
    df.to_csv(f"results/uitars_results_single.csv", index=False)
    accuracy = df[df["label"] == df["pred"]].shape[0] / df.shape[0]
    print(f"Accuracy: {accuracy}")
