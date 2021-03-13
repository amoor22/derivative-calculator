import re
import sympy as smp
from pytexit import py2tex
from flask import Flask, render_template, redirect, request, url_for
possible_pow = ('**', '^')
min_plot, max_plot = -40, 40
# statement = "2.5x^2 + 4x + 5 + 5x"
types = ('statement', 'multiply', 'division', 'power')
symbol = 'x'
# steps
normal_steps_en = ['Simplify (if needed)', 'Using derivative rules', 'Final simplification (if needed)']
normal_steps_ar = ['التبسيط (إن وجد)', 'باستخدام قانون المشتقة', 'التبسيط النهائي (إن وجد)']
mult_steps_en = ['Calculate the derivative of both functions', 'Using the multiplication rule', 'Substituting in the rule', 'Adding values together']
mult_steps_ar = ['حساب المشتقة لكل دالة', 'باستخدام قانون مشتقة ضرب دالتين', 'التعويض في القانون', 'جمع الطرفين']
div_steps_en = ['Calculate the derivative of both functions', 'Using the division rule', 'Substituting in the rule', 'Adding values together', 'Final simplification']
div_steps_ar = ['حساب المشتقة لكل دالة', 'باستخدام قانون مشتقة قسمة دالتين', 'التعويض في القانون', 'طرح الطرف الثاني من الطرف الأول', 'التبسيط النهائي']
smp_steps_en = ['Calculate the derivative']
smp_steps_ar = ['حساب المشتقة (مباشرة)']
power_steps_en = ['Calculating the derivative of the bracket and its contents', 'Using the power rule', 'Substituting in the rule', 'Final simplification', 'Extra simplification']
power_steps_ar = ['حساب مشتقة القوس وما بداخل القوس', 'باستخدام قانون مشتقة الدالة الأسية', 'التعويض في القانون', 'التبسيط النهائي', 'التبسيط الإضافي']
rounding = 2
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
    statement = re.sub(r'\(', '', statement)
    statement = re.sub(r'\)', '', statement)
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
    steps.append(Step(smp.nsimplify(original_tex), normal_steps_en[0], normal_steps_ar[0], 1))
    steps.append(Step(new_statement, normal_steps_en[1], normal_steps_ar[1], 2))
    steps.append(Step(smp.nsimplify(new_statement), normal_steps_en[2], normal_steps_ar[2], 3))
    return [steps, types[0]]
def get_sympy_format_full(statement):
    statement = str(statement) 
    statement = re.sub(r'\s+', '', statement)
    statement = re.sub(r'\(', '', statement)
    statement = re.sub(r'\)', '', statement)
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
    func1 = get_sympy_format_full(func1)
    func2 = get_sympy_format_full(func2)
    steps.append(Step(r'$$f^{\prime}(x) = ' + f'{der1}' + r'\;  |  \;' + r'g^{\prime}(x) = ' + f'{der2}' + '$$', mult_steps_en[0], mult_steps_ar[0], latex=True))
    steps.append(Step(r'$$\frac{d}{dx} = f\left ( {x} \right ) \cdot g^{\prime}\left ( {x} \right ) + g\left ( {x} \right ) \cdot f^{\prime}\left ( {x} \right )$$', mult_steps_en[1], mult_steps_ar[1], latex=True))
    sum1 = smp.nsimplify(f'({der2}) * ({get_sympy_format_full(func1)})')
    sum2 = smp.nsimplify(f'({der1}) * ({get_sympy_format_full(func2)})')
    try:
        sum1_org, sum2_org = sum1, sum2
        sum1_text = py2tex(str(sum1), False, False).replace('$', '')
        sum2_text = py2tex(str(sum2), False, False).replace('$', '')
        print(sum1, sum2)
    except Exception as e:
        sum1_text, sum2_text = sum1_org, sum2_org
    steps.append(Step(r'$$\frac{d}{dx} = ' r'\left ('  f"{py2tex(func1, print_formula=False, print_latex=False).replace('$', '')}" r'\right )' r' \cdot ' r'\left (' + f"{py2tex(der2, print_formula=False, print_latex=False).replace('$', '')}" r'\right )' '+' r'\left (' f"{py2tex(func2, print_formula=False, print_latex=False).replace('$', '')}" r'\right )' r' \cdot ' r'\left (' f"{py2tex(der1, print_formula=False, print_latex=False).replace('$', '')}" r'\right )' '$$', mult_steps_en[2], mult_steps_ar[2], latex=True))
    steps.append(Step(r'$$' r'\frac{d}{dx} = ' r'\left (' f'{sum1_text}' r'\right )' '+' r'\left (' f'{sum2_text}' r'\right )' r'$$', mult_steps_en[2], mult_steps_ar[2], latex=True))
    final_sum = smp.nsimplify(sum1 + sum2)
    steps.append(Step(str(final_sum), mult_steps_en[3], mult_steps_ar[3]))
    return [steps, types[1]]

