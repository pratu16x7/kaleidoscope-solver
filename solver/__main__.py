# EVERYTHING that's not directly related to the algorithm

from flask import Flask, render_template
from solver import Solver
from detector import get_pattern_img, get_black_thresh
from puzzle import get_board_from_img


app = Flask(__name__)


from solver import Puzzle
puzzle = Puzzle()
app.jinja_env.globals.update(get_piece=puzzle.get_piece)

@app.route('/')
def home():
  pattern_img = get_pattern_img()
  board = get_board_from_img(pattern_img, get_black_thresh())
  
  # TODO: get only the string of the board from img,
  # do everything else via the solver
  
  solver = Solver(board)

  
  hole = solver.holes['1hole']
  solution_progression = solver.solve_hole(hole)
  
  return render_template('home.html', 
    data=solver.board, 
    holes=solver.holes, 
    piece_sets=solver.get_piece_sets(),
    window_index=solution_progression[0][1],
    
    hole=hole['grid'],
    solution_progression=solution_progression,
  )
  
if __name__ == "__main__":
    app.run(debug=True)
