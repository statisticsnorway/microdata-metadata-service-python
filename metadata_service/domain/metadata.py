from typing import List

from metadata_service.adapter import datastore
from metadata_service.exceptions.exceptions import DataNotFoundException
import json

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
                'releaseStatus': (
                    'DRAFT' if version['version'].startswith('0.0.0.')
                    else 'RELEASED'
                )
            }
    raise DataNotFoundException(
        f"No data structure named {datastructure_name} was found"
    )


def find_data_structures(
    names: List[str], version: str, include_attributes: bool, skip_code_lists: bool = False
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
    if not skip_code_lists:
        return datastore.get_metadata_all(version)
    else:
        return find_all_metadata_skip_code_list_and_missing_values(version)

def find_languages():
    return [
        {
            'code': 'no',
            'label': 'Norsk'
        },
    ]

def find_all_metadata_skip_code_list_and_missing_values(version):
    metadata = datastore.get_metadata_all(version)
     
    if 'dataStructures' in metadata:
        _clear_code_list_and_missing_values(metadata['dataStructures'])
    else:
        raise DataNotFoundException(f'Expected dataStructures')
    return metadata

def _clear_code_list_and_missing_values(metadata):
    for md in metadata:
        for av in md['attributeVariables']:
            for rv in av['representedVariables']:
                if 'codeList' in rv['valueDomain']:
                    rv['valueDomain']['codeList'].clear()
                if 'missingValues' in rv['valueDomain']:
                    rv['valueDomain']['missingValues'].clear()
        for iv in md['identifierVariables']:
            for rv in iv['representedVariables']:
                if 'codeList' in rv['valueDomain']:
                    rv['valueDomain']['codeList'].clear()
                if 'missingValues' in rv['valueDomain']:
                    rv['valueDomain']['missingValues'].clear()
        for rv in md['measureVariable']['representedVariables']:
                if 'codeList' in rv['valueDomain']:
                    rv['valueDomain']['codeList'].clear()
                if 'missingValues' in rv['valueDomain']:
                    rv['valueDomain']['missingValues'].clear()
    
    return metadata
