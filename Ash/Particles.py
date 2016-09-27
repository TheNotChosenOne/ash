from Values import random
from Values import Values
from Entity import BaseEntity
from Pool import BasePool

class Particle(BaseEntity):
    """A particle designed to move randomly and eventually die."""
    def __init__(self):
        """Initialize the entity and values."""
        super(self.__class__).__init__(self.__class__)
        self.life = 50
        self.decay = 0.9
        self.scatter = 0.137
        self.colour = (255, 255, 255)
        
    def Update(self):
        """Update the position, then randomize velocity. Return 0 if dead, else 1."""
        super(self.__class__, self).Update()
        self.life -= 1
        velX = self.velocity.x
        velY = self.velocity.y
        self.vector.x += velX
        self.vector.y += velY
        velX *= self.decay
        velY *= self.decay
        change = int(((velX if velX >= 0 else -velX) + (velY if velY >= 0 else -velY) + 7) * self.scatter)
        self.velocity.x += random.randrange(-change, change + 1)
        self.velocity.y += random.randrange(-change, change + 1)
        if self.life <= 0: return 0
        return 1

class ParticlePool(BasePool):
    """A pool for the use of Particles."""
    def New(self, vector, velocity, life=None, colourset='fire'):
        """Return a new particle, either from the pool or a created one."""
        construct = super(self.__class__, self).New(vector)
        construct.velocity.Set(velocity.Get())
        construct.velocity *= Values.PARTICLE_BIRTH_DECAY
        construct.colour = random.choice(Colours[colourset])
        if life: construct.life = life
        else: construct.life = self.factory.life
        return construct

poolParticles = ParticlePool(Particle())
Colours = {'fire':[(255, 0, 0), (200, 0, 0), (100, 0, 0), (255, 215, 0), (205, 55, 0), (81, 81, 81)],
           'none':[(255, 255, 255)],
           'shades':[tuple([i for j in xrange(3)]) for i in xrange(1, 256)]}
