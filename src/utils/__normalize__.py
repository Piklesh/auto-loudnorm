from subprocess import (run, PIPE)
from pathlib import Path
from json import loads
from re import search
from distutils.util import strtobool
from src.utils.__validate__ import (is_audio_file, has_length_gte_3s)
from src.utils.__utils__ import (AudioTools, file_size, make_directory)


REGEX_EXPRESSION = r'\{(\r.*|\n.*)+[}$]'


class Normalize():

    def __init__(self):
        self.full_path = ''
        self.directory = ''
        self.file_name = ''
        self.file_name_no_suffix = ''
        self.target_lufs = 0
        self.metrics = ''
        self.original_audio_duration = 0
        self.output_folder = ''


    def first_pass(self, file, target_lufs):
        self.full_path = Path(file)
        self.directory = Path(file).parent
        self.file_name = Path(file).name
        self.file_name_no_suffix = Path(file).stem
        self.target_lufs = target_lufs


        if is_audio_file(self.full_path)['is_audio_file'] and not has_length_gte_3s(self.full_path):
            tools = AudioTools()
            tools.fill_audio_length(self.full_path)

            self.original_audio_duration = tools.original_audio_duration
            self.directory = 'misc/filled'
            self.file_name = f'{tools.filled_file_name}{tools.filled_file_suffix}'
            self.file_name_no_suffix = tools.filled_file_name
            self.full_path = f'{self.directory}/{self.file_name}'


        if (is_audio_file(self.full_path)['is_audio_file'] and has_length_gte_3s(self.full_path)):
            ffmpeg_command = f'''ffmpeg                                 \
                                    -hide_banner                        \
                                    -nostdin                            \
                                    -i "{self.full_path}"               \
                                    -af loudnorm=I={self.target_lufs}:dual_mono=true:TP=-1.5:LRA=11:print_format=json \
                                    -f null -                           \
                                '''
            ffmpeg_output = run(args = ffmpeg_command, stderr = PIPE)
            ffmpeg_output = ffmpeg_output.stderr
            ffmpeg_output = ffmpeg_output.decode(encoding = 'utf-8')

            capture_metrics = search(pattern = REGEX_EXPRESSION, string = ffmpeg_output).group(0)
            self.metrics = loads(capture_metrics)
            self.metrics['file_size'] = file_size(self.full_path)

            return {'sucess': True,
                    'message': 'Audio loudness metrics captured'}

        return {'sucess': False,
                'message': f'"{Path(file).name}" is a invalid audio file'}


    def second_pass(self, file, target_lufs, convert_to_wav = False):
        tools = AudioTools()

        self.output_folder = 'misc/temp'
        self.original_file_name = Path(file).name

        if strtobool(str(convert_to_wav)) == 0:
            convert_to_wav = False
        else:
            convert_to_wav = True

        make_directory(self.output_folder)

        result = self.first_pass(file = Path(file), target_lufs = target_lufs)

        if result['sucess'] == False:
            return {'sucess': False,
                    'message': f'"{Path(file).name}" is a invalid audio file'}

        ffmpeg_command = f'''ffmpeg\
                                -loglevel quiet\
                                -i "{self.full_path}"\
                                -af loudnorm=I={target_lufs}:TP=-1.5:LRA=11:measured_I={self.metrics['input_i']}:measured_TP={self.metrics['input_tp']}:measured_LRA={self.metrics['input_lra']}:measured_thresh={self.metrics['input_thresh']}:offset={self.metrics['target_offset']}:linear=true:print_format=summary\
                                -y {self.output_folder}/{self.original_file_name}\
                            '''
        ffmpeg_output = run(args = ffmpeg_command, stderr = PIPE)

        tools.back_normal_length(filled_file = f'{self.output_folder}/{self.original_file_name}',
                                 original_audio_duration = self.original_audio_duration,
                                 output_filename = self.original_file_name)

        if convert_to_wav:
        # TO-DO: capture input sample rate and channels
            ffmpeg_command = f'''ffmpeg                                                     \
                                    -loglevel quiet                                         \
                                    -i "{self.output_folder}/{self.file_name}"              \
                                    -c:a pcm_s16le                                          \
                                    -ar 44100                                               \
                                    -ac 2                                                   \
                                    -y {self.output_folder}/{self.file_name_no_sufix}.wav   \
                                '''
            ffmpeg_output = run(args = ffmpeg_command, stderr = PIPE)

        # TO-DO: IF new_size > old_size print warning file_size
        return {'sucess': True,
                'message': f'Audio for file "{Path(file).name}" normalized'}
