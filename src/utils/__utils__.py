from subprocess import (run, PIPE)
from pathlib import Path
from shutil import rmtree
from librosa.core.audio import get_duration
from math import ceil
from os.path import getsize


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
        audio_duration = get_duration(filename = file)
        # EBU R128 recommends that audio files be at least 3 seconds duration.
        n_to_duplicate = ceil(3 / audio_duration)

        for _ in range(n_to_duplicate):
            with open(f'files.txt', 'a') as f:
                f.write(f'file {file}\n')

        return {'sucess': True, 'message': 'files.txt created.'}

    except FileNotFoundError:
        return {'sucess': False, 'error': 'File not found.', 'file': file}


def fill_audio_length(file):
    result = generate_txt(file)

    if result['sucess']:
        file_name = Path(file).stem
        file_suffix = Path(file).suffix

        delete_directory('misc/temp')
        make_directory('misc/temp')

        ffmpeg_command = f'''ffmpeg -loglevel quiet -f concat -safe 0 -i "files.txt" -c copy -y "misc/temp/{file_name}_filled{file_suffix}"'''
        ffmpeg_output = run(args = ffmpeg_command, stdout = PIPE)

        delete_file('files.txt')

        return f'\'{file}\' filled up to 3 seconds and saved at \'misc/temp/{file_name}_filled{file_suffix}\''

    return {'sucess': False, 'error': 'File not found.', 'file': file}


def back_normal_length(file):
    ...
