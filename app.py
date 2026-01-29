from flask import Flask, jsonify, render_template, request
from pymongo.errors import ServerSelectionTimeoutError 
from services.api_services import api_bp
from env import username, password, database_name
app = Flask(__name__)
from mongoengine import connect
from urllib.parse import quote_plus

encoded_password = quote_plus(password)

MONGO_URI = (
    f"mongodb+srv://{username}:{encoded_password}"
    f"@cluster0.hcdteph.mongodb.net/{database_name}"
    "?retryWrites=true&w=majority"
)
connect(host=MONGO_URI)

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