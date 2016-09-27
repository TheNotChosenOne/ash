from pygame import Rect
from Values import random
from Values import Values
from Vectors import poolVectors
from Entity import BaseEntity
from Pool import BasePool

class missileManager(object):
    """A manager for all the in game missiles."""
    def __init__(self, key):
        """Link the tower and initialize the pool and missile list."""
        self.Tower = key.Tower
        self.Missiles = []
        self.Pool = BasePool(Missile())
            
    def __iter__(self):
        """Return an iterator for the missiles."""
        return iter(self.Missiles)
    
    def New(self, ship, player=None):
        """Get a missiles from the pool and add it to the missiles list."""
        if player != None:
            construct = self.Pool.New(self.Tower.poolVectors.New(ship), player)
        else:
            construct = self.Pool.New(ship.vector, ship.player)
        construct.velocity.x = -construct.speed if construct.player else construct.speed
        if player != None:
            return construct
        else:
            self.Missiles.append(construct)
    
    def Update(self):
        """Create a new missile list from the non-dead missiles."""
        self.Missiles[:] = [missile for missile in self.Missiles if self.specUpdate(missile)]
    
    def specUpdate(self, missile):
        """Update a specific missile.

        Find a velocity for the missile.
        Update the missile.
        Emit particles if necessary.
        Return the result of a collision check.

        """
        enemy = self.Tower.Ships[not missile.player]
        self.specFindVelocity(missile, enemy)
        missile.Update()
        if self.Tower.Visual.level == self.Tower.Values.FANCY:
            emit = -missile.old_velocity
            self.Tower.Particles += [self.Tower.poolParticles.New(missile.vector, emit)\
                                     for i in xrange(int((abs(emit.x) + abs(emit.y)) / 4))]
        return self.specCheckCollision(missile, enemy)

    def specFindVelocity(self, missile, enemy):
        """Find the correct velocity for a missile to smoothly hit it's target.

        If the missile is going up and the projected location is beneath the target position,
            or the missile is going down and the projected location is above the target position,
            than speed the missile up if possible.
        Else:
            If the missile is above the enemy, increase the downwards velocity if possible.
            If the missile is beneath the enemy, increase the upwards velocity if possible.

        """
        if (missile.velocity.y < 0 and missile.vector.y - Sum(int(missile.velocity.y - 1)) < enemy.vector.y) or\
           (missile.velocity.y > 0 and missile.vector.y + Sum(int(missile.velocity.y + 1)) > enemy.vector.y):
            if missile.velocity.y > 0:
                missile.velocity.y -= 1
            elif missile.velocity.y < 0:
                missile.velocity.y += 1
        else:
            if missile.vector.y - enemy.vector.y < 0:
                if missile.velocity.y + 1 <= missile.speed:
                    missile.velocity.y += 1
            elif missile.vector.y - enemy.vector.y > 0:
                if missile.velocity.y - 1 >= -missile.speed:
                    missile.velocity.y -= 1

    def specCheckCollision(self, missile, enemy):
        """Check for collisions on the given missile.

        Get the Rect that covers the area of the new and old positions.
        If the enemy ship collides with that rectangle:
            Check all the positions between old and new for
            collision with the ship.
        Else:
            Check that the missile is still on screen.
        Return 0 if the missile should be destroyed, else 1.

        """
        check = missile.rect.union(missile.old_rect)
        if enemy.rect.colliderect(check):
            check = missile.rect
            step = missile.old_velocity.Copy()
            current = missile.old_vector.Copy()
            step.Normalize()
            for i in xrange(int(len(missile.velocity))):
                check.center = current.Get()
                if enemy.rect.colliderect(check):
                    if not enemy.shdValue:
                        enemy.health -= 2
                        if enemy.health <= -1:
                            enemy.health = 0
                    return 0
                current += step
        if not self.Tower.Visual.screen.get_rect().colliderect(missile.rect): return 0
        return 1

def Sum(num):
    """Find the distance that would be travelled before the missile could come to a complete vertical stop."""
    num = num if num >= 0 else -num
    return (num + 1) * (num / 2.0)

class Missile(BaseEntity):
    """A projectile that attempts to follow it's target without changing horizontal velocity."""
    def __init__(self):
        """Initialize the base entity, speed, and rect."""
        super(self.__class__, self).__init__()
        self.speed = Values.MISSILE_SPEED
        self.myRect = Rect((0, 0), (Values.MISSILE_SIZE, Values.MISSILE_SIZE))

        self.old_vector = self.vector.Copy()
        self.old_velocity = self.velocity.Copy()
        self.old_rect = None

    def Update(self):
        """Edit the base update to leave a copy of the new vector, velocity, and rect."""
        super(self.__class__, self).Update()
        self.old_vector = self.vector.Copy()
        self.old_velocity = self.velocity.Copy()
        self.old_rect = self.rect.copy()
