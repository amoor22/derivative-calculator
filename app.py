import re
import sympy as smp
from pytexit import py2tex
from flask import Flask, render_template, redirect, request, url_for
from calculations import *
# --------- FLASK ---------
app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index(): 
    if request.method == 'POST':
        statement = str(request.form['math-input'])
        der_num = int(request.form['der-num'])
        derivatives = classify(statement, der_num)
        print(derivatives[0][0][-1].step)
        # for derivative in derivatives:
        #     derivative[0] = list(map(lambda x: py2tex(str(x.step), False, False) ,derivative[0]))
        print(derivatives[0][0][-1].step)
        return render_template('index.html', derivatives=derivatives)
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
    return render_template('index.html')
if __name__ == '__main__':
    app.run(debug=True)
    pass