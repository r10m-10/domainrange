from tokenizer import tokenizer
from parser import parse_add

radius = 25
x_spacing = 90
y_spacing = 110
margin = 50

def assign_positions(node, depth, id_count, leaf_count, tree):
    if type(node) == str:
        str_id = id_count
        str_x = leaf_count
        tree[str_id] = {'label': node, 'x': str_x, 'depth': depth}
        id_count+=1
        leaf_count+=1
        return (str_id, id_count, str_x, leaf_count, tree)
    else:
        if len(node) == 3:
            op, left, right = node
            l_id, id_count, l_x, leaf_count, tree = assign_positions(left, depth+1, id_count, leaf_count, tree)
            r_id, id_count, r_x, leaf_count, tree = assign_positions(right, depth+1, id_count, leaf_count, tree)
            op_x = (l_x+r_x)/2
            op_id = id_count
            tree[op_id] = {'label': op, 'x': op_x, 'depth': depth, 'children': [l_id, r_id]}
            id_count+=1
            return (op_id, id_count, op_x, leaf_count, tree)
        else:
            op, child = node
            child_id, id_count, child_x, leaf_count, tree = assign_positions(child, depth+1, id_count, leaf_count, tree)
            op_x = child_x
            op_id = id_count
            tree[op_id] = {'label': op, 'x': op_x, 'depth': depth, 'children': [child_id]}
            id_count+=1
            return (op_id, id_count, op_x, leaf_count, tree)

def get_pixel_coords(x, depth):
    pixel_x = margin+x*x_spacing
    pixel_y = margin+depth*y_spacing

    return pixel_x, pixel_y 

def draw_nodes(tree):
    nodes = []
    for i in tree.values():
        x, y = get_pixel_coords(i['x'], i['depth'])
        svg = f'<circle cx="{x}" cy="{y}" r="25" fill="skyblue" stroke="black" /> <text x="{x}" y="{y}" text-anchor="middle" dominant-baseline="middle">{i['label']}</text>'
        nodes.append(svg)
    return " ".join(nodes)

def draw_lines(tree):
    lines = []
    for i in tree.values():
        if 'children' in i:
            x1, y1 = get_pixel_coords(i['x'], i['depth'])
            children = i['children']
            for j in children:
                child = tree[j]
                x2, y2 = get_pixel_coords(child['x'], child['depth'])
                line = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="white" />'
                lines.append(line)
    return " ".join(lines)

def render_expression(exp):
    tokens = tokenizer(exp)
    parsed = parse_add(tokens, 0)[0]
    tree = assign_positions(parsed, 0, 0, 0, {})[4]
    nodes = draw_nodes(tree)
    lines = draw_lines(tree)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="850" height="650"> {lines} {nodes} </svg>'
    with open("tree.svg", 'w') as f:
        f.write(svg)
    return svg