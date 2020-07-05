from subs2srs.gui.globalobject import GlobalObject
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from subs2srs.core.extractor import Extractor
from subs2srs.core.subtitle import Subtitle
from subs2srs.gui.process_runnable import ProcessRunnable
from subs2srs.gui.main_widget import MainWidget
from subs2srs.gui.state import State
from typing import List
from .preview_model import PreviewModel


class RootModel:
    def __init__(self, app: QMainWindow, state: State):
        super().__init__()

        self._app = app
        self._state = state

        PreviewModel(app, state)

        GlobalObject().addEventListener("changeDeckName", self.setDeckName)
        GlobalObject().addEventListener("changeSub1", self.changeSub1)
        GlobalObject().addEventListener("changeSub2", self.changeSub2)
        GlobalObject().addEventListener("changeVideo", self.changeVideo)
        GlobalObject().addEventListener("changeOutput", self.changeOutput)
        GlobalObject().addEventListener("generate", self.generate)

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
            exclude = set()
            if self._state.preview:
                exclude = self._state.preview.inactive_items

            for type, i, total in extractor.run(output, exclude=exclude):
                val = int(i / total * 100)
                QMetaObject.invokeMethod(self._app,
                                         "updateProgress", Qt.QueuedConnection,
                                         Q_ARG(str, type),
                                         Q_ARG(int, val),
                                         Q_ARG(int, i),
                                         Q_ARG(int, total))

        process = ProcessRunnable(target=run, args=())
        process.start()
