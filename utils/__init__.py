import re

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


def sw_task(doc_string: str = None, *args, **kwargs):
    """Декоратор для расширения стандартного функционала декоратора @invoke.task"""
    import invoke

    def decorator(func):
        # 1. Если передана строка документации, принудительно устанавливаем её
        if doc_string is not None:
            func.__doc__ = doc_string
        return invoke.task(*args, **kwargs)(func)

    return decorator
