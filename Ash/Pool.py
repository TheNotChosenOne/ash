class BasePool(object):
    """A base pool for providing objects."""
    def __init__(self, factory):
        """Set up the pool itself, and the factory."""
        self.pool = []
        self.factory = factory
        self.factory.variablePool = self.pool
        
    def Get(self):
        """Return a new object, from the pool if possible."""
        if self.pool:
            construct = self.pool.pop()
        else:
            construct = self.factory.__class__.__new__(self.factory.__class__)
            construct.__dict__ = self.factory.__dict__.copy()
        return construct
    
    def New(self, vector, player=None):
        """Return a new object, editing the values as appropriate for a BaseEntity derived class."""
        construct = self.Get()
        construct.Reset()
        construct.vector.Set(vector.Get())
        construct.player = player
        return construct
