from data import PIECES
import copy

# Also the utils to calc state given an input board/state

# Always err on the side of 'the way we'd do it' 

# we are doing the tree pruning as much as we can



# the moves grid: 
# the first playthrough, before any backtracking
# gonna need some solid data structures for this
# cols: 
# 1. the empty board with moves (current move highlighted)
# 2. each of the holes as header, with their current state (pattern, stats, windows) and the piece selected following
#   a. 




# Magic Wand placement has its own special rules. First all possibilities, 
# then choose the one that leaves the hole less edge dense.
# aka
# 1. Check if end points exists, filter
# 2. Check if color of end points matches
# 3. Check if middle points exist too, filter
# viable options received at this stage
# 4. No holes formed? Prefer these
# 5. The adjecent cells have lesser existing edges? Prefer these 

# then your normal piece placement. I think we've done this before, roughly.



#########################################################################
# # Pieces props:
# # data
# name, just coz
# grid str: coord-color chain
# # Computables now
# grid: cell: coord val, color val, edges val
# no of cells / size (Main categorization, bigger ones are tried/placed first)
# type: red or blue
# no of colored cells (no of Black can be inferred)
# (for blue side) no of blue cells (no of Yellow can be inferred)

# crookedness index/no of corners/perimeter-to-area: line - L - T - Z (hence rarity)
#    also will be compared during hole part matching to get a rough idea
# **color feature uniqueness (hence rarity)
# 

# all 4 Orientations
# ***INDEX 'extensions' of a piece, similar edges to pieces that are easier to lookup
#########################################################################



# pieces should be queriable, and only the name of pieces stored for any list
# every single piece by name and orientation
# So a separate list holds the orientation, special name, grid and coord list for every pices
# The master list holds actual piece orient-independent info
# This is the one removed from available in the case of deleting a piece

# uldr
DIR_OPS = [[-1,0], [0, -1], [1, 0], [0, 1]]
DIR_REVS = [2, 3, 0, 1]


def get_pieces():
  pieces_reg = {}
  orients_reg = {}
  for p in PIECES:
    piece = get_pattern_and_stats(p['val'])
    name = p['name']
    piece['name'] = name
    pos = p['positions'] if 'positions' in p.keys() else 4
    piece['positions'] = pos
  
    orients = [{
      'grid': piece['grid'],
      'cell_coord_list': piece['cell_coord_list']
    }]
    
    if pos != 1:
      if pos == 2:
        orients.append(get_rotated(piece, 90))
      elif pos == 4:
        r180 = get_rotated(piece, 180)
        orients = orients + [
          get_rotated(piece, 90),
          r180,
          get_rotated(r180, 90)
        ]
    
    pieces_reg[name] = piece
    orients_reg[name] = orients
  return pieces_reg, orients_reg
  
  
def fill_piece(hole, piece, window_coord_pair, open_edges={}, calc_edges=False):
    changed_hole = copy.deepcopy(hole)
    wy, wx = window_coord_pair
    for coord_t in piece['cell_coord_list']:
      cy, cx = int(coord_t[0]), int(coord_t[1])
      y, x = wy + cy, wx + cx
      
      filled_cell = changed_hole[y][x]
      changed_hole[y][x] = None
      coord = coord_t[:2]
      
      if calc_edges:
          piece_cell = piece['grid'][cy][cx]
          
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


def get_piece_size_progression(cell_count):
  # Level 1: No. of blocks to get big picture of which available pieces add up to it
  #   break down into number of pieces, first all 4s, the 3s/2s+1s
  #   if multiple of 4, the first choice 4s
  #   if not, 3s chance higher: 3 + 3 more likely than 4 + 2
  
  piece_size_progression = []
  
  if cell_count % 4 == 0:
    piece_size_progression = [4] * (cell_count/4)
  elif cell_count % 2 == 0:
    if cell_count > 2:
      # has a 6 in there, first choice 3 + 3, rather than 4 + 2
      mult_4 = cell_count - 6
      piece_size_progression = [4] * (mult_4/4) + [3, 3]
    else:
      # 2, then 1 + 1
      piece_size_progression = [2]
      
  else:
    # odd
    remainder = cell_count % 4
    piece_size_progression = [4] * int(cell_count/4) + [remainder]
    
  return piece_size_progression
    
    

