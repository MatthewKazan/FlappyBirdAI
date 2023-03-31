import sys

import pygame

import Player
import globfile
from Genome import Genome
from HumanAgent import HumanAgent
from Pipes import Pipes


class Population:
    def __init__(self, size, dt):
        self.players = []
        self.innovationHistory = []
        self.pipes = Pipes(-128  * dt, 32)
        n_inputs = 4
        n_outputs = 1
        layers = 2
        for i in range(size):
            self.players.append(Player.Player(int(globfile.SCREENWIDTH * 0.2),
                                              globfile.SCREENHEIGHT / 2 + i * 2,
                                              Genome(n_inputs, n_outputs, layers), self.pipes))
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
        for player in self.players:
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
