import pygame
import os

class VisualManager(object):
    """A manager for all game visuals."""
    def __init__(self, key):
        """Initialize all the necessary values.

        Link the tower.
        Set fullscreen, width, and weight.
        Set the game caption, and the mouse invisible.
        Set the visuals level.
        Load the shield frames.
        Load the ship images.
        Set the game colours.
        Set the game font.

        """
        
        self.Tower = key.Tower
        self.fullscreen = key.fullscreen
        self.width = key.width
        self.height = key.height
        if key.fullscreen:
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Asteroid Holes 3')
        pygame.mouse.set_visible(False)
        self.level = key.visual_level
        self.Load_shield(key)
        self.Load_images(key)
        self.colours = key.colours
        self.font = pygame.font.Font(None, 37)
        
    def Load_shield(self, key):
        """Load the shield animation frames."""
        self.shieldFrames = []
        full = pygame.image.load(os.path.abspath(os.path.join('Ash', 'Resources', 'shield.png')))
        size = full.get_width()
        for i in xrange(full.get_height() / size):
            temp = pygame.Surface((size, size))
            temp.blit(full, (0, -i * size))
            temp = pygame.transform.scale(temp, (key.shipSize, key.shipSize))
            temp.set_alpha(225)
            self.shieldFrames.append(temp)
        self.shieldIndex = 0
        self.shieldMaxIndex = len(self.shieldFrames)

    def Load_images(self, key):
        """Load the ship images."""
        self.Images = [pygame.transform.scale(pygame.image.load(os.path.join('Ash', 'Resources', 'ship%d.bmp' % (i + 1))).convert(), (key.shipSize, key.shipSize)) for i in xrange(2)]
        for image in self.Images:
            image.set_colorkey((0, 0, 0))

    def Set_level(level):
        """Set the visual level."""
        self.level = level

    def draw_text(self, text, pos, anchor):
        """Draw the string text to the screen on a rect with the rect's corner (anchor) on pos Return that rect."""
        text = self.font.render(str(text), 1, (255, 255, 255))
        rect = text.get_rect()
        setattr(rect, anchor, pos)
        self.screen.blit(text, rect)
        return rect

    def UpdateShield(self):
        self.shieldIndex += 1
        if self.shieldIndex == self.shieldMaxIndex:
            self.shieldIndex = 0

    def DrawParticles(self):
        """Draw all the particles."""
        for particle in self.Tower.Particles:
            pygame.draw.circle(self.screen,
                               particle.colour,
                               (int(particle.vector.x),
                                int(particle.vector.y)),
                               int(particle.life / 100))

    def DrawLasers(self):
        """Draw all the lasers."""
        for laser in self.Tower.Lasers:
            pygame.draw.line(self.screen,
                             self.colours[laser.player][self.Tower.Values.SECONDARY],
                             laser.vector.Get(),
                             (laser.vector.x + laser.velocity.x,
                              laser.vector.y))

    def DrawLaser(self, laser, reverse=0):
        """Draw a specific laser."""
        x2 = laser.vector.x
        if reverse:
            x2 -= laser.velocity.x
        else:
            x2 += laser.velocity.x
        pygame.draw.line(self.screen,
                         self.colours[laser.player][self.Tower.Values.SECONDARY],
                         laser.vector.Get(),
                         (x2, laser.vector.y))
        if reverse:
            return -laser.velocity.x
        else:
            return laser.velocity.x

    def DrawMissiles(self):
        """Draw all the missiles."""
        for missile in self.Tower.Missiles:
            pygame.draw.rect(self.screen,
                             self.colours[missile.player][self.Tower.Values.TERTIARY],
                             missile.rect)

    def DrawMissile(self, missile, reverse=0):
        """Draw a specific missiles."""
        pygame.draw.rect(self.screen,
                         self.colours[missile.player][self.Tower.Values.TERTIARY],
                         missile.rect)
        if reverse:
            return -missile.rect.width
        else:
            return missile.rect.width

    def DrawShield(self, topleft):
        """Draw a shield in the specified spot."""
        self.screen.blit(self.shieldFrames[self.shieldIndex], topleft)
        return self.shieldFrames[self.shieldIndex].get_rect().width

    def DrawShips(self):
        """Draw the ships.

        If the visual level is fancy, draw the ship image, if the shield is on too, draw that.
        Otherwise, if the ship is shielded draw the shield colour, otherwise draw the ship colour.

        """
        
        for ship in self.Tower.Ships:
            if self.level == self.Tower.Values.FANCY:
                self.screen.blit(self.Images[ship.player], ship.rect)
                if ship.shdValue:
                    self.screen.blit(self.shieldFrames[self.shieldIndex], ship.rect)
            elif self.level == self.Tower.Values.FAST:
                if ship.shdValue:
                    pygame.draw.rect(self.screen,
                                     (200, 200, 200),
                                     ship.rect)
                else:
                    pygame.draw.rect(self.screen,
                                     self.colours[ship.player][self.Tower.Values.PRIMARY],
                                     ship.rect)

    def DrawDebug(self):
        """Draw the controlling modules debug if applicable."""
        if self.Tower.DEBUG:
            for ship in self.Tower.Ships:
                if hasattr(self.Tower.Minds[ship.mind], 'draw_debug'):
                    self.Tower.Minds[ship.mind].draw_debug(self.Tower, ship, self.screen)

    def DrawBorders(self):
        """Draw the borders."""
        pygame.draw.line(self.screen,
                         (255, 0, 0),
                         (self.width / 2, 0),
                         (self.width / 2,
                          self.height),
                          2)

    def DrawDeath(self, Checks):
        """If either ship is dead, cross it's name out."""
        for player in [0, 1]:
            if self.Tower.Ships[player].health <= 0:
                pygame.draw.line(self.screen,
                                 (255, 0, 0),
                                 (Checks[player].left, Checks[player].centery),
                                 (Checks[player].right, Checks[player].centery),
                                  3)

    def DrawDelay(self, Checks):
        """Draw lasers, shields, and missiles when they are available to be used."""
        Points = [[Checks[0].right, Checks[0].centery],[Checks[1].left, Checks[1].centery]]
        Offset = 5
        for player in [0, 1]:
            point = Points[player]
            
            if player: point[0] -= Offset
            else: point[0] += Offset * 2
            
            if self.Tower.Ships[player].shdDelay == 0:
                if player:
                    point[0] -= self.DrawShield((Checks[player].left - Offset - self.shieldFrames[self.shieldIndex].get_rect().width, Checks[player].top))
                else:
                    point[0] += self.DrawShield((Checks[player].right + Offset, Checks[player].top))
                    
            if player: point[0] -= Offset * 2
            else: point[0] += Offset
            
            if self.Tower.Ships[player].misDelay == 0:
                point[0] += self.DrawMissile(self.Tower.Missiles.New(point, player), player)
                
            if player: point[0] -= Offset * 2
            else: point[0] += Offset
            
            if self.Tower.Ships[player].lasDelay == 0:
                self.DrawLaser(self.Tower.Lasers.New(point, player), player)

    def DrawInfo(self):
        """Draw the controlling modules' names."""

        #I've decided I don't like this right now so...
        return
    
        Checks = [self.draw_text(self.Tower.Ships[0].mind,
                                (5, self.height - 5),
                                'bottomleft'),
                  self.draw_text(self.Tower.Ships[1].mind,
                                (self.width - 5, self.height - 5),
                                'bottomright')]
        self.DrawDeath(Checks)
        self.DrawDelay(Checks)
    
    def Draw(self):
        """Draw the game.

        Set the caption to show the frames per second.
        If the visual level is set to off, return.
        Update the shield animation if necessary.
        Clear the screen.
        Draw the particles if necessary.
        Draw the lasers and missiles.
        Draw the ships.
        Draw the ships' healths.
        Draw the names of the ship controllers if necessary.
        Flip the display!

        """
        
        pygame.display.set_caption('AsteroidHoles 3: %.3f' % (self.Tower.clock.get_fps()))
        if self.level == self.Tower.Values.OFF:
            return
        if self.level == self.Tower.Values.FANCY: self.UpdateShield()
        
        self.screen.fill((0, 0, 0))
        if self.level == self.Tower.Values.FANCY: self.DrawParticles()
        self.DrawLasers()
        self.DrawMissiles()
        self.DrawShips()
        if self.Tower.DEBUG: self.DrawDebug()
        self.DrawBorders()
        
        self.draw_text(self.Tower.Ships[0].health, (5, 5), 'topleft')
        self.draw_text(self.Tower.Ships[1].health, (self.width - 5, 5), 'topright')
        if self.level == self.Tower.Values.FANCY: self.DrawInfo()
        pygame.display.flip()
