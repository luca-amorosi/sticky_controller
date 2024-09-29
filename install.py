from maya import cmds, mel

from sticky_controller import utils


def onMayaDroppedPythonFile(_):
    """Create in current shelf the button to create sticky and open Ui."""
    icon_path = utils.get_resource("icons").joinpath("sticky.png")
    label = "Sticky Controller"
    tooltip = "LeftClick - Create sticky controller on selected vertex / DoubleClick - Open sticky Ui"
    cmd = "from sticky_controller.core import sticky; sticky.create()"
    double_click_cmd = "from sticky_controller import ui; ui.StickyUi.show_ui()"

    ## Add button to current shelf.
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
