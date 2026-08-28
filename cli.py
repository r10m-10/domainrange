from engine.ast.tokenizer import tokenize
from engine.ast.parser import parse_add
from engine.ast.tree import download_svg_cli
from engine.calculators.derivative import differentiate
from engine.calculators.domain import find_domain
from engine.calculators.range import find_range
from engine.calculators.simplify import simplify

print('''1. Enter
2. Quit''')
in_ch = int(input("> "))

while in_ch == 1:
    print('''
----------SELECT TOOL----------
''')
    print('''1. AST Generator
2. AST Visualizer
3. Domain
4. Range
5. Derivative
6. simplify
7. Quit''')
    tool = int(input(">  "))

    if tool == 1:
        print('''
----------AST GENERATOR----------''')
        print('''Info: See the raw parsed structure behind an expression.
''')
        print('''Enter Expression:''')
        exp = str(input(">  "))
        print('''
Output:''')
        tokens = tokenize(exp)
        print(parse_add(tokens)[0])
        print('''
1. Continue
2. Quit''')
        in_ch = int(input("> "))
        continue

    elif tool == 2:
        print('''
----------AST VISUALIZER----------''')
        print('''Info: Download the Tree diagram of entered expression as SVG file.
''')
        print('''Enter Expression:''')
        exp = str(input(">  "))
        print('''
Select node color:
1. Skyblue (default)
2. Custom color (Enter hex value only)
''')
        node_color_inp = int(input(">  "))
        node_color = "skyblue" if node_color_inp == 1 else str(input("Enter hex color: "))
        print('''
Select text color:
1. black (default)
2. Custom color (Enter hex value only)
''')
        text_color_inp = int(input(">  "))
        text_color = "black" if text_color_inp == 1 else str(input("Enter hex color: "))
        print('''
Select line color:
1. white (default)
2. Custom color (Enter hex value only)
''')
        line_color_inp = int(input(">  "))
        line_color = "white" if line_color_inp == 1 else str(input("Enter hex color: "))
        download_svg_cli(exp, node_color, text_color, line_color)
        print('''
tree.svg installed successfully!''')
        print('''
1. Continue
2. Quit''')
        in_ch = int(input("> "))
        continue

    elif tool == 3:
        print('''
----------DOMAIN----------''')
        print('''Info: Find the domain of entered expression.
''')
        print('''Enter Expression:''')
        exp = str(input(">  "))
        print('''
Output:''')
        print(find_domain(exp)[0])
        print('''
1. Continue
2. Quit''')
        in_ch = int(input("> "))
        continue

    elif tool == 4:
        print('''
----------RANGE----------''')
        print('''Info: Find the range of entered expression.
''')
        print('''Enter Expression:''')
        exp = str(input(">  "))
        print('''
Output:''')
        print(find_range(exp)[0])
        print('''
1. Continue
2. Quit''')
        in_ch = int(input("> "))
    
    if tool == 7:
        in_ch = 2
        break
