import random
from faker import Faker

faker = Faker()


class DataGenerator:
    def __init__(self, seed=None):
        if seed != None:
            random.seed(seed)
            
    def generate_data(self, symbol):
        if symbol == "int_pos":
            return self.generate_number(num_type=int, positive=True)
        elif symbol == "int_neg":
            return self.generate_number(num_type=int, positive=False)
        elif symbol == "float_pos":
            return self.generate_number(num_type=float, positive=True)
        elif symbol == "float_neg":
            return self.generate_number(num_type=float, positive=False)
        elif symbol == "str":
            return self.generate_string()
        elif symbol == "str_short":
            return self.generate_string(length="char")
        elif symbol == "str_word":
            return self.generate_string(length="word")
        elif symbol == "list":
            return self.generate_list()
        else:
            return None
        
    def generate_number(self, num_type, positive=None):
        a, b = -10, 10
        if positive == True:
            a = 0
        elif positive == False:
            b = 0
            
        num = random.uniform(a, b)
        num_str = f"{num:.2f}" if num_type == float else f"{int(num)}"
        return num_str

    def generate_string(self, length=None):
        if length == "char":
            vocab = "~!@#$%^&*()_+[]{}:;'<>?,."
            index = random.randint(0, len(vocab)-1)
            return "\"" + vocab[index] + "\""
        elif length == "word":
            return "\"" + faker.word() + "\""
        else:
            text = faker.text()
            text = text.split(".")[0] 
            return "\"" + text + "\""
    
    def generate_list(self, length=5, type=str):
        data = "["
        for _ in range(length):
            x = ("\"" + faker.word() + "\"") if type == str else random.randint(-100, 100)
            data += f"{x}, "
        data = data[:-2]
        data += "]"
        return data