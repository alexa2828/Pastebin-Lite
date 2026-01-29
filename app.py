from flask import Flask, jsonify, render_template, request
from services.api_services import api_bp
app = Flask(__name__)
from mongoengine import connect
import os
from urllib.parse import quote_plus

username = os.environ.get("MONGO_USERNAME")
password = os.environ.get("MONGO_PASSWORD")
database_name = os.environ.get("MONGO_DB_NAME")

if not all([username, password, database_name]):
    raise RuntimeError("Missing MongoDB environment variables")

encoded_password = quote_plus(password)

MONGO_URI = (
    f"mongodb+srv://{username}:{encoded_password}"
    f"@cluster0.hcdteph.mongodb.net/{database_name}"
    "?retryWrites=true&w=majority"
)
connect(
    host=MONGO_URI,
    serverSelectionTimeoutMS=5000
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