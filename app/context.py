"""Context management for agent conversations."""

from pydantic import BaseModel


class Context(BaseModel):
    """Holds the context for an agent conversation."""
    
    prompt: str
    history: list[dict] = []
    tool_results: list[dict] = []
    
    def build_messages(self) -> list[dict]:
        """Build the messages list for the LLM."""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": self.prompt},
        ]
        messages.extend(self.history)
        return messages
    
    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to history."""
        self.history.append({"role": "assistant", "content": content})
    
    def add_tool_result(self, tool_name: str, result: str) -> None:
        """Add a tool result to context."""
        self.tool_results.append({"tool": tool_name, "result": result})


