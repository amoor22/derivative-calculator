import re
import sympy as smp
from pytexit import py2tex
from flask import Flask, render_template, redirect, request, url_for
possible_pow = ('**', '^')
# statement = "2.5x^2 + 4x + 5 + 5x"
types = ('statement', 'multiply', 'division')
symbol = 'x'
# steps
normal_steps_en = ['Simplify (if needed)', 'Using derivative rules', 'Final simplification (if needed)']
mult_steps_en = ['Calculate the derivative of both functions', 'Using the rule of multiplication', 'Substituting in the rule', 'Adding values together']
div_steps_en = ['Calculate the derivative of both functions', 'Using the rule of multiplication', 'Substituting in the rule', 'Adding values together', 'Final simplification']
smp_steps_en = ['Calculate the derivative']
class Step:
    def __init__(self, step, info_en, info_ar, count=0, latex=False):
        self.step = step
        self.info_en = info_en
        self.info_ar = info_ar
        self.count = count
        self.latex = latex
    def __repr__(self):
        return str(self.step)
    
    def get_latex(self):
        if not self.latex:
            return py2tex(str(self.step), False, False)
        return self.step
class Unit:
    @staticmethod
    def classify(amount):
        try:
            float(amount)
            return Constant(amount)
        except:
            return Variable(amount, 'x')
class Constant(Unit):
    def __init__(self, const):
        self.constant = const
        self.derivative = 0;
    
    def get_derivative(self):
        return self.derivative

    def get_sympy_format(self):
        return f'{self.constant}'
    
    def get_sympy_format_der(self):
        return f'{self.derivative}'

    def get_tex_format(self):
        return f'{self.constant}'
class Variable(Unit):
    def __init__(self, string, letter='x'):
        '-x^3'
        self.raw_string = string
        self.letter = letter
        self.get_data()

    def get_data(self):
        self.raw_string = self.raw_string.strip()
        self.raw_string = self.raw_string.replace(' ', '')
        self.raw_string = self.raw_string.replace('^', '**')
        split_power = self.raw_string.split('**')
        if len(split_power) == 1:
            self.power = 1
        else:
            # print(split_power[1])
            self.power = float(split_power[1])
        
        # To be replaced with a regular expression
        self.raw_string = self.raw_string.replace('*', '')
        split_power = self.raw_string.split('**')
        # --------
        split_x = list(filter(lambda x: x != '', split_power[0].split(self.letter)))
        if len(split_x) == 0 or self.raw_string[0] == self.letter:
            self.factor = 1
        else:
            if split_x[0] == '-':
                self.factor = -1
            elif split_x[0] == '+':
                self.factor = 1
            else:
                self.factor = float(split_x[0])
        self.get_derivative()
    
    def get_derivative(self):
        new_power = self.power - 1
        new_factor = self.power * self.factor
        if new_power == 1: 
            self.derivative = f'{new_factor}{self.letter}'
            return f'{new_factor}{self.letter}'
        if new_power == 0:
            self.derivative = f'{new_factor}'
            return f'{new_factor}'
        if new_factor == 1: new_factor = ''
        if new_factor == -1: new_factor = '-'
        self.derivative = f'{new_factor}{self.letter}^{new_power}' 
        return f'{new_factor}{self.letter}^{new_power}'

    def get_sympy_format_der(self):
        new_power = self.power - 1
        new_factor = self.power * self.factor
        return f'{new_factor}*{self.letter}**{new_power}'

    def get_sympy_format(self):
        return f'{self.factor}*{self.letter}**{self.power}'

    def get_tex_format(self):
        return f'{self.factor}*{self.letter}**{self.power}'

