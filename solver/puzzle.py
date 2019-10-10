from data import PIECES

# Also the utils to calc state given an input board/state

# Always err on the side of 'the way we'd do it' 


# Magic Wand placement has its own special rules. First all possibilities, 
# then choose the one that leaves the hole less edge dense.


# we are doing the tree pruning as much as we can


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


def get_pieces():
  pieces = []
  for p in PIECES:
    piece = calc_props(p['val'])
    piece['name'] = p['name']
    pieces.append(piece)
    print(piece['grid'])
    
  return pieces
  
  
# ***
def calc_props(s):
  # everything computable
  
  # get colors in a grid
  # get edges
  # Null blocks are IMPORTANT
  
  cells = {}
  # TODO: blue/yellow version alert
  colored_cells_cnt = 0
  # blue_cells_cnt = 0
  cell_type = 'r'
  
  for i in range(0, len(s), 3):
    cell = s[i: i+3]
    coord = cell[:2]
    y, x = coord[0], coord[1]
    color = cell[2]
    
    cells[coord] = {
      'coord': [int(y), int(x)],
      'color': color
    }
    
    if color == 'r':
      colored_cells_cnt += 1

  grid_h = max([cell['coord'][0] for cell in cells.values()]) + 1
  grid_w = max([cell['coord'][1] for cell in cells.values()]) + 1
  
  grid = []
  
  for i in range(grid_h):
    row = []
    for j in range(grid_w):
      coord = str(i) + str(j)
      row.append(cells[coord] if coord in cells else None)
    grid.append(row)
  
    
  grid = add_edges_to_grid_data(grid)
  
  # TODO:
  # perimeter = 
  
  # deviation_index = 
  
  # orientations =
  
  return {
    'grid': grid,
    'size': len(cells),
    'type': cell_type,
    'colored_cells_cnt': colored_cells_cnt,
    # 'perimeter': perimeter,
    # 'deviation_index': deviation_index,
    # 'orientations': orientations
  }
  
  
def add_edges_to_grid_data(grid):
  # ulrd = 0000
  
  u_edge = '1000'
  no_edge = '0000'
  
  dir_nos = {
    'd': 1,
    'r': 10,
    'l': 100,
    'u': 1000
  }
  
  def add_edge(edges, edge):
    num = int(edges) + dir_nos[edge]
    return "{:04d}".format(num)
    # return str().zfill(4)
    
  edge_pattern = []
  
  # Set row level prev
  prev_edges_row = []
  # Just
  prev_cell_row = []
  
  for cell_row in grid:
    # Your guinea pig, row level
    curr_edges_row = [no_edge] * 8
    
    if not prev_edges_row:
      curr_edges_row = [u_edge] * 8
      
      
    
    
    # Set cell level prev
    prev_edge = None
    # Just
    cell_prev = None
    
    for idx, cell in enumerate(cell_row):
      # Your guinea pig, cell level
      curr_edge = curr_edges_row[idx]
      
      if not cell_prev:
        curr_edge = add_edge(curr_edge, 'l')
      
      if cell and cell_prev == cell['color']:
        curr_edge = add_edge(curr_edge, 'l')
        prev_edge = add_edge(prev_edge, 'r')
        
      if cell and prev_cell_row and prev_cell_row[idx] and prev_cell_row[idx]['color'] == cell['color']:
        # Put down in that one and up in current
        prev_edges_row[idx] = add_edge(prev_edges_row[idx], 'd')
        curr_edge = add_edge(curr_edge, 'u')
      
      
      # Add PREV edge to row, and update it
      if idx > 0:
        curr_edges_row[idx-1] = prev_edge
      prev_edge = curr_edge
      # Just
      cell_prev = cell and cell['color']
      
      
    # Update the right for end of row
    prev_edge = add_edge(prev_edge, 'r')
    curr_edges_row[7] = prev_edge
    
    
    # Add PREV row to pattern, and update it
    if prev_edges_row:
      edge_pattern.append(prev_edges_row)
    prev_edges_row = curr_edges_row
    # Just
    prev_cell_row = cell_row
    
    
    
  # Update the down for end of pattern
  prev_edges_row = [add_edge(edge, 'd') for edge in prev_edges_row]
  edge_pattern.append(prev_edges_row)
  
  
  
  for i, row in enumerate(grid):
    for j, cell in enumerate(row):
      if cell:
        cell['edges'] = edge_pattern[i][j]
      
      
  return grid

  


#########################################################################
# # Board props/stats:
# Red/blueyellow/red and blueyellow
# No of colored
# **No of holes
# ==>Checkered Index ~= size of biggest hole (generally 16 to 64) Higher count, more difficult with current mothod (if different color, then slightly easier)
# 
# ****Feature density (a feature can itself be checkered too, the different color talked about above)
#########################################################################

SAMPLE_BOARD_41 = [
  '00x01y02x03b04x05r06x07r10b11x ....'
]

def get_board(board_grid):
  # with all the edges, counts, holes, hole sizes, hole start zones, checkered index
  return board

# **
def get_holes(cell):
  trav = []
  untrav = []
  
  holes = {}
  
  # Do flood fills for each of the untrav, with diff color each time, and keep adding in trav
  
  return holes
  
# ***
def flood_fill(cell):
  # non edge side change in single dim
  trav = []
  to_trav = []
  return trav



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
# anomalies, like hole in inconsistent state on numeric cell/color count
# Update Hole state with count and stuff, if broken make two holes 
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







# # Game state / Board props after every play (All of this can belong in a local state)
# No of holes, with sizes, hole divided hardly/roughly into 'attemptable' windows by edge density
# used pieces, remaining pieces
# remaining pieces possible positions, no of possible positions (if even one does not have a possible position, abandon move, backtrack and retry)
# ==> *** how we're doing heuristic, based on used/remaining pieces sizes and crookedness indices






