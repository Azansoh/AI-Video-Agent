import os
import whisper

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

_model = None


def load_model():
    global _model

    if _model is None:
        print("Loading model...")
        _model = whisper.load_model(WHISPER_MODEL)
        print("Whisper model loaded successfully.")

    return _model


def transcribe_chunk(
    chunk_path: str, language: str = None, translate: bool = False
) -> str:
    model = load_model()

    task = "translate" if translate else "transcribe"

    options = {"task": task}
    if language:
        options["language"] = language

    # Added verbose=True to stream text live to terminal
    result = model.transcribe(chunk_path, fp16=False, verbose=True, **options)

    return result["text"]

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