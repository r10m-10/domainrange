from tokenizer import tokenizer

exp = str(input("Enter expression: "))
tokens = tokenizer(exp)

def parse_add(tokens, pos):
    left, pos = parse_mul(tokens, pos)

    while pos < len(tokens) and tokens[pos] in '+-':
        token = tokens[pos]
        pos+=1
        right, pos = parse_mul(tokens, pos)
        left = (token, left, right)
    else:
        return (left, pos)

def parse_mul(tokens, pos):
    left, pos = parse_atom(tokens, pos)

    while pos < len(tokens) and tokens[pos] in '*/':
        token = tokens[pos]
        pos+=1
        right, pos = parse_atom(tokens, pos)
        left = (token, left, right)
    else:
        return (left, pos)

def parse_atom(tokens, pos):
    token = tokens[pos]
    if token in ['sqrt', 'log', 'ln', 'sin', 'cos', 'tan', 'sec', 'cosec', 'arcsin', 'arccos', 'arctan', 'arcsec', 'arccosec']:
        pos+=2
        left, pos = parse_add(tokens, pos)
        pos+=1
        left = (token, left)
        return (left, pos)    
    elif token.isdigit() or token.isalpha():
        pos+=1
        return (token, pos)
    elif token == '(':
        pos+=1
        child, pos = parse_add(tokens, pos)
        pos+= 1
        return (child, pos)


print (parse_add(tokens, 0)[0])