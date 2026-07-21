import pathlib

from tabulate import tabulate
from collections.abc import Callable
from typing import List, Tuple, Optional, TypeAlias

from .i_document_creator import IDocumentCreator

import utils

__all__ = [
    'AssemblyDocCreator',
]


class AssemblyDocCreator(IDocumentCreator):
    """TODO: need to provide some comment"""

    class TableDataPreparator:
        """TODO: need to provide some comment"""

        TableData: TypeAlias = List[Tuple[
            str,  # название детали
            int  # количество экземпляров
        ]]

        def __init__(self, saving_groups: utils.SavingGroups, save_folder: pathlib.Path, base_matcher: Callable[[str, str], bool]):
            self.__marked_saving_groups = [['', saving_group] for saving_group in saving_groups]
            self.__save_folder = save_folder
            self.__base_matcher = base_matcher
            # ---
            self.__save_folder.mkdir(parents=True, exist_ok=True)

        def prepare(self, match_expressions: List[str] = [], *, quantity_expression: Callable[[int], int] = lambda q: q) -> TableData:
            table_data = []
            for marked_saving_group in self.__marked_saving_groups:
                mark = marked_saving_group[0]
                (reference_body, quantity, reference_component, save_file_name) = marked_saving_group[1]
                component_full_name = str(save_file_name)
                for match_expression in match_expressions:
                    if self.__base_matcher(match_expression, component_full_name):
                        if mark != '':
                            raise Exception(f"'{component_full_name}' is already passed by '{mark}'-mark")
                        step_file = self.__save_folder / 'STEP' / save_file_name.with_suffix('.step')
                        utils.save_body_from_component_like_step(reference_component, reference_body, step_file)
                        utils.success.log_line(f"STEP file created: {step_file}")
                        table_data.append([component_full_name, quantity_expression(quantity)])
                        break
            return table_data

    def __init__(self, project_name: str):
        self.__content = [
            f"# Техническое задания на закупку базовых сборочных компонентов для «{project_name}»",
            "",
            "❗Для точной идентификации физической формы компонента смотри соответствующий STEP файл.",
            "",
        ]

    def add_table(self, table_header: str, table_data: TableDataPreparator.TableData, component_link: Optional[str] = None) -> 'AssemblyDocCreator':
        try:
            if len(table_data) > 0:
                table_data = sorted(table_data, key=lambda x: x[0])
                table_data = tabulate(table_data, headers=["Компонент", "STEP", "Количество (штук)"], tablefmt="pipe")
                self.__content.extend([
                    f"## {table_header}",
                    f"[Справочная ссылка для компонента]({component_link})\n" if component_link else "",
                    f"{table_data}",
                    "",
                ])
        except Exception as error:
            raise RuntimeError(f"cannot add '{table_header}'-table in DOC: {error}")
        return self

    def create(self, save_folder: pathlib.Path):
        doc_file_path = save_folder / 'Assembly_Components.md'
        try:
            with open(doc_file_path, "w", encoding="utf-8") as file:
                file.write("\n".join(self.__content))
        except Exception as error:
            raise RuntimeError(f"cannot create DOC in {doc_file_path}: {error}")
