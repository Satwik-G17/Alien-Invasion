import pygame # type: ignore
from pygame.sprite import Sprite # type: ignore
from settings import Settings

class Bullet(Sprite):
    """A class to manage bullet fired from ship"""
    def __init__(self, ai_game):
        """Create a bullet object a current ship's position"""
        super().__init__()
        self.screen = ai_game.screen
        self.setting = ai_game.settings
        self.color = ai_game.settings.bullet_color

        #create a bullet rect at(0,0) and set correct positon
        self.rect = pygame.Rect(0, 0, self.setting.bullet_width, self.setting.bullet_height)
        self.rect.midbottom = ai_game.ship.rect.midtop

        self.y = float(self.rect.y)

    def update(self):
        """Move the bullet up the screen"""
        #update the decimal position of the bullet.
        self.y -= self.setting.bullet_speed
        #update the rect position
        self.rect.y = self.y

    def draw_bullet(self):
        """draw the bullet to the screen"""
        pygame.draw.rect(self.screen, self.color, self.rect)
