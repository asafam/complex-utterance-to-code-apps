import argparse
from tasks.rewrite_task import RewriteTask
from utils.file_utils import write_output_file


def main(input_csv_path_dir, input_conjunction_file_path, output_file, k, intents_counts, intent_counts_p, conjunction_words_count, conjunction_words_min, skip_domains=[]):
    task = RewriteTask()
    options = {
        'sizes': intents_counts,
        'size_weights': intent_counts_p,
        'conjunction_limit': conjunction_words_count,
        'conjunction_min': conjunction_words_min,
        'conjunction_file_path': input_conjunction_file_path,
        'domains_dir_path': input_csv_path_dir,
        'skip_domains': skip_domains,
    }
    samples = task.sample(k=k, options=options)
    write_output_file(path=output_file, data=samples)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates pairs of scenario and intents')
    parser.add_argument('--k', type=int, default=50, help='number of examples to generate')
    parser.add_argument('--inputcsvpathdir', type=str, help='input csv path directory')
    parser.add_argument('--inputconjunctionfilepath', type=str, help='input conjunction file path')
    parser.add_argument('--outputfile', type=str, help='output file path')
    parser.add_argument('--intentscounts', type=int, nargs='+', help='number of intents to sample for each example')
    parser.add_argument('--intentscountweights', type=float, nargs='+', help='probability weights on the number of intents to sample for each example')
    parser.add_argument('--conjunctionwordscount', type=int, default=3, help='number of conjunction words to sample for each example')
    parser.add_argument('--conjunctionwordsmin', type=int, default=1, help='minimal number of required conjunction words to use')
    parser.add_argument('--skipdomains', type=str, nargs='+', default=["music", "timer"], help='domains to skip')

    args = parser.parse_args()
    
    main(input_csv_path_dir=args.inputcsvpathdir, input_conjunction_file_path=args.inputconjunctionfilepath, 
         output_file=args.outputfile, k=args.k, intents_counts=args.intentscounts, intent_counts_p=args.intentscountweights,
         conjunction_words_count=args.conjunctionwordscount, conjunction_words_min=args.conjunctionwordsmin, skip_domains=args.skipdomains)