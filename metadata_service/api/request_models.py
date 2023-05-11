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
    skip_code_lists: bool = False

    @validator('names', pre=True)
    @classmethod
    def split_str(cls, names):
        if isinstance(names, List):
            return names[0].split(',')
        elif isinstance(names, str):
            return names.split(',')
        else:
            raise RequestValidationException(
                'names field must be a list or a string'
            )

    @validator('version', pre=True)
    @classmethod
    def validate_version(cls, version: str):
        if not SEMVER_4_PARTS_REG_EXP.match(version):
            raise RequestValidationException(
                f'Version is in incorrect format: {version}. '
                'Should consist of 4 parts, e.g. 1.0.0.0'
            )
        return version


class NameParam(BaseModel, extra=Extra.forbid):
    names: str

    def get_names_as_list(self) -> List[str]:
        return self.names.split(',')
