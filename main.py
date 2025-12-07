import os
from typing import Annotated
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel
from bs4 import BeautifulSoup
from fastmcp import FastMCP
from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
from mcp.server.auth.provider import AccessToken

load_dotenv()

# Configuration
TOKEN = os.getenv("TOKEN", "12345678")
MY_NUMBER = os.getenv("MY_NUMBER")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
PORT = int(os.getenv("PORT", 8080))

# Auth and Models
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

app = FastMCP("Web Research Assistant MCP", auth=SimpleBearerAuthProvider(TOKEN))

# Tool Definitions
ResearchDescription = RichToolDescription(
    description="Performs a web search for a query and provides a detailed summary paragraph, followed by a list of source websites.",
    use_when="When the user asks a question that requires up-to-date information. This is the first step."
)

ScrapeDescription = RichToolDescription(
    description="Extracts all the clean text content from a specific webpage URL. Use this after finding sources with the research tool.",
    use_when="When the user wants the full content of a specific link that was found via web research."
)

# Tools

@app.tool
async def about() -> dict:
    """Returns server metadata."""
    return {
        "name": app.name,
        "description": "Async web research assistant using non-blocking I/O."
    }

@app.tool
async def validate() -> str:
    """Validation for Puch AI Hackathon."""
    return MY_NUMBER if MY_NUMBER else "Validation Number Not Configured"

@app.tool(description=ResearchDescription.model_dump_json())
async def perform_web_research(query: Annotated[str, "The user's question or topic to search for."]) -> dict:
    # Validate config
    if not SERPER_API_KEY:
        return {"message": "Error: SERPER_API_KEY is not set."}
    
    # Validate input
    if not query or not query.strip():
        return {"message": "Error: Search query cannot be empty."}
    
    url = "https://google.serper.dev/search"
    payload = {"q": query, "num": 5}
    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=10.0)
            response.raise_for_status()
            data = response.json()

        if "organic" not in data or not data["organic"]:
            return {"message": f"No results found for '{query}'."}
        
        first_snippet = data["organic"][0].get('snippet', 'No summary available.')
        
        sources = []
        for result in data["organic"]:
            try:
                domain = urlparse(result['link']).netloc
                site = domain.replace('www.', '').split('.')[0].title()
                sources.append(f"- **{result['title']}** (found on {site})")
            except:
                continue

        summary = (
            f"Based on my research for **'{query}'**, here is a summary:\n\n"
            f"{first_snippet}\n\n"
            f"--- \n"
            f"### Where to Learn More\n"
            f"Top sources:\n"
            f"{'\n'.join(sources)}"
        )
        
        return {"message": summary, "results_data": data["organic"]}
        
    except httpx.HTTPStatusError as e:
        return {"message": f"Search API Error ({e.response.status_code}): {e.response.text}"}
    except Exception as e:
        return {"message": f"An unexpected search error occurred: {e}"}

@app.tool(description=ScrapeDescription.model_dump_json())
async def scrape_webpage_content(url: Annotated[str, "URL to read."]) -> dict:
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, headers=headers, timeout=15.0)
            response.raise_for_status()
            
            # Verify content type
            content_type = response.headers.get("content-type", "").lower()
            if "text/html" not in content_type and "text/plain" not in content_type:
                return {"message": f"Error: URL points to '{content_type}', not a webpage."}
            
            content = response.content

        # Parse HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Clean up DOM elements
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()

        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text() for p in paragraphs])
        
        if not text.strip():
            return {"message": "Visited page but found no main text content."}
            
        return {"message": "Extracted text:", "full_text": text.strip()[:5000]}

    except httpx.RequestError as e:
        return {"message": f"Network error: {e}"}
    except Exception as e:
        return {"message": f"Scrape error: {e}"}