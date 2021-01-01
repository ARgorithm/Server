from flask import jsonify , request , make_response
import json
from .utils import token_required , auth_required
from ..core.database import users , algorithms 
from ..main import app

@app.route("/users/verify" , methods=['GET'])
@token_required
def route_user_verify(email):
    return jsonify({"status":True})

@app.route("/users/register" , methods=['POST'])
@auth_required
def route_register_user():
    data = request.get_json()
    return jsonify(users.register_user(data=data))

@app.route("/users/login" , methods=['POST'])
@auth_required
def route_user_login():
    data = request.get_json()
    return make_response(jsonify(users.login(data)),201)