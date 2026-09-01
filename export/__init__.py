import invoke
import shutil
import pathlib

from datetime import datetime

import utils
import utils.doc_creator


@invoke.task(
    help={
        "path": "path to SW-assembly-project which bodies should be saved as *.step",
        "doc_path": "subfolder in model-folder where step filles should be saved (default is None = in the root folder of the SW-project)",
    })
def step(ctx, path: str = None, doc_path: str = None):
    """
    Mass exporting of SW-solid-bodies in unique step-files.
    """
    project_path = pathlib.Path(path)

    unique_bodies_manager = utils.UniqueBodiesManager()
    unique_bodies_manager.add_from_project(project_path)
    saving_groups = utils.prepare_saving_groups(unique_bodies_manager.unique_bodies)

    doc_folder = pathlib.Path(doc_path) if doc_path else project_path.parent  / 'DOC' / f"step-export {datetime.now().strftime('%Y-%m-%d_%H-%M')}"
    shutil.rmtree(doc_folder, ignore_errors=True)

    polywood = utils.doc_creator.StandardElementsTable(saving_groups)
    polywood.prepare_data([f".+"], step=True, dxf=False, save_folder_opt=doc_folder)

collection = invoke.Collection()
collection.add_task(step)