def get_piece_to_window_edge_scores(piece, window):
  shape_edges_count = 0
  matched_edges_count = 0
  window_edges_count = 0 
  
  # unmatched piece edges
  piece_open_edges = {}
           
  for row in window:
      for block in row:
          if block:
              window_edges_count += len(block['edges'])
              # if len(piece[0]) >= block['coord'][1] + 1:
              # TODO: needs custom rules for how a square 
              # (or a smaller piece than window) 
              # should be placed
              y, x = block['rel_coord_pair']
              piece_cell = piece[y][x] if y < len(piece) and x < len(piece[0]) else None
              if piece_cell:
                  open_edges = []
                  for idx, edge in enumerate(piece_cell['edges']):
                      if edge == '1':
                          shape_edges_count += 1
                          if block['edges'][idx] == '1':
                              matched_edges_count += 1
                          else:
                              open_edges.append(idx)
                      if block['edges'][idx] == '1':
                          window_edges_count += 1
                  if open_edges:
                      piece_open_edges[block['rel_coord']] = open_edges
                       
            
  w_match = matched_edges_count/window_edges_count 
  s_match = matched_edges_count/shape_edges_count
  w_x_s = w_match * s_match 
  
  # return {
  #     # 'SE': shape_edges_count,
  #     # 'WE': window_edges_count,
  #     # 'ME': matched_edges_count,
  #     #
  #     # 'W_MATCH': w_match,
  #     # 'S_MATCH': s_match,
  #     'W_X_S': w_x_s,
  # }

  # NOTE: Plenty of instances where readability is compromised for perf 
  scores = [matched_edges_count, w_match, s_match, w_x_s]
  return scores, piece_open_edges
  
# ***
def get_pattern_and_stats(s):
  # everything computable
  
  # get colors in a grid
  # get edges
  # Null blocks are IMPORTANT
  
  cells = {}
  # TODO: blue/yellow version alert
  colored_cells_cnt = 0
  # blue_cells_cnt = 0
  cell_type = 'r'
  
  edges_done = False
  cell_coord_list = []
  
  if type(s) is str:
    cell_str_len = 3
    s = [s[i: i+cell_str_len] for i in range(0, len(s), cell_str_len)]
  else: 
    edges_done = True
    
  for cell in s:
    coord = cell[:2]
    y, x = coord[0], coord[1]
    color = cell[2]
    
    cells[coord] = {
      'coord_pair': [int(y), int(x)],
      'coord': coord,
      'color': color,
      'edges': None if not edges_done else cell[3:]
    }
    
    if color == 'r':
      colored_cells_cnt += 1

  y_coords = [cell['coord_pair'][0] for cell in cells.values()]
  x_coords = [cell['coord_pair'][1] for cell in cells.values()]
  min_y = min(y_coords)
  max_y = max(y_coords)
  min_x = min(x_coords)
  max_x = max(x_coords)
  
  grid_h = max_y - min_y + 1
  grid_w = max_x - min_x + 1
  
  grid = []
  
  for i in range(grid_h):
    row = []
    for j in range(grid_w):
      coord = str(i + min_y) + str(j + min_x)
      cell = None
      if coord in cells:
        cell = cells[coord]
        coord_to_enlist = coord
        if min_y or min_x:
          rel_coord_pair = [
            cell['coord_pair'][0] - min_y,
            cell['coord_pair'][1] - min_x
          ]
          
          cell['rel_coord_pair'] = rel_coord_pair
          rel_coord = str(rel_coord_pair[0]) + str(rel_coord_pair[1])
          cell['rel_coord'] = rel_coord
          coord_to_enlist = rel_coord
          
        cell_coord_list.append(coord_to_enlist + cell['color'])
      
      row.append(cell)
    grid.append(row)
  
  if not edges_done:
    grid = add_edges_to_grid_data(grid)
  
  # TODO:
  # perimeter = 
  
  # deviation_index = 
  
  # orientations =
  
  return {
    'grid': grid,
    'cell_coord_list': cell_coord_list,
    
    'size': len(cells),
    'dim': [grid_h, grid_w],
    'type': cell_type,
    'colored_cells_cnt': colored_cells_cnt,
    'offset': [min_y, min_x],
    # 'perimeter': perimeter,
    # 'deviation_index': deviation_index,
    # 'orientations': orientations
  }
  
