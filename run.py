"""run.py: one-command entry point for Subscription Ghost.

    python run.py   ->  http://127.0.0.1:8080
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("ghost.api:app", host="127.0.0.1", port=8080, log_level="info")
