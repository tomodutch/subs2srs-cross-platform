import sys
import qdarkstyle
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from subs2srs.gui.globalobject import FileChangeEvent, GlobalObject
from subs2srs.core.extractor import Extractor
from subs2srs.core.subtitle import Subtitle
from subs2srs.gui.view_model import ViewModel
from subs2srs.gui.main_widget import SubtitlePaneGrid, SubtitleOptions, SaveRow, MainWidget


class State:
    deck_name = None
    sub1_file = "/Users/thomasfarla/Downloads/Eizouken ni wa Te wo Dasu na! - 01 (NHKG).srt"
    sub2_file = None
    video_file = "/Users/thomasfarla/Downloads/[HorribleSubs] Eizouken ni wa Te wo Dasu na! - 01 [480p].mkv"
    output_file = "/Users/thomasfarla/Documents/test-subs"


state = State()


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self._model = ViewModel(self, state)

    def run(self):
        super().__init__()
        self.setWindowTitle("subs2srs")
        self.setObjectName("App.Main")
        self.setCentralWidget(MainWidget())
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    subs2srs = App()
    subs2srs.run()
    sys.exit(app.exec_())
