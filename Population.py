import sys
from math import floor

import pygame

from Player import Player
import globfile
from Genome import Genome
from HumanAgent import HumanAgent
from Pipes import Pipes
from Species import Species


class Population:
    def __init__(self, size):
        globfile.next_connection_number = 0
        self.players = []
        self.innovationHistory = []
        self.pipes = Pipes(32)
        self.n_inputs = 4
        self.n_outputs = 1
        self.layers = 2
        for i in range(size):
            self.players.append(Player(self.pipes,
                                              agent=Genome(self.n_inputs, self.n_outputs, layers=self.layers)))
            self.players[i].agent.mutate(self.innovationHistory)
            self.players[i].agent.generate_network()
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
        i = 0
        for player in self.players:
            print(f"{i}, {player.agent}")
            i += 1
            player.update()
            if player.checkCrash():
                player.isAlive = False
                self.sounds['hit'].play()
            if self.pipes.passed(player):
                player.score += 1
                self.sounds['point'].play()
        self.pipes.update()

    def draw(self, screen):
        for player in self.players:
            player.draw(screen)
        self.pipes.draw(screen)
        
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
        
    def total_average_fitness(self, species):
        total = 0
        for s in species:
            total += s.average_fitness()
        return total / len(species)
    
    def birth_new_generation(self):
        species = self.create_species()
        self.pipes = Pipes(32)
        for specie in species:
            specie.sort_species()  
        species.sort(key=lambda x: x.best_score, reverse=True)
        
        babies = []
        index = 0
        total_ave = self.total_average_fitness(species)
        while len(babies) < len(self.players):
            specie = species[index]
            index = (index + 1) % len(species)
            babies.append(Player(self.pipes, agent=specie.best_player.agent))
            num_babies = floor(specie.average_fitness() / total_ave * len(self.players)) - 1
            
            for i in range(num_babies):
                babies.append(specie.create_new_life_and_new_civilization(self.innovationHistory))
        self.players = babies
        
