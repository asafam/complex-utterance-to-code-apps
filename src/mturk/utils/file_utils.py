import os
import yaml
import csv


def load_all_csv_files(path, suffix='.tsv', skip=[]):
    files = find_csv_filenames(path=path, suffix=suffix)
    files = [f for f in files if suffix in f and not any(map(lambda x: f.startswith(x), skip))]
    data = []
    for file in files:
        file_data = load_csv_file(f"{path}/{file}")
        data += file_data
    return data
        
        
def find_csv_filenames(path, suffix='.tsv'):
    filenames = [ filename for filename in os.listdir(path) if filename.endswith(suffix) ]
    return filenames
        
        
def load_csv_file(path):
    data = []
    with open(path) as file:
        for idx, line in enumerate(file.readlines()):
            if idx == 0:
                continue
            domain, utterance, semantic_parse = line.strip().split('\t')
            record = {
                'domain': domain,
                'subdomain': extract_subdomain(semantic_parse),
                'semantic_parse': semantic_parse,
                'utterance': utterance,
            }
            data.append(record)
    return data
        
        
def load_yml_file(path):
    with open(path, 'r') as fstream:
        try:
            data = yaml.safe_load(fstream)
            return data
        except yaml.YAMLError as exc:
            print(exc)


def extract_subdomain(item):
    start = item.index(':') + 1
    end = item.index(' ')
    subdomain = item[start:end]
    return subdomain


def get_domain_icon(domain):
    icon = None
    if domain == 'alarm':
        icon = "alarm"
    elif domain == 'apps':
        icon = "phone"
    elif domain == 'calendar':
        icon = "calendar3"
    elif domain == 'events':
        icon = "info"
    elif domain == 'messaging':
        icon = "chat"
    elif domain == 'music':
        icon = "music-note"
    elif domain == 'navigation':
        icon = "truck"
    elif domain == 'places':
        icon = "pin-map"
    elif domain == 'reminder':
        icon = "bell"
    elif domain == 'timer':
        icon = "watch"
    elif domain == 'weather':
        icon = "cloud-sun"
    elif domain == 'event':
        icon = "star"
    return icon


def write_output_file(path, data, delimiter=','):
    with open(path, 'w', newline='') as f:
        file_handler = csv.writer(f, delimiter=delimiter)
        file_handler.writerow(['id', 'intents', 'intent-icons', 'min-intents', 'conjunction-words', 'min-conjunction-words'])
        for i, item in enumerate(data):  
            intents_str = " | ".join([intent['utterance'] for intent in item['intents']])
            icons_str = " | ".join([get_domain_icon(domain[0]) for domain in item['domains']])
            conjunctions_str = " | ".join([f"{c['display']}:{c['verification'] if 'verification' in c else c['display']}" for c in item['conjunctions']])
            min_intents = len(item['intents'])
            min_conjunctions = 1
            
            line = [i, intents_str, icons_str, min_intents, conjunctions_str, min_conjunctions ]
            file_handler.writerow(line)
