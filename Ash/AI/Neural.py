"""An AI based on a neural network.

    The neural network has 24 inputs:
        0 - 8: are the number of lasers in the relevant detection zone.
        9 - 17: are the number of missiles in the relevant detection zone.
        18: Up Feeler
        19: Down Feeler
        20: Front Feeler
        21: Back Feeler
        22: Enemy Y position relative to ship y position (value is distance / ship size) Positive above, negative below
        23: Constant(1)

    There are 15 nodes in the hidden layer.

    There are 7 outputs:
        0: fire laser
        1: fire missile
        2: fire shield
        3: move up
        4: move down
        5: move forward
        6: move backward

    This means there are 583 total values necessary to run this network.

"""

import os
import sys
sys.path.append(os.path.abspath(os.path.join('Ash')))
from Values import random
import pygame

TOTAL_INPUTS = 24
TOTAL_HIDDEN_NODES = 15
TOTAL_OUTPUT_NODES = 7
TOTAL_WEIGHTS = (TOTAL_INPUTS * TOTAL_HIDDEN_NODES) + (TOTAL_HIDDEN_NODES * TOTAL_OUTPUT_NODES)
TOTAL_THRESHOLDS = TOTAL_HIDDEN_NODES + TOTAL_OUTPUT_NODES
TOTAL_VALUES = TOTAL_WEIGHTS + TOTAL_THRESHOLDS
PROPOGATION_VALUE = 0.137

ZONE_DANGER = 0
ZONE_BACK_UPPER = 1
ZONE_BACK_LOWER = 2
ZONE_MID_UPPER = 3
ZONE_MID_LOWER = 4
ZONE_DIRECT_UPPER = 5
ZONE_DIRECT_LOWER = 6
ZONE_FRONT_UPPER = 7
ZONE_FRONT_LOWER = 8

FEELER_LENGTH = 3
MAX_VERTICAL_DISTANCE = 10

Zones = []

def Init(Tower):
    """Set up the Zones."""
    global Zones
    global FEELER_LENGTH
    global MAX_VERTICAL_DISTANCE
    size = Tower.Values.SHIP_SIZE
    FEELER_LENGTH = (FEELER_LENGTH + 0.5) * size
    MAX_VERTICAL_DISTANCE = MAX_VERTICAL_DISTANCE * size
    detection_range = size + 2 * (Tower.Values.MISSILE_SIZE + Tower.Values.MISSILE_SPEED)
    Zones = [pygame.Rect((0, 0), (detection_range, detection_range)),   #Danger zone                0
             pygame.Rect((0, 0), (size * 3, size * 2)),                 #Upper back zone            1
             pygame.Rect((0, 0), (size * 3, size * 2)),                 #Lower back zone            2
             pygame.Rect((0, 0), (size, size * 3)),                     #Upper mid zone             3
             pygame.Rect((0, 0), (size, size * 3)),                     #Lower mid zone             4
             pygame.Rect((0, 0), (size * 5, size / 2)),                 #Upper direct front zone    5
             pygame.Rect((0, 0), (size * 5, size / 2)),                 #Lower direct front zone    6
             pygame.Rect((0, 0), (size * 3, size * 2)),                 #Upper front zone           7
             pygame.Rect((0, 0), (size * 3, size * 2))]                 #Lower front zone           8

class Brain(object):
    """An object that holds both all necessary values, plus a fitness level, and chance value used for genetic algorithms."""
    def __init__(self, genome=None):
        """Initialize the values, and setup the genome."""
        self.fitness = 0.0
        self.chance = 0.0
        if not genome: self.genome = [random.uniform(-1, 1) for i in xrange(TOTAL_VALUES)]
        else: self.genome = genome
    def __str__(self):
        return 'Brain: Fitness: %.3f' % (self.fitness)

def getWeights(brain):
    """A generator that will return all the weightings for the neural network."""
    for weight in brain.genome[:TOTAL_WEIGHTS + 1]:
        yield weight

def getThresholds(brain):
    """A generator that will return all the thresholds for the neural network."""
    for thresh in brain.genome[TOTAL_WEIGHTS:]:
        yield thresh

def backPropogate(ship, action):
    """In theory, performs back propogation on a neural network."""
    action = {'fireLaser':0, 'fireMissile':1,
              'fireShield':2, 'moveUp':3,
              'moveDown':4, 'moveFore':5,
              'moveBack':6}[action]
    error = ship.brain.genome[TOTAL_WEIGHTS + TOTAL_HIDDEN_NODES + action] - ship.output[action]
    for weight in ship.brain.genome[TOTAL_INPUTS * TOTAL_HIDDEN_NODES + action * TOTAL_OUTPUT_NODES:TOTAL_INPUTS * TOTAL_HIDDEN_NODES + (action + 1) * TOTAL_OUTPUT_NODES]:
        weight += error

def getZones(ship):
    """Return the detection zones, properly aligned to the given ship."""
    marker = ship.rect
    Zones[ZONE_DANGER].center = marker.center
    Zones[ZONE_MID_UPPER].bottomleft = marker.topleft
    Zones[ZONE_MID_LOWER].topleft = marker.bottomleft
    if ship.player:
        Zones[ZONE_BACK_UPPER].bottomleft = (marker.right, marker.centery)
        Zones[ZONE_DIRECT_UPPER].bottomright = (marker.left, marker.centery)
        Zones[ZONE_FRONT_UPPER].bottomright = marker.topleft
        Zones[ZONE_FRONT_LOWER].topright = marker.bottomleft
    else:
        Zones[ZONE_BACK_UPPER].bottomright = (marker.left, marker.centery)
        Zones[ZONE_DIRECT_UPPER].bottomleft = (marker.right, marker.centery)
        Zones[ZONE_FRONT_UPPER].bottomleft = marker.topright
        Zones[ZONE_FRONT_LOWER].topleft = marker.bottomright
    Zones[ZONE_BACK_LOWER].topleft = Zones[ZONE_BACK_UPPER].bottomleft
    Zones[ZONE_DIRECT_LOWER].topright = Zones[ZONE_DIRECT_UPPER].bottomright
    return Zones

