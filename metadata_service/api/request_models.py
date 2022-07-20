import re
from typing import List

from pydantic import BaseModel, Extra, validator

from metadata_service.exceptions.exceptions import RequestValidationException

SEMVER_4_PARTS_REG_EXP = re.compile(
    r"^([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)$"
)


class MetadataQuery(BaseModel, extra=Extra.forbid, validate_assignment=True):
    names: List[str] = []
    version: str
    include_attributes: bool = False

    @validator('names', pre=True)
    @classmethod
    def split_str(cls, v):
        if isinstance(v, List):
            return v[0].split(',')
        elif isinstance(v, str):
            return v.split(',')
        else:
            raise RequestValidationException(
                'names field must be a list or a string'
            )

    @validator('version', pre=True)
    @classmethod
    def to_file_version(cls, v: str):
        if not SEMVER_4_PARTS_REG_EXP.match(v):
            raise RequestValidationException(
                f'Version is in incorrect format: {v}. '
                'Should consist of 4 parts, e.g. 1.0.0.0.'
            )
        dot_count = v.count('.')
        if v.startswith('0.0.0') and dot_count == 3:
            return 'DRAFT'
        else:
            return v.replace('.', '_')


class NameParam(BaseModel, extra=Extra.forbid):
    name: str
