import logging
import uuid

import json_logging
import msgpack
from flask import Flask, Response, request, jsonify, make_response
from werkzeug.exceptions import NotFound

from metadata_service.api.metadata_api import metadata_api
from metadata_service.api.observability import observability
from metadata_service.config.logging import (
    CustomJSONLog, CustomJSONRequestLogFormatter
)
from metadata_service.exceptions.exceptions import (
    DataNotFoundException, RequestValidationException
)


def init_json_logging():
    json_logging.CREATE_CORRELATION_ID_IF_NOT_EXISTS = True
    json_logging.CORRELATION_ID_GENERATOR = (
        lambda: "metadata-service-" + str(uuid.uuid1())
    )
    json_logging.init_flask(
        enable_json=True,
        custom_formatter=CustomJSONLog
    )
    json_logging.init_request_instrument(
        app, custom_formatter=CustomJSONRequestLogFormatter
    )


logging.getLogger("json_logging").setLevel(logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.register_blueprint(observability)
app.register_blueprint(metadata_api)

init_json_logging()


@app.after_request
def after_request(response: Response):
    response.headers.set(
        'X-Request-ID', json_logging.get_correlation_id(request)
    )
    if (
        'Accept' in request.headers and
        request.headers['Accept'] == 'application/x-msgpack'
    ):
        # create a new Response to send the payload only as "data" field
        response_msgpack = make_response(msgpack.dumps(response.json))
        response_msgpack.headers.set('Content-Type', 'application/x-msgpack')
        return response_msgpack

    return response


@app.errorhandler(Exception)
def handle_generic_exception(exc):
    logger.exception(exc)
    return jsonify({
        'code': 202,
        "message": f"Error: {str(exc)}",
        'service': 'metadata-service',
        'type': 'SYSTEM_ERROR',
    }), 500


@app.errorhandler(NotFound)
def handle_url_invalid(exc):
    logger.exception(exc)
    return jsonify({
        'code': 103,
        "message": f"Error: {str(exc)}",
        'service': 'metadata-service',
        'type': 'PATH_NOT_FOUND',
    }), 400


@app.errorhandler(DataNotFoundException)
def handle_data_not_found(exc):
    logger.exception(exc)
    return jsonify(exc.to_dict()), 404


@app.errorhandler(RequestValidationException)
def handle_invalid_request(exc):
    logger.exception(exc)
    return jsonify(exc.to_dict()), 400


# this is needed to run the application in IDE
if __name__ == "__main__":
    app.run(port=8000, host="0.0.0.0")