def get_derivative_div(func1, func2):
    steps = []
    der1 = str(get_derivative_full(func1)[0][-1].step)
    der2 = str(get_derivative_full(func2)[0][-1].step)
    func1 = get_sympy_format_full(func1)
    func2 = get_sympy_format_full(func2)
    print(func1, der1, func2, der2, 'fds')
    # s = r'$$f^{\prime}(x) = ' + f'{der1}' + '  |  ' + r'g^{\prime}(x) = ' + f'{der2}' + '$$'
    steps.append(Step(r'$$f^{\prime}(x) = ' + f'{der1}' + r'\; | \;' + r'g^{\prime}(x) = ' + f'{der2}' + '$$', div_steps_en[0], div_steps_ar[0], latex=True))
    steps.append(Step(r'$$\frac{d}{dx}=\frac{ g(x) \cdot f^{‎\prime}(x)-f(x)\cdot g^‎{\prime}(x)}{\left [ g(x) \right ]^2}$$', div_steps_en[1], div_steps_ar[1], latex=True))
    sum_num_first = smp.nsimplify(f'({get_sympy_format_full(func2)}) * ({der1})')
    sum_num_second = smp.nsimplify(f'({get_sympy_format_full(func1)}) * ({der2})')
    substitute = r'$$\frac{d}{dx}=\frac{' r'\left (' r' func2' r'\right )' r'\cdot \left ( der1 \right ) - \left ( func1 \right ) \cdot \left ( der2 \right ) }{\left [ func2 \right ]^2}$$'
    substitute = substitute.replace('func2', py2tex(get_sympy_format_full(func2)).replace('$', ''))
    substitute = substitute.replace('func1', py2tex(get_sympy_format_full(func1)).replace('$', ''))
    substitute = substitute.replace('der1', py2tex(der1).replace('$', ''))
    substitute = substitute.replace('der2', py2tex(der2).replace('$', ''))
    steps.append(Step(substitute, div_steps_en[2], div_steps_ar[2], latex=True))
    # b = r'$$\frac{d}{dx}=\frac{' r'\left (' f'{sum_num_first}' r'\right )' r'- \left (' f'{sum_num_second}' r'\right )' '}{\left [' f'{func2}' r'\right ]^2}$$'
    b = f'(({sum_num_first}) - ({sum_num_second})) / ({func2})**2'
    steps.append(Step(b, div_steps_en[3], div_steps_ar[3], latex=False))
    sum_num = smp.nsimplify(f'({sum_num_first}) - ({sum_num_second})')
    # final_sum = smp.nsimplify(f'({sum_num}) / (({get_sympy_format_full(func2)})**2)')
    steps.append(Step(f'({get_sympy_format_full(sum_num)})/({get_sympy_format_full(func2)})**2', div_steps_en[4], div_steps_ar[4]))
    print(steps[-1], 'fds')
    return [steps, types[2]]
