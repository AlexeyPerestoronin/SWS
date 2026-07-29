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

class ValidMetadata:
    """TODO: need to provide some comment"""
    
    def __init__(self, valid_body_name: ValidBodyName, valid_component_name: ValidComponentName, valid_folder_name_opt: Optional[ValidFolderName]):
        self.__valid_body_name = valid_body_name
        self.__valid_component_name = valid_component_name
        self.__valid_folder_name_opt = valid_folder_name_opt

    def __str__(self) -> str:
        return f"ValidMetadata[ValidBodyName: '{self.valid_body_name}', ValidComponentName: '{self.valid_component_name}', ValidFolderName: '{self.valid_folder_name}']"
    
    @property
    def valid_body_name(self) -> ValidBodyName:
        return self.__valid_body_name
    
    @property
    def valid_component_name(self) -> ValidComponentName:
        return self.__valid_component_name
    
    @property
    def valid_folder_name(self) -> Optional[ValidFolderName]:
        return self.__valid_folder_name_opt

class ValidMetadataCollection(List[ValidMetadata]):
    """TODO: need to provide some comment"""

    def __str__(self) -> str:
        return "ValidMetadataCollection[{valid_collection}]".format(valid_collection = ','.join(str(valid_metadata) for valid_metadata in self))

class UniqueBodyValidMetadata:
    """TODO: need to provide some comment"""

    def __init__(self, quantity: int):
        self.__quantity: int = quantity
        self.__valid_metadata = ValidMetadataCollection()
        
    def __str__(self) -> str:
        return f"UniqueBodyValidMetadata[quantity = {self.quantity}, {self.__valid_metadata}]"

    @property
    def quantity(self) -> int:
        return self.__quantity
    
    @property
    def collection(self) -> ValidMetadataCollection:
        return self.__valid_metadata

    def add(self, valid_metadata: ValidMetadata):
        self.__valid_metadata.append(valid_metadata)

class SaveFileNameCreator(Protocol):
    """Callable that builds an export file name from component/body sets."""

    def __call__(self, saving_valid_info: UniqueBodyValidMetadata) -> pathlib.Path:
        ...


class StandardSaveFileNameCreator(SaveFileNameCreator):
    """Default implementation that joins all name parts with `+`."""

    def create_for_own_component(self, valid_metadata_collection: ValidMetadataCollection) -> pathlib.Path:
        assembly_names_set: Set[str] = set()
        models_names_set: Set[str] = set()
        folders_names_set: Set[str] = set()
        bodies_names_set: Set[str] = set()
        for (valid_metadata) in valid_metadata_collection:
            assembly_name = valid_metadata.valid_component_name.valid_model_name.assembly_name
            if assembly_name:
                assembly_names_set.add(assembly_name)
            models_names_set.add(valid_metadata.valid_component_name.valid_model_name.model_name)
            if valid_metadata.valid_folder_name:
                folders_names_set.add(valid_metadata.valid_folder_name.folder_name)
            bodies_names_set.add(valid_metadata.valid_body_name.main_name)

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

    def create_for_ISO_component(self, valid_metadata_collection: ValidMetadataCollection) -> pathlib.Path:
        models_names_set: Set[str] = set()
        configuration_names_set: Set[str] = set()
        for valid_metadata in valid_metadata_collection:
            models_names_set.add(valid_metadata.valid_component_name.valid_model_name.model_name)
            configuration_names_set.add(valid_metadata.valid_component_name.configuration_name)

        assert len(models_names_set) == 1
        assert len(configuration_names_set) == 1
        save_file_name = "{model_name} {configuration_name}".format(
            model_name='+'.join(models_names_set),
            configuration_name='+'.join(configuration_names_set),
        )
        save_file_name = re.sub(r'\w+_iso', '', save_file_name)
        save_file_name = re.sub(r'style \d', '', save_file_name)
        save_file_name = re.sub(r'\s+', ' ', save_file_name)
        save_file_name = save_file_name.strip()
        return pathlib.Path(save_file_name)

    def __call__(self, valid_metadata_info: UniqueBodyValidMetadata) -> pathlib.Path:
        assert valid_metadata_info.quantity == len(valid_metadata_info.collection)
        valid_component_names = [valid_metadata.valid_component_name for valid_metadata in valid_metadata_info.collection]
        all_is_default = all(valid_component_name.valid_model_name.approach == ModelNameValidationApproach.DEFAULT for valid_component_name in valid_component_names)
        all_is_iso = all(valid_component_name.valid_model_name.approach == ModelNameValidationApproach.ISO_COMPONENT for valid_component_name in valid_component_names)
        if all_is_default and not all_is_iso:
            return pathlib.Path(self.create_for_own_component(valid_metadata_info.collection))
        elif all_is_iso and not all_is_default:
            return pathlib.Path(self.create_for_ISO_component(valid_metadata_info.collection))
        else:
            raise Exception(f"cannot create save file name for unique bodies collection: {[valid_metadata_info.collection]}")


