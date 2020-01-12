# discord-midi-player
 🎵 Simple Discord MIDI player, converts MIDI to WAV with sound font. 🎵
 
**[BETA AS FUCC]**

## Content

### Sound fonts

In this repository, there are 4 sound fonts. You can additionally add yourself more to the `soundfonts/` folder, but you have to add these to `MIDIConverter.py` and `Bot.py` by changing the code a bit.

| Sound fonts         | Name            | Name in `!convert` command |
| :------------------ | :-------------- | :------------------------- |
| generaluser_gs.sf2  | Default         | `[Whatever you type there]`|
| megadrive.sf2       | Sega Genesis    | `megadrive`                |
| n64_1.sf2           | Nintendo 64     | `n64`                      |
| SNES.sf2            | Super Nintendo  | `snes`                     |

### Commands (that you can use for now)

Don't worry, I have other commands planned to implement. If I have time, I'll develop more commands in

| Commands                                                 | Description                           |
| :------------------------------------------------------- | :------------------------------------ |
| !convert <sound font and/or sample rate[optional]>       | Converts MIDI file to WAV audio file. |
| !play                                                    | Starts playing audio.                 |
| !stop                                                    | Stops playing audio.                  |
| !pause                                                   | Pauses playing audio.                 |
| !resume                                                  | Resumes paused audio.                 |

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

**ANOTHER NOTE:** doesn't work on Windows, only on Debian or Ubuntu (as much as I've tested)

### AWS (Amazon Web Services)

This repository's setup script (`setup.sh`) automates everything according to the AWS instance. It automatically makes `rc.local` file with commands in them + adds `tail -f /tmp/rc.local.log` to the `.bashrc` file at the end (when logging in, you'll see the bot output logs pretty much). I'll work on it so you could have a choice not to, if you don't want to nor have no root user access.

## TODO

1. Setup script a bit more dynamic
2. Add queue system
3. Custom bot prefix per server
4. memes

I'll update the todo list from time to time.

## 

Alright, bye-bye :) Bluntano 2020
