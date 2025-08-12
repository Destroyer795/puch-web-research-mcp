import os
import json
import requests
from dotenv import load_dotenv
from typing import Annotated, Dict
from pydantic import BaseModel
from bs4 import BeautifulSoup
from fastmcp import FastMCP
from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
from mcp.server.auth.provider import AccessToken

# Load environment variables from a .env file for local testing
load_dotenv()

# --- Securely Load Secrets from Environment Variables ---
TOKEN = os.getenv("TOKEN", "12345678")
MY_NUMBER = os.getenv("MY_NUMBER", "YOUR_MOBILE_NUMBER_HERE")
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "YOUR_SERPER_API_KEY_HERE")

# --- Models and Auth ---
class RichToolDescription(BaseModel):
    description: str
    use_when: str

class SimpleBearerAuthProvider(BearerAuthProvider):
    def __init__(self, token: str):
        k = RSAKeyPair.generate()
        super().__init__(public_key=k.public_key, jwks_uri=None, issuer=None, audience=None)
        self.token = token
    async def load_access_token(self, token: str) -> AccessToken | None:
        if token == self.token:
            return AccessToken(token=token, client_id="unknown", scopes=[], expires_at=None)
        return None

mcp_server = FastMCP("Web Research Assistant MCP", auth=SimpleBearerAuthProvider(TOKEN))

# --- Tool Descriptions ---
ResearchDescription = RichToolDescription(
    description="Performs an initial web search for a query to find relevant sources.",
    use_when="When the user asks a question that requires up-to-date information. This is the first step."
)
ScrapeDescription = RichToolDescription(
    description="Extracts all the clean text content from a specific webpage URL. Use this after finding sources with the research tool.",
    use_when="When the user wants a detailed summary or the full content of a specific link that was found via web research."
)

# --- The Research Tools ---
@mcp_server.tool
async def validate() -> str:
    """Validation tool for the Puch AI Hackathon."""
    return MY_NUMBER

@mcp_server.tool(description=ResearchDescription.model_dump_json())
def perform_web_research(query: Annotated[str, "The user's question or topic to search for."]) -> dict:
    if not SERPER_API_KEY or "YOUR_SERPER_API_KEY_HERE" in SERPER_API_KEY:
        return {"message": "Error: The SERPER_API_KEY is not configured in the tool server."}
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query, "num": 5})
    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        search_results = response.json()
        if "organic" not in search_results or not search_results["organic"]:
            return {"message": f"I couldn't find any web results for '{query}'."}
        summary_parts = [f"I found these top results for **'{query}'**. Which one would you like me to read and summarize in detail?\n"]
        for i, result in enumerate(search_results["organic"]):
            summary_parts.append(f"\n{i+1}. **{result['title']}**\n   *Source: {result['link']}*")
        message = "\n".join(summary_parts)
        return {"message": message, "results_data": search_results["organic"]}
    except Exception as e:
        return {"message": f"An unexpected error occurred during web search: {e}"}

@mcp_server.tool(description=ScrapeDescription.model_dump_json())
def scrape_webpage_content(url: Annotated[str, "The URL of the webpage to read."]) -> dict:
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')
        paragraphs = soup.find_all('p')
        full_text = ' '.join([p.get_text() for p in paragraphs])
        if not full_text:
            return {"message": "I visited the page, but I couldn't find any main article text to summarize."}
        return {"message": "Here is the extracted text for summarization:", "full_text": full_text.strip()}
    except Exception as e:
        return {"message": f"Sorry, I was unable to read the content from that URL. Error: {e}"}

# --- Main Server Execution ---
async def main():
    """Runs the MCP server."""
    print("Starting Web Research Assistant MCP Server...")
    await mcp_server.run_async("streamable-http", host="0.0.0.0", port=8080)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())