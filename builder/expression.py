import random
import re
import copy
import string
from variable import Variable
from data_generator import DataGenerator



class Expression:
    Variables = []
    
    def __init__(self, grammar, weight, symbol, formula, ret_type, code_snippet, intent, indent, level, source, seed=None):
        self.seed = None
        if seed != None:
            self.seed = seed
            random.seed(seed)
        
        self.grammar = grammar
        self.weight = weight
        self.symbol = symbol
        self.formula = formula
        self.type = ret_type
        self.code_snippet = code_snippet
        self.intent = intent
        self.indent = indent
        self.level = level
        self.source = source
        
        self.symbols_map = dict()
        self.expressions_map = dict()
        
        self.assignment = None
        self.reference = None
        self.variables = []
        
        self.lines = []
        self.code_lines = []
        self.intent_lines = []
        self.line_indents = []
        self.code_line_indents = []
        
        self.parse_formula()
        
    def assign_variable(self, explicit=True):
        var_name = self.get_variable_name()
        variable = Variable(name=var_name, expression=self, explicit=explicit)
        self.Variables.append(variable)
        return variable
    
    def expand(self):
        # get the variables in the scope
        scope_variables = self.get_scope_variables()
        # get the expression
        self.expression = self.get_expression(scope_variables)
        
        # if this expression references a variable stop further expanding
        if self.reference:
            return
        
        # assign a variable if this expression meets variable criteria
        if self.symbol == "Atomic" and self.type != "void":
            variable = self.assign_variable(explicit=False)
            self.assignment = variable
            self.source.variables.append(variable)
        
        # expand nested symbols
        for symbol_mask in self.symbols_map.keys():
            expression_for_symbol = self.get_expression_for_symbol(self.symbols_map[symbol_mask])
            self.expressions_map[symbol_mask] = expression_for_symbol
            expression_for_symbol.expand()
        
            # add variables from expanded nested expressions
            if self.symbol in ["COND", "LOOP"]:
                variables = self.get_variables(included_symbols=["str", "list", "int"], excluded_symbols=["SEQ"])
                self.source.variables += variables
        
    def find_variable(self, variables):
        for index, variable in enumerate(variables): 
            if (variable.reference == self or variable.reference.type == self.symbol) and self.get_assignment() != variable:
                return index, variable
        return None, None
    
    def get_assignment(self):
        if self.assignment:
            return self.assignment
        elif not self.source:
            return None
        
        return self.source.get_assignment()
        
    def get_expression(self, variables, reuse_variable=False):
        # search in the scope of variables if any match this expression
        index, variable = self.find_variable(variables)
        if variable:
            self.reference = variable
            if not reuse_variable:
                variables.pop(index)
            return variable
        
        # otherwise get a new expression
        expression = self.get_expression_for_symbol(self.symbol)
        return expression
    
    def get_expression_for_symbol(self, symbol):
        weighted_items = []
        items = self.grammar[symbol]
        for item in items:
            weighted_items += [item]*(int(item["weight"]) ** self.level)
        item = random.choice(weighted_items)
        indent = 0
        if self.symbol in ["LOOP", "COND"] and symbol == "SEQ":
            indent = (self.indent + 1) 
        elif self.symbol == "SEQ" and symbol in ["LOOP", "COND", "SEQ"] :
            indent = self.indent
        
        if item["symbol"].islower():
            dataGenerator = DataGenerator(seed=self.seed)
            data = dataGenerator.generate_data(item["symbol"]) 
            if data:
                item["formula"] = item["code_snippet"] = item["intent"] = data
        
        expression = Expression(self.grammar, item["weight"], item["symbol"], item["formula"], item["type"], item["code_snippet"], item["intent"], indent, self.level + 1, self)
        return expression
    
    def get_scope_variables(self):
        if self.source == None:
            return self.variables
        
        return self.variables + self.source.get_scope_variables()
        
    
    def get_variables(self, included_symbols, excluded_symbols):
        if self.symbol in included_symbols and not self.reference:
            variable = self.assign_variable()
            self.reference = variable
            return [variable]
        elif self.symbol.islower() or self.symbol in excluded_symbols:
            return []
        
        # loop over nested expressions in recursion and get all variables that have not been referenced
        variables = []
        for symbol_mask in self.expressions_map.keys():
            expression = self.expressions_map[symbol_mask] if symbol_mask in self.expressions_map else None
            variables += expression.get_variables(included_symbols, excluded_symbols)
                
        return variables
    
    def get_variable_name(self):
        name = None
        if self.type == "str":
            name = random.choice(["s", "t", "my_str", "some_str"])
        elif self.type == "int":
            name = random.choice(["a", "b", "c", "d", "m", "n", "x", "y", "z", "var", "my_var", "some_var"])
        elif self.type == "list":
            name = random.choice(["lst", "my_list", "some_list"])
        else:
            name = random.choice(["a", "b", "c", "d", "x", "y", "z", "var", "my_var", "some_var"])
        
        existing_names = [v.name for v in Expression.Variables]
        i = 0
        unique_name = name
        while unique_name in existing_names:
            unique_name = name + str(i + 1)
            i += 1
        
        return unique_name
        
    def parse_formula(self):
        code_lines = [line.strip() for line in self.code_snippet.split("\\n")]
        self.code_lines = code_lines
        
        lines = [line.strip() for line in self.formula.split("\\n")]
        self.lines = lines
        
        for i, (line, code_line) in enumerate(zip(self.lines, self.code_lines)):
            
            self.line_indents.append(0)
            self.code_line_indents.append(0)
            if self.symbol in ["COND", "LOOP"]:
                self.line_indents[i] = 0
                if line.startswith("\\t "):
                    self.lines[i] = line.replace("\\t ", "")
                    self.line_indents[i] = 1
                
                self.code_line_indents[i] = 0
                if code_line.startswith("\\t"):
                    self.code_lines[i] = code_line.replace("\\t", "")
                    self.code_line_indents[i] = 1
                    
            elif self.symbol == "SEQ" and i > 0:
                self.line_indents[i] = self.indent
                self.code_line_indents[i] = self.indent
                
            for j, symbol in enumerate(re.split(r"\s+", line.strip())):
                letters = string.ascii_lowercase
                id = ''.join(random.choice(letters) for i in range(8))
                symbol_mask = f"sym_{id}"
                if symbol in self.grammar:
                    self.symbols_map[symbol_mask] = symbol
                    self.lines[i] = re.sub(symbol, symbol_mask, self.lines[i], 1)
                    self.code_lines[i] = re.sub(symbol, symbol_mask, self.code_lines[i], 1)
                    self.intent = re.sub(symbol, symbol_mask, self.intent, 1)
        
    def to_string(self, spaces="\t", lines_delimiter="\n", is_variable=False, mode="pseudo"):
        if self.reference and not is_variable:
            return self.reference.to_string()
        
        lines = []
        code_lines = []
        intent_lines = []
        line_indents = []
        
        # add explicit variables at the start of the expression
        for variable in [var for var in self.variables if var.explicit]:
            var_name = variable.to_string()
            var_value = variable.reference.to_string(spaces=spaces, lines_delimiter=lines_delimiter, is_variable=True, mode=mode)
            var_str = f"{var_name} = {var_value}" if mode != "intent" else f"Let {var_name} be {var_value}."
            indent = self.indent
            var_str = indent * spaces + var_str 
            lines.append(var_str)
            code_lines.append(var_str)
            intent_lines.append(var_str)
            line_indents.append(self.line_indents[0])
         
        # append the rest of the lines 
        lines += self.lines
        code_lines += self.code_lines
        intent_lines += [self.intent]
        line_indents += self.line_indents 
        
        # cast lines to string with indentations
        final_lines = []
        for i, line in enumerate(lines):
            final_line = line 
            if mode == "code":
                final_line = code_lines[i]
            elif mode == "intent":
                final_line = intent_lines[i] if i < len(intent_lines) else final_lines[-1]
            
            tokens = line.split()
            for token in tokens:
                if token in self.symbols_map:
                    expression = self.expressions_map[token]
                    expression_str = expression.to_string(spaces=spaces, lines_delimiter=lines_delimiter, is_variable=is_variable, mode=mode)
                    # add implicit variables assignments
                    if expression.assignment and not expression.assignment.explicit:
                        expression_str = f"{expression.assignment.to_string()} = {expression_str}" if mode != "intent" else f"{expression.assignment.to_string()} is {expression_str}"
                    final_line = final_line.replace(token, expression_str)
                    
                    if expression.symbol in ["Atomic"] and self.symbol not in ["LOOP", "COND"] and mode != "intent":
                        final_line = self.indent * spaces + final_line
            
            if self.symbol in ["LOOP", "COND"]:
                indent = self.indent if line_indents[i] == 0 else 0
                final_line = indent * spaces + final_line  
                            
            if final_line and mode == "intent":
                if i < len(intent_lines):
                    final_lines.append(final_line)
                else:
                    final_lines[-1] = final_line
            elif final_line:
                final_lines.append(final_line)
            
        full_str = lines_delimiter.join(final_lines)
        return full_str
    
    def to_code_snippet(self, spaces="\t"):
        return self.to_string(spaces=spaces, mode="code")
    
    def to_intent(self):
        return self.to_string(spaces="", lines_delimiter=" ", mode="intent")
    