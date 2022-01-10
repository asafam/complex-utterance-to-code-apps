import argparse
import csv
from utterance2 import Utterance
import random
import yaml


def load_file(filepath):
    scenarios = [] 
    intents = {}
    
    with open(filepath, 'r') as fstream:
        try:
            data = yaml.safe_load(fstream)
            scenarios = data['scenarios']
            intents = data['intents']
            constraints = data['constraints']
            link_words = data['link_words']
            quantifiers = data['quantifiers']
        except yaml.YAMLError as exc:
            print(exc)
    
    return scenarios, intents, constraints, link_words, quantifiers


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
        icon = "map"
    elif domain == 'places':
        icon = "geo"
    elif domain == 'reminder':
        icon = "bell"
    elif domain == 'timer':
        icon = "watch"
    elif domain == 'weather':
        icon = "cloud-sun"
    return icon #f"<i class=\"bi bi-{icon}\"></i>" if icon else ''


def write_file_batch(data, filepath, delimiter=','):
    with open(filepath, 'w', newline='') as f:
        file_handler = csv.writer(f, delimiter=delimiter)
        file_handler.writerow(['id', 'contexts', 'intents', 'constraints', 'intent-icons', 'constraint-icons', 'link-words', 'quantifiers', 'min-intents', 'min-constraints'])
        for i, item in enumerate(data):
            scenarios, intents, constraints, link_words, quantifiers, min_intents, min_constraints = item
            
            icons = []
            constraint_icons = []
            for i, intent in enumerate(intents):
                domain, _ = intent
                icons.append(get_domain_icon(domain))
            
            for i, intent in enumerate(constraints):
                domain, _ = intent
                constraint_icons.append(get_domain_icon(domain))
            
            scenarios_str = " | ".join(scenarios)
            intent_str = " | ".join([intent[1]['intent'] for intent in intents])
            icons_str = " | ".join(icons)
            constraints_str = " | ".join([constraint[1]['intent'] for constraint in constraints])
            constraint_icons_str = " | ".join(constraint_icons)
            link_words_str = " | ".join(link_words)
            quantifiers_str = " | ".join(quantifiers)
            file_handler.writerow([i ,scenarios_str, intent_str, constraints_str, icons_str, constraint_icons_str, link_words_str, quantifiers_str, min_intents, min_constraints])


def main(input_file, output_file, limit, intents_count, constraints_count, link_words_count, quantifiers_count, scenarios_count, seed=None, debug=False): 
    data = []   
    all_scenarios, all_intents, all_constraints, all_link_words, all_quantifiers = load_file(filepath=input_file)
    for i in range(limit):
        task = Utterance(all_scenarios, all_intents, all_constraints, all_link_words, all_quantifiers)
        intents, conjunction_words, quantifiers, min_conjunction, min_constraints = task.sample(intents_count, constraints_count, link_words_count, quantifiers_count, scenarios_count)
        data.append((scenarios, intents, constraints, link_words, quantifiers, min_intents, min_constraints))
        # print(f"{i+1}) scenario = {scenario}, intents = {', '.join([(intent[1]['description'][:1].upper() + intent[1]['description'][1:]) for intent in intents])}")
    
    write_file_batch(data, filepath=output_file)
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates pairs of scenario and intents')
    parser.add_argument('--limit', type=int, default=50, help='number of examples to generate')
    parser.add_argument('--inputfile', type=str, help='input file')
    parser.add_argument('--outputfile', type=str, help='output file')
    parser.add_argument('--intentscount', type=int, default=5, help='number of intents to sample')
    parser.add_argument('--constraintscount', type=int, default=5, help='number of constraints to sample')
    parser.add_argument('--linkwordscount', type=int, default=3, help='number of link words to sample')
    parser.add_argument('--quantifierscount', type=int, default=2, help='number of quantifiers to sample')
    parser.add_argument('--scenarioscount', type=int, default=10, help='number of scenarios to sample')
    args = parser.parse_args()
    
    main(input_file=args.inputfile, output_file=args.outputfile, limit=args.limit, 
         intents_count=args.intentscount, constraints_count=args.constraintscount,
         link_words_count=args.linkwordscount, quantifiers_count=args.quantifierscount,
         scenarios_count=args.scenarioscount)