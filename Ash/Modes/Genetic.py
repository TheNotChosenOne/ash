POOLSIZE = 75
NUMBER_GENERATIONS = float('inf')
RANDOM_NEW_MEMBERS = 0
NUM_ELITE = 4
MUTATION_CHANCE = 0.0032

def Save(Pool):
    """Save the given pool, overwriting any old Pool."""
    text = open('GeneticResults.txt', 'w')
    for brain in Pool:
        text.write(':'.join([str(val) for val in brain.genome]))
        text.write('\n')
    text.close()

def main(Tower, player_one, player_two, Pool = None):
    """Set up the system for efficient testing, then start using genetic to improve the pool of genomes, save the result."""
    if not Pool: Pool = [Tower.Minds['Neural'].Brain() for i in xrange(POOLSIZE)]
    Tower.Game.time_limit = 20000
    player = 0 #The ship that will be used to mark the genome
    if player_one == 'Neural':
        player = 0
        Tower.Game.no_camping = [True, False]
    elif player_two == 'Neural':
        player = 1
        Tower.Game.no_camping = [False, True]

    i = -1
    while i < NUMBER_GENERATIONS: #This allows for easy use of infinite gens
        i += 1
        result = Round(Tower, player_one, player_two, i, player, Pool)
        if result == Tower.Values.QUIT: break
        else: Pool = result
        Save(Pool)
    Save(Pool)
    
def Round(Tower, player_one, player_two, generation, player, Pool):
    """Rate all the genomes, then process and populate the pool.

    The genomes are rated through 3 rounds.
    First is a fair fight against Tree AI.
    Second is an unfair fight in favour of Tree AI.
    Third is a fair fight against Dodger AI.
    This is to make sure the AI can, in order, fight, dodge, and seek.

    """
    
    for i, brain in enumerate(Pool):
        Tower.Game.punish_timeout = False
        setPlayers(Tower, player_one, player_two, 'Tree', False, brain)
        result = Tower.Game.Round()
        if result == Tower.Values.QUIT: return result
        else: brain.fitness = result[1][player]
        
        setPlayers(Tower, player_one, player_two, 'Tree', True, brain)
        result = Tower.Game.Round()
        if result == Tower.Values.QUIT: return result
        else: brain.fitness += result[1][player]

        Tower.Game.punish_timeout = True
        setPlayers(Tower, player_one, player_two, 'Dodger', False, brain)
        result = Tower.Game.Round()
        if result == Tower.Values.QUIT: return result
        else: brain.fitness += result[1][player]
        
    Pool = Process(Tower, Pool, generation)
    if generation + 1 < NUMBER_GENERATIONS:
        Pool = Populate(Tower, Pool)
    return Pool

def Process(Tower, Pool, generation):
    """Set the brain chances for roulette selection, and display generation statistics."""
    Final = sorted(Pool, key=lambda brain: brain.fitness, reverse=True)
    totalFitness = sum([brain.fitness for brain in Final])
    if generation + 1 < NUMBER_GENERATIONS:
        Pool = Final[:POOLSIZE / 2]
        survivorFitness = sum([brain.fitness for brain in Pool])
        soFar = 0.0
        localHigh = -999999999.0
        if survivorFitness:
            for brain in Pool:
                if brain.fitness > localHigh:
                    localHigh = brain.fitness
                brain.chance = abs(soFar + (brain.fitness / survivorFitness))
                soFar += brain.chance
        else:
            for brain in Pool: brain.chance = Tower.Values.random.random()
        print 'Generation %d: Average Fitness: %.3f Average Survivor Fitness: %.3f Highest Fitness: %.3f' %\
              (generation + 1, totalFitness / POOLSIZE, survivorFitness / (POOLSIZE / 2), localHigh)
    else:
        print 'Final Generation %d: Average Fitness: %.3f Highest Fitnes: %.3f' %\
              (generation + 1, sum([brain.fitness for brain in Final]) / POOLSIZE, max([brain.fitness for brain in Final]))
    return Pool

def Populate(Tower, Pool):
    """Populate the new pool. First add elite members, then completely new members, then children."""
    newPop = Pool[:NUM_ELITE]
    newPop += [Tower.Minds['Neural'].Brain() for i in xrange(RANDOM_NEW_MEMBERS)]
    Reproduce = (POOLSIZE - len(newPop) + 1) / 2
    for i in xrange(Reproduce):
        father = Roulette_Select(Tower, Pool)
        mother = Roulette_Select(Tower, Pool)
        newPop.append(Create_New(Tower, father, mother))
        newPop.append(Create_New(Tower, mother, father))
    return newPop[:POOLSIZE]
        
def Roulette_Select(Tower, Pool):
    """Select a genome using roulette selection."""
    num = Tower.Values.random.random()
    for brain in Pool:
        if num <= brain.chance:
            return brain.genome
    return Pool[0].genome

def Create_New(Tower, father, mother):
    """Return a new genome given the father, mother, and mutation chance. First mix the genomes, than mutate appropriately."""
    weight_slice_start = Tower.Values.random.randrange(1, Tower.Minds['Neural'].TOTAL_WEIGHTS - 2)
    weight_slice_end = Tower.Values.random.randrange(weight_slice_start + 1, Tower.Minds['Neural'].TOTAL_WEIGHTS)
    
    threshold_slice_start = Tower.Values.random.randrange(Tower.Minds['Neural'].TOTAL_WEIGHTS, Tower.Minds['Neural'].TOTAL_VALUES - 2)
    threshold_slice_end = Tower.Values.random.randrange(threshold_slice_start + 1, Tower.Minds['Neural'].TOTAL_VALUES)
    
    newGenome = father[:weight_slice_start] + mother[weight_slice_start:weight_slice_end] +\
                father[weight_slice_end:threshold_slice_start] +\
                mother[threshold_slice_start:threshold_slice_end] + father[threshold_slice_end:]
    
    for i in xrange(len(newGenome)):
        if Tower.Values.random.random() <= MUTATION_CHANCE:
            if i < Tower.Minds['Neural'].TOTAL_WEIGHTS: #Weights go from -1 to 1, thresholds from 0 to 1
                newGenome[i] = Tower.Values.random.uniform(-1, 1)
    return Tower.Minds['Neural'].Brain(newGenome)

def setPlayers(Tower, player_one, player_two, facing, pacify_network, brain):
    """Set up the ships approproately, so that the correct ships get the given brain."""
    if player_one == player_two == 'Neural':
        Tower.Manager.Pacify = [pacify_network, False]
        Tower.Ships = Tower.Manager.Create(player_one, player_two, brain, brain)
    elif player_one == 'Neural':
        Tower.Manager.Pacify = [pacify_network, False]
        Tower.Ships = Tower.Manager.Create(player_one, facing, brain)
    elif player_two == 'Neural':
        Tower.Manager.Pacify = [False, pacify_network]
        Tower.Ships = Tower.Manager.Create(facing, player_two, None, brain)
    else:
        raise Exception('At least one player must be type Neural!')
