from flask import Blueprint, render_template, request, jsonify
from engine.ast.tokenizer import tokenize
from engine.ast.parser import parse_add
from engine.ast.tree import render_expression

ast_bp = Blueprint('ast', __name__)

@ast_bp.route('/ast-generator')
def ast_generator_page():
    return render_template('ast_generator.html')

@ast_bp.route('/api/ast-generate', methods=['POST'])
def ast_generate_api():
    data = request.get_json()
    exp = data.get('expression', '')

    try:
        tokens = tokenize(exp)
        node = parse_add(tokens)[0]
        return jsonify({'success': True, 'node': str(node)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@ast_bp.route('/ast-visualizer')
def ast_visualizer_page():
    return render_template('ast_visualizer.html')

@ast_bp.route('/api/ast-visualize', methods=['POST'])
def ast_visualizer_api():
    data = request.get_json()
    exp = data.get('expression', '')

    try:
        tree = render_expression(exp)
        return jsonify({'success': True, 'svg': tree})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400