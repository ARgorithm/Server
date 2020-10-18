from flask import jsonify , request
import json

from ..core.database import users , algorithms
from ..main import app

@app.route("/users/")
def route_users():
    users_data = users
    return jsonify(users_data)

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