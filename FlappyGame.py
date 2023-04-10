from itertools import cycle
import random
import sys
import pygame
from pygame.locals import *

import globfile
from HumanAgent import HumanAgent
from Pipes import Pipes
from Player import Player
from Population import Population

# Source code for game taken from: https://github.com/sourabhv/FlapPyBird

# image,and sound dicts
IMAGES, SOUNDS = {}, {}

# list of backgrounds
BACKGROUNDS_LIST = (
    'assets/sprites/background-day.png',
    'assets/sprites/background-night.png',
)

def main():
    global SCREEN, FPSCLOCK
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((globfile.SCREENWIDTH, globfile.SCREENHEIGHT))
    pygame.display.set_caption('Flappy Bird')

    # numbers sprites for score display
    IMAGES['numbers'] = (
        pygame.image.load('assets/sprites/0.png').convert_alpha(),
        pygame.image.load('assets/sprites/1.png').convert_alpha(),
        pygame.image.load('assets/sprites/2.png').convert_alpha(),
        pygame.image.load('assets/sprites/3.png').convert_alpha(),
        pygame.image.load('assets/sprites/4.png').convert_alpha(),
        pygame.image.load('assets/sprites/5.png').convert_alpha(),
        pygame.image.load('assets/sprites/6.png').convert_alpha(),
        pygame.image.load('assets/sprites/7.png').convert_alpha(),
        pygame.image.load('assets/sprites/8.png').convert_alpha(),
        pygame.image.load('assets/sprites/9.png').convert_alpha()
    )

    # game over sprite
    IMAGES['gameover'] = pygame.image.load('assets/sprites/gameover.png').convert_alpha()
    # message sprite for welcome screen
    IMAGES['message'] = pygame.image.load('assets/sprites/message.png').convert_alpha()
    # base (ground) sprite
    IMAGES['base'] = pygame.image.load('assets/sprites/base.png').convert_alpha()
    population = Population(20)
    while True:
        # select random background sprites
        randBg = random.randint(0, len(BACKGROUNDS_LIST) - 1)
        IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[randBg]).convert()

        FPSCLOCK.tick(globfile.FPS)
        crashInfo = mainGame(population)
        population.birth_new_generation()
        #showGameOverScreen(crashInfo)


def mainGame(population):
    basex = -28
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()
    #ha = HumanAgent()
    # pipes = Pipes(-128 * dt, 32)
    # player = Player(int(SCREENWIDTH * 0.2), globfile.SCREENHEIGHT/2, ha, pipes)
    # dt = FPSCLOCK.tick(FPS)/1000
    # print(dt)
    # population = Population(2, dt)
    while True:
        # check for crash here
        population.update()
        if all([not p.isAlive for p in population.players]):
            return population.players[0]

        basex = -((-basex + 100) % baseShift)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))
        population.draw(SCREEN)
        SCREEN.blit(IMAGES['base'], (basex, globfile.BASEY))
        # print score so player overlaps the score
        showScore(population.players[0].score)

        pygame.display.update()
        FPSCLOCK.tick(globfile.FPS)


def showGameOverScreen(player):
    """crashes the player down and shows gameover image"""
    playerx = globfile.SCREENWIDTH * 0.2

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if player.y + player.height >= globfile.BASEY - 1:
                    return
        player.drop_dead()
        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))

        player.pipes.draw(SCREEN)
        player.draw(SCREEN)

        SCREEN.blit(IMAGES['base'], (playerx-60, globfile.BASEY))
        showScore(player.score)

        SCREEN.blit(IMAGES['gameover'], (50, 180))

        FPSCLOCK.tick(globfile.FPS)
        pygame.display.update()


def playerShm(playerShm):
    """oscillates the value of playerShm['val'] between 8 and -8"""
    if abs(playerShm['val']) == 8:
        playerShm['dir'] *= -1

    if playerShm['dir'] == 1:
        playerShm['val'] += 1
    else:
        playerShm['val'] -= 1


def showScore(score):
    """displays score in center of screen"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0 # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = (globfile.SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, globfile.SCREENHEIGHT * 0.1))
        Xoffset += IMAGES['numbers'][digit].get_width()


if __name__ == '__main__':
    main()