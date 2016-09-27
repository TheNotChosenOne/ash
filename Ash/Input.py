import pygame

class InputManager(object):
    def __init__(self, key):
        self.Tower = key.Tower
        self.Keys = [False for i in xrange(256)]

    def Update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return self.Tower.Values.QUIT
            elif event.type == pygame.KEYDOWN:
                if event.key <= 255:
                    if event.key == pygame.K_ESCAPE: return self.Tower.Values.QUIT
                    elif event.key == pygame.K_RETURN: return self.Tower.Values.ROUND_END
                    self.Keys[event.key] = True
            elif event.type == pygame.KEYUP:
                if event.key <= 255:
                    self.Keys[event.key] = False
        return 0
