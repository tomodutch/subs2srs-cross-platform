import simpleaudio as sa
import wave
from io import BytesIO


class Audio():
    def __init__(self, audio_bytes):
        wave_read = wave.open(BytesIO(audio_bytes))
        audio_data = wave_read.readframes(wave_read.getnframes())
        num_channels = wave_read.getnchannels()
        bytes_per_sample = wave_read.getsampwidth()
        sample_rate = wave_read.getframerate()

        self._wave_obj = sa.WaveObject(
            audio_data, num_channels, bytes_per_sample, sample_rate)

    def play(self):
        self._play_obj = self._wave_obj.play()

    def stop(self):
        if self._play_obj:
            self._play_obj.stop()
