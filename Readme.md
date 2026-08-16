# 🎥 AI Video Intelligence Agent

An end-to-end intelligent AI application that transforms **YouTube videos and local audio files into searchable, actionable knowledge**.

The system automatically downloads and processes audio, transcribes speech locally using **OpenAI Whisper**, generates structured executive insights using **Mistral AI**, and builds a **Retrieval-Augmented Generation (RAG)** knowledge base that allows users to interactively query the video transcript.

## 🌟 Key Features

### 🎧 Audio Acquisition & Processing

* Downloads audio directly from YouTube using `yt-dlp`
* Supports local audio files
* Converts audio to **16kHz mono WAV** format for optimized transcription
* Dynamically splits large audio files into manageable chunks using `pydub`

### 🗣️ Local Speech-to-Text

* Performs high-quality transcription locally using **OpenAI Whisper**
* Supports GPU acceleration when available
* Uses `fp16=False` for stable CPU execution
* Processes long-form audio efficiently through chunk-based transcription

### 🧠 Automated Insight Extraction

Uses **LangChain** and **Mistral AI (`mistral-small-latest`)** to transform raw transcripts into structured executive insights.

The system automatically generates:

* 📝 Concise meeting or video titles
* 📄 Comprehensive executive summaries
* ✅ Categorized action items

  * Task
  * Owner
  * Deadline
* 🎯 Key decisions
* ❓ Open and unresolved questions

### 🔎 Vector Indexing & RAG Engine

* Splits transcripts into semantic chunks using `RecursiveCharacterTextSplitter`
* Generates embeddings with HuggingFace's `all-MiniLM-L6-v2`
* Stores and persists vector data locally using **ChromaDB**
* Retrieves relevant transcript context for every user query

### 💬 Interactive Contextual Q&A

An interactive terminal-based RAG interface allows users to ask questions about the processed video or audio content.

Responses are generated using relevant retrieved transcript context, helping keep answers grounded in the original content.

## 🔄 Application Workflow

```text
YouTube Video / Local Audio
            │
            ▼
   Audio Download & Processing
            │
            ▼
      Audio Chunking
            │
            ▼
   Whisper Transcription
            │
            ▼
      Full Transcript
            │
      ┌─────┴─────┐
      ▼           ▼
Mistral AI     ChromaDB
Insights       Vector Store
      │           │
      ▼           ▼
Summary      RAG Retrieval
Actions           │
Decisions         ▼
Questions    Interactive Q&A
```

## 📁 Repository Structure

```text
├── core/
│   ├── extractor.py        # Extracts action items, decisions, and open questions
│   ├── rag_engine.py       # Builds the RAG pipeline and handles Q&A
│   ├── summarize.py        # Generates summaries and titles using map-reduce chains
│   ├── transcriber.py      # Whisper model loading and transcription logic
│   └── vector_store.py     # ChromaDB initialization, persistence, and retrieval
│
├── utils/
│   └── audio_processor.py  # YouTube download, audio conversion, and chunking
│
├── downloads/              # Downloaded and processed audio files (git-ignored)
├── vector_db/              # Persisted ChromaDB vector database (git-ignored)
│
├── main.py                 # Terminal CLI entry point and complete execution pipeline
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignored files and directories
└── README.md               # Project documentation
```

## 🛠️ Tech Stack

| Technology             | Purpose                                    |
| ---------------------- | ------------------------------------------ |
| Python 3.11+           | Core programming language                  |
| LangChain              | LLM orchestration and RAG pipeline         |
| Mistral AI             | Insight extraction and response generation |
| OpenAI Whisper         | Local speech-to-text transcription         |
| ChromaDB               | Persistent vector database                 |
| HuggingFace Embeddings | Semantic text embeddings                   |
| Sentence Transformers  | `all-MiniLM-L6-v2` embedding model         |
| yt-dlp                 | YouTube audio extraction                   |
| pydub                  | Audio conversion and chunking              |
| FFmpeg                 | Audio decoding and processing              |

## ⚙️ Installation

Clone the repository:

```bash
git clone <your-repository-url>
cd ai-video-agent
```

Create and activate a virtual environment:

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### macOS/Linux

```bash
source venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

> **Note:** FFmpeg must also be installed and available in your system PATH for audio conversion and processing.

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
MISTRAL_API_KEY=your_mistral_api_key
```

## 🚀 Usage

Run the application:

```bash
python main.py
```

The application allows you to provide either:

1. A **YouTube video URL**
2. A **local audio file**

The system then performs the complete pipeline:

```text
Audio Input
    ↓
Download / Load Audio
    ↓
Convert & Chunk Audio
    ↓
Whisper Transcription
    ↓
Generate Executive Insights
    ↓
Create ChromaDB Vector Store
    ↓
Start Interactive RAG Chat
```

After processing is complete, you can ask contextual questions about the video or audio transcript through the interactive terminal interface.

## 🧠 Example Capabilities

The AI Video Intelligence Agent can answer questions such as:

```text
What was the main topic of discussion?
```

```text
What action items were assigned?
```

```text
Who is responsible for each task?
```

```text
What decisions were made?
```

```text
Which questions are still unresolved?
```

## 🔮 Future Improvements

* Streamlit or React-based web interface
* Speaker diarization
* Timestamp-based citations
* Multi-language transcription
* Video file upload support
* Chat history and memory
* Export insights to PDF or DOCX
* Cloud-based deployment
* Authentication and user workspaces

## 🎯 Project Goal

The goal of this project is to convert long, unstructured video and audio content into **structured, searchable, and actionable intelligence**.

By combining **Whisper for transcription**, **Mistral AI for intelligent analysis**, and **ChromaDB-powered RAG**, the application enables users to move beyond simply watching or listening to content and instead interact with it as a searchable knowledge source.

---

⭐ If you found this project interesting, consider giving the repository a star!
