import json

from metadata_service.adapter import datastore
from metadata_service.domain import metadata

METADATA_ALL_FILE_PATH = (
    'tests/resources/fixtures/domain/metadata_all.json'
)
DATASTORE_VERSIONS_FILE_PATH = (
    'tests/resources/fixtures/domain/datastore_versions.json'
)
DRAFT_VERSION_FILE_PATH = (
    'tests/resources/fixtures/domain/draft_version.json'
)
DATA_STRUCTURES_FILE_PATH = (
    'tests/resources/fixtures/api/data_structures.json'
)

METADATA_ALL_NO_CODE_LIST_FILE_PATH = (
    'tests/resources/fixtures/domain/metadata_all_no_code_list__1_0_0_0.json'
)

DATA_STRUCTURES_NO_CODE_LIST_FILE_PATH = (
    'tests/resources/fixtures/api/data_structures_no_code_list.json'
)

def test_find_two_data_structures_with_attrs(mocker):
    with open(METADATA_ALL_FILE_PATH, encoding='utf-8') as f:
        mocked_metadata_all = json.load(f)
    mocker.patch.object(
        datastore, 'get_metadata_all',
        return_value=mocked_metadata_all
    )
    actual = metadata.find_data_structures(
        ['TEST_PERSON_INCOME', 'TEST_PERSON_PETS'],
        '1_0_0',
        True,
        skip_code_lists=False
    )
    assert len(actual) == 2
    income = next(  
        data_structure for data_structure
        in mocked_metadata_all["dataStructures"]
        if data_structure["name"] == 'TEST_PERSON_INCOME'
    )
    assert 'attributeVariables' in income
    pets = next(
        data_structure for data_structure
        in mocked_metadata_all["dataStructures"]
        if data_structure["name"] == 'TEST_PERSON_PETS'
    )
    assert 'attributeVariables' in pets


def test_find_two_data_structures_without_attrs(mocker):
    with open(METADATA_ALL_FILE_PATH, encoding='utf-8') as f:
        mocked_metadata_all = json.load(f)
    mocker.patch.object(
        datastore, 'get_metadata_all',
        return_value=mocked_metadata_all
    )
    actual = metadata.find_data_structures(
        ['TEST_PERSON_INCOME', 'TEST_PERSON_PETS'],
        '1_0_0',
        False,
        skip_code_lists=False
    )
    assert len(actual) == 2
    income = next(
        data_structure for data_structure
        in mocked_metadata_all["dataStructures"]
        if data_structure["name"] == 'TEST_PERSON_INCOME'
    )
    assert 'attributeVariables' not in income
    pets = next(
        data_structure for data_structure
        in mocked_metadata_all["dataStructures"]
        if data_structure["name"] == 'TEST_PERSON_PETS'
    )
    assert 'attributeVariables' not in pets


def test_find_data_structures_no_name_filter(mocker):
    with open(METADATA_ALL_FILE_PATH, encoding='utf-8') as f:
        mocked_metadata_all = json.load(f)
    mocker.patch.object(
        datastore, 'get_metadata_all',
        return_value=mocked_metadata_all
    )
    actual = metadata.find_data_structures(
        [],
        '1_0_0',
        True,
        skip_code_lists=False
    )
    assert len(actual) == 2


def test_find_current_data_structure_status_released(mocker):
    with open(DATASTORE_VERSIONS_FILE_PATH, encoding='utf-8') as f:
        mocked_datastore_versions = json.load(f)
    with open(DRAFT_VERSION_FILE_PATH, encoding='utf-8') as f:
        mocked_draft_version = json.load(f)
    mocker.patch.object(
        datastore, 'get_datastore_versions',
        return_value=mocked_datastore_versions
    )
    mocker.patch.object(
        datastore, 'get_draft_version',
        return_value=mocked_draft_version
    )
    actual = metadata.find_current_data_structure_status(
        'TEST_PERSON_INCOME'
    )
    assert actual == {
        "name": "TEST_PERSON_INCOME",
        "operation": "ADD",
        "releaseTime": 1607332752,
        "releaseStatus": "RELEASED"
    }


