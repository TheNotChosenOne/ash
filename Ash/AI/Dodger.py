"""A version of the Squirrel AI that cares less about the game borders and constantly fires."""
import Squirrel

draw_debug = Squirrel.draw_debug

def RUN(Tower, ship, Desires, Counts):
    """Run away."""
    enemy = Tower.Ships[Tower.Values.otherPlayer(ship.player)]
    if enemy.vector.y > ship.vector.y:
        Desires[Squirrel.GO_UP] += 2
    elif enemy.vector.y < ship.vector.y:
        Desires[Squirrel.GO_DOWN] += 2
    else:
        Desires[Squirrel.random.choice([Squirrel.GO_UP, Squirrel.GO_DOWN])] += Squirrel.WEIGHT_DEATH

def Update(Tower, ship):
    """Update the ship."""
    Squirrel.Update(Tower, ship, care_border=0.731, modifier=RUN)
    Tower.Manager.fireLaser(ship)
    Tower.Manager.fireMissile(ship)

    
