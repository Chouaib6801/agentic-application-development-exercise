"""Agent that orchestrates LLM and tools to process prompts."""

from app.llm import call_llm
from app.context import Context
from app.tools.wikipedia import search_wikipedia


AVAILABLE_TOOLS = {
    "wikipedia": search_wikipedia,
}


def process_prompt(prompt: str) -> str:
    """Process a prompt using the agent loop."""
    ctx = Context(prompt=prompt)
    
    # Simple agent loop: ask LLM, optionally use tools, return result
    response = call_llm(ctx.build_messages())
    
    # For now, just return the LLM response directly
    # TODO: Implement tool calling loop
    return response

