# gemini_yt_cleaner
clean youtube transcript using gemini flash experimental


# YouTube Transcript Processor Setup Guide

## Requirements

Create a file named `environment.yml` with the following contents:

```yaml
name: transcript-env
channels:
  - defaults
  - conda-forge
dependencies:
  - python=3.10
  - pip
  - pip:
    - youtube-transcript-api
    - requests
    - python-dotenv
    - google-generativeai
```

## Setup Instructions

1. Create the Conda environment:
```bash
conda env create -f environment.yml
```

2. Activate the environment:
```bash
conda activate transcript-env
```

3. Create a `.env` file in your project directory with your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

## Project Structure
Your project directory should look like this:
```
project/
├── environment.yml
├── .env
├── personas/
│   └── transcript.py
└── transcripts/    # Will be created automatically
```

## Running the Code

1. Make sure you're in the project directory
2. Ensure your Conda environment is activated
3. Run the script:
```bash
python personas/transcript.py
```

4. When prompted, enter a YouTube URL to process its transcript

## Notes
- You'll need a Google API key with access to the Gemini API
- The script will create a `transcripts` directory to store both raw and cleaned transcripts
- Make sure your YouTube video has captions/transcripts available
- The cleaned transcript processing might take a few moments depending on the length of the video

## Troubleshooting
If you encounter any dependency issues, you can manually install them using:
```bash
pip install youtube_transcript_api requests python-dotenv google-generativeai
```
