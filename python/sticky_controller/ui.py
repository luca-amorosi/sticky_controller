from __future__ import annotations


from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QPalette, QColor
from PySide2.QtWidgets import (
    QDialog,
    QTreeWidget,
    QVBoxLayout,
    QWidget,
    QTreeWidgetItem,
    QMenu,
    QAction,
    QInputDialog,
    QPushButton,
    QHBoxLayout,
    QLineEdit,
    QTreeWidgetItemIterator,
)
import shiboken2

from maya import cmds
from maya.OpenMayaUI import MQtUtil

from sticky_controller import utils, core


def maya_main_window() -> QWidget:
    """Returns maya mainWindow as a QWidget."""
    return shiboken2.wrapInstance(int(MQtUtil.mainWindow()), QWidget)


class StickyUi(QDialog):
    UI_NAME = "Stickies"

    def __init__(self):
        super().__init__()

        self._stickies: list[dict[str, str]] = [
            # {"soft_mod": str, "slide_ctrl": str, "ctrl": str}
        ]

        self.main_layout = QVBoxLayout(self)
        self.build_ui()
        self.fill_ui()

    def build_ui(self):
        # Widgets.
        create_btn = QPushButton("Create")
        create_btn.setIcon(
            QIcon(f"{utils.get_package_root()}/icons/sticky.png")
        )
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
        self.filter_lie.textChanged.connect(self.filter_items)
        # Tree.
        create_btn.pressed.connect(core.run_create_sticky)
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
        self.tree.itemClicked.connect(self.enable_sticky)

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

    def enable_sticky(self, item: StickyItem):
        """If item is checked then its soft mod is enabled."""
        item.soft_mod["envelope"].set(item.checkState(0) == Qt.Checked)

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
        ctrls_pos = utils.reset_controllers_position(
            [item.slide_ctrl, item.ctrl]
        )
        core.add_geometries_to_soft_mod(item.soft_mod, geometries)
        utils.apply_controllers_position(ctrls_pos)

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

        core.remove_geometries_from_soft_mod(item.soft_mod, geometries)

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


class StickyTree(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setRootIsDecorated(False)  # Remove left padding.
        self.setHeaderHidden(True)
        self.setColumnCount(3)

        # AlternatingRowColors.
        palette = QPalette()
        palette.setColor(QPalette.Base, QColor(43, 43, 43))
        palette.setColor(QPalette.AlternateBase, QColor(50, 50, 50))
        self.setPalette(palette)
        self.setAlternatingRowColors(True)

        self._build_context_menu()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, position):
        """Show customContextMenu."""
        self.menu.exec_(self.mapToGlobal(position))

    def _build_context_menu(self):
        """Create a context menu with constraints."""
        self.menu = QMenu(self)

        self.select_controllers_act = QAction(
            QIcon(":selectModel.png"), "Select Controllers", parent=self
        )
        self.select_geometries_act = QAction(
            QIcon(":selectSimilar.png"), "Select Geometries", parent=self
        )
        self.add_deformed_geometries_act = QAction(
            QIcon(":addWrapInfluence.png"),
            "Deform selected geometries",
            parent=self,
        )
        self.remove_deformed_geometries_act = QAction(
            QIcon(":removeWrapInfluence.png"),
            "Remove selected geometries",
            parent=self,
        )
        self.rename_act = QAction(
            QIcon(":renamePreset.png"), "Rename", parent=self
        )
        self.delete_act = QAction(QIcon(":delete.png"), "Delete", parent=self)

        self.menu.addAction(self.rename_act)
        self.menu.addAction(self.select_controllers_act)
        self.menu.addAction(self.select_geometries_act)
        self.menu.addSeparator()
        self.menu.addAction(self.add_deformed_geometries_act)
        self.menu.addAction(self.remove_deformed_geometries_act)
        self.menu.addSeparator()
        self.menu.addAction(self.delete_act)

    def filter_items(self, text: str):
        """Hide all items of tree which do not have given text their name."""
        tree_it = QTreeWidgetItemIterator(self, QTreeWidgetItemIterator.All)
        while tree_it.value():
            item = tree_it.value()
            item.setHidden(not text.lower() in item.text(0).lower())
            tree_it += 1


class StickyItem(QTreeWidgetItem):
    def __init__(self, soft_mod: str, slide_ctrl: str, ctrl: str, parent=None):
        super().__init__(parent)

        self.soft_mod = soft_mod
        self.slide_ctrl = slide_ctrl
        self.ctrl = ctrl

        self.setCheckState(0, Qt.Checked)

        self.update_display()

    @property
    def deformed_geometries(self) -> list[str]:
        """Returns the transform of each geometry deformed by the softMod."""
        return [
            cmds.listRelatives(shape, parent=True, path=True)[0]
            for shape in cmds.deformer(self.soft_mod, query=True, geometry=True)
            or []
        ]

    @property
    def has_keys(self) -> bool:
        """Returns whether any controller of the sticky has keyframes or not."""
        for ctrl in [self.ctrl, self.slide_ctrl]:
            for attr in cmds.listAttr(ctrl, keyable=True):
                input_nodes = cmds.listConnections(
                    f"{ctrl}.{attr}",
                    source=True,
                    destination=False,
                    plugs=False,
                )
                if input_nodes and "animCurve" in cmds.nodeType(input_nodes[0]):
                    return True

        return False

    def update_display(self):
        """Check for deformed geometries and if controllers of soft mod has
        keyframes.
        """
        self.setText(0, self.soft_mod)
        self.setText(1, str(len(self.deformed_geometries)))
        self.setIcon(1, QIcon(":mesh.svg"))
        self.setIcon(
            2, QIcon(":setKeyframe.png") if self.has_keys else QIcon("")
        )
