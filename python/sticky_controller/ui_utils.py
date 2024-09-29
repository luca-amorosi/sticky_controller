from __future__ import annotations

from pathlib import Path

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget
from maya.OpenMayaUI import MQtUtil
from shiboken2 import wrapInstance

from sticky_controller import utils


def get_icon(
    icon_name: str, as_qicon: bool = True, default_dir: str = "resources/icons"
) -> QIcon | str:
    """Return the full path as string of given icon_name if found in
    default directory.

    :param icon_name: Name of icon present in "resources/icons" directory.
    :param as_qicon: If function should return a QIcon object or the fullPath of
        icon.
    :param default_dir: Default directory to look for icons in.
        Ex: "package_root/resources/icons/icon_name.png".
        Default is "resources/icons".

    :returns: QIcon or full_path as a string of the icon.
    """
    path = f"{utils.get_package_root()}/{default_dir}/{icon_name}.png"
    if not Path.exists(Path(path)):
        path = f"{utils.get_package_root()}/resources/icons/icon_not_found.png"
    return QIcon(path) if as_qicon else path


def maya_main_window() -> QWidget:
    """Returns maya mainWindow as a QWidget."""
    return wrapInstance(int(MQtUtil.mainWindow()), QWidget)
