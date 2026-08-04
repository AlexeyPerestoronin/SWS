import pathlib

from typing import Protocol, List
from collections.abc import Callable

import utils

__all__ = [
    'NameTransformator',
    'QuantityEvaluator',
    'TableDataPreparator',
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


class IDocumentCreator(Protocol):
    """Интерфейс генератора документа.

    Конкретные реализации должны создавать/записывать документ в заданный путь.
    """

    def create(self, doc_file_path: pathlib.Path):
        """Создать документ (или перезаписать существующий) по указанному пути."""
        ...
