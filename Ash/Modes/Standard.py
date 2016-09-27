def main(Tower, player_one, player_two):
    """Run a standard game repeatedly until the game is quit."""
    while 1:
        Tower.Ships = Tower.Manager.Create(player_one, player_two)
        Result = Tower.Game.Round()
        if Result == Tower.Values.QUIT: break
        else: print Result
