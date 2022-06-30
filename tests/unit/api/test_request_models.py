import pytest
from pydantic import ValidationError

from metadata_service.api.request_models import MetadataQuery
from metadata_service.exceptions.exceptions import RequestValidationException


def test_metadata_query_correct_version():
    query = MetadataQuery(
        version='1.0.0.0'
    )
    assert query.version == '1_0_0_0'


def test_metadata_query_no_version():
    with pytest.raises(ValidationError) as e:
        MetadataQuery()
    assert "('version',)" in str(e)


def test_metadata_query_invalid_version():
    with pytest.raises(RequestValidationException) as e:
        MetadataQuery(
            version='1.0.0'
        )
    assert 'Version is in incorrect format' in e.value.message['message']


def test_metadata_query_invalid_version2():
    with pytest.raises(RequestValidationException) as e:
        MetadataQuery(
            version='1.0.0.0.0'
        )
    assert 'Version is in incorrect format' in e.value.message['message']


def test_metadata_query_invalid_version3():
    with pytest.raises(RequestValidationException) as e:
        MetadataQuery(
            version='1_0_0_0'
        )
    assert 'Version is in incorrect format' in e.value.message['message']


def test_metadata_query_draft_version():
    query = MetadataQuery(
        version='0.0.0.12345'
    )
    assert query.version == 'DRAFT'


def test_metadata_query_names_as_str():
    query = MetadataQuery(
        names='a,b',
        version='1.0.0.0'
    )
    assert isinstance(query.names, list)


def test_metadata_query_names_as_list():
    query = MetadataQuery(
        names=['a', 'b'],
        version='1.0.0.0'
    )
    assert isinstance(query.names, list)


def test_metadata_query_invalid_names():
    with pytest.raises(RequestValidationException) as e:
        MetadataQuery(
            names={'a'},
            version='1.0.0.0'
        )
    assert 'names field must be a list or a string' in e.value.message['message']
