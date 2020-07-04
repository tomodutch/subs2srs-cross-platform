from PyQt5 import QtCore
import functools


class Event:
    def __init__(self, value):
        super().__init__()
        self.value = value


class FileChangeEvent(Event):
    pass


@functools.lru_cache()
class GlobalObject(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self._events = {}

    def addEventListener(self, name, func):
        if name not in self._events:
            self._events[name] = [func]
        else:
            self._events[name].append(func)

    def dispatchEvent(self, name, event=None):
        functions = self._events.get(name, [])
        for func in functions:
            def f():
                func(event)
            QtCore.QTimer.singleShot(0, f)
