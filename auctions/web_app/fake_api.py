import base64
import uuid

from flask import Flask, abort, jsonify, request

app = Flask(__name__)


@app.route("/api/v1/charge", methods=["POST"])
def hello_world():
    assert "Authorization" in request.headers
    _, basic_auth = request.headers["Authorization"].split(" ")
    if base64.b64decode(basic_auth) != b"login:pass":
        abort(403)

    assert "card_token" in request.json
    assert "currency" in request.json
    assert "amount" in request.json
    return jsonify({"success": True, "charge_uuid": str(uuid.uuid4())})
