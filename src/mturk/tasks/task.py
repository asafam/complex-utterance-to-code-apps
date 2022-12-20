from abc import abstractmethod




class Task:
    
    @abstractmethod
    def sample(self, k, options):
        raise NotImplemented