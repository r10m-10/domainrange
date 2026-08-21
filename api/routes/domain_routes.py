from flask import Blueprint, render_template, request, jsonify
from engine.calculators.domain import find_domain

domain_bp = Blueprint('domain', __name__)

@domain_bp.route('/domain')
def domain_page():
    return render_template('domain.html')

@domain_bp.route('/api/domain', methods=['POST'])
def domain_api():
    data = request.get_json()
    exp = data.get('expression', '')

    try:
        domain = find_domain(exp)[0]
        return jsonify({'success': True, 'domain': str(domain)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400