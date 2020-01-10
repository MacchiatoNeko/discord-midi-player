import os

from dotenv import load_dotenv
load_dotenv(verbose=True)

TOKEN = os.getenv("DISCORD")
import discord
import asyncio
from discord.ext import commands
client = commands.Bot(command_prefix = "!")

import MIDIConverter as midic

import FileServer
FileServer.run_it()
cooldown_time = 3

class MIDI_player(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, cooldown_time, commands.BucketType.guild)
    async def convert(self, ctx, arg1=None, arg2=None):
        if ctx.message.attachments == []:
            message = await ctx.send("❌ No MIDI file in the attachment!")
            return

        link = ctx.message.attachments[0].url
        message = await ctx.send("⏳ Checking the file...")

        midic.detect_midi_file(link)
        if midic.detect_midi_file.is_midi == False:
            await message.edit(content="❌ Not a valid MIDI file!")
            raise commands.CommandError("No valid MIDI file.")
            return

        soundfonts = ['megadrive', 'snes', 'n64']

        try:
            arg2 = int(arg1)
            arg1 = 'default'
        except ValueError:
            arg1 = arg1
            try:
                arg2 = int(arg2)
            except TypeError:
                arg2 = 22050
            except ValueError:
                await message.edit(content="❌ Not a valid sample rate!")
                raise commands.CommandError("No valid sample rate.")
                return

        if arg1 != None:
            try:
                k = soundfonts.index(arg1)
                arg1 = soundfonts[k]
            except ValueError:
                arg1 = 'default'

        if arg2 > 44100:
            arg2 = 44100
        if arg2 < 8000:
            arg2 = 8000

        print('Converting with {} soundfont @ {} Hz...'.format(arg1, arg2))

        await message.edit(content="♻️ Uploading...")
        midic.convert_midi_to_audio(link, arg1, arg2)
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
        await ctx.voice_client.disconnect()
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
                await ctx.send("▶️ Playing")
            else:
                await ctx.send("⏯️ Already paused")

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
    @pause.before_invoke
    @stop.before_invoke
    @resume.before_invoke
    async def ensure_channel(self, ctx):

        channel = discord.utils.get(ctx.message.guild.channels, name="midi-player")
        if ctx.message.channel != channel:
            raise commands.CommandError("{} typed in wrong channel.".format(ctx.message.author))
        else:
            if ctx.message.author.bot: raise commands.CommandError("Is a bot.")
            if ctx.message.author.id == client.user.id: raise commands.CommandError("It's a-me, Mario!")
    
    @play.before_invoke
    async def ensure_voice(self, ctx):

        channel = discord.utils.get(ctx.message.guild.channels, name="midi-player")
        if ctx.message.channel != channel:
            raise commands.CommandError("{} typed in wrong channel.".format(ctx.message.author))
        else:
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
async def on_guild_join(guild):
    print("MIDI Player joined the new lobby:", guild)
    channel = discord.utils.get(guild.channels, name="midi-player")
    if not channel:
        await guild.create_text_channel('midi-player')

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        return
    elif isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.CommandError):
        return print("Command error:", error)
    elif isinstance(error, commands.errors.BadArgument):
        return
    raise error

client.add_cog(MIDI_player(client))
client.run(TOKEN)