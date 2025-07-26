"""
Logging-Modul für HTW Noten-Checker
"""

import logging
import sys
from pathlib import Path


class Logger:
    """Zentrale Logging-Klasse mit File- und Console-Output"""

    def __init__(self, log_level: str = "INFO", log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Logger setup
        self.logger = logging.getLogger("htwd_grade_checker")
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # Clear existing handlers
        self.logger.handlers.clear()

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File Handler
        log_file = self.log_dir / "htwd_checker.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Rotating file handler für große Logs
        from logging.handlers import RotatingFileHandler

        rotating_handler = RotatingFileHandler(
            self.log_dir / "htwd_checker_rotating.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding="utf-8",
        )
        rotating_handler.setFormatter(file_formatter)
        self.logger.addHandler(rotating_handler)

    def debug(self, message: str):
        """Debug-Level Logging"""
        self.logger.debug(message)

    def info(self, message: str):
        """Info-Level Logging"""
        self.logger.info(message)

    def warning(self, message: str):
        """Warning-Level Logging"""
        self.logger.warning(message)

    def error(self, message: str):
        """Error-Level Logging"""
        self.logger.error(message)

    def critical(self, message: str):
        """Critical-Level Logging"""
        self.logger.critical(message)

    def log_grades(self, grades: list, title: str = "Aktuelle Noten"):
        """Spezielle Funktion zum Loggen von Noten"""
        self.info(f"=== {title} ===")
        if not grades:
            self.info("Keine Noten gefunden")
            return

        for i, grade in enumerate(grades, 1):
            self.info(f"{i}. {grade['module']}: {grade['grade']}")
        self.info(f"=== Gesamt: {len(grades)} Noten ===")

    def log_request_debug(self, url: str, status_code: int, response_size: int = None):
        """Debug-Logging für HTTP-Requests"""
        size_info = f", {response_size} bytes" if response_size else ""
        self.debug(f"HTTP {status_code} - {url}{size_info}")

    def log_notification_debug(
        self, service: str, success: bool, error_msg: str = None
    ):
        """Debug-Logging für Benachrichtigungen"""
        if success:
            self.debug(f"Benachrichtigung via {service} erfolgreich gesendet")
        else:
            self.error(f"Benachrichtigung via {service} fehlgeschlagen: {error_msg}")

    def log_startup_info(self, config):
        """Startup-Informationen loggen"""
        self.info("=" * 50)
        self.info("HTW Dresden Noten-Checker gestartet")
        self.info("Version: 2.0.0")
        self.info(f"Benutzer: {config.htwd_username}")
        self.info(f"Prüfintervall: {config.poll_interval}s")
        self.info(
            f"Benachrichtigungsdienste: {', '.join(config.get_enabled_notification_services())}"
        )
        self.info(f"Debug-Modus: {'An' if config.debug_mode else 'Aus'}")
        self.info("=" * 50)
