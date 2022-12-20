class Variable:
    
    def __init__(self, name, expression, explicit=True):
        self.name = name
        self.reference = expression
        self.explicit = explicit
        
    def to_string(self):
        return self.name