import os
import yaml

def read_csv_file(filepath):
    data = []
    with open(filepath) as file:
        for line in file.readlines():
            data.append(line.strip().split("\t"))
    return data


def read_yaml_file(filepath):
    with open(filepath) as file:
        return yaml.load(file, Loader=yaml.FullLoader)

def write_yaml_file(data, filepath):
    create_dir_if_not_exists(filepath)
    with open(filepath, "w") as file:
        yaml.dump(data, file)
        
        
def create_dir_if_not_exists(filepath):
    # get the directory path
    dirpath = os.path.dirname(filepath)
    
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)