def test_find_current_data_structure_status_draft(mocker):
    with open(DATASTORE_VERSIONS_FILE_PATH, encoding='utf-8') as f:
        mocked_datastore_versions = json.load(f)
    with open(DRAFT_VERSION_FILE_PATH, encoding='utf-8') as f:
        mocked_draft_version = json.load(f)
    mocker.patch.object(
        datastore, 'get_datastore_versions',
        return_value=mocked_datastore_versions
    )
    mocker.patch.object(
        datastore, 'get_draft_version',
        return_value=mocked_draft_version
    )
    actual = metadata.find_current_data_structure_status(
        'TEST_PERSON_HOBBIES'
    )
    assert actual == {
        "name": "TEST_PERSON_HOBBIES",
        "operation": "ADD",
        "releaseTime": 1608000000,
        "releaseStatus": "DRAFT"
    }


def test_find_all_datastore_versions(mocker):
    with open(DATASTORE_VERSIONS_FILE_PATH, encoding='utf-8') as f:
        mocked_datastore_versions = json.load(f)
    with open(DRAFT_VERSION_FILE_PATH, encoding='utf-8') as f:
        mocked_draft_version = json.load(f)
    mocker.patch.object(
        datastore, 'get_datastore_versions',
        return_value=mocked_datastore_versions
    )
    mocker.patch.object(
        datastore, 'get_draft_version',
        return_value=mocked_draft_version
    )
    actual = metadata.find_all_datastore_versions()
    assert len(actual['versions']) == 2
    assert actual['versions'][0]['version'] == '0.0.0.1608000000'
    assert actual['versions'][1]['version'] == '1.0.0.0'


def test_find_all_datastore_versions_when_draft_version_empty(mocker):
    with open(DATASTORE_VERSIONS_FILE_PATH, encoding='utf-8') as f:
        mocked_datastore_versions = json.load(f)
    mocker.patch.object(
        datastore, 'get_datastore_versions',
        return_value=mocked_datastore_versions
    )
    mocker.patch.object(
        datastore, 'get_draft_version',
        return_value={}
    )
    actual = metadata.find_all_datastore_versions()
    assert len(actual['versions']) == 1
    assert actual['versions'][0]['version'] == '1.0.0.0'

def test_find_all_metadata_skip_code_list_and_missing_values_for_metadata_all(mocker):
    
    with open(METADATA_ALL_FILE_PATH, encoding='utf-8') as f:
        mocked_metadata_all = json.load(f)

    mocker.patch.object(
        datastore, 'get_metadata_all',
        return_value=mocked_metadata_all
    )
    
    filtered_metadata = metadata.find_all_metadata_skip_code_list_and_missing_values(version='1.0.0.0')
    __assert_code_list_and_missing_values(filtered_metadata['dataStructures'])

    with open(METADATA_ALL_NO_CODE_LIST_FILE_PATH, encoding='utf-8') as f:
        metadata_no_code_list = json.load(f)

    assert metadata_no_code_list == filtered_metadata

def test_find_all_metadata_skip_code_list_and_missing_values_for_data_structures(mocker):
    
    with open(DATA_STRUCTURES_FILE_PATH, encoding='utf-8') as f:
        mocked_data_structures = json.load(f)

    mocker.patch.object(
        datastore, 'get_metadata_all',
        return_value=mocked_data_structures
    )
    
    filtered_metadata = metadata.find_all_metadata_skip_code_list_and_missing_values(version='1.0.0.0')
    __assert_code_list_and_missing_values(filtered_metadata)

    with open(DATA_STRUCTURES_NO_CODE_LIST_FILE_PATH, encoding='utf-8') as f:
        data_structures_no_code_list = json.load(f)

    assert data_structures_no_code_list == filtered_metadata

def __assert_code_list_and_missing_values(metadata):

    for md in metadata:
        for av in md['attributeVariables']:
            for rv in av['representedVariables']:
                if 'codeLists' in rv['valueDomain']: 
                    assert rv['valueDomain']['codeList'] == []
                if 'missingValues' in rv['valueDomain']: 
                    assert rv['valueDomain']['missingValues'] == []     
        for iv in md['identifierVariables']:
            for rv in iv['representedVariables']:
                if 'codeList' in rv['valueDomain']:
                    assert rv['valueDomain']['codeList'] == []
                if 'missingValues' in rv['valueDomain']:
                    assert rv['valueDomain']['missingValues'] == []
        for rv in md['measureVariable']['representedVariables']:
            if 'codeList' in rv['valueDomain']: 
                assert rv['valueDomain']['codeList'] == []
            if 'missingValues' in rv['valueDomain']: 
                assert rv['valueDomain']['missingValues'] == []

