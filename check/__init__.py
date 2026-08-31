
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
    user_approach = utils.BodyNameValidationApproach.USER_NAME

    def rename_indexed(bodies, common_name, last_index, describe):
        for i, body, _ in bodies:
            last_index += 1
            new_name = f"{common_name} {last_index}"
            utils.warning.log_line(describe(i, body.name, new_name))
            if repair:
                body.name = new_name
        return last_index

    for same_bodies in unique_body_manager.unique_bodies:
        utils.status.log_line(f"Detected {len(same_bodies)} same bodies:")

        parsed = [
            (i, body, utils.validate_and_parse_body_name(body))
            for i, (body, _) in enumerate(same_bodies, 1)
        ]
        user_bodies = [(i, body, name) for i, body, name in parsed if name.approach == user_approach]
        user_new = [(i, body, name) for i, body, name in user_bodies if name.has_new]
        sw_bodies = [(i, body, name) for i, body, name in parsed if name.approach != user_approach]
        names = [body.name for body, _ in same_bodies]

        if not user_bodies:
            raise Exception(f"no one user's defined name for same bodies group: {names}")
        if len(user_new) > 1:
            raise Exception(f"only one user's defined name could be with 'new'-suffix in bodies group: {names}")

        if user_new:
            common_name = user_new[0][2].main_name
            last_index = rename_indexed(
                user_bodies, common_name, 0,
                lambda i, old, new: f" {i}-body has right user's defined name '{old}' but {'will be' if repair else 'should be'} renaming to '{new}'",
            )
        else:
            common_name = '+'.join({name.main_name for _, _, name in user_bodies})
            last_index = max(name.index or 0 for _, _, name in user_bodies)
            for i, body, _ in user_bodies:
                utils.info.log_line(f" {i}-body has right user's defined name '{body.name}'")

        rename_indexed(
            sw_bodies, common_name, last_index,
            lambda i, old, new: f" {i}-body has right auto defined name '{old}' and {'will be' if repair else 'could be'} renaming to '{new}'",
        )


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
