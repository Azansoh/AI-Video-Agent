import os
import re
from dotenv import load_dotenv
from utils.audio_processor import chunk_audio, download_youtube_audio
from core.transcriber import transcribe_all
from core.summarize import summarize, generate_title
from core.extractor import extract_action_items, extract_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()


def is_url(source: str) -> bool:
    """Checks if input is a URL or local file path."""
    return source.startswith(("http://", "https://"))


def run_pipeline(source: str, language: str = "english") -> dict:
    
    print("Starting AI Video Assistant pipeline...")

    # Step 0: Handle URL download vs local file
    if is_url(source):
        print("Step 0: Downloading audio from YouTube...")
        audio_file = download_youtube_audio(source)
    else:
        audio_file = source

    print("Step 1: Chunking audio source...")
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
    rag_chain = build_rag_chain(transcript)

    print("Pipeline execution completed successfully.")

    return {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_items,
        "decisions": decisions,
        "questions": questions,
        "rag_chain": rag_chain,
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

        rag_chain = results["rag_chain"]

        while True:
            question = input("\nYour Question: ").strip()
            if question.lower() in ["exit", "quit"]:
                print("Exiting session. Goodbye!")
                break

            if not question:
                continue

            response = ask_question(rag_chain, question)
            print(f"\nAnswer: {response}")