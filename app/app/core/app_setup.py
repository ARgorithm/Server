from ..api import routes 
from ..main import app

@app.route("/")
def hello():
    # This could also be returning an index.html
    return """Hello World from Flask in a uWSGI Nginx Docker container with \
     Python 3.8 (from the example template)"""
