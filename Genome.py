
import random

from Node import Node
from Connection import Connection
from innovationHistory import ConnectionHistory
import globfile as glob

class Genome:
    def __init__(self, num_inputs: int, num_outputs: int, crossover=False, layers=2):
        self.num_inputs: int = num_inputs
        self.num_outputs: int = num_outputs
        self.layers: int = layers
        self.connections: list[Connection] = []
        self.nodes: list[Node] = []
        self.input_nodes: list[Node] = []
        self.output_nodes: list[Node] = []
        self.hidden_nodes: list[Node] = []
        # self.next_node_id = 0 # id of the next node to add that is not an input or output node
        
        if crossover:
            return 

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
        ret += "Outputs: " + str(self.num_outputs)  + "\n"
        ret += "Nodes: " + str([str(x.id) for x in self.nodes]) + "\n"
        ret += "Connections: " + str([str(x.in_node.id) + " ->(" + str(round(x.weight, 3)) + ", " + str(x.innovation_num) + ") " + str(x.out_node.id) for x in self.connections]) + "\n"
        return ret
        
        
    def connect_nodes(self):
        # remove all connections so when reconnecting after mutation there are no errors
        for node in self.nodes:
            node.out_connections = []
        for connection in self.connections:
            connection.in_node.out_connections.append(connection)
            
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
        if self.is_fully_connected():
            Exception("Genome is fully connected")
            
        # from_node_choices = [node for node in self.nodes if node.layer != self.layers - 1 # TODO: This might be wrong
        #                     and len(node.out_connections) < len(list(filter(lambda n: n.layer > node.layer, self.nodes)))]
        # from_node: Node = random.choice(from_node_choices)
        # # filter out input nodes and previously chosen layer and nodes already connected to as the new output connection
        # to_node_choices = [node for node in self.nodes if node.layer != 0
        #                        and node.id != from_node.layer
        #                        and not from_node.is_connected_to(node)]
        # 
        # to_node = random.choice(to_node_choices)
        
        from_node: Node = random.choice(self.nodes)
        to_node: Node = random.choice(self.nodes)
        while from_node.layer == to_node.layer or from_node.is_connected_to(to_node):
            from_node = random.choice(self.nodes)
            to_node = random.choice(self.nodes)
        
        # swap the input and output nodes if the input node is on a higher layer than the output node
        if from_node.layer > to_node.layer:
            from_node, to_node = (lambda x, y: (y, x))(from_node, to_node)

        # create a new connection
        new_connection = Connection(
            in_node=from_node, out_node=to_node, weight=random.uniform(-1, 1),
            # TODO: Fix the connection history (do we really need a connection history class
            innovation_num=self.get_innovation_num(innovation_history, from_node, to_node))

        # add the connection to the genome
        self.connections.append(new_connection)

        # add the connection to the nodes
        from_node.out_connections.append(new_connection)
        
    def get_innovation_num(self, innovation_history: list[ConnectionHistory], in_node: Node, out_node: Node):
        for innovation in innovation_history:
            if innovation.matches_genome(self, in_node, out_node):
                Exception('Innovation number already exists')
                return innovation.innovation_number
        
        # if it is a new mutation, add it to the history
        connection_innovation_number = glob.next_connection_number
        
        # set innovation numbers for the new state of the genome
        new_innovation_nums = [connection.innovation_num for connection in self.connections]
        # add this mutation to the innovation history
        innovation_history.append(ConnectionHistory(in_node.id, out_node.id, connection_innovation_number, new_innovation_nums))
        glob.next_connection_number += 1
        
        return connection_innovation_number
    
    def add_node(self, innovation_history):
        if len(self.connections) == 0:
            self.add_connection(innovation_history)
            return
        # get a random connection to split that is not the bias node connection
        new_connection = random.choice(self.connections)
        while new_connection.in_node.id == self.bias_node_id and len(self.connections) != 1:
            new_connection = random.choice(self.connections)
        #new_connection = random.choice(list(filter(lambda c: c.in_node.id != self.bias_node_id, self.connections)))

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
        new_node.out_connections.append(new_connection.out_node)
        
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
            nodes_per_layer[node.layer] += 1 # TODO: this is fucked
        
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
            
    def crossover(self, other_parent: 'Genome', innovation_history: list, disable_gene_chance=0.75):
        child = Genome(self.num_inputs, self.num_outputs, crossover=True, layers=self.layers)
        child.bias_node_id = self.bias_node_id # TODO: Might need to store and pass copy of actual bias node
        
        child_connection_genes: list[Connection] = []
        is_enabled: list[bool] = []
        
        for connection in self.connections:
            is_child_connection_enabled = True
            other_parent_connection = self.matching_connection(other_parent, connection.innovation_num)
            
            # if the two parents have a matching connection gene
            if not other_parent_connection is None: 
                if not connection.enabled or not other_parent_connection.enabled:
                    if random.uniform(0, 1) < disable_gene_chance:
                        is_child_connection_enabled = False
                
                # randomly choose which parent to take the gene from
                if random.uniform(0, 1) < 0.5:
                    child_connection_genes.append(connection)
                else:
                    child_connection_genes.append(other_parent_connection)
            
            # deal with disjoint or excess connection genes
            else:
                child_connection_genes.append(connection)
                is_child_connection_enabled = connection.enabled
            is_enabled.append(is_child_connection_enabled)
        
        # all excess and disjoint nodes are inherited from the more fit parent (this Genome) so the structure is the
        # same as this parents structure a.k.a. we can copy over all the nodes
        for node in self.nodes:
            child.nodes.append(node.__copy__())
            
        for node in self.input_nodes:
            child.input_nodes.append(node.__copy__())
        
        for node in self.output_nodes:
            child.output_nodes.append(node.__copy__())
        
        # copy all the connections
        for child_connection, is_child_enabled in zip(child_connection_genes, is_enabled):
            child_in_node = child.get_node(child_connection.in_node.id)
            child_out_node = child.get_node(child_connection.out_node.id)
            child.connections.append(child_connection.__copy__(child_in_node, child_out_node))
            child_connection.enabled = is_child_enabled
        
        child.connect_nodes()
        return child
    
    def __copy__(self):
        copy = Genome(self.num_inputs, self.num_outputs, True, layers=self.layers)
        
        for node in self.nodes:
            copy.nodes.append(node.__copy__())

        for node in self.input_nodes:
            copy.input_nodes.append(node.__copy__())

        for node in self.output_nodes:
            copy.output_nodes.append(node.__copy__())
            
        for connection in self.connections:
            copy.connections.append(connection.__copy__(copy.get_node(connection.in_node.id),
                                                        copy.get_node(connection.out_node.id)))
            
        copy.bias_node_id = self.bias_node_id
        copy.connect_nodes()

        return copy
        
    def get_node(self, node_id: int):
        for node in self.nodes:
            if node.id == node_id:
                return node
        
        Exception("No nodes found with node id:", node_id)
        return None
        
    def matching_connection(self, other_parent: 'Genome', innovation_num: int):
        for other_parent_connection in other_parent.connections:
            if other_parent_connection.innovation_num == innovation_num:
                return other_parent_connection
            
        return None
        