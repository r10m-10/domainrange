from flask import Flask, request, jsonify, render_template
from api.routes.home import home_bp
from api.routes.ast_routes import ast_bp
from api.routes.derivative_routes import der_bp

app = Flask(__name__, template_folder='../templates', static_folder='../static')

app.register_blueprint(home_bp)
app.register_blueprint(ast_bp)
app.register_blueprint(der_bp)