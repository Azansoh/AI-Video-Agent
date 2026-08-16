import os
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_mistralai import ChatMistralAI
from core.vector_store import build_vector_store, get_retrieval, load_vector_store


def get_llm():
    return ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.3,
    )


def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])


# Prompt template accepting video metadata alongside transcript context
RAG_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are VideoAgent.ai, an expert AI assistant built to answer questions about video and meeting content.

Video Metadata:
- Video Title: {video_title}

Instructions:
1. If the user asks for the video title, state the Video Title provided above directly.
2. If the user greets you or asks about your capabilities, respond politely and explain how you can help.
3. For questions regarding video/meeting content, answer based on the transcript context provided below.
4. If the answer cannot be found in the context or metadata, reply:
"I could not find this information in the meeting transcript."

Context from meeting transcript:
{context}""",
    ),
    ("human", "{question}"),
])


def build_rag_chain(transcript: str):
    vector_store = build_vector_store(transcript)
    retriever = get_retrieval(vector_store, k=4)
    llm = get_llm()

    rag_chain = (
        {
            "context": itemgetter("question") | retriever | format_docs,
            "question": itemgetter("question"),
            "video_title": itemgetter("video_title"),
        }
        | RAG_PROMPT
        | llm
        | StrOutputParser()
    )

    return rag_chain


def load_rag_chain():
    vector_store = load_vector_store()
    retriever = get_retrieval(vector_store)
    llm = get_llm()

    rag_chain = (
        {
            "context": itemgetter("question") | retriever | format_docs,
            "question": itemgetter("question"),
            "video_title": itemgetter("video_title"),
        }
        | RAG_PROMPT
        | llm
        | StrOutputParser()
    )

    return rag_chain


def ask_question(rag_chain, question: str, video_title: str = "Unknown Title") -> str:
    print(f"Question: {question} | Title: {video_title}")
    
    answer = rag_chain.invoke({
        "question": question,
        "video_title": video_title
    })
    return answer