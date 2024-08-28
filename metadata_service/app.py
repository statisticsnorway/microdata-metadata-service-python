import logging

import msgpack
from flask import Flask, Response, request, jsonify, make_response
from werkzeug.exceptions import NotFound, HTTPException

from metadata_service.api.metadata_api import metadata_api
from metadata_service.api.observability import observability
from metadata_service.config.logging import setup_logging
from metadata_service.exceptions.exceptions import (
    DataNotFoundException,
    InvalidStorageFormatException,
    RequestValidationException,
    InvalidDraftVersionException,
)


logger = logging.getLogger()

app = Flask(__name__)
app.register_blueprint(observability)
app.register_blueprint(metadata_api)

setup_logging(app)


@app.after_request
def after_request(response: Response):
    if (
        "Accept" in request.headers
        and request.headers["Accept"] == "application/x-msgpack"
    ):
        # create a new Response to send the payload only as "data" field
        response_msgpack = make_response(msgpack.dumps(response.json))
        response_msgpack.headers.set("Content-Type", "application/x-msgpack")
        return response_msgpack

    return response


@app.errorhandler(Exception)
def handle_generic_exception(exc):
    logger.exception(exc)
    return (
        jsonify(
            {
                "code": 202,
                "message": f"Error: {str(exc)}",
                "service": "metadata-service",
                "type": "SYSTEM_ERROR",
            }
        ),
        500,
    )


@app.errorhandler(NotFound)
def handle_url_invalid(exc):
    logger.warning(exc, exc_info=True)
    return (
        jsonify(
            {
                "code": 103,
                "message": f"Error: {str(exc)}",
                "service": "metadata-service",
                "type": "PATH_NOT_FOUND",
            }
        ),
        400,
    )

@app.errorhandler(HTTPException)
def handle_http_exception(exc: HTTPException):
    if str(exc.code).startswith("4"):
        logger.warning(exc, exc_info=True)
        error_type = "BAD_REQUEST"
    else:
        logger.exception(exc)
        error_type = "HTTP_ERROR"
    return (
        jsonify(
            {
                "code": exc.code,
                "message": f"Error: {str(exc.description)}",
                "service": "metadata-service",
                "type": f"{error_type}",
            }
        ),
        exc.code,
    )


@app.errorhandler(DataNotFoundException)
def handle_data_not_found(exc):
    logger.warning(exc, exc_info=True)
    return jsonify(exc.to_dict()), 404


@app.errorhandler(InvalidDraftVersionException)
def handle_invalid_draft(exc):
    logger.warning(exc, exc_info=True)
    return str(exc), 404


@app.errorhandler(RequestValidationException)
def handle_invalid_request(exc):
    logger.warning(exc, exc_info=True)
    return jsonify(exc.to_dict()), 400


@app.errorhandler(InvalidStorageFormatException)
def handle_invalid_format(exc):
    logger.exception(exc)
    return jsonify(exc.to_dict()), 500


# this is needed to run the application in IDE
if __name__ == "__main__":
    app.run(port=8000, host="0.0.0.0")
