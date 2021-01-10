import os
from flask import render_template,send_from_directory
from ..api import programmer_routes , argorithm_routes , user_routes , admin_routes
from ..main import app

@app.route("/")
def hello():
    return render_template('index.html')