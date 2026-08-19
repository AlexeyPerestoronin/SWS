import shutil
import pathlib

from tabulate import tabulate
from typing import Optional, List, Tuple

from .i_document_creator import IDocumentCreator, TableDataPreparator

import utils

__all__ = [
    'MaterialInfoTable',
    'CNCWoodMillingCuttingDocCreator',
]


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


class CNCWoodMillingCuttingDocCreator(IDocumentCreator):
    """Генератор Markdown-документа для лазерной резки металла (STEP/DXF).

    Класс собирает «шапку» с технологическими пояснениями и добавляет таблицы

    деталей/файлов (STEP и/или DXF) с указанием количества.
    """

    def __init__(self, project_name: str):
        self.__content = [
            f"# Техническое задания на изготовление деревянных деталей для «{project_name}» методом ЧПУ фрезерной резки",
            "",
            "❗ **Геометрические параметры всех деталей в STEP/DXF-файлах учитывают технологические отступы:**",
            "",
            "Траектория реза задается относительно контура детали следующим образом:",
            "- для сквозных отверстий, пазов и иных внутренних элементов, рез выполняется по внутреннему контуру (материал удаляется изнутри контура);",
            "- для наружного контура детали (отрезка заготовки), рез выполняется по внешнему контуру (материал удаляется снаружи контура).",
            "",
            "❗В случае если деталь изготавливается **только при помощи фрезерной резки листового материала** (ДСП, ОСБ, фанера, и т.д.), документация содержит соответствующий DXF файл!",
            "",
        ]

    def add_table(self, header: str, table: TableDataPreparator, material_info_table: MaterialInfoTable) -> 'CNCWoodMillingCuttingDocCreator':
        try:
            table = tabulate(table.get_data(), table.get_headers(), tablefmt="pipe")
            material_info_table = tabulate(material_info_table.get_data(), material_info_table.get_headers(), tablefmt="pipe")
            self.__content.extend([
                f"## {header}",
                f"Справочная информация о рабочем материале",
                f"{material_info_table}",
                "",
                "***",
                "",
                f"{table}",
                "",
            ])
        except Exception as error:
            raise RuntimeError(f"cannot add '{header}'-table in DOC: {error}")
        return self

    # wood-sheet(s)

    def add_12mm_OSB(self, table: TableDataPreparator) -> 'CNCWoodMillingCuttingDocCreator':
        material_info_table = MaterialInfoTable()
        material_info_table.prepare_data([
            ["материал", "ОСБ плита"],
            ["толщина", "12мм"],
            ["сорт", "2 или 3 (приоритет меньшей итоговой стоимости)"],
            ["древесина", "не имеет значения (приоритет меньшей итоговой стоимости)"],
            ["исходный размер", "не имеет значения (приоритет меньшей итоговой стоимости)"],
            ["влагостойкость", "не имеет значения (приоритет меньшей итоговой стоимости)"],
            ["возможная справочная ссылка для закупки", "https://pilomarket.com/catalog/osb/osb-%28osv%29-12mm-1%2C22-x-2%2C44-m/"],
        ])
        return self.add_table('ОСБ 12мм', table, material_info_table)

    def add_15mm_plywood(self, table: TableDataPreparator) -> 'CNCWoodMillingCuttingDocCreator':
        material_info_table = MaterialInfoTable()
        material_info_table.prepare_data([
            ["материал", "фанера"],
            ["толщина", "15мм"],
            ["сорт", "3 или 4 (приоритет меньшей итоговой стоимости)"],
            ["древесина", "не имеет значения (приоритет меньшей итоговой стоимости)"],
            ["исходный размер", "не имеет значения (приоритет меньшей итоговой стоимости)"],
            ["влагостойкость", "не имеет значения (приоритет меньшей итоговой стоимости)"],
            ["шлифование", "не имеет значения (приоритет меньшей итоговой стоимости)"],
            ["ламинирование", "не имеет значения (приоритет меньшей итоговой стоимости)"],
            ["возможная справочная ссылка для закупки", "https://pilomarket.com/catalog/shlifovannaya/fanera-shlifovannaya-fk-15mm/"],
        ])
        return self.add_table('Фанера 15мм', table, material_info_table)

    # ---

    def create(self, save_folder: pathlib.Path):
        doc_file_path = save_folder / 'CNC_milling_cutting_of_wood.md'
        try:
            save_folder.mkdir(parents=True, exist_ok=True)
            with open(doc_file_path, "w", encoding="utf-8") as file:
                file.write("\n".join(self.__content))
            utils.success.log_line(f"Documentation for CNC-milling-cutting of wood have created: {doc_file_path}")
        except Exception as error:
            raise RuntimeError(f"cannot create DOC in {doc_file_path}: {error}")
