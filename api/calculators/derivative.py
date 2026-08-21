from ..ast.tokenizer import tokenize
from ..ast.parser import parse_add
from .domain import contains_var
from .simplify import simplify, flatten, form_term, merge_terms, form_node, rebuild, pow_to_div

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
            return ('*', ('/', '1', ('^', ('-', '1', ('^', child, '2')), '0.5')), differentiate_unsim(child))
        elif op == 'arccos':
            return ('*', ('/', '-1', ('^', ('-', '1', ('^', child, '2')), '0.5')), differentiate_unsim(child))
        elif op == 'arctan':
            return ('*', ('/', '1', ('+', '1', ('^', child, '2'))), differentiate_unsim(child))
        elif op == 'arccosec':
            return ('*', ('/', '-1', ('*', ('abs', child), ('-', ('^', child, '2'), '1'))), differentiate_unsim(child))
        elif op == 'arcsec':
            return ('*', ('/', '1', ('*', ('abs', child), ('-', ('^', child, '2'), '1'))), differentiate_unsim(child))
        elif op == 'arccot':
            return ('*', ('/', '-1', ('+', '1', ('^', child, '2'))), differentiate_unsim(child))
        elif op == 'ln':
            return ('*', ('/', '1', child), differentiate_unsim(child))
        elif op == 'log':
            return ('*', ('/', '1', ('*', child, ('ln', '10'))), differentiate_unsim(child))

def differentiate(exp):
    tokens = tokenize(exp)
    node = parse_add(tokens)[0]
    sim_node = simplify(node)
    der = differentiate_unsim(sim_node)
    final = pow_to_div(simplify(der))
    return final