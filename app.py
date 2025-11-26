from flask import Flask, Blueprint, jsonify, render_template
from threading import Thread
from backend import fetcher, latest_times

app = Flask(__name__)

web_bp = Blueprint("web", __name__)
api_bp = Blueprint("api", __name__)

@web_bp.route("/")
def home():
    return render_template("index.html")

@api_bp.route("/latest-times")
def get_latest_times():
    return jsonify(latest_times)

app.register_blueprint(web_bp)
app.register_blueprint(api_bp)

if __name__ == "__main__":
    Thread(target=fetcher, daemon=True).start()
    app.run(host="127.0.0.1", port=2200, debug=True)

