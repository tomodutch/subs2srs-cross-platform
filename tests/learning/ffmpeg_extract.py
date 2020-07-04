import ffmpeg

def extract():
    input = ffmpeg.input('tests/fixtures/in.mkv')
    # audio = input.audio.filter("aecho", 0.8, 0.9, 1000, 0.3)
    # working command
    # ffmpeg -i ./tests/fixtures/in.mkv -ss 00:03:05 -t 00:00:45.0 -q:a 0 -map a sample.mp3
    # audio = input.audio.filter('ss', '00:03:05').filter('t', '00:00:45.0').filter('q', 'a', '0').filter("acodec")
    # audio = input.audio.filter("aecho", 0.8, 0.9, 1000, 0.3)
    audio = input.audio.filter('atrim', start=10, end=60)
    audio2 = input.audio.filter('atrim', start=70, end=90)

    # video = input.video.hflip()
    # ffmpeg -i sample.avi -ss 00:03:05 -t 00:00:45.0 -q:a 0 -map a sample.mp3
    # with open('./out.mp3', 'w+') as f:
    out = ffmpeg.output(audio, 'out.mp3').overwrite_output()
    out2 = ffmpeg.output(audio2, 'out2.mp3').overwrite_output()
    # print(out.get_args())
    out.run()
    out2.run()

if __name__ == "__main__":
    extract()