import os
import re
import traceback
from dotenv import load_dotenv
from utils.audio_processor import chunk_audio, get_youtube_transcript, download_youtube_audio, extract_youtube_id
from core.transcriber import transcribe_all
from core.summarize import summarize, generate_title
from core.extractor import extract_action_items, extract_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

CURRENT_RAG_CHAIN = None


def is_youtube_url(source: str) -> bool:
    source = source.strip()
    return bool(re.match(r"^(https?://|www\.)", source, re.IGNORECASE))


def run_pipeline(source: str, language: str = "english") -> dict:
    global CURRENT_RAG_CHAIN

    print("Starting AI Video Assistant pipeline...")
    source = source.strip()

    if is_youtube_url(source):
        if source.startswith("www."):
            source = "https://" + source

        transcript = None

        print(f"Step 0: Trying transcript API... ({source})")
        try:
            transcript = get_youtube_transcript(source)
            print("Transcript fetched successfully via API.")
        except Exception as e:
            print(f"Transcript API failed: {e}")

        if not transcript:
            print("Step 0b: No captions found. Downloading audio with yt-dlp + cookies...")
            audio_file = download_youtube_audio(source)
            print(f"Step 1: Chunking audio from '{audio_file}'...")
            audio_chunks = chunk_audio(audio_file)
            print("Step 2: Transcribing audio with Whisper...")
            transcript = transcribe_all(audio_chunks, language=language)

        print("Step 3: Generating title...")
        title = generate_title(transcript)
    else:
        if not os.path.exists(source):
            raise FileNotFoundError(f"Local audio file does not exist: '{source}'")

        print(f"Step 0: Chunking audio from '{source}'...")
        audio_chunks = chunk_audio(source)

        print("Step 1: Transcribing audio with Whisper...")
        transcript = transcribe_all(audio_chunks, language=language)

        print("Step 2: Generating title...")
        title = generate_title(transcript)

    print("Step 3: Summarizing transcript...")
    summary = summarize(transcript)

    print("Step 4: Extracting key insights...")
    action_items = extract_action_items(transcript)
    decisions = extract_decisions(transcript)
    questions = extract_questions(transcript)

    print("Step 5: Building RAG chain...")
    CURRENT_RAG_CHAIN = build_rag_chain(transcript)

    print("Pipeline execution completed successfully.")

    return {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_items,
        "decisions": decisions,
        "questions": questions,
    }


if __name__ == "__main__":
    source = input("Enter YouTube URL or audio file path: ").strip()
    language = (
        input("Enter language (press Enter for 'english'): ").strip()
        or "english"
    )

    if not source:
        print("Error: Source URL or path cannot be empty.")
    else:
        try:
            results = run_pipeline(source, language=language)

            print("\n" + "=" * 50)
            print(f"TITLE: {results['title']}")
            print("=" * 50)

            print("\n--- SUMMARY ---")
            print(results["summary"])

            print("\n--- ACTION ITEMS ---")
            print(results["action_items"])

            print("\n--- DECISIONS ---")
            print(results["decisions"])

            print("\n--- UNRESOLVED QUESTIONS ---")
            print(results["questions"])

            print("\n" + "=" * 50)
            print("Ask questions about the meeting (type 'exit' or 'quit' to stop):")
            print("=" * 50)

            while True:
                question = input("\nYour Question: ").strip()
                if question.lower() in ["exit", "quit"]:
                    print("Exiting session. Goodbye!")
                    break

                if not question:
                    continue

                if CURRENT_RAG_CHAIN:
                    response = ask_question(CURRENT_RAG_CHAIN, question)
                    print(f"\nAnswer: {response}")
                else:
                    print("RAG chain unavailable.")

        except Exception as e:
            print("\nPipeline failed with error:")
            traceback.print_exc()
