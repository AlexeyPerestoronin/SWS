import pathlib
import invoke
import importlib.util

collection = invoke.Collection()

def load_project_task(project_tasks_file_path: pathlib.Path, project_name: str):
    module_specification = importlib.util.spec_from_file_location(project_name, project_tasks_file_path)
    module = importlib.util.module_from_spec(module_specification)
    module_specification.loader.exec_module(module)
    collection.add_collection(module.collection, name=project_name)

load_project_task(pathlib.Path(r"C:\MyLife\SWP\Projects\МАСТЕРСКАЯ\Проект 4\automated.py"), "mm_v_iv")