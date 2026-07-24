from api.calculators.domain import find_domain
from api.ast.tree import render_expression
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder='../templates', static_folder='../static')

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)