import random
import re
import copy

class Grammar:
    def __init__(self, grammar_file):
        self.grammar = self.build_grammar(grammar_file)
    
    def generate(self, item, variables=[], level=1):
        if self.is_terminal(item) or "reference" in item:
            return (item, item)
        
        level += 1
        formula_symbols = self.get_formula_symbols(item["formula"])
        
        children = []
        
        # process children sequentially so variable from one child can propagate to the others
        for symbol in formula_symbols:
            sub_item = self.get_item(symbol, variables, level)    
            child = self.generate(sub_item, variables, level)
            children.append(child)
            
            # assign a variable
            if child[0]["symbol"] == "Atomic" and "reference" not in child[0]:
                sub_item["assignment"] = f"x{random.randint(0,30)}"
                # sub_item["type"] = self.get_item_type(child)
                variable = sub_item
                variables += [variable]
            
        return (item, children)
    
    def get_item(self, symbol, variables=[], level=1):
        idx = self.get_variable_index(symbol, variables)
        if idx is not None:
            variable = variables.pop(idx)
            item = copy.deepcopy(variable)
            item["reference"] = variable["assignment"]
            item["symbol"] = symbol
            del item["assignment"]
            return item
        else:
            weighted_items = []
            items = self.get_items_for_symbol(symbol)
            for itm in items:
                weighted_items += [itm]*(int(itm["weight"]) * level)
            item = copy.deepcopy(random.choice(weighted_items))
            
            return item
    
    def get_item_type(self, item):
        item_type = item[0]["symbol"]
        if item_type in ["Str", "Int", "List"] or item_type.islower():
            return item_type
        return self.get_item_type(item[1][0])
    
    def get_formula_symbols(self, formula):
        formula_symbols = re.split(r'\s+', formula)
        formula_symbols =  [symbol for symbol in formula_symbols if symbol in self.grammar]
        return formula_symbols
    
    def is_terminal(self, item):
        symbol = item["symbol"]
        return symbol in self.terminals or not symbol in self.grammar
    
    def get_variable_index(self, symbol, variables):
        for i, variable in enumerate(variables):
            if variable["type"] == symbol:
                return i
        return None
    
    def get_items_for_symbol(self, symbol):
        items = self.grammar[symbol]
        return items
    
    def build_grammar(self, grammar_file):
        grammar = dict()
        self.terminals = []
        with open(grammar_file, 'r', encoding='utf8') as f:
            content = f.readlines()
            content = [x.rstrip().split("#")[0] for x in content if x.strip() != ""] 
            for index, line in enumerate(content):
                item = self.parse_grammar_line(line)
                item["id"] = index
                symbol = item["symbol"]
                
                grammar[symbol] = grammar[symbol] if symbol in grammar else []
                grammar[symbol].append(item)
                
                if symbol.islower() and symbol not in self.terminals:
                    self.terminals.append(symbol)
        return grammar 
    
    def parse_grammar_line(self, line):
        item = dict()
        keys = ["weight", "symbol", "formula", "type"]#, "code_snippet", "intent"]
        tokens = [token.strip() for token in re.split(r"\t+", line.strip(), len(keys)-1)]
        for (key, value) in zip(keys[:len(tokens)], tokens):
            item[key] = value
        return item
    

def flatten(item, str=None):
    parent, children = item[0], item[1]
    
    formula, symbol = parent["symbol"], parent["formula"]
    if "reference" in parent:
        symbol = parent["reference"]
    elif "assignment" in parent:
        symbol = f"{parent['assignment']} = {symbol}"
    
    str = parent['formula'] if str is None else re.sub(rf"\b{formula}\b", symbol, str, 1)
    
    if type(children) == list:
        for sub_item in children:
            str = flatten(sub_item, str=str)
    
    return str
        
        
g = Grammar(grammar_file="./builder/test")
for _ in range(1):
    example = g.generate(g.get_item("S"))
    print(flatten(example))
        
    