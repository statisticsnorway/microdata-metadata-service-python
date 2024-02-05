from flask import Blueprint


observability = Blueprint("observability", __name__)


@observability.get("/health/alive")
def alive():
    return "I'm alive!"


@observability.get("/health/ready")
def ready():
    return "I'm ready!"
