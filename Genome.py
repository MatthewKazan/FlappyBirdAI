
import random

from Node import Node
from Connection import Connection
from innovationHistory import ConnectionHistory
import globfile as glob

class Genome:
    def __init__(self, num_inputs: int, num_outputs: int, layers=2):
        self.num_inputs: int = num_inputs
        self.num_outputs: int = num_outputs
        self.layers: int = layers
        self.connections: list[Connection] = []
        self.nodes: list[Node] = []
        self.input_nodes: list[Node] = []
        self.output_nodes: list[Node] = []
        self.hidden_nodes: list[Node] = []
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
    
    def __str__(self):
        ret = "Inputs:  " + str(self.num_inputs) + "\n"
        ret += "Outputs: " + str(self.num_outputs)
        ret += "Nodes: " + str([str(x.id) + "\n" for x in self.hidden_nodes])
        ret += "Connections: " + str([str(x.in_node) + " -> " + str(x.out_node) for x in self.connections])
        return ret
        
        
    def connect_nodes(self):
        # remove all connections so when reconnecting after mutation there are no errors
        for node in self.nodes:
            node.out_connections = []
        for connection in self.connections:
            connection.in_node.out_connections.append(connection.outNode)
            
    def next_move(self, input_features: list[float]):
        if len(input_features) != self.num_inputs:
            raise Exception('Input feature list is not equal to number of inputs')
        # add input features to input nodes
        for i in range(self.num_inputs):
            self.input_nodes[i].output = input_features[i]

        # sort the nodes by layer to perform feedforwarding
        self.nodes.sort(key=lambda n: n.layer)
        for node in self.nodes:
            node.feed_forward()

        # get outputs from final layer
        outputs = [node.output for node in self.output_nodes]

        for node in self.nodes:
            node.input_sum = 0

        return outputs

    def add_connection(self, innovation_history):
        # make sure the input node is not an output node and the output node is not an input node
        # filter out output nodes  and nodes already connected to everything as the new input connection
        non_output_nodes = [node for node in self.nodes if node.layer != self.layers - 1
                            and len(node.out_connections) != len(self.nodes) - self.num_inputs - 1]     # subtract one for the bias node
        input_node = random.choice(non_output_nodes)
        # filter out input nodes and previously chosen layer and nodes already connected to as the new output connection
        non_input_nodes = [node for node in self.nodes if node.layer != 0
                           and node.id != input_node.layer
                           and node not in input_node.out_connections.out_node]
        output_node = random.choice(non_input_nodes)
        
        # swap the input and output nodes if the input node is on a higher layer than the output node
        if input_node.layer > output_node.layer:
            input_node, output_node = (lambda x, y: (y, x))(input_node, output_node)

        # create a new connection
        new_connection = Connection(
            in_node=input_node, out_node=output_node, weight=random.uniform(-1, 1),
            # TODO: Fix the connection history (do we realy need a connection history class
            innovation_num=innovation_history.get_innovation_num(input_node, output_node))

        # add the connection to the genome
        self.connections.append(new_connection)

        # add the connection to the nodes
        input_node.out_connections.append(new_connection)
        
    def get_innovation_num(self, innovation_history: list, in_node: Node, out_node: Node):
        for innovation in innovation_history:
            if innovation.matches(self, in_node, out_node):
                return innovation.innovation_num
        
        # if it is a new mutation, add it to the history
        connection_innovation_number = glob.next_connection_number
        
        # set innovation numbers for the new state of the genome
        new_innovation_nums = [connection.innovation_num for connection in self.connections]
        # add this mutation to the innovation history
        innovation_history.append(ConnectionHistory(in_node.id, out_node.id, connection_innovation_number, new_innovation_nums))
        glob.next_connection_number += 1
        
        return connection_innovation_number
    
    def add_node(self, innovation_history):
        # TODO: NOT WORKING YET
        if len(self.connections) == 0:
            self.add_connection(innovation_history)
            return
        # get a random connection to split that is not the bias node connection
        new_connection = random.choice(filter(lambda c: c.in_node.id != self.bias_node_id, self.connections))

        # disable the connection
        new_connection.enabled = False
        
        # create a new node
        new_node = Node(id=len(self.nodes), layer=new_connection.in_node.layer + 1)
        self.nodes.append(new_node)
        self.hidden_nodes.append(new_node)
        
        # create a new connection to the new node
        connection_innovation_number = self.get_innovation_num(innovation_history, new_connection.in_node, new_node)
        self.connections.append(Connection(new_connection.in_node, new_node, 1, connection_innovation_number))
        
        # get the connection innovation number for the new connection
        connection_innovation_number = self.get_innovation_num(innovation_history, new_node, new_connection.out_node)
        self.connections.append(Connection(new_node, new_connection.out_node, new_connection.weight, connection_innovation_number))
        
        # connect the bias node to the new node
        bias_node = self.nodes[self.bias_node_id]   # TODO: not sure if this is correct
        connection_innovation_number = self.get_innovation_num(innovation_history, bias_node, new_node)
        self.connections.append(Connection(bias_node, new_node, 0, connection_innovation_number))
        
        # push back other layers if needed
        if new_node.layer == new_connection.out_node.layer:
            # don't include the new node in this filter
            for node in filter(lambda n: n.id != new_node.id, self.nodes):
                if node.layer >= new_node.layer:
                    node.layer += 1
            self.layers += 1
        
        self.connect_nodes()
        
    def is_fully_connected(self) -> bool:
        # calculate how many nodes are in each layer
        nodes_per_layer = [0] * self.layers
        for node in self.nodes:
            nodes_per_layer[node.layer] += 1
        
        # return false if a node's output connections are not equal to the amount of nodes in the next layer
        for node in filter(lambda n: n.layer != self.layers - 1, self.nodes):   # don't include the output nodes
            if len(node.out_connections) != nodes_per_layer[node.layer + 1]:
                return False
            
        return True
        
    def mutate(self, innovation_history, mutate_weight_chance=0.8, perturb_weight_chance=0.9, new_connection_chance=0.05, new_node_chance=0.03):
        if len(self.connections) == 0:
            self.add_connection(innovation_history)
        
        # generate random number between 0-1
        rand = random.uniform(0, 1)
        if rand < mutate_weight_chance:
            for connection in self.connections:
                connection.mutate_weight(perturb_weight_chance)
                
        rand = random.uniform(0, 1)
        if rand < new_connection_chance:
            self.add_connection(innovation_history)
            
        rand = random.uniform(0, 1)
        if rand < new_node_chance:
            self.add_node(innovation_history)
            
    def crossover(self, parent2: 'Genome', innovation_history: list):
        child = Genome(self.num_inputs, self.num_outputs, layers=self.layers)
        child.bias_node_id = self.bias_node_id
        
        