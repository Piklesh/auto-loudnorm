from subprocess import (run, PIPE)
from pathlib import Path
from shutil import rmtree
from librosa.core.audio import get_duration
from math import ceil
from os.path import getsize
from json import loads
from __validate__ import is_audio_file


def file_size(file):
    try:
        return getsize(file)

    except FileNotFoundError:
        return {'sucess': False,
                'message': 'File not found.',
                'file': file}


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
        try:
            self.original_audio_duration = get_duration(filename = file)
            self.original_file_name = Path(file).stem
            self.original_file_suffix = Path(file).suffix
            # EBU R128 recommends that audio files be at least 3 seconds duration.
            self.times_to_duplicate = ceil(3 / self.original_audio_duration)
            self.new_duration = self.original_audio_duration * self.times_to_duplicate

            for _ in range(self.times_to_duplicate):
                with open(f'files.txt', 'a') as f:
                    f.write(f'file {file}\n')

            return {'sucess': True,
                    'message': 'files.txt created.'}

        except FileNotFoundError:
            return {'sucess': False,
                    'message': 'File not found.',
                    'file': file}


    def fill_audio_length(self, file):
        result = self.generate_txt(file)
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
                'message': 'File not found.',
                'file': file}


    def back_normal_length(self, output_folder = 'misc/temp'):
        filled_file = f'{self.filled_file_name}{self.filled_file_suffix}'

        ffmpeg_command = f'''ffmpeg                                          \
                                -i "{output_folder}/{filled_file}"           \
                                -af atrim=0:{self.original_audio_duration}   \
                                -y "misc/temp/{self.original_file_name}{self.original_file_suffix}" \
                            '''
        ffmpeg_output = run(args = ffmpeg_command, stdout = PIPE)


    def get_audio_infos(self, file):

        if not is_audio_file(file)['is_audio_file']:
            return {'sucess': False,
                    'message': 'Invalid audio file.',
                    'file': file}

        ffprobe_command = f'''ffprobe                       \
                                    -loglevel quiet         \
                                    -i {file}               \
                                    -select_streams a       \
                                    -show_entries stream=codec_type,codec_name,channels,sample_rate,bit_rate,sample_fmt:format=bit_rate\
                                    -print_format json      \
                            '''
        ffprobe_output = run(args = ffprobe_command, stdout = PIPE)
        ffprobe_output = loads(ffprobe_output.stdout)

        #ffprobe_output['streams'][0]['bit_rate']
        #ffprobe_output['format']['bit_rate']

        return loads(ffprobe_output.stdout)
