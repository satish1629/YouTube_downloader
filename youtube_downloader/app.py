import os
import logging
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
from utils import validate_youtube_url, get_video_info
import threading

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "youtube-downloader-secret"

# Global dictionary to store download progress
download_progress = {}

def progress_hook(d):
    """Callback function to track download progress"""
    if d['status'] == 'downloading':
        try:
            total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total:
                percentage = (downloaded / total) * 100
                video_id = d['info_dict']['id']
                download_progress[video_id] = percentage
                logging.debug(f"Download progress for {video_id}: {percentage:.2f}%")
        except Exception as e:
            logging.error(f"Error updating progress: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-video-info', methods=['POST'])
def get_video_details():
    url = request.form.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        is_valid, _ = validate_youtube_url(url)
        if not is_valid:
            return jsonify({'error': 'Invalid YouTube URL'}), 400

        video_info = get_video_info(url)
        return jsonify(video_info)
    except Exception as e:
        error_msg = str(e)
        logging.error(f"Error getting video info: {error_msg}")
        return jsonify({'error': error_msg}), 500

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')
    quality = request.form.get('quality', 'high')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        is_valid, video_id = validate_youtube_url(url)
        if not is_valid:
            return jsonify({'error': 'Invalid YouTube URL'}), 400

        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]' if quality == 'high' else 'worst[ext=mp4]',
            'outtmpl': os.path.join('downloads', '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warnings': True
        }

        # Start download in a separate thread
        def download_thread():
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except Exception as e:
                logging.error(f"Download error: {str(e)}")
                download_progress[video_id] = -1

        thread = threading.Thread(target=download_thread)
        thread.start()

        return jsonify({
            'video_id': video_id,
            'message': 'Download started'
        })

    except Exception as e:
        error_msg = str(e)
        logging.error(f"Error downloading video: {error_msg}")
        return jsonify({'error': error_msg}), 500

@app.route('/progress/<video_id>')
def get_progress(video_id):
    return jsonify({'progress': download_progress.get(video_id, 0)})

# Ensure downloads directory exists
if not os.path.exists('downloads'):
    os.makedirs('downloads')