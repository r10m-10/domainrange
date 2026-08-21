import math

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
    'frac': lambda v: math.modf(v)[0],
    'gif': math.floor,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'arcsin': math.asin,
    'arccos': math.acos,
    'arctan': math.atan,
    'sec': lambda v: 1 / math.cos(v),
    'cosec': lambda v: 1 / math.sin(v),
    'cot': lambda v: 1 / math.tan(v),
    'arcsec': lambda v: math.acos(1 / v),
    'arccosec': lambda v: math.asin(1 / v),
    'arccot': lambda v: math.atan(1 / v)
}

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

def pow_to_div(node):
    if type(node) == str:
        return node
    elif len(node) == 3:
        op, left, right = node
        left = pow_to_div(left)
        right = pow_to_div(right)
        if op == '*':
            if left[0] == right[0] == '/':
                try:
                    numr = float(left[1]) * float(right[1])
                    return ('/', convert_to_str(numr), ('*', left[2], right[2]))
                except (ValueError, TypeError):
                    if left[1] == '1':
                        return ('/', right[1], ('*', left[2], right[2]))
                    elif right[1] == '1':
                        return ('/', left[1], ('*', left[2], right[2]))
                    else:
                        return ('/', ('*', left[1], right[1]), ('*', left[2], right[2]))
            elif left[0] == '/':
                try:
                    numr = float(left[1]) * float(right)
                    return ('/', convert_to_str(numr), left[2])
                except (ValueError ,TypeError):
                    if left[1] == '1':
                        return ('/', right, left[2])
                    elif right == '1':
                        return ('/', left[1], left[2])
                    else:
                        return ('/', ('*', left[1], right), left[2])
            elif right[0] == '/':
                try:
                    numr = float(right[1]) * float(left)
                    return ('/', convert_to_str(numr), right[2])
                except (ValueError ,TypeError):
                    if right[1] == '1':
                        return ('/', left, right[2])
                    elif left == '1':
                        return ('/', right[1], right[2])
                    else:
                        return ('/', ('*', right[1], left), right[2])
            else:
                return (op, left, right)
        elif op == '^' and type(right) == str and right[0] == '-':
            denomi = simplify_initial((op, left, right[1:]))
            return ('/', '1', denomi)
        else:
            return (op, left, right)
    elif len(node) == 2:
        op, child = node
        child = pow_to_div(child)
        return (op, child)

def float_to_frac(num: str):
    if '.' not in num:
        return num
    frac_num = num[num.find('.')+1:]
    x = len(str(frac_num))
    numr = int(float(num) * 10**x)
    denomi = 10**x
    hcf = math.gcd(numr, denomi)
    numr //= hcf
    denomi //= hcf
    return ('/', str(numr), str(denomi))

def simplify(node):
    initial = simplify_initial(node)
    if type(initial)==float:
        return convert_to_str(initial)
    else:
        return initial