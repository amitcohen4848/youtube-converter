from flask import Flask, request, send_file, render_template, send_from_directory
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from io import BytesIO
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
    search_text = request.form.get("name")  # The song name the user entered
    buffer = BytesIO()

    try:
        # Search for the song on YouTube
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'temp_audio.%(ext)s',
            'quiet': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{search_text}", download=True)
            # If multiple search results, yt-dlp returns a dict with a 'entries' list
            if 'entries' in info:
                info = info['entries'][0]  # Take the first search result
            filename = ydl.prepare_filename(info)

        # Read the file into memory
        with open(filename, 'rb') as f:
            buffer.write(f.read())
        buffer.seek(0)

        # Use video title as download name
        title = info.get('title', 'audio').replace('/', '_')  # Avoid slash in file names
        download_name = f"{title}.mp3"

    except DownloadError:
        return "Failed to download the video.", 500

    finally:
        # Delete temp file
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)

    return send_file(buffer, as_attachment=True, download_name=download_name, mimetype='audio/mpeg')

if __name__ == '__main__':
    app.run()
