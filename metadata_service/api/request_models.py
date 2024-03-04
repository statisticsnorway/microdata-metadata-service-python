import re
from typing import List

from pydantic import BaseModel, field_validator

from metadata_service.exceptions.exceptions import RequestValidationException

SEMVER_4_PARTS_REG_EXP = re.compile(
    r"^([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)$"
)


class MetadataQuery(BaseModel, extra="forbid", validate_assignment=True):
    names: List[str] = []
    version: str
    include_attributes: bool = False
    skip_code_lists: bool = False

    @field_validator("names", mode="before")
    @classmethod
    def split_str(cls, names):
        if isinstance(names, List):
            return names[0].split(",")
        elif isinstance(names, str):
            return names.split(",")
        else:
            raise RequestValidationException(
                "names field must be a list or a string"
            )

    @field_validator("version", mode= "before")
    @classmethod
    def validate_version(cls, version: str):
        if not SEMVER_4_PARTS_REG_EXP.match(version):
            raise RequestValidationException (
                f"Version is in incorrect format: {version}. "
                "Should consist of 4 parts, e.g. 1.0.0.0"
            )
        return version


class NameParam(BaseModel, extra="forbid"):
    names: str

    def get_names_as_list(self) -> List[str]:
        return self.names.split(",")
