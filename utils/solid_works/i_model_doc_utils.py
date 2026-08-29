import re

from enum import Enum
from typing import TypeAlias, List, Optional, Protocol
from pyswx.api.sldworks.interfaces import IModelDoc2, IBody2, IBodyFolder
from pyswx.api.swconst.enumerations import SWBodyFolderFeatureTypE

__all__ = [
    'ModelNameValidationApproach',
    'ValidModelName',
    'ModelNameValidator',
    'DefaultModelValidator',
    'ISOModelValidator',
    'validate_and_parse_model_name',
]


class ModelNameValidationApproach(str, Enum):
    DEFAULT = "user's defined model-name"
    ISO_COMPONENT = 'ISO component model-name'


class ValidModelName:
    ModelName: TypeAlias = str
    AssemblyNameOpt: TypeAlias = Optional[str]

    def __init__(self, model_name: ModelName, assembly_name: AssemblyNameOpt, configuration_name: str, approach: ModelNameValidationApproach):
        self.__model_name = model_name
        self.__assembly_name = assembly_name
        self.__configuration_name = configuration_name
        self.__approach = approach

    def __str__(self) -> str:
        return f"{self.model_name} ({self.configuration_name})"

    @property
    def model_name(self) -> ModelName:
        return self.__model_name

    @property
    def assembly_name(self) -> AssemblyNameOpt:
        return self.__assembly_name

    @property
    def configuration_name(self) -> str:
        return self.__configuration_name

    @property
    def approach(self) -> ModelNameValidationApproach:
        return self.__approach


class ModelNameValidator(Protocol):
    """Model name validator protocol"""

    @property
    def name(self) -> str:
        ...

    def __call__(self, model: IModelDoc2) -> Optional[ValidModelName]:
        ...


class DefaultModelValidator(ModelNameValidator):
    """User-own model name validator"""

    @property
    def name(self) -> str:
        return str(ModelNameValidationApproach.DEFAULT)

    def __call__(self, model: IModelDoc2) -> Optional[ValidModelName]:
        model_name = model.get_path_name().stem
        model_name_pattern = r'(?P<model_name>[A-ZА-ЯЁ](\w|\d)*(-[A-ZА-ЯЁ](\w|\d)*)*)(\^(?P<assembly_name>[A-ZА-ЯЁ](\w|\d)*(-[A-ZА-ЯЁ](\w|\d)*)*))?'
        match = re.fullmatch(model_name_pattern, model_name)
        if match:
            if re.match(r'(iso|ISO)', model_name):
                raise Exception(f"your own designed model has 'ISO'-abbreviation in its name '{model_name}'")
            groups = match.groupdict()
            model_name = groups['model_name']
            assembly_name = groups.get('assembly_name', None)
            configuration_name = model.configuration_manager.active_configuration.name
            return ValidModelName(model_name, assembly_name, configuration_name, ModelNameValidationApproach.DEFAULT)
        return None


class ISOModelValidator(ModelNameValidator):
    """ISO model name validator"""

    @property
    def name(self) -> str:
        return str(ModelNameValidationApproach.ISO_COMPONENT)

    def __call__(self, model: IModelDoc2) -> Optional[ValidModelName]:
        model_name = model.get_path_name().stem
        model_name_pattern = r'(?P<model_name>.+?_iso)'
        match = re.fullmatch(model_name_pattern, model_name)
        if match:
            groups = match.groupdict()
            model_name = groups['model_name']
            assembly_name = None
            configuration_name = model.configuration_manager.active_configuration.name
            return ValidModelName(model_name, assembly_name, configuration_name, ModelNameValidationApproach.ISO_COMPONENT)
        return None


def validate_and_parse_model_name(model: IModelDoc2, *, validators: List[ModelNameValidator] = [DefaultModelValidator(), ISOModelValidator()]) -> ValidModelName:
    """Validate and parse name of the SW-IModelDoc2."""

    for validator in validators:
        valid_model_name_opt = validator(model)
        if valid_model_name_opt:
            return valid_model_name_opt
    raise Exception(f"model name '{model.get_path_name().stem}' does not validate any of validators: {[validator.name for validator in validators]}")
