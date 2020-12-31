from flask import jsonify , request , make_response
import json
from .utils import programmer_token_required , auth_required , token_required
from ..core.database import algorithms
from ..main import app


@app.route("/argorithms/list" , methods=['GET'])
def route_list_algorithms():
    return jsonify({"list" : algorithms.list()})

@app.route("/argorithms/insert" , methods=['POST'])
@programmer_token_required
def route_insert_argorithm(maintainer):
    file_data = json.loads(str(request.files['data'].read() , 'utf-8'))
    file_data['maintainer'] = maintainer
    posted_file = request.files['document']
    return jsonify(algorithms.insert(file_data,posted_file))

@app.route("/argorithms/run" , methods=['POST'])
@token_required
def route_run_algorithms(email):
    data = request.get_json()
    data["email"] = email
    print(f"{email} has executed ARgorithmID : {data['argorithmID']}")
    return jsonify(algorithms.process(data))

@app.route("/argorithms/update" , methods=['POST'])
@programmer_token_required
def route_update_argorithm(maintainer):
    file_data = json.loads(str(request.files['data'].read() , 'utf-8'))
    file_data['maintainer'] = maintainer
    posted_file = request.files['document']
    return jsonify(algorithms.update(file_data,posted_file))

@app.route("/argorithms/delete" , methods=['POST'])
@programmer_token_required
def route_delete_argorithm(maintainer):
    data = request.get_json()
    data['maintainer'] = maintainer
    return jsonify(algorithms.delete(data))
