from copy import deepcopy


class ConnectionHistory:
	def __init__(self, in_node_id, out_node_id, innovation_number, innovation_nums):
		self.in_node_id = in_node_id
		self.out_node_id = out_node_id
		self.innovation_number = innovation_number
		# TODO: Check that this copies the list
		self.innovation_nums = deepcopy(innovation_nums)
		
	def matches_genome(self, genome, in_node, out_node):
		if self.in_node_id == in_node.id and self.out_node_id == out_node.id:
			# check if the innovation number is in the genome's innovation history
			for connectionGene in genome.connections:
				if connectionGene.innovation_num not in self.innovation_nums:
					return False
			# if we reach this point the genomes are identical and the connection is between the same nodes
			return True
		return False
	
	def __str__(self):
		return f"ConnectionHistory(in_node: {self.in_node_id}, out_node: {self.out_node_id}, inno: {self.innovation_number}, nums: {self.innovation_nums})"
	