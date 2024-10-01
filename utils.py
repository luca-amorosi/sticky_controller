from __future__ import annotations

import json
import functools
import itertools
from pathlib import Path
from typing import Iterable, Any

from maya import cmds

from sticky_controller import log


def get_package_root() -> Path:
    """
    :returns str: Path of ".../rig" package.
    """
    return Path(__file__).parents[2]


def get_resource(string: str | Path) -> Path:
    """Returns ".../package_root/resources/<string>"."""
    directory = get_package_root().joinpath("resources", string)
    if not directory.exists():
        raise NotADirectoryError(f"Directory -{directory}- doesn't exist !")
    return directory


def deserialize(path: str | Path) -> Any:
    """Deserialize file and returns data.

    :param path: Full path of file without extension (Considered as ".json").

    :return: Data.

    :raise NotADirectoryError: If directory does not exist.
    """
    json_file = path if Path(path).suffix == ".json" else Path(f"{path}.json")

    if not Path(json_file).exists():
        raise NotADirectoryError(f"Directory -{json_file}- does not exists !")

    with open(json_file) as f:
        data = json.load(f)

    return data


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
