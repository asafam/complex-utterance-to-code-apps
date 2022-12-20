import copy
import random


CATEGORY_SEQUENCE = 'seq'
CATEGORY_CONDITION = 'cond'


class Utterance:
    
    def __init__(self, all_scenarios, all_intents, all_constraints, link_words, quantifiers, seed=None):
        self.all_scenarios = all_scenarios
        self.all_intents = all_intents
        self.all_constraints = all_constraints
        self.all_link_words = link_words
        self.all_quantifiers = quantifiers
        if seed:
            random.seed(seed)
        
    def sample(self, intents_limit, constraints_limit, link_words_count, quantifiers_count, scenarios_count, min_intents_values=[1, 2, 3, 4], min_intents_weights=[0.40, 0.43, 0.13, 0.02], min_constraints_values=[1, 2, 3], min_constraints_weights=[0.90, 0.08, 0.02]):
        scenarios = self.sample_scenarios(limit=scenarios_count)
        intents = self.sample_intents(limit=intents_limit)
        constraints = self.sample_constraints(limit=constraints_limit)
        link_words = self.sample_link_words(count=link_words_count)
        quantifiers = self.sample_quantifiers(count=quantifiers_count)
        min_intents = random.choices(min_intents_values, weights=min_intents_weights, k=1)[0]
        min_constraints = random.choices(min_constraints_values, weights=min_constraints_weights, k=1)[0]
        
        return scenarios, intents, constraints, link_words, quantifiers, min_intents, min_constraints
        
    def sample_scenarios(self, k):
        all_scenarios = self.all_scenarios
        scenarios = random.sample(all_scenarios, k)
        return scenarios
    
    def sample_domain(self, domains):
        domain = random.choice(domains)
        return domain
    
    def sample_intents(self, k=5, shuffle=True):
        intents = self.sample_actions(all_actions=self.all_intents, limit=k, shuffle=shuffle)
        return intents
    
    def sample_constraints(self, k=3, shuffle=True):
        constraints = self.sample_actions(all_actions=self.all_constraints, limit=k, shuffle=shuffle)
        return constraints
        
    def sample_actions(self, all_actions, k, shuffle):
        all_actions_copy = copy.deepcopy(all_actions)
        actions = []
        
        while len(actions) < k:
            for _ in range(k):
                action = None
                
                while action is None: # in some iterations the sampled domain is empty
                    # sample domain 
                    domain = random.choice(list(all_actions_copy.keys()))
                    # sample intent by domain and required return type
                    action = self.sample_domain_actions(all_actions_copy, domain)
                    
                    if action:
                        actions.append((domain, action))
        
        if shuffle:
            random.shuffle(actions)
            
        return actions
    
    def sample_domain_actions(self, all_actions, domain, ret_type=None, pop=True):
        domain_actions = all_actions[domain] if domain in all_actions else []
        actions = [(i, action) for (i, action) in enumerate(domain_actions) if 'disabled' not in action or not action['disabled']]
        if len(actions) == 0:
            return None
        
        index, action = random.choice(actions)
        
        if pop and action:
            domain_actions.pop(index)
            if len(domain_actions) == 0:
                all_actions.pop(domain, None)
        
        return action
    
    def sample_link_words(self, count):
        link_words = random.sample(self.all_link_words, count)
        return link_words
    
    def sample_quantifiers(self, count):
        quantifiers = random.sample(self.all_quantifiers, count)
        return quantifiers