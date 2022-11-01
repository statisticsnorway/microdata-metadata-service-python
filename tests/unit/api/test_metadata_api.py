import json

import msgpack
from flask import url_for, Response

from metadata_service.domain import metadata

MOCKED_DATASTORE_VERSIONS = {
    "name": "SSB-RAIRD",
    "label": "SSB datastore",
    "description": "Inneholder SSB databaser med data siden 1970 :-)",
    "versions": [
        {
            "version": "3.2.0.0",
            "description": "Denne versjonen handler om nye inntektsvariabler",
            "releaseTime": 123456,
            "languageCode": "no",
            "dataStructureUpdates": [
                {
                    "description": "string",
                    "name": "INNTEKT_TJENPEN",
                    "operation": "ADD"
                },
                {
                    "description": "string",
                    "name": "INNTEKT_BANKINNSK",
                    "operation": "ADD"
                }
            ],
            "updateType": "MINOR"
        }
    ],
    "languageCode": "no"
}

MOCKED_DATASTRUCTURE = {
    "description": "dummy",
    "name": "INNTEKT_TJENPEN",
    "operation": "ADD",
    "releaseTime": 123123
}

MOCKED_LANGUAGES = [
    {
        'code': 'no',
        'label': 'Norsk'
    },
    {
        'code': 'en',
        'label': 'English'
    }
]

DATA_STRUCTURES_FILE_PATH = (
    'tests/resources/fixtures/api/data_structures.json'
)
METADATA_ALL_FILE_PATH = (
    'tests/resources/fixtures/domain/metadata_all.json'
)

def test_get_data_store(flask_app, mocker):
    spy = mocker.patch.object(
        metadata, 'find_all_datastore_versions',
        return_value=MOCKED_DATASTORE_VERSIONS
    )
    response: Response = flask_app.get(
        url_for('metadata_api.get_data_store'),
        headers={
            'X-Request-ID': 'test-123',
            'Accept-Language': 'no',
            'Accept': 'application/json'
        })
    spy.assert_called()
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json == MOCKED_DATASTORE_VERSIONS


def test_get_current_data_structure_status(flask_app, mocker):
    spy = mocker.patch.object(
        metadata, 'find_current_data_structure_status',
        return_value=MOCKED_DATASTRUCTURE
    )
    response: Response = flask_app.get(
        url_for(
            'metadata_api.get_data_structure_current_status',
            name='INNTEKT_TJENPEN'
        ),
        headers={
            'X-Request-ID': 'test-123',
            'Accept-Language': 'no',
            'Accept': 'application/json'
        })
    spy.assert_called_with(
        MOCKED_DATASTRUCTURE['name']
    )
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json == MOCKED_DATASTRUCTURE


def test_get_data_structures(flask_app, mocker):
    with open(DATA_STRUCTURES_FILE_PATH, encoding='utf-8') as f:
        mocked_data_structures = json.load(f)

    spy = mocker.patch.object(
        metadata, 'find_data_structures',
        return_value=mocked_data_structures
    )
    response: Response = flask_app.get(
        url_for('metadata_api.get_data_structures',
                names='FNR,AKT_ARBAP',
                version='3.2.1.0'
                ),
        headers={
            'X-Request-ID': 'test-123',
            'Accept-Language': 'no',
            'Accept': 'application/json'
        })
    spy.assert_called_with(
        ['FNR', 'AKT_ARBAP'],
        '3_2_1',
        True,
        False
    )
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json == mocked_data_structures


def test_get_data_structures_with_messagepack(flask_app, mocker):
    with open(DATA_STRUCTURES_FILE_PATH, encoding='utf-8') as f:
        mocked_data_structures = json.load(f)

    spy = mocker.patch.object(
        metadata, 'find_data_structures',
        return_value=mocked_data_structures
    )
    response: Response = flask_app.get(
        url_for('metadata_api.get_data_structures',
                names='FNR,AKT_ARBAP',
                version='3.2.1.0'
                ),
        headers={
            'X-Request-ID': 'test-123',
            'Accept-Language': 'no',
            'Accept': 'application/x-msgpack'
        })
    spy.assert_called_with(
        ['FNR', 'AKT_ARBAP'],
        '3_2_1',
        True,
        False
    )
    assert response.headers['Content-Type'] == 'application/x-msgpack'
    assert msgpack.loads(response.data) == mocked_data_structures


