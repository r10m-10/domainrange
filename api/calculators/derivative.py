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
        if type(left) == type(right) == float:
            return binary_ops[op](left, right)
        elif op in '+-*/':
            if type(left) == float:
                left = convert_to_str(left)
            if type(right) == float:
                right = convert_to_str(right)
            if op in '+-':
                flat = flatten((op, left, right), '+')
            else:
                flat = flatten((op, left, right), '*')
            terms = []
            for i in flat:
                terms.append(form_term(i))
            merged = merge_terms(terms, op)
            nodes = []
            for i in merged:
                nodes.append(form_node(i))
            final = rebuild(nodes, op)
            return final
        elif op == '^':
            if type(right) == float:
                if right == 1.0:
                    return left
                elif right == 0.0:
                    return 1.0
                elif type(left) == tuple and left[0] == '^':
                    if type(left[2]) == str and left[2].isalpha() == False:
                        exp = convert_to_str(float(left[2]) * right)
                        return ('^', left[1], exp)
                    else:
                        exp = ('*', left[2], convert_to_str(right))
                        return ('^', left[1], simplify(exp))
                else:
                    return (op, left, convert_to_str(right))
            elif type(left) == float:
                if left == 1.0:
                    return 1.0
                else:
                    return (op, convert_to_str(left), right)
            else:
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
            neg = ('*', '-1', right)
            neg = simplify(neg)
            new_node = ('+', left, neg)
            f = flatten(new_node, op)
            return f
        elif op=='*' and cur_op=='/':
            div = ('^', right, '-1')
            div = simplify(div)
            new_node = ('*', left, div)
            f = flatten(new_node, op)
            return f
        else:
            return [node]
    elif len(node)==2:
        return [node]

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
            elif (type(right)==tuple and right[0]=='*') or (type(left)==tuple and left[0]=='*'):
                coeff, base = extract_cb(node, '*')
                if coeff == None:
                    return (1.0, base, 1.0)
                else:
                    return (coeff, base, 1.0)
            else:
                return (1.0, node, 1.0)
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
    elif coeff == 0.0:
        return '0'
    elif exp == 0.0:
        return '1'
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
                    if left == '0':
                        left = i
                    elif i == '0':
                        left = left
                    else:
                        left = ('+', left, i)
            elif op in '*/':
                if (type(left) == str and left.isalpha() == False) or (type(i) == str and i.isalpha() == False):
                    if left == '0' or i == '0':
                        left = '0'
                    elif left == '1':
                        left = i
                    elif i == '1':
                        left = left
                    else:
                        left = ('*', left, i)
                else:
                    left = ('*', left, i)
        elif len(i)==3:
            cop, l, r = i
            if op in '+-':
                if type (l) == str and l.isalpha()==False and float(l)<0:
                    if l == '-1':
                        if left == '0':
                            left = i
                        else:
                            left = ('-', left, r)
                    else:
                        left = ('-', left, (cop, l[1:], r))
                else:
                    if left == '0':
                        left = i
                    else:
                        left = ('+', left, i)
            elif op in '*/':
                if left == '0':
                    left = '0'
                elif left == '1':
                    left = i
                else:
                    left = ('*', left, i)
        elif len(i)==2:
            if op in '+-':
                left = ('+', left, i)
            elif op in '*/':
                if left == '0':
                    left = '0'
                elif left == '1':
                    left = i
                else:
                    left = ('*', left, i)
    if type(left) == str and left.isalpha() == False:
        return float(left)
    else:
        return left

def extract_cb(node, op):
    flat = flatten(node, op)
    terms = []
    for i in flat:
        terms.append(form_term(i))
    merged = merge_terms(terms, op)
    nodes = []
    for i in merged:
        nodes.append(form_node(i))
    coeff = None
    base = []
    for i in nodes:
        try:
            coeff = float(i)
        except (ValueError, TypeError):
            base.append(i)
    base = rebuild(base, op)
    return coeff, base

def differentiate(exp):
    tokens = tokenize(exp)
    node = parse_add(tokens)[0]
    sim_node = simplify(node)
    der = differentiate_unsim(sim_node)
    final = simplify(der)
    return final

#op = '+'
#flat = flatten(('-', ('*', '2', 'x'), 'x'), op)
#print(flat)
#terms = []
#for i in flat:
#    terms.append(form_term(i))
#print(terms)
#merged = merge_terms(terms, op)
#print(merged)
#nodes = []
#for i in merged:
#    nodes.append(form_node(i))
#print(nodes)
#final = rebuild(nodes, op)
#print(final)

test_exprs = [
    "x^2",              # expect: 2x
    "x^3",              # expect: 3x^2
    "5x^2",             # expect: 10x
    "x^2 - x",          # expect: 2x - 1
    "x^2 + 3x - 5",     # expect: 2x + 3

    "sin(x)",           # expect: cos(x)
    "cos(x)",           # expect: -sin(x)  (or equivalent with -1 coefficient)
    "tan(x)",           # expect: sec(x)^2
    "sec(x)",           # expect: sec(x)*tan(x)

    "x - sin(x)",       # expect: 1 - cos(x)  -- exercises differentiate_unsim's '-' handling + final simplify

    "x*sin(x)",         # expect: sin(x) + x*cos(x)  -- product rule, two different function bases
    "sin(x)*cos(x)",    # expect: cos(x)^2 - sin(x)^2  -- product rule, distinct trig bases
    "x^2*sin(x)",       # expect: 2x*sin(x) + x^2*cos(x)
    "(x^2)(3x)",        # expect: 9x^2  -- product rule where both sides are powers of same base;
                         # low confidence this fully re-collapses through merge_terms after
                         # differentiate_unsim, worth checking closely

    "sin(x)/x",         # expect: (x*cos(x) - sin(x))/x^2  -- quotient rule
    "x/sin(x)",         # expect: quotient rule, mirrored -- check sign/shape consistency vs above

    "sin(x^2)",         # expect: 2x*cos(x^2)  -- chain rule, non-constant exponent inside
    "sqrt(x)",          # expect: 1/(2*sqrt(x))
    "x*sqrt(x)",        # expect: mathematically (3/2)*sqrt(x); LOW confidence the pipeline
                         # fully collapses this -- sqrt(x) is a 2-tuple base, exponent arithmetic
                         # across two sqrt(x) factors isn't something we've tested this session

    "ln(x)",            # expect: 1/x
    "ln(x^2)",          # expect: 2/x  -- chain rule then simplification should cancel the x^2/x down
    "log(x)",           # expect: 1/(x*ln(10))

    "1/x",              # expect: -1/x^2, or per your locked decision: -x^-2 (stays as ^, not /)
    "1/x^2",            # expect: -2x^-3 (stays as ^, not /)

    "x^x",              # expect: x^x * (ln(x) + 1)  -- variable base AND variable exponent,
                         # general power rule branch in differentiate_unsim

    "x^(2x)",           # expect: symbolic-exponent chain rule case, related to the merge_terms
                         # x^(2x)*x^x test from earlier -- but this is differentiation, not
                         # just multiplication, so it's a genuinely new code path

    "2^x",              # expect: 2^x * ln(2)  -- constant base, variable exponent; tests whether
                         # the left'/left term (which should multiply out to 0 since left'=0)
                         # actually vanishes rather than leaving a dangling 0/2 or similar

    "arcsin(x)",        # expect: 1/sqrt(1 - x^2)
    "arctan(x)",        # expect: 1/(1 + x^2)
]

for i in test_exprs:
    print(differentiate(i))