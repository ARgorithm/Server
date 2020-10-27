from flask import jsonify , request , make_response
import json
from .utils import token_required , auth_required
from ..core.database import users , algorithms 
from ..main import app
import jwt

@app.route("/users/<email>" , methods=['GET'])
@auth_required
def route_users(email):
    users_data = users.search_user(email)
    if users_data == None:
        return {"status" : "Not Found"}
    users_data = users_data.describe()
    return jsonify(users_data)

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

@app.route("/argorithms/list" , methods=['GET'])
def route_list_algorithms():
    return jsonify({"list" : algorithms.list()})

@app.route("/argorithms/insert" , methods=['POST'])
@token_required
def route_insert_argorithm(maintainer):
    file_data = json.loads(str(request.files['data'].read() , 'utf-8'))
    file_data['maintainer'] = maintainer
    posted_file = request.files['document']
    return jsonify(algorithms.insert(file_data,posted_file))

@app.route("/argorithms/run" , methods=['POST'])
def route_run_algorithms():
    data = request.get_json()
    return jsonify(algorithms.process(data))

@app.route("/argorithms/delete" , methods=['POST'])
@token_required
def route_delete_argorithm(maintainer):
    data = request.get_json()
    data['maintainer'] = maintainer
    return jsonify(algorithms.delete(data))
