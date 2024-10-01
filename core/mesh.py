from __future__ import annotations

from maya import cmds
from maya.api import OpenMaya as om

import utils


def get_shape_deformed(transform: str, create: bool = True) -> str | None:
    """For given transform, get its shape deformed. A shapeDeformed is
    considered as a shape without intermediateObject checked.

    :param transform: Transform to get shapeDeformed from.
    :param create: If a shapeDeformed should be created if not found.

    :returns: The deformed shape DagNode or None.
    """
    shapes = transform.get_shapes(path=True)
    if len(shapes) != 1:
        for shape in shapes:
            if not shape["intermediateObject"].get():
                return shape

    return create_shape_deformed(transform) if create else None


def create_shape_deformed(transform: str) -> str:
    """Create an orig shape and return deformedShape for non referenced
    deformable object. Or create a shapeDeformed and returns it for referenced
    deformable object.

    :returns DagNode: Shape deformed.
    """
    original_shape = get_original_shape(transform)

    if transform.is_referenced:
        shape_deformed = f"{transform.name.split(':')[-1]}ShapeDeformed"
        shape_deformed = transform.duplicate_shape(name=shape_deformed)
    else:
        shape_deformed = original_shape
        original_shape = transform.duplicate_shape(name=f"{transform}ShapeOrig")

    original_shape["intermediateObject"].set(True)

    return shape_deformed


def get_original_shape(transform: str) -> str:
    """Returns the original shape of a transform. The original Shape is
    considered as the referenced shape for referenced geometries. Or for
    non-referenced geometries, as a shape without any input connection in its
    input attribute. If multiple shapes fulfill this condition get the shape
    which endswith "Orig".

    :param transform: Transform DagNode.

    :returns: DagNode of shape or None if no original shape found.

    :raises RuntimeError: If no shapes found.
    """
    shapes = cmds.listRelatives(transform, shapes=True, path=True)
    if not shapes:
        raise RuntimeError(f"Node -{transform}- doesn't have any shape !")

    if transform.is_referenced:
        for shape in shapes:
            if shape.is_referenced:  # Referenced shape is the original shape.
                return shape

    # For non referenced geometries.
    orig_shapes = []
    for shape in shapes:
        if not shape["inMesh"].inputs():
            orig_shapes.append(shape)

    if len(orig_shapes) == 1:
        return orig_shapes[0]

    for shape in orig_shapes:
        if shape.name.endswith("Orig"):
            return shape


def get_deformers(mesh: str, deformer_types: list[str] = None) -> list[str]:
    """Get all the deformers ordered connected the mesh.

    :param mesh: Mesh to get deformers from, must be a fullPathName.
    :param deformer_types: Only returns deformer of these types.

    :returns: Empty list, or list[str].
    """
    deformer_types = deformer_types or []
    common_types = 1 if not deformer_types else 2
    deformer_types.insert(0, "geometryFilter")

    deformers = []
    for node in cmds.listHistory(mesh):
        node_types = cmds.nodeType(node, inherited=True)
        if not utils.has_common_members(
            node_types, deformer_types, common_types
        ):
            # Not of type "geometryFilter" and any of given deformer_types.
            continue

        # Wrap deformer has no originalGeo attribute, we then get geoMatrix.
        orig_attr = "geomMatrix" if "wrap" in node_types else "originalGeometry"
        orig_geos = cmds.listConnections(
            f"{node}.{orig_attr}", source=True, shapes=True
        )
        if not orig_geos:
            # if no input connections in originalGeo or geomMatrix.
            continue
        shapes = cmds.listRelatives(mesh, shapes=True, path=True)
        if not utils.has_common_members(orig_geos, shapes):
            # Check if any shapes are in originalGeos. This way we can get the
            # deformer even if there are duplicated deformed shapes.
            continue

        if node not in deformers:
            deformers.append(node)

    return deformers


def get_uv_coordinates(
    position: tuple[float, float, float], geometry: str
) -> tuple[float, float]:
    """Get UV coordinates on a geometry based on a transform's world
    position.

    :param position: Tuple of 3 floats.
    :param geometry: Shape of geometry to get UV coordinates from.

    :returns: U and V value.
    """
    cpom = cmds.createNode("closestPointOnMesh")
    cmds.setAttr(f"{cpom}.inPosition", *position)
    cmds.connnectAttr(f"{geometry}.worldMatrix][0]", f"{cpom}.inputMatrix")
    cmds.connnectAttr(f"{geometry}.worldMesh][0]", f"{cpom}.inMesh")
    cmds.delete(cpom.name)

    return (
        cmds.getAttr(f"{cpom}.parameterU"),
        cmds.getAttr(f"{cpom}.parameterV"),
    )
