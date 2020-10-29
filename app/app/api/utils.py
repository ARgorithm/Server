from flask import jsonify , make_response , request
from ..core.database import users
import jwt
import os
from functools import wraps
from ..main import app

def token_required(f): 
    @wraps(f) 
    def decorated(*args, **kwargs): 
        if app.config["AUTH"] != "ENABLED":
            return f(app.config["ADMIN_EMAIL"],*args , **kwargs)
        
        token = None
        if 'x-access-token' in request.headers: 
            token = request.headers['x-access-token'] 
        
        if not token: 
            return jsonify({
                'status' : False,
                'message' : 'Token is missing !!'
                }), 401
   
        try: 
            # decoding the payload to fetch the stored details 
            data = jwt.decode(token, app.config['SECRET_KEY']) 
            current_user = users.search_public_id(data['public_id']).email
        except: 
            return jsonify({ 
                'status' : False,
                'message' : 'Token is invalid !!'
            }), 401
        # returns the current logged in users contex to the routes 
        return  f(current_user, *args, **kwargs) 
   
    return decorated 

def auth_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        if app.config["AUTH"] != "ENABLED":
            return jsonify({
                "status" : "operation not allowed",
                "message" : "authentication and authorization feature is disabled"
            }) , 400
        return f(*args,**kwargs)
    return decorated