def Logistic(num):
    """A logistic function to limit the results from 0 to 1."""
    try:
        return 1.0 / (1 + (2.71828 ** -num))
    except:
        return 1.79769311957e+308

def getRange(ship):
    """Return the range of the ship's vicinity."""
    ship_range = ship.rect
    for rect in getZones(ship):
        ship_range = ship_range.union(rect)
    return ship_range

def getProjectiles(Tower, ship):
    """Return lists of all projectiles in the ship's vicinity."""
    vicinity = getRange(ship)
    lasers = []
    missiles = []
    for laser in Tower.Lasers:
        if laser .player != ship.player:
            if vicinity.collidepoint(laser.vector.Get()):
                lasers.append(laser)
    for missile in Tower.Missiles:
        if missile.player != ship.player:
            if vicinity.collidepoint(missile.vector.Get()):
                missiles.append(missile)
    return lasers, missiles

def getFeelers(Tower, ship):
    """Return of the FEELER_LENGTH covered by each wall."""
    boundary = Tower.Boundaries[ship.player]
    upper = FEELER_LENGTH - ship.vector.y
    lower = ship.vector.y - (boundary.bottom - FEELER_LENGTH)
    if ship.player == Tower.Values.PLAYER_ONE:
        back = FEELER_LENGTH - ship.vector.x
        front = ship.vector.x + FEELER_LENGTH - boundary.right
    else:
        back = ship.vector.x + FEELER_LENGTH - boundary.right
        front = FEELER_LENGTH - ship.vector.x
    return [x if x > 0 else 0 for x in [upper, lower, front, back]]

def doInputs(Tower, ship):
    """Return the input values.

    Gather all projectiles in the vicinity.
    Check to see if they fit in any zones and increment the inputs accordingly.
    Set the ship status inputs.
    Set the enemy status inputs.

    """
    Inputs = [0 for i in xrange(TOTAL_INPUTS)]
    lasCheck, misCheck = getProjectiles(Tower, ship)
    
    for i, zone in enumerate(getZones(ship)):
        collides = zone.colliderect
        for laser in lasCheck:
            if collides(laser.rect):
                Inputs[i] += 1
        for missile in misCheck:
            if collides(missile.rect):
                Inputs[i + 9] += 1

    Inputs[18:22] =  getFeelers(Tower, ship)
    vertical_distance = (ship.vector.y - Tower.Ships[Tower.Values.otherPlayer(ship.player)].vector.y)
    if vertical_distance < 0:
        if vertical_distance < -MAX_VERTICAL_DISTANCE:
            vertical_distance = -MAX_VERTICAL_DISTANCE
    elif vertical_distance > 0:
        if vertical_distance > MAX_VERTICAL_DISTANCE:
            vertical_distance = MAX_VERTICAL_DISTANCE
    Inputs[22] = vertical_distance / Tower.Values.SHIP_SIZE
    Inputs[23] = 1
    return Inputs

def doHidden(Inputs, nextWeight, nextThresh):
    """Return the values for the hidden layer, using the Logistic function."""
    Hidden = [0 for i in xrange(TOTAL_HIDDEN_NODES)]
    for i in xrange(TOTAL_HIDDEN_NODES):
        check = Logistic(sum([num * nextWeight() for num in Inputs]))
        if check >= nextThresh():
            Hidden[i] = check
    return Hidden

def doOutputs(Hidden, Outputs, nextWeight, nextThresh, ship):
    """Find the output values and perform actions as appropriate."""
    for i in xrange(TOTAL_OUTPUT_NODES):
        check = Logistic(sum([num * nextWeight() for num in Hidden]))
        ship.output.append(check)
        if check >= nextThresh():
            Outputs[i](ship)
    
def Update(Tower, ship):
    """Update a neural network based ship.

    Get the input levels, then the weight and theshold generators.
    Get the hidden values,
    Prepare the output functions, then get and perform applicable outputs.

    """
    if not ship.brain:
        ship.brain = Brain()
    Inputs = doInputs(Tower, ship)
    nextWeight = getWeights(ship.brain).next
    nextThresh = getThresholds(ship.brain).next
    Hidden = doHidden(Inputs, nextWeight, nextThresh)
    Outputs = [Tower.Manager.fireLaser,
               Tower.Manager.fireMissile,
               Tower.Manager.fireShield,
               Tower.Manager.moveUp,
               Tower.Manager.moveDown,
               Tower.Manager.moveFore,
               Tower.Manager.moveBack]
    doOutputs(Hidden, Outputs, nextWeight, nextThresh, ship)

def draw_debug(Tower, ship, screen):
    """Draw the detection zones."""
    for zone in getZones(ship):
        pygame.draw.rect(screen, (255, 0, 0), zone, 1)
    offset = Tower.Values.SHIP_SIZE / 2
    pygame.draw.line(screen, (0, 255, 0),
                     (ship.vector.x, ship.vector.y - offset - FEELER_LENGTH),
                     (ship.vector.x, ship.vector.y + offset + FEELER_LENGTH), 1)
    pygame.draw.line(screen, (0, 255, 0),
                     (ship.vector.x - offset - FEELER_LENGTH, ship.vector.y),
                     (ship.vector.x + offset + FEELER_LENGTH, ship.vector.y), 1)
    pygame.draw.rect(screen, (0, 255, 0), getRange(ship), 1)
