from __future__ import annotations

import itertools

from maya import cmds
from maya.api import OpenMaya as om

from sticky_controller import utils

COLORS = {
    "red": [1, 0, 0],
    "yellow": [1, 1, 0],
}


def create_curve(
    edit_points: list[tuple[float, float, float]],
    name: str,
    parent: str,
    degree: int = 1,
    form: int = 1,
) -> str:
    """Create a nurbsCurve.

    :param edit_points: Point list.
    :param name: Name of curve.
    :param parent: Transform to whom the nurbsCurve will be parented.
        If None, a new transform is created with given name.
    :param degree: 1 to 3.
    :param form: Either 1(Open) or 3(Periodic).

    :return: nurbsCurve DagNode.
    """
    curve_mobject = om.MFnNurbsCurve().createWithEditPoints(
        edit_points,  # eps
        degree,
        form,
        False,  # is2D
        True,  # rational
        True,  # uniform
        om.MGlobal.getSelectionListByName(parent).getDependNode(0),  # parent
    )

    curve_node = om.MDagPath.getAPathTo(curve_mobject).partialPathName()
    if name:
        curve_node = cmds.rename(curve_node, name)

    return curve_node


def create(
    name: str, shape_type: str, degree: int = 1, color: str = "yellow"
) -> tuple[str, str]:
    """Create a controller with its orig transform.

    :param name: Name of the controller.
    :param shape_type: Shape types available in "resources/controller_lib".
    :param degree: Either 1 or 3.
    :param color: Any color in COLORS.

    :returns: orig, and controller transforms
    """
    orig = cmds.createNode("transform", name=f"{name}_orig")
    transform = cmds.createNode("transform", name=name, parent=orig)

    curves_data = utils.deserialize(
        f"{utils.get_resource('controller_lib')}/{shape_type}"
    )

    for i, shape_data in enumerate(curves_data):
        shape = create_curve(
            name=f"{name}Shape" if i == 0 else f"{name}Shape{i}",
            degree=degree,
            parent=transform,
            **shape_data,
        )
        # Set color.
        cmds.setAttr(f"{shape}.overrideEnabled", True)
        cmds.setAttr(f"{shape}.overrideRGBColors", True)
        cmds.setAttr(f"{shape}.overrideColorRGB", *COLORS[color])

    return orig, transform


def apply_controllers_position(
    data: dict[str, dict[str, tuple[float, float, float]]]
):
    """Apply position data. Replace the controllers at their position before
    adding or removing deformed geometries.
    """
    for node, pos_data in data.items():
        cmds.xform(node, **pos_data, worldSpace=True)


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
