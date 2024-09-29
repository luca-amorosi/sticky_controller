from __future__ import annotations

import functools
import itertools
from pathlib import Path
from typing import Iterable

from sticky_controller import log

from maya import cmds


def get_package_root() -> Path:
    """
    :returns str: Path of ".../rig" package.
    """
    return Path(__file__).parents[2]


def undoable(function: callable):
    """Decorator to create an undo chunk."""

    @functools.wraps(function)
    def wrapper_function(*args, **kwargs):
        # Open undoChunk
        cmds.undoInfo(openChunk=True, chunkName=function.__name__)

        # Run function.
        try:
            function(*args, **kwargs)
        except Exception:
            log.exception(
                f"An error has occured while running {function.__name__}",
                exc_info=True,
            )

        # Close undoChunk
        cmds.undoInfo(closeChunk=True, chunkName=function.__name__)

    return wrapper_function


def has_common_members(
    array_1: Iterable, array_2: Iterable, common_nbr: int = 1
) -> bool:
    """For given arrays check if they have at least 1 or more common members.

    :param array_1: Arrays of objects.
    :param array_2: Arrays of objects.
    :param common_nbr: Number of common members asked. Default is 1.

    :returns: Bool depending on common members asked.
    """
    return len(set(array_1).intersection(set(array_2))) >= common_nbr


def reset_controllers_position(
    controllers: list[str],
) -> dict[str, dict[str, tuple[float, float, float]]]:
    """Get controllers position, reset there values and returns there stored
    position.
    """
    initial_pos = {}
    for ctrl in controllers:
        # Get initial position.
        xform_flags = {"query": True, "worldSpace": True}
        initial_pos[ctrl] = {
            "translation": cmds.xform(ctrl, **xform_flags, translation=True),
            "rotation": cmds.xform(ctrl, **xform_flags, rotation=True),
            "scale": cmds.getAttr(f"{ctrl}.scale")[0],
        }
        # Reset position to default.
        for attr in itertools.product("trs", "xyz"):
            cmds.setAttr(f"{ctrl}.{attr}", 1 if attr[0] == "s" else 0)

    return initial_pos


def apply_controllers_position(
    data: dict[str, dict[str, tuple[float, float, float]]]
):
    """Apply position data. Replace the controllers at their position before
    adding or removing deformed geometries.
    """
    for node, pos_data in data.items():
        cmds.xform(node, **pos_data, worldSpace=True)
