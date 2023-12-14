import uuid
import importlib
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from main import linear_optimize

app = Flask(__name__)
CORS(app, resources={"*": {"origins": "*"}})

@app.route('/optimize', methods=['POST', 'GET'])
def optimize():
    payload = request.get_json()
    res, sales, revenue = linear_optimize(**payload)
    if res:
        return jsonify({
            'status': 'success',
            'sales': [x for x in sales if x['qty'] > 0],
            'revenue': revenue
        }), 200
    else:
        return jsonify({
            'status': 'no solution found'
        }), 404

if __name__ == '__main__':
    app.run(debug=True)