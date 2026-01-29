from flask import Flask, jsonify, render_template, request
import mongoengine
import os 
from pymongo.errors import ServerSelectionTimeoutError 
from services.api_services import api_bp

app = Flask(__name__)

mongoengine.connect(
    db='mydatabase',
    host='localhost',
    port=27017
)

@app.route('/')
def index():
    return render_template("create.html")


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Not found"}), 404
    return render_template("error.html"), 404


app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(debug=True) 