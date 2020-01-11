from threading import Thread
from flask import Flask, send_file, jsonify
app = Flask(__name__)

@app.route("/<path>")
def main(path=None):
    try:
        return send_file(path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)})

def run_file_server():
    app.run(host='0.0.0.0', port=80)

def run_it():
    server = Thread(target=run_file_server)
    server.start()