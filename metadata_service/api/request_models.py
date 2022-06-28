import re
from typing import List

from pydantic import BaseModel, Extra, validator

SEMVER_4_PARTS_REG_EXP = re.compile(r"^([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)$")


class MetadataQuery(BaseModel, extra=Extra.forbid, validate_assignment=True):
    names: List[str] = []
    version: str
    include_attributes: bool = False

    @validator('names', pre=True)
    def split_str(cls, v):
        if isinstance(v, List):
            return v[0].split(',')
        elif isinstance(v, str):
            return v.split(',')
        else:
            raise ValueError('names field must be a list or a string')

    @validator('version', pre=True)
    def to_file_version(cls, v: str):
        if not SEMVER_4_PARTS_REG_EXP.match(v):
            msg = f'Version is in incorrect format: {v}. '
            'Should consist of 4 parts, e.g. 1.0.0.0".'
            raise ValueError(
                msg,
                {
                    "type": "REQUEST_VALIDATION_ERROR",
                    "code": 106,
                    "service": "data-store",
                    "version": v,
                    "message": msg
                })
        dot_count = v.count('.')
        if v.startswith('0.0.0') and dot_count == 3:
            return 'DRAFT'
        else:
            return v.replace('.', '_')


class NameParam(BaseModel, extra=Extra.forbid):
    name: str
