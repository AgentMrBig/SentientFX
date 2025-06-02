from flask import Flask, send_from_directory, send_file
import os

app = Flask(__name__)

# Serve frontend files (HTML, JS, CSS)
@app.route('/')
def serve_html():
    return send_from_directory('.', 'chart_renderer.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@app.route('/data/<path:filename>')
def serve_data(filename):
    return send_from_directory('../data', filename)


# ✅ Serve live MT4 ticks.csv
@app.route('/data/ticks.csv')
def serve_live_ticks():
    # Update this path to match your real one if it changes
    ticks_path = os.path.expanduser(
        r"C:\Users\PcTech\AppData\Roaming\MetaQuotes\Terminal\25647ED30FD793D6866C7F0E90C511F1\MQL4\Files\ticks.csv"
    )
    return send_file(ticks_path, mimetype='text/csv')

if __name__ == '__main__':
    app.run(port=8080)
