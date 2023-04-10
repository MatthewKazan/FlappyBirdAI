import sys
from math import floor

import pygame

from Player import Player
import globfile
from Genome import Genome
from HumanAgent import HumanAgent
from Pipes import Pipes
from Species import Species
from copy import deepcopy


class Population:
    def __init__(self, size):
        globfile.next_connection_number = 0
        
        self.players: list[Player] = []
        self.best_player = None  # the best player ever
        self.best_score = 0  # best score of the best player ever
        self.global_best_score = 0
        
        self.innovationHistory = []
        
        self.generation = 1
        self.generation_players = []
        self.species: list[Species] = []
        
        self.mass_extinction_event = False
        self.new_stage = False
        self.generations_since_new_world = 0
        
        self.pipes = Pipes(32)
        self.n_inputs = 4
        self.n_outputs = 1
        self.layers = 2
        for _ in range(size):
            # TODO: check if the new player is made correctly
            new_player = Player(self.pipes, agent=Genome(self.n_inputs, self.n_outputs, layers=self.layers))
            self.players.append(new_player)
            new_player.agent.mutate(self.innovationHistory)
            new_player.agent.generate_network()
            
            # TODO: randomly mutate the genome
            
        if 'win' in sys.platform:
            soundExt = '.wav'
        else:
            soundExt = '.ogg'

        self.sounds = {'die': pygame.mixer.Sound('assets/audio/die' + soundExt),
                       'hit': pygame.mixer.Sound('assets/audio/hit' + soundExt),
                       'point': pygame.mixer.Sound(
                           'assets/audio/point' + soundExt),
                       'swoosh': pygame.mixer.Sound(
                           'assets/audio/swoosh' + soundExt),
                       'wing': pygame.mixer.Sound(
                           'assets/audio/wing' + soundExt)}

    def update(self):
        # print([x.innovation_number for x in self.innovationHistory])
        # print(f"###################################################\n{len(self.players)} \n###################################################")
        # i = 0
        for player in self.players:
            # print(f"{i}, {player.agent}")
            # i += 1
            # player.update()
            player.check_crash()
            if player.isAlive:
                self.sounds['hit'].play()
                player.look_around()  # corresponds to look
                player.update()
            if self.pipes.passed(player):
                player.score += 1
                self.sounds['point'].play()
            if player.score > self.global_best_score:
                self.global_best_score = player.score
        self.pipes.update()
        
    def done(self):
        for player in self.players:
            player.check_crash()
            if player.isAlive:
                return False
        return True
    
    def set_best_player(self):
        temp_best = self.species[0].players[0]
        temp_best.generation = self.generation
        
        if temp_best.score >= self.best_score:
            self.generation_players.append(temp_best.__copy__())
            self.best_score = temp_best.score
            self.best_player = temp_best.__copy__()

    def create_species(self):
        species = []
        for player in self.players:
            found_species = False
            for specie in species:
                if specie.is_in_species(player):
                    specie.add_player(player)
                    found_species = True
                    break
            if not found_species:
                species.append(Species(player))
        return species
    
    def speciate(self):
        for specie in self.species:
            specie.players = []
        for player in self.players:
            found_species = False
            for specie in self.species:
                if specie.is_in_species(player.agent):
                    specie.add_player(player)
                    found_species = True
                    break
            if not found_species:
                self.species.append(Species(player))
                
    def calculate_fitness_level(self):
        for player in self.players:
            player.fitness_level()
            
    def sort_species(self):
        for specie in self.species:
            specie.sort_species()
        self.species.sort(key=lambda s: s.best_score, reverse=True)
        
    def total_average_fitness(self, species):
        total = 0
        for s in species:
            total += s.average_fitness
        return total / len(species)
    
    def birth_new_generation(self):  # natural selection
        # species = self.create_species()
        # self.pipes = Pipes(32)
        # for specie in species:
        #     specie.sort_species()
        # species.sort(key=lambda x: x.best_score, reverse=True)
        #
        # babies = []
        # index = 0
        # total_ave = self.total_average_fitness(species)
        # while len(babies) < len(self.players):
        #     specie = species[index]
        #     index = (index + 1) % len(species)
        #     babies.append(Player(self.pipes, agent=specie.best_player.agent))
        #     num_babies = floor(specie.average_fitness() / total_ave * len(self.players)) - 1
        #
        #     for i in range(num_babies):
        #         babies.append(specie.create_new_life_and_new_civilization(self.innovationHistory))
        # self.players = babies
        
        prev_best = self.players[0]
        self.speciate()
        self.calculate_fitness_level()
        self.sort_species()
        
        if self.mass_extinction_event:
            self.mass_extinction()
            self.mass_extinction_event = False
            
        self.cull_species()  # kill the birds that haven't learned how to fly
        self.set_best_player()  # save this generation's best player (tom brady bird)
        self.kill_stale_species(threshold=15)  # kill the species that haven't improved in threshold=15 generations
        self.kill_bad_species()  # kill the species that are so bad they don't deserve the chance to reproduce
        
        print(f"Generation: {self.generation}, mutations: {len(self.innovationHistory)}, species: {len(self.species)} =======================")
        
        sum_of_species_average = sum([s.average_fitness for s in self.species])
        baby_birds = []
        for specie in self.species:
            baby_birds.append(specie.best_player.__copy__())
            # the number of babies this species is allowed (-1 because the best player is already added)
            num_babies = floor(specie.average_fitness / sum_of_species_average * len(self.players)) - 1
            
            for _ in range(num_babies):
                baby_birds.append(specie.hatch_egg(self.innovationHistory))
        
        # if we don't have enough babies we need to fix that
        # first we need to keep the best
        if len(baby_birds) < len(self.players):
            baby_birds.append(prev_best.__copy__())
        
        print(f"baby birds: {len(baby_birds)}")
        print(f"players: {len(self.players)}")
        print(f"species: {len(self.species)}")
        while len(baby_birds) < len(self.players):
            baby_birds.append(self.species[0].hatch_egg(self.innovationHistory))  # only take from the best species b/c elitism

        # aliasing errors suck so lets be extra careful
        self.players = []
        for bird in baby_birds:
            self.players.append(bird.__copy__())
        self.generation += 1
        
        # unscramble the baby birds brains
        for baby_bird in self.players:
            baby_bird.agent.generate_network()
    
    def mass_extinction(self):
        for i in range(5, len(self.species)):
            del self.species[i][1:]
            
    def cull_species(self):
        for specie in self.species:
            specie.cull()
            specie.share_fitness()
            specie.set_average_fitness()
            
    def kill_stale_species(self, threshold=15):
        for specie in self.species:
            if specie.staleness >= threshold:
                self.species.remove(specie)
                
    def kill_bad_species(self):
        sum_of_species_average = sum([specie.average_fitness for specie in self.species])
        
        for specie in self.species[1:]:
            if specie.average_fitness / sum_of_species_average * len(self.players) < 1:
                # TODO: check that remove works (he uses splice)
                self.species.remove(specie)

    def draw(self, screen):
        for player in self.players:
            player.draw(screen)
        self.pipes.draw(screen)
