from random import random

from Player import Player


class Species:
    def __init__(self, player=None):
        self.players = []
        self.best_score = 0
        self.best_agent = None
        self.best_player = None
        self.average_fitness = 0
        
        self.disjoint_multiplier = 1
        self.weight_multiplier = 0.5
        self.threshold = 3
        self.staleness = 0
        
        if player is not None:
            self.players.append(player)
            self.best_player = player
            self.best_score = player.fitness_level()
            
    def is_in_species(self, agent: 'Genome'):
        disjoint = self.get_disjoint(agent, self.best_player.agent)
        average_diff = self.average_diff(agent, self.best_player.agent)
        
        normalizer = 1 if len(agent.connections) - 20 < 1 else len(agent.connections) - 20
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
    
    def set_average_fitness(self):
        total_fitness = sum([player.fitness_level() for player in self.players])
        self.average_fitness = total_fitness / len(self.players)
    
    def sort_species(self):
        self.players.sort(key=lambda p: p.fitness_level(), reverse=True)
        
        if len(self.players) == 0:
            self.staleness = 200
            return
        
        # check for new best player
        if self.best_score <= self.players[0].fitness_level():
            self.staleness += 1
        else:
            self.staleness = 0
            self.best_score = self.players[0].fitness_level()
            self.best_player = self.players[0].__copy__()
            self.best_agent = self.players[0].agent.__copy__()
            
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
            my_baby = self.get_pseudo_random_player()  # TODO: this might cause problems from not deep copying
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
    
    def hatch_egg(self, innovation_history, clone_chance=0.25):
        if random() < clone_chance:
            baby_bird = self.get_pseudo_random_player().__copy__()
        else:
            mama_bird = self.get_pseudo_random_player()
            papa_bird = self.get_pseudo_random_player()
            
            if mama_bird.fitness_level() < papa_bird.fitness_level():
                baby_bird_brain = papa_bird.agent.crossover(mama_bird.agent, innovation_history)
            else:
                baby_bird_brain = mama_bird.agent.crossover(papa_bird.agent, innovation_history)
            baby_bird = Player(papa_bird.pipes, agent=baby_bird_brain)
            
        baby_bird.agent.mutate(innovation_history)
        return baby_bird
    
    def cull(self):
        # kill off the bottom half of the species
        if len(self.players) <= 2:
            return
        self.sort_species()
        self.players = self.players[:int(len(self.players) / 2)]
        
    def share_fitness(self):
        for player in self.players:
            player.fitness /= len(self.players)
            