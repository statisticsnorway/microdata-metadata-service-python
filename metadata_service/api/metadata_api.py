import logging

from flask import Blueprint, jsonify
from flask_pydantic import validate

from metadata_service.api.request_models import NameParam, MetadataQuery
from metadata_service.domain import metadata
from metadata_service.domain.version import Version

logger = logging.getLogger()
metadata_api = Blueprint("metadata_api", __name__)


@metadata_api.route("/metadata/data-store", methods=["GET"])
@validate()
def get_data_store():
    logger.info("GET /metadata/data-store")

    response = jsonify(metadata.find_all_datastore_versions())
    response.headers.set("content-language", "no")
    return response


@metadata_api.route("/metadata/data-structures/status", methods=["GET"])
@validate()
def get_data_structure_current_status(query: NameParam):
    logger.info(f"GET /metadata/data-structures/status with name = {query.names}")
    response = jsonify(
        metadata.find_current_data_structure_status(query.get_names_as_list())
    )
    response.headers.set("content-language", "no")
    return response


@metadata_api.route("/metadata/data-structures", methods=["GET"])
@validate()
def get_data_structures(query: MetadataQuery):
    query.include_attributes = True
    logger.info(f"GET /metadata/data-structures with query: {query}")

    response = jsonify(
        metadata.find_data_structures(
            query.names,
            Version(query.version),
            query.include_attributes,
            query.skip_code_lists,
        )
    )
    response.headers.set("content-language", "no")
    return response


@metadata_api.route("/metadata/all", methods=["GET"])
@validate()
def get_all_metadata(query: MetadataQuery):
    logger.info(f"GET /metadata/all with version: {query.version}")

    response = jsonify(
        metadata.find_all_metadata(Version(query.version), query.skip_code_lists)
    )
    response.headers.set("content-language", "no")
    return response


@metadata_api.route("/languages", methods=["GET"])
@validate()
def get_languages():
    logger.info("GET /languages")

    response = jsonify(metadata.find_languages())
    return response
