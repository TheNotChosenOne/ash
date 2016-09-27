from pygame import Rect
from Entity import BaseEntity
from Pool import BasePool
from Values import Values

class laserManager(object):
    """A manager for all the in game lasers."""
    def __init__(self, key):
        """Link the tower and initialize the pool and laser list."""
        self.Tower = key.Tower
        self.Lasers = []
        self.Pool = BasePool(Laser())
        
    def __iter__(self):
        """Return an iterator for the lasers."""
        return iter(self.Lasers)
    
    def New(self, ship, player=None):
        """Get a laser from the pool and add it to the laser list."""
        if player != None:
            construct = self.Pool.New(self.Tower.poolVectors.New(ship), player)
        else:
            construct = self.Pool.New(ship.vector, ship.player)
        construct.velocity.Set(-self.Tower.Values.LASER_SPEED if construct.player else self.Tower.Values.LASER_SPEED, 'x')
        if player != None:
            return construct
        else:
            self.Lasers.append(construct)
        
    def Update(self):
        """Create a new laser list from all the non-dead lasers."""
        self.Lasers[:] = [laser for laser in self.Lasers if self.specUpdate(laser)]
        
    def specUpdate(self, laser):
        """Update a specific laser.

        Find the laser's target, and check for collision.
        If there is a collision:
            Destroy the laser.
            If the target is not currently shielded, inflict
            damage on the target.
        Else:
            If the laser is offscreen, destroy it.
        return a 0 to destroy the laser, or a 1 if it lives.
        
        """
        laser.Update()
        enemy = self.Tower.Ships[not laser.player]
        if enemy.rect.colliderect(laser.rect):
            if not enemy.shdValue:
                enemy.health -= 1
                if enemy.health < 0: enemy.health = 0
            return 0
        if not self.Tower.Visual.screen.get_rect().contains(laser.rect): return 0
        return 1


class Laser(BaseEntity):
    """A basic projectile that moves in a straight line."""
    def __init__(self):
        """Initialize the base entity and the rect."""
        super(self.__class__, self).__init__()
        self.myRect = Rect((0, 0), (Values.LASER_LENGTH, 1))
        
    @property
    def rect(self):
        """Override the base rect option.

        Return the rect with the topright corner on the laser's position
        if the laser is from player one. Otherwise return the rect with
        the topleft corner on the laser's position.

        """
        if self.player == Values.PLAYER_ONE:
            self.myRect.topright = self.vector.Get()
        elif self.player == Values.PLAYER_TWO:
            self.myRect.topleft = self.vector.Get()
        return self.myRect
