from subs2srs.gui.globalobject import GlobalObject
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from subs2srs.core.extractor import Extractor
from subs2srs.core.subtitle import Subtitle
from .process_runnable import ProcessRunnable
from .preview import Preview
from subs2srs.gui.main_widget import MainWidget
from subs2srs.gui.state import State, StatePreview
from typing import List


class ViewModel:
    def __init__(self, app: QMainWindow, state: State):
        super().__init__()

        self._app = app
        self._state = state

        GlobalObject().addEventListener("changeDeckName", self.setDeckName)
        GlobalObject().addEventListener("changeSub1", self.changeSub1)
        GlobalObject().addEventListener("changeSub2", self.changeSub2)
        GlobalObject().addEventListener("changeVideo", self.changeVideo)
        GlobalObject().addEventListener("changeOutput", self.changeOutput)
        GlobalObject().addEventListener("generate", self.generate)
        GlobalObject().addEventListener("preview", self.doPreview)
        GlobalObject().addEventListener("backToMain", self.toMain)
        GlobalObject().addEventListener("previewSelectionChange", self.changeSelection)
        GlobalObject().addEventListener("previewDeactivate", self.inactivateLines)
        GlobalObject().addEventListener("previewActivate", self.activateLines)
        GlobalObject().addEventListener("previewSelectAll", self.selectAllPreview)
        GlobalObject().addEventListener("previewSelectNone", self.selectNonePreview)
        GlobalObject().addEventListener("previewSelectInvert", self.selectInvertPreview)

    @pyqtSlot()
    def selectInvertPreview(self, event):
        preview_table: QTableWidget = self._app.findChild(
            QTableWidget, "Preview.Table")
        if not preview_table:
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
        preview_table: QTableWidget = self._app.findChild(
            QTableWidget, "Preview.Table")
        if not preview_table:
            return

        preview_table.clearSelection()

    @pyqtSlot()
    def selectAllPreview(self, event):
        preview_table: QTableWidget = self._app.findChild(
            QTableWidget, "Preview.Table")
        if not preview_table:
            return

        preview_table.selectAll()

    @pyqtSlot()
    def inactivateLines(self, event):
        preview_table: QTableWidget = self._app.findChild(
            QTableWidget, "Preview.Table")
        if not preview_table:
            return

        for i in preview_table.selectedIndexes():
            i: QModelIndex
            index = i.row()
            self._state.preview.inactive_items.add(index)
            item = preview_table.item(index, i.column())
            item.setBackground(Qt.darkRed)

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
        preview_table: QTableWidget = self._app.findChild(
            QTableWidget, "Preview.Table")
        if not preview_table:
            return

        for i in preview_table.selectedIndexes():
            i: QModelIndex
            index = i.row()
            if index in self._state.preview.inactive_items:
                self._state.preview.inactive_items.remove(index)

            item: QTableWidgetItem = preview_table.item(index, i.column())
            item.setBackground(QBrush())

        self.updateActiveLineCount()

    @pyqtSlot()
    def changeSelection(self, event):
        def chunks(lst, n):
            """Yield successive n-sized chunks from lst."""
            for i in range(0, len(lst), n):
                yield lst[i:i + n]

        preview_table: QTableWidget = self._app.findChild(
            QTableWidget, "Preview.Table")
        if not preview_table:
            return

        rows = chunks(preview_table.selectedItems(),
                      preview_table.columnCount())

        for row in rows:
            row: List[QTableWidgetItem]

    @pyqtSlot()
    def toMain(self, event):
        self._app.setCentralWidget(MainWidget())

    @pyqtSlot()
    def setDeckName(self, event):
        child = self._app.findChild(QObject, "Deck.Name")
        self._state.deck_name = child.text()

    @pyqtSlot()
    def changeSub2(self, event):
        if event is None:
            return

        self._state.sub1_file = event.value
        input = self._app.findChild(QObject, "sub2Input")
        input.setText(event.value)

    @pyqtSlot()
    def changeSub1(self, event):
        if event is None:
            return

        self._state.sub1_file = event.value
        input = self._app.findChild(QObject, "sub1Input")
        input.setText(event.value)

    @pyqtSlot()
    def changeVideo(self, event):
        if event is None:
            return

        self._state.video_file = event.value
        input = self._app.findChild(QObject, "Video.Input")
        input.setText(event.value)

    @pyqtSlot()
    def doPreview(self, event):
        self._state.preview = StatePreview()
        self._extractor = Extractor(
            media_file=self._state.video_file,
            target_sub=Subtitle(self._state.sub1_file)
        )

        items = list(self._extractor.preview())
        self._state.preview.items = items

        preview = Preview(items)

        self._app.setCentralWidget(preview)
        self.updateActiveLineCount()

    @pyqtSlot()
    def changeOutput(self, event):
        if event is None:
            return

        self._state.output_file = event.value
        input = self._app.findChild(QObject, "Output.Input")
        input.setText(event.value)

    def updateProgress(self, type, value, i, total):
        progress = self._app.progress
        progress.setValue(value)
        if type == "audio":
            progress.setLabelText(
                "Audio (" + str(i) + "/ " + str(total) + ")")
        elif type == "picture":
            progress.setLabelText(
                "Picture (" + str(i) + "/ " + str(total) + ")")

    def generate(self, event):
        media_file = self._state.video_file
        target_sub = self._state.sub1_file
        output = self._state.output_file

        p = QProgressDialog("Creating audio files",
                            "Cancel", 0, 100, self._app)

        p.setWindowModality(Qt.WindowModal)
        p.setObjectName("Progress.Dialog")
        p.setCancelButton(None)
        p.setAutoClose(True)
        p.show()
        self._app.progress = p

        def run():
            extractor = Extractor(media_file, Subtitle(target_sub))
            for type, i, total in extractor.run(output):
                val = int(i / total * 100)
                QMetaObject.invokeMethod(self._app,
                                         "updateProgress", Qt.QueuedConnection,
                                         Q_ARG(str, type),
                                         Q_ARG(int, val),
                                         Q_ARG(int, i),
                                         Q_ARG(int, total))

        process = ProcessRunnable(target=run, args=())
        process.start()
