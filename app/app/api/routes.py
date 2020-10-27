from flask import jsonify , request
import json

from ..core.database import users , algorithms , AUTH
from ..main import app

@app.route("/users/<email>" , methods=['GET'])
def route_users(email):
    if AUTH != 'ENABLED' or users==None:
        return {
            "status" : "not allowed" , 
            "description" : "Auth is disabled"
        }
    users_data = users.search_user(email)
    if users_data == None:
        return {"status" : "Not Found"}
    users_data = users_data.describe()
    return jsonify(users_data)

@app.route("/users/register" , methods=['POST'])
def route_register_user():
    data = request.get_json()
    return jsonify(users.register_user(data=data))

@app.route("/users/login" , methods=['POST'])
def route_login():
    data = request.get_json()
    return jsonify(users.login(data))

@app.route("/argorithms/list" , methods=['GET'])
def route_list_algorithms():
    return jsonify({"list" : algorithms.list()})

@app.route("/argorithms/insert" , methods=['POST'])
def route_insert_argorithm():
    file_data = json.loads(str(request.files['data'].read() , 'utf-8'))
    posted_file = request.files['document']
    return jsonify(algorithms.insert(file_data,posted_file))

@app.route("/argorithms/run" , methods=['POST'])
def route_run_algorithms():
    data = request.get_json()
    return jsonify(algorithms.process(data))

@app.route("/argorithms/delete" , methods=['POST'])
def route_delete_argorithm():
    data = request.get_json()
    return jsonify(algorithms.delete(data))
