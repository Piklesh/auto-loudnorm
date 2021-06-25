###### Para retornar à página principal [clique aqui](https://github.com/Multi8000/auto-2pass-loudnorm).

## O que é esse projeto? :thinking:

É uma **abordagem automática** ao filtro de áudio `loudnorm` do *FFmpeg* onde é necessário executá-lo manualmente duas vezes. Na primeira execução do filtro é capturada as informações a respeito do áudio. Na segunda execução o áudio é normalizado usando as informações que foram capturadas da primeira vez.

```shell
# Primeira execução
ffmpeg -i "misc/audio_file.ogg" \
       -af loudnorm=I=-16:dual_mono=true:TP=-1.5:LRA=11:print_format=summary \
       -f null -

# Esse é o retorno
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

# Now run the second time using the audio information returned
ffmpeg -i "misc/audio_file.ogg" \
       -af loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=-27.2:measured_TP=-14.4:measured_LRA=0.1:measured_thresh=-37.7:offset=-0.5:linear=true:print_format=summary \
       "misc/audio_file_normalized.ogg"
```

## Requisitos externos

* Python (>= 3.8)
* FFmpeg (>= 3.1)
* FFprobe (>= 3.1)

## Como usar

```shell
# Clone o projeto
git clone https://github.com/Multi8000/auto-2pass-loudnorm.git auto-2pass-loudnorm

# Navegue até o diretório do projeto
cd auto-2pass-loudnorm

# Instale os módulos do Python usados neste projeto
pip install -r requirements.txt
```

```shell
# Agora você pode usar o `normalize.py`
python normalize.py -file FILE -lufs LUFS [-convert CONVERT]

-h                   Show help message and exit
-file FILE           The path of audio file to be normalized
-lufs LUFS           The target LUFS to normalize the audio file
-convert BOOLEAN     Convert the normalized file to .wav format?

# Exemplo de uso
python normalize.py -file "misc/audio_file.ogg" -lufs -16

# Os arquivos de áudio normalizados serão salvos em './auto-2pass-loudnorm/misc/normalized'
```
