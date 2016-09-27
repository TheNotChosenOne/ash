import os
def main(Tower, player_one, player_two):
    """Load the last genetic pool and face all it's members."""
    if not os.path.exists('GeneticResults.txt'):
        raise Exception('There is no pool to review!')
    text = open('GeneticResults.txt', 'r')
    Pool = [Tower.Minds['Neural'].Brain([float(val) for val in genome.split(':')]) for genome in text]
    text.close()
    
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
