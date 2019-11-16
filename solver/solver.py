# You know the game properties and rules
# you also know how to calc a move (instance/intermediate) state
# now define how the game will proceed initially


# Goal: to play one puzzle that I know to solve, and all its steps, most determinate, only a few non-determinate

# Rule: only store deduced info, not intermediate info
# Trye to save all intermediate data as storage as well


# Global state (The decision tree level, all knowing, global state)


import copy
from puzzle import (
  get_pieces, 
  get_holes_from_grid,
  get_piece_size_progression, 
  get_holes,
  get_valid_windows, 
  get_long_windows,
  get_piece_to_window_edge_scores, 
  get_edge_matches_total_score,
  get_cell_count, 
  DIR_OPS,
  DIR_REVS,
  SMALL_HOLE_SIZE
)

MAX_MAGIC_WAND_INIT_EDGES = 11



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
    # TODO: called twice or many times. Reduce.
    orient = int(orient)
    return self.orients_registry[name][orient]
    
  def get_pieces(self):
    return self.pieces_registry.keys()
    
  def get_piece_sets(self, names=[]):
    if not names:
      names = self.get_pieces()
    return [self.get_orients(name) for name in names]


puzzle = Puzzle()


class Solver:
  def __init__(self, board, pieces):
    self.board = board
    # TODO: You have to make per state copies of these
    # TODO: Maintain a state of percent solved
    self.all_holes = get_holes_from_grid(board['grid']) 
    self.holes = self.all_holes[:]
    self.progressions = [get_piece_size_progression(hole['size']) for hole in self.holes]
    
    # this is only per state
    self.moves = []
    self.solved = False
    
    self.available_pieces = pieces
    self.used_pieces = []
    
    self.current_hole = self.holes.pop(0)
    self.current_hole_index = 0
    self.current_offset = self.current_hole['offset']
    self.current_hole_grid = copy.copy(self.current_hole['grid'])
    self.current_progression = self.progressions.pop(0)
    
    self.magic_wand_placed = False
    self.small_wand_placed = False
    
    # TODO: Trigger warnings, lower scores
    self.domino_used = False
    self.r_monomino_used = False
    self.x_monomino_used = False

    
  # TODO: will be based on the game state
  # will initially not support backtracking 
  def get_next_move(self):
    move = {}
    # will have coord, piece, score ... rel_coord, hole_id, type, subtype, other_moves
    
    if self.solved == True:
      return
    
    # TODO: Keep track of hole solution score
    if not self.magic_wand_placed:
      move = self.place_magic_wand()
      if move:
        self.magic_wand_placed = True
        return move 
      
    # if not self.small_wand_placed:
    #   move =
    # else:
    #   pass
    
    while not move or move == 'retry':
        move = self.get_move()
        if not self.available_pieces:
          self.solved = True
        
    return move
    
  # You mostly can't have a pure 'solve_hole' functionality
  # because this game is better solved by considering global contexts
  # You can only ever have a 'get_next_move' base on current circumstances 
  def get_move(self):
    # hole offset
    off_y, off_x = self.current_offset
    
    # TODO: Hole piece solve score
    # track the cheat (small) peices used
    hole_solution_score = 0
    
    # TODO: For testing on more cases, remove once done
    print('=======hole, progressions now', self.current_hole_index, self.progressions, self.current_progression)

    next_expected_count = self.current_progression.pop(0)
    # TODO: keep refreshing progressions when only a few pieces left
    
    hole_grid = self.current_hole_grid
    new_hole_grid = None
    
    sol = self.get_best_hole_move(
      hole_grid, 
      self.available_pieces, 
      next_expected_count
    )
    
    if sol:
      piece, orient, coord_pair, scores, new_hole_grid, other_possible_pieces = sol
    
      self.available_pieces.remove(piece)
      self.used_pieces.append(piece)
    
      # hole_rel_window_pos
      p_y, p_x = coord_pair
      pos = [off_y + p_y, off_x + p_x]
      
      move = [
          pos, 
          piece, 
          orient, 
          self.current_hole_index, 
          
          scores, 
          hole_grid, 
          new_hole_grid, 
          other_possible_pieces
      ]
      self.moves.append(move)
      
    # TODO: more cases
    elif next_expected_count == 3:
      self.current_progression = [2, 1] + self.current_progression
      return 'retry'
    else:
      move = None
    
    now_hole_grid = new_hole_grid or hole_grid
    
    # TODO: [bug] Temp Red Monomino move has trouble, place small_wand in first big hole and check
    remaining_count = get_cell_count(new_hole_grid)
    print('remaining_count', remaining_count)
    if not remaining_count:
        if self.holes:
          self.current_hole = self.holes.pop(0)
          self.current_hole_index += 1
          self.current_offset = self.current_hole['offset']
          self.current_hole_grid = copy.copy(self.current_hole['grid'])
          
          if self.holes:
            self.current_progression = self.progressions.pop(0)
          else:
            # for last hole, the progression is the sizes of the pieces left
            self.current_progression = []
            for piece in self.available_pieces:
              piece_info = puzzle.get_piece_info(piece)
              self.current_progression.append(piece_info['size'])
            self.current_progression = sorted(self.current_progression, reverse=True)
            print('======self.current_progression', self.current_progression)
        else:
          print('SOLVED!!!')
    
    # TODO: [bug] in the scoring system! Switch this off and see
    # NEED to round up all highest scorers and see how their scores were calculated and why they lost
    else:
      self.current_hole_grid = new_hole_grid
          
    # Next up, 3 = 2+1 flow/bug
    # better move template
    # then, include the small_wand in the scoring system too
    # make small_wand lose
    # include the big hole in the solving
    # ... then, to be continued
    
    return move
      
  def place_magic_wand(self):
    magic_wand_hole_data = []
    
    for idx, hole in enumerate(self.all_holes):
      # if size big, select for magic wand
      if hole['max_span'] == 8:
         # TODO: Multiple holes might have magic wand positions
         magic_wand_hole_data.append({
           'hole': hole,
           # 'grid': hole['grid'],
           'idx': idx
         })

    # valid_position_windows = {}
    
    max_edge_score = 0
    selected_pos = None
    for data in magic_wand_hole_data:
      grid = data['hole']['grid']
      for row in grid:
        if None not in row:
          pos_cell = row[0]
          # s = str(pos_cell['coord'][0]) + str(pos_cell['coord'][1]) + 'h'
          pos = [pos_cell['coord_pair'], 'h', pos_cell['color'], data]
        
          edge_score = sum([cell['edges'].count('1') for cell in row])
          if edge_score > max_edge_score and edge_score < MAX_MAGIC_WAND_INIT_EDGES:
            max_edge_score = edge_score
            selected_pos = pos
          
          # valid_position_windows[s] = pos
     
      for idx in range(len(grid[0])):
        col = [row[idx] for row in grid]
        if None not in col:
          pos_cell = col[0]
          # s = str(pos_cell['coord'][0]) + str(pos_cell['coord'][1]) + 'v'
          pos = [pos_cell['coord_pair'], 'v', pos_cell['color'], data]

          edge_score = sum([cell['edges'].count('1') for cell in col])
          if edge_score > max_edge_score and edge_score < MAX_MAGIC_WAND_INIT_EDGES:
            max_edge_score = edge_score
            selected_pos = pos
          
          # valid_position_windows[s] = pos
    
       
    # select the best position (non-hole-breaking/most edges count for position, leaving hole least crooked)
    position = selected_pos[0]
    magic_wand_hole = selected_pos[3]['hole']
    grid = magic_wand_hole['grid']
    
    max_edge_score = 0

    # select orientation needed by the selected position
    orient_map = {
      'hr': 0,
      'vr': 1,
      'hx': 2,
      'vx': 3
    }
    orient = orient_map[selected_pos[1] + selected_pos[2]]
    
    # place the magic wand and get new hole
    changed_hole = fill_piece(grid, 'magic_wand', orient, position, None)
    self.available_pieces.remove('magic_wand')
    
    magic_wand_hole['grid'] = changed_hole
    
    return [
        position, 
        'magic_wand', 
        orient, 
        selected_pos[3]['idx'],
        
        {
             'match': max_edge_score,
             # 'm_w': m_w,
             # 'm_p': m_p,
             'deviation': 0,
             # 'span': span,
             'total': max_edge_score
        }, 
        grid, 
        changed_hole, 
        [ ]
    ]
    
    
  def get_best_hole_move(self, hole, available_pieces, next_expected_count=4):
    # Keep updating hole state and call this window again
    window_index = {}
    all_possible_pieces = []
    
    windows = get_valid_windows(hole, next_expected_count) 
    # Take note of the size of window and available pieces to get the possible window cell count combinations
    
    for win in windows:
      coord, dim, no_of_cells = win
      y, x = int(coord[0]), int(coord[1])
      h, w = dim
      
      window_id = coord + str(dim[0]) + str(dim[1])
      
      window, cell_coord_list = get_window_and_cell_coord_list(hole, y, x, h, w) 
      possible_pieces = get_possible_pieces_having_count_with_scores(available_pieces, window, cell_coord_list, no_of_cells, next_expected_count, window_id, [y, x])
      
      if 'square' in available_pieces and next_expected_count == 4:
        cell_only_coord_list = [cell[:2] for cell in cell_coord_list]
        print(cell_only_coord_list)
        if set(['01', '02', '11', '12']).issubset(set(cell_only_coord_list)):
          print('yes is part 1')
          cell = window[0][1]
          # TODO: another rel_coord
          coord = cell['rel_coord_pair'] if 'rel_coord_pair' in cell else cell['coord_pair']
          piece = 'square'
          orient = 0 if cell['color'] == 'r' else 1
        
          piece_orient = puzzle.get_piece(piece, orient)
          new_window = [window[0][1:], window[1][1:]]
          
          for row in new_window:
            for cell in row:
              cell['rel_coord_pair'][1] -= 1
              cy, cx = cell['rel_coord_pair'] 
              cell['rel_coord'] = str(cy) + str(cx)
          
          match_c, win_c, piece_c, open_edges = get_piece_to_window_edge_scores(piece_orient['grid'], new_window)
          piece_data = {
             'piece': piece,
             'orient': orient,
             'coord_pair': [y, x + 1],
             'scores': {
                 'match_c': match_c,
                 'win_c': win_c,
                 'piece_c': piece_c,
                 'deviation': 0.4,
                 'span': 0,
                 'total': get_edge_matches_total_score(match_c, win_c, piece_c) + 0.4
             },
          }
      
          possible_pieces += [piece_data]
        
        if set(['10', '11', '20', '21']).issubset(set(cell_only_coord_list)):
          print('yes is part 2')
          cell = window[1][0]
          # TODO: another rel_coord
          coord = cell['rel_coord_pair'] if 'rel_coord_pair' in cell else cell['coord_pair']
          piece = 'square'
          orient = 0 if cell['color'] == 'r' else 1
        
          piece_orient = puzzle.get_piece(piece, orient)
          new_window = window[1:]
          for row in new_window:
            for cell in row:
              cell['rel_coord_pair'][0] -= 1
              cy, cx = cell['rel_coord_pair'] 
              cell['rel_coord'] = str(cy) + str(cx)

          match_c, win_c, piece_c, open_edges = get_piece_to_window_edge_scores(piece_orient['grid'], new_window)
          piece_data = {
             'piece': piece,
             'orient': orient,
             'coord_pair': [y + 1, x],
             'scores': {
                 'match_c': match_c,
                 'win_c': win_c,
                 'piece_c': piece_c,
                 'deviation': 0.4,
                 'span': 0,
                 'total': get_edge_matches_total_score(match_c, win_c, piece_c) + 0.4
             },
          }
        
          possible_pieces += [piece_data]
        
      # TODO: also do for monomino: red and black
      
      for piece in possible_pieces:
        print('piece', piece)
      all_possible_pieces += possible_pieces
      
    # TODO: You DO need a window index, for meta-analysis
      
    if 'small_wand' in available_pieces and next_expected_count == 4:
      hori_postions, vert_postions = get_long_windows(hole)
      
      for pos in hori_postions + vert_postions:
          match_c, win_c, piece_c = pos['edge_scores']
          # NOTE: See the show-off of l-right-r and small wand scores, where L has crookedness, wand has span
          #   scores should not be much different, just pick one or make the tree now
          SPAN_BONUS = 0.25
          all_possible_pieces.append({
             'piece': 'small_wand',
             'orient': pos['orient'],
             'coord_pair': pos['coord'],
             'scores': {
                 'match_c': match_c,
                 'win_c': win_c,
                 'piece_c': piece_c,
                 'deviation': 0,
                 'span': SPAN_BONUS,
                 'total': get_edge_matches_total_score(match_c, win_c, piece_c) + SPAN_BONUS
             },
          })
        
    # TODO: More graceful failing, for handling in the caller
    # print(windows)
    if not all_possible_pieces:
      return
      
    selected_pieces = sorted(all_possible_pieces, key=lambda x: x['scores']['win_c'] + x['scores']['match_c'], reverse=True)[:6]
    
    # TODO: IMP, Also check if piece breaks the hole
    # In case of a tie, can check which one makes hole less edge-ful (smoother hole is left in ideal situation)
    
    # consistent_pieces = []
    # for piece in selected_pieces:
    #   changed_hole = fill_piece(
    #       hole,
    #       piece['piece'],
    #       piece['orient'],
    #       piece['coord_pair'],
    #       piece.get('open_edges', None),
    #   )
    #   # TODO: Damn ugly! This coord should have stayed the actual. Replace everywhere quickly
    #   holes = get_holes(changed_hole, True)
    #   if len(holes) <= 1:
    #     consistent_pieces.append(piece)
    
    consistent_pieces = sorted(selected_pieces, key=lambda x: x['scores']['total'], reverse=True)
    highest_scoring_piece = consistent_pieces[0]
    other_possible_pieces = consistent_pieces[1:4]
    
    # TODO: Don't need all of highest_scoring_piece
    # Maybe also cleanup fill_piece implementation
    # TODO: remove coord_pair param, or expand piece param into only what's needed
    
    changed_hole = fill_piece(
        hole, 
        highest_scoring_piece['piece'], 
        highest_scoring_piece['orient'], 
        highest_scoring_piece['coord_pair'],  
        highest_scoring_piece.get('open_edges', None),
    )
      
      
    # Pass on next possible pieces instead of window index. Do we need the index fo r the possible pices?
    # We needed for this piece to fill it, have to store the index some where and keep
    # or simply store the window along with each possible instead of the entire index
    # TODO: we need to be able to remove a piece too while backtracking
    # Easier way is to just saving a defined game state at every move, that enables all the other logic to stay constant. The state will probably consist of all the self stuff
    # For now, just pieces and their scores, because that's all we need to see and track
    # TODO: store away possible others in another dict by move_id
    # that means move can be an ORDERED DICT
    
    # - store possible pieces in separate dict
    # - store moves in a dict
    # - flex table entries and possible pieces with their scores
    
    # TODO: another type of score for wand pieces, distance from border, negative if higher distance
    # TODO: Ideally possible pieces scores should be compared across windows :P
    #   You can favour small wand's other potential position in ANOTHER hole, to show it is closer 
    #   board border in the other hole. Obscure condition (specific to this case) to break the tie. 
    #   (And bias in our favour >=<)
    #   
    #   All the generic work you're putting in now will help us in our next Pattern that we take up to solve.

    hsp = highest_scoring_piece
    
    return hsp['piece'], hsp['orient'], hsp['coord_pair'], hsp['scores'], changed_hole, other_possible_pieces
    


