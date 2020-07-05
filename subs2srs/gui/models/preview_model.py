from subs2srs.gui.globalobject import GlobalObject
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from subs2srs.core.extractor import Extractor
from subs2srs.core.subtitle import Subtitle
from subs2srs.gui.preview import Preview
from subs2srs.gui.state import State, StatePreview
from typing import List
from subs2srs.gui.main_widget import MainWidget
from subs2srs.core.preview_item import PreviewItem


class PreviewModel:
    def __init__(self, app: QMainWindow, state: State):
        super().__init__()

        self._app = app
        self._state = state

        GlobalObject().addEventListener("preview", self.doPreview)
        GlobalObject().addEventListener("backToMain", self.toMain)
        GlobalObject().addEventListener("previewSelectionChange", self.changeSelection)
        GlobalObject().addEventListener("previewDeactivate", self.inactivateLines)
        GlobalObject().addEventListener("previewActivate", self.activateLines)
        GlobalObject().addEventListener("previewSelectAll", self.selectAllPreview)
        GlobalObject().addEventListener("previewSelectNone", self.selectNonePreview)
        GlobalObject().addEventListener("previewSelectInvert", self.selectInvertPreview)

    def table(self):
        preview_table: QTableWidget = self._app.findChild(
            QTableWidget, "Preview.Table")
        if not preview_table:
            return None

        return preview_table

    @pyqtSlot()
    def selectInvertPreview(self, event):
        preview_table = self.table()
        if preview_table is None:
            return

        items = preview_table.children()
        row_count = preview_table.rowCount()
        col_count = preview_table.columnCount()
        i = 0
        while i < row_count:
            j = 0
            while j < col_count:
                item: QTableWidgetItem = preview_table.item(i, j)
                item.setSelected(not item.isSelected())

                j = j + 1

            i = i + 1

    @pyqtSlot()
    def selectNonePreview(self, event):
        preview_table = self.table()
        if preview_table is None:
            return

        preview_table.clearSelection()

    @pyqtSlot()
    def selectAllPreview(self, event):
        preview_table = self.table()
        if preview_table is None:
            return

        preview_table.selectAll()

    @pyqtSlot()
    def inactivateLines(self, event):
        preview_table = self.table()
        if preview_table is None:
            return

        for i in preview_table.selectedIndexes():
            i: QModelIndex
            index = i.row()
            self._state.preview.inactive_items.add(index)
            item = preview_table.item(index, i.column())
            item.setBackground(Qt.darkRed)
            f = item.font()
            f.setStrikeOut(True)
            item.setFont(f)

        self.updateActiveLineCount()

    def updateActiveLineCount(self):
        active_label: QLabel = self._app.findChild(
            QLabel, "Preview.Active.Value")
        inactive_label: QLabel = self._app.findChild(
            QLabel, "Preview.Inactive.Value")

        inactive_count = len(self._state.preview.inactive_items)
        active = str(len(self._state.preview.items) - inactive_count)
        active_label.setText(active)
        inactive_label.setText(str(inactive_count))

    @pyqtSlot()
    def activateLines(self, event):
        preview_table = self.table()
        if preview_table is None:
            return

        for i in preview_table.selectedIndexes():
            i: QModelIndex
            index = i.row()
            if index in self._state.preview.inactive_items:
                self._state.preview.inactive_items.remove(index)

            item: QTableWidgetItem = preview_table.item(index, i.column())
            item.setBackground(QBrush())
            f = item.font()
            f.setStrikeOut(False)
            item.setFont(f)

        self.updateActiveLineCount()

    @pyqtSlot()
    def changeSelection(self, event):
        def chunks(lst, n):
            """Yield successive n-sized chunks from lst."""
            for i in range(0, len(lst), n):
                yield lst[i:i + n]

        preview_table = self.table()
        if preview_table is None:
            return

        rows = chunks(preview_table.selectedItems(),
                      preview_table.columnCount())

        for row in rows:
            row: List[QTableWidgetItem]

        index = preview_table.selectedIndexes()[0]
        self.updateDetails(index.row())

    def updateDetails(self, active_row_index):
        items = self._state.preview.items
        if len(items) > 0:
            item: PreviewItem = items[active_row_index]
            snapshot1: QTextEdit = self._app.findChild(QObject, "PreviewSub1")
            snapshot1.setText(item.target_sub)

            if item.native_sub:
                snapshot2: QTextEdit = self._app.findChild(QObject, "PreviewSub2")
                snapshot2.setText(item.native_sub)

            output = self._extractor.get_snapshot(item.from_time_seconds())
            l: QLabel = self._app.findChild(QLabel, "PreviewSnapshot")
            p = QPixmap()
            p.loadFromData(output)
            l.setPixmap(p)

    @pyqtSlot()
    def toMain(self, event):
        self._app.setCentralWidget(MainWidget())

    @pyqtSlot()
    def doPreview(self, event):
        self._state.preview = StatePreview()
        self._extractor = Extractor(
            media_file=self._state.video_file,
            target_sub=Subtitle(self._state.sub1_file),
            native_sub=Subtitle(self._state.sub2_file)
        )

        items = list(self._extractor.preview())
        self._state.preview.items = items

        preview = Preview(items)

        self._app.setCentralWidget(preview)
        self.updateActiveLineCount()
        self.updateDetails(0)
