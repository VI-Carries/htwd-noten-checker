# HTW Noten-Checker Makefile

.PHONY: help build run stop logs clean setup test-grades test-notifications dev status

# Default target
help:
	@echo "HTW Dresden Noten-Checker v2.0"
	@echo "================================"
	@echo ""
	@echo "Verfügbare Kommandos:"
	@echo "  setup       		- Erstelle .env aus .env.example"
	@echo "  build       		- Docker Image bauen"
	@echo "  run         		- Container im Hintergrund starten"
	@echo "  stop        		- Container stoppen"
	@echo "  restart     		- Container neu starten"
	@echo "  logs        		- Live-Logs anzeigen"
	@echo "  test-notifications	- Benachrichtigungen testen"
	@echo "  test-grades 		- Neue Noten simulieren (TEST-MODUS)"
	@echo "  clean       		- Container und Images entfernen"
	@echo "  dev         		- Lokale Entwicklungsumgebung"

# Setup - .env erstellen
setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ .env wurde erstellt. Bitte bearbeiten!"; \
	else \
		echo "⚠️  .env existiert bereits"; \
	fi

# Docker Build
build:
	@echo "🔨 Baue Docker Image..."
	docker compose build

# Container starten
run: build
	@echo "🚀 Starte Container..."
	docker compose up -d
	@echo "✅ Container läuft! Logs mit 'make logs' anzeigen"

# Container stoppen
stop:
	@echo "🛑 Stoppe Container..."
	docker compose down

# Container neu starten
restart: stop run

# Live-Logs anzeigen
logs:
	@echo "📋 Live-Logs (Ctrl+C zum Beenden)..."
	docker compose logs -f

# Benachrichtigungen testen
test-notifications:
	@echo "🧪 Teste Benachrichtigungen..."
	@if [ ! -f .env ]; then \
		echo "❌ .env nicht gefunden! Führe 'make setup' aus"; \
		exit 1; \
	fi
	python3 test_notifications.py

# Neue Noten simulieren
test-grades:
	@echo "🎯 Starte Noten-Simulation..."
	@if [ ! -f .env ]; then \
		echo "❌ .env nicht gefunden! Führe 'make setup' aus"; \
		exit 1; \
	fi
	python3 test_new_grades.py

# Cleanup
clean:
	@echo "🧹 Entferne Container und Images..."
	docker compose down --rmi all --volumes --remove-orphans
	docker system prune -f

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

# Status anzeigen
status:
	@echo "📊 Container Status:"
	docker compose ps
	@echo ""
	@echo "📈 Resource Usage:"
	docker stats --no-stream $(docker compose ps -q) 2>/dev/null || echo "Container nicht aktiv"
