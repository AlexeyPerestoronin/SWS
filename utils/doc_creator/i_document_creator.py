import pathlib

from typing import Protocol, List
from collections.abc import Callable

import utils

__all__ = [
    'QuantityEvaluator',
    'TableDataPreparator',
    'IDocumentCreator',
]


class QuantityEvaluator(Callable[[int], int]):
    """TODO: need to provide some comment"""

    def __call__(self, quantity: int) -> int:
        return quantity


class TableDataPreparator(Protocol):
    """TODO: need to provide some comment"""

    def __init__(self, saving_groups: utils.SavingGroups):
        self._saving_groups = saving_groups

    def get_headers(self) -> List[str]:
        """TODO: need to provide some comment"""
        ...

    def get_data(self) -> list:
        """TODO: need to provide some comment"""
        ...

    def prepare_data(self):
        """TODO: need to provide some comment"""
        ...


class IDocumentCreator(Protocol):
    """Интерфейс генератора документа.

    Конкретные реализации должны создавать/записывать документ в заданный путь.
    """

    def create(self, doc_file_path: pathlib.Path):
        """Создать документ (или перезаписать существующий) по указанному пути."""
        ...
