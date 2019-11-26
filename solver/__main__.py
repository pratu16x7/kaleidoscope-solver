# EVERYTHING that's not directly related to the algorithm

# !!!!!!!!!!!!!!!
# IMPORTANT !!!
# ALL the learnings from matching pieces to grid windows should be consolidated and used for the next solve
# all stored as indexs for lightning fast piece to window matching
# it's a similar concept on which ML depends: 
# training and getting a model that is used for subsequent solves

# Looks like this program will have 3 major parts:
# 1. The learnings indexes, and the program to generate them
# 2. The Solver program, all the heavylifting logic
# 3. The presenter program, keeping track of the states and scores


from flask import Flask, render_template, get_template_attribute
from solver import Puzzle, Solver
from detector import get_pattern_img, get_black_thresh
from puzzle import get_board_from_img, add_piece_edges_to_grid

app = Flask(__name__)

pattern_img = get_pattern_img()
# TODO: get only the string of the board from img,
# do everything else via the solver
board = get_board_from_img(pattern_img, get_black_thresh())
raw_board = get_board_from_img(pattern_img, get_black_thresh(), False)

puzzle = Puzzle(board['red_count'], board['black_count'])
app.jinja_env.globals.update(get_piece=puzzle.get_piece)

pieces = list(puzzle.get_pieces())
solver = Solver(board, pieces, puzzle)

# piece_sets = puzzle.get_piece_sets()

pieces_registry = puzzle.get_pieces_registry()

pieces_map = {}
for name, piece in pieces_registry.items():
  size = piece['size']
  name = piece['name']
  dev = piece['deviation']
  
  if size not in pieces_map:
    pieces_map[size] = {}
  
  if dev not in pieces_map[size]:
    pieces_map[size][dev] = [name]
  else:
    pieces_map[size][dev].append(name)
    
    
moves = []

@app.route('/')
def home():
  return render_template('home.html', 
    raw_board=raw_board,
    data=board, 
    holes=solver.all_holes, 
    pieces_map=pieces_map
  )
  
board_grid = board['grid']

@app.route('/get_next_move')
def get_next_move():
  grid_macro = get_template_attribute('components.html', 'grid_pattern')
  board_template = grid_macro(board_grid, 'board') 
  
  move = solver.get_next_move()
  if type(move) == str:
    
    return {
      'state': move, 
      'board': board_template
    }
      
  # TODO: macro doesn't take some keys
  move_macro = get_template_attribute('components.html', 'move')
  move_template = move_macro(**(move.__dict__)) 
  
  moves.append(move)
  
  the_hole = [hole for hole in solver.all_holes if hole['id'] == move.global_hole_id][0]
  add_piece_edges_to_grid(board_grid, puzzle.get_piece(move.piece, move.orient), move.coord, the_hole['offset'])
  
  return {
    'message': move_template,
    'solved': solver.state.solved,
    'board': board_template
  }
  
if __name__ == "__main__":
    app.run(debug=True)
