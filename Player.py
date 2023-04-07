import sys

import numpy
import pygame
import globfile
from HumanAgent import HumanAgent


class Player:
    """Player class"""

    def __init__(self, pipes, x=int(globfile.SCREENWIDTH * 0.2), y=globfile.SCREENHEIGHT / 2, agent=HumanAgent()):
        self.score = 0 # number of pipes the flappy bird has crossed
        self.x = x
        self.y = y
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
        self.agent = agent
        self.width = self.sprites[0].get_width()
        self.height = self.sprites[0].get_height()
        self.rect = pygame.Rect(self.x, self.y, self.sprites[0].get_width(),
                                self.sprites[0].get_height())
        self.pipes = pipes
        self.isAlive = True

    def flap(self):
        """Flap the player"""
        self.playerVelY = self.playerFlapAcc
        self.playerFlapped = True

    def checkCrash(self):
        self.rect = pygame.Rect(self.x, self.y, self.sprites[0].get_width(),
                                self.sprites[0].get_height())

        if self.y + self.height >= globfile.BASEY - 1 or self.y < 0:
            self.isAlive = False
        elif self.pipes.collide(self)[0] or self.pipes.collide(self)[1]:
            self.isAlive = False

    def update(self):
        self.lifespan += 1
        decision = self.agent.next_move(self.getState())[0]
        if decision > .5:
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
        #print(self.agent)

    def getState(self):
        dists = [0] * 4
        closest_pipe = 0
        dists[0] = numpy.interp(self.playerVelY, [-10, 10], [-1, 1])
        if self.x < self.pipes.lowerPipes[1]['x'] and \
                (self.pipes.lowerPipes[0]['x'] < self.x or
                 self.pipes.lowerPipes[0]['x'] > self.pipes.lowerPipes[1]['x']):
            closest_pipe = 1
        dists[1] = numpy.interp(
            self.pipes.lowerPipes[closest_pipe]['x'] - self.x,
            [0, globfile.SCREENWIDTH], [0, 1])
        dists[2] = numpy.interp(
            max(0, self.pipes.lowerPipes[closest_pipe]['y'] - self.y),
            [0, globfile.SCREENHEIGHT], [0, 1])
        dists[3] = numpy.interp(max(0, self.y - (
                self.pipes.upperPipes[closest_pipe]['y'] + self.pipes.height)),
                                [0, globfile.SCREENHEIGHT], [0, 1])
        return dists

    def dropDead(self):
        # player y shift
        if self.y + self.height < globfile.BASEY - 1:
            self.y += min(self.playerVelY,
                          globfile.BASEY - self.y - self.height)

        # player velocity change
        if self.playerVelY < 15:
            self.playerVelY += self.playerAccY

    def draw(self, screen):
        if self.isAlive:
            # Player rotation has a threshold
            visibleRot = self.playerRotThr
            if self.playerRot <= self.playerRotThr:
                visibleRot = self.playerRot
    
            playerSurface = pygame.transform.rotate(self.sprites[0], visibleRot)
            screen.blit(playerSurface, (self.x, self.y))

