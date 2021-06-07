from pathlib import Path
from shutil import rmtree
from librosa.core.audio import get_duration
from math import ceil
from os.path import getsize
from subprocess import (check_output, STDOUT)


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


def generate_txt(file):
    try:
        path = Path.cwd()

        audio_duration = get_duration(filename = file)
        # EBU R128 recommends that audio files be at least 3 seconds duration.
        n_to_duplicate = ceil(3 / audio_duration)

        for _ in range(n_to_duplicate):
            with open(f'files.txt', 'a') as f:
                f.write(f'file {file}\n')

    except FileNotFoundError:
        return {'file': file, 'error': 'File not found.', 'sucess': False}


def fill_audio_length(file):
    generate_txt(file)
    delete_directory('misc/temp')
    make_directory('misc/temp')

    ffmpeg_command = f'''ffmpeg -f concat -safe 0 -i "files.txt" -c copy -y "misc/temp/file_name_filled.ogg"'''
    ffmpeg_output = check_output(ffmpeg_command, stderr = STDOUT).decode('utf-8')

    delete_file('files.txt')
    #print(f'File {file} filled up to 5 seconds and saved at \'misc/temp/{file}_filled.wav\'')
    #print(0)
    #return 0


def back_normal_length(file):
    ...
