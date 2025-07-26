"""
Konfigurationsmanagement für HTW Noten-Checker
"""

import os
from typing import Optional

from dotenv import load_dotenv


class Config:
    """Zentrale Konfigurationsklasse"""

    def __init__(self):
        load_dotenv()
        self._validate_config()

    # HTW Credentials
    @property
    def htwd_url(self) -> str:
        return os.getenv(
            "HTWD_URL",
            "https://mobil.htw-dresden.de/de/mein-studium/noten-und-pruefungen",
        )

    @property
    def htwd_username(self) -> str:
        return os.getenv("HTWD_USERNAME", "")

    @property
    def htwd_password(self) -> str:
        return os.getenv("HTWD_PASSWORD", "")

    # Application Config
    @property
    def poll_interval(self) -> int:
        return int(os.getenv("POLL_INTERVAL", "600"))

    @property
    def post_individual_grades(self) -> bool:
        return os.getenv("POST_GRADES", "true").lower() == "true"

    @property
    def debug_mode(self) -> bool:
        return os.getenv("DEBUG", "false").lower() == "true"

    # Pushbullet Config
    @property
    def pushbullet_enabled(self) -> bool:
        return os.getenv("PUSHBULLET_ENABLED", "false").lower() == "true"

    @property
    def pushbullet_token(self) -> Optional[str]:
        return os.getenv("PUSHBULLET_TOKEN")

    # Telegram Config
    @property
    def telegram_enabled(self) -> bool:
        return os.getenv("TELEGRAM_ENABLED", "false").lower() == "true"

    @property
    def telegram_bot_token(self) -> Optional[str]:
        return os.getenv("TELEGRAM_BOT_TOKEN")

    @property
    def telegram_chat_id(self) -> Optional[str]:
        return os.getenv("TELEGRAM_CHAT_ID")

    # Logging Config
    @property
    def log_level(self) -> str:
        return os.getenv("LOG_LEVEL", "INFO").upper()

    @property
    def log_dir(self) -> str:
        return os.getenv("LOG_DIR", "logs")

    def _validate_config(self):
        """Validiert die wichtigsten Konfigurationswerte"""
        if not self.htwd_username:
            raise ValueError("HTWD_USERNAME ist erforderlich")

        if not self.htwd_password:
            raise ValueError("HTWD_PASSWORD ist erforderlich")

        if self.pushbullet_enabled and not self.pushbullet_token:
            raise ValueError(
                "PUSHBULLET_TOKEN ist erforderlich wenn Pushbullet aktiviert ist"
            )

        if self.telegram_enabled and (
            not self.telegram_bot_token or not self.telegram_chat_id
        ):
            raise ValueError(
                "TELEGRAM_BOT_TOKEN und TELEGRAM_CHAT_ID sind erforderlich wenn Telegram aktiviert ist"
            )

        if not (self.pushbullet_enabled or self.telegram_enabled):
            raise ValueError(
                "Mindestens ein Benachrichtigungsdienst muss aktiviert sein"
            )

    def get_enabled_notification_services(self) -> list:
        """Gibt Liste der aktivierten Benachrichtigungsdienste zurück"""
        services = []
        if self.pushbullet_enabled:
            services.append("pushbullet")
        if self.telegram_enabled:
            services.append("telegram")
        return services
