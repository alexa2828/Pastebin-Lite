from flask import Flask, jsonify, render_template, request
from services.api_services import api_bp
from pymongo import MongoClient
import os
from urllib.parse import quote_plus

app = Flask(__name__)

# ---------------- MongoDB connection ----------------
username = os.environ.get("MONGO_USERNAME")
password = os.environ.get("MONGO_PASSWORD")
database_name = os.environ.get("MONGO_DB_NAME")

if not all([username, password, database_name]):
    raise RuntimeError("Missing MongoDB environment variables")

encoded_password = quote_plus(password)

MONGO_URI = (
    f"mongodb+srv://{username}:{encoded_password}"
    f"@cluster0.hcdteph.mongodb.net/{database_name}"
    "?retryWrites=true"
    "&tls=true"
)

# Create a single global client
mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = mongo_client[database_name]

# Attach the client to Flask app for easy access in views
app.config["MONGO_CLIENT"] = mongo_client
app.config["DB"] = db

# ----------------------------------------------------

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