def get_derivative_full(statement):
    statement = re.sub(r'\s+', '', statement)
    original_tex = ''
    steps = []
    stop = ['+', '-']
    begin = 0
    new_statement = ''
    for i in range(len(statement)):
        if statement[i] in stop:
            new_statement += Unit.classify(statement[begin: i]).get_sympy_format_der() + statement[i]
            original_tex += Unit.classify(statement[begin: i]).get_tex_format() + statement[i]
            begin = i + 1
        if i == len(statement) - 1:
            new_statement += Unit.classify(statement[begin: ]).get_sympy_format_der()
            original_tex += Unit.classify(statement[begin: ]).get_tex_format()
    steps.append(Step(smp.nsimplify(original_tex), normal_steps_en[0], normal_steps_en[0], 1))
    steps.append(Step(new_statement, normal_steps_en[1], normal_steps_en[1], 2))
    steps.append(Step(smp.nsimplify(new_statement), normal_steps_en[2], normal_steps_en[2], 3))
    return [steps, types[0]]
def get_sympy_format_full(statement):
    statement = re.sub(r'\s+', '', statement)
    original_tex = ''
    steps = []
    stop = ['+', '-']
    begin = 0
    new_statement = ''
    for i in range(len(statement)):
        if statement[i] in stop:
            new_statement += Unit.classify(statement[begin: i]).get_sympy_format() + statement[i]
            original_tex += Unit.classify(statement[begin: i]).get_tex_format() + statement[i]
            begin = i + 1
        if i == len(statement) - 1:
            new_statement += Unit.classify(statement[begin: ]).get_sympy_format()
            original_tex += Unit.classify(statement[begin: ]).get_tex_format()
    return new_statement

def get_derivative_mult(func1, func2):
    steps = []
    der1 = str(get_derivative_full(func1)[0][-1].step)
    der2 = str(get_derivative_full(func2)[0][-1].step)
    steps.append(Step(r'$$f^{\prime}(x) = ' + f'{der1}' + r'\;  |  \;' + r'g^{\prime}(x) = ' + f'{der2}' + '$$', mult_steps_en[0], mult_steps_en[0], latex=True))
    steps.append(Step(r'$$\frac{d}{dx} = f\left ( {x} \right ) \cdot g^{\prime}\left ( {x} \right ) + g\left ( {x} \right ) \cdot f^{\prime}\left ( {x} \right )$$', mult_steps_en[1], mult_steps_en[1], latex=True))
    sum1 = smp.nsimplify(f'({der2}) * ({get_sympy_format_full(func1)})')
    sum2 = smp.nsimplify(f'({der1}) * ({get_sympy_format_full(func2)})')
    try:
        sum1_org, sum2_org = sum1, sum2
        sum1_text = py2tex(str(sum1), False, False).replace('$', '')
        sum2_text = py2tex(str(sum2), False, False).replace('$', '')
        print(sum1, sum2)
    except Exception as e:
        sum1_text, sum2_text = sum1_org, sum2_org
    s = r'\left (' + r'\right )'
    steps.append(Step(r'$$\frac{d}{dx} = ' r'\left ('  f'{func1}' r'\right )' r' \cdot ' r'\left (' + f'{der2}' r'\right )' '+' r'\left (' f'{func2}' r'\right )' r' \cdot ' r'\left (' f'{der1}' r'\right )' '$$', mult_steps_en[2], mult_steps_en[2], latex=True))
    steps.append(Step(r'$$' r'\frac{d}{dx} = ' r'\left (' f'{sum1_text}' r'\right )' '+' r'\left (' f'{sum2_text}' r'\right )' r'$$', mult_steps_en[2], mult_steps_en[2], latex=True))
    final_sum = smp.nsimplify(sum1 + sum2)
    steps.append(Step(str(final_sum), mult_steps_en[3], mult_steps_en[3]))
    return [steps, types[1]]

