import os

from dotenv import load_dotenv
load_dotenv(verbose=True)

TOKEN = os.getenv("DISCORD")
import discord
import asyncio
from discord.ext import commands
client = commands.Bot(command_prefix = "!")

import MIDIConverter as midic

cooldown_time = 5

@client.event
async def on_ready():
    game = discord.Game("yes | [BETA]")
    await client.change_presence(status=discord.Status.idle, activity=game)
    print("MIDI Player Ready")

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        return
    elif isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.errors.BadArgument):
        return
    raise error

@client.command()
@commands.cooldown(1, cooldown_time, commands.BucketType.guild)
async def convert(ctx, sf=None, sr=22050):
    channel = discord.utils.get(ctx.message.guild.channels, name='midi-player', type=discord.ChannelType.text)
    if ctx.message.channel != channel: return
    if ctx.message.author == client.user: return
    if ctx.message.author.bot == True: return
    if ctx.message.attachments == []:
        message = await ctx.send("❌ No MIDI file in the attachment!")
        return

    link = ctx.message.attachments[0].url
    message = await ctx.send("⏳ Checking the file...")

    midic.detect_midi_file(link)
    if midic.detect_midi_file.is_midi == False:
        await message.edit(content="❌ Not a valid MIDI file!")
        return

    soundfonts = ['megadrive', 'snes', 'n64']

    if sf != None:
        try:
            k = soundfonts.index(sf)
            sf = soundfonts[k]
        except ValueError:
            sf = 'default'
    
    if not isinstance(sr, int):
        await message.edit(content="❌ Not a valid sample rate!")
        return
    
    if sr > 44100:
        sr = 44100
    if sr < 8000:
        sr = 8000

    print('Converting with {} soundfont @ {} Hz...'.format(sf, sr))

    await message.edit(content="♻️ Uploading...")
    midic.convert_midi_to_audio(link, sf, sr)
    while True:
        is_uploaded = midic.convert_midi_to_audio.is_downloaded
        if not is_uploaded:
            error = midic.convert_midi_to_audio.error
            await message.edit(content="❗ Uploading failed:\n`{}`".format(error))
            break
        is_converted = midic.convert_midi_to_audio.is_converted
        if not is_converted:
            error = midic.convert_midi_to_audio.error
            await message.edit(content="❗ Converting failed:\n`{}`".format(error))
            break
        else:
            await message.edit(content="✅ MIDI file converted!")
            break

@client.command()
@commands.cooldown(1, cooldown_time, commands.BucketType.guild)
async def play(ctx):
    channel = discord.utils.get(ctx.message.guild.channels, name='midi-player', type=discord.ChannelType.text)
    if ctx.message.channel != channel: return
    if ctx.message.author.bot: return
    if ctx.message.author.id == client.user.id: return

    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('weed.wav'))
            ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
            await ctx.send("▶️ Playing")
            while ctx.voice_client.is_playing():
                await asyncio.sleep(1)
            ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("🚫 You are not connected to a voice channel!")
            raise commands.CommandError("Author not connected to a voice channel")

@client.command()
@commands.cooldown(1, cooldown_time, commands.BucketType.guild)
async def stop(ctx):
    channel = discord.utils.get(ctx.message.guild.channels, name='midi-player', type=discord.ChannelType.text)
    if ctx.message.channel != channel: return
    if ctx.message.author.bot: return
    if ctx.message.author.id == client.user.id: return

    if ctx.author.voice:
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
            await ctx.send("⏹️ Stopped")
        else:
            await ctx.send("🔇 There is nothing playing at the moment!")
    else:
        await ctx.send("🚫 You are not connected to a voice channel!")

@client.command()
@commands.cooldown(1, cooldown_time, commands.BucketType.guild)
async def pause(ctx):
    channel = discord.utils.get(ctx.message.guild.channels, name='midi-player', type=discord.ChannelType.text)
    if ctx.message.channel != channel: return
    if ctx.message.author.bot: return
    if ctx.message.author.id == client.user.id: return

    if ctx.author.voice:
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏸️ Paused")
        elif ctx.voice_client.is_paused():
            await ctx.send("⏯️ Already paused")
        else:
            await ctx.send("🔇 There is nothing playing at the moment!")
    else:
        await ctx.send("🚫 You are not connected to a voice channel!")

@client.command()
@commands.cooldown(1, cooldown_time, commands.BucketType.guild)
async def resume(ctx):
    channel = discord.utils.get(ctx.message.guild.channels, name='midi-player', type=discord.ChannelType.text)
    if ctx.message.channel != channel: return
    if ctx.message.author.bot: return
    if ctx.message.author.id == client.user.id: return

    if ctx.author.voice:
        if not ctx.voice_client.is_playing():
            ctx.voice_client.resume()
            await ctx.send("▶️ Resuming")
        elif ctx.voice_client.is_playing():
            await ctx.send("▶️ Already playing")
        else:
            await ctx.send("🔇 There is nothing playing at the moment!")
    else:
        await ctx.send("🚫 You are not connected to a voice channel!")

client.run(TOKEN)