from pathlib import Path
from subprocess import check_output, STDOUT
from __validate__ import is_audio_file, GraceffulyGetDictKey
from json import loads
from re import search
import librosa


REGEX_EXPRESSION = r'\{(\r.*|\n.*)+[}$]'
gracefully = GraceffulyGetDictKey()


ffmpeg_command = '''ffmpeg -hide_banner -i misc/audio_file_2.wav -af loudnorm=I=-16:dual_mono=true:TP=-1.5:LRA=11:print_format=json -f null -'''
output = check_output(ffmpeg_command, stderr = STDOUT).decode('utf-8')


match = search(pattern = REGEX_EXPRESSION, string = output).group(0)
json_output = loads(match)

print(gracefully.format('{input_i}', **json_output))
