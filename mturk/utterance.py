import copy
import random


CATEGORY_SEQUENCE = 'seq'
CATEGORY_CONDITION = 'cond'


class Utterance:
    
    def __init__(self, all_scenarios, all_domains_groups, all_intents, link_words, quantifiers):
        self.all_scenarios = all_scenarios
        self.all_domains_groups = all_domains_groups
        self.all_intents = all_intents
        self.link_words = link_words
        self.quantifiers = quantifiers
        
    def sample(self, intents_count, link_words_count, quantifiers_count):
        scenario = self.sample_scenario(self.all_scenarios)
        category, intents, link_words, quantifiers = self.sample_intents(intents_count, link_words_count, quantifiers_count)
        link_word_idx = random.choice(range(len(intents))) if link_word else None
        quantifier_idx = random.choice(range(len(intents))) if quantifier else None
        
        return scenario, intents, category, link_word, link_word_idx, quantifier, quantifier_idx
        
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
          
        link_word = self.sample_link_word() if category ==  CATEGORY_CONDITION else None
        quantifier = self.sample_quantifier(count=quantifiers_count)
            
        return category, intents, link_words, quantifiers
    
    def sample_link_word(self):
        link_word = random.choice(self.link_words)
        return link_word
    
    def sample_quantifier(self, quantifier_prob=0.5):
        quantifier = random.choice(self.quantifiers) if random.random() > quantifier_prob else None
        return quantifier