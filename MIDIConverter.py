################################
# MIT License                  #
# ---------------------------- #
# Copyright (c) 2020 Bluntano  #
################################
import os
import json
import requests # for downloading MIDI file from link
import audio_metadata # for checking converted WAV metadata
from midi2audio import FluidSynth

# for debugging info
from pytz import timezone
from datetime import datetime
tz = timezone('EET')

soundfonts = []
DEBUG = True

class MIDIConverter:

    for dirpath, dirnames, filenames in os.walk('soundfonts/'):
        for i in filenames:
            i = os.path.splitext(i)
            if i[1] == ".sf2":
                if i[0] != "generaluser_gs":
                    soundfonts.append(i[0])
        break
    
    def __init__(self, discord_id, url):
        """MIDI Converter module
        Parameters
        ==========
        discord_id : int
            Discord guild's id (in this context).
        url : string
            URL to check validation of and/or downloading MIDI file.
        """
        self.id = discord_id
        self.url = url
        self.sample_rate = 22050 # default sample rate
        self.sf = "generaluser_gs" # default sound font

    # For detecting whether the file is MIDI or not
    # method used here: the end of the url passed in the function
    def is_midi_file(self):
        """Checks whether the file from URL is MIDI or not"""
        mid = ['mid', 'midi']
        file_ext = self.url.rsplit('.', 1)[1]
        return bool(file_ext in mid)

    # MIDI to WAV Converter
    def convert_midi_to_audio(self, name, sample_rate=22050, sf='generaluser_gs'):
        """Downloads MIDI from the URL and converts it to WAV file.

        Parameters
        ==========
        name : string
            MIDI file name
        
        sample_rate : int
            Sample rate to convert at (default is 22050)
        
        sf : string
            Sound font to convert with (default is 'generaluser_gs')
        """

        self.name = name
        self.midi_path = f'guilds/{self.id}/{self.name}.mid'
        self.wav_file = f'guilds/{self.id}/{self.name}.wav'
        self.sample_rate = sample_rate
        self.duration = 0
        self.success = False
        self.error = ""

        if not os.path.exists(f'guilds/{self.id}'):
            os.makedirs(f'guilds/{self.id}')

        # downloading MIDI from the link
        headers = {
            'User-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
        }
        try:
            r = requests.get(url=self.url, headers=headers, stream=True)
            with open(self.midi_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

            if sf in soundfonts:
                self.sf = sf

            fs = FluidSynth(f'soundfonts/{self.sf}.sf2', sample_rate=self.sample_rate)
            
            # file duplicate prevention
            if not os.path.exists(self.wav_file):
                fs.midi_to_audio(self.midi_path, self.wav_file)

                # metadata check
                metadata = audio_metadata.load(self.wav_file)
                self.duration = metadata.streaminfo['duration']
                if self.duration > 600:
                    os.remove(self.wav_file)
                    raise ConversionError("MIDI file longer than 10 minutes.")
            else:
                print(f"{self.wav_file} already exists!")

            # removes MIDI file
            os.remove(self.midi_path)
            self.success = True
            self.debug()
            return self.wav_file
            
        except Exception as e:
            self.error = str(e)
            self.debug()
            raise ConversionError(self.error)
    
    def debug(self):
        if DEBUG:
            info = {
                self.id: {
                    'date-time': str(datetime.now(tz)),
                    'midi_path': self.midi_path,
                    'url': self.url,
                    'sf': self.sf,
                    'file_name': self.name,
                    'wav_file:': {
                        'path': self.wav_file,
                        'duration': self.duration
                    },
                    'convert_success': [
                        self.success, 'no errors' if not self.error else self.error
                    ]
                }
            }
            if not os.path.exists('debug.json'):
                with open('debug.json', 'w', encoding='utf-8') as outfile:
                    outfile.write(json.dumps({'debug': []}, indent=4, sort_keys=True))
            with open('debug.json', 'r') as infile:
                data = json.load(infile)
                data['debug'].append(info)
                with open('debug.json', 'w') as outfile:
                    json.dump(data, outfile, indent=4, sort_keys=True)

class ConversionError(Exception):
    """Raised when there is an error with converting MIDI to WAV"""
