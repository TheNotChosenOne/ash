import os
class GameManager(object):
    """A class for running a match between two ships."""
    def __init__(self, key):
        """Set up the default values for a round.

        Game Variables:
        time_limit -- The time limit for a round (in milliseconds)
        killer_opponents -- A list of AI's, the beating of which will have the winning genome saved.
        punish_timeout -- Whether or not to subtract points for a timeout

        Camping Variables:
        no_camping -- Whether or not camping (staying in one spot for too long)
                      is allowed
        old_positions -- A pair of rects for tracking the position of the two ships 
        camp_times -- Two counters to track how long a ship has been in one place

        Result Variables:
        winner -- The winner of the round, or non-camping ship
        loser -- The loser of the round, or camping ship
        camper -- The camper (if there was one)
        round_length -- The length of the round (in milliseconds)
        scores -- The scores for the ships
        
        """
        self.Tower = key.Tower
        
        self.time_limit = 0
        self.killer_opponents = key.killer_opponents
        self.punish_timeout = False
        
        self.no_camping = key.no_camping
        self.old_positions = [None, None]
        self.camp_times = [0, 0]
        
        self.winner = None
        self.loser = None
        self.camper = None
        self.round_length = 0
        self.scores = [0.0, 0.0]

    def Reset(self):
        self.winner = None
        self.loser = None
        self.camper = None
        self.round_length = 0.0
        self.scores = [0.0, 0.0]
        
    def checkCamping(self):
        """Return the value of a ship staying in one place for too long, or None."""
        for i, ship in zip([self.Tower.Values.PLAYER_ONE, self.Tower.Values.PLAYER_TWO], self.Tower.Ships):
            if not self.no_camping[i]:
                continue
            if self.old_positions[i].contains(ship.rect):
                if self.camp_times[i]:
                    self.camp_times[i] -= 1
                else:
                    self.camper = i
                    return True
            else:
                self.camp_times[i] = self.Tower.Values.MAX_CAMPING_TIME
            self.old_positions[i] = ship.rect.copy().inflate(self.Tower.Values.CAMPING_ALLOWANCE,
                                                        self.Tower.Values.CAMPING_ALLOWANCE)
        return False

    def findScore(self):
        """Return two scores, one for each ship.

        Score is found as follows:
            A ship starts with a score of 0.
            50 points are awarded for every hit the opponent ship has taken.
            If the ship had died:
                410 points are subtracted
                if there is a time limit, points are subtracted for every
                millisecond left on the clock.
            Else:
                10 points are subtracted for every hit taken.
                If there is a time limit, points are added for every
                millisecond left on the clock.
            If the ship was camping, 1000 points are subtracted

        If one of the killer_opponents has lost to a neural network, save the weightings.

        """
        if self.winner != None and self.loser != None:
            for ship_a, ship_b in [[self.Tower.Ships[self.winner], self.Tower.Ships[self.loser]],
                                   [self.Tower.Ships[self.loser], self.Tower.Ships[self.winner]]]:
                self.scores[ship_a.player] += (self.Tower.Values.MAX_HEALTH - ship_b.health) * 50
                if ship_a.health <= 0:
                    self.scores[ship_a.player] -= 410
                    if self.time_limit: self.scores[ship_a.player] -= (self.time_limit - self.round_length) / 1000.0
                else:
                    self.scores[ship_a.player] -= (self.Tower.Values.MAX_HEALTH - ship_a.health) * 10
                    if self.time_limit: self.scores[ship_a.player] += (self.time_limit - self.round_length) / 1000.0
            if self.no_camping and self.camper: self.scores[self.camper] -= 1000

        if self.Tower.Ships[self.winner].mind == 'Neural':
            if self.Tower.Ships[self.loser].mind in self.killer_opponents:
                killer_genome = ':'.join([str(val) for val in self.Tower.Ships[self.winner].brain.genome])

                if os.path.exists('Killers.txt'):
                    text = open('Killers.txt', 'r+')
                    already = set([line.strip() for line in text])
                    if not killer_genome in already:
                        text.write(killer_genome)
                        text.write('\n')
                else:
                    text = open('Killers.txt', 'w')
                    text.write(killer_genome)
                    text.write('\n')
                text.close()
        if self.punish_timeout and self.time_limit and self.Tower.time >= self.time_limit:
            self.scores[0] -= 1000
            self.scores[1] -= 1000

    def Round(self):
        """Run a match between two players."""
        self.Tower.Clear()
        self.Reset()
        
        if any(self.no_camping):
            self.camper = None
            self.camp_times = [self.Tower.Values.MAX_CAMPING_TIME, self.Tower.Values.MAX_CAMPING_TIME]
            self.old_positions = [ship.rect.copy().inflate(self.Tower.Values.CAMPING_ALLOWANCE,
                                                           self.Tower.Values.CAMPING_ALLOWANCE) for ship in self.Tower.Ships]
        while 1:
            if self.time_limit and self.Tower.time >= self.time_limit: break
            
            result = self.Tower.Update()
            if result == self.Tower.Values.QUIT: return self.Tower.Values.QUIT
            elif result == self.Tower.Values.ROUND_END: break
            elif result == self.Tower.Values.ROUND_FINISH: break
            
            if self.no_camping and self.checkCamping(): return self.End()
        return self.End()

    def End(self):
        """Return the winner and scores."""
        self.round_length = self.Tower.time
        
        if self.Tower.Ships[self.Tower.Values.PLAYER_ONE].health <= 0:
            self.winner = self.Tower.Values.PLAYER_TWO
            self.loser = self.Tower.Values.PLAYER_ONE
        else:
            self.winner = self.Tower.Values.PLAYER_ONE
            self.loser = self.Tower.Values.PLAYER_TWO
        
        if self.no_camping and self.camper:
            self.winner = self.Tower.Values.otherPlayer(self.camper)
            self.loser = self.camper

        self.findScore()

        return self.winner, self.scores
