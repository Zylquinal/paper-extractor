import os
from dataclasses import dataclass

from dotenv import load_dotenv

from src.exceptions import ConfigError

load_dotenv()


@dataclass(frozen=True)
class Config:
    api_key: str
    base_url: str
    model: str

    @classmethod
    def from_env(cls) -> "Config":
        api_key = os.getenv("PAPER_PIPELINE_API_KEY")
        base_url = os.getenv("PAPER_PIPELINE_BASE_URL", "https://api.openai.com/v1")
        model = os.getenv("PAPER_PIPELINE_MODEL", "gpt-4o")

        if not api_key:
            raise ConfigError(
                "PAPER_PIPELINE_API_KEY not found in .env. "
                "Copy .env.example to .env and fill in your API key."
            )

        return cls(api_key=api_key, base_url=base_url, model=model)
