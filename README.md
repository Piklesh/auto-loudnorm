###### Para ler em pt-BR [clique aqui](README.pt-BR.md).

## What is this project? :thinking:

That's an **automatic aproach** to *FFmpeg* `loudnorm` audio filter wheres we need to manually execute the filter two times. On the first execution it's captured the audio information. On the second execution we need to use those audio information than loudnorm filter can normalize the audio loudness.

```shell
# First execution
ffmpeg -i "misc/audio_file.ogg" \
       -af loudnorm=I=-16:dual_mono=true:TP=-1.5:LRA=11:print_format=summary \
       -f null -

# That's the return
Input Integrated:    -27.2 LUFS
Input True Peak:     -14.4 dBTP
Input LRA:             0.1 LU
Input Threshold:     -37.7 LUFS
Output Integrated:   -15.5 LUFS
Output True Peak:     -2.7 dBTP
Output LRA:            0.0 LU
Output Threshold:    -26.2 LUFS
Normalization Type:        Dynamic
Target Offset:        -0.5 LU

# Second execution using the audio information returned
ffmpeg -i "misc/audio_file.ogg" \
       -af loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=-27.2:measured_TP=-14.4:measured_LRA=0.1:measured_thresh=-37.7:offset=-0.5:linear=true:print_format=summary \
       "misc/audio_file_normalized.ogg"
```

## External requirements

* Python (>= 3.8)
* FFmpeg (>= 3.1)
* FFprobe (>= 3.1)

## How to use

```shell
# Clone the project
git clone https://github.com/Multi8000/auto-2pass-loudnorm.git auto-2pass-loudnorm

# Change to the project directory
cd auto-2pass-loudnorm

# Install the Python modules used in this project
pip install -r requirements.txt
```

```shell
# Now you can use the `normalize.py`
python normalize.py -file FILE -lufs LUFS [-convert CONVERT]

-h                   Show help message and exit
-file FILE           The path of audio file to be normalized
-lufs LUFS           The target LUFS to normalize the audio file
-convert BOOLEAN     Convert the normalized file to .wav format?

# Example of use
python normalize.py -file "misc/audio_file.ogg" -lufs -16

# The normalized audio files will be saved at
# auto-2pass-loudnorm/misc/normalized
```
