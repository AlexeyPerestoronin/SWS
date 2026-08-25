import re
import pathlib

from typing import Protocol, List, Tuple, Optional
from collections.abc import Callable

import utils

__all__ = [
    'NameTransformator',
    'QuantityEvaluator',
    'TableDataPreparator',
    'StandardElementsTable',
    'MaterialInfoTable',
    'IDocumentCreator',
]


class NameTransformator(Callable[[str], str]):
    """TODO: need to provide some comment"""

    def __call__(self, name: str) -> str:
        return name


class QuantityEvaluator(Callable[[int], int]):
    """Callable that evaluates the quantity of items for a table row."""

    def __call__(self, quantity: int) -> int:
        return quantity


class TableDataPreparator(Protocol):
    """Protocol for preparing table data from saving groups."""

    def __init__(self, saving_groups: utils.SavingGroups):
        self._saving_groups = saving_groups

    def get_headers(self) -> List[str]:
        """Return list of column headers for the table."""
        ...

    def get_data(self) -> list:
        """Return list of rows (data) for the table."""
        ...

    def prepare_data(self):
        """Process saving groups and populate the table data."""
        ...


class StandardElementsTable(TableDataPreparator):
    """TODO: need to provide some comment"""

    def __init__(self, saving_groups: utils.SavingGroups):
        super().__init__(saving_groups)
        self.__table_data: List[Tuple[str, str, str, str]] = []

    def get_headers(self) -> List[str]:
        return ["Компонент", "STEP", "DXF", "Количество (штук)"]

    def get_data(self) -> list:
        self.__table_data = sorted(self.__table_data, key=lambda x: x[0])
        return self.__table_data

    def prepare_data(self,
                     match_expressions: List[str],
                     *,
                     name_transformator: NameTransformator = NameTransformator(),
                     quantity_evaluator: QuantityEvaluator = QuantityEvaluator(),
                     step: bool = False,
                     dxf: bool = False,
                     save_folder_opt: Optional[pathlib.Path] = None) -> 'StandardElementsTable':
        for saving_group in self._saving_groups:
            component_full_name = str(saving_group.save_file_name)
            for match_expression in match_expressions:
                match = re.fullmatch(match_expression, component_full_name)
                if match:
                    if saving_group.mark is not None:
                        raise Exception(f"'{component_full_name}' is already accounted by '{saving_group.mark}'-mark")
                    saving_group.mark = f"StandardElementsTable by '{match_expression}'"
                    save_file_name = name_transformator(str(saving_group.save_file_name))
                    if step:
                        assert save_folder_opt
                        step_file = save_folder_opt / 'STEP' / pathlib.Path(save_file_name).with_suffix('.step')
                        utils.save_body_from_component_like_step(saving_group.component, saving_group.body, step_file)
                        utils.success.log_line(f"STEP file created: {step_file}")
                    if dxf:
                        assert save_folder_opt
                        dxf_file = save_folder_opt / 'DXF' / pathlib.Path(save_file_name).with_suffix('.dxf')
                        utils.save_body_from_component_like_dxf(saving_group.component, saving_group.body, dxf_file)
                        utils.success.log_line(f"DXF file created: {dxf_file}")
                    self.__table_data.append([save_file_name, step, dxf, quantity_evaluator(saving_group.valid_metadata.quantity)])
                    break
        return self


class MaterialInfoTable(TableDataPreparator):
    """TODO: need to provide some comment"""

    def __init__(self):
        super().__init__(None)
        self.__table_data: List[Tuple[str, str]] = []

    def get_headers(self) -> List[str]:
        return ["Параметр", "Показатель"]

    def get_data(self) -> list:
        return self.__table_data

    def prepare_data(self, data: List[Tuple[str, str]]) -> 'MaterialInfoTable':
        self.__table_data.extend(data)
        return self


class IDocumentCreator(Protocol):
    """Интерфейс генератора документа.

    Конкретные реализации должны создавать/записывать документ в заданный путь.
    """

    def create(self, doc_file_path: pathlib.Path):
        """Создать документ (или перезаписать существующий) по указанному пути."""
        ...
