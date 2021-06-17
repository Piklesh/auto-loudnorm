from pathlib import Path
from subprocess import (run, PIPE)
from librosa.core.audio import get_duration
from json import loads
from string import Formatter
from pathlib import Path


class KindlyGetDictKey(Formatter):
    """
    Function description.

    Parameters
    ----------
    file : `string`

    Return
    ------
    Returns a `dict` containing the file name and a boolen if file is audio or not.

    Usage example
    -------------
        >>> data = {'name': 'Marcos', 'age': 23}
        >>> graceffuly = KindlyGetDictKey()
        >>> result = graceffuly.format('{name}, {age}, {hair_color}', **data)
        >>> print(result)
        Marcos, 23, ?
    """

    def __init__(self, missing = '?', bad_fmt = '!'):
        self.missing = missing
        self.bad_fmt = bad_fmt

    def get_field(self, field_name, args, kwargs):
        try:
            val = super(KindlyGetDictKey, self).get_field(field_name, args, kwargs)
        except (KeyError, AttributeError, IndexError):
            val = None, field_name
        return val

    def format_field(self, value, spec):
        if value == None:
            return self.missing
        try:
            return super(KindlyGetDictKey, self).format_field(value, spec)
        except ValueError:
            if self.bad_fmt is not None:
                return self.bad_fmt
            else:
                raise


def is_audio_file(file):
    """
    Function description.

    Parameters
    ----------
    file : `string`

    Return
    ------
    Returns a `dict` containing the file name and a boolen if file is audio or not.

    Usage example
    -------------
        >>> iam_audio = is_audio_file('misc/audio_file_1.txt')
        >>> print()
        {'file': 'misc/audio_file_1.txt', 'is_audio_file': False}
    """

    data = dict()
    graceffuly = KindlyGetDictKey()

    _file_ = Path(file)

    ffprobe_command = f'''ffprobe                               \
                            -loglevel quiet                     \
                            -i "{_file_}"                       \
                            -select_streams a                   \
                            -show_entries                       \
                                stream=codec_type               \
                            -print_format json                  \
                        '''
    ffprobe_output = run(args = ffprobe_command, stdout = PIPE)
    ffprobe_output = loads(ffprobe_output.stdout)

    graceffuly_output = graceffuly.format('{streams[0][codec_type]}', **ffprobe_output)

    if graceffuly_output == '?' or graceffuly_output is None:
        data['file'] = _file_
        data['is_audio_file'] = False

        return data

    data['file'] = _file_
    data['is_audio_file'] = True

    return data


def has_length_gte_3s(file):
    _file_ = Path(file)
    duration = get_duration(filename = _file_)

    return True if duration > 3 else False
