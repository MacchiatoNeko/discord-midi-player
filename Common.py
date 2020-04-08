__all__ = ['MONGODB_HOST', 'MONGODB_PORT', 'TOKEN', 'NotMIDIFileError', 'add_to_json', 'ConversionError']

import json
import os

# Load variables from .env file
from dotenv import load_dotenv
load_dotenv(verbose=True)

# Get MongoDB variables (host and port)
MONGODB_HOST = os.getenv("MONGODB_HOST")
MONGODB_PORT = os.getenv("MONGODB_PORT")

# Get Discord app token
TOKEN = os.getenv("DISCORD")

# Global cooldown time set
cooldown_time = 3

# available sound fonts to use
soundfonts = []

for dirpath, dirnames, filenames in os.walk('soundfonts/'):
    for i in filenames:
        i = os.path.splitext(i)
        if i[1] == ".sf2":
            if i[0] != "generaluser_gs":
                soundfonts.append(i[0])
    break

# This is for storing MIDI file info and the MIDI file itself on
# guild's directory
class add_to_json:
    def __init__(self, name, id):
        self.name = name
        self.id = id
    
    def write_json_file(self):
        try:
            os.makedirs(f"guilds/{self.id}/")
        except FileExistsError:
            pass

        conv_dict = {'guild_id': self.id, 'filename': self.name}
        with open(f'guilds/{self.id}/info.json', 'w') as json_file:
            json.dump(conv_dict, json_file)
        return

# Error handling
class ConversionError(Exception):
    """Raised when there is an error with converting MIDI to WAV"""
    pass

class NotMIDIFileError(Exception):
    """Raised when submitted file is not MIDI"""
    pass