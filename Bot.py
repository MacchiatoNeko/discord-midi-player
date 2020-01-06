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

class MIDI_player(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, cooldown_time, commands.BucketType.guild)
    async def convert(self, ctx, sf=None, sr=22050):
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

    @commands.command()
    @commands.cooldown(1, cooldown_time, commands.BucketType.guild)
    async def play(self, ctx):

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('weed.wav'))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
        await ctx.send("▶️ Playing")

    @commands.command()
    @commands.cooldown(1, cooldown_time, commands.BucketType.guild)
    async def stop(self, ctx):
        ctx.voice_client.stop()
        await ctx.send("⏹️ Stopped")

    @commands.command()
    @commands.cooldown(1, cooldown_time, commands.BucketType.guild)
    async def pause(self, ctx):

        song_playing = ctx.voice_client.is_playing()
        paused = ctx.voice_client.is_paused()

        if paused != True:
            ctx.voice_client.pause()
            await ctx.send("⏸️ Paused")
        else:
            if song_playing == True:
                await ctx.send("⏯️ Already paused")
            else:
                await ctx.send("🔇 There is nothing playing at the moment!")

    @commands.command()
    @commands.cooldown(1, cooldown_time, commands.BucketType.guild)
    async def resume(self, ctx):

        paused = ctx.voice_client.is_paused()

        if paused == True:
            ctx.voice_client.resume()
            await ctx.send("▶️ Resuming")
        else:
            await ctx.send("⏯️ Already playing")

    @convert.before_invoke
    @play.before_invoke
    @pause.before_invoke
    @stop.before_invoke
    @resume.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("🚫 You are not connected to a voice channel!")
    
    

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

client.add_cog(MIDI_player(client))
client.run(TOKEN)