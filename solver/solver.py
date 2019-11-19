# You know the game properties and rules
# you also know how to calc a move (instance/intermediate) state
# now define how the game will proceed initially


# Goal: to play one puzzle that I know to solve, and all its steps, most determinate, only a few non-determinate

# Rule: only store deduced info, not intermediate info
# Trye to save all intermediate data as storage as well


# Global state (The decision tree level, all knowing, global state)

# TODO: Reclaim backtracking space whenever you switch to parent, turn the child to null

# another type of score for wand pieces, distance from border, negative if higher distance
# TODO: Ideally possible pieces scores should be compared across windows :P
#   You can favour small wand's other potential position in ANOTHER hole, to show it is closer 
#   board border in the other hole. Obscure condition (specific to this case) to break the tie. 
#   (And bias in our favour >=<)
#   
#   All the generic work you're putting in now will help us in our next Pattern that we take up to solve.

# TODO: **LATER: [LEARN] Take note of the size of window and available pieces to get the possible window cell count combinations

import copy
from puzzle import (
  get_pieces, 
  get_holes_and_prog_from_grid,
  get_piece_size_progression, 
  get_holes,
  get_valid_windows, 
  get_long_windows,
  get_piece_to_window_edge_scores, 
  get_edge_matches_total_score,
  get_cell_count, 
  get_edge_count,
  DIR_OPS,
  DIR_REVS,
  SMALL_HOLE_SIZE,
  AVG_WIN_SIZE
)

MAX_MAGIC_WAND_INIT_EDGES = 11

def sort_holes(holes):
  # TODO: we'll sort better later
  # TODO: size property is not changed yet when we remove the progression

  # for hole in holes:
  #   hole['size'] = get_cell_count(hole['grid'])
  #   hole['edge_count'] = get_edge_count(hole['grid'])
  # holes.sort(key=lambda x: x['edge_count'], reverse=True)
  # holes.sort(key=lambda x: x['size'])
  
  small_holes = [hole for hole in holes if hole['size'] <= 4]
  big_holes = [hole for hole in holes if hole['size'] > 4]
  holes = sorted(small_holes, key=lambda x: x['size']) + sorted(big_holes, key=lambda x: x['density'])
  return holes


# TODO: First tryouts: Single Playthrough
# TODO: Second tryouts, multiple playthroughs
# i.e hook up all of the best possible choices at every stage to the hook

class Puzzle:
  def __init__(self, r_count=32, x_count=32):
    # pieces = 
    self.r_count = r_count
    self.x_count = x_count
    self.pieces_registry, self.orients_registry = get_pieces(r_count, x_count)
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

class Solver:
  def __init__(self, board, pieces, puzzle):
    # TODO: place progressions inside holes themselves
    self.all_holes = get_holes_and_prog_from_grid(board['grid'])
    
    self.all_holes = sort_holes(self.all_holes)
    
    # LATER: and probably also fill in the unquestionables to avoid questioning them in future 
    self.state = State(
      puzzle,
      copy.deepcopy(self.all_holes), 
      pieces,
      None
    )

  def get_next_move(self):
    if self.state:
      data = self.state.get_new_state()
      print('stateand_move', data)
      if data:
        # TODO: Acknowledge for backtrack step, same proper format as solved ans failed
        if len(data) == 2:
          self.state, move = data
          return move
        else:
          self.state = data[0]
          return 'backtrack'
      else:
        if self.state.failed:
          self.failed = True
          return 'failed'
        if self.state.solved:
          # TODO: return proper format required
          return 'solved'
          
    else:
      # return previous result whatever it was
      pass


