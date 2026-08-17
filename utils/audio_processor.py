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
        raise RuntimeError(
            f"No transcript available for this video. {e}"
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
