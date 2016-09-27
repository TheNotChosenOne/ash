from Vectors import poolVectors
class BaseEntity(object):
    """A base entity that all moving objects inherit from."""
    def __init__(self, player=None):
        """Initialize the necessary values.

        player -- The player who owns this object (or None)
        vector -- The position of the object
        velocity -- The velocity of the object
        variablePool -- The pool into which the object is put upon deletion

        """
        self.player = player
        self.vector = poolVectors.New()
        self.velocity = poolVectors.New()
        self.variablePool = None
    def Update(self):
        """Update the position with the velocity."""
        self.vector += self.velocity
    @property
    def rect(self):
        """If the object has a rect, return it centred on the object's position."""
        try:
            self.myRect.center = self.vector.Get()
            return self.myRect
        except:
            return None
    def Reset(self):
        """Get a new vector and velocity, to prevent sharing of vectors."""
        self.vector = poolVectors.New()
        self.velocity = poolVectors.New()
    def __del__(self):
        """If the object came from a pool, return it. Also, delete it."""
        try:
            self.variablePool.append(self)
            del self
        except:
            del self
