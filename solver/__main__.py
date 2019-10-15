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

  
  
  window_index, changed_hole, winner = solver.solve(solver.holes['1hole']['grid'], 4)
  window_index2, changed_hole2, winner2 = solver.solve(changed_hole, 4)
  window_index3, changed_hole3, winner3 = solver.solve(changed_hole2, 3)
  
  # print(windows)
  
  
  
  return render_template('home.html', 
    data=solver.board, 
    holes=solver.holes, 
    piece_sets=solver.get_piece_sets(),
    window_index=window_index,
    
    changed_hole=changed_hole,
    changed_hole2=changed_hole2,
    changed_hole3=changed_hole3, 
    
    winner=winner,
    winner2=winner2,
    winner3=winner3,
  )
  
if __name__ == "__main__":
    app.run(debug=True)
