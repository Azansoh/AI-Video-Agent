import os
import re
import requests
from pydub import AudioSegment

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:
    video_id = re.search(r"(?:v=|/)([\w-]{11})", url)
    file_id = video_id.group(1) if video_id else "unknown"

    return _download_via_piped(url, file_id)


def _download_via_piped(url: str, file_id: str) -> str:
    piped_instances = [
        "https://pipedapi.kavin.rocks",
        "https://pipedapi.adminforge.de",
        "https://api.piped.yt",
    ]

    vid_id = re.search(r"(?:v=|/)([\w-]{11})", url)
    if not vid_id:
        raise RuntimeError(f"Could not extract video ID from URL: {url}")
    video_id_str = vid_id.group(1)

    last_error = None
    for instance in piped_instances:
        try:
            api_url = f"{instance}/streams/{video_id_str}"
            resp = requests.get(api_url, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            audio_streams = [
                s for s in data.get("audioStreams", [])
                if s.get("mimeType", "").startswith("audio/")
            ]
            if not audio_streams:
                last_error = "No audio streams found"
                continue

            best = max(audio_streams, key=lambda s: s.get("bitrate", 0))
            stream_url = best.get("url")
            if not stream_url:
                last_error = "No stream URL"
                continue

            print(f"Downloading audio from Piped ({instance})...")
            dl_resp = requests.get(stream_url, stream=True, timeout=120, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            dl_resp.raise_for_status()

            temp_path = os.path.join(DOWNLOAD_DIR, f"{file_id}_temp.m4a")
            with open(temp_path, "wb") as f:
                for chunk in dl_resp.iter_content(chunk_size=8192):
                    f.write(chunk)

            wav_path = os.path.join(DOWNLOAD_DIR, f"{file_id}.wav")
            audio = AudioSegment.from_file(temp_path)
            audio = audio.set_channels(1).set_frame_rate(16000)
            audio.export(wav_path, format="wav")

            try:
                os.remove(temp_path)
            except OSError:
                pass

            return wav_path

        except Exception as e:
            last_error = f"{instance}: {e}"
            print(f"Piped instance {instance} failed: {e}")
            continue

    raise RuntimeError(f"All Piped instances failed. Last error: {last_error}")


def convert_to_wav(input_path: str) -> str:
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_path, format="wav")
    return output_path


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
