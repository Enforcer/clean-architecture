import dataclasses

from flask import Blueprint, Response, abort, jsonify, make_response
from flask_login import current_user

from shipping import GetNextPackage, ShippingPackage  # ShippingPackageInputDto

# import uuid


# from shipping.domain.exceptions import PackageAlreadyShipped

shipping_blueprint = Blueprint("shipping_blueprint", __name__)


@shipping_blueprint.route("/package")
def get_next_package(query: GetNextPackage) -> Response:
    result = query.query()
    if not result:
        abort(404)
    return make_response(jsonify(dataclasses.asdict(result)))


@shipping_blueprint.route("/package/<package_uuid>/ship", methods=["POST"])
def ship_package(package_uuid: str, shipping_package_uc: ShippingPackage) -> Response:
    if not current_user.is_authenticated:
        abort(403)
    # try:
    #     shipping_package_uc.execute(ShippingPackageInputDto(uuid.UUID(package_uuid)))
    # except PackageAlreadyShipped:
    #     abort(make_response(jsonify({"message": f"Package '{package_uuid}' has been shipped already"}), 400))
    # return make_response(jsonify({"message": f"Package '{package_uuid}' shipped successfully"}))
    return make_response()
