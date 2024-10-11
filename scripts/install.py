import sys

from pathlib import Path

from maya import cmds, mel


def add_package_to_python_path():
    """Add the sticky_controller package to the python path."""
    # .../sticky_controller/python.
    package_path = Path(__file__).parents[1].joinpath("python").resolve()
    if package_path.as_posix() not in sys.path:
        sys.path.append(package_path.as_posix())


def add_package_to_python_path_cmd():
    """Returns a command used in the shelf button command and doubleClickCommand
    to add to the PYTHONPATH the sticky_controller package's path.
    """
    install_file_path = Path(__file__).resolve().as_posix()
    cmd = "import sys; from pathlib import Path\n"
    cmd += f"install_file_path = Path('{install_file_path}')\n"
    cmd += "package_path = install_file_path.parents[1].joinpath('python').resolve()\n"
    cmd += "if package_path.as_posix() not in sys.path:\n"
    cmd += "    sys.path.append(package_path.as_posix())"

    return cmd


def onMayaDroppedPythonFile(_):
    """Create button to create sticky and open Ui in current active shelf."""
    add_package_to_python_path()

    from sticky_controller import utils, __version__

    icon_path = utils.get_resource("icons").joinpath("sticky.png")
    label = "Sticky"
    tooltip = f"LeftClick -> Create sticky controller on selected vertex \nDoubleClick -> Open sticky Ui \n{__version__}"
    cmd = f"{add_package_to_python_path_cmd()} \nfrom sticky_controller.core import sticky; sticky.create()"
    double_click_cmd = f"{add_package_to_python_path_cmd()} \nfrom sticky_controller.ui import sticky_ui; sticky_ui.StickyUi.show_ui()"

    # Add button to current shelf.
    top_shelf = mel.eval("$nul = $gShelfTopLevel")
    current_shelf = cmds.tabLayout(top_shelf, query=True, st=1)
    cmds.shelfButton(
        parent=current_shelf,
        image=icon_path.resolve().as_posix(),
        command=cmd,
        doubleClickCommand=double_click_cmd,
        label=label,
        annotation=tooltip,
    )
