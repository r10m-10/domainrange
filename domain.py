import math
from tokenizer import tokenizer
from parser import parse_add
from tree import render_expression

binary_ops = {'+': lambda a, b: a + b, '-': lambda a, b: a - b, '*': lambda a, b: a * b, '/': lambda a, b: a / b, '^': lambda a, b: a**b}
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

comparison_ops = {
    '>':  lambda a, b: a > b,
    '>=': lambda a, b: a >= b,
    '<':  lambda a, b: a < b,
    '<=': lambda a, b: a <= b,
    '!=': lambda a, b: a != b,
    '==': lambda a, b: a == b,
}

def get_constraints(node):
    constraints = []
    if type(node) == str:
        return constraints
    elif len(node) == 2:
        op, child = node
        if contains_var(child):
            child_constraints = get_constraints(child)
            constraints.extend(child_constraints)
            if op in ['sqrt', 'log', 'ln', 'arcsin', 'arccos', 'arcsec', 'arccosec', 'tan', 'sec', 'cosec']:
                if op == 'sqrt':
                    op_constraint = (child, '>=', 0)
                    constraints.append(op_constraint)
                elif op in ['log', 'ln']:
                    op_constraint = (child, '>', 0)
                    constraints.append(op_constraint)
                elif op in ['arcsin', 'arccos']:
                    op_constraint = [(child, '>=', -1), (child, '<=', 1)]
                    constraints.append(op_constraint)
                elif op in ['arcsec', 'arccosec']:
                    op_constraint = [(child, '<=', -1), (child, '>=', 1)]
                    constraints.append(op_constraint)
                elif op in ['tan', 'sec']:
                    op_constraint = (child, 'excludes_periodic', math.pi/2, math.pi)
                    constraints.append(op_constraint)
                elif op == 'cosec':
                    op_constraint = (child, 'excludes_periodic', 0, math.pi)
                    constraints.append(op_constraint)
        return constraints
    elif len(node) == 3:
        op, left, right = node
        left_constraints = get_constraints(left)
        right_constraints = get_constraints(right)
        constraints.extend(left_constraints)
        constraints.extend(right_constraints)
        if op == '/':
            if contains_var(right):
                op_constraint = (right, '!=', 0)
                constraints.append(op_constraint)
        return constraints

def contains_var(node):
    if type(node) == str:
        if node.isdigit() or '.' in node or node[0]=='-' and node[1].isdigit() or node[0]=='-' and node[1] =='.':
            return False
        else:
            return True
    elif len(node) == 3:
        op, left, right = node
        l_x, r_x = contains_var(left), contains_var(right)
        return l_x or r_x
    elif len(node) == 2:
        op, child = node
        child_x = contains_var(child)
        return child_x

def evaluate_at(node, x_val):
    if type(node)==str:
        if node.isalpha():
            return x_val
        else:
            return float(node)
    elif len(node) == 3:
        op, left, right = node
        left = evaluate_at(left, x_val)
        right = evaluate_at(right, x_val)
        num = binary_ops[op](left, right)
        return num
    elif len(node) == 2:
        op, child = node
        child = evaluate_at(child, x_val)
        num = unary_ops[op](child)
        return num

def flip_inequality(inequality):
    if inequality=='>':
        inequality='<'
    elif inequality=='>=':
        inequality='<='
    elif inequality=='<':
        inequality='>'
    elif inequality=='<=':
        inequality='>='
    return inequality

def solve_constraints(constraints):
    for i in constraints:
        if type(i)==tuple:
            subtree, inequality, rhs = i

def solve_node(node, inequality, rhs):
    if type(node) == str:
        var = contains_var(node)
        if var:
            if node[0] == '-':
                inequality = flip_inequality(inequality)
                node = node[1:]
                rhs = -float(rhs)
            return node, inequality, rhs
    elif len(node) == 3:
            op, left, right = node
            l_var, r_var = contains_var(left), contains_var(right)
            if l_var==True and r_var==False:
                r_val = evaluate_at(right)
                if op == '+':
                    rhs = float(rhs) - float(r_val)
                    l_val, inequality, rhs = solve_node(left, inequality, rhs)
                    return l_val, inequality, rhs
                elif op == '*':
                    if float(r_val)<0:
                        inequality = flip_inequality(inequality)
                    rhs = float(rhs)/float(r_val)
                    l_val, inequality, rhs = solve_node(left, inequality, rhs)
                    return l_val, inequality, rhs
            elif l_var==False and r_var==True:
                l_val = evaluate_at(left)
                if op == '+':
                    rhs = float(rhs) - float(l_val)
                    r_val, inequality, rhs = solve_node(right, inequality, rhs)
                    return r_val, inequality, rhs
                elif op == '*':
                    if str(l_val)[0] == '-':
                        inequality = flip_inequality(inequality)
                    rhs = float(rhs)/float(l_val)
                    r_val, inequality, rhs = solve_node(right, inequality, rhs)
                    return r_val, inequality, rhs
            elif l_var==False and r_var==False:
                val = evaluate_at(node)
                return val, inequality, rhs

