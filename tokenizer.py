exp = "x*y"

def tokenizer(exp):
    tokens = []
    num = []
    word = []
    for i in range(len(exp)):
        if exp[i] in "+-*/()":
            tokens.append(exp[i])
#        elif exp[i:i+4] == "sqrt":
#            tokens.append(exp[i:i+4])
        elif exp[i].isdigit():
            if exp[i+1].isdigit():
                num.append(exp[i])
            elif exp[i-1].isdigit():
                num.append(exp[i])
                tokens.append("".join(num))
                num.clear()
            else:
                tokens.append(exp[i])
        elif exp[i].isalpha():
            if i == len(exp) -1:
                tokens.append(exp[i])
            elif exp[i+1].isalpha():
                word.append(exp[i])
            elif exp[i-1].isalpha():
                word.append(exp[i])
                tokens.append("".join(word))
                word.clear()
            else:
                tokens.append(exp[i])
    return tokens

print(tokenizer(exp))