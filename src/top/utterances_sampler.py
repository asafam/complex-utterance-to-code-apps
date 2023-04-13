import glob
import argparse
import numpy as np
from utils.file_utils import read_yaml_file, write_yaml_file
import re
import random
from collections import Counter
import uuid


def get_intent_name(parsed_string):
    text = re.sub(r"\s*\[\s*", " [ ", parsed_string)
    text = re.sub(r"\s*\]\s*", " ] ", text)
    left_sq_brackets = []
    token = text.strip().split()[1]
    if token.startswith("IN:"):
        if len(left_sq_brackets) > 0:
            left_sq_brackets[-1] -= 1
        left_sq_brackets.append(1)
        intent = token[len("IN:") :]
        return intent
    return None


def get_utterances(path, intents_map, max_length=250):
    utterances = {}

    for filename in glob.glob(path):
        with open(filename) as file:
            for idx, line in enumerate(file.readlines()):
                if idx == 0:
                    continue

                _, utterance, semantic_parse = line.strip().split("\t")

                intent_name = get_intent_name(semantic_parse)
                intent = intents_map.get(intent_name)
                if intent is not None and len(utterance) < max_length:
                    utterances[intent] = utterances.get(intent, [])
                    utterances[intent].append(utterance)
    return utterances


def write_output_file(data, filepath):
    # check file extension
    file_ext = filepath.split(".")[-1]

    if file_ext == "yaml" or file_ext == "yml":
        write_yaml_file(data, filepath)
        return
    else:
        with open(filepath, "w") as file:
            for intent in data:
                for slot in data[intent]:
                    file.write(f"{intent}\t{slot}\n")


def main(
    key,
    n,
    k,
    config_file,
    dataset_dir_path,
    outputfile,
    max_length,
    seed=42,
    delimiter="|||",
):
    random.seed(seed)
    intents_sample_config = read_yaml_file(config_file)
    intents = list(intents_sample_config.keys())
    intent_names = []
    for intent in intents:
        intent_names += [
            intent.get("intents") for intent in intents_sample_config.values()
        ]
    weights = [intent.get("weight", 1) for intent in intents_sample_config.values()]

    intents_map = {}
    for intent in intents:
        for intent_name in intents_sample_config[intent].get("intents"):
            intents_map[intent_name] = intent
    utterances = get_utterances(dataset_dir_path, intents_map, max_length=max_length)
    sampled_utterances = []
    # create n tuples of k utterances
    guid = uuid.uuid4().hex
    for i in range(n):
        sampled_intents = random.choices(population=intents, weights=weights, k=k)
        sampled_intents_counts = Counter(sampled_intents)
        # sample one utterance for each intent
        sampled_utterance_tuple = []
        for sampled_intent, sample_count in sampled_intents_counts.items():
            sampled_utterance = random.sample(utterances[sampled_intent], sample_count)
            sampled_utterance_tuple += sampled_utterance
        sampled_utterances.append({"id": f"{guid}.{i}", key: sampled_utterance_tuple})
    # write to file
    write_output_file(sampled_utterances, outputfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract the onthologies from dataset files"
    )
    parser.add_argument(
        "--key",
        type=str,
        help="Key to use for the utterances",
        default="rephrase-utterances",
    )
    parser.add_argument("--k", type=int, help="number of intents to sample", default=3)
    parser.add_argument(
        "--n", type=int, help="number of utterances tuples to generate", default=3
    )
    parser.add_argument(
        "--max-length", type=int, help="max utterance length", default=250
    )
    parser.add_argument("--seed", type=int, help="random seed value", default=42)
    parser.add_argument(
        "--datasetdirpath",
        type=str,
        help="dataset path",
        default="/Users/asaf/Workspace/biu/thesis-swiss-army-knife/data/TOPv2_Dataset/*.tsv",
    )
    parser.add_argument(
        "--configfile",
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

    main(
        args.key,
        args.n,
        args.k,
        max_length=args.max_length,
        seed=args.seed,
        dataset_dir_path=args.datasetdirpath,
        config_file=args.configfile,
        outputfile=args.outputfile,
    )
