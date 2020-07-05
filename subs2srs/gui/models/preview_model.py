import re
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
from PyQt5.QtMultimedia import QSoundEffect, QSound, QAudioFormat, QAudioOutput
from subs2srs.gui.audio import Audio


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
        GlobalObject().addEventListener("previewAdio", self.playAudio)

    def table(self):
        preview_table: QTableWidget = self._app.findChild(
            QTableWidget, "Preview.Table")
        if not preview_table:
            return None

        return preview_table

    @pyqtSlot()
    def playAudio(self, event):
        preview_table = self.table()
        index = preview_table.selectedIndexes()
        row = 0
        if index:
            row = index[0].row()

        item = self._state.preview.items[row]
        start = item.from_time / 1000
        audio_bytes = self._extractor.get_audio(
            start, item.end_time / 1000)

        if self._state.preview.audio:
            self._state.preview.audio.stop()

        audio = Audio(audio_bytes)
        self._state.preview.audio = audio
        audio.play()

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
            self.setInactive(preview_table, i.row(), i.column())

        self.updateActiveLineCount()

    def setInactive(self, preview_table, row_index, column_index):
        self._state.preview.inactive_items.add(row_index)
        item = preview_table.item(row_index, column_index)
        item.setBackground(Qt.darkRed)
        f = item.font()
        f.setStrikeOut(True)
        item.setFont(f)

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
                snapshot2: QTextEdit = self._app.findChild(
                    QObject, "PreviewSub2")
                snapshot2.setText(item.native_sub)

            output = self._extractor.get_snapshot(item.from_time_seconds())
            # TODO: update snapshot on different thread so it's non blocking
            l: QLabel = self._app.findChild(QLabel, "PreviewSnapshot")
            p = QPixmap()
            p.loadFromData(output)
            l.setPixmap(p)

    @pyqtSlot()
    def toMain(self, event):
        self._state.preview = StatePreview()
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
        self._state.preview.inactive_items.add(1)

        preview = Preview(items)

        self._app.setCentralWidget(preview)
        self.updateDetails(0)
        self._app.updateGeometry()

        preview_table = self.table()
        for i, item in enumerate(items):
            item: PreviewItem
            sub = item.target_sub
            if not is_good_japanese(sub):
                self.setRowInactive(preview_table, i)

        self.updateActiveLineCount()

    def setRowInactive(self, preview_table, row_index):
        for i in range(preview_table.columnCount()):
            self.setInactive(preview_table, row_index, i)


def is_good_japanese(text: str):
    # （
    # ）
    # remove: 。♪♪～
    # if len(text) < 6:
    #     return False

    if not is_japanese(text):
        return False

    clean = re.sub(r'（.*）', '', text).strip()
    if not is_min_length(clean):
        return False

    return True


kanji_regex = re.compile('([一-龯])')
kana_regex = re.compile('([ぁ-んァ-ン])')
japanese_regex = re.compile('([一-龯ぁ-んァ-ン])')


def is_japanese(text: str):
    matches = re.search(japanese_regex, text)

    return not matches is None


def is_min_length(text: str):
    kanji_match = re.findall(kanji_regex, text)
    if kanji_match:
        return len(text) > 6

    else:
        return len(text) > 8
