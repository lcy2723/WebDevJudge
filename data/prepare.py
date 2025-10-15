import json
from datasets import load_dataset
import pandas as pd


if __name__ == "__main__":
    labels = json.load(open("data/index2label.json"))
    ids = list(labels.keys())
    print("Loading dataset...")
    ds = load_dataset("lmarena-ai/webdev-arena-preference-10k", split="test")
    df = pd.read_csv("data/index2category.csv")
    index2question_id = {i: item["question_id"] for i, item in enumerate(ds)}
    df["question_id"] = df["index"].map(index2question_id)
    df = df.drop(columns=["index"])
    df.to_csv("data/category.csv", index=False)
    with open("data/all.jsonl", "w") as f:
        for i in ids:
            item = ds[int(i)]
            item["label"] = labels[i]
            f.write(json.dumps(item) + "\n")

    print("Done preparing data, category saved to data/category.csv, data saved to data/all.jsonl")