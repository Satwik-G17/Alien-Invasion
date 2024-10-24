import sys
from time import sleep

import pygame # type: ignore
 
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard

class AlienInvasion:
    """Overall class to manage game assets and behaviour"""

    def __init__(self):
        """Initialize the game, and create game resources"""
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height

        self.screen = pygame.display.set_mode((self.settings.screen_width,self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")
        self.stats = GameStats(self)
        self.ship = Ship(self)
        self.bullet = pygame.sprite.Group()
        self.alien = pygame.sprite.Group()
        self._create_fleet()
        self.play_button = Button(self, "Play")
        self.sb = Scoreboard(self)

    def run_game(self):
        """Start the main loop for the game"""
        while True:
            # Watch for keyboard and mouse events.
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self._update_aliens()
                self._update_bullets()
            
            self._update_screen()
            self._check_alien_bottom()
            
    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:   
                self._check_keydownevents(event)
            elif event.type == pygame.KEYUP:
                self._check_keyupevents(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)


    def _check_play_button(self, mouse_pos=None):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos) if mouse_pos else False
        if button_clicked and not self.stats.game_active:
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships() 

            self.alien.empty()
            self.bullet.empty()

            self._create_fleet()
            self.ship.center_ship()

            self.settings.initialize_dynamic_settings()

            pygame.mouse.set_visible(False)
                
    def _check_keydownevents(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        if event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        if event.key == pygame.K_q:
            sys.exit()
        if event.key == pygame.K_p:
            mouse_pos = pygame.mouse.get_pos()
            self._check_play_button(mouse_pos)
        if event.key == pygame.K_SPACE:
            self._fire_bullet()
        if event.key == pygame.K_ESCAPE:
            sys.exit()

    def _check_keyupevents(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        if event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _update_bullets(self):
        self.bullet.update()
    
        #get rid of bullet that have disappeared
        for bullet in self.bullet.copy():
            if bullet.rect.bottom <= 0:
                self.bullet.remove(bullet)
            print(len(self.bullet))

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        #check for any bullet that have hit the aliens
        #if so, get rid of the alien and the bullet
        collisions = pygame.sprite.groupcollide(self.bullet, self.alien, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
                self.sb.prep_score()
                self.sb.check_high_score()

        if not self.alien :
            #destroy existing bullets and create a new fleet.
            self.bullet.empty()  
            self._create_fleet()
            self._update_screen()
            sleep(2)
            self.settings.increase_speed()

            self.stats.level +=1
            self.sb.prep_level()

    def _fire_bullet(self):
        """create a new bullet and add it to the bullets group"""
        if len(self.bullet) < self.settings.bullets_allowed:   
            new_bullet = Bullet(self)
            self.bullet.add(new_bullet)

    def _create_fleet(self):
        """Create the feet of aliens."""
        # Create an alien and find the number of aliens in a row.
        # Spacing between each alien is equal to one alien width.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_of_alien_x = available_space_x // (2 * alien_width)

        ship_height = self.ship.rect.height
        available_space_y = self.settings.screen_height - (3 * alien_height) - ship_height
        number_rows = available_space_y // (2 * alien_height)

        # Create the first row of aliens.
        for row_number in range(number_rows):
            for alien_number in range(number_of_alien_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
            alien = Alien(self)
            alien_width, alien_height = alien.rect.size
            alien.x = alien_width + (2 * alien_width * alien_number)
            alien.rect.x = alien.x
            alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
            self.alien.add(alien)

    def _update_aliens(self):
        """check if fleet is at the edge of screen then
                Update the position of aliens in the fleet"""
        self._check_fleet_edges()
        self.alien.update()

        #look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.alien):
            print("SHIP HIT!!!")
            self._ship_hit()

    def _check_fleet_edges(self):
        """Resopnd approprialtly when aliene has reached an edge"""
        for alien in self.alien.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the direction"""
        for alien in self.alien.sprites():  
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _check_alien_bottom(self):
        """check if any aliens have reached the bottom of the screen"""
        screen_rect = self.screen.get_rect()
        for alien in self.alien.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break           

    def _ship_hit(self):
        """respond to the ship being hit by alien"""
        if self.stats.ships_left > 0:
            # Discrement ship life
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            #get rid of aliens and ships
            self.alien.empty()
            self.bullet.empty()

            #create a new fleet and centre the ship
            self._create_fleet()
            self.ship.center_ship()

            #pause the game
            pygame.mouse.set_visible(True)
            sleep(0.5)
        else:
            print("GAME OVER!!!")
            sleep(0.5)
            self.stats.game_active = False

    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullet.sprites():
            bullet.draw_bullet()
        self.alien.draw(self.screen) 

        self.sb.show_score()    

        if not self.stats.game_active:
            self.play_button.draw_button()   

        pygame.display.flip()


if __name__ == '__main__':
    # Make a game instance and run the game. 
    ai = AlienInvasion()
    ai.run_game()