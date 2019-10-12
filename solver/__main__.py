from flask import Flask, render_template
from detector import get_pattern
from puzzle import get_pieces

app = Flask(__name__)

@app.route('/')
def home():
  data = get_pattern()
  return render_template('home.html', data=data, pieces=get_pieces())
  
if __name__ == "__main__":
    app.run(debug=True)
