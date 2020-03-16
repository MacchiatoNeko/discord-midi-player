################################
# MIT License                  #
# ---------------------------- #
# Copyright (c) 2020 Bluntano  #
################################
import os
import requests # for downloading MIDI file from link
from midi2audio import FluidSynth
import json

# Boolean for to allow/deny uploading converted WAV file to Dropbox
allow_dropbox_upload = False

# For detecting whether the file is MIDI or not
# method used here: the end of the url passed in the function
def detect_midi_file(discord_url):
    mid = ['MID', 'mid', 'Mid', 'MIDI', 'midi', 'Midi']
    if discord_url.endswith(tuple(mid)):
        detect_midi_file.is_midi = True
        return
    else:
        detect_midi_file.is_midi = False
        return

# MIDI to WAV Converter
def convert_midi_to_audio(audio, sf, sample_rate, id, name):

    midi_path = 'guilds/{}/midi_to_convert.mid'.format(id)
    info_path = 'guilds/{}/info.json'.format(id)

    # downloading MIDI from the link
    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
    }
    try:
        r = requests.get(url=audio, headers=headers, stream=True)
        with open(midi_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        
        # checks which sound font got passed
        if sf == 'megadrive':
            fs = FluidSynth('soundfonts/megadrive.sf2', sample_rate=sample_rate)
        elif sf == 'snes':
            fs = FluidSynth('soundfonts/SNES.sf2', sample_rate=sample_rate)
        elif sf == 'n64':
            fs = FluidSynth('soundfonts/n64_2-0.sf2', sample_rate=sample_rate)
        else:
            fs = FluidSynth('soundfonts/generaluser_gs.sf2', sample_rate=sample_rate)
        
        # file duplicate prevention
        if not os.path.exists('guilds/{}/{}.wav'.format(id, name)):
            fs.midi_to_audio(midi_path, 'guilds/{}/{}.wav'.format(id, name))
        else:
            print("/{}/{}.wav already exists!".format(id, name))
        convert_midi_to_audio.is_converted = True

        # removes MIDI file and metadata JSON file
        os.remove(midi_path)
        os.remove(info_path)
        
    except Exception as e:
        print('Err:', e)
        convert_midi_to_audio.is_converted = False
        convert_midi_to_audio.error = str(e)
        return