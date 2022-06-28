import json
import os


def get_pending_operations() -> dict:
    pending_operations_json = (
        f'{os.environ["DATASTORE_ROOT_DIR"]}/datastore/pending_operations.json'
    )
    with open(pending_operations_json, encoding="utf-8") as f:
        return json.load(f)


def get_datastore_versions() -> dict:
    datastore_versions_json = (
        f'{os.environ["DATASTORE_ROOT_DIR"]}/datastore/datastore_versions.json'
    )
    with open(datastore_versions_json, encoding="utf-8") as f:
        return json.load(f)


def get_metadata_all(version: str) -> str:
    metadata_all_file_path = (
        f'{os.environ["DATASTORE_ROOT_DIR"]}/datastore/'
        f'metadata_all__{version}.json'
    )
    with open(metadata_all_file_path, 'r') as f:
        return json.load(f)
