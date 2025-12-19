"""LLM client for OpenAI API calls."""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_client() -> OpenAI:
    """Get an OpenAI client instance."""
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def call_llm(messages: list[dict]) -> str:
    """Call the LLM with the given messages and return the response."""
    client = get_client()
    model = os.getenv("MODEL", "gpt-4o-mini")
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    
    return response.choices[0].message.content or ""

