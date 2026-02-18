#!/usr/bin/env python3
"""
Test-Script für Benachrichtigungsdienste
Kann verwendet werden um die Konfiguration zu testen
"""

# Add src to path
import sys

sys.path.append("src")

from src.config import Config
from src.logger import Logger
from src.notifications import NotificationManager


def main():
    print("HTW Noten-Checker - Benachrichtigungstest")
    print("=" * 50)

    try:
        # Konfiguration laden
        config = Config()
        logger = Logger(log_level="INFO")

        # Services anzeigen
        services = config.get_enabled_notification_services()
        print(f"Aktivierte Services: {', '.join(services) if services else 'Keine'}")

        if not services:
            print("❌ Keine Benachrichtigungsdienste aktiviert!")
            print("Bitte aktiviere mindestens einen Service in der .env Datei")
            return 1

        # Notification Manager erstellen
        notification_manager = NotificationManager(config, logger)

        # Test-Benachrichtigung senden
        print("\n🧪 Sende Test-Benachrichtigung...")
        success = notification_manager.test_services()

        if success:
            print("✅ Test erfolgreich! Benachrichtigungen funktionieren.")
            return 0
        else:
            print("❌ Test fehlgeschlagen! Bitte Konfiguration prüfen.")
            return 1

    except ValueError as e:
        print(f"❌ Konfigurationsfehler: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
