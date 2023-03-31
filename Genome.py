
import random

from Node import Node
from Connection import Connection


class Genome:
    def __init__(self, num_inputs: int, num_outputs: int, layers=2):
        self.num_inputs: int = num_inputs
        self.num_outputs: int = num_outputs
        self.layers: int = layers
        self.connections: list[Connection] = []
        self.nodes: list[Node] = []
        self.input_nodes: list[Node] = []
        self.output_nodes: list[Node] = []
        # self.next_node_id = 0 # id of the next node to add that is not an input or output node

        # add input nodes equivalent to the number of input features
        for i in range(num_inputs):
            input_node = Node(id=i, layer=0)
            self.nodes.append(input_node)
            self.input_nodes.append(input_node)
            # self.next_node_id += 1

        # add output nodes equivalent to the number of outputs the genome should have (for flappy bird it is 1... flap or dont)
        for i in range(num_outputs):
            output_node = Node(id=i + num_inputs, layer=1)
            self.nodes.append(output_node)
            self.output_nodes.append(output_node)
            # self.next_node_id += 1

        # add the bias node
        self.bias_node_id = len(self.nodes)
        self.nodes.append(Node(id=self.bias_node_id, layer=0))
        
    def connect_nodes(self):
        # remove all connections so when reconnecting after mutation there are no errors
        for node in self.nodes:
            node.out_connections = []
        for connection in self.connections:
            connection.in_node.out_connections.append(connection.outNode)
            

    def next_move(self, input_features: list[float]):
        if len(input_features) != self.num_inputs:
            raise Exception(
                'Input feature list is not equal to number of inputs')
        for i in range(self.num_inputs):
            self.nodes[i].output = input_features[i]

        # sort the nodes by layer to perform feedforwarding
        self.nodes.sort(key=lambda n: n.layer)
        for node in self.nodes:
            node.activate()

        # get outputs from final layer
        outputs = [node.output for node in self.output_nodes]

        for node in self.nodes:
            node.input_sum = 0

        return outputs

    def add_connection(self, innovation_history):
        # get a random input node
        input_node = self.nodes[random.randint(0, len(self.nodes) - 1)]

        # get a random output node
        output_node = self.nodes[random.randint(0, len(self.nodes) - 1)]

        # make sure the input node is not an output node and the output node is not an input node
        while input_node.layer == output_node.layer or input_node.isConnectedTo(output_node):
            input_node = self.nodes[random.randint(0, len(self.nodes) - 1)]
            output_node = self.nodes[random.randint(0, len(self.nodes) - 1)]
        
        if input_node.layer > output_node.layer:
            temp = input_node
            input_node = output_node
            output_node = temp

        # create a new connection
        new_connection = Connection(
            input_node, output_node, random.uniform(-1, 1), True, 0)

        # add the connection to the genome
        self.connections.append(new_connection)

        # add the connection to the nodes
        input_node.out_connections.append(new_connection)
    
    def add_node(self, innovation_history):
        # TODO: NOT WORKING YET
        if len(self.connections) == 0:
            self.add_connection(innovation_history)
            return
        # get a random connection to split
        connection = self.connections[random.randint(0, len(self.connections) - 1)]

        # disable the connection
        connection.enabled = False
        # More to come...
    
    def mutate(self, innovation_history):
        #TODO: Do a random mutation
        return None