# There's multiple Moves for very State
# A State saves a COPY the ENTIRE BOARD data within itself
class State:
  def __init__(self, puzzle, holes, pieces, parent):
    self.puzzle = puzzle
    
    self.holes = holes
    self.pieces = pieces
    self.curr_hole_idx = 0
    
    self.solved = False # will be when you have used up your pieces
    self.failed = False # will be when your moves are over and you have no parent
    
    self.parent = parent
    
    # check the hole stats and select a hole
    # LATER: select multiple holes and do moves
    
    # just get, don't play
    self.possible_moves = self.get_moves()
    self.current_move_idx = -1
    
  def get_new_state(self):
    # check if solved
    if not self.pieces:
      self.solved = True
      return None
      
    # check if failed
    if self.possible_moves_over():
      if self.parent:
        # TODO: reclaim space
        
        print('==== parent')
        return [self.parent]
      else:
        self.failed = True
        return None
    
    self.current_move_idx += 1
    move = self.possible_moves[self.current_move_idx]
    now_filled_hole_grid = move.get_filled_hole_grid() # you will always have this, 
                                                       # that how you decided the moves in the first place
    move.old_grid = self.holes[move.hole_id]['grid']
    move.new_grid = now_filled_hole_grid
    
    pieces = copy.deepcopy(self.pieces)
    pieces.remove(move.piece)
    
    all_holes = copy.deepcopy(self.holes)
    
    if not get_cell_count(now_filled_hole_grid):
      all_holes.pop(move.hole_id)
      # TODO: change progression if only one hole left
      if len(all_holes) == 1:
        all_holes[0]['progression'] = get_pieces_progression(pieces, self.puzzle)
    else:
      curr_hole = all_holes[move.hole_id]
      curr_hole['grid'] = now_filled_hole_grid
      # TODO: LATER recalc this as well
      curr_hole['progression'].pop(0)
    
    print('=====Start new_state: pieces', pieces, )
    return [State( self.puzzle, all_holes, pieces, self ), move]
    
  def get_moves(self):
    # Make move objects. Account for all the special pieces that you have
    # TODO: LATER: after first board is done, account for all holes
    
    if not self.pieces:
      self.solved = True
      return []
    
    if 'magic_wand' in self.pieces:
      return self.get_magic_wand_moves()
      
    sort_holes(self.holes)
    hole_id = 0
    hole = self.holes[hole_id]
    grid = hole['grid']
    # next_count = min(hole['progression'][0], get_cell_count(grid))
    print('======next_counts', hole['progression'])
    next_count = hole['progression'][0]
    moves = get_possible_moves(grid, hole_id, self.pieces, self.puzzle, next_count)
    
    if not moves and next_count == 3:
      hole['progression'].pop(0)
      hole['progression'] = [2, 1] + hole['progression']
      next_count = hole['progression'][0]
      moves = get_possible_moves(hole['grid'], hole_id, self.pieces, self.puzzle, next_count)
     
    # TODO: 
    # if not moves and len(self.holes) > 1:
    #   hole_id += 1
    #   hole = self.holes[hole_id]
    #   grid = hole['grid']
    #   # next_count = min(hole['progression'][0], get_cell_count(grid))
    #   print('====++==next_counts', hole['progression'])
    #   next_count = hole['progression'][0]
    #   moves = get_possible_moves(grid, hole_id, self.pieces, self.puzzle, next_count)
    #
    #   if not moves and next_count == 3:
    #     hole['progression'].pop(0)
    #     hole['progression'] = [2, 1] + hole['progression']
    #     next_count = hole['progression'][0]
    #     moves = get_possible_moves(hole['grid'], hole_id, self.pieces, self.puzzle, next_count)
      
      
    # TODO: Way to try multiple progression chains
    
    for move in moves:
      move.state = self
    
    return moves
    

    
  def possible_moves_over(self):
    return self.current_move_idx == len(self.possible_moves) - 1
    
  def get_magic_wand_moves(self):
    magic_wand_hole_data = []
    
    for idx, hole in enumerate(self.holes):
      if hole['max_span'] == 8:
         magic_wand_hole_data.append({ 'grid': hole['grid'], 'idx': idx })
         
    return get_magic_wand_moves_for_holes(magic_wand_hole_data, self)


  # def select_next_hole(self):
  #   # TODO:
  #   return self.holes[0], 0
    
  # def get_magic_wand_hole(self):
  #   # get_move_for_hole_and_pieces
  #   # TODO: place magic wand and contruct the first move with only magic wand possible positions
  #   magic_wand_hole = self.get_magic_wand_hole()
  #   return self.holes[0]

  # def get_best_hole_move(self, hole, available_pieces, next_expected_count=4):
  #   # Keep updating hole state and call this window again
  #   window_index = {}
  #
  
class Move:
  def __init__(self, hole_id, coord, piece, orient, scores, state, open_edges=None):
    self.hole_id = hole_id
    self.coord = coord
    self.piece = piece
    self.orient = orient
    
    self.scores = scores
    
    self.state = state
    
    self.old_grid = None
    self.new_grid = None
    
    self.open_edges = open_edges
    
  def get_filled_hole_grid(self):
    print(self.hole_id, self.piece,
      self.orient,
      self.coord)
    now_filled_hole = fill_piece(
      self.get_hole_grid(),
      self.piece,
      self.orient,
      self.coord,
      None,
      self.state.puzzle
    )
    
    return now_filled_hole
    
  # def get_piece(self):
  #   return puzzle.get_piece(self.piece, self.orient)
    
  def get_hole_grid(self):
    return self.state.holes[self.hole_id]['grid']



