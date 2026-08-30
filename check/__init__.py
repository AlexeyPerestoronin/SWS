
import invoke
import pathlib

from typing import Optional, Set
from pyswx.api.swconst.enumerations import SWDocumentTypesE

import utils


@invoke.task(help={
    "path": "path to SW-project models in which should be checked",
})
def project_naming(ctx, path: str = None):
    """
    Check project name via its filename for a SW project.
    """
    assert utils.validate_project_naming(utils.open_document(path).root_model)
    utils.success.log_line("model name is right")


@invoke.task(help={
    'path': 'path to SW-project bodies in which should be checked',
    'repair': 'if True wrong names will be renaming (by default: False)',
})
def bodies_naming(ctx, path: str = None, repair: bool = False):
    """
    Validate names of all solid bodies in a SW project.
    """
    assert path

    unique_body_manager = utils.UniqueBodiesManager()
    unique_body_manager.add_from_project(pathlib.Path(path))
    unique_bodies = unique_body_manager.unique_bodies

    for same_bodies in unique_bodies:
        utils.status.log_line(f"Detected {len(same_bodies)} same bodies:")
        valid_body_names = [(i, body, utils.validate_and_parse_body_name(body)) for (i, (body, _)) in enumerate(same_bodies, 1)]
        valid_user_body_names = [(i, body, valid_body_name) for (i, body, valid_body_name) in valid_body_names if valid_body_name.approach == utils.BodyNameValidationApproach.USER_NAME]
        valid_sw_body_names = [(i, body, valid_body_name) for (i, body, valid_body_name) in valid_body_names if valid_body_name.approach != utils.BodyNameValidationApproach.USER_NAME]

        if len(valid_user_body_names) == 0:
            raise Exception(f"no one user's defined name for same bodies group: {[body.name for (body, _) in same_bodies]}")

        for (i, body, _) in valid_user_body_names:
            utils.info.log_line(f" {i}-body has right user's defined name '{body.name}'")

        common_name = '+'.join(set([valid_body_name.main_name for (_, _, valid_body_name) in valid_user_body_names]))
        last_index = max([0 if not valid_body_name.index else valid_body_name.index for (_, _, valid_body_name) in valid_user_body_names])

        for (i, body, _) in valid_sw_body_names:
            last_index += 1
            new_name = "{} {}".format(common_name, last_index)
            utils.warning.log_line(f" {i}-body has right auto defined name '{body.name}' and {'will be' if repair else 'could be'} renaming to '{new_name}'")
            if repair:
                body.name = new_name


@invoke.task(help={
    "path": "path to SW-project bodies in which should be checked",
})
def folders_naming(ctx, path: str = None):
    """
    Check body folder names in a SW project.
    """

    root_model = utils.open_document(path, SWDocumentTypesE.SW_DOC_PART).root_model
    assert utils.validate_folders_naming(utils.get_solid_body_folders_in_component(root_model.configuration_manager.active_configuration.get_root_component3(False)))
    utils.success.log_line("all folders' names is right!")


@invoke.task(help={
    "path": "path to SW-project which should be complexity checked",
})
def all(ctx, path: str = None):
    """
    Run all naming checks for a SW project
    """
    project_naming(ctx, path)
    bodies_naming(ctx, path)
    folders_naming(ctx, path)


collection = invoke.Collection()
collection.add_task(project_naming, name="project-naming")
collection.add_task(bodies_naming, name="body-naming")
collection.add_task(folders_naming, name="folder-naming")
collection.add_task(all, name="all")
