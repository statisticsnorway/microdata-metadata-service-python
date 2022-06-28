
from flask import Blueprint, Response

openapi_docs = Blueprint('openapi_docs', __name__)


@openapi_docs.route('/docs', methods=['GET'])
def docs():
    with open('metadata_service/static/redoc.html') as f:
        file_contents = f.read()

    return Response(file_contents, mimetype="text/html")
