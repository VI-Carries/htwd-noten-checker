# HTW Dresden Noten-Checker v2.0

Ein containerisierter Service zur automatischen Überwachung neuer Noten im HTW Dresden Portal mit Benachrichtigungen über Pushbullet und Telegram.

## ⚡ Features

- 🔄 Automatische Überwachung neuer Noten (alle 10 Minuten)
- 📱 Benachrichtigungen via Pushbullet oder Telegram
- 🐳 Docker-Container für einfaches Deployment
- 📊 Umfassendes Logging mit Rotation
- 🕐 Intelligente Zeitsteuerung (nur 06:00-22:00 Uhr)
- 🧪 Test-Modi für Entwicklung

## 🚀 Quick Start

### 1. Repository klonen
```bash
git clone https://github.com/MaxPtg/htwd-noten-checker.git
cd htwd-noten-checker
```

### 2. Konfiguration erstellen
```bash
make setup  # Erstellt .env aus .env.example
```

### 3. .env-Datei bearbeiten
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
make run    # Startet Container im Hintergrund
make logs   # Zeigt Live-Logs an
```

## 📋 Makefile-Kommandos

```bash
make setup              # .env aus Vorlage erstellen
make run                # Container starten
make logs               # Live-Logs anzeigen
make stop               # Container stoppen
make test-notifications # Benachrichtigungen testen
make test-grades        # Neue Noten simulieren
make clean              # Alles aufräumen
```

## 🔧 Benachrichtigungsdienste einrichten

### Pushbullet
1. Account auf [pushbullet.com](https://www.pushbullet.com) erstellen
2. API-Token unter [Settings > Access Tokens](https://www.pushbullet.com/#settings/account) generieren
3. Token in `.env` eintragen

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
make test-notifications

# Neue Noten simulieren (Mock-Daten)
make test-grades
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
├── docker-compose.yml    # Container-Konfiguration
├── Dockerfile           # Container-Definition
├── Makefile            # Entwickler-Kommandos
└── .env.example        # Konfigurationsvorlage
```

## ⚠️ Disclaimer

Die Verwendung erfolgt auf eigene Gefahr. Der Autor übernimmt keine Haftung für Schäden durch die Nutzung dieses Scripts. Das Script basiert auf der aktuellen Struktur des HTW-Portals und könnte bei Änderungen nicht mehr funktionieren.

---

**Version:** 2.0.0 | **Author:** Max Patecky | **License:** MIT
