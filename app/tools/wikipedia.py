"""Wikipedia search tool."""

import requests


def search_wikipedia(query: str) -> str:
    """Search Wikipedia and return a summary."""
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(" ", "_")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("extract", "No summary found.")
    except requests.RequestException as e:
        return f"Error searching Wikipedia: {e}"


