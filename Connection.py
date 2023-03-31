from Node import Node

class Connection:
    def __init__(self, in_node: Node, out_node: Node, weight: float, innovation_num: int):
        self.in_node = in_node
        self.out_node = out_node
        self.weight = weight
        self.enabled = True
        self.innovation_num = innovation_num
