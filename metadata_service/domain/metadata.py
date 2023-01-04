from itertools import chain
from metadata_service.adapter import datastore
from metadata_service.exceptions.exceptions import (
    DataNotFoundException, InvalidStorageFormatException
)


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
            (
                ds for ds in version['dataStructureUpdates']
                if datastructure_name == ds['name']
            ),
            None
        )
        if dataset:
            return {
                'name': datastructure_name,
                'operation': dataset['operation'],
                'releaseTime': version['releaseTime'],
                'releaseStatus': dataset['releaseStatus']
            }
    raise DataNotFoundException(
        f"No data structure named {datastructure_name} was found"
    )


def find_data_structures(
    names: list[str],
    version: str,
    include_attributes: bool,
    skip_code_lists: bool = False
):
    metadata = datastore.get_metadata_all(version) if not skip_code_lists \
        else find_all_metadata_skip_code_list_and_missing_values(version)

    if names:
        matched = [
            ds for ds in metadata['dataStructures'] if ds['name'] in names
        ]
    else:
        matched = metadata['dataStructures']

    for match in matched:
        if not include_attributes:
            match.pop('attributeVariables', None)
    return matched


def find_all_metadata(version, skip_code_lists: bool = False):
    return (
        datastore.get_metadata_all(version) if not skip_code_lists
        else find_all_metadata_skip_code_list_and_missing_values(version)
    )


def find_languages():
    return [
        {
            'code': 'no',
            'label': 'Norsk'
        },
    ]


def find_all_metadata_skip_code_list_and_missing_values(version):
    metadata_all = datastore.get_metadata_all(version)
    if 'dataStructures' in metadata_all:
        _clear_code_list_and_missing_values(metadata_all['dataStructures'])
    else:
        raise InvalidStorageFormatException('Invalid metadata format')
    return metadata_all


def _clear_code_list_and_missing_values(data_structures: list[dict]):
    represented_variables = []
    for metadata in data_structures:
        represented_measure = (
            metadata['measureVariable']['representedVariables']
        )
        represented_identifiers = list(chain(*[
            identifier['representedVariables']
            for identifier in metadata['identifierVariables']
        ]))
        represented_attributes = list(chain(*[
            attribute['representedVariables']
            for attribute in metadata['attributeVariables']
        ]))
        represented_variables += (
            represented_measure
            + represented_identifiers
            + represented_attributes
        )
    for represented_variable in represented_variables:
        if 'codeList' in represented_variable['valueDomain']:
            represented_variable['valueDomain']['codeList'].clear()
        if 'missingValues' in represented_variable['valueDomain']:
            represented_variable['valueDomain']['missingValues'].clear()
