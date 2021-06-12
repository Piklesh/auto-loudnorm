from subprocess import (run, PIPE)
from pathlib import Path
from shutil import rmtree
from librosa.core.audio import get_duration
from math import ceil, floor
from os.path import getsize
from json import loads

from __validate__ import (KindlyGetDictKey, is_audio_file)


def file_size(file):
    _file_ = Path(file)

    try:
        return getsize(_file_)

    except FileNotFoundError:
        return {'sucess': False,
                'message': 'File not found',
                'file': _file_}


def make_directory(path):
    Path(path).mkdir(parents = True, exist_ok = True)


def delete_directory(path):
    rmtree(Path(path), ignore_errors = True)


def delete_file(path):
    Path(path).unlink(missing_ok = True)


class AudioTools():

    def __init__(self):
        self.original_audio_duration = 0
        self.original_file_name = ''
        self.original_file_suffix = ''
        self.filled_file_name = ''
        self.filled_file_suffix = ''

    def generate_txt(self, file):
        _file_ = Path(file)

        try:
            self.original_audio_duration = get_duration(filename = _file_)
            self.original_file_name = Path(_file_).stem
            self.original_file_suffix = Path(_file_).suffix
            # EBU R128 recommends that audio files be at least 3 seconds duration.
            self.times_to_duplicate = ceil(3 / self.original_audio_duration)
            self.new_duration = self.original_audio_duration * self.times_to_duplicate

            for _ in range(self.times_to_duplicate):
                with open(f'files.txt', 'a') as f:
                    f.write(f'file {_file_}\n')

            return {'sucess': True,
                    'message': 'files.txt created'}

        except FileNotFoundError:
            return {'sucess': False,
                    'message': 'File not found',
                    'file': _file_}


    def fill_audio_length(self, file):
        _file_ = Path(file)
        result = self.generate_txt(_file_)
        self.filled_file_name = f'{self.original_file_name}_filled'
        self.filled_file_suffix = self.original_file_suffix

        if result['sucess']:
            delete_directory('misc/temp')
            make_directory('misc/temp')

            # TO-DO: try save files.txt at misc/temp
            ffmpeg_command = f'''ffmpeg                         \
                                    -loglevel quiet             \
                                    -f concat                   \
                                    -safe 0                     \
                                    -i "files.txt"              \
                                    -y "misc/temp/{self.filled_file_name}{self.filled_file_suffix}" \
                                '''
            ffmpeg_output = run(args = ffmpeg_command, stdout = PIPE)

            delete_file('files.txt')

            return {'sucess': True,
                    'message': 'File filled up to 3 seconds and saved at \'misc/temp\'',
                    'file': f'{self.original_file_name}_filled{self.original_file_suffix}',
                    'original_duration': self.original_audio_duration,
                    'new_duration': self.new_duration}

        return {'sucess': False,
                'message': 'File not found',
                'file': _file_}


    def back_normal_length(self, output_folder = 'misc/temp'):
        filled_file = f'{self.filled_file_name}{self.filled_file_suffix}'

        ffmpeg_command = f'''ffmpeg                                          \
                                -i "{output_folder}/{filled_file}"           \
                                -af atrim=0:{self.original_audio_duration}   \
                                -y "misc/temp/{self.original_file_name}{self.original_file_suffix}" \
                            '''
        ffmpeg_output = run(args = ffmpeg_command, stdout = PIPE)


    def get_audio_infos(self, file):
        _file_ = Path(file)
        graceffuly = KindlyGetDictKey()

        if not is_audio_file(_file_)['is_audio_file']:
            return {'sucess': False,
                    'message': 'Invalid audio file',
                    'file': _file_}

        ffprobe_command = f'''ffprobe                       \
                                    -loglevel quiet         \
                                    -i "{_file_}"           \
                                    -select_streams a       \
                                    -show_entries stream=codec_type,codec_name,channels,sample_rate,bit_rate,sample_fmt:format=bit_rate\
                                    -print_format json      \
                            '''

        ffprobe_output = run(args = ffprobe_command, stdout = PIPE)
        ffprobe_output = ffprobe_output.stdout
        ffprobe_output = ffprobe_output.decode(encoding = 'utf-8')
        ffprobe_output = loads(ffprobe_output)

        streams_entries = graceffuly.format('{streams[0]}', **ffprobe_output)
        streams_entries = streams_entries.replace("\'", "\"")
        streams_entries = loads(streams_entries)
        format_entries = graceffuly.format('{format}', **ffprobe_output)
        format_entries = format_entries.replace("\'", "\"")
        format_entries = loads(format_entries)

        streams_bitrate = graceffuly.format('{bit_rate}', **streams_entries)
        format_bitrate = graceffuly.format('{bit_rate}', **format_entries)

        if streams_bitrate == '?':
            streams_entries['bit_rate'] = int(round(int(format_bitrate) / 1000, 0))
        else:
            streams_entries['bit_rate'] = int(round(int(streams_entries['bit_rate']) / 1000, 0))

        return streams_entries
