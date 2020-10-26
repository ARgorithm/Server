from flask import Flask

app = Flask(__name__)

from .core import app_setup


if __name__ == "__main__":
    # Only for debugging while developing
    with open('uploads/__init__.py','w') as init:
        init.write("") 
    app.run(host="0.0.0.0", debug=True, port=80)