# def get_grid(cells):
#   pass
  
  
def add_edges_to_grid_data(grid):
  edge_grid = get_edge_grid(grid) 
  
  for i, row in enumerate(grid):
    for j, cell in enumerate(row):
      if cell:
        cell['edges'] = edge_grid[i][j]
      
      
  return grid
  
  
def get_cell_count(this_hole):
  size = 0
  for row in this_hole:
    for cell in row:
      if cell:
        size += 1
  return size



#########################################################################
# # Board props/stats:
# Red/blueyellow/red and blueyellow
# No of colored
# **No of holes
# ==>Checkered Index ~= size of biggest hole (generally 16 to 64) Higher count, more difficult with current mothod (if different color, then slightly easier)
# 
# ****Feature density (a feature can itself be checkered too, the different color talked about above)
#########################################################################

SAMPLE_BOARD_41 = '00x01y02x03b04x05r06x07r10b11x ....'

def get_board(board_val):
  # with all the edges, counts, holes, hole sizes, hole start zones, checkered index
  board = board_val
  return board


CELL_SIZE = 16
CELLS_SIDE = 8
GRID_AREA = 64

def get_board_from_img(img, thresh):
  # with all the edges, counts, holes, hole sizes, hole start zones, checkered index
  
  start_point = CELL_SIZE / 2
  indices_1d = [int(start_point + CELL_SIZE * x) for x in range(0, CELLS_SIDE)]
  
  grid = []
  red_count = 0
  black_count = 0
  
  # TODO: better sampling of color
  for idx, i_1d in enumerate(indices_1d):
    row = []
    for jdx, j_1d in enumerate(indices_1d):
      val = img[i_1d][j_1d]
      if val > thresh:
        val = 'r'
        red_count += 1
      else:
        val = 'x'
        black_count += 1
      row.append({
        'coord': str(idx) + str(jdx),
        'color': val
      })
    grid.append(row)

  grid = add_edges_to_grid_data(grid)

  
     
#      for row in obj['grid']:
#        arr = [('x' if cell else '0') for cell in row]
#        print("".join(arr))
#      print(" ", len(obj['grid']), obj['cells'])
     
  
  return {
    'grid': grid,
    'red_count': red_count,
    'black_count': black_count,
    'total_count': GRID_AREA,
  }
  

def get_holes_and_stats(grid):
  holes = get_holes(grid)
  
  for key, hole in holes.items():
     obj = get_pattern_and_stats(hole['cells'])
     
     obj['cells'] = hole['cells']
     holes[key] = obj
     
  return holes



#########################################################################
# # HOLE LEVEL
# The state 'filling a piece' leaves a hole in is also a thing to score
# Basically, not just window wise (blind to everything else), you need to
# be able to look at the Bigger Picture.
# Level 1: No. of blocks to get big picture of which available pieces add up to it
#   break down into number of pieces, first all 4s, the 3s/2s+1s
#   if multiple of 4, the first choice 4s
#   if not, 3s chance higher: 3 + 3 more likely than 4 + 2
# Level 2: 
#   Approach 1, if hole is too lean
#   try finding 'Disparate' windows that satisfy your choice
#   then match each window separately
#   Approach 2, if the hole has dense areas
#   try finding those areas and smoothening them out till hole is less dense
#   select those areas for first filling, and check density at every step
#   Approach 3, if hole is squat (not dense)      
#   go for the edges  



# # ===>* HOLE-TO-WINDOW LEVEL
# Windows stock obtained by simple method of sliding, 
# given window size and min number of cells (else shifted)

# another window shortlisting: by edge density/perimeter-to-area score

# Now that we have window shortlist, 
# levels of window parsing/piece shortlisting/selection:
  # 1. shapes by no of cells
  # 2. shapes by coord AND color of cells (both orientations)
  # 3. shape with higher edge score and/or rarity
# selected only for time being
# Whole hole parsed this way, 
# winner selected for this move: highest scoring window who does not leave 
# anomalies, like hole in inconsistent state on numeric cell/color count,
# or hole BROKEN (not allowed, only decresing a hole is allowed. Exception: Magic Wand)
# Update Hole state with count and stuff
# NOT whole hole parsed, only 'affected' region, and compared with the previous windows
# highest scoring wins and so on

