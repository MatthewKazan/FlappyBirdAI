import unittest
from Genome import Genome


class TestGenome(unittest.TestCase):
	def setUp(self) -> None:
		self.agent = Genome(num_inputs=2, num_outputs=1, layers=2)
		self.innovationHistory = []
		self.agent2 = Genome(num_inputs=2, num_outputs=1, layers=2)
		
	def test_genome_constructor(self):
		self.assertEqual(len(self.agent.nodes), 4)
		self.assertEqual(len(self.agent.connections), 0)
		
	def test_add_connection(self):
		print(self.agent)
		self.assertFalse(self.agent.is_fully_connected())
		self.agent.add_connection(self.innovationHistory)
		self.assertEqual(len(self.agent.connections), 1)
		print(self.agent)
		self.agent.add_connection(self.innovationHistory)
		self.assertEqual(len(self.agent.connections), 2)
		print(self.agent)
		self.agent.add_connection(self.innovationHistory)
		self.assertEqual(len(self.agent.connections), 3)
		print(self.agent)
		self.assertTrue(self.agent.is_fully_connected())
		with self.assertRaises(Exception):
			self.agent.add_connection(self.innovationHistory)
		print(self.agent)
		
	def test_innovation_number_no_new_nodes(self):
		self.agent.add_connection(self.innovationHistory)
		self.agent.add_connection(self.innovationHistory)
		self.agent.add_connection(self.innovationHistory)
		# check to make sure the first agent is fully connected
		self.assertTrue(self.agent.is_fully_connected())
		print(self.agent)
		
		self.agent2.add_connection(self.innovationHistory)
		self.agent2.add_connection(self.innovationHistory)
		for connection in self.agent2.connections:
			matching_connection = self.agent.connections[connection.innovation_num]
			self.assertEqual(connection.in_node.id, matching_connection.in_node.id)
			self.assertEqual(connection.out_node.id, matching_connection.out_node.id)
		print(self.agent2)
		
	def test_add_node(self):
		# add a connection then 2 nodes
		self.agent.add_connection(self.innovationHistory)
		self.agent.add_node(self.innovationHistory)
		self.assertEqual(self.agent.layers, 3)
		self.agent.add_node(self.innovationHistory)
		self.assertEqual(len(self.agent.nodes), 6)

		# connect all nodes for agent (main)
		while not self.agent.is_fully_connected():
			self.agent.add_connection(self.innovationHistory)
		# print(self.agent)
		
		self.agent2.add_connection(self.innovationHistory)
		self.agent2.add_node(self.innovationHistory)
		self.assertEqual(self.agent2.layers, 3)
		self.agent2.add_node(self.innovationHistory)
		self.assertEqual(len(self.agent2.nodes), 6)

		# connect all nodes for agent2
		while not self.agent2.is_fully_connected():
			self.agent2.add_connection(self.innovationHistory)
		print(self.agent)
		print(self.agent2)
	
	def test_mutate_connection_weight(self):
		print(self.agent)
		self.agent.add_connection(self.innovationHistory)
		print(self.agent)
		self.agent.mutate(self.innovationHistory)
		self.assertEqual(len(self.agent.connections), 1)
		print(self.agent)
		
	def test_mutate_new_connection(self):
		print(self.agent)
		self.agent.add_connection(self.innovationHistory)
		print(self.agent)
		self.agent.mutate(self.innovationHistory, new_connection_chance=1, new_node_chance=0, mutate_weight_chance=0)
		self.assertEqual(len(self.agent.connections), 2)
		print(self.agent)
		self.agent.mutate(self.innovationHistory, new_connection_chance=1, new_node_chance=0, mutate_weight_chance=0)
		self.assertEqual(len(self.agent.connections), 3)
		print(self.agent)
		
	def test_splice(self):
		arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
		del arr[1:]
		self.assertEqual(arr, [1])
		
	def test_crossover(self):
		base_agent = Genome(num_inputs=1, num_outputs=1, layers=2)
		while not base_agent.is_fully_connected():
			base_agent.add_connection(self.innovationHistory)
		
		agent_with_node = Genome(num_inputs=1, num_outputs=1, layers=2)
		while not agent_with_node.is_fully_connected():
			agent_with_node.add_connection(self.innovationHistory)
		agent_with_node.add_node(self.innovationHistory)
		
		baby1 = agent_with_node.crossover(base_agent)
		baby2 = base_agent.crossover(agent_with_node)
		print("base:\n", base_agent)
		print(baby2)
		print("added node:\n", agent_with_node)
		print("baby:\n", baby1)
	
	
if __name__ == '__main__':
	unittest.main()
	