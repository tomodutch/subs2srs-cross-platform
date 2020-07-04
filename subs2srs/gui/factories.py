from subs2srs.gui.globalobject import GlobalObject
from PyQt5.QtWidgets import QPushButton


def dispatch(event):
    def do():
        GlobalObject().dispatchEvent(event)

    return do


def button(label, name, clickEventName):
    btn = QPushButton(label)
    btn.clicked.connect(dispatch(clickEventName))
    return btn
