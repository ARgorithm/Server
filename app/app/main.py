from flask import Flask
import os

app = Flask(__name__)

config_keys = [
    "SECRET_KEY" , "AUTH" , "MAIL" ,
    "DATABASE" , "DB_USERNAME" , "DB_PASSWORD" ,
    "ADMIN_EMAIL" , "ADMIN_PASSWORD"
]

for KEY in config_keys:
    app.config[KEY] = os.getenv(KEY)

from .core import app_setup

if __name__ == "__main__":
    # Only for debugging while developing
    with open('uploads/__init__.py','w') as init:
        init.write("") 
    app.run(host="0.0.0.0", debug=True, port=80)
