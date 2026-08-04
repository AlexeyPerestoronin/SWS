import re
import pathlib

from tabulate import tabulate
from typing import List, Tuple, Optional

from .i_document_creator import IDocumentCreator, TableDataPreparator, QuantityEvaluator, NameTransformator

import utils

__all__ = [
    'LaserCuttingManufacturingElementsTable',
    'CNCLaserCuttingDocCreator',
]


class LaserCuttingManufacturingElementsTable(TableDataPreparator):
    """Table of laser-cut metal parts with STEP/DXF file references and quantities."""

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
                     save_folder_opt: Optional[pathlib.Path] = None) -> 'LaserCuttingManufacturingElementsTable':
        for saving_group in self._saving_groups:
            component_full_name = str(saving_group.save_file_name)
            for match_expression in match_expressions:
                match = re.fullmatch(match_expression, component_full_name)
                if match:
                    if saving_group.mark is not None:
                        raise Exception(f"'{component_full_name}' is already accounted by '{saving_group.mark}'-mark")
                    saving_group.mark = f"LaserCuttingManufacturingElementsTable by '{match_expression}'"
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


class CNCLaserCuttingDocCreator(IDocumentCreator):
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
            "❗В случае если деталь изготавливается при помощи резки листового металла, документация содержит соответствующий DXF файл!",
            "",
            "❗В случае, если фактические параметры металлических заготовок будут отличаться от заданных, прошу сообщить отдельно для внесения корректировок в проект изделия!",
            "",
        ]

    def add_table(self, header: str, table: TableDataPreparator, material_link: Optional[str] = None) -> 'CNCLaserCuttingDocCreator':
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

    def add_8mm_steel_sheet_table(self, table: TableDataPreparator) -> 'CNCLaserCuttingDocCreator':
        return self.add_table('Лист стальной горячекатанный 8мм', table, 'https://купитьметалл.рф/product/list-gk-8-st3sp-ps-5')

    def add_6mm_steel_sheet_table(self, table: TableDataPreparator) -> 'CNCLaserCuttingDocCreator':
        return self.add_table('Лист стальной горячекатанный 6мм', table, 'https://купитьметалл.рф/product/list-gk-6-st3sp-ps-5')

    def add_4mm_steel_sheet_table(self, table: TableDataPreparator) -> 'CNCLaserCuttingDocCreator':
        return self.add_table('Лист стальной горячекатанный 4мм', table, 'https://купитьметалл.рф/product/list-gk-4-st3sp-ps-5')

    def create(self, save_folder: pathlib.Path):
        doc_file_path = save_folder / 'CNC_Laser_Metal_Cutting.md'
        try:
            save_folder.mkdir(parents=True, exist_ok=True)
            with open(doc_file_path, "w", encoding="utf-8") as file:
                file.write("\n".join(self.__content))
            utils.success.log_line(f"CNC-Laser-Cutting documentation created: {doc_file_path}")
        except Exception as error:
            raise RuntimeError(f"cannot create DOC in {doc_file_path}: {error}")
