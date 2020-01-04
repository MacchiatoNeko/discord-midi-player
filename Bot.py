import os

from dotenv import load_dotenv
load_dotenv(verbose=True)

TOKEN = os.getenv("DISCORD")
import discord
import asyncio
from discord.ext import commands
from discord.ext.commands import Bot
client = Bot(command_prefix = ["!"])

import MIDIConverter as midic

@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name='MIDI\'s'))
    print("Weed is ready to serve!")

@client.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.CommandOnCooldown):
        return
    elif isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.errors.BadArgument):
        return
    raise error

@client.command(pass_context=True)
@commands.cooldown(1, 12, commands.BucketType.server)
async def convert(ctx, link, sf=None, sr=22050):
    channel = discord.utils.get(ctx.message.server.channels, name='midi-player', type=discord.ChannelType.text)
    if ctx.message.author == client.user: return
    if ctx.message.author.bot == True: return
    if ctx.message.channel != channel: return
    if ctx.message.attachments == []: return

    link = ctx.message.attachments[0]['url']
    await client.send_typing(channel)
    msg_status = await client.send_message(ctx.message.channel, "⏳ Checking the file...")

    midic.detect_midi_file(link)
    if midic.detect_midi_file.is_midi == False:
        await client.edit_message(msg_status, "❌ Not a valid MIDI file!")
        return

    soundfonts = ['megadrive', 'snes', 'n64']

    if sf != None:
        try:
            k = soundfonts.index(sf)
            sf = soundfonts[k]
        except ValueError:
            sf = 'default'
    
    if not isinstance(sr, int):
        await client.edit_message(msg_status, "❌ Not a valid sample rate!")
        return
    
    if sr > 44100:
        sr = 44100
    if sr < 8000:
        sr = 8000

    print('Converting with {} soundfont @ {} Hz...'.format(sf, sr))

    msg_status = await client.edit_message(msg_status, "♻️ Uploading...")
    midic.convert_midi_to_audio(link, sf, sr)
    while True:
        is_uploaded = midic.convert_midi_to_audio.is_downloaded
        if not is_uploaded:
            error = midic.convert_midi_to_audio.error
            await client.edit_message(msg_status, "❗ Uploading failed:\n`{}`".format(error))
            break
        is_converted = midic.convert_midi_to_audio.is_converted
        if not is_converted:
            error = midic.convert_midi_to_audio.error
            await client.edit_message(msg_status, "❗ Converting failed:\n`{}`".format(error))
            break
        else:
            await client.edit_message(msg_status, "✅ MIDI file converted!")
            break

@client.command(pass_context=True)
@commands.cooldown(1, 12, commands.BucketType.server)
async def play(ctx):
    channel = discord.utils.get(ctx.message.server.channels, name='midi-player', type=discord.ChannelType.text)
    if ctx.message.author == client.user: return
    if ctx.message.author.bot == True: return
    if ctx.message.channel != channel: return

    user = ctx.message.author
    voice_channel = user.voice.voice_channel
    channel = None
    if voice_channel != None:
        channel=voice_channel.name
        try:
            vc = await client.join_voice_channel(voice_channel)
            player = vc.create_ffmpeg_player('./weed.wav')
            player.start()
            while not player.is_done():
                await asyncio.sleep(1)

            player.stop()
            await vc.disconnect()
        except discord.ClientException as e:
            print('error:', e)

client.run(TOKEN)