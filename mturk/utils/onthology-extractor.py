import glob
import re
import argparse


def extract_onthologies(path):
    onthologies = {}
    
    for filename in glob.glob(path):
        with open(filename) as file:
            for idx, line in enumerate(file.readlines()):
                if idx == 0:
                    continue
                
                _, _, semantic_parse = line.strip().split('\t')
                
                text = re.sub(r'\s*\[\s*', ' [ ', semantic_parse)
                text = re.sub(r'\s*\]\s*', ' ] ', text)
                left_sq_brackets = []
                intents = []
                for token in text.strip().split():
                    if token == '[':
                        if len(left_sq_brackets) > 0:
                            left_sq_brackets[-1] += 1
                    elif token == ']':
                        left_sq_brackets[-1] -= 1
                        if left_sq_brackets[-1] == 0:
                            left_sq_brackets.pop()
                            intents.pop()
                    elif token.startswith('IN:'):
                        if len(left_sq_brackets) > 0:
                            left_sq_brackets[-1] -= 1
                        left_sq_brackets.append(1)
                        intent = token[len('IN:'):]
                        intents.append(intent)
                        onthologies[intent] = onthologies[intent] if intent in onthologies else []
                    elif token.startswith('SL:'):
                        slot = token[len('SL:'):]
                        if slot not in onthologies[intents[-1]]:
                            onthologies[intents[-1]].append(slot)
    return onthologies

                       
def main(path, outputfile):
    onthologies = extract_onthologies(path)
    
    with open (outputfile,'w') as file:
        for intent in onthologies:
            for slot in onthologies[intent]:
                file.write(f"{intent}\t{slot}\n")

                        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract the onthologies from dataset files')
    parser.add_argument('--path', type=str, help='dataset path', default='/Users/asaf/Downloads/TOPv2_Dataset/*.tsv')
    parser.add_argument('--outputfile', type=str, help='dataset path', default='./onthologies.tsv')
    args = parser.parse_args()
    
    main(path=args.path,outputfile=args.outputfile)
