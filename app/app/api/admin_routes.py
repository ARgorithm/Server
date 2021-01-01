from flask import jsonify , request , make_response
import json
from .utils import programmer_token_required , auth_required
from ..core.database import programmers , users
from ..main import app

@app.route("/admin/delete_user" , methods=['POST'])
@programmer_token_required
def route_delete_user(maintainer):
    data = request.get_json()
    programmers_data = programmers.search_programmer(maintainer)
    if programmers_data.admin == False:
        return jsonify({"status" : "access denied"})
    return jsonify(users.delete(data))

@app.route("/admin/delete_programmer" , methods=['POST'])
@programmer_token_required
def route_delete_programmer(maintainer):
    data = request.get_json()
    programmers_data = programmers.search_programmer(maintainer)
    if programmers_data.admin == False:
        return jsonify({"status" : "access denied"})
    return jsonify(programmers.delete(data))


@app.route("/admin/black_list" , methods=['POST'])
@programmer_token_required
def route_black_list(maintainer):
    data = request.get_json()
    programmers_data = programmers.search_programmer(maintainer)
    if programmers_data.admin == False:
        return jsonify({"status" : "access denied"})
    st1 = programmers.black_list(data)['status']
    st2 = users.black_list(data)['status']
    if st1 == "successful" or st2 == "successful":
        return jsonify({"status" : "successful"})     
    return jsonify({"status" : "not found"})

@app.route("/admin/white_list" , methods=['POST'])
@programmer_token_required
def route_white_list(maintainer):
    data = request.get_json()
    programmers_data = programmers.search_programmer(maintainer)
    if programmers_data.admin == False:
        return jsonify({"status" : "access denied"})
    st1 = programmers.white_list(data)['status']
    st2 = users.white_list(data)['status']
    if st1 == "successful" or st2 == "successful":
        return jsonify({"status" : "successful"})     
    return jsonify({"status" : "not found"})

@app.route("/admin/grant" , methods=['POST'])
@programmer_token_required
def route_grant_admin(maintainer):
    data = request.get_json()
    programmers_data = programmers.search_programmer(maintainer)
    if programmers_data.admin == False:
        return jsonify({"status" : "access denied"})
    return jsonify(programmers.grant(data))

@app.route("/admin/revoke" , methods=['POST'])
@programmer_token_required
def route_revoke_admin(maintainer):
    data = request.get_json()
    programmers_data = programmers.search_programmer(maintainer)
    if programmers_data.admin == False:
        return jsonify({"status" : "access denied"})
    return jsonify(programmers.revoke(data))

