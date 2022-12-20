import argparse
import csv
import json


def read_results(filepath, delimiter=','):
    results = []
    headers = []
    with open(filepath, 'r') as file:
        f_reader = csv.reader(file, delimiter=delimiter)
        for i, line in enumerate(f_reader):
            if i == 0:
                headers = line
            if i != 0:
                record = {}
                for j, item in enumerate(line):
                    record[headers[j]] = item
                results.append(record)
    return results
    

def write_pretty_output_file(filepath, data, delimiter=','):
    with open(filepath, "w") as file:
        for line in data:
            intents = [item.strip() for item in line['Input.intents'].split('|')] if 'Input.intents' in line else None
            conjunction_words = [x.strip().split(':')[0] for x in line['Input.conjunction-words'].split('|')] if 'Input.conjunction-words' in line else None
            min_intents = line['Input.min-intents'] if 'Input.min-intents' in line else None
            answer_str = line['Answer.taskAnswers']
            answer = json.loads(answer_str)[0]
            worker_responses = json.loads(answer['worker-responses']) if 'worker-responses' in answer else None
            
            utterances = None
            annotations = None
            if worker_responses:
                for response in worker_responses:
                    for key in response.keys():
                        file.write(f"{key}:\n")
                        file.write(f"{response[key]}\n")
            #         utterances = utterances or []
            #         utterances.append(response['utterance'])
                    
            #         annotations = annotations or []
            #         annotations.append([item.strip() for item in response['intents-annotations'].split('|')] if 'intents-annotations' in response else None)
            
            # # print output
            # file.write(f"HIT ({line['HITId']}):\n\n")
            
            # if min_intents:
            #     file.write(f"[Intents] (at least {min_intents}):\n")
            #     for i, item in enumerate(intents):
            #         file.write(f"{i+1}) {item.strip()}\n")
            
            # if conjunction_words:
            #     file.write(f"\n[Conjunction words]:\n")
            #     file.write(f"{', '.join(conjunction_words)}\n")
            
            # file.write("\n")
            
            # if utterances:
            #     for i, utterance in enumerate(utterances):
            #         file.write(f"[Utterance {i+1}]:\n{utterance}\n")
            
            #         if annotations[i]:
            #             file.write(f"\n[Annotations]:\n")
            #             for j, item in enumerate(annotations[i]):
            #                 file.write(f"* {item.strip()}\n")
            
            # file.write(f"\nWorker [{line['WorkerId']}]\n")
            # file.write(f"{line['AcceptTime']} - {line['SubmitTime']} ({line['WorkTimeInSeconds']} seconds)\n")
            # if answer['worker-feedback'] != 'undefined':
            #     file.write(f"\"{answer['worker-feedback']}\"\n")
            file.write(f"\n{'-'*10}\n\n")
            

def write_csv_output_file(filepath, data, delimiter='\t'):
    with open(filepath, "w") as file:
        row_num = 0
        for index, line in enumerate(data):
            intents = [item.strip() for item in line['Input.intents'].split('|')] if 'Input.intents' in line else None
            conjunction_words = [x.strip().split(':')[0] for x in line['Input.conjunction-words'].split('|')] if 'Input.conjunction-words' in line else None
            min_intents = line['Input.min-intents'] if 'Input.min-intents' in line else None
            answer_str = line['Answer.taskAnswers']
            answer = json.loads(answer_str)[0]
            worker_responses = json.loads(answer['worker-responses']) if 'worker-responses' in answer else None
            
            utterances = None
            annotations = None
            if worker_responses:
                for response in worker_responses:
                    utterances = utterances or []
                    if 'utterance' in response:
                        utterances.append(response['utterance'].strip().replace('\n', '\\n'))
                    
                    annotations = annotations or []
                    if 'intents-annotations' in response:
                        annotations.append([item.strip() for item in response['intents-annotations'].split('|')] if 'intents-annotations' in response else None)
            elif 'utterances' in answer:
                utterances = [ut.strip() for ut in answer['utterances'].split('|') if ut.strip() != ''][-1:]
            elif 'utterance' in answer:
                utterances = [answer['utterance']]
            
            # print output
            records = [[]]
            headers = []
            
            headers.append('HITId')
            data = line['HITId']
            for record in records:
                record.append(data)
                
            headers.append('WorkerId')
            data = line['WorkerId']
            for record in records:
                record.append(data)
                
            headers.append('worker-feedback')
            data = answer['worker-feedback'] if 'worker-feedback' in answer else ''
            for record in records:
                record.append(data)
                
            headers.append('WorkTimeInSeconds')
            data = line['WorkTimeInSeconds']
            for record in records:
                record.append(data)
            
            headers.append('min_intents')
            if min_intents:
                data = min_intents
                for record in records:
                    record.append(data)
            
            headers.append('intents')
            if intents:
                data = ", ".join(intents)
                for record in records:
                    record.append(data)
            
            if conjunction_words:
                headers.append('conjunction_words')
                data = ', '.join(conjunction_words)
                for record in records:
                    record.append(data)
            
            if utterances:
                headers.append('utterances')
                for _ in range(len(utterances) - len(records)):
                    records.append(records[0].copy())
                for i, utterance in enumerate(utterances):
                    records[i].append(utterance)
                    
            if annotations:
                headers.append('intents-annotations')
                data = ', '.join(annotations)
                for record in records:
                    record.append(data)
                    
            headers = ['Row'] + headers
                    
            if index == 0:
                file.write(f"{delimiter.join(headers)}\n")
                
            for record in records:
                record = [str(row_num + 1)] + record
                file.write(f"{delimiter.join(record)}\n")
                row_num += 1
            

def main(results_filepath, pretty_results_filepath, file_type):
    results = read_results(filepath=results_filepath)
    if file_type == 'csv':
        write_csv_output_file(filepath=pretty_results_filepath, data=results)
    else:
        write_pretty_output_file(filepath=pretty_results_filepath, data=results)
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates pairs of scenario and intents')
    parser.add_argument('--resultsfilepath', type=str, help='MTurk results file path')
    parser.add_argument('--outputfilepath', type=str, help='Output file path')
    parser.add_argument('--outputfiletype', type=str, help='csv | txt')
    
    args = parser.parse_args()
    
    main(results_filepath=args.resultsfilepath, pretty_results_filepath=args.outputfilepath, file_type=args.outputfiletype)