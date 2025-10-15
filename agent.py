from argparse import ArgumentParser
from evaluator.gui_prepare import main as process_data
from evaluator.gui_eval import eval_results as eval_data


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--base_dir", type=str, default="/data/WebDevJudge_test")
    parser.add_argument("--data_path", type=str, default="data/all.jsonl")
    parser.add_argument("--rubric_path", type=str, default="data/rubric.jsonl")
    parser.add_argument("--path_list", type=str, default="webs.txt")
    parser.add_argument("--add_rubric", action="store_true")
    parser.add_argument("--do_process", action="store_true")
    parser.add_argument("--do_eval", action="store_true")
    return parser.parse_args()

def run_exp(args):
    if args.do_process:
        process_data(args)
    elif args.do_eval:
        eval_data(args.data_path, args.base_dir, args.path_list, do_check=True)
    else:
        print("Please specify --do_process or --do_eval")

if __name__ == "__main__":
    args = parse_args()
    run_exp(args)