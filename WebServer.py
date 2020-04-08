# Web server stuff here
from flask import Flask, redirect # redirect for Discord bot invite link (non-permanent solution for now)
from threading import Thread
app = Flask(__name__)

client_userid = 0

@app.route("/")
def hello():
    return redirect(f"https://discordapp.com/oauth2/authorize?client_id={client_userid}&permissions=3147776&scope=bot")

# Start up web server
def run_webserver():
    app.run(host='0.0.0.0', port=80)

# Creates a thread
def keep_alive():
    t = Thread(target=run_webserver)
    t.start()