# Web Research Assistant MCP

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful, two-step research agent built as an MCP Tool for the Puch AI Hackathon. This tool gives any AI the ability to access real-time information from the internet, find relevant sources, and read the content of webpages to provide detailed, up-to-date answers.

---
## Features

* **Real-Time Web Search**: Utilizes the Serper API to perform live Google searches for any user query.
* **Webpage Content Scraping**: Can visit a specific URL from the search results and extract its main text content for summarization.
* **Secure Configuration**: Uses environment variables to securely manage API keys and tokens, ready for cloud deployment.
* **Self-Descriptive API**: Includes `about` and `validate` tools for easy integration and verification with the hackathon platform.
* **Deployment**: Deployed via Render.

---

## Example demo:

<p align="center">
  <img width="600" height="800" alt="image" src="https://github.com/user-attachments/assets/c98dfeed-67f2-4162-8307-aac4ce8c1a9c">
</p>

---

[Click here to check it out on Puch AI](https://puch.ai/mcp/33LvRaUqGa)

---

## Setting Up ngrok

`ngrok` is a tool that creates a secure, public URL to your local machine, allowing you to test your server with the Puch AI platform before deploying.

**1. Sign Up for ngrok:**
Go to the [ngrok dashboard](https://dashboard.ngrok.com/signup) and create a free account.

**2. Download ngrok:**
Download the ngrok executable for your operating system (Windows, Mac, or Linux) from the [download page](https://ngrok.com/download). Unzip the file to a location you can easily access.

**3. Connect Your Account:**
To connect your account, you'll need your authtoken. Find it on your ngrok dashboard. Then, run the following command in your terminal, replacing `YOUR_AUTHTOKEN` with the token you copied:
```bash
ngrok config add-authtoken YOUR_AUTHTOKEN
```

---
## Local Setup

To run this project on your local machine, follow these steps:

**1. Clone the repository:**
```bash
git clone https://github.com/Destroyer795/puch-web-research-mcp.git
cd puch-web-research-mcp
```

**2. Create a .env file:**
```bash
TOKEN="12345678"
MY_NUMBER="YOUR_MOBILE_NUMBER_HERE_WITH_COUNTRY_CODE"
SERPER_API_KEY="YOUR_SECRET_SERPER_API_KEY"
```

**3. Install dependencies:**
```bash
# Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # Or on Windows: .venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

**4. Run the server:**
```bash
python server.py
```

**5. Connect to ngrok**
Open a second, separate terminal window and run the following command. This starts the tunnel to your local server.
```bash
ngrok http 8080
```
Running the above command gives a randomly generated url which can be used to connect to the AI platform

**6. Connect to Puch AI**
* Open Puch AI in your browser
* Start a new conversation
* Use the connect command:
```bash
/mcp connect https://your-domain.ngrok.app/mcp your_secret_token_here
```
* Debug Mode:
To get more detailed error messages:
```bash
/mcp diagnostics-level debug
```
