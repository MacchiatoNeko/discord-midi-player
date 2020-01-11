from threading import Thread
from flask import Flask, send_file
app = Flask(__name__)

@app.route("/<path>")
def main(path=None):
    if path is None:
        self.Error(400)
    try:
        return send_file(path, as_attachment=True)
    except Exception as e:
        self.log.exception(e)
        self.Error(400)

def run_file_server():
    app.run(host='0.0.0.0', port=8892)

def run_it():
    server = Thread(target=run_file_server)
    server.start()