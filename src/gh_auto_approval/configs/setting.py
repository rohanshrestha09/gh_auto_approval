import os
from dataclasses import dataclass


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@dataclass(frozen=True)
class Settings:
    slack_bot_token: str
    slack_signing_secret: str
    slack_app_token: str
    github_token: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            slack_bot_token=_require_env("SLACK_BOT_TOKEN"),
            slack_signing_secret=_require_env("SLACK_SIGNING_SECRET"),
            slack_app_token=_require_env("SLACK_APP_TOKEN"),
            github_token=_require_env("GITHUB_TOKEN"),
        )
