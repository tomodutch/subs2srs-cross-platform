class PreviewItem:
    def __init__(self, from_time, end_time, target_sub, native_sub):
        super().__init__()
        self._from_time = from_time
        self._end_time = end_time
        self.target_sub = target_sub
        self.native_sub = native_sub