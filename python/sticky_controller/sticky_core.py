from maya import cmds

import sticky_controller.utils
from sticky_controller import log


def create_sticky(position: tuple[float, float, float], geometry: str):
    """Creates a softMod deformer with a bindPreMatrix setup that allows it to
    deform and follow a mesh without double transformation.

    :param position: WorldSpace position at which the sticky is built.
    :param geometry: Geometry to deform.

    :returns: SoftMod node.
    """
    name = geometry.name
    de = Node(deformers_utils.get_deformers(geometry.name, return_name=True)[0])

    # Build uvPin at specified uv position.
    uvp = check_create_node("uvPin", name=f"{name}_sticky_uvPin")
    idx = 1
    if uvp["coordinate"].get_used_indices():
        idx = uvp["coordinate"].get_used_indices()[-1] + 1
    uvp["normalAxis"].set(1)
    shp_def = shapes.get_shape_deformed(geometry)
    shp_orig = shapes.get_original_shape(geometry)
    uv = mesh.get_uv_coordinates(position, shp_def)
    uvp[f"coordinate"][idx]["coordinateU"].set(uv[0])
    uvp[f"coordinate"][idx]["coordinateV"].set(uv[1])
    if not uvp["deformedGeometry"].source():
        de["outputGeometry"][0].connect(uvp["deformedGeometry"])
        shp_orig["outMesh"].connect(uvp["originalGeometry"])

    sticky_name = f"{name}_{idx}"

    # Create softMod controllers
    base_orig, base_ctrl = controller.create(
        name=f"{sticky_name}_softMod_slide_ctrl",
        orig=True,
        shape_type="square_pin",
    )
    orig, ctrl = controller.create(
        name=f"{sticky_name}_softMod_ctrl",
        orig=True,
        degree=3,
        shape_type="sphere",
        color="red",
    )
    controller.rotate(base_ctrl, (90, 0, 0), from_transform_pivot=True)
    controller.scale(base_ctrl, (0.15, 1, 0.15), from_transform_pivot=True)
    # Add custom attributes to edit the sticky.
    attributes.add_header(ctrl, label="Sticky")
    ctrl.add_attr(
        long_name="radius",
        attributeType="double",
        defaultValue=1,
        keyable=True,
        min=0,
    )
    ctrl["radius"].set(10)
    ctrl.add_attr(
        long_name="falloff_mode",
        attributeType="enum",
        enumName="Volume:Surface:",
        keyable=True,
    )
    orig.set_parent(base_ctrl)

    # Create softMod node.
    cmds.select(clear=True)
    soft_mod, soft_mod_handle = cmds.softMod(name=f"{sticky_name}_sfm")
    soft_mod = Node(soft_mod)
    soft_mod_handle = DagNode(soft_mod_handle)
    ctrl["falloff_mode"].connect(soft_mod["falloffMode"])
    ctrl["radius"].connect(soft_mod["falloffRadius"])
    soft_mod_handle["visibility"].set(0)

    # Create decomposeMatrix, will be connected to falloffCenter attribute.
    dcmtx = create_node("decomposeMatrix", name=f"{sticky_name}_sticky_dm")

    # Connect node network.
    mmtx = create_node("multMatrix", name=f"{sticky_name}_sticky_mm")
    base_ctrl["worldMatrix"][0].connect(dcmtx["inputMatrix"])
    base_ctrl["worldMatrix"][0].connect(soft_mod_handle["offsetParentMatrix"])
    dcmtx["outputTranslate"].connect(soft_mod["falloffCenter"])
    uvp["outputMatrix"][idx].connect(mmtx["matrixIn"][1])
    mmtx["matrixSum"].connect(base_orig["offsetParentMatrix"])
    base_ctrl["worldInverseMatrix"][0].connect(soft_mod["bindPreMatrix"])

    # Connect controller to softMod handle through a matrix calculation.
    ctrl_mmtx = create_node(
        "multMatrix", name=f"{sticky_name}_sticky_transforms_mm"
    )
    base_ctrl["worldMatrix"].connect(ctrl_mmtx["matrixIn"][0])
    orig["worldInverseMatrix"].connect(ctrl_mmtx["matrixIn"][1])
    ctrl["worldMatrix"].connect(ctrl_mmtx["matrixIn"][2])
    base_ctrl["worldInverseMatrix"].connect(ctrl_mmtx["matrixIn"][4])
    ctrl_dcmtx = matrix.decompose(ctrl_mmtx["matrixSum"])
    ctrl_dcmtx["outputTranslate"].connect(soft_mod_handle["translate"])
    ctrl_dcmtx["outputRotate"].connect(soft_mod_handle["rotate"])
    ctrl_dcmtx["outputScale"].connect(soft_mod_handle["scale"])

    # Parent the base controller's orig and the softMod's handle in a group.
    grp = create_node("transform", name=f"{sticky_name}_sticky_grp")
    stickies_grp = check_create_node("transform", name="STICKIES")
    grp.set_children([base_orig, soft_mod_handle])
    grp.set_parent(stickies_grp)

    # Add main mesh to the sticky.
    add_geometries_to_soft_mod(soft_mod=soft_mod, geometries=[geometry])
    cmds.select(clear=True)


def add_geometries_to_soft_mod(soft_mod: Node, geometries: list[DagNode]):
    """Add given geometries to the soft mod allowing it to deform multiple
    geometries at once.

    :param soft_mod: Soft mod node to add the geometries on.
    :param geometries: Geometries to be deformed by the soft mod.
    """
    cmds.softMod(
        soft_mod.name, edit=True, geometry=[geo.name for geo in geometries]
    )


def remove_geometries_from_soft_mod(soft_mod: Node, geometries: list[DagNode]):
    """Remove given geometries from the soft mod.

    :param soft_mod: Soft mod node to add the geometries on.
    :param geometries: Geometries to be removed from the soft mod.
    """
    cmds.softMod(
        soft_mod.name,
        edit=True,
        remove=True,
        geometry=[geo.name for geo in geometries],
    )


@sticky_controller.utils.undoable
def run_create_sticky():
    sel = cmds.ls(selection=True)
    if not sel:
        log.warning("Please select one vertex !")
        return
    geometry = DagNode(sel[-1].split(".")[0])
    position = transforms.get_world_pos(sel[-1])
    create_sticky(position=position, geometry=geometry)
