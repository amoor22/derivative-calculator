import decimal
from flask import jsonify, Flask, render_template
from json import dumps

from flask.json import loads
from jsonpickle import decode, encode

class thing:
    def __init__(self):
        self.so = 'ds'
app = Flask(__name__)
@app.route('/')
def index():

    asss = encode([['21', '23', True, thing()]])
    print(decode(asss))
    return render_template('index.html')

app.run(debug=True)