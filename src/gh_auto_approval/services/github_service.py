import requests
from dataclasses import dataclass

from configs.setting import Settings
from utils.pr_detector import PullRequestRef


@dataclass(frozen=True)
class ApprovalResult:
    pr: PullRequestRef
    ok: bool
    detail: str


class GithubService:
    def __init__(self):
        self._settings = Settings.from_env()
        self._session = requests.Session()

    def approve_pull_request(self, pr: PullRequestRef) -> ApprovalResult:
        url = f"https://api.github.com/repos/{pr.owner}/{pr.repo}/pulls/{pr.number}/reviews"
        headers = {
            "Authorization": f"Bearer {self._settings.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        payload = {"event": "APPROVE"}
        try:
            response = self._session.post(
                url, headers=headers, json=payload, timeout=10
            )
            if response.status_code in (200, 201):
                return ApprovalResult(pr=pr, ok=True, detail="approved")
            return ApprovalResult(
                pr=pr, ok=False, detail=f"{response.status_code}: {response.text}"
            )
        except requests.RequestException as exc:
            return ApprovalResult(pr=pr, ok=False, detail=f"request failed: {exc}")
