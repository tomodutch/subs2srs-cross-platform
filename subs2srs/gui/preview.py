from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from subs2srs.core.extractor import Extractor
from subs2srs.gui.factories import *
from subs2srs.gui.globalobject import GlobalObject
from subs2srs.gui.state import State
from subs2srs.core.subtitle import Subtitle
from subs2srs.core.preview_item import PreviewItem
from datetime import timedelta
from typing import List


class Preview(QWidget):
    def __init__(self, items: List[PreviewItem], parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        display = PreviewDisplay(items)

        layout.addWidget(self.setup_top())
        layout.addWidget(display)
        layout.addWidget(PreviewSnapshot())

    def setup_top(self):
        return Top()


class PreviewDisplaySettings(QWidget):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        layout = QVBoxLayout()
        top_layout = QVBoxLayout()
        bottom_layout = QVBoxLayout()
        self.setLayout(layout)

        top_layout.setAlignment(Qt.AlignTop)
        bottom_layout.setAlignment(Qt.AlignBottom)
        layout.addLayout(top_layout)
        layout.addLayout(bottom_layout)

        top_layout.addWidget(
            button("Select All", "Preview.SelectAll", "previewSelectAll"))

        top_layout.addWidget(
            button("Select None", "Preview.SelectNone", "previewSelectNone"))

        top_layout.addWidget(
            button("Invert", "Preview.Invert", "previewSelectInvert"))

        bottom_layout.addWidget(
            info_button("Activate", "Preview.Active", "previewActivate"))

        bottom_layout.addWidget(
            error_button("Deactivate", "Preview.Deactive", "previewDeactivate"))


class PreviewDisplay(QWidget):
    def __init__(self, items: List[PreviewItem], parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        layout = QHBoxLayout()
        self._items = items

        layout.addWidget(self.setup_table())
        layout.addWidget(PreviewDisplaySettings())

        self.setLayout(layout)

    def setup_table(self):
        table = QTableWidget()
        table.setObjectName("Preview.Table")
        table.itemSelectionChanged.connect(dispatch("previewSelectionChange"))
        table.setColumnCount(5)
        table.setSortingEnabled(True)
        table.setSelectionBehavior(QTableView.SelectRows)

        table.setHorizontalHeaderLabels(
            ["From", "To", "Duration", "Sub1", "Sub2"])
        table.setRowCount(len(self._items))
        header = table.horizontalHeader()
        header: QHeaderView
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)

        for i, item in enumerate(self._items):
            item: PreviewItem

            from_time = timedelta(milliseconds=item.from_time)
            end_time = timedelta(milliseconds=item.end_time)
            duration = end_time - from_time
            from_column = QTableWidgetItem(format(from_time))

            table.setItem(i, 0, from_column)
            table.setItem(i, 1, QTableWidgetItem(format(end_time)))
            table.setItem(i, 2, QTableWidgetItem(format(duration)))
            table.setItem(i, 3, QTableWidgetItem(item.target_sub))
            table.setItem(i, 4, QTableWidgetItem(item.native_sub))

        table.resizeColumnsToContents()
        table.resizeRowsToContents()

        return table


def format(time: timedelta):
    return str(time).split(".")[0]


class Top(QWidget):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        layout = QGridLayout()

        input = text("Preview.Search", "changePreviewSearch")
        btn = button("Find", "Preview.Search", "previewSearch")

        layout.addWidget(input, 0, 0, 1, 1)
        layout.addWidget(btn, 0, 2, 1, 1)
        layout.addWidget(Result(), 0, 3, 1, 1)
        self.setLayout(layout)


class Result(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setContentsMargins(0, 0, 0, 0)
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        active_label = info_label("Active", "Preview.Active")
        active_value_label = info_label("0", "Preview.Active.Value")

        inactive_label = error_label("Inactive", "Preview.Inactive")
        inactive_value_label = error_label("0", "Preview.Inactive.Value")

        layout.addWidget(active_label, 0, 0)
        layout.addWidget(active_value_label, 0, 1)
        layout.addWidget(inactive_label, 1, 0)
        layout.addWidget(inactive_value_label, 1, 1)

        self.setLayout(layout)


class PreviewSnapshot(QWidget):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        layout = QGridLayout()
        details_layout = QVBoxLayout()
        details_layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)
        i = image("", "PreviewSnapshot")
        layout.addWidget(i, 0, 0, 1, 1)

        details_layout.addWidget(
            label("Sub1", "SnapshotSub1"), alignment=Qt.AlignTop)
        details_layout.addWidget(
            textarea("PreviewSub1"), alignment=Qt.AlignTop)

        details_layout.addWidget(label("Sub2", "SnapshotSub2"))
        details_layout.addWidget(
            textarea("PreviewSub2", text=""), alignment=Qt.AlignTop)

        layout.addLayout(details_layout, 0, 2, 1, 1)

        preview_audio_button = button(
            "Preview Audio", "PreviewAudio", "previewAdio")

        layout.addWidget(preview_audio_button, 1, 0)
        bottom_layout = QHBoxLayout()

        bottom_layout.addWidget(BottomButton(), alignment=Qt.AlignRight)
        layout.addLayout(bottom_layout, 1, 2)


class BottomButton(QWidget):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        layout = QHBoxLayout()
        self.setLayout(layout)

        back_btn = button("back", "preview.back", "backToMain")
        generate_btn = button("generate", "Preview.Generate", "generate")

        layout.addWidget(back_btn, alignment=Qt.AlignRight)
        layout.addWidget(generate_btn, alignment=Qt.AlignRight)
