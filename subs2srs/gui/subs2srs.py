import sys
import qdarkstyle
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from subs2srs.gui.globalobject import FileChangeEvent, GlobalObject
from subs2srs.core.extractor import Extractor
from subs2srs.core.subtitle import Subtitle


class ProcessRunnable(QRunnable):
    def __init__(self, target, args):
        QRunnable.__init__(self)
        self.t = target
        self.args = args

    def run(self):
        self.t(*self.args)

    def start(self):
        QThreadPool.globalInstance().start(self)


class State:
    deck_name = None
    sub1_file = "/Users/thomasfarla/Downloads/Eizouken ni wa Te wo Dasu na! - 01 (NHKG).srt"
    sub2_file = None
    video_file = "/Users/thomasfarla/Downloads/[HorribleSubs] Eizouken ni wa Te wo Dasu na! - 01 [480p].mkv"
    output_file = "/Users/thomasfarla/Documents/test-subs"


state = State()


class App(QMainWindow):
    @pyqtSlot()
    def setDeckName(self, event):
        child = self.findChild(QObject, "Deck.Name")
        state.deck_name = child.text()

    @pyqtSlot()
    def changeSub2(self, event):
        if event is None:
            return

        state.sub1_file = event.value
        input = self.findChild(QObject, "sub2Input")
        input.setText(event.value)

    @pyqtSlot()
    def changeSub1(self, event):
        if event is None:
            return

        state.sub1_file = event.value
        input = self.findChild(QObject, "sub1Input")
        input.setText(event.value)

    @pyqtSlot()
    def changeVideo(self, event):
        if event is None:
            return

        state.video_file = event.value
        input = self.findChild(QObject, "Video.Input")
        input.setText(event.value)

    @pyqtSlot()
    def changeOutput(self, event):
        if event is None:
            return

        state.output_file = event.value
        input = self.findChild(QObject, "Output.Input")
        input.setText(event.value)

    @pyqtSlot(str, int, int, int)
    def updateProgress(self, type, value, i, total):
        self.progress.setValue(value)
        if type == "audio":
            self.progress.setLabelText(
                "Audio (" + str(i) + "/ " + str(total) + ")")
        elif type == "picture":
            self.progress.setLabelText(
                "Picture (" + str(i) + "/ " + str(total) + ")")

    def generate(self, event):
        media_file = state.video_file
        target_sub = state.sub1_file
        output = state.output_file

        p = QProgressDialog("Creating audio files", "Cancel", 0, 100, self)

        p.setWindowModality(Qt.WindowModal)
        p.setObjectName("Progress.Dialog")
        p.setCancelButton(None)
        self.progress = p
        p.setAutoClose(True)
        p.show()

        def run():
            extractor = Extractor(media_file, Subtitle(target_sub))
            for type, i, total in extractor.run(output):
                val = int(i / total * 100)
                QMetaObject.invokeMethod(self,
                                         "updateProgress", Qt.QueuedConnection,
                                         Q_ARG(str, type),
                                         Q_ARG(int, val),
                                         Q_ARG(int, i),
                                         Q_ARG(int, total))

        process = ProcessRunnable(target=run, args=())
        process.start()

    def __init__(self):
        super().__init__()

        GlobalObject().addEventListener("changeDeckName", self.setDeckName)
        GlobalObject().addEventListener("changeSub1", self.changeSub1)
        GlobalObject().addEventListener("changeSub2", self.changeSub2)
        GlobalObject().addEventListener("changeVideo", self.changeVideo)
        GlobalObject().addEventListener("changeOutput", self.changeOutput)
        GlobalObject().addEventListener("generate", self.generate)

    def run(self):
        super().__init__()
        self.setWindowTitle("subs2srs")
        layout = QVBoxLayout()

        layout.addWidget(SubtitlePaneGrid())
        layout.addWidget(SubtitleOptions())
        layout.addWidget(SaveRow())

        layout.setContentsMargins(0, 0, 0, 0)
        GlobalObject()
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        layout.setAlignment(Qt.AlignTop)

        field = self.findChild(QObject, "Deck.Name")
        self.show()


class TimingGroup(QGroupBox):
    def __init__(self, str, parent=None):
        super().__init__(str, parent=parent)
        layout = QVBoxLayout()
        self.setLayout(layout)

        radio_1 = QRadioButton("Sub1")
        radio_2 = QRadioButton("Sub2")

        radio_1.setChecked(True)

        layout.addWidget(radio_1)
        layout.addWidget(radio_2)


class SpanGroup(QGroupBox):
    def __init__(self, str, parent=None):
        super().__init__(str, parent=parent)
        layout = QFormLayout()
        self.setCheckable(True)
        self.setChecked(False)

        label = QLabel("Start")
        field = QTimeEdit()
        layout.addRow(label, field)

        label = QLabel("End")
        field = QTimeEdit()
        layout.addRow(label, field)

        self.setLayout(layout)


