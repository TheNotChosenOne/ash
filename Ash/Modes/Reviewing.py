import os
def main(Tower, player_one, player_two):
    """Set up a match between the given AIs, one must be a neural AI, which will use the learnt weightings."""
    if not os.path.exists('Learnt.txt'):
        raise Exception('No neural weighting exists to review!')
    text = open('Learnt.txt', 'r')
    student = Tower.Minds['Neural'].Brain([float(val) for val in text.read().split(':')])
    text.close()
    
    while 1:
        setPlayers(Tower, player_one, player_two, student)
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
