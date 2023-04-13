import glob
import argparse
from utils.file_utils import write_yaml_file
import re


def get_onthologies(parsed_string):
    onthologies = {}
    text = re.sub(r"\s*\[\s*", " [ ", parsed_string)
    text = re.sub(r"\s*\]\s*", " ] ", text)
    left_sq_brackets = []
    intents = []
    for token in text.strip().split():
        if token == "[":
            if len(left_sq_brackets) > 0:
                left_sq_brackets[-1] += 1
        elif token == "]":
            left_sq_brackets[-1] -= 1
            if left_sq_brackets[-1] == 0:
                left_sq_brackets.pop()
                intents.pop()
        elif token.startswith("IN:"):
            if len(left_sq_brackets) > 0:
                left_sq_brackets[-1] -= 1
            left_sq_brackets.append(1)
            intent = token[len("IN:") :]
            intents.append(intent)
            onthologies[intent] = onthologies[intent] if intent in onthologies else []
        elif token.startswith("SL:"):
            slot = token[len("SL:") :]
            if slot not in onthologies[intents[-1]]:
                onthologies[intents[-1]].append(slot)
    return onthologies


def extract_onthologies(path):
    onthologies = {}

    for filename in glob.glob(path):
        with open(filename) as file:
            for idx, line in enumerate(file.readlines()):
                if idx == 0:
                    continue

                _, _, semantic_parse = line.strip().split("\t")

                utterance_onthologies = get_onthologies(semantic_parse)
                onthologies = {
                    key: list(
                        set(
                            onthologies.get(key, [])
                            + utterance_onthologies.get(key, [])
                        )
                    )
                    for key in (onthologies.keys() | utterance_onthologies.keys())
                }
    return onthologies


def write_output_file(data, filepath):
    # check file extension
    file_ext = filepath.split(".")[-1]

    if file_ext == "yaml" or file_ext == "yml":
        write_yaml_file(data, filepath)
        return

    with open(filepath, "w") as file:
        for intent in data:
            for slot in data[intent]:
                file.write(f"{intent}\t{slot}\n")


def main(dataset_dir_path, outputfile):
    onthologies = extract_onthologies(dataset_dir_path)
    write_output_file(onthologies, outputfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract the onthologies from dataset files"
    )
    parser.add_argument(
        "--datasetdirpath",
        type=str,
        help="dataset path",
        default="/Users/asaf/Workspace/biu/thesis-swiss-army-knife/data/TOPv2_Dataset/*.tsv",
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        help="dataset path",
        default="./build/onthologies.yaml",
    )
    args = parser.parse_args()

    main(dataset_dir_path=args.datasetdirpath, outputfile=args.outputfile)
