from flask import Blueprint, render_template, request, jsonify
from engine.calculators.derivative import differentiate

der_bp = Blueprint('derivative', __name__)

@der_bp.route('/differentiate')
def calculate_derivative_page():
    return render_template('derivative_calc.html')

@der_bp.route('/api/differentiate', methods=['POST'])
def calculate_derivative_api():
    data = request.get_json()
    exp = data.get('expression', '')

    try:
        der = differentiate(exp)
        return jsonify({'success': True, 'der': str(der)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400