import pygame
pygame.init()
import os
import sys
from Values import Values
from Vectors import poolVectors
from Particles import poolParticles

from Visual import VisualManager
from Input import InputManager
from Ships import ShipManager
from GameRunner import GameManager
from Lasers import laserManager
from Missiles import missileManager

class Tower(object):
    """An object for tieing together all the different classes for the game, the main interface."""
    def __init__(self, key):
        """Initialize all the necessary modules."""
        key.Tower = self

        #A few settings.
        self.DEBUG = key.DEBUG
        self.TOGGLING = key.toggling
        self.FPS = key.FPS

        #Important game variables.
        self.clock = pygame.time.Clock()
        self.time = 0
        self.Ships = []
        self.Boundaries = [pygame.Rect((0, 0), (key.width / 2, key.height)),
                           pygame.Rect((key.width / 2, 0), (key.width / 2, key.height))]

        #Set up the values and two pools.
        self.Values = Values
        self.poolVectors = poolVectors
        self.poolParticles = poolParticles

        #Initialize all the game classes.
        self.Visual = VisualManager(key)
        self.Manager = ShipManager(key)
        self.Game = GameManager(key)
        self.Input = InputManager(key)
        self.Lasers = laserManager(key)
        self.Missiles = missileManager(key)

        #Set up the particle pool.
        self.Particles = []

        #Load the ship controllers.
        self.Minds = {}
        self.LoadMinds()
    
    def LoadMinds(self):
        """Loads all ship controllers in the AI directory.

        Append the AI folder to the system path.
        For every file in the directory, if it is a python file,
            if the file has not already been loaded under a different name
            for example, me.py and me.pyc being loaded twice,
                attempt to import the module.
        If there are no controllers after this problem, quit.

        """
        
        already = set()
        sys.path.append(os.path.abspath(os.path.join('Ash', 'AI')))
        for fille in os.listdir(os.path.abspath(os.path.join('Ash', 'AI'))):
            if '.py' in fille:
                fileName = fille[:fille.index('.')]
                if not fileName in already:
                    try:
                        module = __import__(fileName)
                        if hasattr(module, 'Name'): fileName = module.Name
                        self.Minds[fileName] = module
                        already.add(fileName)
                        if hasattr(self.Minds[fileName], 'Init'):
                            self.Minds[fileName].Init(self)
                    except Exception as inst:
                        print 'Loading of mind %s has failed because: %s' % (fille, repr(inst))
        if not self.Minds:
            self.Quit()
            raise Exception('No ship minds available')

    def Update(self):
        """Update the game.

        Update the time on the clock.
        Update the input.
        End the game if necessary.
        Update the lasers and missiles.
        For both ships:
            Prepare the ship to be updated.
            Update the ship using it's controller.
            Update the ship's position.
        If necessary, update the particles.
        Draw the screen.
        If any ship has lost, end the game.
        Return 0 (nothing of interest happened).

        """
        self.time += self.clock.tick(self.FPS)
        result = self.Input.Update()
        if result: return result
        self.Lasers.Update()
        self.Missiles.Update()
        for ship in self.Ships:
            self.Manager.Prep(ship)
            self.Minds[ship.mind].Update(self, ship)
            self.Manager.Update(ship)
        if self.Visual.level == self.Values.FANCY:
            self.Particles[:] = [particle for particle in self.Particles if particle.Update()]
        self.Visual.Draw()
        if any([ship.health == 0 for ship in self.Ships]): return self.Values.ROUND_FINISH
        return 0

    def Clear(self):
        """Reset the game for the next round."""
        self.clock.tick()
        self.time = 0
        self.Lasers.Lasers = []
        self.Missiles.Missiles = []
        self.Particles = []

    def Quit(self):
        """Quit pygame."""
        pygame.quit()
        
class Key(object):
    """An object for setting up the game."""
    def __init__(self):
        """Set the default values.

        FPS: Frames per second, 0 is unlimited
        width: Screen width
        height: screen height
        fullscreen: Fullscreen or not
        visual_level: How fancy the graphics should be

        toggling: Whether or not the human AI has toggling weapon controls
        pacify: Whether or not to pacify the specified players
        no_camping: Whether or not to penalize camping for the specified players
        killer_opponents: Opponents the defeat of will get a neural network saved in Killers.txt

        shipSize: The size of the ships.
        colours: In RGB, Ship, laser, missile colour for each player.

        """
        
        self.FPS = 30
        self.width = 500
        self.height = 500
        self.fullscreen = False
        self.visual_level = Values.FANCY
        
        self.toggling = True
        self.pacify = [False, False]
        self.no_camping = [False, False]
        self.killer_opponents = ['Tree']
        
        self.shipSize = 20
        self.colours = [[(0, 0, 255), (75, 75, 255), (150, 150, 255)],
                        [(0, 255, 0), (75, 255, 75), (150, 255, 150)]]
