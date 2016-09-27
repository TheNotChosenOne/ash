from pygame import Rect
from Values import random
from Values import Values
from Entity import BaseEntity
from Vectors import poolVectors

class ShipManager(object):
    """A class responsible for controlling the ships."""
    def __init__(self, key):
        """Link the tower and set up the initial ships."""
        self.Tower = key.Tower
        self.shipSize = key.shipSize
        self.Pacify = key.pacify
        self.Tower.Ships = [self.New(self.Tower.Values.PLAYER_ONE, 0),
                            self.New(self.Tower.Values.PLAYER_TWO, 0)]

    def New(self, player, mind, brain=None):
        """Return a new ship, properly positioned according to it's player."""
        if player == self.Tower.Values.PLAYER_ONE:
            return Ship(50, self.Tower.Visual.height / 2, player, mind, brain)
        elif player == self.Tower.Values.PLAYER_TWO:
            return Ship(self.Tower.Visual.width - 50, self.Tower.Visual.height / 2, player, mind, brain)

    def Create(self, mind1, mind2, brain1=None, brain2=None):
        """Return a list of two ships with the specified paramaters."""
        return [self.New(self.Tower.Values.PLAYER_ONE, mind1, brain1),
                self.New(self.Tower.Values.PLAYER_TWO, mind2, brain2)]

    def Prep(self, ship):
        """Prepare the given ship for another cycle."""
        ship.moved = []
        ship.output = []

    def Update(self, ship):
        """Update the given ship.

        Get the boundary for the ship.
        Simulate the ship's movement.
        If the ship moves out of bounds:
            Find the direction the ship went out of bounds in,
            and reverse the velocity appropriately.
        De-simulate the movement, than actually do the move.
        If necessary, emit particles.
        Decay the velocity.
        Update the ship delays.

        """
        boundary = self.Tower.Boundaries[ship.player]
        ship.Update()
        if not boundary.contains(ship.rect):
            if ship.rect.left < boundary.left:
                ship.velocity.x = 0
                ship.vector.x = boundary.left + (ship.rect.width / 2)
            elif ship.rect.right > boundary.right:
                ship.velocity.x = 0
                ship.vector.x = boundary.right - (ship.rect.width / 2)
            if ship.rect.top < boundary.top:
                ship.velocity.y = 0
                ship.vector.y = boundary.top + (ship.rect.width / 2)
            elif ship.rect.bottom > boundary.bottom:
                ship.velocity.y = 0
                ship.vector.y = boundary.bottom - (ship.rect.width / 2)
        if self.Tower.Visual.level == self.Tower.Values.FANCY:
            emit = -ship.velocity
            self.Tower.Particles += [self.Tower.poolParticles.New(ship.vector, emit)\
                                     for i in xrange(int(abs(emit.x) + abs(emit.y)) / 4)]
        ship.velocity *= self.Tower.Values.VELOCITY_DECAY
        self.updateDelays(ship)

    def updateDelays(self, ship):
        """Update the various delays the ship has."""
        if ship.lasDelay > 0:
            ship.lasDelay -= 1
        if ship.misDelay > 0:
            ship.misDelay -= 1
        if ship.shdValue > 0:
            ship.shdValue -= 1
        if ship.shdDelay > 0:
            ship.shdDelay -= 1
            
    def fireLaser(self, ship):
        """Have the ship fire a laser if it can."""
        ship.moved.append('fireLaser')
        if not self.Pacify[ship.player] and not ship.lasDelay:
            ship.lasDelay = self.Tower.Values.MAX_DELAY_LASER
            self.Tower.Lasers.New(ship)

    def fireMissile(self, ship):
        """Have the ship fire a missile if it can."""
        ship.moved.append('fireMissile')
        if not self.Pacify[ship.player] and not ship.misDelay:
            ship.misDelay = self.Tower.Values.MAX_DELAY_MISSILE
            self.Tower.Missiles.New(ship)

    def fireShield(self, ship):
        """Have the ship activate it's shield if it can."""
        ship.moved.append('fireShield')
        if not ship.shdDelay:
            ship.shdDelay = self.Tower.Values.MAX_DELAY_SHIELD
            ship.shdValue = self.Tower.Values.MAX_VALUE_SHIELD

    def moveUp(self, ship):
        """Increase the ship's upward velocity."""
        ship.moved.append('moveUp')
        ship.velocity.y -= 1

    def moveDown(self, ship):
        """Increase the ship's downward velocity."""
        ship.moved.append('moveDown')
        ship.velocity.y += 1

    def moveFore(self, ship):
        """Increase the ship's forward velocity."""
        ship.moved.append('moveFore')
        if ship.player == self.Tower.Values.PLAYER_ONE:
            ship.velocity.x += 1
        elif ship.player == self.Tower.Values.PLAYER_TWO:
            ship.velocity.x -= 1

    def moveBack(self, ship):
        """Increase the ship's backward velocity."""
        ship.moved.append('moveBack')
        if ship.player == self.Tower.Values.PLAYER_ONE:
            ship.velocity.x -= 1
        elif ship.player == self.Tower.Values.PLAYER_TWO:
            ship.velocity.x += 1


class Ship(BaseEntity):
    """A ship class. It can fly around and shoot and stuff."""
    def __init__(self, x, y, player, mind, brain):
        """Initialize the base entity and other nice variables.

        Artificial Intelligence Variables:
        mind -- The name of the module that controls the ship.
        brain -- A special feature for the neural networks.
        plan -- A list of moves to perform (not yet used).
        moved -- A list of all moves performed in the last cycle.
        output -- Tracks the neural networks' outputs.
        myRect -- A rect for the ship

        Functional Variables:
        health -- How much health the ship has
        lasDelay -- The delay until a laser can be fired again.
        misDelay -- The delay until a missile can be fired again.
        shdDelay -- The delay untilt the shield can be used again.
        shdValue -- The current value of the ship's shield.

        Human Input Variables:
        firLaser -- Whether laser firing has been toggled.
        firMissile -- Whether missile firing has been toggled.

        """
        
        super(self.__class__, self).__init__(player)
        self.vector.Set((x, y))
        self.mind = mind
        self.brain = brain
        self.plan = []
        self.moved = []
        self.output = []
        self.myRect = Rect((0, 0), (Values.SHIP_SIZE, Values.SHIP_SIZE))
        
        self.health = Values.MAX_HEALTH
        self.lasDelay = 0
        self.misDelay = 0
        self.shdDelay = 0
        self.shdValue = 0

        self.firLaser = False
        self.firMissile = False
