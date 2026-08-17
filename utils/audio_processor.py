import os
import requests
import yt_dlp
from pydub import AudioSegment

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    try:
        return _download_via_cobalt(url)
    except Exception as cobalt_err:
        print(f"Cobalt API failed: {cobalt_err}, trying yt-dlp...")

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
        raise RuntimeError(
            f"Download failed: {e}\n"
            "YouTube blocks downloads from cloud servers."
        )


def _download_via_cobalt(url: str) -> str:
    cobalt_url = "https://api.cobalt.tools/"

    resp = requests.post(
        cobalt_url,
        json={
            "url": url,
            "downloadMode": "audio",
            "audioFormat": "wav",
        },
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()

    if "error" in data:
        raise RuntimeError(f"Cobalt error: {data['error'].get('code', data['error'])}")

    download_url = data.get("url")
    if not download_url:
        raise RuntimeError("Cobalt returned no download URL")

    filename = os.path.join(DOWNLOAD_DIR, f"cobalt_audio_{hash(url) % 100000}.wav")

    dl_resp = requests.get(download_url, stream=True, timeout=120)
    dl_resp.raise_for_status()

    with open(filename, "wb") as f:
        for chunk in dl_resp.iter_content(chunk_size=8192):
            f.write(chunk)

    converted = os.path.splitext(filename)[0] + ".wav"
    if filename != converted:
        os.rename(filename, converted)

    return converted


def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
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


