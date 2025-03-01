import logging
from urllib.parse import urlparse, parse_qs
import yt_dlp

def validate_youtube_url(url):
    """Validate if the given URL is a valid YouTube URL"""
    try:
        parsed_url = urlparse(url)
        if 'youtube.com' in parsed_url.netloc or 'youtu.be' in parsed_url.netloc:
            # Extract video ID
            if 'youtube.com' in parsed_url.netloc:
                query = parse_qs(parsed_url.query)
                video_id = query.get('v', [None])[0]
            else:  # youtu.be
                video_id = parsed_url.path[1:]

            if video_id and len(video_id) == 11:
                return True, video_id
    except Exception as e:
        logging.error(f"URL validation error: {str(e)}")
    return False, None

def get_video_info(url):
    """Get video information from YouTube URL using yt-dlp"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if not info:
                raise Exception("Could not fetch video information")

            return {
                'title': info.get('title', 'Untitled Video'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration', 0),
                'author': info.get('uploader', 'Unknown Author'),
                'views': info.get('view_count', 0),
                'video_id': info.get('id')
            }

    except Exception as e:
        logging.error(f"Error in get_video_info: {str(e)}")
        raise Exception("Could not fetch video information. Please verify the video URL and try again.")