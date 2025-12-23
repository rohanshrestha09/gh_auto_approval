import logging
from typing import Iterable, List

from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from slack_bolt.adapter.socket_mode import SocketModeHandler

from gh_auto_approval.configs.setting import Settings
from services.github_service import ApprovalResult
from utils.pr_detector import PullRequestDetector
from services.github_service import GithubService

logger = logging.getLogger(__name__)


class SlackService:
    def __init__(self):
        self._app = App()
        self._settings = Settings.from_env()
        self._github_service = GithubService()
        self._detector = PullRequestDetector()

    def get_request_handler(self) -> SlackRequestHandler:
        self._init_app()
        return SlackRequestHandler(self._app)

    def get_socket_handler(self) -> SocketModeHandler:
        self._init_app()
        return SocketModeHandler(self._app, self._settings.slack_app_token)

    @staticmethod
    def _format_results(results: List[ApprovalResult]) -> str:
        success_lines = [
            f"• {res.pr.owner}/{res.pr.repo}#{res.pr.number}"
            for res in results
            if res.ok
        ]
        failure_lines = [
            f"• {res.pr.owner}/{res.pr.repo}#{res.pr.number}"
            for res in results
            if not res.ok
        ]

        sections: Iterable[str] = []
        if success_lines:
            sections = [*sections, ":white_check_mark: *Approved:*", *success_lines]
        if failure_lines:
            sections = [*sections, ":x: *Failed:*", *failure_lines]

        return "\n".join(sections)

    def _init_app(self):
        @self._app.event("message")
        def handle_events(event, say):
            if event.get("channel_type") != "im":
                return

            text = event.get("text", "")
            prs = self._detector.extract_unique(text)

            if not prs:
                logger.info("No PR links found in DM text='%s'", text)
                return

            results: List[ApprovalResult] = []
            for pr in prs:
                result = self._github_service.approve_pull_request(pr)
                results.append(result)
                if result.ok:
                    logger.info("Approved PR %s/%s #%s", pr.owner, pr.repo, pr.number)
                else:
                    logger.error(
                        "Failed to approve PR %s/%s #%s: %s",
                        pr.owner,
                        pr.repo,
                        pr.number,
                        result.detail,
                    )

            message_text = self._format_results(results)
            if message_text:
                say(message_text)
