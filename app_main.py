"""FitnessAI — AI-powered dietary health management.
Entry point: launches the API server + static frontend.
"""
import uvicorn
from api import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=7862)
