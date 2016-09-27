"""A passive AI.

This AI counts all projectiles in a certain range based on where
they are in relation to the ship. Using these sector counts, the
ship attempts to head away from as many projectiles as possible
without running into borders. It also attempts to follow it's
opponent as much as possible without dying or going close to
the edges (which it tries to avoid).

"""

import os
import sys
sys.path.append(os.path.abspath(os.path.join('Ash')))
from Values import random
import pygame

DETECT_FRONT = 150
DETECT_BACK = 50
DETECT_HEIGHT = 80
DETECT_BORDER = 150
DEATH_DETECTION = 30
WEIGHT_BORDER = 2
WEIGHT_LASER = 1
WEIGHT_MISSILE = 2
WEIGHT_DEATH = 10
WEIGHT_CENTRE = 5
WEIGHT_CHASE = 0.5

GO_DOWN = 0
GO_UP = 1
GO_FORWARD = 2
GO_BACK = 3

FRONT_TOP = 0
FRONT_MID = 3
FRONT_LOW = 6
MID_TOP = 1
MID_LOW = 7
BACK_TOP = 2
BACK_MID = 5
BACK_LOW = 8
SHIP_SHIELD = 4

Sectors = []
#Ship 0 Ship 1
####### #######
#2.1.0# #0.1.2#
#5.4.3# #3.4.5#
#8.7.6# #6.7.8#
####### #######
#4 is ship
def Init(Tower):
    """Set up the sectors."""
    global Sectors
    size = Tower.Manager.shipSize
    Sectors = [pygame.Rect((0, 0), (DETECT_FRONT, DETECT_HEIGHT)),  #Sector 0
               pygame.Rect((0, 0), (size, DETECT_HEIGHT)),          #Sector 1
               pygame.Rect((0, 0), (DETECT_BACK, DETECT_HEIGHT)),   #Sector 2
               pygame.Rect((0, 0), (DETECT_FRONT, size)),           #Sector 3
               pygame.Rect((0, 0), (size, size)),                   #Sector 4
               pygame.Rect((0, 0), (DETECT_BACK, size)),            #Sector 5
               pygame.Rect((0, 0), (DETECT_FRONT, DETECT_HEIGHT)),  #Sector 6
               pygame.Rect((0, 0), (size, DETECT_HEIGHT)),          #Sector 7
               pygame.Rect((0, 0), (DETECT_BACK, DETECT_HEIGHT))]   #Sector 8
    Sectors[SHIP_SHIELD].inflate_ip(DEATH_DETECTION, DEATH_DETECTION)

def getSectors(ship):
    """Align the sectors around the ship, keeping in mind the ships face different directions."""
    global Sectors
    rect = ship.rect
    if ship.player == 0:
        Sectors[FRONT_TOP].bottomleft = rect.topright
        Sectors[MID_TOP].bottomleft = rect.topleft
        Sectors[BACK_TOP].bottomright = rect.topleft
        Sectors[FRONT_MID].topleft = rect.topright
        Sectors[SHIP_SHIELD].center = rect.center
        Sectors[BACK_MID].topright = rect.topleft
        Sectors[FRONT_LOW].topleft = rect.bottomright
        Sectors[MID_LOW].topleft = rect.bottomleft
        Sectors[BACK_LOW].topright = rect.bottomleft
    else:
        Sectors[FRONT_TOP].bottomright = rect.topleft
        Sectors[MID_TOP].bottomleft = rect.topleft
        Sectors[BACK_TOP].bottomleft = rect.topright
        Sectors[FRONT_MID].topright = rect.topleft
        Sectors[SHIP_SHIELD].center = rect.center
        Sectors[BACK_MID].topleft = rect.topright
        Sectors[FRONT_LOW].topright = rect.bottomleft
        Sectors[MID_LOW].topleft = rect.bottomleft
        Sectors[BACK_LOW].topleft = rect.bottomright
    return Sectors

def draw_debug(Tower, ship, screen):
    """Draw the sectors to the screen."""
    for sector in getSectors(ship):
        pygame.draw.rect(screen, (255, 0, 0), sector, 1)

def fact_sum(num):
    """Attempt to predict the distance travelled after coming to a complete stop."""
    num = num if num >= 0 else -num
    return (1 + num) * (num / 2.0)

