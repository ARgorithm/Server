from flask import jsonify

from ..core.database import users
from ..main import app

@app.route("/users/")
def route_users():
    users_data = users
    return jsonify(users_data)