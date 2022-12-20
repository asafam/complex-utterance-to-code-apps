from tasks.task import Task
import random
from utils import task_utils

class RewriteTask(Task):
    def sample(self, k, options):
        sizes = options['sizes']
        weights = options['size_weights']
        skip_domains = options['skip_domains']
        domains_dir_path = options['domains_dir_path']
        conjunction_file_path = options['conjunction_file_path']
        conjunction_limit = options['conjunction_limit']
        min_conjunctions = options['conjunction_min']
        task = self._build_tasks(k, sizes, weights, domains_dir_path, conjunction_file_path, conjunction_limit, min_conjunctions, skip_domains)
        return task
    
    def _build_tasks(self, k, sizes, weights, domains_dir_path, conjunction_file_path, conjunction_limit, min_conjunctions=1, skip_domains=[]):
        tasks = []
        # list domains
        data = task_utils.get_all_data(path=domains_dir_path, skip=skip_domains)
        domains = task_utils.get_all_domains(data)
        
        sample_sizes = random.choices(sizes, k=k, weights=weights)
        for sample_size in sample_sizes:
            task = self._build_task(data, sample_size, domains, conjunction_file_path, conjunction_limit, min_conjunctions)
            tasks.append(task)
        
        return tasks
            
    def _build_task(self, data, sample_size, domains, conjunction_file_path, conjunction_limit, min_conjunctions):
            # randomize domain
            sample_domains = random.sample(domains, sample_size)
            
            # randomize content
            sample_intents = []
            for sample_domain in sample_domains:
                sample_intent = task_utils.sample_subdomain_intent(subdomain=sample_domain[1], data=data)
                sample_intents += sample_intent
                
            # sample conjunctions
            conjunction_words = task_utils.sample_conjunctions_words(path=conjunction_file_path, k=conjunction_limit)
            
            # build the task
            task = {
                'intents': sample_intents,
                'domains': sample_domains,
                'conjunctions': conjunction_words,
                'min_conjunctions': min_conjunctions
            } 
            return task