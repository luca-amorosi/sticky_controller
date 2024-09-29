from maya import cmds

from sticky_controller.core import mesh, controller


def create_sticky(position: tuple[float, float, float], geometry: str):
    """Creates a softMod deformer with a bindPreMatrix setup that allows it to
    deform and follow a mesh without double transformation.

    :param position: WorldSpace position at which the sticky is built.
    :param geometry: Geometry to deform.

    :returns: SoftMod node.
    """
    de = mesh.get_deformers(geometry)[0]

    # Build uvPin at specified uv position.
    uvp = f"{geometry}_sticky_uvPin"
    if not cmds.objExists(uvp):
        uvp = cmds.createNode("uvPin", name=uvp)
    # Get free attribute index.
    used_indexes = cmds.getAttr(f"{uvp}.coordinate", multiIndices=True)
    idx = int(used_indexes[-1] + 1) if used_indexes else 0
    cmds.setAttr(f"{uvp}.normalAxis", 1)
    shp_def = mesh.get_shape_deformed(geometry)
    shp_orig = mesh.get_original_shape(geometry)
    uv = mesh.get_uv_coordinates(position, shp_def)
    cmds.setAttr(f"{uvp}.coordinate[{idx}][coordinateU]", uv[0])
    cmds.setAttr(f"{uvp}.coordinate[{idx}][coordinateV]", uv[1])
    if not cmds.listConnections(
        f"{uvp}.deformedGeometry", source=True, destination=False
    ):
        cmds.connectAttr(f"{de}.outputGeometry[0]", f"{uvp}.deformedGeometry")
        cmds.connectAttr(f"{shp_orig}.outMesh", f"{uvp}.originalGeometry")

    sticky_name = f"{geometry}_{idx}"

    # Create softMod controllers
    base_orig, base_ctrl = controller.create(
        name=f"{sticky_name}_softMod_slide_ctrl",
        shape_type="square_pin",
    )
    orig, ctrl = controller.create(
        name=f"{sticky_name}_softMod_ctrl",
        degree=3,
        shape_type="sphere",
        color="red",
    )
    # TODO: create the controller directly with the right size and orientation.
    # controller.rotate(base_ctrl, (90, 0, 0), from_transform_pivot=True)
    # controller.scale(base_ctrl, (0.15, 1, 0.15), from_transform_pivot=True)
    # Add custom attributes to edit the sticky.
    cmds.addAttr(
        ctrl,
        longName="sticky_header",
        niceName=" ",
        attributeType="enum",
        enumName="Sticky",
    )
    cmds.setAttr(channelBox=True)
    cmds.addAttr(
        ctrl,
        longName="radius",
        attributeType="double",
        defaultValue=10,
        keyable=True,
        min=0,
    )
    cmds.addAttr(
        ctrl,
        longName="falloff_mode",
        attributeType="enum",
        enumName="Volume:Surface:",
        keyable=True,
    )
    cmds.parent(orig, base_ctrl)

    # Create softMod node.
    cmds.select(clear=True)
    soft_mod, soft_mod_handle = cmds.softMod(name=f"{sticky_name}_sfm")
    cmds.connectAttr(f"{ctrl}.falloff_mode", f"{soft_mod}.falloffMode")
    cmds.connectAttr(f"{ctrl}.radius", f"{soft_mod}.falloffRadius")
    cmds.setAttr(f"{soft_mod_handle}.visibility", False)

    # Create decomposeMatrix, will be connected to falloffCenter attribute.
    dcmtx = cmds.createNode("decomposeMatrix", name=f"{sticky_name}_sticky_dm")
    # Connect node network.
    mmtx = cmds.createNode("multMatrix", name=f"{sticky_name}_sticky_mm")
    cmds.connectAttr(f"{base_ctrl}.worldMatrix][0]", f"{dcmtx}.inputMatrix")
    cmds.connectAttr(
        f"{base_ctrl}.worldMatrix][0]", f"{soft_mod_handle}.offsetParentMatrix"
    )
    cmds.connectAttr(f"{dcmtx}.outputTranslate", f"{soft_mod}.falloffCenter")
    cmds.connectAttr(f"{uvp}.outputMatrix][{idx}]", f"{mmtx}.matrixIn][1]")
    cmds.connectAttr(f"{mmtx}.matrixSum", f"{base_orig}.offsetParentMatrix")
    cmds.connectAttr(
        f"{base_ctrl}.worldInverseMatrix[0]", f"{soft_mod}.bindPreMatrix"
    )

    # Connect controller to softMod handle through a matrix calculation.
    ctrl_mmtx = cmds.createNode(
        "multMatrix", name=f"{sticky_name}_sticky_transforms_mm"
    )
    cmds.connectAttr(f"{base_ctrl}.worldMatrix", f"{ctrl_mmtx}.matrixIn[0]")
    cmds.connectAttr(f"{orig}.worldInverseMatrix", f"{ctrl_mmtx}.matrixIn[1]")
    cmds.connectAttr(f"{ctrl}.worldMatrix", f"{ctrl_mmtx}.matrixIn[2]")
    cmds.connectAttr(
        f"{base_ctrl}.worldInverseMatrix", f"{ctrl_mmtx}.matrixIn[4]"
    )
    ctrl_dcmtx = cmds.createNode(
        "decomposeMatrix", name=f"{ctrl_mmtx}_matrixSum_dm"
    )
    cmds.connectAttr(f"{ctrl_mmtx}.matrixSum", f"{ctrl_dcmtx}.inputMatrix")
    cmds.connectAttr(
        f"{ctrl_dcmtx}.outputTranslate", f"{soft_mod_handle}.translate"
    )
    cmds.connectAttr(f"{ctrl_dcmtx}.outputRotate", f"{soft_mod_handle}.rotate")
    cmds.connectAttr(f"{ctrl_dcmtx}.outputScale", f"{soft_mod_handle}.scale")

    # Parent the base controller's orig and the softMod's handle in a group.
    grp = cmds.createNode("transform", name=f"{sticky_name}_sticky_grp")
    stickies_grp = "STICKIES"
    if not cmds.objExists(stickies_grp):
        stickies_grp = cmds.createNode("transform", name=stickies_grp)
    cmds.parent([base_orig, soft_mod_handle], grp)
    cmds.parent(grp, stickies_grp)

    # Add main mesh to the sticky.
    add_geometries_to_soft_mod(soft_mod=soft_mod, geometries=[geometry])
    cmds.select(clear=True)


def add_geometries_to_soft_mod(soft_mod: str, geometries: list[str]):
    """Add given geometries to the soft mod allowing it to deform multiple
    geometries at once.

    :param soft_mod: Soft mod node to add the geometries on.
    :param geometries: Geometries to be deformed by the soft mod.
    """
    cmds.softMod(soft_mod, edit=True, geometry=geometries)


def remove_geometries_from_soft_mod(soft_mod: str, geometries: list[str]):
    """Remove given geometries from the soft mod.

    :param soft_mod: Soft mod node to add the geometries on.
    :param geometries: Geometries to be removed from the soft mod.
    """
    cmds.softMod(soft_mod, edit=True, remove=True, geometry=geometries)
