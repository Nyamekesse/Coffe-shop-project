# from crypt import methods
import os
from turtle import title
from flask import Flask, request, jsonify, abort
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


db_drop_and_create_all()

# ROUTES



@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        available_drinks = Drink.query.all()
        if not available_drinks:
            abort(404)
        else:
            drinks = [drink.short() for drink in available_drinks]
            return jsonify({
                'success': True,
                'drinks': drinks
            }), 200

    except:
        abort(404)




@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_details(payload):
    try:
        available_drinks = Drink.query.order_by(Drink.id).all()
        if not available_drinks:
            abort(404)
        else:
            drinks = [drink.long() for drink in available_drinks]
            return jsonify({
                'success': True,
                'drinks': drinks
            }), 200

    except:
        abort(404)




@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_new_drink(payload):
    body = request.get_json()

    if body == None:
        abort(422)
    else:
        try:
            drink = Drink(title=body.get('title'),
                          recipe=json.dumps(body.get('recipe')))
            drink.insert()
            return jsonify({
                'success': True,
                'drinks': [drink.long() for drink in Drink.query.all()]
            }), 200
        except:
            abort(400)




@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload,id):
    body = request.get_json()
    if not body:
        abort(422)
    else:
        try:
            drink = Drink.query.filter(Drink.id == id).one_or_none()

            if not drink:
                abort(404)
            drink.title = body.get('title')
            drink.recipe = json.dumps(body.get('recipe'))
            drink.update()
            return jsonify({
                'success': True,
                'drinks': [drink.long() for drink in Drink.query.all()]
            }), 200
        except:
            abort(400)



@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        drink.delete()
        return jsonify({
            'success': True,
            'delete': id
        })
    except:
        abort(404)


# Error Handling

@ app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code


@ app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unauthorized'
    }), 401


@ app.errorhandler(400)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'Bad Request'
    }), 400


@ app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@ app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@ app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden"
    }), 403


@ app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": 'Method Not Allowed'
    }), 405


@ app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'Internal Server Error'
    }), 500
