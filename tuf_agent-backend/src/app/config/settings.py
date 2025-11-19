import os
from typing import Optional

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    # Proceed without .env auto-loading if python-dotenv is not installed
    pass


class Settings:
    def __init__(self) -> None:
        self.GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
        self.TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")

        missing = [k for k, v in {
            "GOOGLE_API_KEY": self.GOOGLE_API_KEY,
            "TAVILY_API_KEY": self.TAVILY_API_KEY,
        }.items() if not v]

        if missing:
            raise RuntimeError(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Ensure they are set in the environment or in a .env file at project root."
            )
 

settings = Settings()
