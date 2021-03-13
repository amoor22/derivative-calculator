import re
import sympy as smp
from pytexit import py2tex
from flask import Flask, render_template, redirect, request, url_for
from calculations import *
# --------- FLASK ---------
max_der = 20
cache = {'arabic': True, 'calculate': [], 'statement': '', 'der_num': None}
app = Flask(__name__)
class Error:
    def __init__(self, string_en, string_ar):
        self.string_en = string_en
        self.string_ar = string_ar
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
            statement = str(request.form['math-input'])
            der_num = int(request.form['der-num'])
            print('ddd')
            calculate = classify(statement, der_num)
            derivatives = calculate[0]
            plotting = calculate[1]
            cache['calculate'] = calculate
            cache['statement'] = statement
            cache['der_num'] = der_num
            return render_template('index.html', derivatives=derivatives, plotting=plotting, arabic=cache['arabic'], input=[statement, der_num])
            print(e, 'fd')
            render_template('index.html', error=Error('An error occurred, please try again', 'حدث خطأ ما، حاول مرة أخرى'))
    return render_template('index.html', arabic=cache['arabic'])
@app.route('/next/', methods=['POST', 'GET'])
def next():
    try:
        statement = cache['statement']
        der_num = int(request.args.get('data'))
        if 0 < der_num <= max_der:
            calculate = classify(statement, der_num)
            derivatives = calculate[0]
            plotting = calculate[1]
            cache['calculate'] = calculate
            cache['statement'] = statement
            cache['der_num'] = der_num
            return render_template('index.html', derivatives=derivatives, plotting=plotting, arabic=cache['arabic'], input=[statement, der_num])
        else:
            der_num = max_der
            calculate = classify(statement, der_num)
            derivatives = calculate[0]
            plotting = calculate[1]
            cache['calculate'] = calculate
            cache['statement'] = statement
            cache['der_num'] = der_num
            return render_template('index.html', derivatives=derivatives, plotting=plotting, arabic=cache['arabic'], input=[statement, der_num])
    except Exception as e:
        print()
        return render_template('index.html')
@app.route('/language', methods=['POST', 'GET'])
def language():
    try:
        calculate = cache['calculate']
        derivatives = calculate[0]
        plotting = calculate[1]
        der_num = cache['der_num']
        statement = cache['statement']
    except:
        derivatives, plotting = [[], None]
        der_num = None
        statement = None
    if request.method == 'POST':
        if request.form['language'] == 'en':
            cache['arabic'] = False
            if statement and der_num:
                return render_template('index.html', arabic=cache['arabic'], derivatives=derivatives, plotting=plotting, input=[statement, der_num])
            else:
                return render_template('index.html', arabic=cache['arabic'], derivatives=derivatives, plotting=plotting)
        else:
            cache['arabic'] = True
            if statement and der_num:
                return render_template('index.html', arabic=cache['arabic'], derivatives=derivatives, plotting=plotting, input=[statement, der_num])
            else:
                return render_template('index.html', arabic=cache['arabic'], derivatives=derivatives, plotting=plotting)
if __name__ == '__main__':
    app.run(debug=True)
    pass