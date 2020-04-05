################################
# MIT License                  #
# ---------------------------- #
# Copyright (c) 2020 Bluntano  #
################################

# All neccessary module imports here
import shutil # folder creatinon, deletion
import pymongo # for MongoDB

# MIDIConverter.py
from MIDIConverter import MIDIConverter

# Common functions and exceptions
from Common import *

guilds_list = {} # player queues/dict for each Discord guild

# Web server stuff here
from flask import Flask, redirect
from threading import Thread
app = Flask(__name__)

@app.route("/")
def hello():
    return redirect(f"https://discordapp.com/oauth2/authorize?client_id={client.user.id}&permissions=3147776&scope=bot")

def run_webserver():
    app.run(host='0.0.0.0', port=80)

def keep_alive():
    t = Thread(target=run_webserver)
    t.start()

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
import discord
import asyncio
from discord.ext import commands
client = commands.Bot(command_prefix=determine_prefix) # determine each guild's bot prefix

# Status changer task
# Changes the status every 30 seconds
async def status_task():
    while True:
        statuses = [
        "MIDI Player",
        f"Serving {guild_col.estimated_document_count()} servers",
        "Play your MIDIs today!",
        ]
        for i in statuses:
            status = discord.Game(f"midi.help | {i}")
            await client.change_presence(activity=status)
            await asyncio.sleep(15)

# On bot logon
@client.event
async def on_ready():
    # game = discord.Game("midi.help | MIDI Player")
    # await client.change_presence(activity=game)
    # counts up all the guilds the bot is in
    for guild in client.guilds:
        guilds_list[guild.id] = {'name': guild.name, 'queue': []}
        
        # checks all the guilds in db's collection
        myquery = { "guild_id": guild.id }
        mydoc = guild_col.find_one(myquery)
        if not mydoc:
            guild_col.insert_one({"guild_id": guild.id, "guild_name": guild.name, "prefix": "midi."})
    print("MIDI Player Ready")
    client.loop.create_task(status_task())
    keep_alive()

# On bot joining new guild
@client.event
async def on_guild_join(guild):
    print("MIDI Player joined the new lobby:", guild)

    # inserts new guild to the db with default prefix
    # as well as creates new object for the guild in the queue dict
    guild_col.insert_one({"guild_id": guild.id, "guild_name": guild.name, "prefix": "midi."})    
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

        if arg1 != 'default':
            name = f'{arg1}-{arg2}hz_{name}'
        else:
            name = f'{arg2}hz_{name}'
        
        # checks whether the file is MIDI or not
        midic = MIDIConverter(link, arg1, arg2, server_id, name)
        try:
            midic.is_midi_file()
        except NotMIDIFileError:
            await message.edit(content="❌ Not a valid MIDI file!")
            raise commands.CommandError("No valid MIDI file.")

        # adding file name and guild id to temporary JSON file
        # so the MIDI converter could process it through
        add_to_json(name, server_id).write_json_file()

        print(f'Converting with {arg1} soundfont @ {arg2} Hz...')
        await message.edit(content="♻️ Converting...")

        # converting process, "front-end"
        try:
            midic.convert_midi_to_audio()
            await message.edit(content="✅ MIDI file converted!")
            guilds_list[server_id]['queue'].append(name)
        except ConversionError as e:
            await message.edit(content=f"❗ Converting failed:\n||`{e}`||")

    @commands.command()
    @commands.cooldown(1, cooldown_time, commands.BucketType.guild)
    async def play(self, ctx):

        # executes play_music command
        await play_music(ctx)

    @commands.command()
    @commands.cooldown(1, cooldown_time, commands.BucketType.guild)
    async def stop(self, ctx):
        guild = ctx.message.guild.id

        # stops bot playing, deletes guild's directory in guilds dir
        # disconnects from the voice channel
        try:
            ctx.voice_client.stop()
            await ctx.send("⏹️ Stopped")
            try:
                shutil.rmtree(f'guilds/{guild}/')
            except FileNotFoundError:
                pass

            # empties the queue
            guilds_list[guild]['queue'] = []

            await ctx.voice_client.disconnect()
        except AttributeError:
            #await ctx.send("⏹️ There is nothing to stop")
            pass

    @commands.command()
    @commands.cooldown(1, cooldown_time, commands.BucketType.guild)
    async def pause(self, ctx):

        try:
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
        except AttributeError:  
            await ctx.send("⏹️ There is nothing to pause")

    @commands.command()
    @commands.cooldown(1, cooldown_time, commands.BucketType.guild)
    async def resume(self, ctx):

        try:
            paused = ctx.voice_client.is_paused()
            if paused == True:
                ctx.voice_client.resume()
                await ctx.send("▶️ Resuming")
            else:
                await ctx.send("⏯️ Already playing")
        except AttributeError:
            await ctx.send("⏹️ There is nothing to resume")
    
    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def skip(self, ctx):

        # skips the song, executes play_music function as being skipped
        try:
            ctx.voice_client.stop()
            await asyncio.sleep(0.5)
            await play_music(ctx, True)
        except AttributeError:
            await ctx.send("⏹️ There is nothing to skip")
    
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
        if len(prefix) > 6:
            await ctx.send(f"❌ Prefix cannot be longer than 6 characters")
            raise commands.CommandError("Prefix too long.")
        
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
                message += f"{counter}. *{i}*\n"
                counter += 1
        await ctx.send(message)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def help(self, ctx):

        pfx = guild_col.find_one({ "guild_id": ctx.message.guild.id }, { "prefix": 1, "_id": 0 })
        pfx = pfx['prefix']

        cmds = [
        f"{pfx}convert <sound font and/or sample rate[optional]>",
        f"{pfx}play",
        f"{pfx}stop",
        f"{pfx}pause",
        f"{pfx}resume",
        f"{pfx}skip",
        f"{pfx}queue",
        f"{pfx}soundfonts",
        f"{pfx}prefix <custom prefix>"
        ]

        message = "***Commands:***\n"
        message += "```\n"
        for i in cmds:
            message += f"{i}\n"
        message += "```"
        await ctx.send(message)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def soundfonts(self, ctx):
        message = "***Sound fonts:***\n"
        message += "```\n"
        for i in soundfonts:
            message += f"{i}\n"
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
                raise commands.CommandError(f"{ctx.message.author} is not connected to voice channel.")
        else:
            if not ctx.author.voice:
                await ctx.send("🚫 You are not connected to a voice channel!")
                raise commands.CommandError(f"{ctx.message.author} is not connected to voice channel.")
            if ctx.author.voice.channel != ctx.voice_client.channel:
                await ctx.send("🚫 Already connected to another voice channel. Sorry!")
                raise commands.CommandError("Already connected to voice channel.")

    @help.before_invoke
    @soundfonts.before_invoke
    @prefix.before_invoke
    async def ensure_channel(self, ctx):

        # ensures that other bot hasn't typed out the command or
        # if it was this bot who typed the command
        if ctx.message.author.bot: raise commands.CommandError("Is a bot.")
        if ctx.message.author.id == client.user.id: raise commands.CommandError("It's a-me, Mario!")

client.remove_command("help") # for custom help command
client.add_cog(MIDI_player(client)) # add MIDI Player commands and its ensuring tools to the bot
client.run(TOKEN) # run the bot