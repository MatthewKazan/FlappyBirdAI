import pygame
import globfile

class Player:
  """Player class"""
  def __init__(self, x, y, sprites, hitmasks):
    self.score = 0
    self.x = x
    self.y = y
    self.playerVelY    =  -9   # player's velocity along Y, default same as playerFlapped
    self.playerMaxVelY =  10   # max vel along Y, max descend speed
    self.playerMinVelY =  -8   # min vel along Y, max ascend speed
    self.playerAccY    =  1    # players downward acceleration
    self.playerRot     =  45   # player's rotation
    self.playerVelRot  =  3    # angular speed
    self.playerRotThr  =  20   # rotation threshold
    self.playerFlapAcc =  -9   # players speed on flapping
    self.playerFlapped = False # True when player flaps
    # self.moveInfo = moveInfo
    self.sprites = sprites
    self.hitmasks = hitmasks
    self.width = self.sprites[0].get_width()
    self.height = self.sprites[0].get_height()
    self.rect = pygame.Rect(self.x, self.y, self.sprites[0].get_width(), self.sprites[0].get_height())
    
  def flap(self):
    """Flap the player"""
    self.playerVelY = self.playerFlapAcc
    self.playerFlapped = True
    
  def checkCrash(self, pipes):
    self.rect = pygame.Rect(self.x, self.y, self.sprites[0].get_width(), self.sprites[0].get_height())
  
    if self.y + self.height >= globfile.BASEY - 1:
        return [True, True]
    else:
      return pipes.collide(self)
    
  def update(self):
    # rotate the player
    if self.playerRot > -90:
      self.playerRot -= self.playerVelRot

    # player's movement
    if self.playerVelY < self.playerMaxVelY and not self.playerFlapped:
      self.playerVelY += self.playerAccY
    if self.playerFlapped:
      playerFlapped = False

      # more rotation to cover the threshold (calculated in visible rotation)
      playerRot = 45

    playerHeight = self.sprites[0].get_height()
    self.y += min(self.playerVelY, globfile.BASEY - self.y - playerHeight)
    
  def draw(self, screen):
    # Player rotation has a threshold
    visibleRot = self.playerRotThr
    if self.playerRot <= self.playerRotThr:
      visibleRot = self.playerRot

    playerSurface = pygame.transform.rotate(self.sprites[0], visibleRot)
    screen.blit(playerSurface, (self.x, self.y))
