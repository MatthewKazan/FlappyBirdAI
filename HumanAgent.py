import sys

import pygame
from pygame import QUIT, K_ESCAPE, KEYDOWN


class HumanAgent:
    def __init__(self):
        pass

    def next_move(self, player):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and (
                event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                return 1
            if event.type == QUIT or (
                event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
        return 0
