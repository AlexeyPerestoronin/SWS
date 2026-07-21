import pathlib

from typing import List, Set, TypeAlias, Protocol, Optional
from pyswx.api.sldworks.interfaces import IComponent2, IBody2

from .logger import *
from .solid_works import *

__all__ = [
    # local utils functions
    'SavingGroup',
    'SavingGroups',
    'SaveFileNameCreator',
    'ComplexSaveFileNameCreator',
    'prepare_saving_groups',
]


class SavingGroup:
    """TODO: need to provide some comment"""
    def __init__(self, *, body: IBody2, component: IComponent2, save_file_name: pathlib.Path, quantity: int):
        self.__body = body
        self.__component = component
        self.__save_file_name = save_file_name
        self.__quantity = quantity
        self.__mark: Optional[str] = None

    @property
    def body(self) -> IBody2:
        return self.__body

    @property
    def component(self) -> IComponent2:
        return self.__component

    @property
    def save_file_name(self) -> pathlib.Path:
        return self.__save_file_name

    @property
    def quantity(self) -> int:
        return self.__quantity

    @property
    def mark(self) -> Optional[str]:
        return self.__mark

    @mark.setter
    def mark(self, value: Optional[str]):
        self.__mark = value

SavingGroups: TypeAlias = List[SavingGroup]


class SaveFileNameCreator(Protocol):
    """Callable that builds an export file name from component/body sets."""

    def __call__(self, assembly_names_set: Set[str], models_names_set: Set[str], folders_names_set: Set[str], bodies_names_set: Set[str], quantity: int) -> str:
        ...


class ComplexSaveFileNameCreator(SaveFileNameCreator):
    """Default implementation that joins all name parts with `+`."""

    def __call__(self, assembly_names_set: Set[str], models_names_set: Set[str], folders_names_set: Set[str], bodies_names_set: Set[str], quantity: int) -> str:
        return "{assembly_name} {model_name} {folder_name} {body_name}".format(
            assembly_name='+'.join(assembly_names_set),
            model_name='+'.join(models_names_set),
            folder_name='+'.join(folders_names_set),
            body_name='+'.join(bodies_names_set),
        )\
        .replace('  ', ' ', -1)\
        .strip()


def prepare_saving_groups(unique_bodies: UniqueBodiesManager.UniqueBodies, save_file_name_creator: SaveFileNameCreator = ComplexSaveFileNameCreator()) -> SavingGroups:
    """
    Prepare unique export paths for groups of identical bodies across components.
    """
    try:
        reg_saving_groups: SavingGroups = []
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

            save_file_name = pathlib.Path(save_file_name_creator(assembly_names_set, models_names_set, folders_names_set, bodies_names_set, quantity))

            for reg_saving_group in reg_saving_groups:
                if save_file_name == reg_saving_group.save_file_name:
                    raise Exception(f"save-file '{save_file_name}' for rep-body '{reference_body.name}' is already reserved by body '{reg_saving_group.body.name}'")
            reg_saving_groups.append(SavingGroup(body=reference_body, quantity=quantity, component=reference_component, save_file_name=save_file_name))
            status.log_line(f"+ defined common save name is '{save_file_name}'")
        return reg_saving_groups
    except Exception as error:
        raise Exception(f"cannot prepare saving group: {error}")
