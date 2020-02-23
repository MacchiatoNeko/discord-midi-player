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

cooldown_time = 3
guilds_list = {}

async def play_music(ctx, skip_command=False):

    def check_queue(error):
        if len(guilds_list[ctx.guild.id]['queue']) > 0:
            player = guilds_list[ctx.guild.id]['queue'][0]
            audio_source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('guilds/{}/{}.wav'.format(ctx.guild.id, player)))
            ctx.voice_client.play(audio_source, after=check_queue)
            message = "▶️ Now Playing: `{}`".format(player)
            try:
                up_next = guilds_list[ctx.guild.id]['queue'][1]
                message += "\n\n⏭️ Up next: `{}`".format(up_next)
            except IndexError:
                pass
            try:
                guilds_list[ctx.guild.id]['queue'].pop(0)
            except IndexError:
                pass
            client.loop.create_task(ctx.send(message))
        else:
            message = "⏹️ Queue is empty"
            client.loop.create_task(ctx.send(message))
            shutil.rmtree('guilds/{}/'.format(ctx.guild.id))
            guilds_list[ctx.guild.id]['queue'] = []
            raise commands.CommandError("{}'s queue is empty.".format(ctx.guild.id))

    if len(guilds_list[ctx.guild.id]['queue']) != 0:
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
    
    if skip_command is False:
        if ctx.voice_client:
            if ctx.voice_client.is_playing():
                await ctx.send("▶️ Already playing!")
                raise commands.CommandError("Bot on guild with the id of {} already playing.")

    if len(guilds_list[ctx.guild.id]['queue']) > 0:
        current = guilds_list[ctx.guild.id]['queue'][0]
        audio_source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('guilds/{}/{}.wav'.format(ctx.guild.id, current)))
        ctx.voice_client.play(audio_source, after=check_queue)

        message = "▶️ Now Playing: `{}`".format(current)
        try:
            up_next = guilds_list[ctx.guild.id]['queue'][1]
            message += "\n\n⏭️ Up next: `{}`".format(up_next)
        except IndexError:
            pass

        try:
            guilds_list[ctx.guild.id]['queue'].pop(0)
        except IndexError:
            pass

        await ctx.send(message)
    else:
        if skip_command is False:
            await ctx.send("⏹️ Queue is empty. You should add something first!")

class MIDI_player(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, cooldown_time, commands.BucketType.guild)
    async def convert(self, ctx, arg1=None, arg2=None):
        if ctx.message.attachments == []:
            await ctx.send("❌ No MIDI file in the attachment!")
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

        soundfonts = ['megadrive', 'snes', 'n64']

        try:
            arg2 = int(arg1)
            arg1 = 'default'
        except ValueError:
            try:
                arg2 = int(arg2)
            except TypeError:
                arg2 = 22050
            except ValueError:
                await message.edit(content="❌ Not a valid sample rate!")
                raise commands.CommandError("No valid sample rate.")
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
        if arg1 != 'default':
            name = '{}-{}hz_{}'.format(arg1, arg2, name)
        else:
            name = '{}hz_{}'.format(arg2, name)

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
        await play_music(ctx)

    @commands.command()
    @commands.cooldown(1, cooldown_time, commands.BucketType.guild)
    async def stop(self, ctx):
        guild = ctx.message.guild.id

        guilds_list[guild]['queue'] = []

        ctx.voice_client.stop()
        await ctx.send("⏹️ Stopped")
        try:
            shutil.rmtree('guilds/{}/'.format(guild))
        except FileNotFoundError:
            pass
        await ctx.voice_client.disconnect()

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
        ctx.voice_client.stop()
        await asyncio.sleep(0.5)
        await play_music(ctx, True)

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

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def help(self, ctx):
        cmds = [
        "!convert <sound font and/or sample rate[optional]>",
        "!play",
        "!stop",
        "!pause",
        "!resume",
        "!skip",
        "!queue",
        "!soundfonts"
        ]
        message = "***Commands:***\n"
        for i in cmds:
            message += "{}\n".format(i)
        await ctx.send(message)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def soundfonts(self, ctx):
        sfs = [
        "default <when nothing is passed> (**GeneralUser GS**)",
        "megadrive (**Sega Genesis**)",
        "n64 (**Nintendo 64**)",
        "snes (**Super Nintendo**)"
        ]
        message = "***Sound fonts:***\n"
        for i in sfs:
            message += "{}\n".format(i)
        await ctx.send(message)

    @convert.before_invoke
    @pause.before_invoke
    @stop.before_invoke
    @resume.before_invoke
    @play.before_invoke
    @skip.before_invoke
    @queue.before_invoke
    async def ensure_everything(self, ctx):

        channel = discord.utils.get(ctx.message.guild.channels, name="midi-player")
        if ctx.message.channel != channel:
            raise commands.CommandError("{} typed in wrong channel.".format(ctx.message.author))
        else:
            if ctx.message.author.bot: raise commands.CommandError("Is a bot.")
            if ctx.message.author.id == client.user.id: raise commands.CommandError("It's a-me, Mario!")
            if ctx.voice_client is None:
                if not ctx.author.voice:
                    await ctx.send("🚫 You are not connected to a voice channel!")
                    raise commands.CommandError("{} is not connected to voice channel.".format(ctx.message.author))
            else:
                if not ctx.author.voice:
                    await ctx.send("🚫 You are not connected to a voice channel!")
                    raise commands.CommandError("{} is not connected to voice channel.".format(ctx.message.author))
                if ctx.author.voice.channel != ctx.voice_client.channel:
                    await ctx.send("🚫 Already connected to another voice channel. Sorry!")
                    raise commands.CommandError("Already connected to voice channel.")

    @help.before_invoke
    @soundfonts.before_invoke
    async def ensure_channel(self, ctx):
        channel = discord.utils.get(ctx.message.guild.channels, name="midi-player")
        if ctx.message.channel != channel:
            raise commands.CommandError("{} typed in wrong channel.".format(ctx.message.author))
        else:
            if ctx.message.author.bot: raise commands.CommandError("Is a bot.")
            if ctx.message.author.id == client.user.id: raise commands.CommandError("It's a-me, Mario!")

@client.event
async def on_ready():
    game = discord.Game("MIDIs (v1.69-lol)")
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

client.remove_command("help")
client.add_cog(MIDI_player(client))
client.run(TOKEN)