# Along with the HOLE state,
# THE WINDOW INDEX for the HOLE has to be maintained, affected windows recalculated or removed.
#########################################################################


#########################################################################
# # Hole stats
# size (area)
# crookedness = perimeter/area ratio
# divisions hardly/roughly into 'attemptable' windows by edge density
#########################################################################




# EDGE-AND-CELL-MATCHING.
#########################################################################
# # Hole wrt Pieces (The decision tree, given usually large available pieces set)
# don't go scanning the whole hole, just do the vicinity first
# 
#########################################################################



#****, optimz
def best_windows(hole):
  # highest density (most perimeter/area) areas, chosen as per available pieces sizes ranges
  # Level 1: just borders (limits)
  return windows

#***, optimz
def best_fit_pieces(window):
  # Okay for now you can just simply scan, anyway you need possible worst cases to compare with your results
  # TODO: do it with even more obviousness
  # It should be relatively easy to select a good enough/best piece given a window,
  #    without having to physically check every piece with every orientation to fit in
  
  pieces = []
  return pieces # with repective scores




# CELL-MATCHING
# THIS IS A LONG CUT. SHORTER CUT IS EDGE-MATCHING.
# Recommended only for status checks, not for finding entire solutions.
#########################################################################
# # Pieces wrt board / hole
# possible positions, no of possible positions
# edge scores for those positions
#########################################################################

def get_pieces_positions_for_hole(hole, available_pieces):
  # possible positions, no of possible positions
  positions_by_pieces = {}
  return positions_by_pieces
  
# ***
def get_piece_positions_for_hole(hole, piece):
  positions = []
  return positions


#########################################################################
# # Hole wrt Pieces (just reverse mapping of above data)
# possible pieces, with no of possible positions
# *** possible solutions (Quite intensive using cellmatching alone
#     but useful for highly checkered cases, especially those with features)
#########################################################################

def get_possible_pieces_for_hole(hole):
  return





#########################################################################
# # Game state / Board props after every play (All of this can belong in a local state)
# No of holes, with sizes, hole divided hardly/roughly into 'attemptable' windows by edge density
# used pieces, remaining pieces
# remaining pieces possible positions, no of possible positions (if even one does not have a possible position, abandon move, backtrack and retry)
# ==> *** how we're doing heuristic, based on used/remaining pieces sizes and crookedness indices
#########################################################################




#########################################################################
# # GRID UTILS
#########################################################################

# **
# TODO: Can be made a bit cleaner, and performant
# TODO: This can be more efficiently done with the 'no. of islands' approach,
# right during creating the grid.
def get_holes(grid):
  untrav = []
  seen = []
  
  holes = {
    # '1': {
    #   'cells': [],
    #   'grid': [],
    #   later 'window_index': {}
    # }
  }
  
  for row in grid:
    for grid_cell in row:
      untrav.append(grid_cell['coord'] + grid_cell['color'] + grid_cell['edges'])
      
  curr_hole = ''
  curr_hole_trav = []
  curr_hole_untrav = []
  
  hole_names = [str(i) + 'hole' for i in range(7)]
  
  while untrav or curr_hole_untrav:
    if not curr_hole_untrav:
      # new hole, pick a random from untrav
      if curr_hole:
        holes[curr_hole] = {
          'cells': curr_hole_trav
        }
      
      # pick a the first from untrav pass it to new hole's untrav
      cell = untrav.pop(0)
      seen.append(cell)
      
      curr_hole = hole_names.pop(0)
      curr_hole_trav = []
      curr_hole_untrav = [cell]
      
    else:
      # same hole, pick from its untrav and travel
      # it's already passed on from untrav so don't bother removing from there
      cell = curr_hole_untrav.pop(0)
      if cell not in seen:
        seen.append(cell)
      if cell not in curr_hole_trav:
        curr_hole_trav.append(cell)
      else:
        continue
      
      y = int(cell[0])
      x = int(cell[1])
      
      edges = cell[2:]
      
      for idx, is_edge in enumerate(edges):
        if is_edge == '0':
          dir_op = DIR_OPS[idx-1]
          new_y = y + dir_op[0]
          new_x = x + dir_op[1]
          
          if new_y >= 0 and new_x >= 0 and new_y < CELLS_SIDE and new_x < CELLS_SIDE:
            # trav it
            grid_cell = grid[new_y][new_x]
            new_cell = grid_cell['coord'] + grid_cell['color'] + grid_cell['edges']
            
            
            
            if new_cell not in curr_hole_trav:
              curr_hole_untrav.append(new_cell)
            # gasp, this one's brand new, not passed from untrav, 
            # gotta remove it from there as well
            # but first check if already traved
            
              if new_cell not in seen:
                seen.append(new_cell)
                untrav.remove(new_cell)
                

  if curr_hole:
    holes[curr_hole] = {
      'cells': curr_hole_trav
    }
  
  return holes
  

  