def get_possible_moves(hole_grid, hole_id, available_pieces, puzzle, next_expected_count=4):
  all_possible_moves = []
  
  windows = get_valid_windows(hole_grid, next_expected_count) 
  
  for win in windows:
    coord, dim, no_of_cells = win
    y, x = int(coord[0]), int(coord[1])
    h, w = dim
    window_id = coord + str(dim[0]) + str(dim[1])
    
    window, cell_coord_list = get_window_and_cell_coord_list(hole_grid, y, x, h, w) 
    
    if no_of_cells == 1:
      term = cell_coord_list[0]
      color = term[-1]
      cy, cx = int(term[0]), int(term[1])
      scores = {
        'match_c': 4,
        'win_c': 4,
        'piece_c': 4,
        'deviation': 0,
        'span': 0,
        'total': get_edge_matches_total_score(4, 4, 4)
      }
      
      name = None
      if color == 'r':
        if 'mono_r' in available_pieces and not puzzle.get_piece_info('mono_r')['flipped']:
          name = 'mono_r'
      else:
        if 'mono_x' in available_pieces:
          name = 'mono_x'
        else:
          if 'mono_r' in available_pieces and puzzle.get_piece_info('mono_r')['flipped']:
            name = 'mono_r'
      
      if name:
        orient = 0
        move = Move(hole_id, [y + cy, x + cx], name, orient, scores, None)
        all_possible_moves.append(move)
      continue
      
    # elif no_of_cells == 2:
    #   move = Move(hole_id, [y + cy, x + cx], name, orient, scores, None)
    #   all_possible_moves.append(move)
    #   continue
    
    
    possible_moves = get_possible_moves_having_count_with_scores(available_pieces, puzzle, window, cell_coord_list, no_of_cells, next_expected_count, hole_id, [y, x])
    
    if 'square' in available_pieces and next_expected_count == 4:
      cell_only_coord_list = [cell[:2] for cell in cell_coord_list]
      piece = 'square'
      
      if set(['01', '02', '11', '12']).issubset(set(cell_only_coord_list)):
        cell = window[0][1]
        
        # TODO: another rel_coord
        coord = cell['rel_coord_pair'] if 'rel_coord_pair' in cell else cell['coord_pair']
        
        orient = 0 if cell['color'] == 'r' else 1
      
        piece_orient = puzzle.get_piece(piece, orient)
        new_window = [window[0][1:], window[1][1:]]
        
        for row in new_window:
          for cell in row:
            cell['rel_coord_pair'][1] -= 1
            cy, cx = cell['rel_coord_pair'] 
            cell['rel_coord'] = str(cy) + str(cx)
        
        match_c, win_c, piece_c, open_edges = get_piece_to_window_edge_scores(piece_orient['grid'], new_window)
        scores = {
             'match_c': match_c,
             'win_c': win_c,
             'piece_c': piece_c,
             'deviation': 0.4,
             'span': 0,
             'total': get_edge_matches_total_score(match_c, win_c, piece_c) + 0.4
         }
        
        move = Move(hole_id, [y, x + 1], piece, orient, scores, None)
        possible_moves += [move]
      
      if set(['10', '11', '20', '21']).issubset(set(cell_only_coord_list)):
        cell = window[1][0]
        # TODO: another rel_coord
        coord = cell['rel_coord_pair'] if 'rel_coord_pair' in cell else cell['coord_pair']
        orient = 0 if cell['color'] == 'r' else 1
      
        piece_orient = puzzle.get_piece(piece, orient)
        new_window = window[1:]
        for row in new_window:
          for cell in row:
            cell['rel_coord_pair'][0] -= 1
            cy, cx = cell['rel_coord_pair'] 
            cell['rel_coord'] = str(cy) + str(cx)

        match_c, win_c, piece_c, open_edges = get_piece_to_window_edge_scores(piece_orient['grid'], new_window)
        scores = {
             'match_c': match_c,
             'win_c': win_c,
             'piece_c': piece_c,
             'deviation': 0.4,
             'span': 0,
             'total': get_edge_matches_total_score(match_c, win_c, piece_c) + 0.4
         }
        
        move = Move(hole_id, [y + 1, x], piece, orient, scores, None)
        possible_moves += [move]
      
    # TODO: also do for monomino: red and black
    
    # if 'square' in available_pieces and next_expected_count == 4:
    
      
    all_possible_moves += possible_moves
    
  # TODO: You DO need a window index, for meta-analysis
    
  if 'small_wand' in available_pieces and next_expected_count == 4:
    all_possible_moves += get_small_wand_moves(hole_grid, hole_id) 
  
  print('=====all_possible_moves', len(all_possible_moves), [move.piece for move in all_possible_moves], next_expected_count)
    
  selected_moves = sorted(all_possible_moves, key=lambda x: x.scores['win_c'] + x.scores['match_c'], reverse=True)[:6]
  moves = sorted(selected_moves, key=lambda x: x.scores['total'], reverse=True)
  
  return moves[:3]
  

  
