from subprocess import (run, PIPE)
from pathlib import Path
from shutil import rmtree
from librosa.core.audio import get_duration
from math import ceil
from os.path import getsize
from textwrap import dedent


def file_size(file):
    try:
        return getsize(file)

    except FileNotFoundError:
        return {'file': file, 'error': 'File not found.', 'sucess': False}


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
            times_to_duplicate = ceil(3 / self.original_audio_duration)

            for _ in range(times_to_duplicate):
                with open(f'files.txt', 'a') as f:
                    f.write(f'file {file}\n')

            return {'sucess': True, 'message': 'files.txt created.'}

        except FileNotFoundError:
            return {'sucess': False, 'error': 'File not found.', 'file': file}


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

            return f'\'{file}\' filled up to 3 seconds and saved at \'misc/temp/{self.original_file_name}_filled{self.original_file_suffix}\''

        return {'sucess': False, 'error': 'File not found.', 'file': file}


    def back_normal_length(self, output_folder = 'misc/temp'):
        filled_file = f'{self.filled_file_name}{self.filled_file_suffix}'

        ffmpeg_command = f'''ffmpeg -i "{output_folder}/{filled_file}" -af atrim=0:{self.original_audio_duration} -y "misc/temp/{self.original_file_name}{self.original_file_suffix}"'''
        ffmpeg_output = run(args = ffmpeg_command, stdout = PIPE)
