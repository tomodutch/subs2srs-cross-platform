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
            for line in self._native_sub.lines():
                if line.start >= target.start and line.start <= target.end:
                    return line

        for line in self._target_sub.lines():
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

    def run(self, output_dir, start=0, end=None, exclude=None):
        if exclude is None:
            exclude = set()

        outputs = []
        picture_outputs = []
        csv_path = os.path.join(output_dir, "output.csv")
        with open(csv_path, 'w+', encoding='utf-8') as f:
            writer = csv.writer(f)
            for i, line in enumerate(self._target_sub.lines()):
                if not i in exclude:
                    if i >= start and (end is None or i < end):
                        loc = os.path.join(output_dir, str(i) + ".mp3")
                        marker = self.sequence_marker(
                            episode=1, sequence=i + 1, start=line.start)
                        audio = self._input.audio.filter(
                            'atrim', start=line.start / 1000, end=line.end / 1000)
                        out = ffmpeg.output(audio, loc).overwrite_output()
                        outputs.append(out)
                        timestamp = line.start
                        writer.writerow([
                            marker,
                            line.text
                        ])

                        loc_pic = os.path.join(output_dir, str(i) + ".jpg")
                        picture_output = ffmpeg.input(self._media_file, ss=line.start / 1000).output(
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
