import random
import re
import copy


ASSIGNMENT = "assignment"
FORMULA = "formula"
ID = "id"
REFERENCE = "reference"
SYMBOL = "symbol"
TYPE = "type"
WEIGHT = "weight"
LEVEL = "level"


class Grammar:
    def __init__(self, grammar_file):
        self.grammar = self.build_grammar(grammar_file)
        self.variable_names = []
    
    def generate(self, item, variables=[], level=1):
        if self.is_terminal(item) or REFERENCE in item:
            return (item, item)
        
        children = [] 
        
        # process children sequentially so variable from one child can propagate to the others
        children_symbols = self.get_children_symbols(item)
        for line_index, line_symbols in enumerate(children_symbols):
            for symbol in line_symbols:
                sub_item = self.get_item(symbol, variables, level+1)    
                child = self.generate(sub_item, variables, level+1)
                children.append(child)
                
                # assign a variable
                if child[0][SYMBOL] == "Atomic" and REFERENCE not in child[0]:
                    sub_item[ASSIGNMENT] = self.assign_variable_name(child, child[0][TYPE])
                    variable = sub_item
                    variables += [variable]
            
            if line_index == 0 and item[SYMBOL] in ["LOOP", "COND"]:
                variables = self.extract_variables((item, children))
                for variable in variables:
                    item[FORMULA] = f"{variable[SYMBOL]} \\n {item[FORMULA]}"
                    children.insert(0, (variable, variable))
            
        return (item, children)
    
    def get_item(self, symbol, variables=[], level=1):
        idx = self.get_variable_index(symbol, variables)
        if idx is not None:
            variable = variables.pop(idx)
            item = copy.deepcopy(variable)
            item[REFERENCE] = variable[ASSIGNMENT]
            item[SYMBOL] = symbol
            del item[ASSIGNMENT]
            return item
        else:
            weighted_items = []
            items = self.get_items_for_symbol(symbol)
            for itm in items:
                weighted_items += [itm]*(int(itm[WEIGHT]) ** level)
            item = copy.deepcopy(random.choice(weighted_items))
            item[LEVEL] = level
            
            return item
        
    def extract_variables(self, item, variables=[]):
        _, children = item
        for child in children:
            if child[0][SYMBOL] in ['str', 'list', 'int']:
                variable = copy.deepcopy(child[0])
                variable[ASSIGNMENT] = self.assign_variable_name(child, child[0][TYPE])
                variables.append(variable)
                child[0][REFERENCE] = variable[ASSIGNMENT]
            elif not child[0][SYMBOL].islower():
                self.extract_variables(child)
            
        return variables
    
    def assign_varialbe(self, variable, symbol):
        item = copy.deepcopy(variable)
        item[REFERENCE] = variable[ASSIGNMENT]
        item[SYMBOL] = symbol
        del item[ASSIGNMENT]
        return item
    
    def get_primitives(self, item):
        if item[0][TYPE].islower():
            return 
    
    def get_children_symbols(self, item):
        formula = item[FORMULA]
        formula_symbols = []
        for line in re.split(r'\\n', formula):
            symbols = re.split(r'\s+', line)
            formula_symbols.append([symbol for symbol in symbols if symbol in self.grammar])
        return formula_symbols
    
    def is_terminal(self, item):
        symbol = item[SYMBOL]
        return symbol in self.terminals or not symbol in self.grammar
    
    def get_variable_index(self, symbol, variables):
        for i, variable in enumerate(variables):
            if variable[TYPE] == symbol:
                return i
        return None
    
    def get_items_for_symbol(self, symbol):
        items = self.grammar[symbol]
        return items
    
    def get_variable(self, item, ret_type):
        _, children = item
        if type(children) is not list:
            return children[REFERENCE] if REFERENCE in children and children[TYPE] == ret_type else None
        return self.get_variable(children[0], ret_type)
                
    def assign_variable_name(self, item, ret_type):
        variable_name = self.get_variable(item, ret_type) or self.get_variable_name()
        return variable_name
    
    def get_variable_name(self, max_vars=30):
        variable_name = f"x{random.randint(0,max_vars)}"
        while variable_name in self.variable_names:
            max_vars += 1
            variable_name = f"x{random.randint(0,max_vars)}"
        self.variable_names.append(variable_name) 
        return variable_name
    
    def build_grammar(self, grammar_file):
        grammar = dict()
        self.terminals = []
        with open(grammar_file, 'r', encoding='utf8') as f:
            content = f.readlines()
            content = [x.rstrip().split("#")[0] for x in content if x.split("#")[0].strip() != ""] 
            for index, line in enumerate(content):
                item = self.parse_grammar_line(line)
                item[ID] = index
                symbol = item[SYMBOL]
                
                grammar[symbol] = grammar[symbol] if symbol in grammar else []
                grammar[symbol].append(item)
                
                if symbol.islower() and symbol not in self.terminals:
                    self.terminals.append(symbol)
        return grammar 
    
    def parse_grammar_line(self, line):
        item = dict()
        keys = [WEIGHT, SYMBOL, FORMULA, TYPE]#, "code_snippet", "intent"]
        tokens = [token.strip() for token in re.split(r"\t+", line.strip(), len(keys)-1)]
        for (key, value) in zip(keys[:len(tokens)], tokens):
            item[key] = value
        return item
    

def flatten(item, str=None):
    parent, children = item
    
    formula, symbol = parent[SYMBOL], parent[FORMULA]
    if REFERENCE in parent:
        symbol = parent[REFERENCE]
    elif ASSIGNMENT in parent:
        symbol = f"{parent['assignment']} = {symbol}"
    
    str =  parent['formula'] if str is None else re.sub(rf"\b{formula}\b", symbol, str, 1)
    
    if type(children) == list:
        for sub_item in children:
            str = flatten(sub_item, str=str)
    
    return str
        
        
g = Grammar(grammar_file="./builder/test")
for _ in range(1):
    example = g.generate(g.get_item("S"))
    print(flatten(example))
        
    