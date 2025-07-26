"""
Web-Scraper für HTW Dresden Noten-Portal
"""

import re
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup


class HTWDScraper:
    """Web-Scraper für das HTW Dresden Noten-Portal"""

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.session = None

        # Request-Headers für bessere Kompatibilität
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def _create_session(self) -> Optional[requests.Session]:
        """Erstellt eine neue Session mit Konfiguration"""
        try:
            session = requests.Session()
            session.headers.update(self.headers)

            # Timeout und Retry-Konfiguration
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry

            retry_strategy = Retry(
                total=3,
                status_forcelist=[429, 500, 502, 503, 504],
                method_whitelist=["HEAD", "GET", "OPTIONS", "POST"],
                backoff_factor=1,
            )

            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            return session

        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen der Session: {e}")
            return None

    def _login(self) -> bool:
        """Führt Login auf HTW-Portal durch"""
        try:
            self.session = self._create_session()
            if not self.session:
                return False

            self.logger.debug(f"Starte Login für Benutzer: {self.config.htwd_username}")

            # Erste Anfrage um Login-Seite zu laden
            response = self.session.get(self.config.htwd_url, timeout=10)
            self.logger.log_request_debug(
                self.config.htwd_url, response.status_code, len(response.content)
            )

            if response.status_code != 200:
                self.logger.error(
                    f"Login-Seite nicht erreichbar: HTTP {response.status_code}"
                )
                return False

            # Login-Formular analysieren
            soup = BeautifulSoup(response.text, "html.parser")
            form = soup.find("form")

            if not form:
                self.logger.error("Login-Formular nicht gefunden")
                return False

            # Formular-Daten vorbereiten
            form_data = self._extract_form_data(soup)
            form_data.update(
                {
                    "user": self.config.htwd_username,
                    "pass": self.config.htwd_password,
                    "submit": "Anmelden",
                    "logintype": "login",
                }
            )

            # Login durchführen
            login_response = self.session.post(
                self.config.htwd_url, data=form_data, timeout=10, allow_redirects=True
            )

            self.logger.log_request_debug(
                self.config.htwd_url, login_response.status_code
            )

            # Login-Erfolg prüfen
            if self._is_login_successful(login_response):
                self.logger.info("Login erfolgreich")
                return True
            else:
                self.logger.error("Login fehlgeschlagen - Benutzerdaten prüfen")
                return False

        except requests.exceptions.Timeout:
            self.logger.error("Login-Timeout - Server nicht erreichbar")
            return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Login-Fehler: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unerwarteter Login-Fehler: {e}")
            return False

    def _extract_form_data(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extrahiert versteckte Formular-Daten"""
        form_data = {}

        # Versteckte Input-Felder finden
        hidden_inputs = soup.find_all("input", type="hidden")
        for input_field in hidden_inputs:
            name = input_field.get("name")
            value = input_field.get("value", "")
            if name:
                form_data[name] = value

        if self.config.debug_mode:
            self.logger.debug(f"Extrahierte Formular-Daten: {list(form_data.keys())}")

        return form_data

    def _is_login_successful(self, response: requests.Response) -> bool:
        """Prüft ob Login erfolgreich war"""
        # Verschiedene Erfolgs-Indikatoren prüfen
        success_indicators = [
            "noten-und-pruefungen" in response.url.lower(),
            "anmelden" not in response.text.lower(),
            response.status_code == 200,
        ]

        # Fehler-Indikatoren prüfen
        error_indicators = [
            "fehler" in response.text.lower(),
            "ungültig" in response.text.lower(),
            "benutzername oder passwort" in response.text.lower(),
        ]

        return any(success_indicators) and not any(error_indicators)

    def _parse_grades(self, html_content: str) -> List[Dict[str, str]]:
        """Parst Noten aus HTML-Inhalt"""
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            grades = []

            # Noten-Elemente finden (basierend auf den Screenshots)
            grade_elements = soup.select(
                ".align-items-baseline.collapsed.list-group-item.list-group-custom-item"
            )

            if not grade_elements:
                self.logger.warning(
                    "Keine Noten-Elemente gefunden - möglicherweise Layout-Änderung"
                )
                return []

            for element in grade_elements:
                try:
                    # Note extrahieren
                    grade_span = element.select_one("span")
                    if not grade_span:
                        continue

                    grade_text = grade_span.get_text(strip=True)

                    # Nur numerische Noten (Format: X,X)
                    if not re.match(r"^\d+,\d+$", grade_text):
                        continue

                    # Modul extrahieren
                    module_element = element.select_one("div > h4")
                    if not module_element:
                        continue

                    module_text = module_element.get_text(strip=True)

                    grades.append({"grade": grade_text, "module": module_text})

                except Exception as e:
                    self.logger.warning(f"Fehler beim Parsen eines Noten-Elements: {e}")
                    continue

            if self.config.debug_mode:
                self.logger.log_grades(grades, "Geparste Noten")

            return grades

        except Exception as e:
            self.logger.error(f"Fehler beim Parsen der Noten: {e}")
            return []

    def get_grades(self) -> Optional[List[Dict[str, str]]]:
        """Hauptfunktion zum Abrufen der Noten"""
        try:
            # Login durchführen
            if not self._login():
                return None

            # Noten-Seite laden
            response = self.session.get(self.config.htwd_url, timeout=10)
            self.logger.log_request_debug(self.config.htwd_url, response.status_code)

            if response.status_code != 200:
                self.logger.error(
                    f"Noten-Seite nicht erreichbar: HTTP {response.status_code}"
                )
                return None

            # Noten parsen
            grades = self._parse_grades(response.text)

            if grades:
                self.logger.info(f"{len(grades)} Noten erfolgreich abgerufen")
            else:
                self.logger.warning("Keine Noten gefunden")

            return grades

        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Noten: {e}")
            return None

        finally:
            # Session schließen
            if self.session:
                self.session.close()
                self.session = None
