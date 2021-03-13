import re
import sympy as smp
from pytexit import py2tex
from flask import Flask, render_template, redirect, request, url_for
from calculations import *
# --------- FLASK ---------
cache = {'arabic': True, 'calculate': []}
app = Flask(__name__)
class Error:
    def __init__(self, string_en, string_ar):
        self.string_en = string_en
        self.string_ar = string_ar
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            statement = str(request.form['math-input'])
            der_num = int(request.form['der-num'])
            calculate = classify(statement, der_num)
            derivatives = calculate[0]
            plotting = calculate[1]
            cache['calculate'] = calculate
            return render_template('index.html', derivatives=derivatives, plotting=plotting, arabic=cache['arabic'])
        except Exception as e:
            render_template('index.html', error=Error('An error occurred, please try again', 'حدث خطأ ما، حاول مرة أخرى'))
    return render_template('index.html', arabic=cache['arabic'])
@app.route('/language', methods=['POST', 'GET'])
def language():
    try:
        calculate = cache['calculate']
        derivatives = calculate[0]
        plotting = calculate[1]
    except:
        derivatives, plotting = [[], None]
    if request.method == 'POST':
        if request.form['language'] == 'en':
            cache['arabic'] = False
            return render_template('index.html', arabic=cache['arabic'], derivatives=derivatives, plotting=plotting)
        else:
            cache['arabic'] = True
            return render_template('index.html', arabic=cache['arabic'], derivatives=derivatives, plotting=plotting)
if __name__ == '__main__':
    app.run(debug=True)
    pass