from flask import jsonify , request , make_response
import json
from .utils import token_required , auth_required
from ..core.database import users , algorithms 
from ..main import app


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
