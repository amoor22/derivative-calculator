import re
from flask.globals import session
from flask import Flask, render_template, redirect, request, url_for, session
from calculations import *
import jsonpickle
# --------- FLASK ---------
max_der = 20
cache = {'arabic': True, 'calculate': [], 'statement': '', 'der_num': None}
app = Flask(__name__)
app.secret_key = 'secret_key'
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
            session['calculate'] = jsonpickle.encode(calculate)
            session['statement'] = statement
            session['der_num'] = der_num
            return render_template('index.html', derivatives=derivatives, plotting=plotting, arabic=session.get('arabic', True), input=[statement, der_num])
        except Exception as e:
            print(e)
            render_template('index.html', error=Error('An error occurred, please try again', 'حدث خطأ ما، حاول مرة أخرى'))
    return render_template('index.html', arabic=session.get('arabic', True))
@app.route('/next/', methods=['POST', 'GET'])
def next():
    try:
        statement = session.get('statement', '')
        der_num = int(request.args.get('data'))
        if 0 < der_num <= max_der:
            calculate = classify(statement, der_num)
            derivatives = calculate[0]
            plotting = calculate[1]
            session['calculate'] = jsonpickle.encode(calculate)
            session['statement'] = statement
            session['der_num'] = der_num
            return render_template('index.html', derivatives=derivatives, plotting=plotting, arabic=session.get('arabic', True), input=[statement, der_num])
        else:
            der_num = max_der
            calculate = classify(statement, der_num)
            derivatives = calculate[0]
            plotting = calculate[1]
            session['calculate'] = jsonpickle.encode(calculate)
            session['statement'] = statement
            session['der_num'] = der_num
            return render_template('index.html', derivatives=derivatives, plotting=plotting, arabic=session.get('arabic', True), input=[statement, der_num])
    except Exception as e:
        print('next f')
        return render_template('index.html')
@app.route('/language', methods=['POST', 'GET'])
def language():
    try:
        calculate = jsonpickle.decode(session.get('calculate', []))
        derivatives = calculate[0]
        plotting = calculate[1]
        der_num = session.get('der_num', None)
        print(der_num)
        statement = session.get('statement', '')
    except:
        derivatives, plotting = [[], None]
        der_num = None
        statement = None
    if request.method == 'POST':
        if request.form['language'] == 'en':
            session['arabic'] = False
            if statement and der_num:
                return render_template('index.html', arabic=session.get('arabic', True), derivatives=derivatives, plotting=plotting, input=[statement, der_num])
            else:
                return render_template('index.html', arabic=session.get('arabic', True), derivatives=derivatives, plotting=plotting)
        else:
            session['arabic'] = True
            if statement and der_num:
                return render_template('index.html', arabic=session.get('arabic', True), derivatives=derivatives, plotting=plotting, input=[statement, der_num])
            else:
                return render_template('index.html', arabic=session.get('arabic', True), derivatives=derivatives, plotting=plotting)
if __name__ == '__main__':
    app.run(debug=True)
    pass