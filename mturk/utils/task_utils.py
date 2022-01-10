import random
from utils import file_utils


data = []


def get_all_data(path, skip=None):
    data = file_utils.load_all_csv_files(path, skip=skip)
    return data


def get_all_domains(data):
    domains = map(lambda item: (item['domain'], item['subdomain']), data)
    return list(set(domains))


def sample_subdomain_intent(subdomain, data, k=1):
    subdomain_data = get_subdomain_data(subdomain, data)
    sample = random.sample(subdomain_data, k=k)
    return sample

        
def get_subdomain_data(subdomain, data):
    subdomain_data = [ item for item in data if item['subdomain'] == subdomain ]
    return subdomain_data


def sample_conjunctions_words(path, k=1):
    data = file_utils.load_yml_file(path)
    sample = random.sample(data['conditionals'], k=k)
    return sample
