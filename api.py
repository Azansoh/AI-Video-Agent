from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import traceback
import main
from core.rag_engine import ask_question

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store rag_chain and video title state for active chat session
session_data = {
    "rag_chain": None,
    "video_title": None
}


class ProcessRequest(BaseModel):
    source: str
    language: str = "english"


class ChatRequest(BaseModel):
    question: str


@app.post("/api/process")
async def process_video(req: ProcessRequest):
    try:
        # Execute processing pipeline
        results = main.run_pipeline(req.source, language=req.language)

        # Store RAG chain reference and video metadata in session
        session_data["rag_chain"] = main.CURRENT_RAG_CHAIN
        session_data["video_title"] = results.get("title", "Unknown Title")

        return {
            "title": results["title"],
            "summary": results["summary"],
            "action_items": results["action_items"],
            "decisions": results["decisions"],
            "questions": results["questions"],
        }
    except Exception as e:
        print("\n=== API PROCESS ERROR TRACE ===")
        traceback.print_exc()
        print("===============================\n")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def chat(req: ChatRequest):
    active_chain = session_data["rag_chain"] or main.CURRENT_RAG_CHAIN
    video_title = session_data.get("video_title") or "Unknown Title"

    if not active_chain:
        raise HTTPException(
            status_code=400, detail="Please process a video first."
        )

    try:
        answer = ask_question(active_chain, req.question, video_title=video_title)
        return {"answer": answer}
    except Exception as e:
        print("\n=== API CHAT ERROR TRACE ===")
        traceback.print_exc()
        print("============================\n")
        raise HTTPException(status_code=500, detail=str(e))


# Serve static UI files
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
async def serve_index():
    return FileResponse("frontend/index.html")