#!/usr/bin/env python3
"""
Run the Eternia API server.

This script starts the FastAPI server that provides the API endpoints for the Eternia UI.
"""

import uvicorn

if __name__ == "__main__":
    print("Starting Eternia API server...")
    uvicorn.run("services.api.server:app", host="0.0.0.0", port=8000, reload=True)
    print("Server stopped.")