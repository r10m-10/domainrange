import math
from ..ast.tokenizer import tokenize
from ..ast.parser import parse_add
from .simplify import simplify, pow_to_div, float_to_frac, convert_to_str

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
    'cot': lambda v: 1 / math.tan(v),
    'arcsec': lambda v: math.acos(1 / v),
    'arccosec': lambda v: math.asin(1 / v),
    'arccot': lambda v: math.atan(1 / v)
}
comparison_ops = {
    '>':  lambda a, b: a > b,
    '>=': lambda a, b: a >= b,
    '<':  lambda a, b: a < b,
    '<=': lambda a, b: a <= b,
    '!=': lambda a, b: a != b,
    '==': lambda a, b: a == b,
}
inclusion_ops = {'True_l': '[', 'False_l': '(', 'True_r': ']', 'False_r': ')'}

def get_constraints(node):
    constraints = []
    if type(node) == str:
        return constraints
    elif len(node) == 2:
        op, child = node
        child_constraints = get_constraints(child)
        constraints.extend(child_constraints)
        if op == 'sqrt':
            op_constraint = (child, '>=', '0')
            constraints.append(op_constraint)
        elif op in ['log', 'ln']:
            op_constraint = (child, '>', '0')
            constraints.append(op_constraint)
        elif op in ['arcsin', 'arccos']:
            op_constraint = [(child, '>=', '-1'), (child, '<=', '1')]
            constraints.extend(op_constraint)
        elif op in ['arcsec', 'arccosec']:
            op_constraint = [(child, '<=', '-1'), (child, '>=', '1')]
            constraints.append(op_constraint)
        #elif op in ['tan', 'sec']:
        #    op_constraint = (child, 'excludes_periodic', math.pi/2, math.pi)
        #    constraints.append(op_constraint)
        #elif op == 'cosec':
        #    op_constraint = (child, 'excludes_periodic', 0, math.pi)
        #    constraints.append(op_constraint)
        return constraints
    elif len(node) == 3:
        op, left, right = node
        left_constraints = get_constraints(left)
        right_constraints = get_constraints(right)
        constraints.extend(left_constraints)
        constraints.extend(right_constraints)
        if op == '/':
            if contains_var(right):
                op_constraint = (right, '!=', '0')
                constraints.append(op_constraint)
        elif op == '^' and type(right) == str and right.isalpha() == False:
            exp = float_to_frac(right)
            if type(exp) == tuple and float(exp[2]) % 2 == 0:
                op_constraint =  (left, '>=', '0')
                constraints.append(op_constraint)
        return constraints

def contains_var(node):
    if type(node) == str:
        if node.isalpha():
            return True
        else:
            return False
    elif len(node) == 3:
        op, left, right = node
        l_x, r_x = contains_var(left), contains_var(right)
        return l_x or r_x
    elif len(node) == 2:
        op, child = node
        child_x = contains_var(child)
        return child_x

def safe_evaluate(node, x):
    try:
        val = evaluate_at(node, x)
    except (ValueError, ZeroDivisionError):
        val = None
    if type(val) == complex:
        val = None
    return val

def safe_check(node, x, inequality, rhs):
    val = safe_evaluate(node, x)
    if val == None:
        return False
    return comparison_ops[inequality](val, rhs)

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

def bisect_class(node, lo, hi, tol=1e-9):
    lo_class = classify(safe_evaluate(node, lo), tol)
    while (hi-lo)>tol:
        mid = (lo+hi)/2
        mid_class = classify(safe_evaluate(node, mid), tol)
        if mid_class == lo_class:
            lo = mid
        else:
            hi = mid
    return hi

def classify(val, tol=1e-9):
    if val is None:
        return 'undef'
    elif val < -tol:
        return 'neg'
    elif val > tol:
        return 'pos'
    else:
        return 'zero'

