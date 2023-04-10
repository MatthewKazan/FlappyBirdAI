import random
import pygame

import globfile
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
        mainGame(population)
        population.birth_new_generation()
        foundALive = False
        for p in population.players:
            if p.isAlive:
                foundALive = True
        if not foundALive:
            raise Exception("No one is alive")

def mainGame(population):
    basex = -28
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    while True:
        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))
        population.draw(SCREEN)
        SCREEN.blit(IMAGES['base'], (basex, globfile.BASEY))
        # print score so player overlaps the score
        showScore(population.global_best_score)
        pygame.display.update()
        FPSCLOCK.tick(globfile.FPS)
        # print(len(population.players))
        foundALive = False
        for p in population.players:
            if p.isAlive:
                foundALive = True
        if not foundALive:
            population.global_best_score = 0
            return

        basex = -((-basex + 100) % baseShift)


        population.update()

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