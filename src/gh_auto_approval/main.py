import subprocess
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request

from services.slack_service import SlackService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()


app = FastAPI()


slack_service = SlackService()
slack_handler = slack_service.get_handler()


@app.get("/")
async def root():
    return "Hello, World!"


@app.get("/gh")
async def gh_health():
    r = subprocess.run(
        ["curl", "-v", "https://api.github.com"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    return {
        "stdout": r.stdout,
        "stderr": r.stderr,
        "code": r.returncode,
    }


@app.post("/slack/events")
async def slack_events(request: Request):
    return await slack_handler.handle(request)