def bisect(node, lo, hi, tol=1e-9):
    while (hi-lo)>tol:
        x = (lo+hi)/2
        lo_val = evaluate_at(node, lo)
        hi_val = evaluate_at(node, hi)
        val = evaluate_at(node, x)
        if lo_val*val < 0:
            lo, hi = lo, x
        elif hi_val*val < 0:
            lo, hi = x, hi
    return x

def get_critical_points(node, lo, hi, step):
    critical_points = []
    x = lo
    prev_x = None
    prev_val = None

    while x<= hi:
        try:
            val = evaluate_at(node, x)
        except (ValueError, ZeroDivisionError):
            val = None
        
        if prev_val!=None and val!=None and prev_val*val < 0:
            critical_points.append(round(bisect(node, prev_x, x), 6))
        elif val == 0:
            critical_points.append(x)
        elif x!=lo and prev_val==None and val!=None:
            critical_points.append(round(bisect(node, prev_x, x), 6))
        elif x!=lo and prev_val!=None and val==None:
            critical_points.append(round(bisect(node, prev_x, x), 6))
        prev_x, prev_val = x, val
        x+=step
    return sorted(critical_points)

def test_domain_intervals(node, inequality, rhs, critical_points):
    critical_points = sorted(critical_points)
    intervals = []
    prev_pt = None
    for i in critical_points:
        if len(critical_points) == 1:
            val_l = evaluate_at(node, i-1)
            val_r = evaluate_at(node, i+1)
            val = evaluate_at(node, i)
            if comparison_ops[inequality](val, rhs):
                if comparison_ops[inequality](val_r, rhs)==False and comparison_ops[inequality](val_l, rhs)==False:
                    intervals.append("{"+str(i)+"}")
                elif comparison_ops[inequality](val_r, rhs)==True and comparison_ops[inequality](val_l, rhs)==True:
                    intervals.append("R")
                elif comparison_ops[inequality](val_l, rhs):
                    intervals.append(f"(-∞, {i}]")
                elif comparison_ops[inequality](val_r, rhs):
                    intervals.append(f"[{i}, ∞)")
            else:
                if comparison_ops[inequality](val_r, rhs)==False and comparison_ops[inequality](val_l, rhs)==False:
                    intervals.append("Φ")
                elif comparison_ops[inequality](val_r, rhs)==True and comparison_ops[inequality](val_l, rhs)==True:
                    intervals.append("R-"+"{"+str(i)+"}")                
                elif comparison_ops[inequality](val_l, rhs):
                    intervals.append(f"(-∞, {i})")
                elif comparison_ops[inequality](val_r, rhs):
                    intervals.append(f"({i}, ∞)")
        elif critical_points.index(i) == 0:
            prev_pt = i
            val = evaluate_at(node, i-1)
            if comparison_ops[inequality](val, rhs):
                incl_val = evaluate_at(node, i)
                if comparison_ops[inequality](incl_val, rhs):
                    intervals.append(f"(-∞, {i}]")    
                else:
                    intervals.append(f"(-∞, {i})")
        elif critical_points.index(i) == len(critical_points)-1:
            prev_pt = i
            val = evaluate_at(node, i+1)
            if comparison_ops[inequality](val, rhs):
                incl_val = evaluate_at(node, i)
                if comparison_ops[inequality](incl_val, rhs):
                    intervals.append(f"[{i}, ∞)")
                else:
                    intervals.append(f"({i}, ∞)")
        else:
            val = evaluate_at(node, (prev_pt+i)/2)
            prev_pt = i
            if comparison_ops[inequality](val, rhs):
                incl_val_lo = evaluate_at(node, prev_pt)
                incl_val_hi = evaluate_at(node, i)
                if comparison_ops[inequality](incl_val_lo, rhs)==False and comparison_ops[inequality](incl_val_hi, rhs)==False:
                    intervals.append(f"({prev_pt}, {i})")
                elif comparison_ops[inequality](incl_val_lo, rhs)==True and comparison_ops[inequality](incl_val_hi, rhs)==True:
                    intervals.append(f"[{prev_pt}, {i}]")
                elif comparison_ops[inequality](incl_val_lo, rhs):
                    intervals.append(f"[{prev_pt}, {i})")
                elif comparison_ops[inequality](incl_val_hi, rhs):
                    intervals.append(f"({prev_pt}, {i}]")
    return intervals

node = (('-', 'x', '3'))  #(x - 3)
critical_points = get_critical_points(node, -10, 10, 0.1)
print (critical_points)
print(test_domain_intervals(node, '!=', 0, critical_points))