def fill_piece(hole, piece, orient, window_coord_pair, open_edges):
    changed_hole = copy.deepcopy(hole)
    wy, wx = window_coord_pair
    
    orient = puzzle.get_piece(piece, orient)
    cell_coord_list = orient['cell_coord_list']
    grid = orient['grid']
    
    for coord_t in cell_coord_list:
      cy, cx = int(coord_t[0]), int(coord_t[1])
      y, x = wy + cy, wx + cx
      
      filled_cell = changed_hole[y][x]
      changed_hole[y][x] = None
      coord = coord_t[:2]
      
      if open_edges is None and open_edges is not []:
          piece_cell = grid[cy][cx]
          
          coord_open_edges = []
          for idx, edge in enumerate(filled_cell['edges']):
              if piece_cell['edges'][idx] != edge:
                coord_open_edges.append(idx) 
      else:
          coord_open_edges = open_edges.get(coord, [])

      for edge_idx in coord_open_edges:
        dy, dx = DIR_OPS[edge_idx]
        cell_to_change = changed_hole[y + dy][x + dx]
        
        change_edge_idx = DIR_REVS[edge_idx]
        edge_list = list(cell_to_change['edges'])
        edge_list[change_edge_idx] = '1'
        cell_to_change['edges'] = "".join(edge_list)
          
    return changed_hole


   
