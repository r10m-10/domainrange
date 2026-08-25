from .tokenizer import tokenize
from .parser import parse_add
from ..calculators.simplify import simplify, pow_to_div

precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}

def needs_paren(child, op, side):
    if type(child) == str:
        return False
    elif len(child) == 2:
        return False
    elif len(child) == 3:
        child_op = child[0]
        if precedence[child_op] < precedence[op]:
            return True
        elif precedence[child_op] > precedence[op]:
            return False
        elif precedence[child_op] == precedence[op]:
            if op in '+*':
                return False
            elif op in '-/':
                if side == 'right':
                    return True
                else:
                    return False
            elif op == '^':
                if side == 'left':
                    return True
                else:
                    return False

def unparse(node):
    if type(node) == str:
        return node
    elif len(node) == 3:
        op, left, right = node
        left_unparsed = unparse(left)
        right_unparsed = unparse(right)

        if needs_paren(left, op, 'left'):
            left_unparsed = f"({left_unparsed})"
        if needs_paren(right, op, 'right'):
            right_unparsed = f"({right_unparsed})"

        return f"{left_unparsed} {op} {right_unparsed}"
    elif len(node) == 2:
        op, child = node
        child_unparsed = unparse(child)
        if op == 'abs':
            return f"|{child_unparsed}|"
        elif op == 'frac':
            return f"{{{child_unparsed}}}"
        elif op == 'gif':
            return f"[{child_unparsed}]"
        else:
            return f"{op}({child_unparsed})"

def get_node(exp):
    tokens = tokenize(exp)
    node = parse_add(tokens)[0]
    sim = pow_to_div(simplify(node))
    return sim

test_cases = [
    # Group 1: same-precedence chains, - and / (non-associative)
    ('-', ('-', 'a', 'b'), 'c'),                          # 1: a - b - c
    ('-', 'a', ('-', 'b', 'c')),                          # 2: a - (b - c)
    ('/', ('/', 'a', 'b'), 'c'),                          # 3: a / b / c
    ('/', 'a', ('/', 'b', 'c')),                          # 4: a / (b / c)

    # Group 2: same-precedence chains, + and * (associative/commutative)
    ('+', ('+', 'a', 'b'), 'c'),                          # 5: a + b + c
    ('+', 'a', ('+', 'b', 'c')),                          # 6: a + b + c
    ('*', ('*', 'a', 'b'), 'c'),                          # 7: a * b * c
    ('*', 'a', ('*', 'b', 'c')),                          # 8: a * b * c

    # Group 3: ^ (right-associative, mirror of -/ /)
    ('^', ('^', 'a', 'b'), 'c'),                          # 9: (a ^ b) ^ c
    ('^', 'a', ('^', 'b', 'c')),                          # 10: a ^ b ^ c

    # Group 4: cross-precedence
    ('*', ('+', 'a', 'b'), 'c'),                          # 11: (a + b) * c
    ('+', ('*', 'a', 'b'), 'c'),                          # 12: a * b + c
    ('/', ('+', 'a', 'b'), ('-', 'c', 'd')),              # 13: (a + b) / (c - d)

    # Group 5: three-levels-deep chains
    ('-', ('-', ('-', 'a', 'b'), 'c'), 'd'),              # 14: a - b - c - d
    ('-', 'a', ('-', 'b', ('-', 'c', 'd'))),              # 15: a - (b - (c - d))
    ('^', 'a', ('^', 'b', ('^', 'c', 'd'))),              # 16: a ^ b ^ c ^ d

    # Group 6: function calls and brackets mixed with ops
    ('*', ('sin', 'x'), ('cos', 'y')),                    # 17: sin(x) * cos(y)
    ('/', ('abs', ('-', 'a', 'b')), 'c'),                 # 18: |a - b| / c
    ('-', ('frac', 'x'), 'y'),                            # 19: {x} - y

    # Group 7: asymmetric siblings
    ('-', ('+', 'a', 'b'), ('*', 'c', 'd')),              # 20: (a + b) - c * d
    ('/', ('*', 'a', 'b'), ('+', 'c', 'd')),              # 21: a * b / (c + d)
]