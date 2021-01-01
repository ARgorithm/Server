from flask import jsonify , request , make_response
import json
from .utils import programmer_token_required , auth_required
from ..core.database import programmers , algorithms 
from ..main import app

@app.route("/auth",methods=['GET'])
@auth_required
def route_auth_check():
    return jsonify({"status":True})

@app.route("/programmers/verify" , methods=['GET'])
@programmer_token_required
def route_token_verify(email):
    return jsonify({"status":True})

@app.route("/programmers/<email>" , methods=['GET'])
@auth_required
def route_programmers(email):
    programmers_data = programmers.search_programmer(email)
    if programmers_data == None:
        return {"status" : "Not Found"}
    programmers_data = programmers_data.describe()
    return f"""
        programmer_email : {programmers_data['email']}
        Joined on {programmers_data['join_time']}
    """

@app.route("/programmers/register" , methods=['POST'])
@auth_required
def route_register_programmer():
    data = request.get_json()
    return jsonify(programmers.register_programmer(data=data))

@app.route("/programmers/login" , methods=['POST'])
@auth_required
def route_login():
    data = request.get_json()
    return make_response(jsonify(programmers.login(data)),201)