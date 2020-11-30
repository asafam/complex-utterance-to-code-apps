import random
import re
import copy
from variable import Variable

random.seed(0)

class Expression:
    Variables = []
    
    def __init__(self, grammar, weight, symbol, formula, exp_type, indent, level):
        self.grammar = grammar
        self.weight = weight
        self.symbol = symbol
        self.formula = formula
        self.type = exp_type
        self.indent = indent
        self.level = level
        
        self.symbols_map = dict()
        self.expressions_map = dict()
        
        self.assignment = None
        self.reference = None
        self.variables = []
        
        self.lines = []
        self.line_indents = []
        
        self.parse_formula()
        
    def assign_variable(self, explicit=True):
        var_name = self.get_variable_name()
        variable = Variable(name=var_name, expression=self, explicit=explicit)
        self.Variables.append(variable)
        return variable
    
    def expand(self, scope_variables=[]):
        # get the expression
        self.expression = self.get_expression(scope_variables)
        
        # if this expression references a variable stop further expanding
        if self.reference:
            return
        
        # assign a variable if this expression meets variable criteria
        if self.symbol == "Atomic":
            variable = self.assign_variable(explicit=False)
            self.assignment = variable
            self.variables.append(variable)
        
        # expand nested symbols
        for symbol_mask in self.symbols_map.keys():
            expression_for_symbol = self.get_expression_for_symbol(self.symbols_map[symbol_mask])
            self.expressions_map[symbol_mask] = expression_for_symbol
            expression_for_symbol.expand(scope_variables=(scope_variables + self.variables))
        
            # add variables from expanded nested expressions
            if self.symbol in ["COND", "LOOP"]:
                variables = self.get_variables(included_symbols=["str", "list", "int"], excluded_symbols=["SEQ"])
                self.variables += variables
        
    def find_variable(self):
        for index, variable in enumerate(self.variables): 
            if variable.reference == self or variable.reference.type == self.symbol:
                return index, variable
        return None, None
        
    def get_expression(self, variables, reuse_variable=False):
        # search in the scope of variables if any match this expression
        index, variable = self.find_variable()
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
        expression = Expression(self.grammar, item["weight"], item["symbol"], item["formula"], item["type"], indent, self.level + 1)
        return expression
    
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
        while name in existing_names:
            name += str(i + 1)
            i += 1
        
        return name
        
    def parse_formula(self):
        lines = [line.strip() for line in self.formula.split("\\n")]
        self.lines = lines
        for i, line in enumerate(self.lines):
            
            self.line_indents.append(0)
            if self.symbol in ["COND", "LOOP"]:
                self.line_indents[i] = 0 #self.indent
                if line.startswith("\\t "):
                    self.lines[i] = line.replace("\\t ", "")
                    self.line_indents[i] = 1
            elif self.symbol == "SEQ" and i > 0:
                self.line_indents[i] = self.indent
                
            for j, symbol in enumerate(re.split(r"\s+", line.strip())):
                symbol_mask = f"sym_{i}_{j}"
                if symbol in self.grammar:
                    self.symbols_map[symbol_mask] = symbol
                    self.lines[i] = re.sub(symbol, symbol_mask, self.lines[i], 1)
        
    def to_string(self, spaces="\t", is_variable=False):
        if self.reference and not is_variable:
            return self.reference.to_string()
        
        lines = []
        line_indents = []
        
        # add explicit variables at the start of the expression
        for variable in [var for var in self.variables if var.explicit]:
            var_str = f"{variable.to_string()} = {variable.reference.to_string(is_variable=True)}"
            lines.append(var_str)
            line_indents.append(self.line_indents[0])
            
         
        # append the rest of the lines   
        lines += self.lines
        line_indents += self.line_indents   
        
        # cast lines to string with indentations
        final_lines = []
        for i, line in enumerate(lines):
            final_line = line   
            # spaces_str = ((self.indent) * spaces)
            # final_line = (spaces_str + final_line)   
                
            for token in line.split():
                if token in self.symbols_map:
                    expression = self.expressions_map[token]
                    expression_str = expression.to_string(spaces=spaces)
                    # add implicit variables assignments
                    if expression.assignment and not expression.assignment.explicit:
                        expression_str = f"{expression.assignment.to_string()} = {expression_str}"
                    final_line = final_line.replace(token, expression_str)
                    
                    if expression.symbol in ["Atomic", "LOOP", "COND"]:
                        final_line = self.indent * spaces + final_line
            
            if final_line:
                final_lines.append(final_line)
            
        full_str = "\n".join(final_lines)
        return full_str
    