import os
import re
from pydub import AudioSegment
from youtube_transcript_api import YouTubeTranscriptApi


def extract_youtube_id(url: str) -> str:
    pattern = r"(?:v=|\/|youtu\.be\/)([0-9A-Za-z_-]{11})"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    raise ValueError("Invalid YouTube URL")


def get_youtube_transcript(url: str) -> str:
    video_id = extract_youtube_id(url)

    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(
            video_id, languages=["en", "ur", "hi", "es", "fr", "de", "pt", "ar"]
        )
        full_text = " ".join([item["text"] for item in transcript_data])
        return full_text
    except Exception:
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            for t in transcript_list:
                generated = t.translate("en")
                full_text = " ".join([item["text"] for item in generated])
                return full_text
        except Exception:
            pass

    raise RuntimeError(
        "No transcript or subtitles available for this video. "
        "Try a video that has captions enabled."
    )


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
