from ..ast.tokenizer import tokenize
from ..ast.parser import parse_add
from .domain import contains_var

def der_pow(term:str, var):
    i = term.find('^')
    o_pow = float(term[i+1:])
    if o_pow.is_integer():
        o_pow = int(o_pow)
    n_pow = f"^{o_pow-1}"
    if n_pow == '^1' or n_pow == '^1.0':
        n_pow = ''
    if term[:i-1] == '':
        der = f"{o_pow}{var}{n_pow}"
    else:
        const = float(term[:i-1]) * o_pow
        if const.is_integer():
            const = int(const)
        der = f"{const}{var}{n_pow}"
    return der

def der_linear(term:str):
    if term.isdigit():
        der = '0'
    else:
        cons = term[:len(term)-1]
        if cons == '':
            der = '1'
        else:
            der = cons
    return der

def der_exp(term:str, var):
    if term[term.find('^')-1] == 'e':
        der = f"e^{var}"
    elif term[term.find('^')-1].isdigit():
        const = term[term.find('^')-1]
        der = f"{term}ln({const})"
    return der

def der_trig(term, var):
    if 'sin' in term:
        c = term[:term.find('s')]
        der = f"{c}cos({var})"
    elif 'cosec' in term:
        c = term[:term.find('c')]
        der = f"-{c}cosec({var})cot({var})"
    elif 'cos' in term:
        c = term[:term.find('c')]
        der = f"-{c}sin({var})"
    elif 'tan' in term:
        c = term[:term.find('t')]
        der = f"{c}(sec({var}))^2"
    elif 'cot' in term:
        c = term[:term.find('c')]
        der = f"-{c}(cosec({var}))^2"
    elif 'sec' in term:
        c = term[:term.find('s')]
        der = f"{c}sec({var})tan({var})"
    return der

def der_itrig(term, var):
    c = term[:term.find('a')]
    if 'arcsin' in term:
        if c=='':
            der = f"1/(1-{var}^2)^1/2"
        else:
            der = f"{c}/(1-{var}^2)^1/2"
    elif 'arccosec' in term:
        if c=='':
            der = f"-1/(|{var}|({var}^2-1))"
        else:
            der = f"-{c}/(|{var}|({var}^2-1))"
    elif 'arccos' in term:
        if c=='':
            der = f"-1/(1-{var}^2)^1/2"
        else:
            der = f"-{c}/(1-{var}^2)^1/2"
    elif 'arctan' in term:
        if c=='':
            der = f"1/(1+{var}^2)"
        else:
            der = f"{c}/(1+{var}^2)"
    elif 'arccot' in term:
        if c=='':
            der = f"-1/(1+{var}^2)"
        else:
            der = f"-{c}/(1+{var}^2)"
    elif 'arcsec' in term:
        if c=='':
            der = f"1/(|{var}|({var}^2-1))"
        else:
            der = f"{c}/(|{var}|({var}^2-1))"
    return der

def der_log(term, var):
    if 'ln' in term:
        der = f"1/{var}"
    else:
        base = term[term.find('g')+1 : term.find('(')].strip()
        if base == 'e':
            der = f"1/{var}"
        else:
            der = f"1/({var}ln({base}))"
    return der

def der_varexp(u, v):
    d = f"({v})*(ln({u}))"
    der = differentiate(d)
    return der

def differentiate(node):
    if type(node)==str:
        if node.isdigit() or '.' in node or (node[0] == '-' and node[1:].isdigit()) or (node[0]=='-' and node[1] =='.'):
            return '0'
        elif node.isalpha() or (node[0] == '-' and node[1:].isalpha()):
            return '1'
    elif len(node)==3:
        op, left, right = node
        if op in '+-':
            return (op, differentiate(left), differentiate(right))
        elif op == '*':
            return ('+', ('*', differentiate(left), right), ('*', differentiate(right), left))
        elif op == '/':
            return ('/', ('-', ('*', differentiate(left), right), ('*', differentiate(right), left)), ('^', right, '2'))
        elif op == '^':
            if contains_var(right)==False:
                return ('*', ('*', right, ('^', left, ('-', right, '1'))), differentiate(left))
            else:
                return ('*', ('^', left, right), ('+', ('*', differentiate(right), ('ln', left)), ('*', right, ('/', differentiate(left), left))))
    elif len(node)==2:
        op, child = node
        if op == 'sqrt':
            return ('/', '1', ('*', '2', ('sqrt', child)))
        elif op == 'sin':
            return ('*', ('cos', child), differentiate(child))
        elif op == 'cos':
            return ('*', ('*', '-1', ('sin', child)), differentiate(child))
        elif op == 'tan':
            return ('*', ('^', ('sec', child), '2'), differentiate(child))
        elif op == 'cosec':
            return ('*', ('*', ('*', '-1', ('cosec', child)), ('cot', child)), differentiate(child))
        elif op == 'sec':
            return ('*', ('*', ('sec', child), ('tan', child)), differentiate(child))
        elif op == 'cot':
            return ('*', ('*', '-1', ('^', ('cosec', child), '2')), differentiate(child))