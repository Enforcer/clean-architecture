from flask import Blueprint, Response, abort, jsonify, make_response
from flask_login import current_user

from shipping import GetNextPackage

# from shipping.application.use_cases import ...

shipping_blueprint = Blueprint("shipping_blueprint", __name__)


@shipping_blueprint.route("/package")
def get_next_package(query: GetNextPackage) -> Response:
    return make_response(jsonify(query.query()))


@shipping_blueprint.route("/package/<package_uuid>/send", methods=["POST"])
def send_package(package_uuid: str) -> Response:
    if not current_user.is_authenticated:
        abort(403)

    return make_response()
