import random
from copy import deepcopy


class Connection:
    def __init__(self, in_node: 'Node', out_node: 'Node', weight: float, innovation_num: int):
        self.in_node = in_node
        self.out_node = out_node
        self.weight = weight
        self.enabled = True
        self.innovation_num = innovation_num
        
    def mutate_weight(self, perturb_chance: float):
        rand = random.uniform(0, 1)
        if rand > perturb_chance:
            self.weight = random.uniform(-1, 1)
        else:
            self.weight += random.gauss(0, 1) / 50
            # keep the weights bounded to not overpower another connection
            if self.weight > 1:
                self.weight = 1
            elif self.weight < -1:
                self.weight = -1
                
    def __copy__(self, in_node=None, out_node=None):
        copy = deepcopy(self)
        if in_node is not None:
            copy.in_node = in_node
        if out_node is not None:
            copy.out_node = out_node
        return copy
    
