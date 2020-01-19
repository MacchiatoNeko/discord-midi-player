import os
import json
import shutil

from dotenv import load_dotenv
load_dotenv(verbose=True)

TOKEN = os.getenv("DISCORD")
import discord
import asyncio
from discord.ext import commands
client = commands.Bot(command_prefix = "!")

import MIDIConverter as midic

cooldown_time = 3
guilds_list = {}

class MIDI_player(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, cooldown_time, commands.BucketType.guild)
    async def convert(self, ctx, arg1=None, arg2=None):
        if ctx.message.attachments == []:
            message = await ctx.send("❌ No MIDI file in the attachment!")
            return

        attached_file = ctx.message.attachments[0]
        link = attached_file.url
        name = attached_file.filename
        server_id = ctx.message.guild.id

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
        except TypeError:
            arg1 = 'default'
            arg2 = 22050

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

        add_to_json(name, server_id).write_json_file()

        print('Converting with {} soundfont @ {} Hz...'.format(arg1, arg2))

        await message.edit(content="♻️ Uploading...")
        midic.convert_midi_to_audio(link, arg1, arg2, server_id, name)
        while True:
            is_uploaded = midic.convert_midi_to_audio.is_converted
            if not is_uploaded:
                error = midic.convert_midi_to_audio.error
                await message.edit(content="❗ Uploading failed:\n`{}`".format(error))
                break
            else:
                await message.edit(content="✅ MIDI file converted!")
                guilds_list[server_id]['queue'].append(name)
                break

    @commands.command()
    @commands.cooldown(1, cooldown_time, commands.BucketType.guild)
    async def play(self, ctx):
        server = ctx.message.guild.id

        def after_playing(err):
            if len(guilds_list[server]['queue']) > 0:
                guilds_list[server]['queue'].pop(0)
                next_song = guilds_list[server]['queue'][0]
                source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('guilds/{}/{}.wav'.format(server, next_song)))
                ctx.voice_client.play(source, after=after_playing)

        try:
            current = guilds_list[server]['queue'][0]
            audio_source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('guilds/{}/{}.wav'.format(server, current)))
            await ctx.send("▶️ Now Playing: `{}`".format(current))
            ctx.voice_client.play(audio_source, after=after_playing)
        except IndexError:
            await ctx.send("⏹️ Queue is empty")

    @commands.command()
    @commands.cooldown(1, cooldown_time, commands.BucketType.guild)
    async def stop(self, ctx):
        guild = ctx.message.guild.id
        ctx.voice_client.stop()
        await ctx.send("⏹️ Stopped")
        shutil.rmtree('guilds/{}/'.format(guild))
        await ctx.voice_client.disconnect()
        guilds_list[guild]['queue'] = []

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
    
    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def skip(self, ctx):
        server = ctx.message.guild.id

        def after_playing(err):
            if len(guilds_list[server]['queue']) > 0:
                guilds_list[server]['queue'].pop(0)
                next_song = guilds_list[server]['queue'][0]
                source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('guilds/{}/{}.wav'.format(server, next_song)))
                ctx.voice_client.play(source, after=after_playing)

        try:
            ctx.voice_client.stop()
            guilds_list[server]['queue'].pop(0)
            next_song = guilds_list[server]['queue'][0]
            message = "▶️ Now Playing: `{}`".format(next_song)
            audio_source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('guilds/{}/{}.wav'.format(server, next_song)))
            ctx.voice_client.play(audio_source, after=after_playing)
        except IndexError:
            message = "⏹️ Queue is empty"
        await ctx.send(message)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def queue(self, ctx):
        server = ctx.message.guild.id
        if guilds_list[server]['queue'] == []:
            message = "⏹️ Queue is empty"
        else:
            counter = 1
            message = "***Queue:***\n"
            for i in guilds_list[server]['queue']:
                message += "{}. *{}*\n".format(counter, i)
                counter += 1
        await ctx.send(message)

    @convert.before_invoke
    @pause.before_invoke
    @stop.before_invoke
    @resume.before_invoke
    @play.before_invoke
    @skip.before_invoke
    async def ensure_voice(self, ctx):

        channel = discord.utils.get(ctx.message.guild.channels, name="midi-player")
        if ctx.message.channel != channel:
            raise commands.CommandError("{} typed in wrong channel.".format(ctx.message.author))
        else:
            if ctx.message.author.bot: raise commands.CommandError("Is a bot.")
            if ctx.message.author.id == client.user.id: raise commands.CommandError("It's a-me, Mario!")
            if ctx.voice_client is None:
                if ctx.author.voice:
                    await ctx.author.voice.channel.connect()
                else:
                    await ctx.send("🚫 You are not connected to a voice channel!")
                    raise commands.CommandError("{} is not connected to voice channel.".format(ctx.message.author))
            else:
                if not ctx.author.voice:
                    await ctx.send("🚫 You are not connected to a voice channel!")
                    raise commands.CommandError("{} is not connected to voice channel.".format(ctx.message.author))
                if ctx.author.voice.channel != ctx.voice_client.channel:
                    await ctx.send("🚫 Already connected to another voice channel. Sorry!")
                    raise commands.CommandError("Already connected to voice channel.")

@client.event
async def on_ready():
    game = discord.Game("MIDI Player v1.42")
    await client.change_presence(activity=game)
    for guild in client.guilds:
        guilds_list[guild.id] = {'queue': []}
    print("MIDI Player Ready")

@client.event
async def on_guild_join(guild):
    print("MIDI Player joined the new lobby:", guild)
    channel = discord.utils.get(guild.channels, name="midi-player")
    if not channel:
        await guild.create_text_channel('midi-player')
    guilds_list[guild.id]['queue'] = []

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        return
    elif isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.CommandError):
        print("Command error:", error)
        raise error

class add_to_json:
    def __init__(self, name, id):
        self.name = name
        self.id = id
    
    def write_json_file(self):
        try:
            os.makedirs("guilds/{}/".format(self.id))
        except FileExistsError:
            pass

        conv_dict = {'guild_id': self.id, 'filename': self.name}
        with open('guilds/{}/info.json'.format(self.id), 'w') as json_file:
            json.dump(conv_dict, json_file)
        return

client.add_cog(MIDI_player(client))
client.run(TOKEN)