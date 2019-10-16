# You know the game properties and rules
# you also know how to calc a move (instance/intermediate) state
# now define how the game will proceed initially


# Goal: to play one puzzle that I know to solve, and all its steps, most determinate, only a few non-determinate


# Global state (The decision tree level, all knowing, global state)



from puzzle import (
  get_pieces, 
  get_piece_size_progression, 
  get_holes_and_stats, 
  get_valid_windows, 
  get_piece_to_window_edge_scores, 
  get_cell_count, 
  fill_piece,
)



# TODO: First tryouts: Single Playthrough
# TODO: Second tryouts, multiple playthroughs
# i.e hook up all of the best possible choices at every stage to the hook

class Puzzle:
  def __init__(self):
    # pieces = 
    self.pieces_registry, self.orients_registry = get_pieces()
    # self.orients_registry = get_orients(pieces)
    
  # get_piece('l4_left_r-0')

  def get_piece_info(self, name):
    return self.pieces_registry[name]
    
  def get_orients(self, name):
    return self.orients_registry[name]
    
  def get_piece(self, name, orient):
    # name, orient = piece_id.split('-')
    orient = int(orient)
    return self.orients_registry[name][orient]
    
  def get_pieces(self):
    return self.pieces_registry.keys()
    
  def get_piece_sets(self, names=[]):
    if not names:
      names = self.get_pieces()
    return [self.get_orients(name) for name in names]
    
    

