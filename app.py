from flask import Flask, request, jsonify
from flask_cors import CORS

from scraper import search_shopping_list

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return {
        "status": "ok",
        "message": "SmartNakup API běží"
    }

@app.route("/api/search", methods=["POST"])
def search():

    data = request.get_json()

    items = data.get("items", [])

    result = search_shopping_list(items)

    return jsonify(result)

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )