import subprocess
import json
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

    def approve_pull_request(self, pr: PullRequestRef) -> ApprovalResult:
        url = f"https://api.github.com/repos/{pr.owner}/{pr.repo}/pulls/{pr.number}/reviews"
        payload = json.dumps({"event": "APPROVE"})

        cmd = [
            "curl",
            "-sS",
            "-X",
            "POST",
            url,
            "-H",
            f"Authorization: Bearer {self._settings.github_token}",
            "-H",
            "Accept: application/vnd.github+json",
            "-H",
            "Content-Type: application/json",
            "-H",
            "X-GitHub-Api-Version: 2022-11-28",
            "--connect-timeout",
            "5",
            "--max-time",
            "20",
        ]

        try:
            result = subprocess.run(
                cmd,
                input=payload,
                text=True,
                capture_output=True,
                check=False,
            )

            if result.returncode == 0:
                return ApprovalResult(pr=pr, ok=True, detail="approved")

            return ApprovalResult(
                pr=pr,
                ok=False,
                detail=f"curl failed: {result.stderr}",
            )

        except Exception as exc:
            return ApprovalResult(pr=pr, ok=False, detail=f"request failed: {exc}")
