# You know the game properties and rules
# you also know how to calc a move (instance/intermediate) state
# now define how the game will proceed initially


# Goal: to play one puzzle that I know to solve, and all its steps, most determinate, only a few non-determinate


# Global state (The decision tree level, all knowing, global state)



from puzzle import get_pieces, get_holes_and_stats, get_valid_windows



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
    
    # move = {
    #   'piece_name': '',
    #   'piece_orient': '',
    #   'piece_coord': '',
    #   'possible_windows': [], # with chars
    #   'possible_pieces': [], # with chars
    # }
    
    self.available_pieces = []
    self.used_pieces = []
    
    self.remaining_holes = []
    self.solved_holes = []
    
    self.magic_wand_placed = False
    
    
    # this is per hole
    
    
    
    # go though the holes to see if area <= 4, Those are already solved
    # go through the holes to see which ones can house magic wand
    # Now solve smallest hole first
    # just display the possible pieces on every step
    
    
    self.solve()
    
    
  def solve(self):
    
    hole = self.holes['1hole']['grid']
    windows = get_valid_windows(hole)
    
    window_index = {
      # 'coord_n_type': {
      #   'coord': '',
      #   'coord_pair': [],
      #   'type': '', # hori or vert 3*6, or long small_wand-ish, helper will get approp coords
      #   'no_of_cells': 0,
      #   'no_of_edges': 0,
      #
      #   # after inital filter
      #   'valid_pieces': [
      #     # pieces with respective scores
      #   ],
      #
      #   # from before itself, or after this window is selected
      #   'connecting_valid_windows': []
      # }
    }
    
    self.scans = []
    
    import copy
    
    for window in windows:
      coord = window[:2]
      y, x = int(coord[0]), int(coord[1])
      h, w = (2, 3) if window[2] == 'h' else (3, 2)
      
      scan = []
      for i in range(y, y + h):
        scan_row = []
        for j in range(x, x + w):
          cell = hole[i][j]
          scan_row.append(copy.copy(cell)) 

        scan.append(scan_row)
    
      self.scans.append(scan)
    
    
    # TODO: also a window for the small wand has to be scanned every move
    
    # don't recalc windows after a move, recycle prev windows only
    # i.e remove those windows
    
    # oh, you'll have to change the edges now
    # No worries, windows are just limits, implement a function to get the hole view with it
    # That's what they're supposed to be
    
    # Meanwhile after a move, every edge that the piece was and the window wasn't 
    
    # BUT
    # windows are just windows but they need to be able to see the rel_coords, to compare with pieces
    # Non persistence you have to check again and again 
    
    
