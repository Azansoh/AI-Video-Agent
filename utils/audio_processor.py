import os
import re
import yt_dlp
from pydub import AudioSegment
from youtube_transcript_api import YouTubeTranscriptApi

DOWNLOAD_DIR = "downloads"
COOKIE_PATH = "/tmp/youtube_cookies.txt"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def extract_youtube_id(url: str) -> str:
    pattern = r"(?:v=|\/|youtu\.be\/)([0-9A-Za-z_-]{11})"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    raise ValueError("Invalid YouTube URL")


def get_youtube_transcript(url: str) -> str:
    video_id = extract_youtube_id(url)

    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        try:
            transcript = transcript_list.find_manually_created_transcript(
                ["en", "ur", "hi", "es", "fr", "de", "pt", "ar"]
            )
        except Exception:
            transcript = transcript_list.find_generated_transcript(
                ["en", "ur", "hi", "es", "fr", "de", "pt", "ar"]
            )

        data = transcript.fetch()
        return " ".join([item["text"] for item in data])
    except Exception as e:
        raise RuntimeError(f"No transcript available: {e}")


def _setup_cookies():
    cookies_content = os.getenv("YOUTUBE_COOKIES")
    if cookies_content:
        with open(COOKIE_PATH, "w") as f:
            f.write(cookies_content)
        print("YouTube cookies loaded from environment variable.")


def download_youtube_audio(url: str) -> str:
    _setup_cookies()

    video_id = extract_youtube_id(url)
    output_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.%(ext)s")

    ydl_opts = {
        "format": "ba/ba*",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "no_warnings": True,
        "geo_bypass": True,
    }

    if os.path.exists(COOKIE_PATH):
        ydl_opts["cookiefile"] = COOKIE_PATH

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = os.path.splitext(ydl.prepare_filename(info))[0] + ".wav"
        return filename


def chunk_audio(wav_path: str, chunk_minutes: int = 2) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []
    base_name = os.path.splitext(wav_path)[0]

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_path = f"{base_name}_chunk{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    return chunks
