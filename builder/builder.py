import re
import random
from expression import Expression

random.seed(0)

def build_grammar(grammar_file):
    grammar = dict()
    with open(grammar_file, 'r', encoding='utf8') as f:
        content = f.readlines()
        content = [x.rstrip().split("#")[0] for x in content if x.split("#")[0].strip() != ""] 
        for index, line in enumerate(content):
            item = parse_grammar_line(line)
            item["id"] = index
            symbol = item["symbol"]
            
            grammar[symbol] = grammar[symbol] if symbol in grammar else []
            grammar[symbol].append(item)
    return grammar


def parse_grammar_line(line):
    item = dict()
    keys = ["weight", "symbol", "formula", "type"]#, "code_snippet", "intent"]
    tokens = [token.strip() for token in re.split(r"\t+", line.strip(), len(keys)-1)]
    for (key, value) in zip(keys[:len(tokens)], tokens):
        item[key] = value
    return item


def generate_example(grammar, root_symbol="S"):
    root_items = grammar[root_symbol]
    item = random.choice(root_items)
    expression = Expression(grammar, item["weight"], item["symbol"], item["formula"], item["type"], 0, 0)
    expression.expand()
    return expression
    

grammar = build_grammar(grammar_file="./builder/test")
expression = generate_example(grammar=grammar)
print(expression.to_string())
print("\ndone")
