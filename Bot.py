################################
# MIT License                  #
# ---------------------------- #
# Copyright (c) 2020 Bluntano  #
################################

# All neccessary module imports here
import os
import json
import shutil # folder creatinon, deletion
import pymongo # for MongoDB

# Load variables from .env file
from dotenv import load_dotenv
load_dotenv(verbose=True)

# MIDIConverter.py
import MIDIConverter as midic

# Global cooldown time set
cooldown_time = 3
guilds_list = {} # player queues/dict for each Discord guild

# Get MongoDB variables (host and port)
MONGODB_HOST = os.getenv("MONGODB_HOST")
MONGODB_PORT = os.getenv("MONGODB_PORT")

# Database stuff here
db_client = pymongo.MongoClient(MONGODB_HOST, int(MONGODB_PORT))
dblist = db_client.list_database_names()
if not "guild_database" in dblist:
    db = db_client["guild_database"]
    guild_col = db["guilds"]
else:
    print("=== guild_database exists ===")
    guild_col = db_client["guild_database"]["guilds"]

# Asynchronous function for determing prefix for each Discord guild
async def determine_prefix(client, message):
    guild = message.guild
    prefix = guild_col.find_one({ "guild_id": guild.id }, { "prefix": 1, "_id": 0 })
    prefix = prefix['prefix']
    return prefix, 'midi.'

# Discord stuff here
TOKEN = os.getenv("DISCORD")
import discord
import asyncio
from discord.ext import commands
client = commands.Bot(command_prefix=determine_prefix) # determine each guild's bot prefix

# On bot logon
@client.event
async def on_ready():
    game = discord.Game("midi.help | MIDI Player")
    await client.change_presence(activity=game)

    # counts up all the guilds the bot is in
    for guild in client.guilds:
        guilds_list[guild.id] = {'name': guild.name, 'queue': []}
        
        # checks all the guilds in db's collection
        myquery = { "guild_id": guild.id }
        mydoc = guild_col.find_one(myquery)
        if not mydoc:
            guild_col.insert_one({"guild_id": guild.id, "prefix": "midi."})
    # for x in guild_col.find():
    #     print(x)
    print("MIDI Player Ready")

# On bot joining new guild
@client.event
async def on_guild_join(guild):
    print("MIDI Player joined the new lobby:", guild)
    # channel = discord.utils.get(guild.channels, name="midi-player")
    # if not channel:
    #     await guild.create_text_channel('midi-player')

    # inserts new guild to the db with default prefix
    # as well as creates new object for the guild in the queue dict
    guild_col.insert_one({"guild_id": guild.id, "prefix": "midi."})    
    guilds_list[guild.id] = {'name': guild.name, 'queue': []}

# On bot being removed from the guild
@client.event
async def on_guild_remove(guild):
    print("MIDI Player was removed/left the lobby:", guild)

    # deletes guild from the 
    del guilds_list[guild.id]
    guild_col.delete_one({"guild_id": guild.id})

# Error handling
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        return
    elif isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 You're missing permissions for that command!")
    elif isinstance(error, commands.CommandError):
        print("Command error:", error)

# This is for storing MIDI file info and the MIDI file itself on
# guild's directory
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

# Asynchronous function for playing music
async def play_music(ctx, skip_command=False):

    # checks the queue whether there is songs to play from queue
    # and removes them once they've played
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
            client.loop.create_task(ctx.voice_client.disconnect()) # disconnect after queue is empty
            client.loop.create_task(ctx.send(message))
            shutil.rmtree('guilds/{}/'.format(ctx.guild.id))
            guilds_list[ctx.guild.id]['queue'] = []
            raise commands.CommandError("{}'s queue is empty.".format(ctx.guild.id))

    # if there's tracks in the queue to play
    if len(guilds_list[ctx.guild.id]['queue']) != 0:
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
    
    # when <prefix>play is executed in the text channel
    if skip_command is False:
        if ctx.voice_client:
            if ctx.voice_client.is_playing():
                await ctx.send("▶️ Already playing!")
                raise commands.CommandError("Bot on guild with the id of {} already playing.".format(ctx.guild.id))

    # follows the same logic as in check_queue function
    # but is required for first time playing tracks
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

