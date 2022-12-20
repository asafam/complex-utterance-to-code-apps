import argparse
import csv
from utterance import Utterance
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
            domain_groups = data['domain_groups']
            link_words = data['link_words']
            quantifiers = data['quantifiers']
        except yaml.YAMLError as exc:
            print(exc)
    
    return scenarios, intents, domain_groups, link_words, quantifiers


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
        file_handler.writerow(['id', 'context', 'intents', 'intents-count', 'icons', 'link-words', 'link-word-idx', 'quantifiers', 'quantifier-idx', 'min-intents'])
        for i, item in enumerate(data):
            scenario, intents, link_words, link_word_idx, quantifiers, quantifier_idx, min_intents = item
            
            icons = []
            instructions_text = ""
            for i, intent in enumerate(intents):
                domain, task, ret_type = intent
                icons.append(get_domain_icon(domain))
                # intents_html += f"<p>{icon}<span style=\"padding-left: 10px;\">{task['description'][:1].upper() + task['description'][1:]}</span></p>"
                # instructions_text += 'depending on ' if ret_type == 'bool' else ''
                # instructions_text += task['returns' if ret_type == 'bool' else 'intent'].lower()
                # instructions_text += ' (don\'t assume you know it)' if ret_type == 'bool' else ''
                # instructions_text += ', ' if category == CATEGORY_CONDITION or i != (len(intents) - 1) else ", and "    
            # instructions_text = instructions_text[:1].upper() + instructions_text[1:-2].strip()
            
            intent_str = " | ".join([intent[1]['intent'] for intent in intents])
            icons_str = " | ".join(icons)
            link_words_str = " | ".join(link_words)
            quantifiers_str = " | ".join(quantifiers)
            file_handler.writerow([i ,scenario, intent_str, len(intents), icons_str, link_words_str, link_word_idx, quantifiers_str, quantifier_idx, min_intents])


def main(input_file, output_file, limit, intents_count, link_words_count, quantifiers_count, seed=None, debug=False): 
    data = []   
    all_scenarios, all_intents, all_domains_groups, all_link_words, all_quantifiers = load_file(filepath=input_file)
    for i in range(limit):
        utterance = Utterance(all_scenarios, all_domains_groups, all_intents, all_link_words, all_quantifiers)
        scenario, intents, link_words, link_word_idx, quantifiers, quantifier_idx, min_intents = utterance.sample(intents_count, link_words_count, quantifiers_count)
        data.append((scenario, intents, link_words, link_word_idx, quantifiers, quantifier_idx, min_intents))
        print(f"{i+1}) scenario = {scenario}, intents = {', '.join([(intent[1]['description'][:1].upper() + intent[1]['description'][1:]) for intent in intents])}")
    
    write_file_batch(data, filepath=output_file)
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates pairs of scenario and intents')
    parser.add_argument('--limit', type=int, default=50, help='number of examples to generate')
    parser.add_argument('--inputfile', type=str, help='input file')
    parser.add_argument('--outputfile', type=str, help='output file')
    parser.add_argument('--intentscount', type=int, default=5, help='number of intents to sample')
    parser.add_argument('--conjunctionWordscount', type=int, default=4, help='number of link words to sample')
    parser.add_argument('--quantifierscount', type=int, default=2, help='number of quantifiers to sample')
    args = parser.parse_args()
    
    main(input_file=args.inputfile, output_file=args.outputfile, limit=args.limit, 
         intents_count=args.intentscount, link_words_count=args.conjunctionWordscount, quantifiers_count=args.quantifierscount)