def get_critical_points(node, lo, hi, step, tol=1e-9):
    critical_points = []
    x = lo
    prev_x = None
    prev_class = None
    zero_run = []
    first = True

    while x<= hi:
        val = safe_evaluate(node, x)
        cls = classify(val, tol)

        if first == False and cls != prev_class:
            if {prev_class, cls} == {'neg', 'pos'}:
                critical_points.append(round(bisect_class(node, prev_x, x), 6))
            elif prev_class == 'undef' or cls == 'undef':
                critical_points.append(round(bisect_class(node, prev_x, x), 6))
            elif cls == 'zero':
                inb = round(bisect_class(node, prev_x, x, tol), 6)
                zero_run = [x]
            elif prev_class == 'zero':
                outb = round(bisect_class(node, prev_x, x, tol), 6)
                if len(zero_run) == 1:
                    critical_points.append(round(zero_run[0], 6))
                else:
                    critical_points.append(inb)
                    critical_points.append(outb)
                zero_run = []
        elif cls == 'zero':
            zero_run.append(x)
        prev_x, prev_class = x, cls
        first = False
        x+=step
    if zero_run and inb is not None:
        critical_points.append(inb)
    return sorted(critical_points)

def test_domain_intervals(node, inequality, rhs, critical_points):
    critical_points = sorted(critical_points)
    intervals = []
    prev_pt = None
    for i in critical_points:
        if len(critical_points) == 1:
            ineq_l = safe_check(node, i-1, inequality, rhs)
            ineq_r = safe_check(node, i+1, inequality, rhs)
            ineq_x = safe_check(node, i, inequality, rhs)
            if ineq_x:
                if ineq_l == ineq_r == False:
                    intervals.append((i, i, True, True))
                elif ineq_l == ineq_r == True:
                    intervals.append((-math.inf, math.inf, False, False))
                elif ineq_l:
                    intervals.append((-math.inf, i, False, True))
                elif ineq_r:
                    intervals.append((i, math.inf, True, False))
            else:
                if ineq_l == ineq_r == False:
                    intervals.append((None, None, False, False))
                elif ineq_l == ineq_r == True:
                    intervals.append([(-math.inf, i, False, False), (i, math.inf, False, False)])                
                elif ineq_l:
                    intervals.append((-math.inf, i, False, False))
                elif ineq_r:
                    intervals.append((i, math.inf, False, False))
        elif i == critical_points[0]:
            prev_pt = i
            ineq_l = safe_check(node, i-1, inequality, rhs)
            if ineq_l:
                ineq_x = safe_check(node, i, inequality, rhs)
                if ineq_x:
                    intervals.append((-math.inf, i, False, True))    
                else:
                    intervals.append((-math.inf, i, False, False))
        elif i == critical_points[len(critical_points)-1]:
            ineq_1 = safe_check(node, (prev_pt+i)/2, inequality, rhs)
            if ineq_1:
                ineq_l = safe_check(node, prev_pt, inequality, rhs)
                ineq_r = safe_check(node, i, inequality, rhs)
                if ineq_l == ineq_r == False:
                    intervals.append((prev_pt, i, False, False))
                elif ineq_l == ineq_r == True:
                    intervals.append((prev_pt, i, True, True))
                elif ineq_l:
                    intervals.append((prev_pt, i, True, False))
                elif ineq_r:
                    intervals.append((prev_pt, i, False, True))
            ineq_2 = safe_check(node, i+1, inequality, rhs)
            if ineq_2:
                ineq_x = safe_check(node, i, inequality, rhs)
                if ineq_x:
                    intervals.append((i, math.inf, True, False))
                else:
                    intervals.append((i, math.inf, False, False))
            prev_pt = i
        else:
            ineq_1 = safe_check(node, (prev_pt+i)/2, inequality, rhs)
            if ineq_1:
                ineq_l = safe_check(node, prev_pt, inequality, rhs)
                ineq_r = safe_check(node, i, inequality, rhs)
                if ineq_l == ineq_r == False:
                    intervals.append((prev_pt, i, False, False))
                elif ineq_l == ineq_r == True:
                    intervals.append((prev_pt, i, True, True))
                elif ineq_l:
                    intervals.append((prev_pt, i, True, False))
                elif ineq_r:
                    intervals.append((prev_pt, i, False, True))
            prev_pt = i
    if not intervals:
        intervals.append((None, None, False, False))
    if len(intervals) > 1:
        intervals = union_intervals(intervals)
    return intervals

