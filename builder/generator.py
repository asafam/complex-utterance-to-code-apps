import random
import re

class Generator:
    
    def __init__(self, grammar, seed=None):
        self.grammar = grammar
        
        if seed:
            random.seed(seed)
            
    def generate_example(self, symbol='ROOT', debug=False):
        example = self.expand(symbol, debug=debug)
        return example
    
    def expand(self, symbol, debug=False):
        if symbol not in self.grammar:
            if debug:
                print(symbol)
            return symbol
        
        rule = self.get_rule(symbol)
        is_terminal = not re.sub(r'\W+', '', rule['symbol']).isupper()
        if is_terminal:
            if debug:
                print(rule['intent'])
            return rule['intent']
        elif 'formula' not in rule:
            if debug:
                print("")
            return ""
        
        tokens = rule['formula'].split()
        sub_intents = [self.expand(token, debug=debug) for token in tokens]
        intent = ' '.join(sub_intents)
        if debug:
            print(intent)
        
        return intent
        
    def get_rule(self, symbol):
        items = self.grammar[symbol]
        weights = [int(item['weight']) for item in items]
        item = random.choices(items, weights=weights, k=1)[0]
        return item
        