# # ***
# def flood_fill(cell):
#   # non edge side change in single dim
#   trav = []
#   to_trav = []
#   return trav



def get_edge_grid(grid):
  # uldr = 0000
  
  u_edge = '1000'
  no_edge = '0000'
  
  dir_nos = {
    'r': 1,
    'd': 10,
    'l': 100,
    'u': 1000
  }
  
  grid_w = len(grid[0])
  
  def add_edge(edges, edge):
    num = int(edges) + dir_nos[edge]
    return "{:04d}".format(num)
    # return str().zfill(4)
    
  edge_grid = []
  
  # Set row level prev
  prev_edges_row = []
  # Just
  prev_cell_row = []
  
  for cell_row in grid:
    # Your guinea pig, row level
    curr_edges_row = [no_edge] * grid_w
    
    # if not prev_edges_row:
#       curr_edges_row = [u_edge] * grid_w
    
    # Set cell level prev
    prev_edge = None
    # Just
    cell_prev = None
    
    for idx, cell in enumerate(cell_row):
      # Your guinea pig, cell level
      curr_edge = curr_edges_row[idx]
      
      if not cell_prev:
        curr_edge = add_edge(curr_edge, 'l')
        
      if cell:
        if cell_prev and cell_prev['color'] == cell['color']:
          curr_edge = add_edge(curr_edge, 'l')
          prev_edge = add_edge(prev_edge, 'r')
        
        if prev_cell_row and prev_cell_row[idx] and prev_cell_row[idx]['color'] == cell['color']:
          # Put down in that one and up in current
          prev_edges_row[idx] = add_edge(prev_edges_row[idx], 'd')
          curr_edge = add_edge(curr_edge, 'u')
          
        elif not prev_cell_row or not prev_cell_row[idx]:
          curr_edge = add_edge(curr_edge, 'u')
          
      else:
        if cell_prev:
          prev_edge = add_edge(prev_edge, 'r')
          
        if prev_cell_row and prev_cell_row[idx]:
          prev_edges_row[idx] = add_edge(prev_edges_row[idx], 'd')
      
      
      # Add PREV edge to row, and update it
      if idx > 0:
        curr_edges_row[idx-1] = prev_edge
      prev_edge = curr_edge
      # Just
      cell_prev = cell
      
      
    # Update the right for end of row
    prev_edge = add_edge(prev_edge, 'r')
    curr_edges_row[grid_w-1] = prev_edge
    
    
    # Add PREV row to grid, and update it
    if prev_edges_row:
      edge_grid.append(prev_edges_row)
    prev_edges_row = curr_edges_row
    # Just
    prev_cell_row = cell_row
    
    
    
  # Update the down for end of grid
  prev_edges_row = [add_edge(edge, 'd') for edge in prev_edges_row]
  edge_grid.append(prev_edges_row)

  return edge_grid


# TODO: dirtied with a cell_coord_list for perf, but now returns different than input
def get_rotated(piece, rotation, get_list=True):
    grid = piece['grid']
    l = len(grid[0])
    h = len(grid)

    if rotation == 90:
        first_range = range(l)
        second_range = range(h - 1, -1, -1)
        get_edges = lambda x: x[1:] + x[0]
        
    elif rotation == 180:
        first_range = range(h - 1, -1, -1)
        second_range = range(l - 1, -1, -1)
        get_edges = lambda x: x[2:] + x[:2]
    
    rotated_grid = []
    cell_coord_list = []
    
    ir = 0
    for i in first_range:  
      row = []
      jr = 0
      
      for j in second_range:
        if rotation == 90:
          b = copy.copy(grid[j][i])
        else:
          b = copy.copy(grid[i][j])
        if b:
            b['coord_pair'] = [ir, jr]
            b['coord'] = str(ir) + str(jr)
            b['edges'] = get_edges(b['edges'])
            
            if get_list: 
              cell_coord_list.append(b['coord'] + b['color'])
        row.append(b)
        jr += 1
        
      rotated_grid.append(row)
      ir += 1
      
    return {
      'grid': rotated_grid,
      'cell_coord_list': cell_coord_list
    }
    