def solve_constraints(constraints):
    combined_intervals = []
    for i in constraints:
        if type(i)==tuple:
            subtree, inequality, rhs = i
            subtree = ('-', subtree, rhs)
            rhs = 0
            critical_points = get_critical_points(subtree, -20, 20, 0.1)
            interval = test_domain_intervals(subtree, inequality, rhs, critical_points)
            if len(interval)>1:
                combined_intervals.append(interval)
            else:
                combined_intervals.extend(interval)
        elif type(i)==list:
            constrnt_1, constrnt_2 = i[0], i[1]
            subtree_1, inequality_1, rhs_1 = constrnt_1
            subtree_1 = ('-', subtree_1, rhs_1)
            rhs_1 = 0
            critical_points_1 = get_critical_points(subtree_1, -20, 20, 0.1)
            interval_1 = test_domain_intervals(subtree_1, inequality_1, rhs_1, critical_points_1)
            subtree_2, inequality_2, rhs_2 = constrnt_2
            subtree_2 = ('-', subtree_2, rhs_2)
            rhs_2 = 0
            critical_points_2 = get_critical_points(subtree_2, -20, 20, 0.1)
            interval_2 = test_domain_intervals(subtree_2, inequality_2, rhs_2, critical_points_2)
            interval = union_intervals(interval_1 + interval_2)
            if len(interval)>1:
                combined_intervals.append(interval)
            else:
                combined_intervals.extend(interval)
    return combined_intervals

def distribute_intervals(left, right):
    distributed = []
    for i in left:
        for j in right:
            distributed.append([i, j])
    return distributed

def union_intervals(intervals):
    n_intervals = []
    for i in intervals:
        if i != (None, None, False, False):
            n_intervals.append(i)
    if len(n_intervals)==0:
        return [(None, None, False, False)]
    n_intervals = sorted(n_intervals)
    union = []
    current = n_intervals[0]
    n_intervals.pop(0)
    for i in n_intervals:
        lo_1, hi_1, lo_incl_1, hi_incl_1 = current
        lo_2, hi_2, lo_incl_2, hi_incl_2 = i

        if hi_1 < lo_2 or (hi_1 == lo_2 and not (hi_incl_1 or lo_incl_2)):
            union.append(current)
            current = i
        else:
            lo = min(float(lo_1), float(lo_2))
            if lo_1 != lo_2:
                if lo == lo_1:
                    lo_incl = lo_incl_1
                elif lo == lo_2:
                    lo_incl = lo_incl_2
            else:
                if lo_incl_1 or lo_incl_2:
                    lo_incl = True
                else:
                    lo_incl = False
            
            hi = max(float(hi_1), float(hi_2))
            if hi_1 != hi_2:
                if hi == hi_1:
                    hi_incl = hi_incl_1
                elif hi == hi_2:
                    hi_incl = hi_incl_2
            else:
                if hi_incl_1 or hi_incl_2:
                    hi_incl = True
                else:
                    hi_incl = False
            
            current = (lo, hi, lo_incl, hi_incl)
    union.append(current)
    return union

