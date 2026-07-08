exp = "|-3|"

def tokenizer(exp):
    exp = exp.lower().replace(" ", "")
    tokens = []
    num = []
    word = []
    for i in range(len(exp)):
        if exp[i] in '+-*/^()|{[]}':
            if exp[i] == "-":
                if i == 0 or exp[i-1] in "[{|(+-*/^":
                    if exp[i+1].isdigit():
                        num.append(exp[i])
                    elif exp[i+1].isalpha():
                        word.append(exp[i])
                else:
                    tokens.append(exp[i])
            else:
                tokens.append(exp[i])
        elif exp[i].isdigit():
            if i == len(exp)-1:
                if exp[i-1].isdigit() or exp[i-1] in ".-":
                    num.append(exp[i])
                    tokens.append("".join(num))
                    num.clear()
                else:
                    tokens.append(exp[i])
            elif exp[i-1] == "-":
                if exp[i+1].isdigit():
                    num.append(exp[i])
                else:
                    num.append(exp[i])
                    tokens.append("".join(num))
                    num.clear()
            elif exp[i+1].isdigit():
                num.append(exp[i])
            elif exp[i+1] == ".":
                num.append(exp[i])
            elif exp[i-1].isdigit() or exp[i-1] == ".":
                num.append(exp[i])
                tokens.append("".join(num))
                num.clear()
            else:
                tokens.append(exp[i])
        elif exp[i].isalpha():
            if i == len(exp)-1:
                if exp[i-1].isalpha() or exp[i-1] == "-":
                    word.append(exp[i])
                    tokens.append("".join(word))
                    word.clear()
                else:
                    tokens.append(exp[i])
            elif exp[i-1] == "-":
                if exp[i+1].isdigit():
                    word.append(exp[i])
                else:
                    word.append(exp[i])
                    tokens.append("".join(word))
                    word.clear()
            elif exp[i+1].isalpha():
                word.append(exp[i])
            elif exp[i-1].isalpha():
                word.append(exp[i])
                tokens.append("".join(word))
                word.clear()
            else:
                tokens.append(exp[i])
        elif exp[i] == ".":
            num.append(exp[i])
    return tokens