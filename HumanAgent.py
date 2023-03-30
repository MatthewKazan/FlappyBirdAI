import sys

import pygame
from pygame import QUIT, K_ESCAPE, KEYDOWN

class HumanAgent:
    def __init__(self):
        pass
    def nextMove(self, player):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                player.flap()
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
              pygame.quit()
              sys.exit()