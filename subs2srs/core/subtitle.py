import pysubs2
from typing import List


class Subtitle:
    def __init__(self, file):
        super().__init__()
        self._subs = pysubs2.load(file)

    def lines(self) -> List[pysubs2.SSAEvent]:
        return self._subs
