import os
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_mistralai import ChatMistralAI


def get_llm():
    return ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.3,
    )


def build_chain(system_prompt: str):
    llm = get_llm()
    return (
        RunnablePassthrough()
        | RunnableLambda(lambda x: {"text": x})
        | ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{text}"),
        ])
        | llm
        | StrOutputParser()
    )


def extract_action_items(transcript: str) -> str:
    prompt = (
        "You are an expert meeting analyst. From the meeting transcript, "
        "extract all action items. For each provide:\n"
        "- Task description\n"
        "- Owner (who is responsible)\n"
        "- Deadline (if mentioned, else write 'Not specified')\n"
        "Format as a numbered list. If none found, say 'No action items found.'"
    )
    chain = build_chain(prompt)
    return chain.invoke(transcript)


def extract_decisions(transcript: str) -> str:
    prompt = (
        "You are an expert meeting analyst. From the meeting transcript, "
        "extract all key decisions that were agreed upon.\n"
        "Format as a bulleted list. If none found, say 'No key decisions found.'"
    )
    chain = build_chain(prompt)
    return chain.invoke(transcript)


def extract_questions(transcript: str) -> str:
    prompt = (
        "You are an expert meeting analyst. From the meeting transcript, "
        "extract all unresolved questions, open issues, or pending inquiries.\n"
        "Format as a bulleted list. If none found, say 'No unresolved questions found.'"
    )
    chain = build_chain(prompt)
    return chain.invoke(transcript)