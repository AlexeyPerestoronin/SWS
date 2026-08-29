import pathlib

from tabulate import tabulate

from .i_document_creator import IDocumentCreator, TableDataPreparator, MaterialInfoTable

import utils

__all__ = [
    'CNCMetalMillingDocCreator',
]


class CNCMetalMillingDocCreator(IDocumentCreator):
    """Генератор ТЗ в виде Markdown-документа для фрезерования металла"""

    def __init__(self, project_name: str):
        self.__content = [
            f"# Техническое задания на изготовление металлических деталей для «{project_name}» методом ЧПУ фрезерования",
            "",
            "❗ **Геометрические параметры всех деталей в STEP-файлах учитывают технологические отступы:**",
            "",
            "Траектория фрезерования задается относительно контура детали следующим образом:",
            "- для сквозных отверстий, пазов, карманов и иных внутренних элементов, фрезерование выполняется по внутреннему контуру (материал удаляется изнутри контура);",
            "- для наружного контура детали (отрезка заготовки), фрезерование выполняется по внешнему контуру (материал удаляется снаружи контура).",
            "",
        ]

    def add_table(self, header: str, table: TableDataPreparator, material_info_table: MaterialInfoTable) -> 'CNCMetalMillingDocCreator':
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

    # ---

    def create(self, save_folder: pathlib.Path):
        doc_file_path = save_folder / 'CNC_milling_of_metal.md'
        try:
            save_folder.mkdir(parents=True, exist_ok=True)
            with open(doc_file_path, "w", encoding="utf-8") as file:
                file.write("\n".join(self.__content))
            utils.success.log_line(f"Documentation for CNC-milling of metal have created: {doc_file_path}")
        except Exception as error:
            raise RuntimeError(f"cannot create DOC in {doc_file_path}: {error}")
