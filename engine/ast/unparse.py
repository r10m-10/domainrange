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