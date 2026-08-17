import os
from faster_whisper import WhisperModel

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")

_model = None


def load_model():
    global _model

    if _model is None:
        print("Loading model...")
        _model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
        print("Whisper model loaded successfully.")

    return _model


def transcribe_chunk(
    chunk_path: str, language: str = None, translate: bool = False
) -> str:
    model = load_model()

    task = "translate" if translate else "transcribe"

    kwargs = {}
    if language:
        kwargs["language"] = language
    if translate:
        kwargs["task"] = "translate"

    segments, info = model.transcribe(chunk_path, beam_size=5, **kwargs)
    text = " ".join(segment.text for segment in segments)

    return text

def transcribe_all(
    chunks: list, language: str = None, translate: bool = False
) -> str:
    full_transcript = ""

    for i, chunk in enumerate(chunks):
        print(f"Transcribing chunk {i + 1}")
        text = transcribe_chunk(
            chunk, language=language, translate=translate
        )
        full_transcript += text + " "

    print("Transcription completed.")
    return full_transcript.strip()