def get_window_and_cell_coord_list(hole, y, x, h, w):
  window = []
  cell_coord_list = []
  for i in range(y, y + h):
    window_row = []
    for j in range(x, x + w):
      cell = copy.copy(hole[i][j])
      if cell:
        # TODO:coord pair by default here too
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
    
  return window, cell_coord_list 
    
def get_possible_pieces_having_count_with_scores(available_pieces, window, cell_coord_list, no_of_cells, next_expected_count, window_id, coord_pair):
  # TODO: if desired 3 not there, 3 = 2 + 1 
  possible_pieces = []
  for name in available_pieces:
    info = puzzle.get_piece_info(name)
    # # next_expected_count for 4-5-6 size windows is always 4
    # if no_of_cells >= 4 and next_expected_count >= 4:
    #    next_expected_count = 4
    if info['size'] <= no_of_cells and info['size'] == next_expected_count:
      
      orients = puzzle.get_orients(name)
      
      primary_orient = orients[0]
      
      for idx, orient in enumerate(orients):
        piece_cell_list = orient['cell_coord_list']
        
        if set(piece_cell_list).issubset(cell_coord_list):
           piece_grid = orient['grid']
           print('====PIECE, coord', name, coord_pair)
           match_c, win_c, piece_c, open_edges = get_piece_to_window_edge_scores(piece_grid, window)
           
           # BONUS_SCORE = 1
           # TETRA_AVG_SPAN = 3
           # extra_span = info['max_span'] - TETRA_AVG_SPAN
           # extra_span_score = extra_span * BONUS_SCORE if extra_span > 0 else 0

           DEVIATE_INCR = 0.26
           total_deviation_score = 0
           piece_grid = primary_orient['grid']
           if len(piece_grid) > 1:
               total_deviation_score += DEVIATE_INCR
               
               none_row = None
               highly_crooked = False # All are none rows
               for row in piece_grid:
                   if None in row:
                       if not none_row:
                           none_row = row
                       else:
                           highly_crooked = True
               
               if highly_crooked:
                   total_deviation_score += 2 * DEVIATE_INCR
               elif none_row:
                   if none_row[0] is None and none_row[-1] is None:
                       total_deviation_score += 1 * DEVIATE_INCR
           
           piece_data = {
             'piece': name,
             'orient': idx,
             'cell_coord_list': piece_cell_list,
             'scores': {
               'match_c': match_c,
               'win_c': win_c,
               'piece_c': piece_c,
               'deviation': round(total_deviation_score, 2),
               # 'span': extra_span_score,
               'total': get_edge_matches_total_score(match_c, win_c, piece_c) + total_deviation_score
             },
             'window_id': window_id,
             'coord_pair': coord_pair,
             'open_edges': open_edges,
           }
           possible_pieces.append(piece_data)
           
           # store open edges and keep: wherever piece had an edge and window had open edge
           
  return possible_pieces
  


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
   
   
   
