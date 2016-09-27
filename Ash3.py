"""Ash 3
Sam Wanuch
29/09/2012

Game Modes:
    For all game modes except Standard and Learning, at least one player must be 'Neural'
    
    Standard: A standard game, prints the results in the format [winner id, [player one score, player two score]].
              Does not end until escape is pressed.
    Genetic: Use a genetic algorithm to find good neural network weightings. Runs for 1000 generations
             but can safely be stopped early.
    Reviewgenetic: Review the latest Pool produced by the Genetic mode.
    Continuegenetic: Continue the genetic algorithm from the last saved Pool.
    Facekillers: Face all unique neural network weightings that beat the Tree AI.
    Breedkillers: Start a genetic algorithm using the weightings that beat the Tree AI.
    Learning: Attempt to teach a neural network through 25 rounds of backpropogation. Does not work very well.
    Reviewing: Review the weightings produced by Learning mode.

AI types:
    Human: A human controlled ship. Controls are:
        Player One:
            Up: W
            Down: S
            Left: A
            Right: D
            Fire Laser: Q
            Fire Missile: E
            Activate Shield: F
        Player Two:
            Up: I
            Down: K
            Left: J
            Right: L
            Fire Laser: O
            Fire Missile: U
            Activate Shield: H
        Currently toggling is enabled, so pressing the fire button for missiles or lasers
        will make the ship automatically fire them as soon as possible.
    Squirrel: A base AI that does not fire lasers or missiles. Has fairly good dodging methods.
    Tree: Based on Squirrel, the exact same, but fires weapons.
    Dodger: Based on Squirrel, this one runs from the opponent (i.e. more defensive)
    Neural: An AI that uses a neural network to react. If no set of weightings is specified,
            one will be randomly generated.

Visual Levels:
    Sets how fancy the graphics are, they are as follows:
        1: Fancy, with particles and names and everything.
        2: Basic, just shapes to let you know what's happening.
        3: Off, only the FPS is displayed in the title, for extreme speed.

FPS: Frames per second. When set to 0, it is unlimited.

width\height\fullscreen: Self explanatory screen configuration.

DEBUG: AI's should have a draw_debug method which will be called when this is active.
       For Squirrel based or Neural AI, it will draw the zones and sensors that
       the AI is paying attention to.

q(): In the event of the game crashing, the error will surf back up to this level.
     Then the user can type q() in the shell, which will close the pygame window.
     Otherwise it freezes and is generally annoying.

Main(): Go through all the game mode modules until the requested game mode is found.
        If the game mode isn't found, raise an error saying so.
    
"""

import Ash
import os
import sys

key = Ash.Key()

#####################
#                   #
#   Main Settings   #
#                   #
################################
MODE = 'Facekillers'
PLAYER_ONE = 'Neural'
PLAYER_TWO = 'Tree'

key.FPS = 30
key.visual_level = 1
###############################

#Screen config.
key.width = 500
key.height = 500
key.fullscreen = False

#Debugging.
key.DEBUG = False


Tower = Ash.Tower(key)

def q():
    import pygame
    pygame.quit()
    
def Main():
    sys.path.append(os.path.abspath(os.path.join('Ash', 'Modes')))
    module = None
    for fille in os.listdir(os.path.abspath(os.path.join('Ash', 'Modes'))):
        if '.py' in fille:
            if fille[:fille.index('.')] == MODE:
                module = __import__(fille[:fille.index('.')])
                module.main(Tower, PLAYER_ONE, PLAYER_TWO)
                break
    if not module: raise Exception('Game mode not found.')
            
if __name__ == '__main__':
    Main()
    Tower.Quit()
