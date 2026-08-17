import os
import re
import requests
import yt_dlp
from pydub import AudioSegment

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:

    try:
        return _download_via_cobalt(url)
    except Exception as e:
        print(f"Cobalt API failed: {e}")

    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
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
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.youtube.com/",
        },
        "extractor_args": {
            "youtube": {
                "player_client": ["web_creator"],
                "player_skip": ["webpage", "configs"],
            }
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = os.path.splitext(ydl.prepare_filename(info))[0] + ".wav"
            return filename
    except Exception as e:
        raise RuntimeError(f"Download failed: {e}")


COBALT_INSTANCES = [
    "https://api.cobalt.tools",
    "https://cobalt-api.kwiatekmiki.com",
]


def _download_via_cobalt(url: str) -> str:
    last_error = None

    for instance in COBALT_INSTANCES:
        try:
            resp = requests.post(
                f"{instance}/",
                json={
                    "url": url,
                    "downloadMode": "audio",
                    "audioFormat": "mp3",
                },
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                timeout=30,
            )

            if resp.status_code != 200:
                last_error = f"HTTP {resp.status_code} from {instance}"
                continue

            try:
                data = resp.json()
            except ValueError:
                last_error = f"Non-JSON response from {instance}"
                continue

            if data.get("status") == "error" or "error" in data:
                err = data.get("error", data.get("status"))
                last_error = f"Cobalt error: {err}"
                continue

            download_url = data.get("url")
            if not download_url:
                last_error = f"No download URL from {instance}"
                continue

            return _download_file(download_url, url)

        except requests.RequestException as e:
            last_error = f"Request failed for {instance}: {e}"
            continue

    raise RuntimeError(f"All Cobalt instances failed. Last error: {last_error}")


def _download_file(download_url: str, original_url: str) -> str:
    video_id = re.search(r"(?:v=|/)([\w-]{11})", original_url)
    file_id = video_id.group(1) if video_id else str(hash(original_url) % 100000)
    filename = os.path.join(DOWNLOAD_DIR, f"{file_id}.mp3")

    resp = requests.get(download_url, stream=True, timeout=120)
    resp.raise_for_status()

    with open(filename, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    wav_path = os.path.splitext(filename)[0] + ".wav"
    audio = AudioSegment.from_file(filename)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(wav_path, format="wav")

    try:
        os.remove(filename)
    except OSError:
        pass

    return wav_path


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
