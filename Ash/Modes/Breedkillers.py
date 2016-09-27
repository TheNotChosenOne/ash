import os
import Genetic
def main(Tower, player_one, player_two):
    """Run the genetic mode, but using a pool of proven genomes."""
    if not os.path.exists('Killers.txt'):
        raise Exception('There are no killers to breed!')
    text = open('Killers.txt', 'r')
    
    Pool = [Tower.Minds['Neural'].Brain([float(val) for val in genome.split(':')]) for genome in text]
    text.close()

    Genetic.main(Tower, player_one, player_two, Pool)
