from __future__ import annotations


from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QWidget,
    QInputDialog,
    QPushButton,
    QHBoxLayout,
    QLineEdit,
)
import shiboken2

from maya import cmds
from maya.OpenMayaUI import MQtUtil

from sticky_controller import utils, __version__
from sticky_controller.core import controller, sticky
from sticky_controller.ui.widgets import StickyTree, StickyItem


def maya_main_window() -> QWidget:
    """Returns maya mainWindow as a QWidget."""
    return shiboken2.wrapInstance(int(MQtUtil.mainWindow()), QWidget)


class StickyUi(QDialog):
    _instance = None

    @classmethod
    def show_ui(cls):
        if not cls._instance:
            cls._instance = StickyUi()

        if cls._instance.isHidden():
            cls._instance.show()
        else:
            cls._instance.raise_()
            cls._instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)

        self.setWindowTitle(f"Sticky Controllers - {__version__}")

        self._stickies: list[dict[str, str]] = [
            # {"soft_mod": str, "slide_ctrl": str, "ctrl": str}
        ]

        self.main_layout = QVBoxLayout(self)
        self.build_ui()
        self.fill_ui()

    def build_ui(self):
        # Widgets.
        create_btn = QPushButton("Create")
        create_btn.setIcon(QIcon(f"{utils.get_resource('icons')}/sticky.png"))
        refresh_btn = QPushButton("Reload")
        refresh_btn.setIcon(QIcon(":refresh.png"))
        self.tree = StickyTree()
        self.filter_le = QLineEdit()
        self.filter_le.setPlaceholderText("Search for Sticky name")
        self.filter_le.setClearButtonEnabled(True)

        # Layout.
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(refresh_btn)
        self.main_layout.addLayout(btn_layout)
        self.main_layout.addWidget(self.filter_le)
        self.main_layout.addWidget(self.tree)

        # Connections.
        self.filter_le.textChanged.connect(self.tree.filter_items)
        # Tree.
        create_btn.pressed.connect(self.run_create_sticky)
        refresh_btn.pressed.connect(self.fill_ui)
        self.tree.select_controllers_act.triggered.connect(
            self.select_controllers
        )
        self.tree.select_geometries_act.triggered.connect(
            self.select_geometries
        )
        self.tree.add_deformed_geometries_act.triggered.connect(
            self.add_deformed_geometries
        )
        self.tree.remove_deformed_geometries_act.triggered.connect(
            self.remove_deformed_geometries
        )
        self.tree.rename_act.triggered.connect(self.rename_sticky)
        self.tree.delete_act.triggered.connect(self.delete_sticky)
        self.tree.itemClicked.connect(enable_sticky)

    def fill_ui(self):
        """Fill the tree with all stickies in the scene."""
        self.tree.clear()
        self.get_stickies()

        for sticky_nodes in self._stickies:
            item = StickyItem(**sticky_nodes)
            self.tree.addTopLevelItem(item)

        self.tree.resizeColumnToContents(0)
        self.tree.resizeColumnToContents(1)
        self.tree.resizeColumnToContents(2)

    def get_stickies(self):
        """Get all stickies in the scene and fill the instance attribute with
        it.
        """
        self._stickies.clear()

        for soft_mod in cmds.ls(type="softMod"):
            bind_pre_mtx_sources = cmds.listConnections(
                f"{soft_mod}.bindPreMatrix", source=True, destination=False
            )
            radius_sources = cmds.listConnections(
                f"{soft_mod}.falloffRadius", source=True, destination=False
            )
            if not bind_pre_mtx_sources and not radius_sources:
                # Is a sticky if it has connection in bindPreMatrix and radius.
                continue

            self._stickies.append(
                {
                    "soft_mod": soft_mod,
                    "slide_ctrl": bind_pre_mtx_sources[0],
                    "ctrl": radius_sources[0],
                }
            )

    def select_controllers(self):
        """Select controllers of selected sticky."""
        items = self.tree.selectedItems()
        if items:
            cmds.select([items[0].slide_ctrl, items[0].ctrl], replace=True)

    def select_geometries(self):
        """Select controllers of selected sticky."""
        items = self.tree.selectedItems()
        if items:
            cmds.select(
                [geo.name for geo in items[0].deformed_geometries], replace=True
            )

    @utils.undoable
    def add_deformed_geometries(self):
        """Add selected viewport geometries as deformed geometries of selected
        sticky.
        """
        items = self.tree.selectedItems()
        if not items:
            return
        item: StickyItem = items[0]

        geometries = []
        for node in cmds.ls(selection=True, shortNames=True):
            if (
                cmds.nodeType(node) != "transform"
                or node in item.deformed_geometries
            ):
                continue
            shapes = cmds.listRelatives(node, shapes=True, path=True)
            if shapes and cmds.nodeType(shapes[0]) == "mesh":
                geometries.append(node)

        if not geometries:
            return

        # Reset position of controllers before adding deformed geometries to
        # avoid offset between geos and make them have the same deformation.
        ctrls_pos = controller.reset_controllers_position(
            [item.slide_ctrl, item.ctrl]
        )
        sticky.add_geometries(item.soft_mod, geometries)
        controller.apply_controllers_position(ctrls_pos)

        item.update_display()

    @utils.undoable
    def remove_deformed_geometries(self):
        """Remove selected viewport geometries from deformed geometries of
        selected sticky.
        """
        items = self.tree.selectedItems()
        if not items:
            return
        item: StickyItem = items[0]

        geometries = []
        for node in cmds.ls(selection=True, shortNames=True):
            if (
                cmds.nodeType(node) != "transform"
                or node not in item.deformed_geometries
            ):
                continue
            shapes = cmds.listRelatives(node, shapes=True, path=True)
            if shapes and cmds.nodeType(shapes[0]) == "mesh":
                geometries.append(node)

        if not geometries:
            return

        sticky.remove_geometries(item.soft_mod, geometries)

        item.update_display()

    @utils.undoable
    def rename_sticky(self):
        """Rename the selected sticky controller."""
        items = self.tree.selectedItems()
        if not items:
            return
        item: StickyItem = items[0]

        new_name, ok = QInputDialog.getText(
            self, "Sticky Renamer", "Enter the new sticky name:"
        )

        if not new_name or not ok:
            return

        sticky_orig = cmds.listRelatives(item.slide_ctrl, parent=True)[0]
        sticky_root = cmds.listRelatives(sticky_orig, parent=True)[0]
        base_name = item.soft_mod.replace("_sfm", "")
        for node in cmds.listRelatives(sticky_root, allDescendents=True):
            cmds.rename(node, node.replace(base_name, new_name))
        cmds.rename(item.soft_mod, new_name + "_sfm")
        cmds.rename(sticky_root, sticky_root.replace(base_name, new_name))

        item.update_display()

    @utils.undoable
    def delete_sticky(self):
        """Delete selected sticky."""
        items = self.tree.selectedItems()
        if items:
            sticky_orig = cmds.listRelatives(items[0].slide_ctrl, parent=True)
            cmds.delete(cmds.listRelatives(sticky_orig[0], parent=True)[0])
        self.fill_ui()

    @utils.undoable
    def run_create_sticky(self):
        sticky.create()
        self.fill_ui()


def enable_sticky(item: StickyItem):
    """If item is checked then its soft mod is enabled."""
    cmds.setAttr(f"{item.soft_mod}.envelope", item.checkState(0) == Qt.Checked)
