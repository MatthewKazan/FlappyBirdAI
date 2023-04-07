from random import random

from Player import Player


class Species:
    def __init__(self, player=None):
        self.players = []
        self.best_score = 0
        self.best_brain = None
        
        self.disjoint_multiplier = 1
        self.weight_multiplier = 0.5
        self.threshold = 3
        self.staleness = 0
        
        if player is not None:
            self.players.append(player)
            self.best_player = player
            self.best_score = player.fitness_level()
            
    def is_in_species(self, player):
        disjoint = self.get_disjoint(player.agent, self.best_player.agent)
        average_diff = self.average_diff(player.agent, self.best_player.agent)
        
        normalizer = 1 if len(player.agent.connections) - 20 < 1 else len(player.agent.connections) - 20
        return self.disjoint_multiplier * disjoint / normalizer + self.weight_multiplier * average_diff < self.threshold
    
    def add_player(self, player):
        self.players.append(player)
        if player.fitness_level() > self.best_score:
            self.best_score = player.fitness_level()
            self.best_player = player

    def average_diff(self, genome, genome1):
        joint_genes = 0
        total_diff = 0
        for gene in genome.connections:
            for gene1 in genome1.connections:
                if gene.innovation_num == gene1.innovation_num:
                    joint_genes += 1
                    total_diff += abs(gene.weight - gene1.weight)
                    break
        if joint_genes == 0:
            return 100
        return total_diff / joint_genes
    def get_disjoint(self, genome, genome1):
        joint_genes = 0
        for gene in genome.connections:
            for gene1 in genome1.connections:
                if gene.innovation_num == gene1.innovation_num:
                    joint_genes += 1
        return len(genome.connections) + len(genome1.connections) - 2 * joint_genes
    
    def average_fitness(self):
        total = 0
        for player in self.players:
            total += player.fitness_level()
        return total / len(self.players)
    
    def sort_species(self):
        self.players.sort(key=lambda x: x.fitness_level(), reverse=True)
        if self.best_score <= self.players[0].fitness_level():
            self.staleness += 1
        else:
            self.staleness = 0
            self.best_score = self.players[0].fitness_level()
            self.best_player = self.players[0]
            
    def get_pseudo_random_player(self):
        score_sum = sum([player.fitness_level() for player in self.players])
        rand = random() * score_sum
        seen_scores = 0
        for player in self.players:
            seen_scores += player.fitness_level()
            if seen_scores >= rand:
                return player
        Exception("No player found")
            
    def create_new_life_and_new_civilization(self, innovation_history):
        my_baby = None
        if random() < 0.25:
            my_baby = self.get_pseudo_random_player() # TODO: this might cause problems from not deep copying
        else:
            mom = self.get_pseudo_random_player()
            dad = self.get_pseudo_random_player()
            
            if mom.fitness_level() < dad.fitness_level():
                my_baby_brain = dad.agent.crossover(mom.agent, innovation_history)
            else:
                my_baby_brain = mom.agent.crossover(dad.agent, innovation_history)
            my_baby = Player(dad.pipes, agent=my_baby_brain)
        my_baby.agent.mutate(innovation_history)
        return my_baby
            