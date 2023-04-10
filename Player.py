import random

import numpy
import pygame
import globfile
from HumanAgent import HumanAgent
from Pipes import Pipes


# from copy import deepcopy


class Player:
    """Player class"""

    def __init__(self, seed=32, x=int(globfile.SCREENWIDTH * 0.2), y=globfile.SCREENHEIGHT / 2, agent=HumanAgent()):
        self.score = 0  # number of pipes the flappy bird has crossed
        
        self.x = x
        self.y = y + random.uniform(-20,20)
        self.playerVelY = -9  # player's velocity along Y, default same as playerFlapped
        self.playerMaxVelY = 10  # max vel along Y, max descend speed
        self.playerMinVelY = -8  # min vel along Y, max ascend speed
        self.playerAccY = 1  # players downward acceleration
        self.playerRot = 45  # player's rotation
        self.playerVelRot = 3  # angular speed
        self.playerRotThr = 20  # rotation threshold
        self.playerFlapAcc = -9  # players speed on flapping
        self.playerFlapped = False  # True when player flaps
        # self.moveInfo = moveInfo
        self.sprites = (
            pygame.image.load(globfile.PLAYERS_LIST[0][0]).convert_alpha(),
            pygame.image.load(globfile.PLAYERS_LIST[0][1]).convert_alpha(),
            pygame.image.load(globfile.PLAYERS_LIST[0][2]).convert_alpha(),
        )
        self.agent: 'Genome' = agent
        self.width = self.sprites[0].get_width() / 1.5
        self.height = self.sprites[0].get_height() / 1.5
        self.rect = pygame.Rect(self.x + self.width / 2, self.y + self.height / 2, self.width,
                                self.height)
        self.seed = seed
        self.pipes = Pipes(self.seed)
        self.isAlive = True
        self.lifespan = 0
        
        # NEAT INFO
        self.fitness = 0  # the fitness score used to breed and annihilate the poorly performing children
        self.sight = []  # the inputs to the neural net
        self.generation = 0
        self.best_score = 0

    def flap(self):
        """Flap the player"""
        self.playerVelY = self.playerFlapAcc
        self.playerFlapped = True

    def check_crash(self):
        self.rect = pygame.Rect(self.x + self.width / 2, self.y + self.height / 2, self.width,
                                self.height)

        if not self.isAlive or self.y + self.height * 2 >= globfile.BASEY - 1 or self.y < 0:
            self.isAlive = False
        elif not self.isAlive or self.pipes.collide(self)[0] or self.pipes.collide(self)[1]:
            self.isAlive = False

    def update(self):
        self.lifespan += 1
        decision = self.agent.next_move(self.sight)[0]
        if decision > .51:
            self.flap()
        # rotate the player
        if self.playerRot > -90:
            self.playerRot -= self.playerVelRot

        # player's movement
        if self.playerVelY < self.playerMaxVelY and not self.playerFlapped:
            self.playerVelY += self.playerAccY
        if self.playerFlapped:
            self.playerFlapped = False

            # more rotation to cover the threshold (calculated in visible rotation)
            self.playerRot = 45

        playerHeight = self.sprites[0].get_height()
        self.y += min(self.playerVelY, globfile.BASEY - self.y - playerHeight)
        self.pipes.update()
        if self.pipes.passed(self):
            self.score += 1

    def look_around(self):
        self.sight = [0] * 4
        closest_pipe = 0
        # 0 input: player y velocity
        self.sight[0] = numpy.interp(self.playerVelY, [-10, 10], [-1, 1])
        # Get the closest pipe
        if self.x < self.pipes.lowerPipes[1]['x'] and \
                (self.pipes.lowerPipes[0]['x'] + self.pipes.width / 2 < self.x or
                 self.pipes.lowerPipes[0]['x'] > self.pipes.lowerPipes[1]['x']):
            closest_pipe = 1
        # 1 input: x distance to next pipe
        self.sight[1] = numpy.interp(
            self.pipes.lowerPipes[closest_pipe]['x'] - self.x,
            [0, globfile.SCREENWIDTH], [0, 1])
        # 2 input: y distance to next lower pipe
        self.sight[2] = numpy.interp(
            (self.pipes.lowerPipes[closest_pipe]['y'] - self.y),
            [0, globfile.SCREENHEIGHT], [0, 1])
        # 3 input: y distance to next upper pipe
        self.sight[3] = numpy.interp((self.y - (
                self.pipes.upperPipes[closest_pipe]['y'] + self.pipes.height)),
                                [0, globfile.SCREENHEIGHT], [0, 1])

    def drop_dead(self):
        # player y shift
        if self.y + self.height < globfile.BASEY - 1:
            self.y += min(self.playerVelY,
                          globfile.BASEY - self.y - self.height)

        # player velocity change
        if self.playerVelY < 15:
            self.playerVelY += self.playerAccY
            
    def fitness_level(self):
        self.fitness = 1 + self.score ** 2 + self.lifespan
            
    def __copy__(self):
        copy = Player()
        copy.agent = self.agent.__copy__()
        copy.fitness = self.fitness
        copy.agent.generate_network()
        copy.generation = self.generation
        copy.best_score = self.best_score
        return copy

    def draw(self, screen):
        if self.isAlive:
            # Player rotation has a threshold
            visibleRot = self.playerRotThr
            if self.playerRot <= self.playerRotThr:
                visibleRot = self.playerRot
    
            playerSurface = pygame.transform.rotate(self.sprites[0], visibleRot)
            screen.blit(playerSurface, (self.x, self.y))
            self.pipes.draw(screen)

