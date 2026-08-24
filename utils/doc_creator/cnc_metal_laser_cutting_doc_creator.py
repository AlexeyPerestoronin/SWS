import pathlib

from tabulate import tabulate
from typing import Optional

from .i_document_creator import IDocumentCreator, TableDataPreparator

import utils

__all__ = [
    'CNCMetalLaserCuttingDocCreator',
]


class CNCMetalLaserCuttingDocCreator(IDocumentCreator):
    """Генератор Markdown-документа для лазерной резки металла (STEP/DXF).

    Класс собирает «шапку» с технологическими пояснениями и добавляет таблицы

    деталей/файлов (STEP и/или DXF) с указанием количества.
    """

    def __init__(self, project_name: str):
        self.__content = [
            f"# Техническое задания на изготовление металлических деталей для «{project_name}» методом ЧПУ лазерной резки",
            "",
            "❗ **Геометрические параметры всех деталей в STEP/DXF-файлах учитывают технологические отступы:**",
            "Траектория реза задается относительно контура детали следующим образом:",
            "- для сквозных отверстий, пазов и иных внутренних элементов, рез выполняется по внутреннему контуру (материал удаляется изнутри контура);",
            "- для наружного контура детали (отрезка заготовки), рез выполняется по внешнему контуру (материал удаляется снаружи контура).",
            "",
            "❗В случае если деталь изготавливается **только при помощи резки листового металла**, документация содержит соответствующий DXF файл!",
            "",
            "❗В случае, если фактические параметры металлических заготовок будут отличаться от заданных, прошу сообщить отдельно для внесения корректировок в проект изделия!",
            "",
        ]

    def add_table(self, header: str, table: TableDataPreparator, material_link: Optional[str] = None) -> 'CNCMetalLaserCuttingDocCreator':
        try:
            table = tabulate(table.get_data(), table.get_headers(), tablefmt="pipe")
            self.__content.extend([
                f"## {header}",
                f"[Справочная ссылка для материала]({material_link})\n" if material_link else "",
                f"{table}",
                "",
            ])
        except Exception as error:
            raise RuntimeError(f"cannot add '{header}'-table in DOC: {error}")
        return self

    # steel-sheet(s)

    def add_8mm_steel_sheet_table(self, table: TableDataPreparator) -> 'CNCMetalLaserCuttingDocCreator':
        return self.add_table('Лист стальной горячекатанный 8мм', table, 'https://купитьметалл.рф/product/list-gk-8-st3sp-ps-5')

    def add_6mm_steel_sheet_table(self, table: TableDataPreparator) -> 'CNCMetalLaserCuttingDocCreator':
        return self.add_table('Лист стальной горячекатанный 6мм', table, 'https://купитьметалл.рф/product/list-gk-6-st3sp-ps-5')

    def add_4mm_steel_sheet_table(self, table: TableDataPreparator) -> 'CNCMetalLaserCuttingDocCreator':
        return self.add_table('Лист стальной горячекатанный 4мм', table, 'https://купитьметалл.рф/product/list-gk-4-st3sp-ps-5')

    def add_3mm_steel_sheet_table(self, table: TableDataPreparator) -> 'CNCMetalLaserCuttingDocCreator':
        return self.add_table('Лист стальной горячекатанный 3мм', table, 'https://купитьметалл.рф/product/list-gk-3-st3sp-ps-5')

    def add_2mm_steel_sheet_table(self, table: TableDataPreparator) -> 'CNCMetalLaserCuttingDocCreator':
        return self.add_table('Лист стальной горячекатанный 2мм', table, 'https://купитьметалл.рф/product/list-gk-2-st3sp-ps-5')

    # profile-tube(s)

    def add_50_50_4mm_steel_profile_tube_table(self, table: TableDataPreparator) -> 'CNCMetalLaserCuttingDocCreator':
        return self.add_table('Труба профильная стальная 50x50x4мм', table, 'https://купитьметалл.рф/product/truba-kvadratnaya-50x50x4')

    def add_50_25_2mm_steel_profile_tube_table(self, table: TableDataPreparator) -> 'CNCMetalLaserCuttingDocCreator':
        return self.add_table('Труба профильная стальная 50x25x2мм', table, 'https://купитьметалл.рф/product/truba-pryamougol-50x25x2')

    # profile-angle

    def add_25_25_4mm_steel_profile_angle_table(self, table: TableDataPreparator) -> 'CNCMetalLaserCuttingDocCreator':
        return self.add_table('Профильный уголок стальной 25x25x4мм', table, 'https://купитьметалл.рф/product/ugolok-gk-25x25x4-st3sp-ps-5')

    # ---

    def create(self, save_folder: pathlib.Path):
        doc_file_path = save_folder / 'CNC_laser_cutting_of_metal.md'
        try:
            save_folder.mkdir(parents=True, exist_ok=True)
            with open(doc_file_path, "w", encoding="utf-8") as file:
                file.write("\n".join(self.__content))
            utils.success.log_line(f"Documentation for CNC-laser-cutting of metal have created: {doc_file_path}")
        except Exception as error:
            raise RuntimeError(f"cannot create DOC in {doc_file_path}: {error}")
