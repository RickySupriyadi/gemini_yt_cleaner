from youtube_transcript_api import YouTubeTranscriptApi
import requests
import re
from datetime import timedelta
import os
from dotenv import load_dotenv

# Load environment variables from .env (for the Google API key)
load_dotenv()

# -----------------------------
# YouTube & Transcript Functions
# -----------------------------

def extract_video_id(url):
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'youtu.be\/([0-9A-Za-z_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def format_timestamp(seconds):
    return str(timedelta(seconds=int(seconds)))

def get_video_title(video_id):
    try:
        response = requests.get(
            f'https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v={video_id}&format=json'
        )
        if response.status_code == 200:
            return response.json()['title']
        return None
    except Exception as e:
        print(f"Error fetching video title: {str(e)}")
        return None

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        print(f"Error fetching transcript: {str(e)}")
        return None

def sanitize_filename(filename):
    # Remove or replace invalid filename characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    # Limit filename length and remove leading/trailing spaces
    return filename.strip()[:200]

# -----------------------------
# Transcript Saving Functions
# -----------------------------

def save_raw_transcript(video_id, video_title, transcript):
    """
    Saves the raw transcript to a file named filename_raw.md
    """
    # Create transcripts directory if it doesn't exist
    if not os.path.exists('transcripts'):
        os.makedirs('transcripts')

    # Use video title if available; otherwise use video ID
    base_filename = sanitize_filename(video_title) if video_title else video_id
    filepath = os.path.join('transcripts', f"{base_filename}_raw.md")

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {video_title or 'Unknown Title'} (Raw Transcript)\n\n")
            f.write("---\n\n")
            for entry in transcript:
                timestamp = format_timestamp(entry['start'])
                text = entry['text']
                f.write(f"[{timestamp}] {text}\n")
        print(f"Raw transcript saved to {filepath}")
        return filepath
    except Exception as e:
        print(f"Error saving raw transcript: {str(e)}")
        return None

def save_cleaned_transcript(video_id, video_title, cleaned_text):
    """
    Saves the cleaned transcript (as processed by the AI) to a file named filename.md
    """
    # Create transcripts directory if it doesn't exist
    if not os.path.exists('transcripts'):
        os.makedirs('transcripts')

    # Use video title if available; otherwise use video ID
    base_filename = sanitize_filename(video_title) if video_title else video_id
    filepath = os.path.join('transcripts', f"{base_filename}.md")

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {video_title or 'Unknown Title'} (Cleaned Transcript)\n\n")
            f.write("---\n\n")
            f.write(cleaned_text)
        print(f"Cleaned transcript saved to {filepath}")
        return filepath
    except Exception as e:
        print(f"Error saving cleaned transcript: {str(e)}")
        return None

# -----------------------------
# Gemini Cleaning Function
# -----------------------------

def clean_transcript_with_gemini(raw_transcript_text):
    """
    Leverages the Google Gemini 2.0 Flash experimental API (via google-genai)
    to clean and reformat the raw transcript text into well-formatted paragraphs.
    """
    try:
        from google import genai

        # Create a client for the Gemini model using your API key
        client = genai.Client(
            api_key=os.getenv("GOOGLE_API_KEY"),
            http_options={"api_version": "v1alpha"},
        )

        # Build a prompt that instructs the model to clean and format the transcript.
        prompt = (
            "The following is a raw YouTube transcript. "
            "Please reformat the transcript into clear paragraphs. "
            "Each paragraph should begin with the timestamp of the first line in that paragraph, "
            "and the formatting should be cleaned up (remove extraneous line breaks, duplicate timestamps, etc.).\n\n"
            "Transcript:\n" + raw_transcript_text
        )

        # Send the prompt to the Gemini model
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[prompt],
        )
        # Return the cleaned text
        return response.text
    except Exception as e:
        print(f"Error cleaning transcript with Gemini: {str(e)}")
        return None

# -----------------------------
# Main Function
# -----------------------------

def main():
    url = input("Please enter the YouTube video URL: ")
    video_id = extract_video_id(url)

    if video_id:
        print(f"Video ID: {video_id}")
        video_title = get_video_title(video_id)
        transcript = get_transcript(video_id)

        if transcript:
            # Build a raw transcript string (for AI input and saving the raw file)
            raw_transcript_lines = []
            for entry in transcript:
                timestamp = format_timestamp(entry['start'])
                text = entry['text']
                raw_transcript_lines.append(f"[{timestamp}] {text}")
            raw_transcript_text = "\n".join(raw_transcript_lines)

            # Print the raw transcript to console (optional)
            print("\nRaw Transcript:")
            print("==========================")
            print(f"Title: {video_title or 'Unknown Title'}")
            print("==========================")
            print(raw_transcript_text)

            # Save the raw transcript file
            save_raw_transcript(video_id, video_title, transcript)

            # Clean the transcript using Gemini 2.0 Flash experimental API
            print("\nCleaning transcript with Gemini (this may take a moment)...")
            cleaned_transcript = clean_transcript_with_gemini(raw_transcript_text)
            if cleaned_transcript:
                print("\nCleaned Transcript:")
                print("==========================")
                print(cleaned_transcript)
                # Save the cleaned transcript file
                save_cleaned_transcript(video_id, video_title, cleaned_transcript)
            else:
                print("Failed to clean transcript.")
        else:
            print("Transcript not available.")
    else:
        print("Invalid YouTube URL.")

if __name__ == "__main__":
    main()
