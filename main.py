import os
import re
import traceback
from dotenv import load_dotenv
from utils.audio_processor import chunk_audio, download_youtube_audio
from core.transcriber import transcribe_all
from core.summarize import summarize, generate_title
from core.extractor import extract_action_items, extract_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# Global in-memory storage for the active RAG chain (prevents JSON serialization errors in FastAPI)
CURRENT_RAG_CHAIN = None


def is_url(source: str) -> bool:
    """Checks if input is a valid HTTP/HTTPS or WWW URL."""
    source = source.strip()
    return bool(re.match(r'^(https?://|www\.)', source, re.IGNORECASE))


def run_pipeline(source: str, language: str = "english") -> dict:
    global CURRENT_RAG_CHAIN
    
    print("Starting AI Video Assistant pipeline...")
    source = source.strip()

    # Step 0: Handle URL download vs local file
    if is_url(source):
        if source.startswith("www."):
            source = "https://" + source
        print(f"Step 0: Downloading audio from YouTube... ({source})")
        audio_file = download_youtube_audio(source)
    else:
        audio_file = source
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Local audio file does not exist: '{audio_file}'")

    print(f"Step 1: Chunking audio source from '{audio_file}'...")
    audio_chunks = chunk_audio(audio_file)

    print("Step 2: Transcribing audio...")
    transcript = transcribe_all(audio_chunks, language=language)

    print("Step 3: Generating title...")
    title = generate_title(transcript)

    print("Step 4: Summarizing transcript...")
    summary = summarize(transcript)

    print("Step 5: Extracting key insights...")
    action_items = extract_action_items(transcript)
    decisions = extract_decisions(transcript)
    questions = extract_questions(transcript)

    print("Step 6: Building RAG chain...")
    CURRENT_RAG_CHAIN = build_rag_chain(transcript)

    print("Pipeline execution completed successfully.")

    # Return only JSON-serializable fields for API responses
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