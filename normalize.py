from argparse import ArgumentParser
from src.utils.__utils__ import (check_ffmpeg, check_ffprobe, delete_directory)
from src.utils.__normalize__ import Normalize


if __name__ == '__main__':

    if not check_ffmpeg():
        quit()

    if not check_ffprobe():
        quit()

    parser = ArgumentParser(description = 'Um programa de exemplo.')

    parser.add_argument('-file',
                        action = 'store',
                        dest = 'file',
                        required = True,
                        help = 'The path of audio file to be normalized.')

    parser.add_argument('-lufs',
                        action = 'store',
                        dest = 'lufs',
                        required = True,
                        help = 'The targed LUFS to normalize the audio file.')

    parser.add_argument('-convert',
                        action = 'store',
                        dest = 'convert',
                        required = False,
                        default = False,
                        help = 'Convert the normalized file to .wav format?')

    arguments = parser.parse_args()

    normalize = Normalize()
    normalize.second_pass(file = arguments.file,
                          target_lufs = arguments.lufs,
                          convert_to_wav = arguments.convert)

    delete_directory('misc/filled')
    delete_directory('misc/temp')
