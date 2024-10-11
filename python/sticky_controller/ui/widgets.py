from __future__ import annotations

from PySide2.QtCore import Qt
from PySide2.QtGui import QPalette, QColor, QIcon
from PySide2.QtWidgets import (
    QTreeWidget,
    QMenu,
    QAction,
    QTreeWidgetItemIterator,
    QTreeWidgetItem,
)
from maya import cmds


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
            QIcon(":rename.png"), "Select Controllers", parent=self
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
