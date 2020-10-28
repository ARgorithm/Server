from flask import jsonify , request , make_response
import json
from .utils import token_required , auth_required
from ..core.database import users , algorithms 
from ..main import app

@app.route("/auth",methods=['GET'])
@auth_required
def route_auth_check():
    return jsonify({"status":True})

@app.route("/users/verify" , methods=['GET'])
@token_required
def route_token_verify(email):
    return jsonify({"status":True})

@app.route("/users/<email>" , methods=['GET'])
@auth_required
def route_users(email):
    users_data = users.search_user(email)
    if users_data == None:
        return {"status" : "Not Found"}
    users_data = users_data.describe()
    return f"""
        User_email : {users_data['email']}
        Joined on {users_data['join_time']}
    """

@app.route("/users/register" , methods=['POST'])
@auth_required
def route_register_user():
    data = request.get_json()
    return jsonify(users.register_user(data=data))

@app.route("/users/login" , methods=['POST'])
@auth_required
def route_login():
    data = request.get_json()
    return make_response(jsonify(users.login(data)),201)