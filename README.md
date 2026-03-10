# EcoHelper

An environmental mentor chatbot that helps people live more sustainably. Built with a Langchain agent, local Llama 3.2 model, and three real-time data tools that ground its responses in actual data instead of guesses.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![React](https://img.shields.io/badge/React-18-61DAFB)
![LangChain](https://img.shields.io/badge/LangChain-Agent-green)
![Llama](https://img.shields.io/badge/Llama-3.2-purple)

## Demo

https://youtu.be/uo9xc25K2w4 

## What It Does

EcoHelper answers environmental questions using a combination of a local LLM, a curated knowledge base, and live external APIs. Instead of relying purely on the model's training data (which can hallucinate numbers, especially for real-time data), it routes questions through a tool-calling system that fetches grounded, accurate information.

For example, you can ask something like:

*"Depending on the air quality in Denver today, should I still go for a run, and how much CO2 would driving 10 miles to the gym produce?"*

The agent will call the air quality tool for Denver's current AQI, call the carbon emissions tool to estimate driving emissions, and then synthesize both into a coherent recommendation.

## Architecture

```
React Frontend ──► FastAPI Backend ──► LangChain Agent ──► Llama 3.2 (local)
                                            │
                                            ├── RAG Tool (ChromaDB)
                                            ├── Air Quality Tool (WAQI API)
                                            └── Carbon Emissions Tool (Climatiq API)
```

The frontend is a React chat UI. The backend is a FastAPI server that receives user messages, passes them to a LangChain agent, and returns the response. The agent decides which tools (if any) to invoke based on the question, executes them, and feeds the results into the LLM's context as ground truth.

## Tools

### RAG (Retrieval-Augmented Generation)

Performs semantic search over a curated set of environmental resources scraped from sources like the EPA, Energy.gov, and Earth911. Documents are scraped with newspaper3k, chunked, embedded with nomic-embed-text, and stored in a ChromaDB collection. When a user asks a general sustainability question, relevant chunks are retrieved and injected into the prompt as context.

### Air Quality (WAQI API)

Fetches live Air Quality Index data and pollutant measurements for any city. Takes a city name, queries the World Air Quality Index API, and returns the AQI value along with individual pollutant readings. The system prompt instructs the LLM to treat these numbers as authoritative and not fabricate its own.

### Carbon Emissions (Climatiq API)

Estimates carbon emissions for driving or flying a given distance. Sends the mode of transport, distance, and unit to the Climatiq API, which returns a calculated emissions estimate. Useful for comparing travel options or understanding the environmental cost of a trip.

## Tool Routing

An `execute_tools` function binds all three tools to the LLM, uses a routing prompt via `SystemMessage` to determine which tools are needed for a given question, invokes them, and passes the results into the overall context. The LLM then uses that real data to generate its final answer.

This means a single complex question can trigger multiple tools in one pass. The system prompt enforces that tool outputs are treated as ground truth, preventing the model from overriding real data with hallucinated values.

## Tech Stack

- **LLM**: Llama 3.2 (local, via Ollama)
- **Agent Framework**: LangChain
- **Backend**: FastAPI (Python)
- **Frontend**: React
- **Vector Store**: ChromaDB
- **Embeddings**: nomic-embed-text
- **Web Scraping**: newspaper3k
- **External APIs**: WAQI (air quality), Climatiq (carbon emissions)

## Setup

### Prerequisites

- Python 3.10+
- Node.js
- [Ollama](https://ollama.com/) with Llama 3.2 installed and running
- Free API keys (see below)

### API Keys

This project uses two free public APIs. Get your keys here:

- **WAQI**: https://aqicn.org/data-platform/token/
- **Climatiq**: https://www.climatiq.io/docs

Add them to a `.env` file in the backend directory.

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Once both are running, open localhost to use the chatbot.

### Notes

- This runs a local LLM, so make sure you have it installed and running before starting the backend. Feel free to swap in a different model if you prefer.
- The ChromaDB vector store is not included in the repo (it's generated from the scraping pipeline). Run the ingestion script to build it locally.

## Project Structure

```
ecohelper/
├── backend/
│   ├── main.py              # FastAPI server + LangChain agent
│   ├── tools/               # Tool definitions (RAG, WAQI, Climatiq)
│   ├── .env                 # API keys (not committed)
│   └── requirements.txt
├── frontend/
│   ├── src/                 # React chat UI
│   └── package.json
├── docs/
│   └── final_report.pdf     # Project writeup
├── .gitignore
└── README.md
```