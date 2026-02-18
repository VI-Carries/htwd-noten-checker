# HTW Dresden Noten-Checker v2.0

Ein containerisierter Service zur automatischen Überwachung neuer Noten im HTW Dresden Portal mit Benachrichtigungen über Pushbullet und Telegram. Unterstützt mehrere Benutzer gleichzeitig.

## ⚠️ Disclaimer

Die Verwendung erfolgt auf eigene Gefahr. Der Autor übernimmt keine Haftung für Schäden durch die Nutzung dieses Scripts. Das Script basiert auf der aktuellen Struktur des HTW-Portals und könnte bei Änderungen nicht mehr funktionieren.

## ⚡ Features

- 🔄 Automatische Überwachung neuer Noten (alle 10 Minuten)
- 👥 Multi-User-Betrieb — mehrere Benutzer parallel überwachen
- 📱 Benachrichtigungen via Pushbullet oder Telegram
- 🐳 Docker-Container für einfaches Deployment
- 📊 Umfassendes Logging mit Rotation (getrennt pro Benutzer)
- 🕐 Intelligente Zeitsteuerung (nur 06:00-22:00 Uhr)
- 🧪 Test-Modi für Entwicklung

## 🚀 Quick Start

### 1. Repository klonen
```bash
git clone https://github.com/MaxPtg/htwd-noten-checker.git
cd htwd-noten-checker
```

### 2. Benutzer einrichten
```bash
make setup USER=s12345  # Erstellt users/s12345.env
```

### 3. Konfiguration bearbeiten

Die erstellte Datei `users/s12345.env` mit den eigenen Daten befüllen:

```bash
# HTW Zugangsdaten
HTWD_USERNAME=s12345
HTWD_PASSWORD=dein_passwort

# Mindestens einen Benachrichtigungsdienst aktivieren
PUSHBULLET_ENABLED=true
PUSHBULLET_TOKEN=o.xxxxxxxxx

# ODER Telegram
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=123456789:AAAAAAAA...
TELEGRAM_CHAT_ID=-123456789
```

### 4. Starten
```bash
make run USER=s12345   # Startet Checker für diesen Benutzer
make logs USER=s12345  # Zeigt Live-Logs an
```

## 👥 Multi-User-Betrieb

Jeder Benutzer bekommt eine eigene `.env`-Datei in `users/` und einen eigenen Docker-Container (`htwd-checker-{username}`). Logs werden getrennt unter `logs/{username}/` gespeichert.

```bash
# Mehrere Benutzer einrichten
make setup USER=s12345
make setup USER=s67890

# Einzeln starten/stoppen
make run USER=s12345
make stop USER=s67890

# Alle gleichzeitig verwalten
make run-all       # Startet alle Benutzer in users/
make stop-all      # Stoppt alle Checker
make status        # Zeigt alle laufenden Checker
```

## 📋 Makefile-Kommandos

```bash
make setup USER=sXXXXX       # User-Config aus Vorlage erstellen
make run USER=sXXXXX         # Checker für Benutzer starten
make stop USER=sXXXXX        # Checker für Benutzer stoppen
make restart USER=sXXXXX     # Checker für Benutzer neu starten
make logs USER=sXXXXX        # Live-Logs eines Benutzers anzeigen
make run-all                 # Alle Benutzer starten
make stop-all                # Alle Benutzer stoppen
make status                  # Alle laufenden Checker anzeigen
make test-notifications USER=sXXXXX  # Benachrichtigungen testen
make test-grades USER=sXXXXX         # Neue Noten simulieren
make clean                   # Alle Container und Images entfernen
make dev                     # Lokale Entwicklungsumgebung einrichten
```

## 🔧 Benachrichtigungsdienste einrichten

### Pushbullet
1. Account auf [pushbullet.com](https://www.pushbullet.com) erstellen
2. API-Token unter [Settings > Access Tokens](https://www.pushbullet.com/#settings/account) generieren
3. Token in die User-Config eintragen

**Vollständige Anleitung:** [Pushbullet API Documentation](https://docs.pushbullet.com/)

### Telegram Bot
1. **Bot erstellen:** [@BotFather](https://t.me/botfather) kontaktieren → `/newbot` → Bot-Token erhalten
2. **Gruppe erstellen:** Neue Telegram-Gruppe erstellen
3. **Bot hinzufügen:** Bot zur Gruppe hinzufügen und zum Admin machen
4. **Chat-ID ermitteln:**
   - Bot zu Gruppe hinzufügen
   - Nachricht in Gruppe senden
   - `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates` aufrufen
   - `chat.id` aus Response kopieren (negative Zahl für Gruppen)

**Ausführliche Tutorials:**
- [Telegram Bot erstellen](https://core.telegram.org/bots/tutorial)
- [Bot-API Dokumentation](https://core.telegram.org/bots/api)
- [Chat-ID finden](https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id)

## 🧪 Testen

```bash
# Benachrichtigungen testen
make test-notifications USER=s12345

# Neue Noten simulieren (Mock-Daten)
make test-grades USER=s12345
```

## 💻 Lokale Entwicklung

```bash
make dev  # Erstellt venv und installiert Dependencies automatisch
```

Das venv wird automatisch erstellt und die Dependencies installiert (Linux/Mac/Windows). Danach das venv aktivieren:

```bash
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows
```

## 📁 Projektstruktur

```
htwd-noten-checker/
├── src/
│   ├── main.py           # Hauptanwendung
│   ├── config.py         # Konfiguration
│   ├── scraper.py        # HTW Web-Scraper
│   ├── notifications.py  # Benachrichtigungsdienste
│   └── logger.py         # Logging-System
├── users/                # User-Konfigurationen (.env pro User)
├── logs/                 # Logs (getrennt pro User)
├── docker-compose.yml    # Container-Konfiguration (Multi-User)
├── Dockerfile            # Container-Definition
├── Makefile              # Entwickler-Kommandos
└── .env.example          # Konfigurationsvorlage
```

---

**Version:** 2.1.0 | **Author:** Max Patecky | **License:** MIT
