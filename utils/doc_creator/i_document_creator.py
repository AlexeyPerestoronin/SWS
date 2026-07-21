import pathlib

from typing import Protocol

__all__ = [
    'IDocumentCreator',
]


class IDocumentCreator(Protocol):
    """Интерфейс генератора документа.

    Конкретные реализации должны создавать/записывать документ в заданный путь.
    """

    def create(self, doc_file_path: pathlib.Path):
        """Создать документ (или перезаписать существующий) по указанному пути."""
        ...
