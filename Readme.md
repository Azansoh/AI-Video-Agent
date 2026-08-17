# 🎥 AI Video Intelligence Agent

An end-to-end intelligent AI application that transforms **YouTube videos and local audio files into searchable, actionable knowledge**.

The application provides a modern **web-based interface** where users can submit YouTube URLs or local audio files, process the content through an AI-powered backend, generate structured insights, and interact with the transcript using a **Retrieval-Augmented Generation (RAG)** chat system.

The system automatically downloads and processes audio, transcribes speech locally using **OpenAI Whisper**, generates structured executive insights using **Mistral AI**, and builds a **RAG knowledge base** that allows users to interactively query the video or audio content.

---

## 🌟 Key Features

### 🌐 Modern Web Interface

The application includes an interactive frontend built with:

* **HTML** for application structure
* **CSS** for responsive and modern UI design
* **JavaScript** for client-side interactivity and API communication

Users can:

* Submit a YouTube video URL
* Upload or select local audio content
* Start AI-powered processing
* View generated summaries and insights
* Explore action items and decisions
* Ask questions about the processed content through an interactive RAG chat interface

---

### ⚙️ Backend API

The backend is powered by **Python** and exposes API functionality through `api.py`.

The API acts as the communication layer between the frontend and the AI processing pipeline.

It handles:

* Receiving requests from the frontend
* Processing YouTube URLs or local audio files
* Audio conversion and chunking
* Whisper transcription
* Mistral AI insight generation
* ChromaDB vector indexing
* RAG-based question answering
* Returning structured results to the frontend

---

### 🎧 Audio Acquisition & Processing

* Downloads audio directly from YouTube using `yt-dlp`
* Supports local audio files
* Converts audio to **16kHz mono WAV** format for optimized transcription
* Dynamically splits large audio files into manageable chunks using `pydub`

---

### 🗣️ Local Speech-to-Text

* Performs high-quality transcription locally using **OpenAI Whisper**
* Supports GPU acceleration when available
* Uses `fp16=False` for stable CPU execution
* Processes long-form audio efficiently through chunk-based transcription

---

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

---

### 🔎 Vector Indexing & RAG Engine

* Splits transcripts into semantic chunks using `RecursiveCharacterTextSplitter`
* Generates embeddings with HuggingFace's `all-MiniLM-L6-v2`
* Stores and persists vector data locally using **ChromaDB**
* Retrieves relevant transcript context for every user query
* Generates context-aware answers based on the processed transcript

---

### 💬 Interactive Contextual Q&A

The application provides an interactive **web-based RAG chat interface**.

Users can ask questions about the processed video or audio content, and the backend retrieves relevant transcript context from ChromaDB before generating a response.

This helps keep answers grounded in the original content.

---

## 🏗️ Frontend & Backend Architecture

```text
                ┌───────────────────────┐
                │       FRONTEND        │
                │                       │
                │      HTML             │
                │      CSS              │
                │      JavaScript       │
                │                       │
                │  YouTube URL Input    │
                │  Audio Upload         │
                │  Insights Dashboard   │
                │  RAG Chat Interface   │
                └───────────┬───────────┘
                            │
                            │ HTTP / API Requests
                            ▼
                ┌───────────────────────┐
                │     BACKEND API       │
                │                       │
                │       api.py          │
                │                       │
                │ Python AI Processing  │
                └───────────┬───────────┘
                            │
                            ▼
        ┌────────────────────────────────────────┐
        │          AI PROCESSING PIPELINE        │
        │                                        │
        │ yt-dlp → pydub → Whisper               │
        │                 ↓                      │
        │            Transcript                  │
        │              ↙     ↘                   │
        │       Mistral AI    ChromaDB           │
        │       Insights      Vector Store       │
        │              ↓          ↓              │
        │        Summary       RAG Retrieval     │
        │        Actions            ↓            │
        │        Decisions     AI Response       │
        └────────────────────────────────────────┘
```

---

## 🔄 Application Workflow

