import hashlib
import ffmpeg
from .subtitle import Subtitle
from .preview_item import PreviewItem
import os
import csv
from datetime import timedelta
from typing import Union


class SubtitleSetting:
    pass


class Extractor:
    def __init__(self, media_file, target_sub, native_sub=None):
        super().__init__()
        self._media_file = media_file
        self._target_sub: Subtitle = target_sub
        self._native_sub: Union[None, Subtitle] = native_sub
        self._input = ffmpeg.input(self._media_file)

    def preview(self):
        def get_native(target):
            marge = 200
            lines = []
            if self._native_sub:
                lines = self._native_sub.lines()

            total = len(lines)
            i = 0
            while i < total:
                line = lines[i]
                next_line = None
                try:
                    next_line = lines[i + 1]
                except IndexError:
                    pass

                if line.start >= target.start - marge:
                    if line.start <= target.end + marge:
                        return line

                    if next_line and target.end < next_line.start:
                        return line

                i = i + 1

        chars = set(["→"])
        lines = self._target_sub.lines()
        i = 0
        while i < len(lines):
            line = lines[i]
            native_line = get_native(line)
            native_sub = ""
            if native_line:
                native_sub = native_line.text

            preview = PreviewItem(
                from_time=line.start,
                end_time=line.end,
                target_sub=line.text,
                native_sub=native_sub
            )

            l = line
            try:
                while l.text.endswith('→'):
                    # concat and skip next line
                    next_item = lines[i + 1]
                    l = next_item
                    i = i + 1
                    preview.end_time = next_item.end
                    preview.target_sub += next_item.text
                    native_line = get_native(next_item)
                    if native_line:
                        preview.native_sub += native_line.text
            except IndexError:
                pass
            finally:
                preview.target_sub = preview.target_sub.replace(
                    "→", "").replace("\\N", "")

            i = i + 1
            yield preview

    def sequence_marker(self, episode, sequence, start):
        marker = (start / 1000000)
        hour, pieces = str(marker).split('.')

        def format(td):
            hours, remainder = divmod(td.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            seconds += td.microseconds / 1e6

            return "{}.{}.{}".format(hours, f'{minutes:02}', f'{seconds:.3f}').strip('.')

        formatted = format(timedelta(milliseconds=start))

        return "{}_{}_{}".format(episode, f'{sequence:03}', formatted)

    def run(self, output_dir, tags=[], start=0, end=None, exclude=None):
        if exclude is None:
            exclude = set()
        
        if tags is None:
            tags = []

        outputs = []
        picture_outputs = []
        csv_path = os.path.join(output_dir, "output.csv")
        with open(csv_path, 'w+', encoding='utf-8') as f:
            writer = csv.writer(f)
            for i, line in enumerate(self.preview()):
                line: PreviewItem
                start = line.from_time
                end = line.end_time
                if not i in exclude:
                    name = generate_name(line.target_sub)
                    audio_name = name + ".mp3"
                    media_name = name + ".jpg"
                    collection_dir = os.path.join(
                        output_dir, "collection.media")
                    if not os.path.exists(collection_dir):
                        os.mkdir(collection_dir)

                    loc = os.path.join(collection_dir, name + ".mp3")
                    marker = self.sequence_marker(
                        episode=1, sequence=i + 1, start=start)
                    audio = self._input.audio.filter(
                        'atrim', start=start / 1000, end=end / 1000)
                    out = ffmpeg.output(audio, loc).overwrite_output()
                    outputs.append(out)
                    timestamp = start
                    writer.writerow([
                        marker,
                        '[sound:{}]'.format(audio_name),
                        '<img src="{}">'.format(media_name),
                        line.target_sub,
                        line.native_sub,
                        "tags:" + " ".join(tags)
                    ])

                    loc_pic = os.path.join(collection_dir, media_name)
                    picture_output = ffmpeg.input(self._media_file, ss=start / 1000).output(
                        loc_pic, vframes=1, format='image2', vcodec='mjpeg').overwrite_output()
                    picture_outputs.append(picture_output)

        total = len(outputs) + len(picture_outputs)
        total_audio = len(outputs)
        for i, o in enumerate(outputs):
            o.run()
            yield ("audio", i + 1, total)

        for i, o in enumerate(picture_outputs):
            o.run()
            yield ("picture", total_audio + i + 1, total)

    def get_snapshot(self, time):
        loc_pic = ""
        picture_output = ffmpeg.input(self._media_file, ss=time).output(
            'pipe:', vframes=1, format='image2', vcodec='mjpeg')

        return picture_output.run(capture_stdout=True)[0]

    def get_audio(self, start_second, end_second):
        out = self._input.audio.filter(
            'atrim', start=start_second, end=end_second) \
            .output('-', format='wav').overwrite_output()

        return out.run(capture_stdout=True)[0]


def generate_name(text: str):
    return hashlib.sha1(text.encode('utf-8')).hexdigest()
