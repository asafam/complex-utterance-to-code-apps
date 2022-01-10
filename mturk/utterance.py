import copy
import random


CATEGORY_SEQUENCE = 'seq'
CATEGORY_CONDITION = 'cond'


class Utterance:
    
    def __init__(self, all_scenarios, all_domains_groups, all_intents, link_words, quantifiers, seed=None):
        self.all_scenarios = all_scenarios
        self.all_domains_groups = all_domains_groups
        self.all_intents = all_intents
        self.all_link_words = link_words
        self.all_quantifiers = quantifiers
        if seed:
            random.seed(seed)
        
    def sample(self, intents_count, link_words_count, quantifiers_count, min_intents_values=[2, 3, 4], min_intents_weights=[0.85, 0.13, 0.02]):
        scenario = self.sample_scenario(self.all_scenarios)
        intents, link_words, quantifiers = self.sample_intents(intents_count, link_words_count, quantifiers_count)
        link_word_idx = random.choice(range(len(intents))) if link_words else None
        quantifier_idx = random.choice(range(len(intents))) if quantifiers else None
        min_intents = random.choices(min_intents_values, weights=min_intents_weights, k=1)[0]
        
        return scenario, intents, link_words, link_word_idx, quantifiers, quantifier_idx, min_intents
        
    def sample_scenario(self, all_scenarios):
        scenario = random.choice(all_scenarios)
        return scenario
    
    def sample_domains_group(self, all_domains_groups):
        all_domains = [domains['domains'] for domains in all_domains_groups]
        all_weights = [domains['weight'] for domains in all_domains_groups]
        domains = random.choices(all_domains, weights=all_weights, k=1)[0]
        return domains
    
    def sample_domain(self, prev_domain, domains, all_intents):
        domain = random.choice(domains)
        return domain
    
    def sample_domain_intents(self, all_intents, domain, ret_type=None, pop=True):
        domain_intents = all_intents[domain] if domain in all_intents else []
        intents = [(i, intent) for (i, intent) in enumerate(domain_intents) if intent[ret_type]]
        if len(intents) == 0:
            return None
        
        index, intent = random.choice(intents)
        
        if pop and intent:
            domain_intents.pop(index)
            if len(domain_intents) == 0:
                all_intents.pop(domain, None)
        
        return intent
    
    def sample_intents(self, intents_count, link_words_count, quantifiers_count, ratio_seq=0.3, limit=None, limits=[2, 3], limits_weights=[0.85, 0.15], shuffle=True):
        intents = []
        all_intents_copy = copy.deepcopy(self.all_intents)
        
        while len(intents) < intents_count:    
            category = CATEGORY_SEQUENCE if random.random() < ratio_seq else CATEGORY_CONDITION
            prev_domain = None
            
            if limit is None:
                limit = random.choices(limits, weights=limits_weights, k=1)[0]
            
            cond_limit = 0 if category == CATEGORY_SEQUENCE else random.choice(list(range(1, limit)))
            cond_count = 0
            
            for i in range(limit):
                intent = None
                domains = self.sample_domains_group(self.all_domains_groups)
                
                while intent is None: # in some iterations the sampled domain is empty
                    # sample domain 
                    domain = self.sample_domain(prev_domain, domains, all_intents_copy)
                    # get required return type
                    ret_type = random.choice(['bool'] * (cond_limit - cond_count) + ['void'] * (limit - i)) 
                    # sample intent by domain and required return type
                    intent = self.sample_domain_intents(all_intents_copy, domain, ret_type)
                    
                    if intent:
                        intents.append((domain, intent, ret_type))
                        cond_count += 1 if ret_type == CATEGORY_CONDITION else 0
                        prev_domain = domain
        
        if shuffle:
            random.shuffle(intents)
          
        link_words = self.sample_link_words(count=link_words_count)
        quantifiers = self.sample_quantifiers(count=quantifiers_count)
            
        return intents, link_words, quantifiers
    
    def sample_link_words(self, count):
        link_words = random.sample(self.all_link_words, count)
        return link_words
    
    def sample_quantifiers(self, count):
        quantifiers = random.sample(self.all_quantifiers, count)
        return quantifiers