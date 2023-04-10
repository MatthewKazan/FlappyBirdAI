import random
import pygame
import globfile


class Pipes:
    def __init__(self, seed, velocity=-128 * globfile.DT):
        self.seed = random.Random(seed)
        self.velocity = velocity
        self.sprites = (
            pygame.transform.flip(
                pygame.image.load(
                    globfile.PIPES_LIST[0]).convert_alpha(), False,
                True),
            pygame.image.load(globfile.PIPES_LIST[0]).convert_alpha(),
        )
        self.width = self.sprites[0].get_width()
        self.height = self.sprites[0].get_height()
        pipe1 = self.getRandomPipe()
        pipe2 = self.getRandomPipe()
        self.upperPipes = [
            {'x': globfile.SCREENWIDTH + 200, 'y': pipe1[0]['y']},
            {'x': globfile.SCREENWIDTH + 200 + (globfile.SCREENWIDTH / 2),
             'y': pipe2[0]['y']},
        ]
        # list of lowerpipe
        self.lowerPipes = [
            {'x': globfile.SCREENWIDTH + 200, 'y': pipe1[1]['y']},
            {'x': globfile.SCREENWIDTH + 200 + (globfile.SCREENWIDTH / 2),
             'y': pipe2[1]['y']},
        ]

    def collide(self, player):
        for uPipe, lPipe in zip(self.upperPipes, self.lowerPipes):
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], self.width,
                                    self.height)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], self.width,
                                    self.height)

            if uPipeRect.colliderect(player.rect) or lPipeRect.colliderect(
                player.rect):
                return [True, True]

        return [False, False]

    def passed(self, player):
        for pipe in self.upperPipes:
            if pipe['x'] <= player.x < pipe['x'] + 5:
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
        if len(self.upperPipes) > 0 and self.upperPipes[0]['x'] < -self.sprites[
            0].get_width():
            self.upperPipes.pop(0)
            self.lowerPipes.pop(0)

    def getRandomPipe(self):
        """returns a randomly generated pipe"""
        # y of gap between upper and lower pipe
        gapY = self.seed.randrange(0,
                                   int(globfile.BASEY * 0.6 - globfile.PIPEGAPSIZE))
        gapY += int(globfile.BASEY * 0.2)
        pipeHeight = self.sprites[0].get_height()
        pipeX = globfile.SCREENWIDTH + 10

        return [
            {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
            {'x': pipeX, 'y': gapY + globfile.PIPEGAPSIZE},  # lower pipe
        ]

    def draw(self, screen):
        for uPipe, lPipe in zip(self.upperPipes, self.lowerPipes):
            screen.blit(self.sprites[0], (uPipe['x'], uPipe['y']))
            screen.blit(self.sprites[1], (lPipe['x'], lPipe['y']))

