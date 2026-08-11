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

def convert_to_str(num):
    if math.modf(num)[0] == 0:
        return str(int(num))
    else:
        return str(num)

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
        if op in '+-*/':
            if op in '+-':
                pass
        elif type(left) == type(right) == float:
            return binary_ops[op](left, right)
        elif (type(left) == str or type(left) == tuple) and type(right) == float:
            if math.modf(right)[0] == 0:
                right = int(right)
            if right == 1:
                if op in '/^':
                    return left
                else:
                    return (op, left, str(right))
            elif right == 0:
                if op == '^':
                    return 1.0
                elif op in '-':
                    return left
            else:
                return (op, left, str(right))
        elif type(left) == float and (type(right) == str or type(right) == tuple):
            if math.modf(left)[0] == 0:
                left = int(left)
            if left == 1:
                if op == '^':
                    return 1.0
                else:
                    return (op, str(left), right)
            elif left == 0:
                if op in '/':
                    return 0.0
                elif op == '-':
                    return ('*', '-1', right)
            else:
                return (op, str(left), right)
        elif (type(left) == str or type(left) == tuple) and (type(right) == str or type(right) == tuple):
            return (op, left, right)
    elif len(node)==2:
        op, child = node
        child = simplify_initial(child)
        if type(child)==float:
            child = convert_to_str(child)
        return (op, child)

def simplify(node):
    initial = simplify_initial(node)
    if type(initial)==float:
        return convert_to_str(initial)
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
        elif op=='+' and cur_op=='-':
            new_node = ('+', left, ('*', '-1', right))
            f = flatten(new_node, op)
            return f
        elif op=='*' and cur_op=='/':
            new_node = ('*', left, ('^', right, '-1'))
            f = flatten(new_node, op)
            return f
        else:
            return [node]
    elif len(node)==2:
        return [node]

def differentiate(exp):
    tokens = tokenize(exp)
    node = parse_add(tokens)[0]
    der = differentiate_unsim(node)
    sim = simplify(der)
    return node

test_exprs = [
    "2x^2",
    "3x",
    "5x^3",
    "x^2 + x",
    "x^2 + 2x + 3x^2",
    "2x + 3x",
    "2*3*x",
    "x*2*3",
    "(2x)(3x)",
    "5*x",
    "7",
    "x*7",
    "sin(x)*2",
    "2*sin(x)*3",
    "x^2/x",
    "x/2",
    "2/x",
    "x^3",
    "0*x",
    "1*x",
    "x + 0",
    "x*1*y",
    "-2x",
    "x - 3x",
]

def form_term(node):
    if type(node)==str:
        if node.isalpha():
            return (1.0, node, 1.0)
        else:
            return (float(node), None, None)
    elif len(node)==3:
        op, left, right = node
        if op=='*':
            if type(left)==str and left.isalpha()==False:
                if type(right)==tuple and len(right)==3 and right[0]=='^' and type(right[1])==str and right[1].isalpha():
                    try:
                        return (float(left), right[1], float(right[2]))
                    except (ValueError, TypeError):
                        return (float(left), right[1], right[2])
                else:
                    return (float(left), right, 1.0)
            elif type(right)==str and right.isalpha()==False:
                if type(left)==tuple and len(left)==3 and left[0]=='^' and type(left[1])==str and left[1].isalpha():
                    try:
                        return (float(right), left[1], float(left[2]))
                    except (ValueError, TypeError):
                        return (float(right), left[1], left[2])
                else:
                    return (float(right), left, 1.0)
        elif op=='^':
            try:
                return (1.0, left, float(right))
            except (ValueError, TypeError):
                return (1.0, left, right)
        else:
            return (1.0, node, 1.0)
    elif len(node)==2:
        return (1.0, node, 1.0)

def merge_terms(terms, op):
    groups = {}
    for i in terms:
        if op in '+-':
            key = (i[1], i[2])
        else:
            key = (i[1])
        if key in groups:
            if op in '+-':
                coeff = groups[key][0] + i[0]
                groups[key] = (coeff, i[1], i[2])
            else:
                if key == None:
                    coeff = groups[key][0] * i[0]
                    groups[key] = (coeff, i[1], i[2])
                else:
                    if type(groups[key][2])==type(i[2])==float:
                        exp = groups[key][2] + i[2]
                        groups[key] = (i[0], i[1], exp)
                    else:
                        l, r = groups[key][2], i[2]
                        if type(l)==float:
                            l = convert_to_str(l)
                        if type(r)==float:
                            r = convert_to_str(r)
                        exp = simplify_initial(('+', l, r))
                        groups[key] = (i[0], i[1], exp)
        else:
            groups[key] = i
    return list(groups.values())

def form_node(merged_term):
    coeff, base, exp = merged_term
    if base == exp == None:
        return convert_to_str(coeff)
    elif coeff == exp == 1.0:
        return base
    elif coeff == 1.0:
        if type(exp)==float:
            exp = convert_to_str(exp)
        return ('^', base, exp)
    elif exp == 1.0:
        coeff = convert_to_str(coeff)
        return ('*', coeff, base)
    else:
        coeff = convert_to_str(coeff)
        if type(exp)==float:
            exp = convert_to_str(exp)
        return ('*', coeff, ('^', base, exp))

def rebuild(nodes, op):
    left = nodes[0]
    for i in nodes[1:]:
        if type(i) == str:
            if op in '+-':
                if i[0] == '-':
                    left = ('-', left, i[1:])
                else:
                    left = ('+', left, i)
            elif op in '*/':
                left = ('*', left, i)
        elif len(i)==3:
            cop, l, r = i
            if op in '+-':
                if type (l) == str and l.isalpha()==False and float(l)<0:
                    left = ('-', left, (cop, l[1:], r))
                else:
                    left = ('+', left, i)
            elif op in '*/':
                left = ('*', left, i)
        elif len(i)==2:
            if op in '+-':
                left = ('+', left, i)
            elif op in '*/':
                left = ('*', left, i)
    return left

node = differentiate('3x^2 + 2 + 1 + 6x^2')
print(node)
fl = (flatten(node, '+'))
print(fl)
terms = []
for i in fl:
    terms.append(form_term(i))
print(terms)
merged = merge_terms(terms, '+')
nodes = []
for i in merged:
    nodes.append(form_node(i))
print(nodes)
node = rebuild(nodes, '+')
print(node)