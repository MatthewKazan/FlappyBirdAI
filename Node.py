import math
from Connection import Connection


def sigmoid(x: float):
    return 1.0 / (1.0 + (math.e ** -x))


class Node:
    def __init__(self, id: int, layer: int):
        self.id: int = id
        # the input has already been calculated when sending outputs from other nodes
        self.input_sum: int = 0
        self.output: int = 0
        self.out_connections: list[Connection] = []
        self.layer: int = layer

    def activate(self):
        if self.layer != 0:
            self.output = sigmoid(self.input_sum)
        for connection in self.out_connections:
            if connection.enabled:
                connection.out_node.input += self.output * connection.weight
                
    def is_connected_to(self, node):
        for connection in self.out_connections:
            if connection.outNode == node:
                return True
        return node.isConnectedTo(self)