# def get_windows(patt):
#   return get_best_hori_windows(patt) + get_best_hori_windows(get_rotated(patt, 90))


# MIN_WINDOW_CELLS = 4
MIN_WINDOW_EDGES = 5

# window recalc is cheaper
# Also take into account the hole full cell count, 
#   And the available pieces
#   so you know the next expectant piece counts 
# TODO:
# Edges filter only for wide distributions of window stats (big, polygonal holes)
#   and for places there are weird areas
#   yep, only for big holes, where you have 
#   so many cells so you have to filter by edge density

# TODO: Longer windows for small_wand
# and incorporate next_expected_piece_count

WINDOW_DIMS = {
  'h': [2, 3], 
  'v': [3, 2],
  'lh': [1, 4],
  'lv': [1, 4],
  'sh': []
}

def get_long_windows(patt):
  # edge scores first for 4 line
  # but first existence cells, for hori and vert
  
  h = len(patt)
  w = len(patt[0])
  
  hori_windows = []
  for row in patt:
    longest_cts_length = 0
    longest_cts_length_coord = None
    for cell in row:
      if not cell:
        if longest_cts_length >= 4:
          break
        else:
          longest_cts_length = 0
          longest_cts_length_coord = None
      else:
        if not longest_cts_length_coord:
          longest_cts_length_coord = cell['rel_coord_pair']
        longest_cts_length += 1
        
    if longest_cts_length >= 4:
      wins = []
      for i in range(longest_cts_length - 4 + 1):
        coord_pair = longest_cts_length_coord
        wins.append({
          'coord': [coord_pair[0], coord_pair[1] + i],
          'color': patt[coord_pair[0]][coord_pair[1] + i]['color']
          # 'type': 'hori'
        })
      
      # only take touching windows
      hori_windows = [wins[0], wins[-1]] if len(wins) > 1 else wins
        
  vert_windows = []
  for x in range(w):
    longest_cts_length = 0
    longest_cts_length_coord = None
    for y in range(h):
      cell = patt[y][x]
      if not cell:
        if longest_cts_length >= 4:
          break
        else:
          longest_cts_length = 0
          longest_cts_length_coord = None
      else:
        if not longest_cts_length_coord:
          longest_cts_length_coord = cell['rel_coord_pair']
        longest_cts_length += 1
        print('vert', cell['rel_coord_pair'], longest_cts_length)
        
    if longest_cts_length >= 4:
      wins = []
      for i in range(longest_cts_length - 4 + 1):
        coord_pair = longest_cts_length_coord
        wins.append({
          'coord': [coord_pair[0] + i, coord_pair[1]],
          'color': patt[coord_pair[0] + i][coord_pair[1]]['color']
          # 'type': 'vert'
        })
        
      # only take touching windows
      vert_windows = [wins[0], wins[-1]] if len(wins) > 1 else wins
        
  return hori_windows, vert_windows

def get_valid_windows(patt, next_expected_piece_count, small_wand_too):
  valid_windows = []
  
  h = len(patt)
  w = len(patt[0])
  
  SMALL_WAND_WIN = False
  
  # Special case for the square tile, and all the smaller ones?
  # Wait naa, maybe they'll be taken care of anyway. Test and check.
  if h * w < 6 and not SMALL_WAND_WIN:
    return [['00', [h, w], get_cell_count(patt)]]
  
  cell_grid, edge_count_grid = get_cell_and_edge_count_grids(patt, h, w)
  hori_cell_2_grads, hori_cell_3_grads = get_hori_cell_gradients(cell_grid, h, w)
  
  # TODO: justify min_window_cells for this hole general windows
  
  # w - WINDOW_DIMS['h'][1] + 1
  cell_count_window_distribution = {}
  cell_sums_wide = get_cell_sums_wide(hori_cell_2_grads, cell_count_window_distribution, h, w)
  cell_sums_long = get_cell_sums_long(hori_cell_3_grads, cell_count_window_distribution, h, w)
  
  windows = get_windows_by_cell_count_window_distribution(cell_count_window_distribution)

  return windows
  

  # print(cell_grid)
  # print(edge_count_grid)
  # print('')
  # print(hori_cell_2_grads)
  # print(hori_cell_3_grads)
  # print('')
  # print(cell_sums_wide)
  # print(cell_sums_long)
  
  # return ['34h', '26v']

