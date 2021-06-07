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
        return {'status_code': 0}


def make_directory(path):
    Path(path).mkdir(parents = True, exist_ok = True)


def delete_directory(path):
    rmtree(Path(path), ignore_errors = True)


def generate_txt(file):
    try:
        path = Path.cwd()

        audio_duration = get_duration(filename = file)
        # 5 its no a magic number. EBU R128 recommends that audio files be at least 3 seconds duration.
        # we use 5 for more precision.
        n_to_duplicate = ceil(5 / audio_duration)

        for _ in range(n_to_duplicate):
            with open(f'files.txt', 'a') as f:
                f.write(f'file {file}\n')

    except FileNotFoundError:
        return {'sucess': False}


def fill_audio_length(file):
    generate_txt(file)
    delete_directory('misc/temp')
    make_directory('misc/temp')

    ffmpeg_command = f'''ffmpeg -f concat -safe 0 -i "files.txt" -c copy -y "misc/temp/file_name_filled.ogg"'''
    ffmpeg_output = check_output(ffmpeg_command, stderr = STDOUT).decode('utf-8')

    # TO-DO: delete files.txt after fill
    #print(f'File {file} filled up to 5 seconds and saved at \'misc/temp/{file}_filled.wav\'')
    print(0)
    #return 0


def back_normal_length(file):
    ...


#fill_audio_length('misc/audio_file_6.ogg')
#generate_txt('misc/audio_file_6.ogg')
