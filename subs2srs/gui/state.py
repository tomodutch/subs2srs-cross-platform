from typing import List
from subs2srs.core.preview_item import PreviewItem


class StatePreview:
    items: List[PreviewItem] = []
    inactive_items = set()

    def __init__(self):
        super().__init__()
        self.items = []
        self.inactive_items = set()
        self.audio = None


class State:
    deck_name = None
    sub1_file = "/Users/thomasfarla/Documents/subs2srs-cross-platform/tests/fixtures/in2.srt"
    sub2_file = "/Users/thomasfarla/Documents/subs2srs-cross-platform/tests/fixtures/in2-en.srt"
    video_file = "/Users/thomasfarla/Documents/subs2srs-cross-platform/tests/fixtures/in2.mkv"
    output_file = "/Users/thomasfarla/Documents/test-subs"
    preview = StatePreview()