def get_cell_and_edge_count_grids(patt, h, w):
  cell_grid = []
  edge_count_grid = []
  
  for i in range(h):
    cells = []
    edge_counts = []
    for j in range(w):
      cell = patt[i][j]
      if cell:
        cells.append(1)
        edge_count = cell['edges'].count('1')
        edge_counts.append(edge_count)
      else:
        cells.append(0)
        edge_counts.append(0)
      
    cell_grid.append(cells)
    edge_count_grid.append(edge_counts)
    
  return cell_grid, edge_count_grid
  
def get_hori_cell_gradients(cell_grid, h, w):
  hori_cell_2_grads = []
  hori_cell_3_grads = []
  
  for i in range(h - WINDOW_DIMS['h'][0] + 1):
    grad_2_row = []
    grad_3_row = [] if i < h - WINDOW_DIMS['h'][0] else None
    
    for j in range(w): 
      sum_2 = cell_grid[i][j] + cell_grid[i+1][j]
      grad_2_row.append(sum_2)
      
      if type(grad_3_row) is list:
        sum_3 = sum_2 + cell_grid[i+2][j]
        grad_3_row.append(sum_3)
        
    hori_cell_2_grads.append(grad_2_row)
    
    if type(grad_3_row) is list:
      hori_cell_3_grads.append(grad_3_row)
      
  return hori_cell_2_grads, hori_cell_3_grads
  
def get_cell_sums_wide(hori_cell_2_grads, cell_count_window_distribution, h, w):
  cell_sums_wide = []
  
  for i in range(h - WINDOW_DIMS['h'][0] + 1):
    grad_wide_sums = []
    # next_sum = None
    for j in range(w - WINDOW_DIMS['h'][1] + 1):
      this_sum = hori_cell_2_grads[i][j] + hori_cell_2_grads[i][j+1] + hori_cell_2_grads[i][j+2]
      
      window = [str(i) + str(j), [2, 3], this_sum]
      if this_sum not in cell_count_window_distribution:
        cell_count_window_distribution[this_sum] = [window]
      else:
        cell_count_window_distribution[this_sum].append(window)
        
      grad_wide_sums.append(this_sum)
      
    cell_sums_wide.append(grad_wide_sums)
    
  return cell_sums_wide
  
def get_cell_sums_long(hori_cell_3_grads, cell_count_window_distribution, h, w):
  cell_sums_long = []
  
  for i in range(h - WINDOW_DIMS['v'][0] + 1):
    grad_long_sums = []
    # next_sum = None
    for j in range(w - WINDOW_DIMS['v'][1] + 1):
      this_sum = hori_cell_3_grads[i][j] + hori_cell_3_grads[i][j+1]
      
      window = [str(i) + str(j), [3, 2], this_sum]
      if this_sum not in cell_count_window_distribution:
        cell_count_window_distribution[this_sum] = [window]
      else:
        cell_count_window_distribution[this_sum].append(window)
      
      grad_long_sums.append(this_sum)
      
    cell_sums_long.append(grad_long_sums)
  
  return cell_sums_long
  
def get_windows_by_cell_count_window_distribution(cell_count_window_distribution):
  windows = []
  ccwd = cell_count_window_distribution
  COUNT_CUTOFF = 1
  
  if ccwd:
    if len(ccwd) == 1:
      windows = ccwd.values()[0]
    else:
      # more than two kinds of sizes (counts)
      sizes = sorted(ccwd.keys(), reverse=True)
      if len(ccwd[sizes[0]]) > COUNT_CUTOFF:
        windows = ccwd[sizes[0]]
      else:
        windows = ccwd[sizes[0]] + ccwd[sizes[1]]
        
  return windows
  
  