#!/usr/bin/env python3
"""
Test-Script für die Simulation neuer Noten
Dieses Script simuliert den Grade-Checker mit Mock-Daten
"""

import signal
import sys
import time
from datetime import datetime
from typing import Dict, List

# Add src to path
sys.path.append("src")

from src.config import Config
from src.logger import Logger
from src.notifications import NotificationManager


class MockGradeChecker:
    """Mock-Version des Grade-Checkers für Tests"""

    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.notification_manager = NotificationManager(self.config, self.logger)

        self.running = True
        self.previous_grades = []
        self.cycle_count = 0

        # Signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Behandelt Shutdown-Signale"""
        self.logger.info(f"Signal {signum} empfangen. Beende Test...")
        self.running = False

    def _get_mock_grades(self) -> List[Dict[str, str]]:
        """Generiert Mock-Noten mit simulierten neuen Noten"""

        # Basis-Noten (immer vorhanden)
        base_grades = [
            {"grade": "1,3", "module": "Mathematik I"},
            {"grade": "2,0", "module": "Programmierung"},
            {"grade": "1,7", "module": "Datenbanken"},
            {"grade": "2,3", "module": "Betriebssysteme"},
        ]

        # Neue Noten basierend auf Zyklen hinzufügen
        self.cycle_count += 1

        # Jeder 3. Zyklus = neue Note
        if self.cycle_count % 3 == 0:
            new_modules = [
                "Algorithmen und Datenstrukturen",
                "Software Engineering",
                "Computergrafik",
                "Künstliche Intelligenz",
                "Netzwerktechnik",
                "IT-Sicherheit",
            ]

            # Zufällige Note zwischen 1,0 und 2,7
            import random

            grades_pool = ["1,0", "1,3", "1,7", "2,0", "2,3", "2,7"]

            module_index = (self.cycle_count // 3 - 1) % len(new_modules)
            new_grade = {
                "grade": random.choice(grades_pool),
                "module": new_modules[module_index],
            }

            base_grades.append(new_grade)
            self.logger.info(
                f"🎯 SIMULATION: Neue Note hinzugefügt - {new_grade['module']}: {new_grade['grade']}"
            )

        return base_grades

    def _find_new_grades(self, current_grades: list) -> list:
        """Findet neue Noten durch Vergleich mit vorherigen"""
        new_grades = []

        for grade in current_grades:
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
            "HTW Noten Update (TEST)", f"{len(new_grades)} neue Note(n) verfügbar!"
        )

        # Einzelne Noten benachrichtigen (wenn aktiviert)
        if self.config.post_individual_grades:
            for grade in new_grades:
                self.notification_manager.send_notification(
                    f"{grade['module']} (TEST)", f"Note: {grade['grade']}"
                )

    def _check_for_new_grades(self):
        """Überprüft auf neue Noten"""
        try:
            # Mock-Noten abrufen
            current_grades = self._get_mock_grades()

            # Erste Ausführung
            if not self.previous_grades:
                self.previous_grades = current_grades
                self.logger.info(
                    f"Initialisierung: {len(current_grades)} Mock-Noten geladen"
                )
                return

            # Neue Noten suchen
            new_grades = self._find_new_grades(current_grades)

            if new_grades:
                self.logger.info(f"🚨 {len(new_grades)} neue Note(n) gefunden!")
                for grade in new_grades:
                    self.logger.info(f"   📝 {grade['module']}: {grade['grade']}")

                self._send_notifications(new_grades)
                self.previous_grades = current_grades
            else:
                self.logger.info(
                    f"Keine neuen Noten ({len(current_grades)} Noten total)"
                )

        except Exception as e:
            self.logger.error(f"Fehler beim Überprüfen der Mock-Noten: {e}")

    def run(self):
        """Hauptschleife der Test-Anwendung"""
        self.logger.info("🧪 HTW Noten-Checker TEST-MODUS gestartet!")
        self.logger.info("=" * 50)
        self.logger.info("🎯 Simuliert alle 3 Zyklen eine neue Note")
        self.logger.info(f"⏱️  Prüfintervall: {self.config.poll_interval} Sekunden")
        self.logger.info("🛑 Stoppen mit Ctrl+C")
        self.logger.info("=" * 50)

        # Startup-Benachrichtigung
        self.notification_manager.send_notification(
            "HTW Noten-Checker (TEST)",
            f"Test-Modus gestartet um {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}",
        )

        # Hauptschleife
        while self.running:
            try:
                self._check_for_new_grades()

                # Countdown für nächste Prüfung
                for remaining in range(self.config.poll_interval, 0, -1):
                    if not self.running:
                        break

                    if remaining <= 5:  # Letzte 5 Sekunden anzeigen
                        print(
                            f"\r⏳ Nächste Prüfung in {remaining}s...",
                            end="",
                            flush=True,
                        )

                    time.sleep(1)

                if self.running:
                    print("\r" + " " * 30 + "\r", end="")  # Clear countdown

            except KeyboardInterrupt:
                self.logger.info("Benutzer-Interrupt empfangen")
                break
            except Exception as e:
                self.logger.error(f"Unerwarteter Fehler: {e}")
                time.sleep(10)

        self.logger.info("🧪 HTW Noten-Checker TEST-MODUS beendet")


def main():
    """Haupteinstiegspunkt"""
    print("🧪 HTW Dresden Noten-Checker - TEST-MODUS")
    print("=" * 50)
    print("Dieser Modus simuliert neue Noten ohne echte HTW-Verbindung")
    print("Perfekt zum Testen der Benachrichtigungen!")
    print()

    try:
        checker = MockGradeChecker()
        checker.run()
    except Exception as e:
        print(f"❌ Kritischer Fehler beim Start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
