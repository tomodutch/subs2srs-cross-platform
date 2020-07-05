from subs2srs.gui.globalobject import GlobalObject
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

info_color = "#3DDC97"
error_color = "#FF495C"


def dispatch(event):
    def do():
        GlobalObject().dispatchEvent(event)

    return do


def info_button(label, name, clickEventName):
    btn = button(label, name, clickEventName)
    btn.setStyleSheet("color: {}".format(info_color))

    return btn


def error_button(label, name, clickEventName):
    btn = button(label, name, clickEventName)
    btn.setStyleSheet("color: {}".format(error_color))

    return btn


def button(label, name, clickEventName):
    btn = QPushButton(label)
    btn.clicked.connect(dispatch(clickEventName))

    return btn


def label(text, name):
    item = QLabel(text)
    item.setObjectName(name)

    return item


def info_label(text, name):
    item = label(text, name)
    item.setStyleSheet("color: {}".format(info_color))

    return item


def error_label(text, name):
    item = label(text, name)
    item.setStyleSheet("color: {}".format(error_color))

    return item


def text(name, event):
    item = QLineEdit()
    item.setObjectName(name)
    item.textChanged.connect(dispatch(event))
    return item


def image(source, name):
    l = label("image", "test")
    item = QPixmap(source)
    size = 512
    item = item.scaled(size, size, Qt.KeepAspectRatio)
    l.setPixmap(item)
    l.setObjectName(name)
    l.setScaledContents(True)
    l.setMaximumWidth((2 * size) / 3)
    l.setMaximumHeight((2 * size) / 4)

    return l


def textarea(name, change_event=None, text=None):
    if change_event is None:
        change_event = "change" + name

    item = QTextEdit()
    item.setObjectName(name)
    item.textChanged.connect(dispatch(change_event))
    if not text is None:
        item.setText(text)

    return item
