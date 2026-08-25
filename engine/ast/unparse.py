from .tokenizer import tokenize
from .parser import parse_add
from ..calculators.simplify import simplify, pow_to_div

def unparse(node):
    if type(node) == str:
        return node
    elif len(node) == 3:
        op, left, right = node
        left_unparsed = unparse(left)
        right_unparsed = unparse(right)

        if op in '+-':
            return f"{left} {op} {right}"
        elif op == '*':
            if type(left) == type(right) == tuple:
                if (left[0] in '+-' and right[0] in '+-') or left[0] == right[0] == '/' or (left[0] in '+-' and right[0] == '/') or (right[0] in '+-' and left[0] == '/'):
                    return f"({left_unparsed}) {op} ({right_unparsed})"
                elif left[0] in '+-':
                    return f"({left_unparsed}) {op} {right_unparsed}"
                elif right[0] in '+-':
                    return f"{left_unparsed} {op} ({right_unparsed})"

def get_node(exp):
    tokens = tokenize(exp)
    


print(unparse(('*', 'x', ('+', 'x', '1'))))