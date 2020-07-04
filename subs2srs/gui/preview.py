from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from subs2srs.gui.factories import button
from subs2srs.gui.globalobject import GlobalObject


class Preview(QWidget):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        layout = QVBoxLayout()
        self.setLayout(layout)
        back_btn = button("back", "preview.back", "backToMain")
        layout.addWidget(back_btn)
