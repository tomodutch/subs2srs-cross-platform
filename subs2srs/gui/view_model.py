from subs2srs.gui.globalobject import GlobalObject
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from subs2srs.core.extractor import Extractor
from subs2srs.core.subtitle import Subtitle
from .process_runnable import ProcessRunnable
from .preview import Preview
from subs2srs.gui.main_widget import MainWidget


class ViewModel:
    def __init__(self, app: QMainWindow, state):
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
        preview = Preview()
        self._app.setCentralWidget(preview)

    @pyqtSlot()
    def changeOutput(self, event):
        if event is None:
            return

        self._state.output_file = event.value
        input = self._app.findChild(QObject, "Output.Input")
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
        media_file = self._state.video_file
        target_sub = self._state.sub1_file
        output = self._state.output_file

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
