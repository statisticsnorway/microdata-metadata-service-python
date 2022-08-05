from flask import Blueprint


observability = Blueprint("observability", __name__)


@observability.route('/health/alive', methods=["GET"])
def alive():
    return "I'm alive!"


@observability.route('/health/ready', methods=["GET"])
def ready():
    return "I'm ready!"
