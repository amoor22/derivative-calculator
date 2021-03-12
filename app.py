import re
import sympy as smp
from pytexit import py2tex
from flask import Flask, render_template, redirect, request, url_for
from calculations import *
# --------- FLASK ---------
cache = {'arabic': True}
app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        statement = str(request.form['math-input'])
        der_num = int(request.form['der-num'])
        calculate = classify(statement, der_num)
        derivatives = calculate[0]
        plotting = calculate[1]
        print(cache['arabic'])
        return render_template('index.html', derivatives=derivatives, plotting=plotting, arabic=cache['arabic'])
        # try:
            # data = py2tex(request.form['math-input'].strip())
            # derivatives = []
            # inp = request.form['math-input'].strip();
            # comma_sep = inp.split(',')
            # if len(comma_sep) == 1:
            #     steps, operation_type = get_derivative_full(comma_sep[0])
            #     steps = list(map(lambda x: py2tex(str(x.step)), steps))
            #     derivatives.append(steps)
            #     return render_template('index.html', derivatives=derivatives)
            # else:
            #     current_der = comma_sep[0]
            #     for i in range(int(comma_sep[1])):
            #         steps, operation_type = get_derivative_full(str(current_der))
            #         current_der = steps[-1].step
            #         steps = list(map(lambda x: py2tex(str(x.step)), steps))
            #         derivatives.append(steps)
            #     return render_template('index.html', derivatives=derivatives)
            #     pass
        # except Exception as e:
        #     print(e)
        #     error = 'An error occurred please try again'
        #     return render_template('index.html', error=error)
    return render_template('index.html', arabic=cache['arabic'])
@app.route('/language', methods=['POST', 'GET'])
def language():
    if request.method == 'POST':
        if request.form['language'] == 'en':
            cache['arabic'] = False
            return render_template('index.html', arabic=cache['arabic'])
        else:
            cache['arabic'] = True
            return render_template('index.html', arabic=cache['arabic'])
if __name__ == '__main__':
    app.run(debug=True)
    pass