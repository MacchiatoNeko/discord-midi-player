# Web server stuff here
from flask import Flask, redirect # redirect for Discord bot invite link (non-permanent solution for now)
from threading import Thread
import os
from dotenv import load_dotenv # for .env file
app = Flask(__name__)
load_dotenv(verbose=True)

client_userid = 0
flask_host = os.getenv("FLASK_HOST")

@app.errorhandler(404)
def not_found(e):
    return "4 + 0 = 4", 404

@app.route("/")
def hello():
    return redirect(f"https://discordapp.com/oauth2/authorize?client_id={client_userid}&permissions=3147776&scope=bot")

# Start up web server
def run_webserver():
    app.run(host=flask_host, port=80)

# Creates a thread
def keep_alive():
    t = Thread(target=run_webserver)
    t.start()
