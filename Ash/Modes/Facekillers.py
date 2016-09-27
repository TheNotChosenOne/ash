import os
def main(Tower, player_one, player_two):
    """Set up a match between the given AIs, using the genetic weightings from the killer file."""
    if not os.path.exists('Killers.txt'):
        raise Exception('No killer weighting exists to face!')
    text = open('Killers.txt', 'r')
    Pool = [Tower.Minds['Neural'].Brain([float(val) for val in genome.split(':')]) for genome in text]
    text.close()

    print 'Facing %i killers.' % (len(Pool))
    for genome in Pool:
        setPlayers(Tower, player_one, player_two, genome)
        if Tower.Game.Round() == Tower.Values.QUIT: break

def setPlayers(Tower, player_one, player_two, brain):
    """Set up the ships approproately, so that the correct ships get the given brain."""
    if player_one == player_two == 'Neural':
        Tower.Ships = Tower.Manager.Create(player_one, player_two, brain, brain)
    elif player_one == 'Neural':
        Tower.Ships = Tower.Manager.Create(player_one, player_two, brain)
    elif player_two == 'Neural':
        Tower.Ships = Tower.Manager.Create(player_one, player_two, None, brain)
    else:
        raise Exception('At least one player must be type Neural!')
