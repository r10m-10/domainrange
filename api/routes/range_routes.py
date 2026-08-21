from flask import Blueprint, render_template, request, jsonify
from engine.calculators.range import find_range

range_bp = Blueprint('range', __name__)

@range_bp.route('/calculate-range')
def calculate_range_page():
    return render_template('range_calc.html')

@range_bp.route('/api/calculate-range', methods=['POST'])
def calculate_range_api():
    data = request.get_json()
    exp = data.get('expression', '')

    try:
        range = find_range(exp)[0]
        return jsonify({'success': True, 'range': str(range)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400