from subprocess import (run, PIPE, DEVNULL)
from pathlib import Path
from shutil import rmtree
from librosa.core.audio import get_duration
from math import ceil
from os.path import getsize
from json import loads
from __validate__ import (KindlyGetDictKey, is_audio_file)


RED = '\033[41m'
NORMAL = '\033[m'


def file_size(file):
    i_file = Path(file)

    try:
        return getsize(i_file)

    except FileNotFoundError:
        return {'sucess': False,
                'message': f'File {i_file} not found'}


def make_directory(path):
    Path(path).mkdir(parents = True, exist_ok = True)


def delete_directory(path):
    rmtree(Path(path), ignore_errors = True)


def delete_file(path):
    Path(path).unlink(missing_ok = True)


def check_ffmpeg():
    command = run(args = 'ffmpeg -version', stdout = DEVNULL, stderr = DEVNULL, shell = True)
    return_code = command.returncode

    if return_code == 1:
        print(f'{RED}FFmpeg ERROR: Check if FFmpeg is installed or if are added to PATH{NORMAL}')
        return False

    return True


def check_ffprobe():
    command = run(args = 'ffprobe -version', stdout = DEVNULL, stderr = DEVNULL, shell = True)
    return_code = command.returncode

    if return_code == 1:
        print(f'{RED}FFprobe ERROR: Check if FFprobe is installed or if are added to PATH{NORMAL}')
        return False

    return True


class AudioTools():

    def __init__(self):
        self.original_audio_duration = 0
        self.original_file_name = ''
        self.original_file_suffix = ''
        self.filled_file_name = ''
        self.filled_file_suffix = ''

    def generate_txt(self, file):
        i_file = Path(file).as_posix()

        try:
            self.original_audio_duration = get_duration(filename = i_file)
            self.original_file_name = Path(i_file).stem
            self.original_file_suffix = Path(i_file).suffix
            # EBU R128 recommends that audio files be at least 3 seconds duration.
            self.times_to_duplicate = ceil(3 / self.original_audio_duration)
            self.new_duration = self.original_audio_duration * self.times_to_duplicate

            for _ in range(self.times_to_duplicate):
                with open(f'files.txt', 'a') as f:
                    f.write(f'file {i_file}\n')

            return {'sucess': True,
                    'message': 'files.txt created'}

        except FileNotFoundError:
            return {'sucess': False,
                    'message': f'File {i_file} not found'}


    def fill_audio_length(self, file):
        i_file = Path(file)
        result = self.generate_txt(i_file)
        self.filled_file_name = f'{self.original_file_name}_filled'
        self.filled_file_suffix = self.original_file_suffix

        if result['sucess']:
            make_directory('misc/filled')

            # TO-DO: try save files.txt at misc/temp
            ffmpeg_command = f'''ffmpeg                         \
                                    -loglevel quiet             \
                                    -f concat                   \
                                    -safe 0                     \
                                    -i "files.txt"              \
                                    -y "misc/filled/{self.filled_file_name}{self.filled_file_suffix}" \
                                '''
            ffmpeg_output = run(args = ffmpeg_command, stdout = PIPE)

            delete_file('files.txt')

            return {'sucess': True,
                    'message': 'File filled up to 3 seconds and saved at \'misc/filled\'',
                    'file': f'{self.original_file_name}_filled{self.original_file_suffix}',
                    'original_duration': self.original_audio_duration,
                    'new_duration': self.new_duration}

        return {'sucess': False,
                'message': f'File {i_file} not found'}


    def back_normal_length(self, filled_file, original_audio_duration, output_filename):
        make_directory('misc/normalized')

        file_name = f'{Path(output_filename).stem}{Path(output_filename).suffix}'

        ffmpeg_command = f'''ffmpeg\
                                -i "{filled_file}"\
                                -af atrim=0:{original_audio_duration}\
                                -y "misc/normalized/{file_name}"\
                            '''
        ffmpeg_output = run(args = ffmpeg_command, stderr = PIPE)


    def get_audio_infos(self, file):
        i_file = Path(file)
        graceffuly = KindlyGetDictKey()

        if not is_audio_file(i_file)['is_audio_file']:
            return {'sucess': False,
                    'message': f'{i_file} is a invalid audio file'}

        ffprobe_command = f'''ffprobe                       \
                                    -loglevel quiet         \
                                    -i "{i_file}"           \
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
