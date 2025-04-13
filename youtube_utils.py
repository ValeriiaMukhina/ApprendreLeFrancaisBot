import requests
import json
import re
from urllib.parse import urlparse, parse_qs

def get_video_id(video_url):
    """
    Extract the video ID from a YouTube URL.
    Supports common formats like:
      - https://www.youtube.com/watch?v=VIDEO_ID
      - https://youtu.be/VIDEO_ID
    """
    match = re.search(r"(?:v=|youtu\.be/)([^&?/]+)", video_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube URL or video ID not found.")

def fetch_video_data(video_id):
    """
    Fetch detailed video information (including caption tracks) using YouTube's undocumented API.
    """
    # Endpoint URL with the YouTube client key (as used by the web client)
    api_endpoint = "https://www.youtube.com/youtubei/v1/player?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&prettyPrint=false"
    payload = {
        "context": {
            "client": {
                "clientName": "WEB",
                "clientVersion": "2.20210721.00.00"  # Example version; update if necessary.
            }
        },
        "videoId": video_id
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.post(api_endpoint, data=json.dumps(payload), headers=headers)
    if response.status_code != 200:
        raise Exception(f"Request failed: {response.status_code} {response.reason}")
    return response.json()

def extract_caption_tracks(api_json):
    """
    Extract caption tracks from the video details JSON.
    """
    try:
        caption_tracks = (
            api_json.get("captions", {})
                    .get("playerCaptionsTracklistRenderer", {})
                    .get("captionTracks", [])
        )
        return caption_tracks
    except Exception as e:
        raise Exception("Error extracting caption tracks: " + str(e))

def select_caption_track(tracks, language="fr"):
    """
    Select a caption track that matches the given language code.
    If none match exactly, return the first available track.
    """
    for track in tracks:
        if track.get("languageCode") == language:
            return track
    return tracks[0] if tracks else None

def download_subtitles(caption_track, fmt="srv3"):
    """
    Download subtitles from the selected caption track.
    The format parameter (fmt) can be adjusted if necessary (common formats include srv1, srv3, etc.).
    """
    base_url = caption_track.get("baseUrl")
    if not base_url:
        raise Exception("No baseUrl found in caption track.")
    download_url = base_url + "&fmt=" + fmt
    response = requests.get(download_url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to download subtitles: {response.status_code} {response.reason}")

def get_youtube_transcript(video_url, languages=['fr', 'en']):
    """
    Given a YouTube video URL, extract and return the transcript (subtitles) as a single string.
    It attempts to select a caption track matching one of the preferred languages.
    """
    video_id = get_video_id(video_url)
    api_json = fetch_video_data(video_id)
    tracks = extract_caption_tracks(api_json)
    if not tracks:
        raise Exception("No captions available for this video!")
    
    # Loop through preferred languages in order until a caption track is found.
    selected_track = None
    for lang in languages:
        selected_track = select_caption_track(tracks, language=lang)
        if selected_track:
            break
    if not selected_track:
        raise Exception("No suitable caption track found!")
    
    subtitles = download_subtitles(selected_track)
    return subtitles
