import pathlib

from tabulate import tabulate
from typing import Optional

from .i_document_creator import IDocumentCreator, TableDataPreparator, MaterialInfoTable

import utils

__all__ = [
    'CNC3DPrintingDocCreator',
]


class CNC3DPrintingDocCreator(IDocumentCreator):
    """Генератор ТЗ в виде Markdown-документа для 3D печати пластиковых деталей (STEP)"""

    def __init__(self, project_name: str):
        self.__content = [
            f"# Техническое задания на изготовление пластиковых деталей для «{project_name}» методом ЧПУ 3D печати",
            "",
            "❗ **Геометрические параметры всех деталей в STEP-файлах соответствуют финальной геометрии изделия.**",
            "",
            "Ориентация детали при печати, необходимость поддержек и технологические параметры печати определяются исполнителем исходя из требований прочности и качества поверхности, если иное не указано в справочной информации о материале.",
            "",
            "❗В случае, если фактические параметры материала или печати будут отличаться от заданных, прошу сообщить отдельно для внесения корректировок в проект изделия!",
            "",
        ]

    def add_table(self, header: str, table: TableDataPreparator, material_info_table: Optional[MaterialInfoTable] = None) -> 'CNC3DPrintingDocCreator':
        try:
            table = tabulate(table.get_data(), table.get_headers(), tablefmt="pipe")
            content = [f"## {header}"]
            if material_info_table is not None:
                material_info_table = tabulate(material_info_table.get_data(), material_info_table.get_headers(), tablefmt="pipe")
                content.extend([
                    f"Справочная информация о рабочем материале",
                    f"{material_info_table}",
                    "",
                    "***",
                    "",
                ])
            content.extend([
                f"{table}",
                "",
            ])
            self.__content.extend(content)
        except Exception as error:
            raise RuntimeError(f"cannot add '{header}'-table in DOC: {error}")
        return self

    # filament(s)

    def add_PLA(self, table: TableDataPreparator) -> 'CNC3DPrintingDocCreator':
        material_info_table = MaterialInfoTable()
        material_info_table.prepare_data([
            ["материал", "PLA (полилактид)"],
            ["технология", "FDM / FFF"],
            ["цвет", "не имеет значения (приоритет меньшей итоговой стоимости)"],
            ["заполнение", "не менее 30%"],
            ["высота слоя", "не более 0.2мм"],
            ["поддержки", "по необходимости"],
            ["постобработка", "удаление поддержек обязательно"],
        ])
        return self.add_table('PLA', table, material_info_table)

    def add_PETG(self, table: TableDataPreparator) -> 'CNC3DPrintingDocCreator':
        material_info_table = MaterialInfoTable()
        material_info_table.prepare_data([
            ["материал", "PETG"],
            ["технология", "FDM / FFF"],
            ["цвет", "не имеет значения (приоритет меньшей итоговой стоимости)"],
            ["заполнение", "не менее 30%"],
            ["высота слоя", "не более 0.2мм"],
            ["поддержки", "по необходимости"],
            ["постобработка", "удаление поддержек обязательно"],
        ])
        return self.add_table('PETG', table, material_info_table)

    # ---

    def create(self, save_folder: pathlib.Path):
        doc_file_path = save_folder / 'CNC_3d_printing_of_plastic.md'
        try:
            save_folder.mkdir(parents=True, exist_ok=True)
            with open(doc_file_path, "w", encoding="utf-8") as file:
                file.write("\n".join(self.__content))
            utils.success.log_line(f"Documentation for CNC-3D-printing of plastic have created: {doc_file_path}")
        except Exception as error:
            raise RuntimeError(f"cannot create DOC in {doc_file_path}: {error}")
