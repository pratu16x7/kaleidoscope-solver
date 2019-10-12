from flask import Flask, render_template
from solver import Solver
from detector import get_pattern_img, get_black_thresh
from puzzle import get_board_from_img


app = Flask(__name__)

@app.route('/')
def home():
  pattern_img = get_pattern_img()
  board = get_board_from_img(pattern_img, get_black_thresh())
  
  # TODO: get only the string of the board from img,
  # do everything else via the solver
  solver = Solver(board)
  
  return render_template('home.html', data=solver.board, holes=solver.holes, pieces=solver.pieces)
  
if __name__ == "__main__":
    app.run(debug=True)
