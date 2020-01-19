import os
import requests
from midi2audio import FluidSynth
import json

# Boolean for to allow/deny uploading converted WAV file to Dropbox
allow_dropbox_upload = False

def detect_midi_file(discord_url):
    mid = ['MID', 'mid', 'Mid', 'MIDI', 'midi', 'Midi']
    if discord_url.endswith(tuple(mid)):
        detect_midi_file.is_midi = True
        return
    else:
        detect_midi_file.is_midi = False
        return

def convert_midi_to_audio(audio, sf, sample_rate, id, name):

    midi_path = 'guilds/{}/midi_to_convert.mid'.format(id)
    info_path = 'guilds/{}/info.json'.format(id)

    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
    }
    try:
        r = requests.get(url=audio, headers=headers, stream=True)
        with open(midi_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        if sf == 'megadrive':
            fs = FluidSynth('soundfonts/megadrive.sf2', sample_rate=sample_rate)
        elif sf == 'snes':
            fs = FluidSynth('soundfonts/SNES.sf2', sample_rate=sample_rate)
        elif sf == 'n64':
            fs = FluidSynth('soundfonts/n64_1.sf2', sample_rate=sample_rate)
        else:
            fs = FluidSynth('soundfonts/generaluser_gs.sf2', sample_rate=sample_rate)
        
        if not os.path.exists('guilds/{}/{}.wav'.format(id, name)):
            fs.midi_to_audio(midi_path, 'guilds/{}/{}.wav'.format(id, name))
        else:
            print("/{}/{}.wav already exists!".format(id, name))
        convert_midi_to_audio.is_converted = True

        os.remove(midi_path)

        if allow_dropbox_upload:
            with open('guilds/{}/info.json'.format(id)) as f:
                data = json.load(f)
                audio = audio_to_dropbox(id, data['filename'])
                audio.upload_audio()

        os.remove(info_path)
        
    except Exception as e:
        print('Err:', e)
        convert_midi_to_audio.is_converted = False
        convert_midi_to_audio.error = str(e)
        return

class audio_to_dropbox:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.local_path = 'guilds/{}/{}.wav'.format(id, name)
        self.upload_path = '/converted_audio/{}/{}.wav'.format(id, name)
    
    def upload_audio(self):
        from dotenv import load_dotenv
        load_dotenv(verbose=True)

        import dropbox

        token = os.getenv("DROPBOX")
        dbx = dropbox.Dropbox(token)

        print('Uploading just converted midi file to Dropbox')
        print('===========================================')
        with open(self.local_path, 'rb') as conv_midi:
            try:
                dbx.files_upload(conv_midi.read(), self.upload_path, mute=True, autorename=True)
                print("Uploaded")
            except Exception as err:
                print('Error occured whilst uploading to Dropbox:', err)