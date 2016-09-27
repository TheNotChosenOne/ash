from Pool import BasePool
from math import sqrt

class Vector(object):
    """A vector object which holds an x and y value.

    Supports most math operations.
    Copy -- Return a copy of the vector
    Get -- Return a list of [x, y].
           Return the value of the given parameter.
    Set -- Set the x and y values from a list.
           Set the given parameter's value.
           Set the x and y values to an assumed vector's values.
    Add -- Add the value to both x and y.
           Add the value to the given parameter.
    Sub -- Same as add, but subtracting.
    Invert -- Invert x and y.
              Invert the given parameter.
    Normalize -- Normalize the vector.
    __len__ -- Return the length of the vector.
    __neg__ -- Return the inverse of the vector.
    __del__ -- Send the vector to it's pool.

    """
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    def Copy(self):
        return poolVectors.New(self.x, self.y)
    def Get(self, param=None):
        return getattr(self, param) if param else [self.x, self.y]
    def Set(self, value, param=None):
        if param:
            setattr(self, param, value)
        elif type(value) in (list, tuple):
            self.x, self.y = value
        else:
            self.x = value.x
            self.y = value.y
    def Add(self, value, param=None):
        if param:
            setattr(self, param, getattr(self, param) + value)
        else:
            self.x += value
            self.y += value
    def Sub(self, value, param=None):
        if param:
            setattr(self, param, getattr(self, param) - value)
        else:
            self.x -= value
            self.y -= value
    def Invert(self, param=None):
        if param:
            setattr(self, param, -getattr(self, param))
        else:
            self.x = -self.x
            self.y = -self.y
    def Normalize(self):
        length = len(self)
        if length != 0:
            self.x /= length
            self.y /= length
    def __len__(self):
        return sqrt(self.x ** 2 + self.y ** 2)
    def __neg__(self):
        construct = poolVectors.New()
        construct.x = -self.x
        construct.y = -self.y
        return construct
    def __del__(self):
        self.variablePool.append(self)
        del self
    def __add__(self, other):
        self.x += other.x
        self.y += other.y
        return self
    def __sub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self
    def __mul__(self, other):
        self.x *= other
        self.y *= other
        return self
    def __div__(self, other):
        self.x /= other
        self.y /= other
        return self
    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self
    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self
    def __imul__(self, other):
        self.x *= other
        self.y *= other
        return self
    def __idiv__(self, other):
        self.x /= other
        self.y /= other
        return self
    def __str__(self):
        return 'X: %.3f Y: %.3f' % (self.x, self.y)
    def __repr__(self):
        return str(self)

class VectorPool(BasePool):
    """A pool for the distribution of vectors."""
    def New(self, x=None, y=None):
        """Return the new vector with the correct values."""
        construct = self.Get()
        if x == y == None:
            construct.x = 0
            construct.y = 0
        elif y == None:
            construct.x = x[0]
            construct.y = x[1]
        else:
            construct.x = x
            construct.y = y
        return construct

poolVectors = VectorPool(Vector())
