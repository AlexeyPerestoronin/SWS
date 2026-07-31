import re

from enum import Enum
from typing import TypeAlias, List, Optional, Protocol
from pyswx.api.sldworks.interfaces import IBodyFolder
from pyswx.api.swconst.enumerations import SWBodyFolderFeatureTypE

from . import i_feature_utils

__all__ = [
    'FolderNameValidationApproach',
    'ValidFolderName',
    'FolderNameValidator',
    'DefaultFolderNameValidator',
    'validate_and_parse_folder_name',
]


class FolderNameValidationApproach(str, Enum):
    DEFAULT = 'default'


class ValidFolderName:
    FolderName: TypeAlias = str
    AssemblyNameOpt: TypeAlias = Optional[str]
    ConfigurationName: TypeAlias = str

    def __init__(self, folder_name: FolderName, approach: FolderNameValidationApproach):
        self.__folder_name = folder_name
        self.__approach = approach

    @property
    def folder_name(self) -> FolderName:
        return self.__folder_name

    @property
    def approach(self) -> FolderNameValidationApproach:
        return self.__approach


class FolderNameValidator(Protocol):
    """Protocol for validating and parsing a SolidWorks body folder name."""

    @property
    def name(self) -> str:
        ...

    def __call__(self, folder: IBodyFolder) -> Optional[ValidFolderName]:
        ...


class DefaultFolderNameValidator(FolderNameValidator):
    """Default validator that checks folder names against a basic pattern."""

    @property
    def name(self) -> str:
        return 'DefaultFolderNameValidator'

    def __call__(self, folder: IBodyFolder) -> Optional[ValidFolderName]:
        folder_name = folder.name
        folder_name_pattern = r'(?P<folder_name>(\w|\d)*(-(\w|\d)*)*)'
        match = re.fullmatch(folder_name_pattern, folder_name)
        if match:
            groups = match.groupdict()
            folder_name = groups['folder_name']
            return ValidFolderName(folder_name, FolderNameValidationApproach.DEFAULT)
        return None


def validate_and_parse_folder_name(folder: IBodyFolder, *, validators: List[FolderNameValidator] = [DefaultFolderNameValidator()]) -> ValidFolderName:
    """Validate and parse a folder name using the provided validators."""

    for validator in validators:
        valid_folder_name_opt = validator(folder)
        if valid_folder_name_opt:
            return valid_folder_name_opt
    raise Exception(f"folder name '{folder.name}' does not validate any of validators: {[validator.name for validator in validators]}")
