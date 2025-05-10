#!/usr/bin/env python3

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import logging
from ytmusicapi import YTMusic

load_dotenv()

# Constants
VOLUME_STEP_PERCENT = 2  # Volume change step size in percent
API_BASE_URL = os.getenv('YTM_API_BASE_URL', 'http://localhost:8080')
API_TOKEN = os.getenv('YTM_API_TOKEN')

# Configure logging - only show INFO and above
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Reduce noise from other loggers
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('werkzeug').setLevel(logging.WARNING)

app = Flask(__name__, static_folder='static')
CORS(app)

# Initialize YTMusic
ytmusic = YTMusic()

def get_headers():
    return {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search_songs():
    query = request.json.get('query')
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    logger.info(f"Searching for query: {query}")
    
    try:
        # Search for both songs and videos like in song.py
        search_results_music = ytmusic.search(query, filter="songs")
        search_results_video = ytmusic.search(query, filter="videos")
        
        # Combine and format results
        results = []
        for song in search_results_music + search_results_video:
            song_data = {
                'title': song.get('title', '?'),
                'artist': song.get('artists', [{'name': '?'}])[0].get('name', '?'),
                'album': song.get('album', {}).get('name', '?'),
                'videoId': song.get('videoId'),
                'imageSrc': song.get('thumbnails', [{}])[-1].get('url') if song.get('thumbnails') else None
            }
            results.append(song_data)
        
        logger.info(f"Found {len(results)} results")
        return jsonify(results)
            
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/queue', methods=['GET'])
def get_queue():
    try:
        # Get current song first
        current_response = requests.get(
            f'{API_BASE_URL}/api/v1/song',
            headers=get_headers()
        )
        current_song = None
        current_video_id = None
        if current_response.status_code == 200:
            current_song = current_response.json()
            current_video_id = current_song.get('videoId')

        # Get queue
        response = requests.get(
            f'{API_BASE_URL}/api/v1/queue',
            headers=get_headers()
        )
        
        if response.status_code == 204:
            return jsonify([])
            
        if response.status_code != 200:
            logger.error(f"Failed to get queue: {response.text}")
            return jsonify({'error': f'Failed to get queue: {response.text}'}), response.status_code
            
        queue_data = response.json()
        
        # Extract songs from the items array
        formatted_queue = []
        found_current = False
        
        # First find the index of the most recent occurrence of the current song
        current_index = -1
        for i, item in enumerate(queue_data.get('items', [])):
            if 'playlistPanelVideoRenderer' in item:
                video_id = item['playlistPanelVideoRenderer'].get('videoId')
                if video_id == current_video_id:
                    current_index = i
        
        # If we found the current song, only include songs after it
        if current_index != -1:
            for item in queue_data.get('items', [])[current_index + 1:]:
                if 'playlistPanelVideoRenderer' in item:
                    song = item['playlistPanelVideoRenderer']
                    video_id = song.get('videoId')
                    
                    # Get the highest quality thumbnail
                    thumbnails = song.get('thumbnail', {}).get('thumbnails', [])
                    image_url = thumbnails[-1].get('url') if thumbnails else None
                    
                    song_data = {
                        'title': song.get('title', {}).get('runs', [{}])[0].get('text', '?'),
                        'artist': song.get('longBylineText', {}).get('runs', [{}])[0].get('text', '?'),
                        'album': next((run.get('text', '?') for run in song.get('longBylineText', {}).get('runs', []) 
                                    if 'navigationEndpoint' in run and 'browseEndpoint' in run.get('navigationEndpoint', {})
                                    and run.get('navigationEndpoint', {}).get('browseEndpoint', {}).get('browseEndpointContextSupportedConfigs', {})
                                    .get('browseEndpointContextMusicConfig', {}).get('pageType') == 'MUSIC_PAGE_TYPE_ALBUM'), '?'),
                        'videoId': video_id,
                        'imageSrc': image_url
                    }
                    formatted_queue.append(song_data)
        
        return jsonify(formatted_queue)
    except Exception as e:
        logger.error(f"Error getting queue: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/queue', methods=['POST'])
def add_to_queue():
    video_id = request.json.get('videoId')
    if not video_id:
        return jsonify({'error': 'videoId is required'}), 400
    
    try:
        # Get song info for logging
        song_info = "unknown song"
        try:
            search_results = ytmusic.search(video_id, filter="songs")
            if search_results:
                song = search_results[0]
                song_info = f"{song.get('title', '?')} by {song.get('artists', [{'name': '?'}])[0].get('name', '?')}"
        except Exception as e:
            logger.warning(f"Could not get song info for logging: {str(e)}")

        response = requests.post(
            f'{API_BASE_URL}/api/v1/queue',
            headers=get_headers(),
            json={
                'videoId': video_id,
                'insertPosition': 'INSERT_AFTER_CURRENT_VIDEO'
            }
        )
        if response.status_code == 204:
            logger.info(f"Added to queue: {song_info}")
        else:
            logger.error(f"Failed to add song to queue: {response.text}")
        return '', response.status_code
    except Exception as e:
        logger.error(f"Error adding to queue: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/current-song', methods=['GET'])
def get_current_song():
    try:
        response = requests.get(
            f'{API_BASE_URL}/api/v1/song',
            headers=get_headers()
        )
        
        if response.status_code == 204:
            return '', 204
            
        if response.status_code != 200:
            logger.error(f"Failed to get current song: {response.text}")
            return jsonify({'error': f'Failed to get current song: {response.text}'}), response.status_code
            
        song_data = response.json()
        
        # Log the new song if it's different from the last one
        if not hasattr(get_current_song, 'last_video_id'):
            get_current_song.last_video_id = None
            
        current_video_id = song_data.get('videoId')
        if current_video_id != get_current_song.last_video_id:
            song_info = f"{song_data.get('title', '?')} by {song_data.get('artist', '?')}"
            logger.info(f"Now playing: {song_info}")
                        
            get_current_song.last_video_id = current_video_id
        
        # Format the song data
        formatted_song = {
            'title': song_data.get('title', '?'),
            'artist': song_data.get('artist', '?'),
            'album': song_data.get('album', '?'),
            'videoId': song_data.get('videoId'),
            'imageSrc': song_data.get('imageSrc'),  # Use imageSrc directly from the API response
            'isPaused': song_data.get('isPaused', True)  # Default to True (paused) if not specified
        }
        
        return jsonify(formatted_song)
    except Exception as e:
        logger.error(f"Error getting current song: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/play-pause', methods=['POST'])
def toggle_play_pause():
    try:
        # Get current song info for logging
        current_response = requests.get(
            f'{API_BASE_URL}/api/v1/song',
            headers=get_headers()
        )
        song_info = "unknown song"
        if current_response.status_code == 200:
            song_data = current_response.json()
            song_info = f"{song_data.get('title', '?')} by {song_data.get('artist', '?')}"

        response = requests.post(
            f'{API_BASE_URL}/api/v1/toggle-play',
            headers=get_headers()
        )
        if response.status_code == 204:
            logger.info(f"Toggled play/pause for: {song_info}")
        else:
            logger.error(f"Failed to toggle play/pause: {response.text}")
        return '', response.status_code
    except Exception as e:
        logger.error(f"Error toggling play/pause: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/next', methods=['POST'])
def next_song():
    try:
        # Get current song info for logging
        current_response = requests.get(
            f'{API_BASE_URL}/api/v1/song',
            headers=get_headers()
        )
        song_info = "unknown song"
        if current_response.status_code == 200:
            song_data = current_response.json()
            song_info = f"{song_data.get('title', '?')} by {song_data.get('artist', '?')}"

        response = requests.post(
            f'{API_BASE_URL}/api/v1/next',
            headers=get_headers()
        )
        if response.status_code == 204:
            logger.info(f"Skipped: {song_info}")
        else:
            logger.error(f"Failed to skip song: {response.text}")
        return '', response.status_code
    except Exception as e:
        logger.error(f"Error skipping to next song: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/previous', methods=['POST'])
def previous_song():
    try:
        # Get current song info for logging
        current_response = requests.get(
            f'{API_BASE_URL}/api/v1/song',
            headers=get_headers()
        )
        song_info = "unknown song"
        if current_response.status_code == 200:
            song_data = current_response.json()
            song_info = f"{song_data.get('title', '?')} by {song_data.get('artist', '?')}"

        response = requests.post(
            f'{API_BASE_URL}/api/v1/previous',
            headers=get_headers()
        )
        if response.status_code == 204:
            logger.info(f"Went to previous song from: {song_info}")
        else:
            logger.error(f"Failed to go to previous song: {response.text}")
        return '', response.status_code
    except Exception as e:
        logger.error(f"Error going to previous song: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/volume', methods=['GET'])
def get_volume():
    try:
        import subprocess
        result = subprocess.run(['amixer', '-D', 'pulse', 'sget', 'Master'], capture_output=True, text=True)
        # Parse the output to get the volume percentage
        import re
        match = re.search(r'\[(\d+)%\]', result.stdout)
        if match:
            volume = int(match.group(1))
            return jsonify({'volume': volume})
        return jsonify({'error': 'Could not get volume'}), 500
    except Exception as e:
        logger.error(f"Error getting volume: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/volume/up', methods=['POST'])
def volume_up():
    try:
        import subprocess
        subprocess.run(['amixer', '-q', '-D', 'pulse', 'sset', 'Master', f'{VOLUME_STEP_PERCENT}%+'])
        return '', 204
    except Exception as e:
        logger.error(f"Error increasing volume: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/volume/down', methods=['POST'])
def volume_down():
    try:
        import subprocess
        subprocess.run(['amixer', '-q', '-D', 'pulse', 'sset', 'Master', f'{VOLUME_STEP_PERCENT}%-'])
        return '', 204
    except Exception as e:
        logger.error(f"Error decreasing volume: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 
