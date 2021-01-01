from flask import jsonify , make_response , request
from ..core.database import programmers,users
import jwt
import os
from functools import wraps
from ..main import app

def programmer_token_required(f): 
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
            current_programmer = programmers.search_public_id(data['public_id'])
            if current_programmer.black_list:
                return jsonify({ 
                    'status' : False,
                    'message' : 'Account is blacklisted'
                }), 401
        except: 
            return jsonify({ 
                'status' : False,
                'message' : 'Token is invalid !!'
            }), 401
        # returns the current logged in programmers contex to the routes
        return  f(current_programmer.email, *args, **kwargs) 
   
    return decorated 

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
            try: 
                current_programmer = programmers.search_public_id(data['public_id'])
                res = current_programmer
            except:
                current_user = users.search_public_id(data['public_id'])
                res = current_user
            if res.black_list:
                return jsonify({ 
                    'status' : False,
                    'message' : 'Account is blacklisted'
                }), 401
        except: 
            return jsonify({ 
                'status' : False,
                'message' : 'Token is invalid !!'
            }), 401
        # returns the current logged in programmers contex to the routes 
        return  f(res.email, *args, **kwargs) 
   
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