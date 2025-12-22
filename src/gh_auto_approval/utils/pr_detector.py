import re
from dataclasses import dataclass
from typing import List


PR_URL_PATTERN = re.compile(
    r"<?https?://github\.com/"
    r"(?P<owner>[^/\s]+)/"
    r"(?P<repo>[^/\s]+)/"
    r"pull/(?P<number>\d+)"
    r"(?:[?#][^\s>]+)?"
    r"(?:\|[^>\s]+)?"
    r">?",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class PullRequestRef:
    owner: str
    repo: str
    number: int


class PullRequestDetector:
    def __init__(self, pattern: re.Pattern[str] = PR_URL_PATTERN):
        self._pattern = pattern

    def extract(self, text: str | None) -> List[PullRequestRef]:
        matches: List[PullRequestRef] = []
        for match in self._pattern.finditer(text or ""):
            matches.append(
                PullRequestRef(
                    owner=match.group("owner"),
                    repo=match.group("repo"),
                    number=int(match.group("number")),
                )
            )
        return matches

    def extract_unique(self, text: str | None) -> List[PullRequestRef]:
        """Return unique PRs while preserving deterministic ordering."""
        seen: set[PullRequestRef] = set()
        ordered: List[PullRequestRef] = []
        for pr in self.extract(text):
            if pr not in seen:
                seen.add(pr)
                ordered.append(pr)
        return ordered
