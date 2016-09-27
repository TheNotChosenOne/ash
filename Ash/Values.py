import random
random.seed()

class ValueManager(object):
    """A class for managing constants and helping find values."""
    def __init__(self):
        """Initialize the game constants."""
        self.random = random
        self.PLAYER_ONE = 0
        self.PLAYER_TWO = 1

        self.PRIMARY = 0
        self.SECONDARY = 1
        self.TERTIARY = 2
        self.FANCY = 1
        self.FAST = 2
        self.OFF = 3

        self.QUIT = -2
        self.ROUND_END = -1
        self.ROUND_FINISH = 1

        self.MAX_CAMPING_TIME = 30
        self.CAMPING_ALLOWANCE = 4

        self.MAX_HEALTH = 5

        self.LASER_LENGTH = 5
        self.LASER_SPEED = 5
        self.MISSILE_SIZE = 5
        self.MISSILE_SPEED = 10

        self.SHIP_SIZE = 20
        self.VELOCITY_DECAY = 0.98
        self.MAX_DELAY_LASER = 7
        self.MAX_DELAY_MISSILE = 45
        self.MAX_DELAY_SHIELD = 200
        self.MAX_VALUE_SHIELD = 50

        self.PARTICLE_BIRTH_DECAY = 0.3
        
    def otherPlayer(self, player):
        """Return the player that is not the given player."""
        return not player
Values = ValueManager()
