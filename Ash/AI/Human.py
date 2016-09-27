"""Takes human input and translates to ship actions."""
import pygame

UP = 0
DOWN = 1
FORE = 2
BACK = 3
FIRELASER = 4
FIREMISSILE = 5
FIRESHIELD = 6

controls = [[pygame.K_w, pygame.K_s, pygame.K_d, pygame.K_a, pygame.K_q, pygame.K_e, pygame.K_f],
            [pygame.K_i, pygame.K_k, pygame.K_j, pygame.K_l, pygame.K_o, pygame.K_u, pygame.K_h]]

def Update(Tower, ship):
    """For every control being pressed, do the correct action. Also act on the toggle modifiers."""
    if Tower.Input.Keys[controls[ship.player][UP]]:
        Tower.Manager.moveUp(ship)
        
    if Tower.Input.Keys[controls[ship.player][DOWN]]:
        Tower.Manager.moveDown(ship)
        
    if Tower.Input.Keys[controls[ship.player][FORE]]:
        Tower.Manager.moveFore(ship)
        
    if Tower.Input.Keys[controls[ship.player][BACK]]:
        Tower.Manager.moveBack(ship)
        
    if Tower.Input.Keys[controls[ship.player][FIRELASER]]:
        if Tower.TOGGLING:
            ship.firLaser = not ship.firLaser
            Tower.Input.Keys[controls[ship.player][FIRELASER]] = False
        else:
            Tower.Manager.fireLaser(ship)
            
    if Tower.Input.Keys[controls[ship.player][FIREMISSILE]]:
        if Tower.TOGGLING:
            ship.firMissile = not ship.firMissile
            Tower.Input.Keys[controls[ship.player][FIREMISSILE]] = False
        else:
            Tower.Manager.fireMissile(ship)
            
    if Tower.Input.Keys[controls[ship.player][FIRESHIELD]]:
        Tower.Manager.fireShield(ship)
        
    if ship.firLaser:
        Tower.Manager.fireLaser(ship)
        
    if ship.firMissile:
        Tower.Manager.fireMissile(ship)