# TODO: IMP, Also check if piece breaks the hole_grid
# In case of a tie, can check which one makes hole_grid less edge-ful (smoother hole_grid is left in ideal situation)

# consistent_moves = []
# for piece in selected_moves:
#   changed_hole_grid = fill_piece(
#       hole_grid,
#       piece['piece'],
#       piece['orient'],
#       piece['coord_pair'],
#       piece.get('open_edges', None),
#   )
#   # TODO: Damn ugly! This coord should have stayed the actual. Replace everywhere quickly
#   hole_grids = get_hole_grids(changed_hole_grid, True)
#   if len(hole_grids) <= 1:
#     consistent_moves.append(piece)

def get_small_wand_moves(hole_grid, hole_id):
  small_wand_moves = []
  SPAN_BONUS = 0.25
  hori_postions, vert_postions = get_long_windows(hole_grid)
  
  for pos in hori_postions + vert_postions:
      match_c, win_c, piece_c = pos['edge_scores']
      scores = {
         'match_c': match_c,
         'win_c': win_c,
         'piece_c': piece_c,
         'deviation': 0,
         'span': SPAN_BONUS,
         'total': get_edge_matches_total_score(match_c, win_c, piece_c) + SPAN_BONUS
      }
      
      move = Move(hole_id, pos['coord'], 'small_wand', pos['orient'], scores, None)
      small_wand_moves.append(move)
            
  return small_wand_moves

def get_magic_wand_moves_for_holes(magic_wand_hole_data, state):  
  valid_moves = []
  
  orient_map = {
    'hr': 0,
    'vr': 1,
    'hx': 2,
    'vx': 3
  }
  
  def get_scores(max_edge_score):
    return {
         'match': max_edge_score,
         # 'm_w': m_w,
         # 'm_p': m_p,
         'deviation': 0,
         # 'span': span,
         'total': max_edge_score
    }
    
  def append_move(hole_id, cell_col, direction):
    cell = cell_col[0]
    orient = orient_map[direction + cell['color']]
    max_edge_score = sum([c['edges'].count('1') for c in cell_col])
    
    # TODO: Another rel_coord
    coord = cell['rel_coord_pair'] if 'rel_coord_pair' in cell else cell['coord_pair']
    move = Move(hole_id, coord, 'magic_wand', orient, get_scores(max_edge_score), state)
    valid_moves.append(move)
  
  for data in magic_wand_hole_data:
    grid = data['grid']
    for row in grid:
      if None not in row:
        append_move(data['idx'], row, 'h')

    for idx in range(len(grid[0])):
      col = [row[idx] for row in grid]
      if None not in col:
        append_move(data['idx'], col, 'v')
        
  return sorted(valid_moves, key=lambda x: x.scores['total'], reverse=True)
      
    

def fill_piece(hole, piece, orient_id, window_coord_pair, open_edges, puzzle):
    changed_hole = copy.deepcopy(hole)
    wy, wx = window_coord_pair
    
    orient = puzzle.get_piece(piece, orient_id)
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
    
def get_possible_moves_having_count_with_scores(available_pieces, puzzle, window, cell_coord_list, no_of_cells, next_expected_count, hole_id, coord_pair):
  possible_moves = []
  for name in available_pieces:
    info = puzzle.get_piece_info(name)

    if info['size'] <= no_of_cells and info['size'] == next_expected_count:
      
      orients = puzzle.get_orients(name)
      
      primary_orient = orients[0]
      
      for idx, orient in enumerate(orients):
        piece_cell_list = orient['cell_coord_list']
        
        if set(piece_cell_list).issubset(cell_coord_list):
           piece_grid = orient['grid']
           match_c, win_c, piece_c, open_edges = get_piece_to_window_edge_scores(piece_grid, window)

           total_deviation_score = get_total_deviation_score(primary_orient['grid'])
           scores = {
             'match_c': match_c,
             'win_c': win_c,
             'piece_c': piece_c,
             'deviation': round(total_deviation_score, 2),
             # 'span': extra_span_score,
             'total': get_edge_matches_total_score(match_c, win_c, piece_c) + total_deviation_score
           }
           
           move = Move(hole_id, coord_pair, name, idx, scores, None, open_edges)
           possible_moves.append(move)
           
  return possible_moves
  
def get_pieces_progression(pieces, puzzle):
  progression = []
  for piece in pieces:
    piece_info = puzzle.get_piece_info(piece)
    progression.append(piece_info['size'])
  return progression

def get_total_deviation_score(piece_grid):
  DEVIATE_INCR = 0.26
  total_deviation_score = 0
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
              
  return total_deviation_score
