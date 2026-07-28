import re
import pathlib

from typing import List, Tuple, Set, TypeAlias, Protocol, Optional
from pyswx.api.sldworks.interfaces import IComponent2, IBody2

from .logger import *
from .solid_works import *

__all__ = [
    # local utils functions
    'UniqueBodyValidMetadata',
    'SaveFileNameCreator',
    'StandardSaveFileNameCreator',
    'SavingGroup',
    'SavingGroups',
    'prepare_saving_groups',
]

class UniqueBodyValidMetadata:
    """TODO: need to provide some comment"""

    ValidMetadata: TypeAlias = Tuple[ValidBodyName, ValidComponentName, Optional[ValidFolderName]]
    ValidMetadataCollection: TypeAlias = List[ValidMetadata]

    def __init__(self, quantity: int):
        self.__quantity: int = quantity
        self.__valid_metadata: ValidMetadataCollection = []

    def add_metadata(self, valid_metadata: ValidMetadata):
        self.__valid_metadata.append(valid_metadata)

    @property
    def quantity(self) -> int:
        return self.__quantity
    
    @property
    def valid_metadata_collection(self) -> ValidMetadataCollection:
        return self.__valid_metadata

class SaveFileNameCreator(Protocol):
    """Callable that builds an export file name from component/body sets."""

    def __call__(self, saving_valid_info: UniqueBodyValidMetadata) -> pathlib.Path:
        ...


class StandardSaveFileNameCreator(SaveFileNameCreator):
    """Default implementation that joins all name parts with `+`."""

    def create_for_own_component(self, valid_metadata_collection: UniqueBodyValidMetadata.ValidMetadataCollection) -> pathlib.Path:
        assembly_names_set: Set[str] = set()
        models_names_set: Set[str] = set()
        folders_names_set: Set[str] = set()
        bodies_names_set: Set[str] = set()
        for (valid_body_name, valid_component_name, valid_folder_name) in valid_metadata_collection:
            assembly_name = valid_component_name.valid_model_name.assembly_name
            if assembly_name:
                assembly_names_set.add(assembly_name)
            models_names_set.add(valid_component_name.valid_model_name.model_name)
            if valid_folder_name:
                folders_names_set.add(valid_folder_name.folder_name)
            bodies_names_set.add(valid_body_name.main_name)

        assert len(assembly_names_set) <= 1
        save_file_name = "{assembly_name} {model_name} {folder_name} {body_name}".format(
            assembly_name='+'.join(assembly_names_set),
            model_name='+'.join(models_names_set),
            folder_name='+'.join(folders_names_set),
            body_name='+'.join(bodies_names_set),
        )\
        .replace('  ', ' ', -1)\
        .strip()
        return pathlib.Path(save_file_name)

    def create_for_ISO_component(self, valid_metadata_collection: UniqueBodyValidMetadata.ValidMetadataCollection) -> pathlib.Path:
        models_names_set: Set[str] = set()
        configuration_names_set: Set[str] = set()
        for (_, valid_component_name, _) in valid_metadata_collection:
            models_names_set.add(valid_component_name.valid_model_name.model_name)
            configuration_names_set.add(valid_component_name.valid_model_name.configuration_name)

        assert len(models_names_set) == 1
        assert len(configuration_names_set) == 1
        save_file_name = "{model_name} {configuration_name}".format(
            model_name='+'.join(models_names_set),
            configuration_name='+'.join(configuration_names_set),
        )
        save_file_name = re.sub(r'\w_iso', '', save_file_name)
        save_file_name = save_file_name.replace('  ', ' ', -1)
        save_file_name = save_file_name.strip()
        return pathlib.Path(save_file_name)

    def __call__(self, saving_valid_info: UniqueBodyValidMetadata) -> pathlib.Path:
        assert saving_valid_info.quantity == len(saving_valid_info.valid_metadata_collection)
        valid_component_names = [valid_component_name for (_, valid_component_name, _) in saving_valid_info.valid_metadata_collection]
        all_is_default = all(valid_component_name.valid_model_name.approach == ModelNameValidationApproach.DEFAULT for valid_component_name in valid_component_names)
        all_is_iso = all(valid_component_name.valid_model_name.approach == ModelNameValidationApproach.ISO_COMPONENT for valid_component_name in valid_component_names)
        if all_is_default and not all_is_iso:
            return pathlib.Path(self.create_for_own_component(saving_valid_info.valid_metadata_collection))
        elif all_is_iso and not all_is_default:
            return pathlib.Path(self.create_for_ISO_component(saving_valid_info.valid_metadata_collection))
        else:
            raise Exception(f"cannot create save file name for unique bodies collection: {[saving_valid_info.valid_metadata_collection]}")


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


def prepare_saving_groups(unique_bodies: UniqueBodiesManager.UniqueBodies, save_file_name_creator: SaveFileNameCreator = StandardSaveFileNameCreator()) -> List[SavingGroup]:
    """
    Prepare unique export paths for groups of identical bodies across components.
    """
    try:
        reg_saving_groups: List[SavingGroup] = []
        for same_bodies in unique_bodies:
            (reference_body, reference_component) = same_bodies[0]
            quantity = len(same_bodies)
            status.log_line(f"Detected {quantity} same bodies:")
            saving_valid_info = UniqueBodyValidMetadata(quantity)
            for same_body in same_bodies:
                (reference_body, reference_component) = same_body
                status.log_line(f"* body '{reference_body.name}' in component '{reference_component.name2}'")

                if not reference_component.referenced_configuration:
                    valid_body_folder = detect_folder_for_body_in_model(reference_component.get_model_doc2(), reference_body)
                else:
                    valid_body_folder = detect_folder_for_body_in_component(reference_component, reference_body)

                saving_valid_info.add_metadata((
                    validate_and_parse_body_name(reference_body),
                    validate_and_parse_component_name(reference_component),
                    validate_and_parse_folder_name(valid_body_folder) if valid_body_folder else None
                ))

            save_file_name = save_file_name_creator(saving_valid_info)
            for reg_saving_group in reg_saving_groups:
                if save_file_name == reg_saving_group.save_file_name:
                    # TODO: не правильно выводится лог ошибки
                    raise Exception(f"save-file '{save_file_name}' for rep-body '{reference_body.name}' is already reserved by unique bodies: '{[saving_valid_info.valid_metadata_collection]}'")
            reg_saving_groups.append(SavingGroup(body=reference_body, quantity=quantity, component=reference_component, save_file_name=save_file_name))
            status.log_line(f"+ defined common save name is '{save_file_name}'")
        return reg_saving_groups
    except Exception as error:
        raise Exception(f"cannot prepare saving group: {error}")
