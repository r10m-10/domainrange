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
        elif op in '*/':
            if type(left) == type(right) == tuple and len(left) == len(right) == 3 and (left[0] in '+-' and right[0] in '+-') or op == '/':
                return f"({left_unparsed}) {op} ({right_unparsed})"
            elif (type(left) == type(right) == tuple and len(left) == 3 and len(right) == 2) or (type(left) == tuple and left[0] in '+-') :
                return f"({left_unparsed}) {op} {right_unparsed}"
            elif (type(left) == type(right) == tuple and right[0] in '+-' and right[0] == '*') or (type(right) == tuple and right[0] in '+-'):
                return f"{left_unparsed} {op} ({right_unparsed})"
            elif op == '*' and type(left) == tuple and type(right) == str and left[0] == '*':
                return f"{left_unparsed} {op} {right_unparsed}"
            else:
                print(left)
                if left.isalpha():
                    return f"{right_unparsed}{left_unparsed}"
                else:
                    return f"{left_unparsed}{right_unparsed}"
        elif op == '/':
            if type(left) == type(right) == tuple and (left[0] in '+-' and right[0] in '+-'):
                return f"({left_unparsed}) {op} ({right_unparsed})"

def get_node(exp):
    tokens = tokenize(exp)
    node = parse_add(tokens)[0]
    sim = pow_to_div(simplify(node))
    return sim

# test -> '(x+2)/(x/(x+1))', '(x+2)/(x+3) * (x+1)/(x+4)'
node = get_node('(x+1) * 3 * x')
print(node)
print(unparse(node))