def test_get_all_metadata(flask_app, mocker):
    with open(DATA_STRUCTURES_FILE_PATH, encoding='utf-8') as f:
        mocked_data_structures = json.load(f)
    mocked_metadata_all = {
        "dataStore": {
            "name": "dummy datastore name",
            "label": "dummy datastore label",
            "description": "dummy datastore description",
            "languageCode": "no"
        },
        "languages": MOCKED_LANGUAGES,
        "dataStructures": mocked_data_structures
    }

    spy = mocker.patch.object(
        metadata, 'find_all_metadata',
        return_value=mocked_metadata_all
    )
    response: Response = flask_app.get(
        url_for('metadata_api.get_all_metadata',
                version='3.2.1.0'
                ),
        headers={
            'X-Request-ID': 'test-123',
            'Accept-Language': 'no',
            'Accept': 'application/json'
        })
    spy.assert_called_with(
        '3_2_1',
        False
    )
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json == mocked_metadata_all

def test_get_all_metadata_long_version_numbers(flask_app, mocker):
    with open(DATA_STRUCTURES_FILE_PATH, encoding='utf-8') as f:
        mocked_data_structures = json.load(f)
    mocked_metadata_all = {
        "dataStore": {
            "name": "dummy datastore name",
            "label": "dummy datastore label",
            "description": "dummy datastore description",
            "languageCode": "no"
        },
        "languages": MOCKED_LANGUAGES,
        "dataStructures": mocked_data_structures
    }

    spy = mocker.patch.object(
        metadata, 'find_all_metadata',
        return_value=mocked_metadata_all
    )
    response: Response = flask_app.get(
        url_for('metadata_api.get_all_metadata',
                version='1234.5678.9012.0'
                ),
        headers={
            'X-Request-ID': 'test-123',
            'Accept-Language': 'no',
            'Accept': 'application/json'
        })
    spy.assert_called_with(
        '1234_5678_9012',
        False
    )
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json == mocked_metadata_all

def test_get_languages(flask_app, mocker):
    spy = mocker.patch.object(
        metadata, 'find_languages',
        return_value=MOCKED_LANGUAGES
    )
    response: Response = flask_app.get(
        url_for('metadata_api.get_languages'),
        headers={
            'X-Request-ID': 'test-123'
        })
    spy.assert_called()
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json == MOCKED_LANGUAGES

def test_get_all_metadata_skip_code_lists(flask_app, mocker):
    with open(METADATA_ALL_FILE_PATH, encoding='utf-8') as f:
        mocked_metadata_all = json.load(f)

    spy = mocker.patch.object(
        metadata, 'find_all_metadata',
        return_value=mocked_metadata_all
    )
    response: Response = flask_app.get(
        url_for('metadata_api.get_all_metadata',
                version='3.2.1.0',
                skip_code_lists=True
                ),
        headers={
            'X-Request-ID': 'test-123',
            'Accept-Language': 'no',
            'Accept': 'application/json'
        })
    spy.assert_called_with(
        '3_2_1',
        True
    )
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json == mocked_metadata_all

def test_get_data_structures_skip_code_lists(flask_app, mocker):
    with open(DATA_STRUCTURES_FILE_PATH, encoding='utf-8') as f:
        mocked_data_structures = json.load(f)

    spy = mocker.patch.object(
        metadata, 'find_data_structures',
        return_value=mocked_data_structures
    )
    response: Response = flask_app.get(
        url_for('metadata_api.get_data_structures',
                names='FNR,AKT_ARBAP',
                version='3.2.1.0',
                skip_code_lists=True
                ),
        headers={
            'X-Request-ID': 'test-123',
            'Accept-Language': 'no',
            'Accept': 'application/json'
        })
    spy.assert_called_with(
        ['FNR', 'AKT_ARBAP'],
        '3_2_1',
        True,
        True
    )
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json == mocked_data_structures



