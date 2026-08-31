import re

from enum import Enum
from typing import TypeAlias, List, Tuple, Protocol, Optional
from pyswx.api.sldworks.interfaces import IBody2

__all__ = [
    'is_two_body_equal',
    'get_equal_bodies_groups',
    'BodyNameValidationApproach',
    'ValidBodyName',
    'BodyNameValidator',
    'SwInsertedPartBodyNameValidator',
    'SwAutoBodyNameValidator',
    'UserBodyNameValidator',
    'validate_and_parse_body_name',
]


def is_two_body_equal(body1: IBody2, body2: IBody2) -> bool:
    """
    Checking two bodies if their are equal (fully geometrical coincidence).
    """
    (result, _) = body1.get_coincidence_transform_2(body2)
    return result


def get_equal_bodies_groups(bodies: List[IBody2]) -> List[List[IBody2]]:
    """
    Groups a list of SolidWorks solid bodies (IBody2) into unique sets based on geometric coincidence.

    Args:
        bodies (List[IBody2]): list of SW bodies for selection of unique

    Returns:
        List[List[IBody2]]: List of lists of same bodies
    """
    unique_bodies = []
    while len(bodies) != 0:
        remain_bodies = []
        body1 = bodies[0]
        unique_bodies.append([body1])
        for body2 in bodies[1:]:
            if is_two_body_equal(body1, body2):
                unique_bodies[-1].append(body2)
            else:
                remain_bodies.append(body2)
        bodies = remain_bodies
    return unique_bodies


class BodyNameValidationApproach(str, Enum):
    SW_INSERTED_PART = 'SolidWorks inserted part body-name'
    SW_AUTO_NAME = 'SolidWorks auto body-name'
    USER_NAME = "user's defined body-name"


class ValidBodyName:
    MainName: TypeAlias = str
    Suffixes: TypeAlias = List[str]
    IndexOpt: TypeAlias = Optional[int]

    def __init__(self, main_name: MainName, suffixes: Suffixes, approach: BodyNameValidationApproach):
        self.__main_name = main_name
        self.__suffixes = suffixes
        self.__approach = approach

    def __str__(self) -> str:
        return f"{self.main_name} {' '.join(self.__suffixes)}"

    @property
    def approach(self) -> BodyNameValidationApproach:
        return self.__approach

    @property
    def main_name(self) -> MainName:
        return self.__main_name

    @property
    def suffixes(self) -> Suffixes:
        return self.__suffixes

    @property
    def index(self) -> IndexOpt:
        index = None
        for suffix in self.__suffixes:
            try:
                number = float(suffix)
            except ValueError:
                continue
            if number.is_integer():
                if not index:
                    index = int(number)
                else:
                    raise Exception(f"more then one suffixes are satisfying of index for body '{self.__main_name} {' '.join(self.__suffixes)}'")
        return index

    @property
    def has_new(self) -> bool:
        return 'new' in self.__suffixes


class BodyNameValidator(Protocol):
    """Body name validator protocol"""

    @property
    def name(self) -> str:
        ...

    def __call__(self, body: IBody2) -> Optional[ValidBodyName]:
        ...


class SwInsertedPartBodyNameValidator(BodyNameValidator):
    """Validator for bodies created by Insert Part (auto-named as <part>-<body>)"""

    @property
    def name(self) -> str:
        return str(BodyNameValidationApproach.SW_INSERTED_PART)

    def __call__(self, body: IBody2) -> Optional[ValidBodyName]:
        body_name = body.name
        body_name_pattern = r'(?P<main_name><.+?>-<.+?>)(?:\s(?P<index>\d+))?'
        match = re.fullmatch(body_name_pattern, body_name)
        if match:
            main_name = match.group('main_name')
            index = match.group('index')
            return ValidBodyName(main_name, [index] if index else [], BodyNameValidationApproach.SW_INSERTED_PART)
        return None


class SwAutoBodyNameValidator(BodyNameValidator):
    """Validator for unchanged SolidWorks auto-generated body names"""

    @property
    def name(self) -> str:
        return str(BodyNameValidationApproach.SW_AUTO_NAME)

    def __call__(self, body: IBody2) -> Optional[ValidBodyName]:
        body_name = body.name
        # CirPattern, Boss-Extrude, Cut-Extrude, Move/Copy1, etc.
        body_name_pattern = r'(Extrude|Revolve|Pattern|Move|Copy|Fillet)'
        if re.search(body_name_pattern, body_name):
            return ValidBodyName(body_name, [], BodyNameValidationApproach.SW_AUTO_NAME)
        return None


class UserBodyNameValidator(BodyNameValidator):
    """User-own body name validator"""

    @property
    def name(self) -> str:
        return str(BodyNameValidationApproach.USER_NAME)

    def __call__(self, body: IBody2) -> Optional[ValidBodyName]:
        def check_main_name(main_name: str) -> Optional[str]:
            main_name_pattern = r'\w+(-\w)*'
            if not bool(re.match(main_name_pattern, main_name)):
                return None
            return main_name

        def check_name_suffixes(body_suffixes: List[str]) -> List[str]:
            available_suffixes = ['R', 'П', 'L', 'Л', 'U', 'В', 'D', 'Н', 'F', 'B', r'\d+', 'new']
            validated_suffixes = []
            for body_suffix in body_suffixes:
                if any([bool(re.match(available_suffix, body_suffix)) for available_suffix in available_suffixes]):
                    validated_suffixes.append(body_suffix)
                else:
                    raise Exception(f"unexpected body suffix: {body_suffix}")
            return validated_suffixes

        body_name = body.name
        if ' ' in body_name:
            parts = body_name.split(' ')
            main_name = check_main_name(parts[0])
            if main_name is None:
                return None
            return ValidBodyName(main_name, check_name_suffixes(parts[1:]), BodyNameValidationApproach.USER_NAME)
        else:
            main_name = check_main_name(body_name)
            if main_name is None:
                return None
            return ValidBodyName(main_name, [], BodyNameValidationApproach.USER_NAME)


def validate_and_parse_body_name(body: IBody2, *, validators: List[BodyNameValidator] = [
        SwInsertedPartBodyNameValidator(),
        SwAutoBodyNameValidator(),
        UserBodyNameValidator(),
]) -> ValidBodyName:
    """Validate and parse name of the SW-IBody2."""

    for validator in validators:
        valid_body_name_opt = validator(body)
        if valid_body_name_opt:
            return valid_body_name_opt
    raise Exception(f"body name '{body.name}' does not validate any of validators: {[validator.name for validator in validators]}")
