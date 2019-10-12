# You know the game properties and rules
# you also know how to calc a move (instance/intermediate) state
# now define how the game will proceed initially


# Goal: to play one puzzle that I know to solve, and all its steps, most determinate, only a few non-determinate


# Global state (The decision tree level, all knowing, global state)



from puzzle import get_pieces, get_holes_and_stats



# TODO: First tryouts: Single Playthrough
# TODO: Second tryouts, multiple playthroughs
# i.e hook up all of the best possible choices at every stage to the hook

class Solver:
  def __init__(self, board):
    self.board = board
    
    
    # TODO: You have to make per state copies of these
    self.holes = get_holes_and_stats(board['grid'])
    self.pieces = get_pieces()
    
    
    # this is only per state
    self.moves = []
    
    
    
    # go though the holes to see if area <= 4, Those are already solved
    
    # go through the holes to see which ones can house magic wand
    
    # Now solve smallest hole first
    
    