def CountProjectiles(Tower, ship, Counts):
    """Find all projectiles and increments the counters as appropriate. Also check for imminent death."""
    deathImminent = False
    Sectors = getSectors(ship)
    for laser in Tower.Lasers:
        if laser.player != ship.player:
            for i, sector in enumerate(Sectors):
                if sector.collidepoint(laser.vector.Get()):
                    Counts[i] += WEIGHT_LASER
                    if i == SHIP_SHIELD:
                        deathImminent = True
                    break
    for missile in Tower.Missiles:
        if missile.player != ship.player:
            for i, sector in enumerate(Sectors):
                if sector.colliderect(missile.rect):
                    Counts[i] += WEIGHT_MISSILE
                    if i == SHIP_SHIELD:
                        deathImminent = True
                    break
    return deathImminent

def CountBorder(Tower, ship, Counts, Desires, care_border):
    """Increment counters and desires to stay away from the game borders, unless necessary (opponent is there.)"""
    enemy = Tower.Ships[not ship.player]
    if ship.vector.y > Tower.Visual.height - DETECT_BORDER and not enemy.vector.y > Tower.Visual.height - DETECT_BORDER:
        Counts[MID_LOW] += (WEIGHT_BORDER * care_border)
    if ship.vector.y < DETECT_BORDER and not enemy.vector.y < 150:
        Counts[MID_TOP] += (WEIGHT_BORDER * care_border)
    if ship.vector.y > enemy.vector.y:
        if ship.vector.y > enemy.vector.y + fact_sum(ship.velocity.y):
            Desires[GO_UP] += (WEIGHT_CHASE * care_border)
        else:
            Desires[GO_DOWN] += (WEIGHT_CHASE * care_border)
    elif ship.vector.y < enemy.vector.y:
        if ship.vector.y < enemy.vector.y - fact_sum(ship.velocity.y):
            Desires[GO_DOWN] += (WEIGHT_CHASE * care_border)
        else:
            Desires[GO_UP] += (WEIGHT_CHASE * care_border)

def preEvade(Counts, Desires):
    """Do a basic evasion."""
    Desires[GO_DOWN] += (Counts[FRONT_TOP] + Counts[MID_TOP] * 4 + Counts[BACK_TOP]) / 4.0
    Desires[GO_UP] += (Counts[FRONT_LOW] + Counts[MID_LOW] * 4 + Counts[BACK_LOW]) / 4.0
    Desires[GO_BACK] += (Counts[FRONT_TOP] + Counts[FRONT_MID] + Counts[FRONT_LOW]) * 2

def Evade(Tower, ship, Desires, Counts):
    """Work out the best direction to go in order to evade incoming projectiles.

    Move back.
    If the ship is already too high or to low to dodge in either vertical dirction,
    move away from the border.
    elif there is more danger in one vertical direction than another, move to the safe side.
    elif the ship is already moving in a direction, keep going.
    else move in a random direction.

    """
    Desires[GO_BACK] += Counts[FRONT_MID] * 2

    if ship.vector.y < DETECT_BORDER:
        Desires[GO_DOWN] += 10
    elif ship.vector.y > Tower.Visual.height - DETECT_BORDER:
        Desires[GO_UP] += 10
        
    elif Counts[FRONT_TOP] + Counts[MID_TOP] + Counts[BACK_TOP] >\
       Counts[FRONT_LOW] + Counts[MID_LOW] + Counts[BACK_LOW]:
        Desires[GO_DOWN] += 1
    elif Counts[FRONT_LOW] + Counts[MID_LOW] + Counts[BACK_LOW] >\
         Counts[FRONT_TOP] + Counts[MID_TOP] + Counts[BACK_TOP]:
        Desires[GO_UP] += 1
        
    elif ship.velocity.y > 0:
        Desires[GO_DOWN] += 1
    elif ship.velocity.y < 0:
        Desires[GO_UP] += 1
        
    elif random.choice([0, 1]):
        Desires[GO_UP] += 1
    else:
        Desires[GO_DOWN] += 1

