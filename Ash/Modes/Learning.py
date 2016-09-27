def main(Tower, player_one, player_two):
    """Set up a student to learn, teach the student, save the result."""
    student = Tower.Manager.New(Tower.Values.PLAYER_TWO, 'Neural', Tower.Minds['Neural'].Brain())

    for i in xrange(25):
        print "%d/25" % (i + 1)
        if Teach(Tower, player_one, player_two, student): break

    text = open('Learnt.txt', 'w')
    text.write(':'.join(str(weight) for weight in student.brain.genome))
    text.write('\n')
    text.close()

def Teach(Tower, player_one, player_two, student):
    """Run a round, use backpropogation to teach the student.

    Setup a new round.
    For every cycle of the round:
        Reset the student values so it is a copy of the teacher.
        Update the game.
        Backpropogate the student for all necessary values.

    """
    Tower.Ships = Tower.Manager.Create(player_one, player_two)
    Tower.Clear()
    while 1:
        #Reset the student values so it is a copy of the teacher.
        student.vector = Tower.Ships[Tower.Values.PLAYER_TWO].vector.Copy()
        student.velocity = Tower.Ships[Tower.Values.PLAYER_TWO].velocity.Copy()
        student.moved = []
        student.output = []

        #Update the game.
        result = Tower.Update()
        if result == Tower.Values.QUIT: return Tower.Values.QUIT
        elif result == Tower.Values.ROUND_END: return 0
        elif result == Tower.Values.ROUND_FINISH: return 0
        
        #Backpropogate the student for all necessary values.
        desired = Tower.Ships[Tower.Values.PLAYER_TWO].moved
        Tower.Minds[student.mind].Update(Tower, student)
        actual = student.moved
        for action in desired:
            if not action in actual:
                Tower.Minds[student.mind].backPropogate(student, action)
