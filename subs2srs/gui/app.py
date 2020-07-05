import sys
import qdarkstyle
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from subs2srs.gui.globalobject import FileChangeEvent, GlobalObject
from subs2srs.core.extractor import Extractor
from subs2srs.core.subtitle import Subtitle
from subs2srs.gui.models.root_model import RootModel
from subs2srs.gui.main_widget import SubtitlePaneGrid, SubtitleOptions, SaveRow, MainWidget
from subs2srs.gui.state import State


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        state = State()
        self._model = RootModel(self, state)

    @pyqtSlot(str, int, int, int)
    def updateProgress(self, type, value, i, total):
        self._model.updateProgress(type, value, i, total)

    def run(self):
        super().__init__()
        self.setWindowTitle("subs2srs")
        self.setObjectName("App.Main")
        self.setCentralWidget(MainWidget())
        self.setMinimumHeight(600)
        self.setMinimumWidth(800)
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    subs2srs = App()
    subs2srs.run()
    sys.exit(app.exec_())
