import os
import re
import requests
import yt_dlp
from pydub import AudioSegment
from pytubefix import YouTube

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:
    video_id = re.search(r"(?:v=|/)([\w-]{11})", url)
    file_id = video_id.group(1) if video_id else "unknown"
    wav_path = os.path.join(DOWNLOAD_DIR, f"{file_id}.wav")

    methods = [
        ("pytubefix", _download_via_pytubefix),
        ("cobalt", _download_via_cobalt),
        ("yt-dlp", _download_via_ytdlp),
    ]

    errors = []
    for name, func in methods:
        try:
            print(f"Trying {name}...")
            result = func(url, file_id)
            print(f"{name} succeeded: {result}")
            return result
        except Exception as e:
            print(f"{name} failed: {e}")
            errors.append(f"{name}: {e}")

    raise RuntimeError(
        "All download methods failed:\n" + "\n".join(errors)
    )


def _download_via_pytubefix(url: str, file_id: str) -> str:
    yt = YouTube(url, use_po_token=True)
    stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
    if not stream:
        raise RuntimeError("No audio stream found")

    temp_path = os.path.join(DOWNLOAD_DIR, f"{file_id}_temp")
    stream.download(output_path=DOWNLOAD_DIR, filename=f"{file_id}_temp")

    downloaded = None
    for f in os.listdir(DOWNLOAD_DIR):
        if f.startswith(f"{file_id}_temp"):
            downloaded = os.path.join(DOWNLOAD_DIR, f)
            break

    if not downloaded:
        raise RuntimeError("File not downloaded")

    wav_path = os.path.join(DOWNLOAD_DIR, f"{file_id}.wav")
    audio = AudioSegment.from_file(downloaded)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(wav_path, format="wav")

    try:
        os.remove(downloaded)
    except OSError:
        pass

    return wav_path


def _download_via_cobalt(url: str, file_id: str) -> str:
    cobalt_instances = [
        "https://api.cobalt.tools",
        "https://cobalt-api.kwiatekmiki.com",
    ]

    last_error = None
    for instance in cobalt_instances:
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
                last_error = f"HTTP {resp.status_code}"
                continue

            try:
                data = resp.json()
            except ValueError:
                last_error = "Non-JSON response"
                continue

            if data.get("status") == "error" or "error" in data:
                last_error = f"Cobalt error: {data.get('error', data.get('status'))}"
                continue

            download_url = data.get("url")
            if not download_url:
                last_error = "No download URL"
                continue

            mp3_path = os.path.join(DOWNLOAD_DIR, f"{file_id}.mp3")
            dl_resp = requests.get(download_url, stream=True, timeout=120)
            dl_resp.raise_for_status()

            with open(mp3_path, "wb") as f:
                for chunk in dl_resp.iter_content(chunk_size=8192):
                    f.write(chunk)

            wav_path = os.path.join(DOWNLOAD_DIR, f"{file_id}.wav")
            audio = AudioSegment.from_file(mp3_path)
            audio = audio.set_channels(1).set_frame_rate(16000)
            audio.export(wav_path, format="wav")

            try:
                os.remove(mp3_path)
            except OSError:
                pass

            return wav_path

        except requests.RequestException as e:
            last_error = str(e)
            continue

    raise RuntimeError(f"All Cobalt instances failed: {last_error}")


def _download_via_ytdlp(url: str, file_id: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")

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

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = os.path.splitext(ydl.prepare_filename(info))[0] + ".wav"
        return filename


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
