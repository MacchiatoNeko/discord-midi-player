# discord-midi-player
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/cb07b219f17b4868bda23eef13afdbf4)](https://app.codacy.com/manual/bluntano/discord-midi-player?utm_source=github.com&utm_medium=referral&utm_content=bluntano/discord-midi-player&utm_campaign=Badge_Grade_Dashboard)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/bluntano/discord-midi-player.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/bluntano/discord-midi-player/alerts/) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/bluntano/discord-midi-player.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/bluntano/discord-midi-player/context:python) [![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/ellarto)

 🎵 Simple Discord MIDI player, converts MIDI to WAV with sound font. 🎵

## Content

### Sound fonts

In this repository, there are 3 sound fonts. You can additionally add yourself more to the `soundfonts/` folder. `MIDIConverter.py` detects automatically sound font files for you on the bot startup, default there is `generaluser_gs.sf2`.

| Sound fonts         | Name            | Name in `midi.convert` command |
| :------------------ | :-------------- | :----------------------------- |
| generaluser_gs.sf2  | Default         | `[Whatever you type there]`    |
| n64.sf2             | Nintendo 64     | `n64`                          |
| snes.sf2            | Super Nintendo  | `snes`                         |

### Commands (that you can use for now)

Bot's default prefix is set as `midi.`. Every server can change their own prefix with the `midi.prefix <your new prefix>` command.

| Commands                                                        | Description                           |
| :-------------------------------------------------------------- | :------------------------------------ |
| `<prefix>convert <sound font and/or sample rate[optional]>`     | Converts MIDI file to WAV audio file, and add to the queue |
| `<prefix>play`                                                  | Starts playing audio.                 |
| `<prefix>stop`                                                  | Stops playing audio.                  |
| `<prefix>pause`                                                 | Pauses playing audio.                 |
| `<prefix>resume`                                                | Resumes paused audio.                 |
| `<prefix>skip`                                                  | Skips current playing song.           |
| `<prefix>queue`                                                 | Displays tracks being queued.         |
| `<prefix>help`                                                  | Shows commands                        |
| `<prefix>soundfonts`                                            | Shows soundfonts                      |
| `<prefix>prefix <custom prefix>`                                | Changes bot's prefix on the server    |

Sample rate max - 44100 Hz; min - 8000 Hz.

## Installation

Before you do anything, make a new `.env` file with the content:
```
DISCORD=<your app secret token>
MONGODB_HOST=<your MongoDB host, can be localhost>
MONGODB_PORT=<your MongoDB port, can be 27017>
FLASK_HOST=localhost
```

I would highly recommend changing the MongoDB's hosting port from default (27017) for safety concerns.

To get it up and running, you first have to launch `bash setup.sh` to install all required packages. After that you can simply launch `./start.sh`.

### What do you essentially need from packets?

- Python with pip (minimum Python version 3.5.3 due to discord.py module requirement)
- ffmpeg (for playing songs in voice channel)
- Fluidsynth (for converting MIDI to WAV file)
- MongoDB (for database storage - for now, prefix system)

To start MongoDB service immediately after setup, all you have to enter is `sudo systemctl start mongod`.

If you don't like to have MongoDB server on the same machine, you can disable it with `sudo systemctl disable mongod` and stop it by replacing disable with stop in the command.

**NOTE**: Works fine on Ubuntu 18.04 instance (AWS - Amazon Web Service). And `setup.sh` has a choice to make the bot work on instance startup, and log the bot's output when logging into the instance.

**ANOTHER NOTE:** doesn't work on Windows, only on Debian or Ubuntu (as much as I've tested). Debian has issue with setup shell code so, you may need to install packages manually.

## TODO

1. Develop skip vote system
2. Implement inactivity system (when inactive, leave the vc)
3. #StayTheFuckHome

I'll update the todo list from time to time.

## 

Alright, bye-bye :) Bluntano 2020
