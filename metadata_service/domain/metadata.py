from typing import List

from metadata_service.adapter import datastore
from metadata_service.exceptions.exceptions import DataNotFoundException


def find_all_datastore_versions():
    draft_version = datastore.get_draft_version()
    datastore_versions = datastore.get_datastore_versions()

    if draft_version:
        datastore_versions['versions'].insert(0, draft_version)

    return datastore_versions


def find_current_data_structure_status(datastructure_name: str):
    datastore_versions = find_all_datastore_versions()
    for version in datastore_versions['versions']:
        dataset = next(
            (ds for ds in version['dataStructureUpdates'] if datastructure_name == ds['name']),
            None)
        if dataset:
            return {
                'name': datastructure_name,
                'operation': dataset['operation'],
                'releaseTime': version['releaseTime'],
                'releaseStatus': "DRAFT" if version['version'].startswith('0.0.0.') else 'RELEASED'
            }

    raise DataNotFoundException(datastructure_name)


def find_data_structures(names: List[str], version: str, include_attributes: bool):
    metadata_all = datastore.get_metadata_all(version)
    if names:
        matched = [ds for ds in metadata_all['dataStructures'] if ds['name'] in names]
    else:
        matched = metadata_all['dataStructures']

    for match in matched:
        if not include_attributes:
            match.pop('attributeVariables', None)
    return matched


def find_all_metadata(version):
    return datastore.get_metadata_all(version)


def find_languages():
    return [
        {
            'code': 'no',
            'label': 'Norsk'
        },
    ]