class TimeShiftGroup(QGroupBox):
    def __init__(self, str, parent=None):
        super().__init__(str, parent=parent)
        self.setCheckable(True)
        self.setChecked(False)

        layout = QFormLayout()
        layout.addRow(QLabel("Subs1"), QSpinBox())
        layout.addRow(QLabel("Subs2"), QSpinBox())

        self.setLayout(layout)


class SubtitleOptions(QWidget):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        layout = QHBoxLayout()
        group = QGroupBox("Subtitle Options")

        group_layout = QHBoxLayout()

        timing_group = TimingGroup("Use Timings From")
        group_layout.addWidget(timing_group)

        span_group = SpanGroup("Span")
        group_layout.addWidget(span_group)

        time_shift_group = TimeShiftGroup("Time Shift (ms)")
        group_layout.addWidget(time_shift_group)

        group.setLayout(group_layout)

        layout.addWidget(group)
        self.setLayout(layout)


class SaveRow(QWidget):
    @pyqtSlot()
    def changeDeckName(self):
        GlobalObject().dispatchEvent("changeDeckName")

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setMaximumHeight(150)
        self.setContentsMargins(0, 0, 0, 0)
        layout = QGridLayout()
        group = QGroupBox("Naming")
        group_layout = QGridLayout()
        group.setLayout(group_layout)

        label = QLabel("Name of deck")
        group_layout.addWidget(label, 0, 0, 1, 1)
        field = QLineEdit()

        field.textChanged.connect(self.changeDeckName)
        field.setObjectName("Deck.Name")
        # field.connectNotify()
        group_layout.addWidget(field, 1, 0, 1, 1)

        layout.addWidget(group, 0, 0, 6, 1)

        preview_button = QPushButton("Preview")

        def go():
            GlobalObject().dispatchEvent("generate")

        go_button = QPushButton("Go")
        go_button.clicked.connect(go)
        button_group = QWidget()
        button_group_layout = QVBoxLayout()
        button_group.setLayout(button_group_layout)

        button_group_layout.addWidget(preview_button)
        button_group_layout.addWidget(go_button)

        layout.addWidget(button_group, 0, 6, 1, 2)

        self.setLayout(layout)


class SubtitlePaneGrid(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = QHBoxLayout()
        group = QGroupBox("Files")
        group_layout = QGridLayout()

        sub1_row = SubtitleInputRow(title="Sub 1", y=0)
        sub1_row.render(group_layout)

        sub2_row = SubtitleInputRow(title="Sub 2", y=1)
        sub2_row.render(group_layout)

        video_row = VideoInputRow(y=2)
        video_row.render(group_layout)

        output_row = OutputRow(y=3)
        output_row.render(group_layout)

        group.setLayout(group_layout)
        layout.addWidget(group)

        self.setLayout(layout)


class VideoInputRow:
    def __init__(self, y):
        super().__init__()
        self._y = y
        self.button = QPushButton("Video")
        self.input = QLineEdit()
        self.input.setObjectName("Video.Input")
        self.combo = QComboBox()

        def click():
            self.openFileNameDialog()

        self.button.clicked.connect(click)

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(
            caption="Choose Video", directory="", filter="All Files (*)", options=options)
        if fileName:
            GlobalObject().dispatchEvent("changeVideo", FileChangeEvent(fileName))

    def render(self, layout: QLayout):
        y = self._y
        layout.addWidget(self.button, y, 0, 1, 1)
        layout.addWidget(self.input, y, 1, 1, 5)
        layout.addWidget(self.combo, y, 6, 1, 1)


class SubtitleInputRow:
    def __init__(self, y, title):
        super().__init__()
        self._y = y
        self.button = QPushButton(title)
        self.input = QLineEdit()
        self.input.setObjectName("sub" + str(y + 1) + "Input")
        self.combo = QComboBox()
        self.combo.addItem("Unicode (UTF-8)")

        def click():
            self.openFileNameDialog()

        self.button.clicked.connect(click)

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(
            caption="Choose subtitle", directory="", filter="All Files (*)", options=options)
        if fileName:
            GlobalObject().dispatchEvent("changeSub" + str(self._y + 1), FileChangeEvent(fileName))

    def render(self, layout: QLayout):
        y = self._y
        layout.addWidget(self.button, y, 0, 1, 1)
        layout.addWidget(self.input, y, 1, 1, 5)
        layout.addWidget(self.combo, y, 6, 1, 1)


class OutputRow():
    def __init__(self, y):
        super().__init__()
        self._y = y
        self.button = QPushButton("Output")
        self.input = QLineEdit()
        self.input.setObjectName("Output.Input")

        def click():
            self.openFileNameDialog()

        self.button.clicked.connect(click)

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        fileName = QFileDialog.getExistingDirectory(
            caption="Choose Output", directory="")
        if fileName:
            GlobalObject().dispatchEvent("changeOutput", FileChangeEvent(fileName))

    def render(self, layout: QLayout):
        y = self._y
        layout.addWidget(self.button, y, 0, 1, 1)
        layout.addWidget(self.input, y, 1, 1, 6)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    subs2srs = App()
    subs2srs.run()
    sys.exit(app.exec_())
