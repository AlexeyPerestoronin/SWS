import pathlib

from tabulate import tabulate
from collections.abc import Callable
from typing import List, Tuple, Optional, TypeAlias

from .i_document_creator import IDocumentCreator

import utils

__all__ = [
    'CNCLaserCuttingDocCreator',
]


class CNCLaserCuttingDocCreator(IDocumentCreator):
    """Генератор Markdown-документа для лазерной резки металла (STEP/DXF).

    Класс собирает «шапку» с технологическими пояснениями и добавляет таблицы

    деталей/файлов (STEP и/или DXF) с указанием количества.
    """

    class TableDataPreparator:
        """Готовит строки таблицы и по необходимости экспортирует STEP/DXF.

        Идея: на вход подаются «группы сохранения» (какое тело/компонент
        соответствует какому имени файла), а также выражения сопоставления.
        Для совпавших деталей формируется строка таблицы; если запрошен экспорт,
        то соответствующие файлы STEP/DXF создаются в подпапках.
        """

        TableData: TypeAlias = List[Tuple[
            str,  # название детали
            bool,  # экспорт в STEP
            bool,  # экспорт в DXF
            int  # количество экземпляров
        ]]

        def __init__(self, saving_groups: utils.SavingGroups, save_folder: pathlib.Path, base_matcher: Callable[[str, str], bool]):
            self.__saving_groups = saving_groups
            self.__save_folder = save_folder
            self.__base_matcher = base_matcher
            # ---
            self.__save_folder.mkdir(parents=True, exist_ok=True)

        def prepare(self,
                    match_expressions: List[str] = [],
                    *,
                    step: bool,
                    dxf: bool,
                    quantity_expression: Callable[[int], int] = lambda q: q) -> TableData:
            table_data = []
            for saving_group in self.__saving_groups:
                component_full_name = str(saving_group.save_file_name)
                for match_expression in match_expressions:
                    if self.__base_matcher(match_expression, component_full_name):
                        if saving_group.mark is not None:
                            raise Exception(f"'{component_full_name}' is already passed by '{saving_group.mark}'-mark")
                        saving_group.mark = f"CNCLaserCuttingDocCreator by '{match_expression}'"
                        if step:
                            step_file = self.__save_folder / 'STEP' / saving_group.save_file_name.with_suffix('.step')
                            utils.save_body_from_component_like_step(saving_group.component, saving_group.body, step_file)
                            utils.success.log_line(f"STEP file created: {step_file}")
                        if dxf:
                            dxf_file = self.__save_folder / 'DXF' / saving_group.save_file_name.with_suffix('.dxf')
                            utils.save_body_from_component_like_dxf(saving_group.component, saving_group.body, dxf_file)
                            utils.success.log_line(f"DXF file created: {dxf_file}")
                        table_data.append([component_full_name, step, dxf, quantity_expression(saving_group.quantity)])
                        break
            return table_data

    def __init__(self, project_name: str):
        self.__content = [
            f"# Техническое задания на изготовление металлических деталей для «{project_name}» методом ЧПУ лазерной резки",
            "",
            "❗ **Геометрические параметры всех деталей в STEP/DXF-файлах учитывают технологические отступы:**",
            "Траектория реза задается относительно контура детали следующим образом:",
            "- для сквозных отверстий, пазов и иных внутренних элементов, рез выполняется по внутреннему контуру (материал удаляется изнутри контура);",
            "- для наружного контура детали (отрезка заготовки), рез выполняется по внешнему контуру (материал удаляется снаружи контура).",
            "",
            "❗В случае если деталь изготавливается при помощи резки листового металла, документация содержит соответствующий DXF файл!",
            "",
            "❗В случае, если фактические параметры металлических заготовок будут отличаться от заданных, прошу сообщить отдельно для внесения корректировок в проект изделия!",
            "",
        ]

    def add_table(self, table_header: str, table_data: TableDataPreparator.TableData, material_link: Optional[str] = None) -> 'CNCLaserCuttingDocCreator':
        try:
            if len(table_data) > 0:
                table_data = sorted(table_data, key=lambda x: x[0])
                table_data = tabulate(table_data, headers=["Деталь-файл", "STEP", "DXF", "Количество (штук)"], tablefmt="pipe")
                self.__content.extend([
                    f"## {table_header}",
                    f"[Справочная ссылка для материала]({material_link})\n" if material_link else "",
                    f"{table_data}",
                    "",
                ])
        except Exception as error:
            raise RuntimeError(f"cannot add '{table_header}'-table in DOC: {error}")
        return self

    def add_8mm_steel_sheet_table(self, table_data: TableDataPreparator.TableData) -> 'CNCLaserCuttingDocCreator':
        return self.add_table('Лист стальной горячекатанный 8мм', table_data, 'https://купитьметалл.рф/product/list-gk-8-st3sp-ps-5')

    def add_6mm_steel_sheet_table(self, table_data: TableDataPreparator.TableData) -> 'CNCLaserCuttingDocCreator':
        return self.add_table('Лист стальной горячекатанный 6мм', table_data, 'https://купитьметалл.рф/product/list-gk-6-st3sp-ps-5')

    def add_4mm_steel_sheet_table(self, table_data: TableDataPreparator.TableData) -> 'CNCLaserCuttingDocCreator':
        return self.add_table('Лист стальной горячекатанный 4мм', table_data, 'https://купитьметалл.рф/product/list-gk-4-st3sp-ps-5')

    def create(self, save_folder: pathlib.Path):
        doc_file_path = save_folder / 'CNC_Laser_Metal_Cutting.md'
        try:
            with open(doc_file_path, "w", encoding="utf-8") as file:
                file.write("\n".join(self.__content))
            utils.success.log_line(f"CNC-Laser-Cutting documentation created: {doc_file_path}")
        except Exception as error:
            raise RuntimeError(f"cannot create DOC in {doc_file_path}: {error}")
