import os
import Genetic
def main(Tower, player_one, player_two):
    """Run the genetic mode, but using the previously saved pool."""
    if not os.path.exists('GeneticResults.txt'):
        raise Exception('There is no pool to breed!')
    text = open('GeneticResults.txt', 'r')
    
    Pool = [Tower.Minds['Neural'].Brain([float(val) for val in genome.split(':')]) for genome in text]
    text.close()

    Genetic.main(Tower, player_one, player_two, Pool)
