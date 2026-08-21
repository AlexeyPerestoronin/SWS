import pathlib
import invoke
import importlib.util

from typing import Optional



def load_project_task(tasks_collection, project_tasks_file_path: pathlib.Path, project_name_opt: Optional[str] = None):
    project_name = project_name_opt if project_name_opt else project_tasks_file_path.stem.replace('_', '-')
    module_specification = importlib.util.spec_from_file_location(project_name, project_tasks_file_path)
    module = importlib.util.module_from_spec(module_specification)
    module_specification.loader.exec_module(module)
    tasks_collection.add_collection(module.collection, name=project_name)

collection = invoke.Collection()

SWP_FOLDER = pathlib.Path("C:/MyLife/SWP/Projects")

load_project_task(collection, SWP_FOLDER / "Тесты/tests.py")
load_project_task(collection, SWP_FOLDER / "МАСТЕРСКАЯ/Верстак-Dim1000x600x50/workbench_1000x600x50.py")
load_project_task(collection, SWP_FOLDER / "МАСТЕРСКАЯ/Инженерная-Стенка/V4/engineering_wall.py")
load_project_task(collection, SWP_FOLDER / "МАСТЕРСКАЯ/Запор-Для-Улитка-Ворот/gate_latch.py")
load_project_task(collection, SWP_FOLDER / "МАСТЕРСКАЯ/Кинематический-Верстак/V3/kinematic_workbench.py")
load_project_task(collection, SWP_FOLDER / "МАСТЕРСКАЯ/Держатель-Для-Сварочной-Горелки/welding_torch_holder.py")
load_project_task(collection, SWP_FOLDER / "МАСТЕРСКАЯ/Поворотный-Стул/rotation_chair.py")
