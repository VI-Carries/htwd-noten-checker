# HTW Noten-Checker Makefile

.PHONY: help build run stop restart logs logs-all clean setup test-grades test-notifications dev status run-all stop-all

USER ?=

# Default target
help:
	@echo "HTW Dresden Noten-Checker v2.0 (Multi-User)"
	@echo "============================================="
	@echo ""
	@echo "Verfügbare Kommandos:"
	@echo "  setup USER=sXXXXX       - Erstelle users/sXXXXX.env aus .env.example"
	@echo "  build                   - Docker Image bauen"
	@echo "  run USER=sXXXXX         - Checker für einen Benutzer starten"
	@echo "  stop USER=sXXXXX        - Checker für einen Benutzer stoppen"
	@echo "  restart USER=sXXXXX     - Checker für einen Benutzer neu starten"
	@echo "  logs USER=sXXXXX        - Live-Logs eines Benutzers anzeigen"
	@echo "  run-all                 - Alle Benutzer starten"
	@echo "  stop-all                - Alle Benutzer stoppen"
	@echo "  logs-all                - Live-Logs aller Benutzer anzeigen"
	@echo "  status                  - Alle laufenden Checker anzeigen"
	@echo "  test-notifications USER=sXXXXX - Benachrichtigungen testen"
	@echo "  test-grades USER=sXXXXX      - Neue Noten simulieren (TEST-MODUS)"
	@echo "  clean                   - Alle Container und Images entfernen"
	@echo "  dev                     - Lokale Entwicklungsumgebung"

# Prüft ob USER gesetzt ist
_check-user:
	@if [ -z "$(USER)" ]; then \
		echo "❌ Bitte USER angeben, z.B.: make run USER=s12345"; \
		exit 1; \
	fi

# Setup - User-Env erstellen
setup: _check-user
	@mkdir -p users
	@if [ ! -f "users/$(USER).env" ]; then \
		cp .env.example "users/$(USER).env"; \
		echo "✅ users/$(USER).env wurde erstellt. Bitte bearbeiten!"; \
	else \
		echo "⚠️  users/$(USER).env existiert bereits"; \
	fi

# Docker Build
build:
	@echo "🔨 Baue Docker Image..."
	docker compose build

# Checker für einen Benutzer starten
run: _check-user build
	@if [ ! -f "users/$(USER).env" ]; then \
		echo "❌ users/$(USER).env nicht gefunden! Führe 'make setup USER=$(USER)' aus"; \
		exit 1; \
	fi
	@echo "🚀 Starte Checker für $(USER)..."
	HTWD_USERNAME=$(USER) docker compose -p htwd-$(USER) up -d
	@echo "✅ Container htwd-checker-$(USER) läuft!"

# Checker für einen Benutzer stoppen
stop: _check-user
	@echo "🛑 Stoppe Checker für $(USER)..."
	HTWD_USERNAME=$(USER) docker compose -p htwd-$(USER) down

# Checker neu starten
restart: _check-user
	@$(MAKE) stop USER=$(USER)
	@$(MAKE) run USER=$(USER)

# Live-Logs eines Benutzers
logs: _check-user
	@echo "📋 Live-Logs für $(USER) (Ctrl+C zum Beenden)..."
	HTWD_USERNAME=$(USER) docker compose -p htwd-$(USER) logs -f

# Alle Benutzer starten
run-all: build
	@if [ ! -d "users" ] || [ -z "$$(ls users/*.env 2>/dev/null)" ]; then \
		echo "❌ Keine User-Configs gefunden in users/"; \
		exit 1; \
	fi
	@for envfile in users/*.env; do \
		user=$$(basename "$$envfile" .env); \
		echo "🚀 Starte Checker für $$user..."; \
		HTWD_USERNAME=$$user docker compose -p htwd-$$user up -d; \
	done
	@echo "✅ Alle Checker gestartet!"

# Alle Benutzer stoppen
stop-all:
	@if [ ! -d "users" ] || [ -z "$$(ls users/*.env 2>/dev/null)" ]; then \
		echo "Keine User-Configs gefunden"; \
		exit 0; \
	fi
	@for envfile in users/*.env; do \
		user=$$(basename "$$envfile" .env); \
		echo "🛑 Stoppe Checker für $$user..."; \
		HTWD_USERNAME=$$user docker compose -p htwd-$$user down; \
	done
	@echo "✅ Alle Checker gestoppt!"

# Live-Logs aller Benutzer
logs-all:
	@echo "📋 Live-Logs aller Checker (Ctrl+C zum Beenden)..."
	@tail -f logs/*/htwd_checker.log 2>/dev/null || echo "Keine Log-Dateien gefunden"

# Status aller Checker
status:
	@echo "📊 Laufende Checker:"
	@docker ps --filter "name=htwd-checker-" --format "table {{.Names}}\t{{.Status}}\t{{.RunningFor}}" 2>/dev/null || echo "Keine aktiven Checker"

# Benachrichtigungen testen
test-notifications: _check-user
	@if [ ! -f "users/$(USER).env" ]; then \
		echo "❌ users/$(USER).env nicht gefunden! Führe 'make setup USER=$(USER)' aus"; \
		exit 1; \
	fi
	@echo "🧪 Teste Benachrichtigungen für $(USER)..."
	@set -a && . users/$(USER).env && set +a && python3 test_notifications.py

# Neue Noten simulieren
test-grades: _check-user
	@if [ ! -f "users/$(USER).env" ]; then \
		echo "❌ users/$(USER).env nicht gefunden! Führe 'make setup USER=$(USER)' aus"; \
		exit 1; \
	fi
	@echo "🎯 Starte Noten-Simulation für $(USER)..."
	@set -a && . users/$(USER).env && set +a && python3 test_new_grades.py

# Cleanup
clean:
	@echo "🧹 Entferne alle Checker-Container und Images..."
	@if [ -d "users" ] && [ -n "$$(ls users/*.env 2>/dev/null)" ]; then \
		for envfile in users/*.env; do \
			user=$$(basename "$$envfile" .env); \
			HTWD_USERNAME=$$user docker compose -p htwd-$$user down --rmi all --volumes --remove-orphans 2>/dev/null; \
		done; \
	fi
	docker system prune -f
	@echo "✅ Aufgeräumt!"

# Lokale Entwicklung
dev:
	@echo "💻 Lokale Entwicklungsumgebung..."
	@if [ ! -d "venv" ]; then \
		python3 -m venv venv; \
		echo "📦 Virtual Environment erstellt"; \
	fi
	@if [ -f "venv/bin/pip" ]; then \
		venv/bin/pip install -r requirements.txt; \
	elif [ -f "venv/Scripts/pip.exe" ]; then \
		venv/Scripts/pip install -r requirements.txt; \
	fi
	@echo "✅ Dependencies installiert!"
	@echo "Zum Aktivieren: source venv/bin/activate (Linux/Mac) oder venv\\Scripts\\activate (Windows)"
