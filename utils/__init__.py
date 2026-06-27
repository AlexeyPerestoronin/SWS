import re, difflib, functools, pathlib

from typing import List, Tuple, Set, TypeAlias
from pyswx.api.sldworks.interfaces import IModelDoc2, IComponent2, IBody2
from pyswx.api.sldworks.interfaces import IModelDoc2, IBodyFolder

from .logger import *
from .solid_works import *

__all__ = [
    # local utils functions
    'validate_project_naming',
    'validate_folders_naming',
    'longest_common_substring',
    # sub modules
    *solid_works.__all__,
    *logger.__all__,
]


def validate_project_naming(model: IModelDoc2):
    """
    Check project name via its model
    """

    model_name = model.get_path_name().stem
    model_name_pattern = r'[A-ZА-ЯЁ]\w+(-[A-ZА-ЯЁ]\w+)*'
    if not bool(re.fullmatch(model_name_pattern, model_name)):
        raise Exception(f"model name '{model_name}' does not match by regular expression: {model_name_pattern}")
    return True


def validate_folders_naming(folders: List[IBodyFolder]):
    """
    Check names of all folders in list.
    """

    folder_name_pattern = r'\w+(-\w+)*'
    for folder in folders:
        folder_name = folder.get_feature().name
        if not bool(re.match(folder_name_pattern, folder_name)):
            raise Exception(f"folder name '{folder_name}' does not match by regular expression: {folder_name_pattern}")
    return True


def longest_common_substring(strings: List[str]) -> str:
    """
    Returns longest common substring for all strings in the list using difflib.
    """
    if not strings:
        return ""
    if len(strings) == 1:
        return strings[0]

    def lcs_pair(a: str, b: str) -> str:
        matcher = difflib.SequenceMatcher(None, a, b)
        match = matcher.find_longest_match(0, len(a), 0, len(b))
        return a[match.a:match.a + match.size]

    return functools.reduce(lcs_pair, strings)


Quantity: TypeAlias = int # quantity of the same body in group
SavingGroup: TypeAlias = Tuple[IBody2, Quantity, IComponent2, pathlib.Path]
SavingGroups: TypeAlias = List[SavingGroup]


def prepare_saving_groups(unique_bodies: UniqueBodiesManager.UniqueBodies, save_folder: pathlib.Path) -> SavingGroups:
    """
    Prepare unique STEP export paths for groups of identical bodies across components.
    """
    result: SavingGroups = []
    for same_bodies in unique_bodies:
        (reference_body, reference_component) = same_bodies[0]
        assembly_names_set: Set[str] = set()
        models_names_set: Set[str] = set()
        folders_names_set: Set[str] = set()
        bodies_names_set: Set[str] = set()
        quantity = len(same_bodies)
        status.log_line(f"Detected {quantity} same bodies:")
        for same_body in same_bodies:
            (reference_body, reference_component) = same_body
            status.log_line(f"* body '{reference_body.name}' in component '{reference_component.name2}'")
            bodies_names_set.add(validate_and_parse_body_name(reference_body).main_name)
            if not reference_component.referenced_configuration:
                body_folder = detect_folder_for_body_in_model(reference_component.get_model_doc2(), reference_body)
            else:
                body_folder = detect_folder_for_body_in_component(reference_component, reference_body)
            if body_folder:
                folders_names_set.add(body_folder)
            valid_model_name = validate_and_parse_component_name(reference_component).valid_model_name
            models_names_set.add(valid_model_name.model_name)
            if valid_model_name.assembly_name:
                assembly_names_set.add(valid_model_name.assembly_name)

        step_file_name = "{assembly_name} {model_name} {folder_name} {body_name}".format(
            assembly_name='+'.join(assembly_names_set),
            model_name='+'.join(models_names_set),
            folder_name='+'.join(folders_names_set),
            body_name='+'.join(bodies_names_set),
        )\
        .replace('  ', ' ', -1)\
        .strip()

        new_save_path = save_folder / pathlib.Path(step_file_name).with_suffix(".step")
        for (body, _, _, save_path) in result:
            if new_save_path == save_path:
                raise Exception(f"step path '{new_save_path}' for rep-body '{reference_body.name}' is already reserved by body '{body.name}'")
        result.append((reference_body, quantity, reference_component, new_save_path))
        status.log_line(f"+ defined common save path is '{new_save_path}'")
    return result
