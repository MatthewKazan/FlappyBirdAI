import pygame
from itertools import cycle
import random
import sys
import pygame
from pygame.locals import *
import globfile

class Pipes:
    def __init__(self, pipe1, pipe2, sprites, velocity, hitmasks):
        self.upperPipes = [
            {'x': globfile.SCREENWIDTH + 200, 'y': pipe1[0]['y']},
            {'x': globfile.SCREENWIDTH + 200 + (globfile.SCREENWIDTH / 2), 'y': pipe2[0]['y']},
        ]
        # list of lowerpipe
        self.lowerPipes = [
            {'x': globfile.SCREENWIDTH + 200, 'y': pipe1[1]['y']},
            {'x': globfile.SCREENWIDTH + 200 + (globfile.SCREENWIDTH / 2), 'y': pipe2[1]['y']},
        ]
        self.sprites = sprites
        self.velocity = velocity
        self.hitmasks = hitmasks
        
    def collide(self, player):
        pipeW = self.sprites[0].get_width()
        pipeH = self.sprites[0].get_height()

        for uPipe, lPipe in zip(self.upperPipes, self.lowerPipes):
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

            # player and upper/lower pipe hitmasks
            pHitMask = player.hitmasks
            uHitmask = self.hitmasks[0]
            lHitmask = self.hitmasks[1]

            # if bird collided with upipe or lpipe
            uCollide = self.pixelCollision(player.rect, uPipeRect, pHitMask, uHitmask)
            lCollide = self.pixelCollision(player.rect, lPipeRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return [True, False]

        return [False, False]

    def pixelCollision(self, rect1, rect2, hitmask1, hitmask2):
        """Checks if two objects collide and not just their rects"""
        rect = rect1.clip(rect2)
    
        if rect.width == 0 or rect.height == 0:
            return False
    
        x1, y1 = rect.x - rect1.x, rect.y - rect1.y
        x2, y2 = rect.x - rect2.x, rect.y - rect2.y
    
        for x in range(rect.width):
            for y in range(rect.height):
                if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                    return True
        return False
    
    def passed(self, player):
        for pipe in self.upperPipes:
            if pipe['x'] < player.x:
                return True
        return False
    
    def update(self):
        # move pipes to left
        for uPipe, lPipe in zip(self.upperPipes, self.lowerPipes):
            uPipe['x'] += self.velocity
            lPipe['x'] += self.velocity

        # add new pipe when first pipe is about to touch left of screen
        if 3 > len(self.upperPipes) > 0 and 0 < self.upperPipes[0]['x'] < 5:
            newPipe = self.getRandomPipe()
            self.upperPipes.append(newPipe[0])
            self.lowerPipes.append(newPipe[1])

        # remove first pipe if its out of the screen
        if len(self.upperPipes) > 0 and self.upperPipes[0]['x'] < -self.sprites[0].get_width():
            self.upperPipes.pop(0)
            self.lowerPipes.pop(0)

    def getRandomPipe(self):
        """returns a randomly generated pipe"""
        # y of gap between upper and lower pipe
        gapY = random.randrange(0, int(globfile.BASEY * 0.6 - globfile.PIPEGAPSIZE))
        gapY += int(globfile.BASEY * 0.2)
        pipeHeight = self.sprites[0].get_height()
        pipeX = globfile.SCREENWIDTH + 10
    
        return [
            {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
            {'x': pipeX, 'y': gapY + globfile.PIPEGAPSIZE}, # lower pipe
        ]
    
    def draw(self, screen):
        for uPipe, lPipe in zip(self.upperPipes, self.lowerPipes):
            screen.blit(self.sprites[0], (uPipe['x'], uPipe['y']))
            screen.blit(self.sprites[1], (lPipe['x'], lPipe['y']))