def get_derivative_div(func1, func2):
    steps = []
    der1 = str(get_derivative_full(func1)[0][-1].step)
    der2 = str(get_derivative_full(func2)[0][-1].step)
    # s = r'$$f^{\prime}(x) = ' + f'{der1}' + '  |  ' + r'g^{\prime}(x) = ' + f'{der2}' + '$$'
    steps.append(Step(r'$$f^{\prime}(x) = ' + f'{der1}' + '  |  ' + r'g^{\prime}(x) = ' + f'{der2}' + '$$', div_steps_en[0], div_steps_en[0], latex=True))
    steps.append(Step(r'$$\frac{d}{dx}=\frac{\ \ g(x)\ \ \cdot f^{‎\prime}(x)-f(x)\cdot g^‎{\prime}(x)}{\left [ g(x) \right ]^2}$$', div_steps_en[1], div_steps_en[1], latex=True))
    sum_num_first = smp.nsimplify(f'({get_sympy_format_full(func2)}) * ({der1})')
    sum_num_second = smp.nsimplify(f'({get_sympy_format_full(func1)}) * ({der2})')
    substitute = r'$$\frac{d}{dx}=\frac{\ \ func2 \ \ \cdot der1-func1\cdot der2}{\left [ func2 \right ]^2}$$'
    substitute = substitute.replace('func2', py2tex(get_sympy_format_full(func2)).replace('$', ''))
    substitute = substitute.replace('func1', py2tex(get_sympy_format_full(func1)).replace('$', ''))
    substitute = substitute.replace('der1', py2tex(der1).replace('$', ''))
    substitute = substitute.replace('der2', py2tex(der2).replace('$', ''))
    print(substitute)
    steps.append(Step(r'', div_steps_en[1], div_steps_en[1], latex=True))
    sum_num = smp.nsimplify(f'{sum_num_first} - {sum_num_second}')
    final_sum = smp.nsimplify(f'({sum_num}) / (({get_sympy_format_full(func2)})**2)')
    print(sum_num_first, sum_num_second, sum_num, sep='    ')
    print(final_sum)
    return [steps, types[2]]
def remove_parentheses(string):
    string = string.replace('(', '')
    string = string.replace(')', '')
    return string
def sympy_function(statement):
    statement = re.sub(r'\s+', '', statement)
    iter_count = len(statement)
    max_iter_count = 300
    i = 0
    while i < iter_count:
        if i >= max_iter_count:
            break
        if statement[i] == symbol and i > 0:
            if statement[i - 1].isnumeric():
                statement = statement[: i] + '*' + statement[i:]
                iter_count = len(statement)
        i += 1
    return statement
sympy_function('(2x + x) ** 2')
def classify(statement, der_num):
    statement = re.sub(r'\s+', '', statement)
    statement = statement.replace('^', '**')
    statement_copy = statement
    cur_return = []
    div_pattern = r'\)\/\('
    mult_pattern = r'\)\*\('
    try:
        for i in range(der_num):
            statement = str(statement)
            statement_copy = str(statement_copy)
            if len(re.findall(mult_pattern, statement)) == 1:
                print('dsa')
                span = re.search(mult_pattern, statement).span()
                func1, func2 = list(map(lambda x: x.strip(), [statement[1: span[0]], statement[span[0] + 1 + 2: -1]]))
                func1, func2 = remove_parentheses(func1), remove_parentheses(func2)
                cur_return.append(get_derivative_mult(func1, func2))
                statement = cur_return[-1][0][-1].step
            elif len(re.findall(div_pattern, statement)) == 1:
                span = re.search(div_pattern, statement).span()
                func1, func2 = list(map(lambda x: x.strip(), [statement[1: span[0]], statement[span[0] + 1 + 2: -1]]))
                func1, func2 = remove_parentheses(func1), remove_parentheses(func2)
                cur_return.append(get_derivative_div(func1, func2))
                statement = cur_return[-1][0][-1].step
            else:
                cur_return.append(get_derivative_full(statement))
                statement = cur_return[-1][0][-1].step
    except Exception as e:
        calc = smp.diff(sympy_function(statement_copy), symbol, der_num)
        cur_return.append([[Step(calc, smp_steps_en[0], smp_steps_en[0])], ''])
        statement = calc
    return cur_return
    # print(statement)
    # Difficult to test all then compare with smp, since some functions need 2 inputs
# get_derivative_div("2x + x", 'x^2')
py2tex(str(smp.diff('(8-x**3)**2')))
# print(classify('(2x + x) * (x)', 2)[0][-1].step)
# print(classify('(2x + x) ** 2', 2)[0][0][-1].step)