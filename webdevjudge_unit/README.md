# WebDevJudge Unit

Webdevjudge Unit is a task-level benchmark for assessing the capability of evaluators to verify task feasibility. Each instance in the benchmark contains a html code, a task instruction, an expected result, and a label indicating whether the task is feasible.

## Data

The data is available in [data/webdevjudge_unit.jsonl](data/webdevjudge_unit.jsonl).

Each instance is a json object with the following fields:

- `web_id`: web_id
- `task_id`: task_id
- `code`: html_code
- `task`: task_instruction
- `expected`: expected_result
- `label`: feasible or infeasible (1 for feasible, 0 for infeasible)
- `error_type`: error type if the task is infeasible. We provide both Chinese and English error types.
- `error_reason`: error reason if the task is infeasible (some may be None since the reason is trivial), We provide both Chinese and English error reasons.

## Evaluation

Similar to WebDevJudge, we provide two evaluation methods:

### Static Code Evaluation

You can run the following command to evaluate the results:

```bash
# make sure you are in the WebDevJudge directory
cd WebDevJudge
python webdevjudge_unit/eval.py --model <model>
```

The results will be saved in outputs/.

### Agent Evaluation

Before running the agent evaluation, you need to set up the environment described in WebDevJudge (you do not need to setup the next.js server since the code are html-based).

First, you need to run the following command to generate the directories for saving the intermediate results:

```bash
# make sure you are in the WebDevJudge directory
cd WebDevJudge
python webdevjudge_unit/preprocessing.py
```

This will generate the directories for saving the intermediate results and a `web_unit.txt` file. Then you can run the following command to generate the results:

```bash
# make sure you are in the WebDevJudge directory
cd WebDevJudge
bash run_webdevjudge_unit.sh <display_port> <start_line> <end_line>
```

where `<display_port>` is the port of the display you want to use, `<start_line>` and `<end_line>` are the start and end line of the data you want to evaluate (1-indexed, based on the `web_unit.txt` file). You can use the `web_unit.txt` file to specify the data you want to evaluate.

After the generation is complete, you can run the following command to evaluate the results:

```bash
# make sure you are in the WebDevJudge directory
cd WebDevJudge
python webdevjudge_unit/eval.py --agent
```
