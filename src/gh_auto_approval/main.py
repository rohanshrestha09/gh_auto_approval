import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request

from services.slack_service import SlackService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()


app = FastAPI()


slack_service = SlackService()
slack_request_handler = slack_service.get_request_handler()
slack_socket_handler = slack_service.get_socket_handler()


slack_socket_handler.connect()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/slack/events")
async def slack_events(request: Request):
    return await slack_request_handler.handle(request)
