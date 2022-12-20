import os
import numpy as np
import random
import csv
import argparse


def fetch_data_files(path, extension='.csv'):
    files = [ f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith(extension) ]
    return files


def load_data_file(data_file):
    with open(data_file, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)

    return data
        

def randomize_data_file(data_files, size=1, weigths=None):
    weights = [(1. / len(data_files))] * len(data_files) if not weigths else weigths
    draw = list(np.random.choice(data_files, size=size, p=weights))
    return draw


def randomize_example(data_file, size=1, cache={}):
    if data_file not in cache: 
        cache[data_file] = load_data_file(data_file)
        
    data = cache[data_file]
    
    examples = []
    for _ in range(size):
        example = random.choice(data)
        examples.add(example)
        
    return examples


def generate_examples(path, size):
    data_files = fetch_data_files(path)
    example_data_files = randomize_data_file(data_files, size=size)
    
    examples = []
    cache = {}
    for data_file in example_data_files:
        examples += randomize_example(data_file, cache=cache)
        
    return examples
        
    
def main(path, outputfile):
    examples = generate_examples(path)
    print(examples)
                        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate examples from dataset files')
    parser.add_argument('--path', type=str, help='dataset path', default='/Users/asaf/Downloads/TOPv2_Dataset/*.tsv')
    parser.add_argument('--size', type=int, help='sample size', default=2)
    parser.add_argument('--outputfile', type=str, help='dataset path', default='./examples.tsv')
    args = parser.parse_args()
    
    main(path=args.path, size=args.size, outputfile=args.outputfile)
