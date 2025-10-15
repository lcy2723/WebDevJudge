import json
import os
from argparse import ArgumentParser
from evaluator.rubric import main as rubric_main
from evaluator.rubric import evaluate_binary as rubric_evaluate
from evaluator.likert import main as likert_main
from evaluator.likert import evaluate as likert_evaluate


def parse_args():
    parser = ArgumentParser()
    # basic settings
    parser.add_argument("--setting", type=str, default="likert", choices=["likert", "rubric"])
    parser.add_argument("--mode", type=str, default="pair", choices=["single", "pair"])
    parser.add_argument("--with_image", action="store_true")
    parser.add_argument("--eval", action="store_true")
    # evaluation settings
    parser.add_argument("--data_path", type=str, default="data/all.jsonl")
    parser.add_argument("--screenshots_dir", type=str, default="data/screenshots")
    parser.add_argument("--output_dir", type=str, default="outputs")
    parser.add_argument("--model", type=str, default="gpt-4.1")
    # for rubric
    parser.add_argument("--rubric_type", type=str, default="combined", choices=["combined", "static", "dynamic", "intention"])
    parser.add_argument("--rubric_path", type=str, default="data/rubric.jsonl")
    return parser.parse_args()


def run_exp(args):
    if args.eval:
        if args.setting == "likert":
            likert_evaluate(args)
        elif args.setting == "rubric":
            rubric_evaluate(args)
        else:
            raise NotImplementedError
    else:
        if args.setting == "likert":
            likert_main(args)
            likert_evaluate(args)
        elif args.setting == "rubric":
            rubric_main(args)
            rubric_evaluate(args)
        else:
            raise NotImplementedError



if __name__ == "__main__":
    args = parse_args()
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    run_exp(args)