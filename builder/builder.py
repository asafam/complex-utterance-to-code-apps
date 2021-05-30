import argparse
import re
import random
from generator import Generator
from expression import Expression

def build_grammar(grammar_file, headers_line=True):
    grammar = dict()
    with open(grammar_file, 'r', encoding='utf8') as f:
        content = f.readlines()
        content = [x.rstrip().split("#")[0] for x in content if x.split("#")[0].strip() != ''] 
        for index, line in enumerate(content):
            if index == 0 and headers_line:
                continue
                
            item = parse_grammar_line(line)
            item['id'] = index
            symbol = item['symbol']
            
            grammar[symbol] = grammar[symbol] if symbol in grammar else []
            grammar[symbol].append(item)
    return grammar


def parse_grammar_line(line):
    item = dict()
    keys = ['weight', 'symbol', 'formula', 'intent', 'code_snippet', 'type']
    tokens = [token.strip() for token in re.split(r'\t+', line.strip(), len(keys)-1)]
    for (key, value) in zip(keys[:len(tokens)], tokens):
        value = value.replace('\\n', '\n')
        item[key] = value[1:-1] if value[0] == '"' and value[-1] == '"' else value 
        # if key in ['formula' , 'intent'] and :
            
    return item


def main(lexicon_file, limit=3, seed=None, debug=False):    
    grammar = build_grammar(grammar_file=lexicon_file)
    generator = Generator(grammar=grammar, seed=seed)
    for _ in range(limit):
        intent = generator.generate_example(debug=debug)
        
        print("Intent:", intent)
        # print('\nCode snippet:\n')
        # print(expression.to_code_snippet())
        print("\n_______")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate synthetic utterances or ')
    parser.add_argument('--grammar', type=str, help='lexicon file name')
    parser.add_argument('--limit', nargs='?', type=int, help='number of examples to generate')
    parser.add_argument('--csv', nargs='?', type=int, help='save data in the provided csv file')
    args = parser.parse_args()
    
    main(args.lexicon_file, args.limit)