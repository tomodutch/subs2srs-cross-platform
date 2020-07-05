import pysubs2
from typing import List


class Subtitle:
    def __init__(self, file):
        super().__init__()
        subs = pysubs2.SSAFile = pysubs2.load(file)
        self._subs = subs

    def lines(self) -> List[pysubs2.SSAEvent]:
        return self._subs