def advancedEvade(Tower, ship, Desires, Counts):
    if Counts[1] or Counts[7]:
        Desires[GO_FORWARD] += 1
    if ship.velocity.y < 0 and Counts[1]:
        Desires[GO_DOWN] += WEIGHT_DEATH
    elif ship.velocity.y > 0 and Counts[7]:
        Desires[GO_UP] += WEIGHT_DEATH
    if Counts[0] or Counts[6]:
        Desires[GO_FORWARD] += 4

def CentreShip(Tower, ship, Desires):
    """Attempt to keep the ship in the horizontal centre of it's side."""
    if ship.player == Tower.Values.PLAYER_ONE:
        if ship.vector.x < Tower.Boundaries[ship.player].centerx:
            if ship.vector.x + fact_sum(ship.velocity.x) < Tower.Boundaries[ship.player].centerx:
                Desires[GO_FORWARD] += WEIGHT_CENTRE
        elif ship.vector.x > Tower.Boundaries[ship.player].centerx:
            if ship.vector.x - fact_sum(ship.velocity.x) < Tower.Boundaries[ship.player].centerx:
                Desires[GO_BACK] += WEIGHT_CENTRE
    elif ship.player == Tower.Values.PLAYER_TWO:
        if ship.vector.x > Tower.Boundaries[ship.player].centerx:
            if ship.vector.x - fact_sum(ship.velocity.x) > Tower.Boundaries[ship.player].centerx:
                Desires[GO_FORWARD] += WEIGHT_CENTRE
        elif ship.vector.x < Tower.Boundaries[ship.player].centerx:
            if ship.vector.x + fact_sum(ship.velocity.x) < Tower.Boundaries[ship.player].centerx:
                Desires[GO_BACK] += WEIGHT_CENTRE

def SlowShip(Tower, ship, Desires):
    """Slow the ship down if it doesn't need to be moving."""
    if ship.velocity.y > 0:
        if not Desires[GO_DOWN]:
            Desires[GO_UP] += 1
    elif ship.velocity.y < 0:
        if not Desires[GO_UP]:
            Desires[GO_DOWN] += 1
    if ship.player == Tower.Values.PLAYER_ONE:
        if ship.velocity.x > 0:
            if not Desires[GO_FORWARD]:
                Desires[GO_BACK] += 1
        elif ship.velocity.x < 0:
            if not Desires[GO_BACK]:
                Desires[GO_FORWARD] += 1
    elif ship.player == Tower.Values.PLAYER_TWO:
        if ship.velocity.x > 0:
            if not Desires[GO_BACK]:
                Desires[GO_FORWARD] += 1
        elif ship.velocity.x < 0:
            if not Desires[GO_FORWARD]:
                Desires[GO_BACK] += 1

def Move(Tower, ship, Desires):
    """Make the final moves as dictated by the desires."""
    if Desires[GO_UP] > Desires[GO_DOWN]:
        Tower.Manager.moveUp(ship)
    elif Desires[GO_DOWN] > Desires[GO_UP]:
        Tower.Manager.moveDown(ship)
    if Desires[GO_FORWARD] > Desires[GO_BACK]:
        Tower.Manager.moveFore(ship)
    elif Desires[GO_BACK] > Desires[GO_FORWARD]:
        Tower.Manager.moveBack(ship)

def Update(Tower, ship, care_border=0.731, modifier=None):
    """Update the ship.

    Setup up the two important lists.
    Estimate the danger provided by projectiles.
    Keep the borders in mind if necessary.
    Do a basic evasion.
    If necessary, do a more complex evasion.
    Attempt to keep the ship centred.
    Move the ship as the previous functions make it desire.

    """
    Counts = [0 for i in xrange(9)]
    Desires = [0 for i in xrange(4)]
    if CountProjectiles(Tower, ship, Counts): Tower.Manager.fireShield(ship)
    CountBorder(Tower, ship, Counts, Desires, care_border)
    preEvade(Counts, Desires)
    if Counts[FRONT_MID]: Evade(Tower, ship, Desires, Counts)
    advancedEvade(Tower, ship, Desires, Counts)
    CentreShip(Tower, ship, Desires)
    if modifier: modifier(Tower, ship, Desires, Counts)
    SlowShip(Tower, ship, Desires)
    Move(Tower, ship, Desires)
