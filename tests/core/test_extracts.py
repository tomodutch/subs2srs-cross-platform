from subs2srs.core.extractor import SubtitleSetting, Extractor
from subs2srs.core.subtitle import Subtitle
import os

curdir = os.path.dirname(os.path.abspath(__file__))
fixtures = os.path.join(curdir, '..', 'fixtures')


def test_run():
    media_file = os.path.join(fixtures, "in.mkv")
    sub_file = os.path.join(fixtures, "in.srt")
    sub = Subtitle(sub_file)
    target_sub = SubtitleSetting()
    extractor = Extractor(
        media_file=media_file,
        target_sub=sub)

    extractor.run()

def test_preview():
    media_file = os.path.join(fixtures, "in.mkv")
    sub_file = os.path.join(fixtures, "in.srt")
    sub = Subtitle(sub_file)
    target_sub = SubtitleSetting()
    extractor = Extractor(
        media_file=media_file,
        target_sub=sub)

    extractor.preview()
