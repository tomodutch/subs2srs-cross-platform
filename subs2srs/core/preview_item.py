class PreviewItem:
    def __init__(self, from_time, end_time, target_sub, native_sub):
        super().__init__()
        self.from_time = from_time
        self.end_time = end_time
        self.target_sub = target_sub
        self.native_sub = native_sub

    def from_time_seconds(self):
        if self.from_time <= 0 or self.from_time is None:
            return -1

        return self.from_time / 1000
