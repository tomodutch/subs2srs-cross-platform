from subs2srs.gui.globalobject import GlobalObject
from PyQt5.QtWidgets import *

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
