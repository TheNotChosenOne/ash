"""A non-passive of the Squirrel AI that constantly fires."""
import Squirrel

draw_debug = Squirrel.draw_debug

def Update(Tower, ship):
    Squirrel.Update(Tower, ship)
    Tower.Manager.fireLaser(ship)
    Tower.Manager.fireMissile(ship)
