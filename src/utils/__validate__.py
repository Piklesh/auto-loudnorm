import subprocess
import json
import string


class GraceffulyGetDictKey(string.Formatter):
    """
    Function description.

    ### Parameters
    file : `string`

    ### Return
    Returns a `dict` containing the file name and a boolen if file is audio or not.

    ### Usage example
        >>> data = {'name': 'Marcos', 'age': 23}
        >>> graceffuly = GraceffulyGetDictKey()
        >>> result = graceffuly.format('{name}, {age}, {hair_color}', **data)
        >>> print(result)
    Marcos, 23, ?

    """

    def __init__(self, missing = '?', bad_fmt = '!'):
        self.missing = missing
        self.bad_fmt = bad_fmt

    def get_field(self, field_name, args, kwargs):
        try:
            val = super(GraceffulyGetDictKey, self).get_field(field_name, args, kwargs)
        except (KeyError, AttributeError, IndexError):
            val = None, field_name
        return val

    def format_field(self, value, spec):
        if value == None:
            return self.missing
        try:
            return super(GraceffulyGetDictKey, self).format_field(value, spec)
        except ValueError:
            if self.bad_fmt is not None:
                return self.bad_fmt
            else:
                raise


def is_audio_file(file):
    """
    Function description.

    ### Parameters
    file : `string`

    ### Return
    Returns a `dict` containing the file name and a boolen if file is audio or not.

    ### Usage example
        >>> iam_audio = is_audio_file('misc/audio_file_1.txt')
        >>> print()
    {'file': 'misc/audio_file_1.txt', 'is_audio_file': False}

    """

    data = dict()
    graceffuly = GraceffulyGetDictKey()

    ffprobe_command = f'''ffprobe -hide_banner -i {file} -loglevel quiet -select_streams a -show_entries stream=codec_type -print_format json'''
    output = subprocess.run(ffprobe_command, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, universal_newlines = True)
    output = json.loads(output.stdout)
    graceffuly_output = graceffuly.format('{streams[0][codec_type]}', **output)

    if graceffuly_output == '?' or graceffuly_output is None:
        data['file'] = file
        data['is_audio_file'] = False

        return data

    data['file'] = file
    data['is_audio_file'] = True

    return data


def has_lenght_gte_3s(file):
    ...