class Solver:
  def __init__(self, board):
    
    self.puzzle = Puzzle()
    
    
    self.board = board
    
    
    # TODO: You have to make per state copies of these
    self.holes = get_holes_and_stats(board['grid'])
    
    
    # TODO: Order by size, 
    # [testing] keep increasing to eventual full array
    # TODO: Maintain a state of percent solved
    self.holes = [self.holes['2hole'], self.holes['3hole'], self.holes['1hole']]
    
    
    # this is only per state
    self.moves = []
    
    # move = {
    #   'piece_name': '',
    #   'piece_orient': '',
    #   'piece_coord': '',
    #   'possible_windows': [], # with chars
    #   'possible_pieces': [], # with chars
    # }
    
    self.available_pieces = list(self.puzzle.get_pieces())
    self.used_pieces = []
    
    self.remaining_holes = []
    self.solved_holes = []
    
    self.magic_wand_placed = False
    
    # TODO: Trigger warnings, lower scores
    self.domino_used = False
    self.r_monomino_used = False
    self.x_monomino_used = False
    
    
    # this is per hole
    
    # go though the holes to see if area <= 4, Those are already solved
    # go through the holes to see which ones can house magic wand
    # Now solve smallest hole first
    # just display the possible pieces on every step
    
  

  def get_piece_sets(self, names=[]):
    return self.puzzle.get_piece_sets(names)
    
    
  # TODO: will be based on the game state 
  def get_next_move(self):
    pass
    
  def solve(self):
    # TODO: Keep track of hole solution score
    
    magic_wand_hole = None
    
    for hole in self.holes:
      # if size big, select for magic wand
      if hole['dim'][0] == 8 or hole['dim'][1] == 8:
         magic_wand_hole = hole
         
    # find valid magic wand positions
    # valid_positions = []
    grid = hole['grid']
    valid_position_windows = {}
    for row in grid:
      if None not in row:
        pos_cell = row[0]
        # valid_positions.append([pos_cell['coord'], 'h', pos_cell['color']])
     
    for idx in range(len(grid[0])):
      col = [row[idx] for row in grid]
      if None not in col:
        pos_cell = col[0]
        # valid_positions.append([pos_cell['coord'], 'v', pos_cell['color']])
    
    
    # select the best position (non-hole-breaking/most edges count for position, leaving hole least crooked)
     
    
    # place the magic wand and get new hole
    
    
    for hole in self.holes:
      self.solve_hole(hole)
      
    
  def solve_hole(self, hole):
    current_hole = hole['grid']

    cell_count = get_cell_count(current_hole)
    piece_size_progression = get_piece_size_progression(cell_count)
    
    # TODO: For testing on more cases, remove once done
    print(piece_size_progression)
    
    # hole offset
    off_y, off_x = hole['offset']
    
    # TODO: Hole piece solve score
    # track the cheat (small) peices used
    hole_solution_score = 0

    while get_cell_count(current_hole):
      next_expected_count = piece_size_progression.pop(0)
      
      sol = self.get_best_hole_move(
        current_hole, 
        self.available_pieces, 
        next_expected_count
      )
      
      if sol:
        winner, score_card, current_hole = sol
      
        self.available_pieces.remove(winner['name'])
        self.used_pieces.append(winner['name'])
      
        # hole_rel_window_pos
        p_y, p_x = winner['coord_pair']
        pos = [off_y + p_y, off_x + p_x]
        self.moves.append([winner, score_card, current_hole, pos])
      else:
        # TODO: more cases
        if next_expected_count == 3:
          piece_size_progression += [2, 1]

    return hole_solution_score
    
    
  def get_best_hole_move(self, hole, available_pieces, next_expected_count=4):
    
    # Keep updating hole state and call this window again
    
    windows = get_valid_windows(hole, next_expected_count) 
    # Take note of the size of window and available pieces to get the possible window cell count combinations
    
    import copy
    
    window_index = {}
    all_possible_pieces = []
    
    # TODO: Special case for the square tile, and all the smaller ones
    # wait, maybe they'll be taken care of anyway. Test and check.
    for win in windows:
      coord, dim, no_of_cells = win
      y, x = int(coord[0]), int(coord[1])
      # h, w = (2, 3) if window_id[2] == 'h' else (3, 2)
      h, w = dim
      
      window_id = coord + str(dim[0]) + str(dim[1])
      
      window = []
      cell_coord_list = []
      for i in range(y, y + h):
        window_row = []
        for j in range(x, x + w):
          cell = copy.copy(hole[i][j])
          if cell:
            if 'rel_coord_pair' in cell:
              cy, cx = cell['rel_coord_pair']
            else:
              cy, cx = cell['coord_pair']
            cy_, cx_ = cy - y, cx - x 
            cell['rel_coord_pair'] = [cy_, cx_]
            cell['rel_coord'] = str(cy_) + str(cx_)
            
            cell_coord_list.append(cell['rel_coord'] + cell['color'])
          
          window_row.append(cell) 

        window.append(window_row)
        
        
      # Piece shortlisting
      possible_pieces = []
      
      # # TODO: if desired 3 not there, 3 = 2 + 1 
      
      # TODO: Looks like pieces should only be stores as nameandorient, and referenced as such
      # Not moved around in 
      for name in available_pieces:
        
        info = self.puzzle.get_piece_info(name)
        # next_expected_count for 4-5-6 size windows is always 4 
        if no_of_cells >= 4:
           next_expected_count = 4
        if info['size'] <= no_of_cells and info['size'] >= next_expected_count:
          
          orients = self.puzzle.get_orients(name)
          for idx, orient in enumerate(orients):
            piece_cell_list = orient['cell_coord_list']
            
            if set(piece_cell_list).issubset(cell_coord_list):
               piece_grid = orient['grid']
               scores, open_edges = get_piece_to_window_edge_scores(piece_grid, window)
               piece_data = {
                 'name': name,
                 'orient': idx,
                 'cell_coord_list': piece_cell_list,
                 'scores': scores,
                 'window_id': window_id,
                 'coord_pair': [y, x],
                 'open_edges': open_edges,
               }
               possible_pieces.append(piece_data)
               all_possible_pieces.append(piece_data)
               
               # store open edges and keep: wherever piece had an edge and window had open edge


      window_index[window_id] = {
        'coord': coord,
        'coord_pair': [y, x],
        'type': window_id[2],  # hori or vert 3*6, TODO: or long small_wand-ish, helper will get approp coords
        
        'grid': window,
        'no_of_cells': no_of_cells,
        'cell_coord_list': cell_coord_list,
        
        'possible_pieces': possible_pieces
      }
      
    
    # # remove
    # print(windows)
      
      
    # TODO: More graceful failing, for handling in the caller
    if not all_possible_pieces:
      return
      
      
    all_possible_pieces = sorted(all_possible_pieces, key=lambda x: x['scores'][-1], reverse=True)
    
    # TODO: IMP, Also check if piece breaks the hole
    # In case of a tie, can check which one makes hole less edge-ful (smoother hole is left in ideal situation)
    highest_scoring_piece = all_possible_pieces[0]
    
    selected_window = window_index[highest_scoring_piece['window_id']]
    
    open_edges = highest_scoring_piece['open_edges']    
    changed_hole = fill_piece(hole, highest_scoring_piece, selected_window['coord_pair'], open_edges)
      
    return highest_scoring_piece, window_index, changed_hole
    
    
    # TODO: Rarer pieces get a 0.5 - 0.95 (< 1) edge point boost, 
    # so that if a rare and a simple have two edges open
    # The rarer one triumphs with a half point
    # But if it's a whole edge difference, the simple one is clear winner
    # In other words, Rarity is a Tie-Breaker, not a one edge extra up
    # Probably only for very high scores though
    # for lower scores (like a rare with 4 edges open) might be better to simply
    # favour the rare one blindly
    
    
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
    
    
