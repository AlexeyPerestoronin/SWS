import invoke, pathlib
from pyswx.api.swconst.enumerations import SWDocumentTypesE

import utils
import check


@invoke.task(
    help={
        "path": "path to SW-part-project which bodies should be saved as *.step",
        "save-subfolder": "subfolder in model-folder where step filles should be saved (default is None = in the root folder of the SW-project)",
        "execute": "if True unique solid-body will be saved in corresponded step-file, otherwise only log (be default: False)",
    })
def step_from_part(ctx, path: str = None, save_subfolder: str = None, execute: bool = False):
    """
    Mass exporting of SW-solid-bodies in unique step-files.
    """
    check.project_naming(ctx, path)

    root_model = utils.open_document(path, SWDocumentTypesE.SW_DOC_PART).root_model

    unique_bodies_manager = utils.UniqueBodiesManager()
    unique_bodies_manager.add_from_model(root_model)

    save_folder = root_model.get_path_name().parent
    if save_subfolder:
        save_folder = save_folder / pathlib.Path(save_subfolder)

    save_paths_and_bodies = utils.prepare_saving_groups(unique_bodies_manager.unique_bodies, save_folder)

    if execute:
        save_folder.mkdir(parents=True, exist_ok=True)
        for reference_component in save_folder.iterdir():
            reference_component.unlink(missing_ok=True)

        for (reference_body, _, reference_component, step_path) in save_paths_and_bodies:
            try:
                utils.save_body_from_component_like_step(reference_component, reference_body, step_path)
                utils.SUCCESS.log_line(f"step file created: {step_path}")
            except Exception as error:
                utils.ERROR.log_line(f"step file wasn't created: {error}")


@invoke.task(
    help={
        "path": "path to SW-assembly-project which bodies should be saved as *.step",
        "save-subfolder": "subfolder in model-folder where step filles should be saved (default is None = in the root folder of the SW-project)",
        "execute": "if True unique solid-body will be saved in corresponded step-file, otherwise only log (be default: False)",
    })
def step_from_assembly(ctx, path: str = None, save_subfolder: str = None, execute: bool = False):
    """
    Mass exporting of SW-solid-bodies in unique step-files.
    """
    check.project_naming(ctx, path)

    root_assembly = utils.open_document(path, SWDocumentTypesE.SW_DOC_ASSEMBLY).root_assembly

    unique_bodies_manager = utils.UniqueBodiesManager()
    unique_bodies_manager.add_from_assembly(root_assembly)

    save_folder = root_assembly.get_path_name().parent
    if save_subfolder:
        save_folder = save_folder / pathlib.Path(save_subfolder)

    save_paths_and_bodies = utils.prepare_saving_groups(unique_bodies_manager.unique_bodies, save_folder)

    if execute:
        save_folder.mkdir(parents=True, exist_ok=True)
        for reference_component in save_folder.iterdir():
            reference_component.unlink(missing_ok=True)

        for (reference_body, _, reference_component, step_path) in save_paths_and_bodies:
            try:
                utils.save_body_from_component_like_step(reference_component, reference_body, step_path)
                utils.SUCCESS.log_line(f"step file created: {step_path}")
            except Exception as error:
                utils.ERROR.log_line(f"step file wasn't created: {error}")


collection = invoke.Collection()
collection.add_task(step_from_part, name="step-from-part")
collection.add_task(step_from_assembly, name="step-from-assembly")
