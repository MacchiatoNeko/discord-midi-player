import requests
from midi2audio import FluidSynth

def detect_midi_file(discord_url):
    mid = ['MID', 'mid', 'Mid', 'MIDI', 'midi', 'Midi']
    if discord_url.endswith(tuple(mid)):
        detect_midi_file.is_midi = True
        return
    else:
        detect_midi_file.is_midi = False
        return

def convert_midi_to_audio(audio, sf, sample_rate):
    '''Convert MIDI file into audio'''
    '''audio - midi file to convert'''
    '''sf - sound font'''
    '''sample_rate - sample rate when converting into wav'''

    midi_path = './midi_to_convert.mid'

    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
    }
    try:
        r = requests.get(url=audio, headers=headers, stream=True)
        with open(midi_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        convert_midi_to_audio.is_downloaded = True
    except Exception as e:
        print('Err:', e)
        convert_midi_to_audio.is_downloaded = False
        convert_midi_to_audio.error = str(e)
        return

    try:
        if sf == 'megadrive':
            fs = FluidSynth('megadrive.sf2', sample_rate=sample_rate)
            convert_midi_to_audio.sound_font = 'Megadrive / Sega Genesis'
        elif sf == 'snes':
            fs = FluidSynth('SNES.sf2', sample_rate=sample_rate)
            convert_midi_to_audio.sound_font = 'SNES / Super Nintendo'
        elif sf == 'n64':
            fs = FluidSynth('n64_1.sf2', sample_rate=sample_rate)
            convert_midi_to_audio.sound_font = 'N64 / Nintendo 64'
        else:
            fs = FluidSynth('generaluser_gs.sf2', sample_rate=sample_rate)
            convert_midi_to_audio.sound_font = 'GeneralUser GS [Default]'
        fs.midi_to_audio(midi_path, './weed.wav')
        """
        with open('weed.wav', 'rb') as conv_midi:
            try:
                dbx.files_upload(conv_midi.read(), '/converted_audio/audio.wav', mute=True, autorename=True)
                print('Uploading just converted midi file to Dropbox')
                print('===========================================')
            except Exception as err:
                print('Error occured when uploading to Dropbox:', err)
        """
        convert_midi_to_audio.is_converted = True
        return
    except Exception as e:
        convert_midi_to_audio.is_converted = False
        convert_midi_to_audio.error = str(e)
        return print("Error occured:", e)