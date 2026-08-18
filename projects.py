import pathlib
import invoke
import importlib.util

collection = invoke.Collection()


def load_project_task(project_tasks_file_path: pathlib.Path, project_name: str):
    module_specification = importlib.util.spec_from_file_location(project_name, project_tasks_file_path)
    module = importlib.util.module_from_spec(module_specification)
    module_specification.loader.exec_module(module)
    collection.add_collection(module.collection, name=project_name)


SWP_FOLDER = pathlib.Path("C:/MyLife/SWP/Projects")

load_project_task(SWP_FOLDER / "Тесты/automated.py", "tests")
load_project_task(SWP_FOLDER / "МАСТЕРСКАЯ/Верстак-Dim1000x600x50/automated.py", "workbench_1000_600_50")
load_project_task(SWP_FOLDER / "МАСТЕРСКАЯ/Инженерная-Стенка/V4/automated.py", "mm_v_iv")
load_project_task(SWP_FOLDER / "МАСТЕРСКАЯ/Кинематический-Верстак/Z-Лифт/V3/automated.py", "z_lift_v_iii")
load_project_task(SWP_FOLDER / "МАСТЕРСКАЯ/Запор-Для-Улитка-Ворот/gate_latch.py", "gate_latch")
load_project_task(SWP_FOLDER / "МАСТЕРСКАЯ/Кинематический-Верстак/V3/automated.py", "kinematic_workbench_v_iii")
load_project_task(SWP_FOLDER / "МАСТЕРСКАЯ/Держатель-Для-Сварочной-Горелки/welding_torch_holder.py", "welding_torch_holder")
load_project_task(SWP_FOLDER / "МАСТЕРСКАЯ/Платформа-Лифтовая-Поворотная/концепт/automated.py", "rotation_lift_platform")
load_project_task(SWP_FOLDER / "МАСТЕРСКАЯ/Поворотный-Стул/rotation_chair.py", "rotation_chair")
