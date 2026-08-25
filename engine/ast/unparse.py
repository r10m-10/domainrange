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

        if op in '+-':
            return f"{left_unparsed} {op} {right_unparsed}"
        elif op in '*/':
            if type(left) == type(right) == tuple and len(left) == len(right) == 3 and ((left[0] in '+-' and right[0] in '+-') or op == '/'):
                return f"({left_unparsed}) {op} ({right_unparsed})"
            elif (type(left) == type(right) == tuple and len(left) == 3 and len(right) == 2) or (type(left) == tuple and left[0] in '+-') or (op == '/' and type(left) == tuple and len(left) == 3):
                return f"({left_unparsed}) {op} {right_unparsed}"
            elif (type(left) == type(right) == tuple and len(left) == 2 and len(right) == 3) or (type(right) == tuple and right[0] in '+-') or (op == '/' and type(right) == tuple and len(right) == 3):
                return f"{left_unparsed} {op} ({right_unparsed})"
            elif (type(left) == type(right) == tuple and len(left) == len(right) == 2) or (type(left) == type(right) == str) or (type(left) == str and (type(right) == tuple and len(right) == 2)) or (type(right) == str and (type(left) == tuple and len(left) == 2)) or (op == '*' and type(left) == tuple and left[0] == '*' and (type(right) == str or (type(right) == tuple and len(right) == 2))):
                return f"{left_unparsed} {op} {right_unparsed}"

def get_node(exp):
    tokens = tokenize(exp)
    node = parse_add(tokens)[0]
    sim = pow_to_div(simplify(node))
    return sim

node = get_node('(x+2)/(x+3) * (x+1)/(x+4)')
print(node)
print(unparse(node))