from pathlib import Path
import subprocess
import json
import string


class GraceffulyGetDictKey(string.Formatter):
    def __init__(self, missing = ''):
        self.missing = missing

    def get_field(self, field_name, args, kwargs):
        try:
            val = super().get_field(field_name, args, kwargs)
        except (KeyError, AttributeError, IndexError):
            val = None, self.missing
        return val


def is_audio_file(file):
    """
    Return: `dict`

    {'file': 'misc/audio_file_1.txt', 'is_audio_file': False}

    """

    data = dict()
    graceffuly = GraceffulyGetDictKey()

    ffprobe_command = f"""ffprobe -hide_banner -i {file} -loglevel quiet -select_streams a -show_entries stream=codec_type -print_format json"""
    output = subprocess.run(ffprobe_command, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, universal_newlines = True)
    output = json.loads(output.stdout)
    graceffuly_output = graceffuly.format('{streams[0][codec_type]}', **output)

    if graceffuly_output == 'None':
        data['file'] = file
        data['is_audio_file'] = False
        return data

    data['file'] = file
    data['is_audio_file'] = True

    return data


# Usage
for file in Path('misc').glob('*'):
    print(is_audio_file(file))
