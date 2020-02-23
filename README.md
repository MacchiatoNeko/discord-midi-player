# discord-midi-player
[![Total alerts](https://img.shields.io/lgtm/alerts/g/bluntano/discord-midi-player.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/bluntano/discord-midi-player/alerts/) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/bluntano/discord-midi-player.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/bluntano/discord-midi-player/context:python)

 🎵 Simple Discord MIDI player, converts MIDI to WAV with sound font. 🎵

## Content

### Sound fonts

In this repository, there are 4 sound fonts. You can additionally add yourself more to the `soundfonts/` folder, but you have to add these to `MIDIConverter.py` and `Bot.py` by changing the code a bit.

| Sound fonts         | Name            | Name in `!convert` command |
| :------------------ | :-------------- | :------------------------- |
| generaluser_gs.sf2  | Default         | `[Whatever you type there]`|
| megadrive.sf2       | Sega Genesis    | `megadrive`                |
| n64_2-0.sf2         | Nintendo 64     | `n64`                      |
| SNES.sf2            | Super Nintendo  | `snes`                     |

### Commands (that you can use for now)

Don't worry, I have other commands planned to implement. If I have time, I'll develop more commands in

| Commands                                                 | Description                           |
| :------------------------------------------------------- | :------------------------------------ |
| !convert <sound font and/or sample rate[optional]>       | Converts MIDI file to WAV audio file, and add to the queue |
| !play                                                    | Starts playing audio.                 |
| !stop                                                    | Stops playing audio.                  |
| !pause                                                   | Pauses playing audio.                 |
| !resume                                                  | Resumes paused audio.                 |
| !skip                                                    | Skips current playing song.           |
| !queue                                                   | Displays tracks being queued.         |
| !help                                                    | Shows commands                        |
| !soundfonts                                              | Shows soundfonts                      |

Sample rate max - 44100 Hz; min - 8000 Hz.

## Installation

Before you do anything, make a new `.env` file with the content:
```
DISCORD=<your app secret token>
DROPBOX=<your app secret token [optional if you want audio to be uploaded to Dropbox]>
```

To get it up and running, you first have to launch `bash setup.sh` to install all required packages. After that you can simply launch `./start.sh`.

### What do you essentially need from packets?

- Python with pip (minimum Python version 3.5.3 due to discord.py module requirement)
- ffmpeg (for playing songs in voice channel)
- Fluidsynth (for converting MIDI to WAV file)

**NOTE**: Works fine on Ubuntu 18.04 instance (AWS - Amazon Web Service). And `setup.sh` has a choice to make the bot work on instance startup, and log the bot's output when logging into the instance.

**ANOTHER NOTE:** doesn't work on Windows, only on Debian or Ubuntu (as much as I've tested)

## TODO

1. Custom bot prefix per server
2. lego city resque helicopter

I'll update the todo list from time to time.

## 

Alright, bye-bye :) Bluntano 2020
