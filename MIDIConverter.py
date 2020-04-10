################################
# MIT License                  #
# ---------------------------- #
# Copyright (c) 2020 Bluntano  #
################################
import os
import requests # for downloading MIDI file from link
import audio_metadata # for checking converted WAV metadata
from midi2audio import FluidSynth
from Common import ConversionError, NotMIDIFileError, soundfonts

class MIDIConverter:

    def __init__(self, url, sf, sample_rate, id, name):
        self.url = url
        self.sf = sf
        self.sample_rate = sample_rate
        self.id = id
        self.name = name

    # For detecting whether the file is MIDI or not
    # method used here: the end of the url passed in the function
    def is_midi_file(self):
        mid = ['MID', 'mid', 'Mid', 'MIDI', 'midi', 'Midi']
        if self.url.endswith(tuple(mid)):
            return True
        else:
            raise NotMIDIFileError(f"{self.url} not a valid MIDI file")

    # MIDI to WAV Converter
    def convert_midi_to_audio(self):

        server_path = f"guilds/{self.id}"

        midi_path = f'{server_path}/midi_to_convert.mid'
        info_path = f'{server_path}/info.json'

        # downloading MIDI from the link
        headers = {
            'User-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
        }
        try:
            r = requests.get(url=self.url, headers=headers, stream=True)
            with open(midi_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

            # checks which sound font got passed
            sf_toconvert = "generaluser_gs" # by default

            if self.sf in soundfonts:
                sf_toconvert = self.sf

            fs = FluidSynth(f'soundfonts/{sf_toconvert}.sf2', sample_rate=self.sample_rate)
            
            # file duplicate prevention
            wav_file = f'{server_path}/{self.name}.wav'
            if not os.path.exists(wav_file):
                fs.midi_to_audio(midi_path, wav_file)

                # metadata check
                metadata = audio_metadata.load(wav_file)
                duration = metadata.streaminfo['duration']
                if duration > 600:
                    os.remove(wav_file)
                    raise ConversionError("MIDI file longer than 10 minutes.")

            else:
                print(f"{wav_file} already exists!")

            # removes MIDI file and metadata JSON file
            os.remove(midi_path)
            os.remove(info_path)
            return True
            
        except Exception as e:
            raise ConversionError(e)