#!/usr/bin/env python3
"""
HTW Dresden Noten-Checker - Modernisierte Version

Author: Max Patecky
Version: 2.0.0
License: MIT

Überwacht automatisch neue Noten im HTW Dresden Portal
und sendet Benachrichtigungen über verschiedene Dienste.
"""

import signal
import sys
import time
from datetime import datetime

from config import Config
from logger import Logger
from notifications import NotificationManager
from scraper import HTWDScraper


class GradeChecker:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.scraper = HTWDScraper(self.config, self.logger)
        self.notification_manager = NotificationManager(self.config, self.logger)

        self.running = True
        self.previous_grades = []

        # Signal handlers für graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Behandelt Shutdown-Signale"""
        self.logger.info(f"Signal {signum} empfangen. Beende Anwendung...")
        self.running = False

    def _is_active_time(self) -> bool:
        """Prüft ob aktuell aktive Zeit ist (06:00-22:00)"""
        now = datetime.now().time()
        start_time = datetime.strptime("06:00", "%H:%M").time()
        end_time = datetime.strptime("22:00", "%H:%M").time()
        return start_time <= now <= end_time

    def _check_for_new_grades(self):
        """Überprüft auf neue Noten"""
        try:
            # Aktive Zeit prüfen
            if not self._is_active_time():
                self.logger.info("Außerhalb der aktiven Zeit (06:00-22:00). Warte...")
                return

            # Noten abrufen
            current_grades = self.scraper.get_grades()
            if current_grades is None:
                self.logger.warning("Konnte keine Noten abrufen")
                return

            # Erste Ausführung
            if not self.previous_grades:
                self.previous_grades = current_grades
                self.logger.info(
                    f"Initialisierung: {len(current_grades)} Noten gefunden"
                )
                return

            # Neue Noten suchen
            new_grades = self._find_new_grades(current_grades)

            if new_grades:
                self.logger.info(f"{len(new_grades)} neue Note(n) gefunden!")
                self._send_notifications(new_grades)
                self.previous_grades = current_grades
            else:
                self.logger.info(
                    f"Keine neuen Noten ({len(current_grades)} Noten total)"
                )

        except Exception as e:
            self.logger.error(f"Fehler beim Überprüfen der Noten: {e}")

    def _find_new_grades(self, current_grades: list) -> list:
        """Findet neue Noten durch Vergleich mit vorherigen"""
        new_grades = []

        for grade in current_grades:
            # Prüfe ob Note bereits in vorherigen Noten vorhanden
            is_new = True
            for prev_grade in self.previous_grades:
                if (
                    grade["module"] == prev_grade["module"]
                    and grade["grade"] == prev_grade["grade"]
                ):
                    is_new = False
                    break

            if is_new:
                new_grades.append(grade)

        return new_grades

    def _send_notifications(self, new_grades: list):
        """Sendet Benachrichtigungen für neue Noten"""
        # Allgemeine Benachrichtigung
        self.notification_manager.send_notification(
            "HTW Noten Update", f"{len(new_grades)} neue Note(n) verfügbar!"
        )

        # Einzelne Noten benachrichtigen (wenn aktiviert)
        if self.config.post_individual_grades:
            for grade in new_grades:
                self.notification_manager.send_notification(
                    grade["module"], f"Note: {grade['grade']}"
                )

    def run(self):
        """Hauptschleife der Anwendung"""
        self.logger.info("HTW Noten-Checker gestartet!")
        self.logger.info(f"Benutzer: {self.config.htwd_username}")
        self.logger.info(f"Prüfintervall: {self.config.poll_interval} Sekunden")

        # Startup-Benachrichtigung
        self.notification_manager.send_notification(
            "HTW Noten-Checker",
            f"Checker gestartet um {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}",
        )

        # Hauptschleife
        while self.running:
            try:
                self._check_for_new_grades()

                # Warten mit Interruption-Check
                for _ in range(self.config.poll_interval):
                    if not self.running:
                        break
                    time.sleep(1)

            except KeyboardInterrupt:
                self.logger.info("Benutzer-Interrupt empfangen")
                break
            except Exception as e:
                self.logger.error(f"Unerwarteter Fehler: {e}")
                time.sleep(60)  # Warte eine Minute bei Fehlern

        self.logger.info("HTW Noten-Checker beendet")


def main():
    """Haupteinstiegspunkt"""
    try:
        checker = GradeChecker()
        checker.run()
    except Exception as e:
        print(f"Kritischer Fehler beim Start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
