# server.py
import asyncio
from main import app, PORT

async def run_server():
    """A robust function to run the server."""
    print(f"Starting server on host 0.0.0.0 and port {PORT}")
    await app.run_async(transport="http", host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\nServer stopped.")