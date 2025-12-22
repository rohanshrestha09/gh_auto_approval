import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
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
        self._session = self._build_session()

    @staticmethod
    def _build_session() -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=None,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(
            max_retries=retry,
            pool_connections=1,
            pool_maxsize=1,
        )
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def approve_pull_request(self, pr: PullRequestRef) -> ApprovalResult:
        url = f"https://api.github.com/repos/{pr.owner}/{pr.repo}/pulls/{pr.number}/reviews"
        headers = {
            "Authorization": f"Bearer {self._settings.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Connection": "close",
        }
        payload = {"event": "APPROVE"}

        try:
            with self._session.post(
                url, headers=headers, json=payload, timeout=(5, 20),
            ) as response:
                if response.status_code in (200, 201):
                    return ApprovalResult(pr=pr, ok=True, detail="approved")
                return ApprovalResult(
                    pr=pr, ok=False, detail=f"{response.status_code}: {response.text}"
                )
        except requests.RequestException as exc:
            return ApprovalResult(pr=pr, ok=False, detail=f"request failed: {exc}")
