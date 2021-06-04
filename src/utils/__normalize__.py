from pathlib import Path
from subprocess import (check_output, run, STDOUT)
from __validate__ import is_audio_file
from json import loads
from re import search
from os.path import getsize
import librosa


REGEX_EXPRESSION = r'\{(\r.*|\n.*)+[}$]'


def first_pass(file, target_lufs):

    if is_audio_file(file)['is_audio_file']:
    # TO-DO: and has_lenght_gte_3s is True
    # TO-DO: if not has_lenght_gte_3s, fill with white noise
        ffmpeg_command = f'''ffmpeg -hide_banner -nostdin -i {file} -af loudnorm=I={target_lufs}:dual_mono=true:TP=-1.5:LRA=11:print_format=json -f null -'''
        ffmpeg_output = check_output(ffmpeg_command, stderr = STDOUT, shell = True).decode('utf-8')

        capture_metrics = search(pattern = REGEX_EXPRESSION, string = ffmpeg_output).group(0)
        capture_metrics = loads(capture_metrics)
        capture_metrics['file_size'] = getsize(file)

        return {'metrics': capture_metrics, 'status_code': 1}

    return {'file': file, 'error': 'Its not a valid audio file.', 'status_code': 0}


def second_pass(file, target_lufs, output_file):
    result = first_pass(file, target_lufs)

    if result['status_code'] == 0:
        return {'file': file, 'error': 'Its not a valid audio file.', 'status_code': 0}

    metrics = result['metrics']

    # TO-DO: default values for measured_I, measured_TP, measured_LRA, measured_thresh
    ffmpeg_command = f'''ffmpeg -hide_banner -nostdin -i {file} -af loudnorm=I={target_lufs}:TP=-1.5:LRA=11:measured_I={metrics['input_i']}:measured_TP={metrics['input_tp']}:measured_LRA={metrics['input_lra']}:measured_thresh={metrics['input_thresh']}:offset={metrics['target_offset']}:linear=true:print_format=summary -y {output_file}'''
    ffmpeg_output = check_output(ffmpeg_command, stderr = STDOUT, shell = True).decode('utf-8')

    # TO-DO: IF new_size > old_size print warning file_size
    # TO-DO: 
    return ffmpeg_output
