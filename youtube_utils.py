from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

def get_youtube_transcript(video_url, languages=['en']):
    """
    Given a YouTube video URL, extract and return the transcript as a single string.

    Parameters:
      video_url (str): The URL of the YouTube video.
      languages (list): A list of language codes to try for the transcript.
                        For French, you can use ['fr'].

    Returns:
      str: The transcript text of the video.

    Raises:
      ValueError: If the URL is invalid or the video ID cannot be extracted.
      Exception: If the transcript is not available.
    """
    # Parse the URL to extract the video ID
    parsed_url = urlparse(video_url)
    video_id = None

    if parsed_url.hostname in ['youtu.be']:
        # For URLs like https://youtu.be/abc123
        video_id = parsed_url.path[1:]
    elif parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        if parsed_url.path == '/watch':
            query = parse_qs(parsed_url.query)
            video_id = query.get('v', [None])[0]
        elif parsed_url.path.startswith('/embed/'):
            video_id = parsed_url.path.split('/')[2]
        elif parsed_url.path.startswith('/v/'):
            video_id = parsed_url.path.split('/')[2]
    else:
        raise ValueError("Invalid YouTube URL provided.")

    if not video_id:
        raise ValueError("Could not extract video ID from the URL.")

    # Fetch the transcript in one of the desired languages
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)

    # Combine all transcript entries into one string
    transcript_text = "\n".join(entry["text"] for entry in transcript_list)
    
    return transcript_text