def intersect_interval(intervals):
    if len(intervals) == 0:
        return [(-math.inf, math.inf, False, False)]
    elif (None, None, False, False) in intervals:
        return [(None, None, False, False)]
    elif len(intervals) == 1:
        return intervals
    elif type(intervals[0]) == list or type(intervals[1]) == list:
        if type(intervals[0]) != list:
            left = [intervals[0]]
        else:
            left = intervals[0]
        if type(intervals[1]) != list:
            right = [intervals[1]]
        else:
            right = intervals[1]
        dist = distribute_intervals(left, right)
        temp = []
        for i in dist:
            temp.extend(intersect_interval(i))
        union = union_intervals(temp)
        intervals.pop(0)
        intervals.pop(0)
        if len(union)>1:
            intervals.insert(0, union)
        else:
            intervals.insert(0, union[0])
        complete_intersection = intersect_interval(intervals)
        return complete_intersection
    else:
        lo_1, hi_1, lo_incl_1, hi_incl_1 = intervals[0]
        lo_2, hi_2, lo_incl_2, hi_incl_2 = intervals[1]
        intervals.pop(0)
        intervals.pop(0)
        lo = max(float(lo_1), float(lo_2))
        if lo_1 != lo_2:
            if lo == lo_1:
                lo_incl = lo_incl_1
            elif lo == lo_2:
                lo_incl = lo_incl_2
        else:
            if lo_incl_1 and lo_incl_2:
                lo_incl = True
            else:
                lo_incl = False
    
        hi = min(float(hi_1), float(hi_2))
        if hi_1 != hi_2:
            if hi == hi_1:
                hi_incl = hi_incl_1
            elif hi == hi_2:
                hi_incl = hi_incl_2
        else:
            if hi_incl_1 and hi_incl_2:
                hi_incl = True
            else:
                hi_incl = False
        if lo>hi:
            intersection = (None, None, False, False)
        elif lo == hi:
            if lo_incl and hi_incl:
                intersection = (lo, hi, lo_incl, hi_incl)
            else:
                intersection = (None, None, False, False)    
        else:
            intersection = (lo, hi, lo_incl, hi_incl)
        
        intervals.insert(0, intersection)
        complete_intersection = intersect_interval(intervals)
        return complete_intersection

def convert_incl(interval):
    lo, hi, lo_incl, hi_incl = interval
    if lo_incl:
        c_lo_incl = 'True_l'
    else:
        c_lo_incl = 'False_l'
    
    if hi_incl:
        c_hi_incl = 'True_r'
    else:
        c_hi_incl = 'False_r'
    
    return (lo, hi, c_lo_incl, c_hi_incl)

def normalize(domain):
    pretty = []
    if (None, None, False, False) in domain:
            pretty.append('Φ')
    elif (-math.inf, math.inf, False, False) in domain:
            pretty.append('R')
    else:
        for i in domain:
            if type(i) == list:
                if len(domain) == 1 and len(i) >= 2:
                    is_pattern = i[0][0] == -math.inf and i[-1][1] == math.inf
                    holes = []
                    if is_pattern:
                        for a, b in zip(i, i[1:]):
                            a_hi, a_hi_incl = a[1], a[3]
                            b_lo, b_lo_incl = b[0], b[2]
                            if a_hi == b_lo and a_hi_incl == False and b_lo_incl == False:
                                holes.append(a_hi)
                            else:
                                is_pattern = False
                                break
                    if is_pattern and holes:
                        pts = ', '.join(convert_to_str(h) for h in holes)
                        return 'R-{' + pts + '}'
                for j in i:
                    lo, hi, lo_incl, hi_incl = convert_incl(j)
                    if lo == hi:
                        pretty.append('{'+str(convert_to_str(lo))+'}')
                    elif lo == -math.inf:
                        pretty.append(f"(-∞, {convert_to_str(hi)}"+inclusion_ops[hi_incl])
                    elif hi == math.inf:
                        pretty.append(inclusion_ops[lo_incl]+f"{convert_to_str(lo)}, ∞)")
                    else:
                        pretty.append(inclusion_ops[lo_incl]+f"{convert_to_str(lo)}, {convert_to_str(hi)}"+inclusion_ops[hi_incl])
                    if i.index(j)<len(i)-1:
                        pretty.append('U')
            else:
                lo, hi, lo_incl, hi_incl = convert_incl(i)
                if lo==hi:
                    pretty.append('{'+str(convert_to_str(lo))+'}')
                elif lo == -math.inf:
                        pretty.append(f"(-∞, {convert_to_str(hi)}"+inclusion_ops[hi_incl])
                elif hi == math.inf:
                        pretty.append(inclusion_ops[lo_incl]+f"{convert_to_str(lo)}, ∞)")
                else:
                    pretty.append(inclusion_ops[lo_incl]+f"{convert_to_str(lo)}, {convert_to_str(hi)}"+inclusion_ops[hi_incl])
    return ' '.join(pretty)

def find_domain(exp):
    tokens = tokenize(exp)
    node = parse_add(tokens)[0]
    sim = pow_to_div(simplify(node))
    constraints = get_constraints(sim)
    intervals = solve_constraints(constraints)
    practical = intersect_interval(intervals)
    pretty = normalize(practical)
    return (pretty, practical)