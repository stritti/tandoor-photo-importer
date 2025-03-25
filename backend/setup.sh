#!/bin/bash

# Erstellen einer virtuellen Umgebung (falls noch nicht vorhanden)
if [ ! -d "venv" ]; then
    echo "Erstelle virtuelle Umgebung..."
    python -m venv venv
fi

# Aktivieren der virtuellen Umgebung
source venv/bin/activate

# Installieren der Abhängigkeiten
echo "Installiere Abhängigkeiten..."
pip install -r requirements.txt

echo "Setup abgeschlossen. Aktiviere die virtuelle Umgebung mit 'source venv/bin/activate'"
