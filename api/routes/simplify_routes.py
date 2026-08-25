from flask import Blueprint, render_template, request, jsonify
from engine.ast.tokenizer import tokenize
from engine.ast.parser import parse_add
from engine.calculators.simplify import simplified_str

sim_bp = Blueprint('simplify', __name__)

@sim_bp.route('/simplify')
def simplify_page():
    return render_template('simplify.html')

@sim_bp.route('/api/simplify', methods=['POST'])
def simplify_api():
    data = request.get_json()
    exp = data.get('expression', '')
    tokens = tokenize(exp)
    node = parse_add(tokens)[0]

    try:
        sim = simplified_str(node)
        return jsonify({'success': True, 'sim': str(sim)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400