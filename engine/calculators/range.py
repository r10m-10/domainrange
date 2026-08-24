import math
from ..ast.tokenizer import tokenize
from ..ast.parser import parse_add
from .simplify import simplify
from .derivative import differentiate
from .domain import find_domain, get_critical_points, safe_evaluate, union_intervals, normalize

FIXED_RANGES = {
    'sin':    [(-1.0, 1.0, True, True)],
    'cos':    [(-1.0, 1.0, True, True)],
    'sec':    [(-math.inf, -1.0, False, True), (1.0, math.inf, True, False)],
    'cosec':  [(-math.inf, -1.0, False, True), (1.0, math.inf, True, False)],
    'arcsin': [(-math.pi/2, math.pi/2, True, True)],
    'arccos': [(0.0, math.pi, True, True)],
    'arctan': [(-math.pi/2, math.pi/2, False, False)],
    'arccot': [(0.0, math.pi, False, False)],
}

def snap(val, tol=1e-4):
    for denom in (1,2,4):
        nearest = round(val * denom) / denom
        if abs(val-nearest) < tol:
            return nearest
    return val

def estimate_limit(node, x, direction, offsets=(1e-2, 1e-4, 1e-6)):
    if x == math.inf or x == -math.inf:
        if x == math.inf:
            chk = [1e4, 1e5, 1e6]
        else:
            chk = [-1e4, -1e5, -1e6]
    else:
        chk = [x + direction * i for i in offsets]

    samples = [safe_evaluate(node,i) for i in chk]
    samples = [s for s in samples if s is not None]

    if len(samples) < len(chk):
        return ('undetermined', None)

    diffs = [abs(samples[i+1] - samples[i]) for i in range(len(samples) - 1)]
    growing = all(abs(samples[i+1]) > abs(samples[i]) for i in range(len(samples) - 1))

    if len(diffs) == 1:
        if growing and abs(samples[-1]) > abs(samples[0])*10:
            if samples[-1] > 0:
                val = math.inf
            else:
                val = -math.inf
            return ('infinite', val)
        return ('finite', snap(samples[-1]))

    if diffs[-1] <= diffs[0]:
        return ('finite', snap(samples[-1]))    

    if growing:
        if samples[-1] > 0:
            val = math.inf
        else:
            val = -math.inf
        return ('infinite', val)

    return ('undetermined', None)

def flatten_domain(domain):
    flat = []
    for i in domain:
        if type(i) == list:
            flat.extend(flatten_domain(i))
        else:
            flat.append(i)
    return flat

def find_range(exp, window = 100):
    tokens = tokenize(exp)
    node = parse_add(tokens)[0]
    node = simplify(node)

    domain = flatten_domain(find_domain(exp)[1])

    if domain == [(None, None, False, False)]:
        return 'Φ', domain, False

    if type(node) == tuple and len(node) == 2 and node[0] in FIXED_RANGES and type(node[1]) == str and node[1].isalpha() and len(node[1]) == 1:
        merged = FIXED_RANGES[node[0]]
        pretty = normalize([merged])
        return pretty, merged, False
    
    der = differentiate(exp)

    range_pieces = []
    partial = False

    for i in domain:
        lo, hi, lo_incl, hi_incl = i
        if lo is None:
            continue

        search_lo = lo if lo != -math.inf else -window
        search_hi = hi if hi != math.inf else window

        crit_pts = get_critical_points(der, search_lo, search_hi, 0.1)
        crit_pts = [c for c in crit_pts if lo < c < hi]

        eval_pts = []

        if lo == -math.inf:
            kind, val = estimate_limit(node, -math.inf, -1)
            if kind == 'undetermined':
                partial = True
            else:
                eval_pts.append((val, False))
        elif lo_incl:
            val = safe_evaluate(node, lo)
            if val is None:
                partial = True
            else:
                eval_pts.append((val, True))
        else:
            kind, val = estimate_limit(node, lo, +1)
            if kind == 'undetermined':
                partial = True
            else:
                eval_pts.append((val, False))

        for i in crit_pts:
            val = safe_evaluate(node, i)
            if val is None:
                continue
            eval_pts.append((val, True))

        if hi == math.inf:
            kind, val = estimate_limit(node, math.inf, +1)
            if kind == 'undetermined':
                partial = True
            else:
                eval_pts.append((val, False))
        elif hi_incl:
            val = safe_evaluate(node, hi)
            if val is None:
                partial = True
            else:
                eval_pts.append((val, True))
        else:
            kind, val = estimate_limit(node, hi, -1)
            if kind == 'undetermined':
                partial = True
            else:
                eval_pts.append((val, False))

        if len(eval_pts) == 1:
            val, incl = eval_pts[0]
            if incl:
                range_pieces.append((val, val, True, True))
        else:
            for i in range(len(eval_pts) - 1):
                val1, incl1 = eval_pts[i]
                val2, incl2 = eval_pts[i+1]
                if val1 in (math.inf, -math.inf):
                    incl1 = False
                if val2 in (math.inf, -math.inf):
                    incl2 = False
                if val1 <= val2:
                    range_pieces.append((val1, val2, incl1, incl2))
                else:
                    range_pieces.append((val2, val1, incl2, incl1))

    merged = union_intervals(range_pieces)
    if len(merged) > 1:
        pretty = normalize([merged])
    else:
        pretty = normalize(merged)
    if partial:
        pretty += '  (partial: some boundary values could not be resolved)'
    return pretty, merged, partial