def get_derivative_power(before_func, func, power):
    steps = []
    func = get_sympy_format_full(func)
    power = float(power)
    power_new = power - 1
    print(before_func, func, power)
    inside_der = str(get_derivative_full(func)[0][-1].step)
    # bracket_der = str(smp.nsimplify(f'{power} * ({func})'))
    before_times_power = round(float(power) * float(before_func), rounding)
    steps.append(Step(r'$$n \cdot \left[ f(x) \right]^{n-1} = ' + f'{py2tex(f"({before_func}) * ({power})", print_formula=False, print_latex=False).replace("$", "")}' r'\cdot' f"{py2tex(f'({func})**{power_new}').replace('$', '')}" + r'\;  |  \;' + r'f^{\prime}(x) = ' + f'{inside_der}' + '$$', power_steps_en[0], power_steps_ar[0], latex=True))
    steps.append(Step(r'$$' r'\frac{d}{dx} =' r'n \cdot \left[ f(x) \right]^{n-1}' r' \cdot ' r'f^{\prime}(x)' r'$$', power_steps_en[1], power_steps_ar[1], latex=True))
    new_func = f'({before_times_power})*({func})**{power_new}'
    steps.append(Step(r'$$' r'\frac{d}{dx} = ' f"{py2tex(f'({new_func})', print_latex=False, print_formula=False).replace('$', '')}" r' \cdot ' f"({py2tex(inside_der).replace('$', '')})" r'$$', power_steps_en[2], power_steps_ar[2], latex=True))
    inside_times_power = py2tex(str(smp.nsimplify(f'({before_times_power}) * ({inside_der})'))).replace('$', '')
    # steps.append(Step(r'$$' r'\frac{d}{dx} = ' f"({inside_times_power})" r' \cdot ' f"{py2tex(new_func, print_latex=False, print_formula=False).replace('$', '')}" r'$$', power_steps_en[3], power_steps_ar[3], latex=True))
    new_func = f'({inside_times_power})*({func})**{power_new}'
    # get sympy
    steps.append(Step(f"{new_func}" , power_steps_en[3], power_steps_ar[3], latex=False))
    # print(get_sympy_format_full(inside_times_power), 'dl')
    if power == 1:
        steps.append(Step(f"{inside_times_power}", power_steps_en[4], power_steps_ar[4], latex=False))
    # steps.append(Step(f"{final_sum}", power_steps_en[4], power_steps_ar[4], latex=False))
    # final_sum = (smp.simplify(f'({inside_times_power}) * ({new_func})'))
    print(steps[-1])
    return [steps, types[3]]
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
def classify(statement, der_num):
    statement = re.sub(r'\s+', '', statement)
    statement = statement.replace('^', '**')
    statement_copy = statement
    cur_return = []
    div_pattern = r'\)\/\('
    mult_pattern = r'\)\*\('
    power_patterns = [r'\)\^', r'\)\*\*']
    try:
        for i in range(der_num):
            statement = str(statement)
            statement_copy = str(statement_copy)
            if len(re.findall(power_patterns[0], statement)) == 1 or len(re.findall(power_patterns[1], statement)) == 1:
                for power in power_patterns:
                    if len(re.findall(power, statement)) == 1:
                        span = re.search(power, statement).span()
                        try:
                            before_func = float(statement.split('(')[0])
                            spn = re.search(r'\(', statement).span()
                        except Exception as e:
                            try:
                                search = re.search(mult_pattern, statement)
                                if search:
                                    before_func = float(remove_parentheses(statement[0: search.span()[0]]))
                                    spn = search.span()
                                else:
                                    before_func = 1
                                    spn = [1, -1]
                            except Exception as e:
                                spn = [1, -1]
                        func, power = list(map(lambda x: x.strip(), [statement[1: span[0]], statement[span[0] + 1 + 2: ]]))
                        func, power = remove_parentheses(func), remove_parentheses(power)
                        func = func[spn[0] -1: ]
                        cur_return.append(get_derivative_power(before_func, func, power))
                        statement = cur_return[-1][0][-1].step
            elif len(re.findall(mult_pattern, statement)) == 1:
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
        from traceback import format_exc
        print(format_exc())
        calc = smp.diff(sympy_function(statement_copy), symbol, der_num)
        cur_return.append([[Step(calc, smp_steps_en[0], smp_steps_ar[0])], ''])
        statement = calc
    try:
        x = list(range(min_plot, max_plot + 1))
        y = []
        to_remove = []
        for i in range(min_plot, max_plot + 1):
            value = smp.parse_expr(str(statement)).subs(symbol, i)
            if not re.search('[a-zA-Z]', str(value)):
                y.append(value)
            elif str(value) == 'zoo':
                y.append(r'Infinity')
            else:
                to_remove.append(i)
        for j in to_remove:
            x.remove(j)
    except Exception as e:
        x, y = None, None 
    return cur_return, [x, y]
    # print(statement)
    # Difficult to test all then compare with smp, since some functions need 2 inputs
# py2tex(get_sympy_format_full('(180.0*x**2.0-24.0*x**1+3)/(12.0*x**2.0)**2'))
# classify('(x**2+4)^2', 3)