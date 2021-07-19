# discord-midi-player

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

| Commands                                                        | Description                                                |
| :-------------------------------------------------------------- | :--------------------------------------------------------- |
| `<prefix>convert <sound font and/or sample rate[optional]>`     | Converts MIDI file to WAV audio file, and add to the queue |
| `<prefix>play`                                                  | Starts playing audio.                                      |
| `<prefix>stop`                                                  | Stops playing audio.                                       |
| `<prefix>pause`                                                 | Pauses playing audio.                                      |
| `<prefix>resume`                                                | Resumes paused audio.                                      |
| `<prefix>skip`                                                  | Skips current playing song.                                |
| `<prefix>queue`                                                 | Displays tracks being queued.                              |
| `<prefix>help`                                                  | Shows commands                                             |
| `<prefix>soundfonts`                                            | Shows soundfonts                                           |
| `<prefix>prefix <custom prefix>`                                | Changes bot's prefix on the server                         |

Sample rate max - 44100 Hz; min - 8000 Hz.

## Installation

Before you start, make sure you update your Discord bot token in `docker-compose.yml` in app section:
```
...
            DISCORD: 'your_bot_token_here'
...
```

And by any chance if you don't want to have external MongoDB connected to your bot, you can simply delete `mongo:` section in `docker-compose.yml`, and then update `MONGO_HOST` environment variable with your MongoDB host:
```
        environment: 
            MONGO_HOST: 'mongodb://<your_host>:<port>'
```

Since the bot is dockerized, all you need to install is Docker and Docker Compose (*Docker Compose comes with Docker Desktop for Windows and macOS by default*). After that you build the image and run it:
```
docker-compose build
docker-compose up
```

## TODO

1.  Develop skip vote system
2.  Implement inactivity system (when inactive, leave the vc)

## 

Alright, bye-bye :) Bluntano 2021
