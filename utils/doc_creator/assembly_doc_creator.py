import re
import pathlib

from tabulate import tabulate
from collections.abc import Callable
from typing import List, Tuple, Optional, Protocol

from .i_document_creator import IDocumentCreator
from .iso_elements import detect_translation, detect_link

import utils

__all__ = [
    'SpecialElementsAssemblyTable',
    'ISOToolboxAssemblyTable',
    'AssemblyDocCreator',
]


class QuantityEvaluator(Callable[[int], int]):
    """TODO: need to provide some comment"""

    def __call__(self, quantity: int) -> int:
        return quantity

class AssemblyTableDataPreparator(Protocol):
    """TODO: need to provide some comment"""

    def __init__(self, saving_groups: utils.SavingGroups):
        self._saving_groups = saving_groups

    def get_headers(self) -> List[str]:
        ...

    def get_data(self) -> list:
        ...

    def prepare_data(self):
        ...

class SpecialElementsAssemblyTable(AssemblyTableDataPreparator):
    """TODO: need to provide some comment"""

    def __init__(self, saving_groups: utils.SavingGroups):
        super().__init__(saving_groups)
        self.__table_data: List[Tuple[str, str, str, str]] = []

    def get_headers(self) -> List[str]:
        return ["Компонент", "STEP", "Количество (штук)", "Ссылка для покупки"]

    def get_data(self) -> list:
        self.__table_data = sorted(self.__table_data, key=lambda x: x[0])
        return self.__table_data

    def prepare_data(self, match_expressions: List[str], *, quantity_evaluator: QuantityEvaluator = QuantityEvaluator(), step: bool = False, save_folder_opt: Optional[pathlib.Path] = None, buy_link: Optional[str] = None) -> 'SpecialElementsAssemblyTable':
        for saving_group in self._saving_groups:
            component_full_name = str(saving_group.save_file_name)
            for match_expression in match_expressions:
                match = re.fullmatch(match_expression, component_full_name)
                if match:
                    if saving_group.mark is not None:
                        raise Exception(f"'{component_full_name}' is already accounted by '{saving_group.mark}'-mark")
                    saving_group.mark = f"GeneralElementsTable by '{match_expression}'"
                    if step:
                        assert save_folder_opt
                        step_file = save_folder_opt / 'STEP' / saving_group.save_file_name.with_suffix('.step')
                        utils.save_body_from_component_like_step(saving_group.component, saving_group.body, step_file)
                        utils.success.log_line(f"STEP file created: {step_file}")
                    self.__table_data.append([component_full_name, step, quantity_evaluator(saving_group.valid_metadata.quantity), buy_link if buy_link else 'None'])
                    break
        return self

class ISOToolboxAssemblyTable(AssemblyTableDataPreparator):
    """TODO: need to provide some comment"""
    
    def __init__(self, saving_groups):
        super().__init__(saving_groups)
        self.__table_data: List[Tuple[str, str, str, str]] = []

    def get_headers(self) -> List[str]:
        return ["Наименование", "Тип", "Количество (штук)", "Ссылка для покупки"]

    def get_data(self) -> list:
        self.__table_data = sorted(self.__table_data, key=lambda x: x[0])
        return self.__table_data

    def prepare_data(self, *, quantity_evaluator: QuantityEvaluator = QuantityEvaluator()) -> 'ISOToolboxAssemblyTable':
        for saving_group in self._saving_groups:
            component_full_name = str(saving_group.save_file_name)
            iso_name_pattern = r'(?P<name>(\w+)(\s\w+)+) (?P<type>ISO .+)'
            match = re.fullmatch(iso_name_pattern, component_full_name)
            if match:
                groups = match.groupdict()
                name = groups['name']
                type = groups.get('type')
                if saving_group.mark is not None:
                    raise Exception(f"'{component_full_name}' is already accounted by '{saving_group.mark}'-mark")
                saving_group.mark = f"ISOToolboxAssemblyTable with '{component_full_name}'"
                self.__table_data.append([detect_translation(name), type, quantity_evaluator(saving_group.valid_metadata.quantity), detect_link(name, type)])
        return self


class AssemblyDocCreator(IDocumentCreator):
    """TODO: need to provide some comment"""

    def __init__(self, project_name: str):
        self.__content = [
            f"# Техническое задания на закупку базовых сборочных компонентов для «{project_name}»",
            "",
            "❗Для точной идентификации физической формы компонента смотри соответствующий STEP файл.",
            "",
        ]

    def add_table(self, header, table: AssemblyTableDataPreparator) -> 'AssemblyDocCreator':
        try:
            table = tabulate(table.get_data(), table.get_headers(), tablefmt="pipe")
            self.__content.extend([
                f"## {header}",
                f"{table}",
                "",
            ])
        except Exception as error:
            raise RuntimeError(f"cannot add '{header}'-table in DOC: {error}")
        return self

    def create(self, save_folder: pathlib.Path):
        doc_file_path = save_folder / 'Assembly_Components.md'
        try:
            with open(doc_file_path, "w", encoding="utf-8") as file:
                file.write("\n".join(self.__content))
            utils.success.log_line(f"Assembly documentation created: {doc_file_path}")
        except Exception as error:
            raise RuntimeError(f"cannot create DOC in {doc_file_path}: {error}")
