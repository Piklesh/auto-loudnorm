from subprocess import (run, PIPE)
from pathlib import Path
from __validate__ import (is_audio_file, has_length_gte_3s)
from __utils__ import (AudioTools, file_size, make_directory)
from json import loads
from re import search


REGEX_EXPRESSION = r'\{(\r.*|\n.*)+[}$]'


def first_pass(file, target_lufs):
    if (is_audio_file(file)['is_audio_file'] and has_length_gte_3s(file)):
    # TO-DO: if not has_lenght_gte_3s, fill with fill_audio_length()
        ffmpeg_command = f'''ffmpeg                             \
                                -hide_banner                    \
                                -nostdin                        \
                                -i {file}                       \
                                -af loudnorm=I={target_lufs}    \
                                        :dual_mono=true         \
                                        :TP=-1.5                \
                                        :LRA=11                 \
                                        :print_format=json      \
                                -f null -                       \
                            '''
        ffmpeg_output = run(args = ffmpeg_command, stderr = PIPE)
        ffmpeg_output = ffmpeg_output.stderr
        ffmpeg_output = ffmpeg_output.decode(encoding = 'utf-8')

        capture_metrics = search(pattern = REGEX_EXPRESSION, string = ffmpeg_output).group(0)
        metrics = loads(capture_metrics)
        metrics['file_size'] = file_size(file)

        return {'sucess': True, 'metrics': metrics}

    return {'sucess': False, 'error': 'Invalid audio file.', 'file': file}


def second_pass(file, target_lufs, convert_to_wav = False, output_folder = 'misc/normalized'):
    make_directory(output_folder)

    file_name = Path(file).name
    file_name_without_suffix = Path(file).stem
    result = first_pass(file, target_lufs)

    if result['sucess'] == False:
        return {'sucess': False, 'error': 'Invalid audio file.', 'file': file}

    metrics = result['metrics']

    ffmpeg_command = f'''ffmpeg                                                 \
                            -loglevel quiet                                     \
                            -i {file}                                           \
                            -af loudnorm=I={target_lufs}                        \
                                    :TP=-1.5                                    \
                                    :LRA=11                                     \
                                    :measured_I={metrics['input_i']}            \
                                    :measured_TP={metrics['input_tp']}          \
                                    :measured_LRA={metrics['input_lra']}        \
                                    :measured_thresh={metrics['input_thresh']}  \
                                    :offset={metrics['target_offset']}          \
                                    :linear=true                                \
                                    :print_format=summary                       \
                            -y {output_folder}/{file_name}                      \
                        '''
    ffmpeg_output = run(args = ffmpeg_command, stderr = PIPE)

    if convert_to_wav:
    # TO-DO: capture input sample rate and channels
    # check if ffmpeg by default already capture this
        ffmpeg_command = f'''ffmpeg                                     \
                                -loglevel quiet                         \
                                -i {output_folder}/{file_name}          \
                                -c:a pcm_s16le                          \
                                -ar 44100                               \
                                -ac 2                                   \
                                -y {output_folder}/{file_name_without_suffix}.wav   \
                            '''
        ffmpeg_output = run(args = ffmpeg_command, stderr = PIPE)

    # TO-DO: IF new_size > old_size print warning file_size
    return {'sucess': True}
