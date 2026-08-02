import math
from ..ast.tokenizer import tokenize
from ..ast.parser import parse_add
from .domain import contains_var

binary_ops = {
    '+': lambda a, b: a + b, 
    '-': lambda a, b: a - b, 
    '*': lambda a, b: a * b, 
    '/': lambda a, b: a / b, 
    '^': lambda a, b: a**b
}
unary_ops = {
    'sqrt': math.sqrt,
    'log': math.log10,
    'ln': math.log,
    'abs': math.fabs,
    'frac': lambda v: v - math.floor(v),
    'gif': math.floor,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'arcsin': math.asin,
    'arccos': math.acos,
    'arctan': math.atan,
    'sec': lambda v: 1 / math.cos(v),
    'cosec': lambda v: 1 / math.sin(v),
    'arcsec': lambda v: math.acos(1 / v),
    'arccosec': lambda v: math.asin(1 / v),
}

def differentiate_unsim(node):
    if type(node)==str:
        if node.isdigit() or '.' in node or (node[0] == '-' and node[1:].isdigit()) or (node[0]=='-' and node[1] =='.'):
            return '0'
        elif node.isalpha():
            return '1'
    elif len(node)==3:
        op, left, right = node
        if op in '+-':
            return (op, differentiate_unsim(left), differentiate_unsim(right))
        elif op == '*':
            return ('+', ('*', differentiate_unsim(left), right), ('*', differentiate_unsim(right), left))
        elif op == '/':
            return ('/', ('-', ('*', differentiate_unsim(left), right), ('*', differentiate_unsim(right), left)), ('^', right, '2'))
        elif op == '^':
            if contains_var(right)==False:
                return ('*', ('*', right, ('^', left, ('-', right, '1'))), differentiate_unsim(left))
            else:
                return ('*', ('^', left, right), ('+', ('*', differentiate_unsim(right), ('ln', left)), ('*', right, ('/', differentiate_unsim(left), left))))
    elif len(node)==2:
        op, child = node
        if op == 'sin':
            return ('*', ('cos', child), differentiate_unsim(child))
        elif op == 'cos':
            return ('*', ('*', '-1', ('sin', child)), differentiate_unsim(child))
        elif op == 'tan':
            return ('*', ('^', ('sec', child), '2'), differentiate_unsim(child))
        elif op == 'cosec':
            return ('*', ('*', ('*', '-1', ('cosec', child)), ('cot', child)), differentiate_unsim(child))
        elif op == 'sec':
            return ('*', ('*', ('sec', child), ('tan', child)), differentiate_unsim(child))
        elif op == 'cot':
            return ('*', ('*', '-1', ('^', ('cosec', child), '2')), differentiate_unsim(child))
        elif op == 'arcsin':
            return ('*', ('/', '1', ('sqrt', ('-', '1', ('^', child, '2')))), differentiate_unsim(child))
        elif op == 'arccos':
            return ('*', ('/', '-1', ('sqrt', ('-', '1', ('^', child, '2')))), differentiate_unsim(child))
        elif op == 'arctan':
            return ('*', ('/', '1', ('+', '1', ('^', child, '2'))), differentiate_unsim(child))
        elif op == 'arccosec':
            return ('*', ('/', '-1', ('*', ('abs', child), ('-', ('^', child, '2'), '1'))), differentiate_unsim(child))
        elif op == 'arcsec':
            return ('*', ('/', '1', ('*', ('abs', child), ('-', ('^', child, '2'), '1'))), differentiate_unsim(child))
        elif op == 'arccot':
            return ('*', ('/', '-1', ('+', '1', ('^', child, '2'))), differentiate_unsim(child))
        elif op == 'sqrt':
            return ('/', '1', ('*', '2', ('sqrt', child)))
        elif op == 'ln':
            return ('*', ('/', '1', child), differentiate_unsim(child))
        elif op == 'log':
            return ('*', ('/', '1', ('*', child, ('ln', '10'))), differentiate_unsim(child))

def simplify_initial(node):
    if type(node) == str:
        if node.isalpha():
            return node
        else:
            return float(node)
    elif len(node) == 3:
        op, left, right = node
        left = simplify_initial(left)
        right = simplify_initial(right)
        if type(left) == type(right) == float:
            return binary_ops[op](left, right)
        elif (type(left) == str or type(left) == tuple) and type(right) == float:
            if math.modf(right)[0] == 0:
                right = int(right)
            if right == 1:
                if op in '*/^':
                    return left
                else:
                    return (op, left, str(right))
            elif right == 0:
                if op == '*':
                    return 0.0
                elif op == '^':
                    return 1.0
                elif op in '+-':
                    return left
            else:
                return (op, left, str(right))
        elif type(left) == float and (type(right) == str or type(right) == tuple):
            if math.modf(left)[0] == 0:
                left = int(left)
            if left == 1:
                if op == '*':
                    return right
                elif op == '^':
                    return 1.0
                else:
                    return (op, str(left), right)
            elif left == 0:
                if op in '*/':
                    return 0.0
                elif op == '+':
                    return right
                elif op == '-':
                    return ('*', '-1', right)
            else:
                return (op, str(left), right)
        elif (type(left) == str or type(left) == tuple) and (type(right) == str or type(right) == tuple):
            return (op, left, right)

def simplify(node):
    initial = simplify_initial(node)
    if type(initial)==float:
        if math.modf(initial)[0] == 0:
            return str(int(initial))
        else:
            return str(initial)
    else:
        return initial

def flatten(node, op):
    if type(node) == str:
        return [node]
    elif len(node)==3:
        cur_op, left, right = node
        if cur_op == op:
            left = flatten(left, op)
            right = flatten(right, op)
            left.extend(right)
            return left
        else:
            return [node]
    elif len(node)==2:
        return [node]

def differentiate(exp):
    tokens = tokenize(exp)
    node = parse_add(tokens)[0]
    der = differentiate_unsim(node)
    sim = simplify(der)
    return sim

def collect_and_reduce(flat, op):
    nums = []
    symbols = []
    for i in flat:
        if type(i) == str:
            try:
                nums.append(float(i))
            except ValueError:
                symbols.append(i)
        else:
            symbols.append(i)

    if len(nums) == 0:
        calc = None
    else:
        calc = nums[0]
        for i in nums[1:]:
            calc = binary_ops[op](calc, i)
        if math.modf(calc)[0] == 0:
            calc = str(int(calc))
        else:
            calc = str(calc)
    return calc, symbols

def rebuild(combined_num, symbols, op):
    if len(symbols) == 0 and combined_num!=None:
        return float(combined_num)
    elif len(symbols) == 1:
        if combined_num==None or (combined_num=='1' and op=='*') or (combined_num=='0' and op=='+'):
            return symbols[0]
        elif combined_num=='0' and op=='*':
            return 0.0
        else:
            return (op, symbols[0], combined_num)
    else:
        left = symbols[0]
        for i in symbols[1:]:
            left = (op, left, i)
        if combined_num==None or (combined_num=='1' and op=='*') or (combined_num=='0' and op=='+'):
            return left
        elif combined_num=='0' and op=='*':
            return 0.0
        else:
            return (op, left, combined_num)

der = differentiate('2x^2')
flat = flatten(der, '*')
num, sym = collect_and_reduce(flat, '*')
print(rebuild('0', ['x'], '*'))