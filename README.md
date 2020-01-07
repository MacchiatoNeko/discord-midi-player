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

| Commands                                                 | Description                           | Usage / Example         |
| :------------------------------------------------------- | :------------------------------------ | :---------------------- |
| !convert <sound font[optional]> <sample rate[optional]>  | Converts MIDI file to WAV audio file. | `!convert snes 22050`
`!convert megadrive`
`!convert 19200`   |
| !play                                                    | Starts playing audio.                 | `!play`                 |
| !stop                                                    | Stops playing audio.                  | `!stop`                 |
| !pause                                                   | Pauses playing audio.                 | `!pause`                |
| !resume                                                  | Resumes paused audio.                 | `!resume`               |

Sample rate max - 44100 Hz; min - 8000 Hz.

## Installation

Before you do anything, make a new `.env` file with the content:
```
DISCORD=<your app secret token>
```

To get it up and running, you first have to launch `bash setup.sh` to install all required packages. After that you can simply launch `./start.sh`.

### What do you essentially need from packets?

- Python with pip (minimum Python version 3.5.3 due to discord.py module requirement)
- ffmpeg (for playing songs in voice channel)
- Fluidsynth (for converting MIDI to WAV file)

**ANOTHER NOTE:** doesn't work on Windows, only on Debian or Ubuntu (as much as I've tested)

## TODO

1. Make commands only available in specific text channel like #midi-player
2. `!convert` parameters, change there a bit
3. Multiple server / guild system (plays different MIDI from the other guild)
4. Add queue system
5. Some else

I'll update the todo list from time to time.

## 

Alright, bye-bye :) Bluntano 2020
