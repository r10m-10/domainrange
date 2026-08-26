from flask import Flask
from api.routes.home import home_bp
from api.routes.ast_routes import ast_bp
from api.routes.derivative_routes import der_bp
from api.routes.domain_routes import domain_bp
from api.routes.range_routes import range_bp
from api.routes.simplify_routes import sim_bp
from api.routes.guide import guide_bp

app = Flask(__name__, template_folder='../templates', static_folder='../static')

app.register_blueprint(home_bp)
app.register_blueprint(ast_bp)
app.register_blueprint(der_bp)
app.register_blueprint(domain_bp)
app.register_blueprint(range_bp)
app.register_blueprint(sim_bp)
app.register_blueprint(guide_bp)