class SavingGroup:
    """TODO: need to provide some comment"""
    def __init__(self, *, body: IBody2, component: IComponent2, save_file_name: pathlib.Path, unique_body_valid_metadata: UniqueBodyValidMetadata):
        self.__body = body
        self.__component = component
        self.__save_file_name = save_file_name
        self.__unique_body_valid_metadata = unique_body_valid_metadata
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
    def valid_metadata(self) -> UniqueBodyValidMetadata:
        return self.__unique_body_valid_metadata

    @property
    def quantity(self) -> int:
        return self.__unique_body_valid_metadata.quantity

    @property
    def mark(self) -> Optional[str]:
        return self.__mark

    @mark.setter
    def mark(self, value: Optional[str]):
        self.__mark = value


class SavingGroups(List[SavingGroup]):
    """TODO: need to provide some comment"""


def prepare_saving_groups(unique_bodies: UniqueBodiesManager.UniqueBodies, save_file_name_creator: SaveFileNameCreator = StandardSaveFileNameCreator()) -> List[SavingGroup]:
    """
    Prepare unique export paths for groups of identical bodies across components.
    """
    try:
        result_saving_groups = SavingGroups()
        for same_bodies in unique_bodies:
            (reference_body, reference_component) = same_bodies[0]
            quantity = len(same_bodies)
            status.log_line(f"Detected {quantity} same bodies:")
            unique_body_valid_metadata = UniqueBodyValidMetadata(quantity)
            for same_body in same_bodies:
                (reference_body, reference_component) = same_body
                status.log_line(f"* body '{reference_body.name}' in component '{reference_component.name2} ({reference_component.referenced_configuration})'")

                if not reference_component.referenced_configuration:
                    valid_body_folder = detect_folder_for_body_in_model(reference_component.get_model_doc2(), reference_body)
                else:
                    valid_body_folder = detect_folder_for_body_in_component(reference_component, reference_body)

                unique_body_valid_metadata.add(ValidMetadata(
                    validate_and_parse_body_name(reference_body),
                    validate_and_parse_component_name(reference_component),
                    validate_and_parse_folder_name(valid_body_folder) if valid_body_folder else None
                ))

            save_file_name = save_file_name_creator(unique_body_valid_metadata)
            for result_saving_group in result_saving_groups:
                if save_file_name == result_saving_group.save_file_name:
                    raise Exception(f"save-file '{save_file_name}' for rep-body '{unique_body_valid_metadata}' is already reserved by unique bodies: '{str(result_saving_group.valid_metadata)}'")
            result_saving_groups.append(SavingGroup(body=reference_body, component=reference_component, save_file_name=save_file_name, unique_body_valid_metadata=unique_body_valid_metadata))
            status.log_line(f"+ defined common save name is '{save_file_name}'")
        return result_saving_groups
    except Exception as error:
        raise Exception(f"cannot prepare saving group: {error}")
