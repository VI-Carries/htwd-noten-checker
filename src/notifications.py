"""
Benachrichtigungsmanager für verschiedene Dienste
"""

import json

import requests


class NotificationService:
    """Basis-Klasse für Benachrichtigungsdienste"""

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def send(self, title: str, message: str) -> bool:
        """Sendet Benachrichtigung - muss von Subklassen implementiert werden"""
        raise NotImplementedError


class PushbulletService(NotificationService):
    """Pushbullet-Benachrichtigungsdienst"""

    API_URL = "https://api.pushbullet.com/v2/pushes"

    def send(self, title: str, message: str) -> bool:
        """Sendet Pushbullet-Benachrichtigung"""
        try:
            if not self.config.pushbullet_token:
                self.logger.error("Pushbullet-Token nicht konfiguriert")
                return False

            data = {"type": "note", "title": title, "body": message}

            headers = {
                "Access-Token": self.config.pushbullet_token,
                "Content-Type": "application/json",
            }

            response = requests.post(
                self.API_URL, data=json.dumps(data), headers=headers, timeout=10
            )

            if response.status_code == 200:
                self.logger.log_notification_debug("Pushbullet", True)
                return True
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg += f": {error_data['error']}"
                except:
                    pass

                self.logger.log_notification_debug("Pushbullet", False, error_msg)
                return False

        except requests.exceptions.Timeout:
            self.logger.log_notification_debug("Pushbullet", False, "Timeout")
            return False
        except requests.exceptions.RequestException as e:
            self.logger.log_notification_debug("Pushbullet", False, str(e))
            return False
        except Exception as e:
            self.logger.log_notification_debug(
                "Pushbullet", False, f"Unerwarteter Fehler: {e}"
            )
            return False


class TelegramService(NotificationService):
    """Telegram-Bot-Benachrichtigungsdienst"""

    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.api_url = f"https://api.telegram.org/bot{config.telegram_bot_token}"

    def send(self, title: str, message: str) -> bool:
        """Sendet Telegram-Benachrichtigung"""
        try:
            if not self.config.telegram_bot_token or not self.config.telegram_chat_id:
                self.logger.error("Telegram-Konfiguration unvollständig")
                return False

            # Nachricht formatieren
            full_message = f"*{title}*\n{message}"

            # URL für Telegram API
            url = f"{self.api_url}/sendMessage"

            data = {
                "chat_id": self.config.telegram_chat_id,
                "text": full_message,
                "parse_mode": "Markdown",
            }

            response = requests.post(url, data=data, timeout=10)

            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    self.logger.log_notification_debug("Telegram", True)
                    return True
                else:
                    error_msg = result.get("description", "Unbekannter API-Fehler")
                    self.logger.log_notification_debug("Telegram", False, error_msg)
                    return False
            else:
                self.logger.log_notification_debug(
                    "Telegram", False, f"HTTP {response.status_code}"
                )
                return False

        except requests.exceptions.Timeout:
            self.logger.log_notification_debug("Telegram", False, "Timeout")
            return False
        except requests.exceptions.RequestException as e:
            self.logger.log_notification_debug("Telegram", False, str(e))
            return False
        except Exception as e:
            self.logger.log_notification_debug(
                "Telegram", False, f"Unerwarteter Fehler: {e}"
            )
            return False


class NotificationManager:
    """Manager für alle Benachrichtigungsdienste"""

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.services = []

        # Aktivierte Services initialisieren
        if config.pushbullet_enabled:
            self.services.append(PushbulletService(config, logger))

        if config.telegram_enabled:
            self.services.append(TelegramService(config, logger))

        if not self.services:
            self.logger.warning("Keine Benachrichtigungsdienste aktiviert!")

    def send_notification(self, title: str, message: str) -> bool:
        """Sendet Benachrichtigung über alle aktivierten Dienste"""
        if not self.services:
            self.logger.warning("Keine Benachrichtigungsdienste verfügbar")
            return False

        success_count = 0

        for service in self.services:
            try:
                if service.send(title, message):
                    success_count += 1
            except Exception as e:
                service_name = service.__class__.__name__
                self.logger.error(f"Fehler bei {service_name}: {e}")

        # Erfolgreich wenn mindestens ein Service funktioniert hat
        success = success_count > 0

        if success:
            self.logger.info(
                f"Benachrichtigung gesendet: '{title}' ({success_count}/{len(self.services)} Services)"
            )
        else:
            self.logger.error(
                f"Alle Benachrichtigungsdienste fehlgeschlagen für: '{title}'"
            )

        return success

    def test_services(self) -> bool:
        """Testet alle konfigurierten Benachrichtigungsdienste"""
        self.logger.info("Teste Benachrichtigungsdienste...")

        test_title = "HTW Noten-Checker Test"
        test_message = "Dies ist eine Test-Benachrichtigung"

        return self.send_notification(test_title, test_message)
