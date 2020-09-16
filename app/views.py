from app import app
from flask_cors import CORS, cross_origin
from flask import request

CORS(app, support_credentials=True)

@app.route('/',methods=["GET"])
@cross_origin(supports_credentials=True)
def sample():
   return "Hello World"