# MIDI Player (core of it)
class MIDI_player(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, cooldown_time, commands.BucketType.guild)
    async def convert(self, ctx, arg1=None, arg2=None):

        # if there's no files attached to the command
        if ctx.message.attachments == []:
            await ctx.send("❌ No MIDI file in the attachment!")
            return

        attached_file = ctx.message.attachments[0]
        link = attached_file.url
        name = attached_file.filename
        server_id = ctx.message.guild.id

        message = await ctx.send("⏳ Checking the file...")

        # checks whether the file is MIDI or not
        midic.detect_midi_file(link)
        if midic.detect_midi_file.is_midi == False:
            await message.edit(content="❌ Not a valid MIDI file!")
            raise commands.CommandError("No valid MIDI file.")

        # available sound fonts to use
        soundfonts = ['megadrive', 'snes', 'n64']

        # handling passed arguments in the command
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
        
        # checks what is passed as first argument in the command
        if arg1 != None:
            try:
                k = soundfonts.index(arg1)
                arg1 = soundfonts[k]
            except ValueError:
                arg1 = 'default'
        
        # sample rate check
        # min - 8000Hz
        # max - 44100Hz
        if arg2 > 44100:
            arg2 = 44100
        if arg2 < 8000:
            arg2 = 8000

        # adding file name and guild id to temporary JSON file
        # so the MIDI converter could process it through
        add_to_json(name, server_id).write_json_file()

        print('Converting with {} soundfont @ {} Hz...'.format(arg1, arg2))
        if arg1 != 'default':
            name = '{}-{}hz_{}'.format(arg1, arg2, name)
        else:
            name = '{}hz_{}'.format(arg2, name)

        await message.edit(content="♻️ Converting...")

        # converting process, "front-end"
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

        # executes play_music command
        await play_music(ctx)

    @commands.command()
    @commands.cooldown(1, cooldown_time, commands.BucketType.guild)
    async def stop(self, ctx):
        guild = ctx.message.guild.id

        # empties the queue
        guilds_list[guild]['queue'] = []

        # stops bot playing, deletes guild's directory in guilds dir
        # disconnects from the voice channel
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

        # skips the song, executes play_music function as being skipped
        ctx.voice_client.stop()
        await asyncio.sleep(0.5)
        await play_music(ctx, True)
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx, prefix=None):

        # for updating guild's bot prefix if wanted
        # requires admin priviledge on the guild
        server_id = ctx.message.guild.id
        pfx = guild_col.find_one({ "guild_id": server_id }, { "prefix": 1, "_id": 0 })
        pfx = pfx['prefix']
        if not prefix:
            await ctx.send(f"❌ Please enter your prefix, like this: `{pfx}prefix <your custom prefix>`")
            raise commands.CommandError("No prefix entered.")
        
        guild_col.update_one({ "guild_id": server_id }, { "$set": { "prefix": prefix }})
        await ctx.send(f"✅ Updated this server's prefix to `{prefix}`")

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
        "{pfx}convert <sound font and/or sample rate[optional]>",
        "{pfx}play",
        "{pfx}stop",
        "{pfx}pause",
        "{pfx}resume",
        "{pfx}skip",
        "{pfx}queue",
        "{pfx}soundfonts",
        "{pfx}prefix <custom prefix>"
        ]

        pfx = guild_col.find_one({ "guild_id": ctx.message.guild.id }, { "prefix": 1, "_id": 0 })
        pfx = pfx['prefix']

        message = "***Commands:***\n"
        message += "```\n"
        for i in cmds:
            message += "{}\n".format(i.format(pfx=pfx))
        message += "```"
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
        message += "```\n"
        for i in sfs:
            message += "{}\n".format(i)
        message += "```"
        await ctx.send(message)

    @convert.before_invoke
    @pause.before_invoke
    @stop.before_invoke
    @resume.before_invoke
    @play.before_invoke
    @skip.before_invoke
    @queue.before_invoke
    async def ensure_everything(self, ctx):

        # channel = discord.utils.get(ctx.message.guild.channels, name="midi-player")
        # if ctx.message.channel != channel:
        #     raise commands.CommandError("{} typed in wrong channel.".format(ctx.message.author))
        # else:

        # ensures everything needed like:
        # - if bot received from other bot
        # - if the bot itself messaged
        # - if bot is already connected to voice channel
        # - if user executing commands is in the voice channel
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
    @prefix.before_invoke
    async def ensure_channel(self, ctx):
        # channel = discord.utils.get(ctx.message.guild.channels, name="midi-player")
        # if ctx.message.channel != channel:
        #     raise commands.CommandError("{} typed in wrong channel.".format(ctx.message.author))
        # else:

        # ensures that other bot hasn't typed out the command or
        # if it was this bot who typed the command
        if ctx.message.author.bot: raise commands.CommandError("Is a bot.")
        if ctx.message.author.id == client.user.id: raise commands.CommandError("It's a-me, Mario!")

client.remove_command("help") # for custom help command
client.add_cog(MIDI_player(client)) # add MIDI Player commands and its ensuring tools to the bot
client.run(TOKEN) # run the bot