import logging

from flask import Blueprint, jsonify
from flask_pydantic import validate

from metadata_service.api.request_models import NameParam, MetadataQuery
from metadata_service.domain import metadata

logger = logging.getLogger()
metadata_api = Blueprint('metadata_api', __name__)


@metadata_api.route('/metadata/data-store', methods=['GET'])
@validate()
def get_data_store():
    logger.info(f'GET /metadata/data-store')

    response = jsonify(metadata.find_all_datastore_versions())
    response.headers.set('content-language', 'no')
    return response


@metadata_api.route('/metadata/data-structures/status', methods=['GET'])
@validate()
def get_data_structure_current_status(query: NameParam):
    logger.info(f'GET /metadata/data-structures/status with name = {query.name}')

    response = jsonify(metadata.find_current_data_structure_status(query.name))
    response.headers.set('content-language', 'no')
    return response


@metadata_api.route('/metadata/data-structures', methods=['GET'])
@validate()
def get_data_structures(query: MetadataQuery):
    query.include_attributes = True
    logger.info(f'GET /metadata/data-structures with query: {query}')

    response = jsonify(metadata.find_data_structures(
        query.names,
        query.version,
        query.include_attributes
    ))
    response.headers.set('content-language', 'no')
    return response


@metadata_api.route('/metadata/all', methods=['GET'])
@validate()
def get_all_metadata(query: MetadataQuery):
    logger.info(f'GET /metadata/all with version: {query.version}')

    response = jsonify(metadata.find_all_metadata(
        query.version
    ))
    response.headers.set('content-language', 'no')
    return response


@metadata_api.route('/languages', methods=['GET'])
@validate()
def get_languages():
    logger.info(f'GET /languages')

    response = jsonify(metadata.find_languages())
    return response
