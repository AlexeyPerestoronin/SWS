import re
import invoke
import shutil
import pathlib
import functools
from datetime import datetime

from typing import List
from pyswx.api.sldworks.interfaces import IModelDoc2
from pyswx.api.sldworks.interfaces import IModelDoc2, IBodyFolder

from .logger import *
from .solid_works import *
from .saving_groups import *

__all__ = [
    # local utils functions
    'validate_project_naming',
    'validate_folders_naming',
    'prepare_archive',
    'sw_task',
    # sub modules
    *logger.__all__,
    *solid_works.__all__,
    *saving_groups.__all__,
]


def validate_project_naming(model: IModelDoc2):
    """
    Check project name via its model
    """

    model_name = model.get_path_name().stem
    model_name_pattern = r'[A-ZА-ЯЁ](\w|\d)*(-[A-ZА-ЯЁ](\w|\d)*)*'
    if not bool(re.fullmatch(model_name_pattern, model_name)):
        raise Exception(f"model name '{model_name}' does not match by regular expression: {model_name_pattern}")
    return True


def validate_folders_naming(folders: List[IBodyFolder]):
    """
    Check names of all folders in list.
    """

    folder_name_pattern = r'\w+(-\w+)*'
    for folder in folders:
        folder_name = folder.get_feature().name
        if not bool(re.match(folder_name_pattern, folder_name)):
            raise Exception(f"folder name '{folder_name}' does not match by regular expression: {folder_name_pattern}")
    return True


def prepare_archive(root_dir: pathlib.Path, archive_dir: pathlib.Path, archive_name: str, archive_type: str, add_date: bool):
    """
    Создаёт архив:
    @root_dir - задаёт корневую директорию из которой должны браться данные для архивирования
    @archive_dir - задаёт директорию где должен появиться архив
    @archive_name - задаёт имя архива
    @archive_type - задаёт тип архива (например 'zip')
    @add_date - если True добавляет к имени архива постфикс времени в формате %Y-%m-%d
    """
    if add_date:
        archive_name = f"{archive_name} {datetime.now().strftime('%Y-%m-%d')}"
    archive = (archive_dir / archive_name).with_suffix(f'.{archive_type}')
    archive.unlink(missing_ok=True)
    shutil.make_archive(base_name=str(archive.with_suffix('')), root_dir=root_dir, format=archive_type)


def sw_task(doc_string: str = None, *args, **kwargs):
    """Декоратор для расширения стандартного функционала декоратора @invoke.task"""

    def decorator(func):
        # 1. Если передана строка документации, устанавливаем её для оригинальной функции
        if doc_string is not None:
            func.__doc__ = doc_string

        @functools.wraps(func)
        def wrapper(*func_args, **func_kwargs):
            if doc_string is not None:
                # Выводим doc_string в консоль перед выполнением
                logger.status_info.log_line(doc_string)
            return func(*func_args, **func_kwargs)

        return invoke.task(*args, **kwargs)(wrapper)

    return decorator
