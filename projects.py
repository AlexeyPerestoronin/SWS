import pathlib
import invoke
import importlib.util

collection = invoke.Collection()


def load_project_task(project_tasks_file_path: pathlib.Path, project_name: str):
    module_specification = importlib.util.spec_from_file_location(project_name, project_tasks_file_path)
    module = importlib.util.module_from_spec(module_specification)
    module_specification.loader.exec_module(module)
    collection.add_collection(module.collection, name=project_name)


# TODO: move 'C:\MyLife\SWP\Projects' into env-variable
load_project_task(pathlib.Path(r"C:\MyLife\SWP\Projects\Тесты\automated.py"), "tests")
load_project_task(pathlib.Path(r"C:\MyLife\SWP\Projects\МАСТЕРСКАЯ\automated.py"), "work_shop")
load_project_task(pathlib.Path(r"C:\MyLife\SWP\Projects\МАСТЕРСКАЯ\Инженерная-Стенка\V4\automated.py"), "mm_v_iv")
load_project_task(pathlib.Path(r"C:\MyLife\SWP\Projects\МАСТЕРСКАЯ\Кинематический-Верстак\Z-Лифт\V3\automated.py"), "z_lift_v_iii")
load_project_task(pathlib.Path(r"C:\MyLife\SWP\Projects\МАСТЕРСКАЯ\Запор-Для-Ворот\automated.py"), "gate_latch")
load_project_task(pathlib.Path(r"C:\MyLife\SWP\Projects\МАСТЕРСКАЯ\Кинематический-Верстак\V3\automated.py"), "kinematic_workbench_v_iii")
