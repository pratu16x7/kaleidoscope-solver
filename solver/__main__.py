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
from puzzle import get_board_from_img


app = Flask(__name__)


puzzle = Puzzle()
app.jinja_env.globals.update(get_piece=puzzle.get_piece)

pattern_img = get_pattern_img()
# TODO: get only the string of the board from img,
# do everything else via the solver
board = get_board_from_img(pattern_img, get_black_thresh())
solver = Solver(board)

@app.route('/')
def home():
  return render_template('home.html', 
    data=solver.board, 
    holes=solver.all_holes, 
    piece_sets=solver.get_piece_sets()
  )

@app.route('/get_next_move')
def get_next_move():
  move_macro = get_template_attribute('components.html', 'move')
  move = move_macro(*solver.get_next_move()) 
  return {
    'message': move
  }
  
if __name__ == "__main__":
    app.run(debug=True)