```text
User
 │
 ▼
Frontend
HTML + CSS + JavaScript
 │
 │ Submit YouTube URL / Audio
 ▼
Backend API
api.py
 │
 ▼
Audio Download / Processing
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
 ├───────────────────┐
 ▼                   ▼
Mistral AI         ChromaDB
Insights           Vector Database
 │                   │
 ▼                   ▼
Summary          RAG Retrieval
Actions               │
Decisions             ▼
Questions        AI Generated Answer
 │                   │
 └───────────┬───────┘
             ▼
       Frontend Display
```

---

## 📁 Repository Structure

```text
ai-video-agent/
│
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
├── frontend/
│   ├── index.html          # Main application interface
│   ├── style.css           # Application styling and responsive design
│   └── script.js           # Frontend logic and backend API communication
│
├── downloads/              # Downloaded and processed audio files (git-ignored)
├── vector_db/              # Persisted ChromaDB vector database (git-ignored)
│
├── api.py                  # Backend API and frontend communication
├── main.py                 # Core AI processing pipeline
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (git-ignored)
├── .gitignore              # Files excluded from version control
└── README.md               # Project documentation
```

---

## 🛠️ Tech Stack

| Category             | Technology             | Purpose                                                 |
| -------------------- | ---------------------- | ------------------------------------------------------- |
| **Frontend**         | HTML                   | Application structure                                   |
| **Frontend**         | CSS                    | UI design and responsiveness                            |
| **Frontend**         | JavaScript             | Client-side logic and API communication                 |
| **Backend**          | Python 3.11+           | Backend and AI processing                               |
| **Backend API**      | `api.py`               | Handles frontend requests and AI pipeline communication |
| **LLM Framework**    | LangChain              | LLM orchestration and RAG pipeline                      |
| **AI Model**         | Mistral AI             | Insight extraction and response generation              |
| **Speech-to-Text**   | OpenAI Whisper         | Local audio transcription                               |
| **Vector Database**  | ChromaDB               | Persistent vector storage                               |
| **Embeddings**       | HuggingFace Embeddings | Semantic text embeddings                                |
| **Embedding Model**  | Sentence Transformers  | `all-MiniLM-L6-v2`                                      |
| **Audio Processing** | yt-dlp                 | YouTube audio extraction                                |
| **Audio Processing** | pydub                  | Audio conversion and chunking                           |
| **System Tool**      | FFmpeg                 | Audio decoding and processing                           |

---

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

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
MISTRAL_API_KEY=your_mistral_api_key
```

---

## 🚀 Usage

Start the backend API:

```bash
python api.py
```

Then open the frontend application in your browser.

The application allows users to provide:

1. A **YouTube video URL**
2. A **local audio file**

The complete processing pipeline is:

```text
YouTube Video / Local Audio
            ↓
HTML + CSS + JavaScript Frontend
            ↓
Python Backend API
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
Interactive RAG Chat
            ↓
Display Results in Web Interface
```

---

## 🧠 Example Capabilities

Users can ask questions such as:

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

The system retrieves relevant transcript content and uses it to generate a context-aware response.

---

## 🔮 Future Improvements

* Speaker diarization
* Timestamp-based citations
* Multi-language transcription
* Video file upload support
* User authentication
* Chat history and persistent conversations
* Export insights to PDF or DOCX
* User dashboards and workspaces
* Cloud deployment
* Real-time processing status
* Multiple video knowledge bases
* Advanced analytics and transcript visualization

---

## 🎯 Project Goal

The goal of this project is to transform long, unstructured video and audio content into **structured, searchable, and actionable intelligence**.

By combining a modern **HTML, CSS, and JavaScript frontend** with a **Python AI backend**, **Whisper transcription**, **Mistral AI-powered analysis**, and **ChromaDB-powered RAG**, the application creates a complete end-to-end AI video intelligence system.

Users can move beyond simply watching or listening to content and instead **upload, analyze, search, and interact with their video and audio content through an intelligent AI-powered web application**.

---

⭐ If you found this project interesting, consider giving the repository a star!
