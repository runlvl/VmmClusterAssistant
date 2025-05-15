# Mitwirken am VMM Cluster Implementation Tool

Vielen Dank für Ihr Interesse am VMM Cluster Implementation Tool! Wir freuen uns über Ihre Unterstützung in Form von Code-Beiträgen, Bug-Reports, Feature-Vorschlägen und Dokumentationsverbesserungen.

## Wie kann ich beitragen?

### Bug melden

Haben Sie einen Bug gefunden? Bitte erstellen Sie ein Issue im GitHub-Repository mit folgenden Informationen:

1. Kurze, aussagekräftige Beschreibung des Problems
2. Schritte zur Reproduktion
3. Erwartetes Verhalten
4. Tatsächliches Verhalten
5. Screenshots (falls hilfreich)
6. Umgebungsdetails (OS, Python-Version, etc.)

### Feature vorschlagen

Haben Sie eine Idee für eine neue Funktion? Wir freuen uns über Ihre Vorschläge! Bitte erstellen Sie ein Issue mit:

1. Klare Beschreibung der vorgeschlagenen Funktion
2. Begründung, warum diese Funktion nützlich wäre
3. Mögliche Implementierungsdetails (falls vorhanden)

### Code beitragen

Möchten Sie direkt Code beisteuern? Großartig! Hier ist der Prozess:

1. Forken Sie das Repository
2. Erstellen Sie einen Feature-Branch (`git checkout -b feature/IhreFunktion`)
3. Führen Sie Ihre Änderungen durch
4. Stellen Sie sicher, dass der Code gut dokumentiert ist
5. Committen Sie Ihre Änderungen (`git commit -m 'Neue Funktion hinzugefügt'`)
6. Pushen Sie den Branch (`git push origin feature/IhreFunktion`)
7. Öffnen Sie einen Pull-Request

## Coding-Richtlinien

- Befolgen Sie den PEP 8 Stil-Guide für Python-Code
- Dokumentieren Sie Ihren Code (Docstrings, Kommentare bei komplexen Abschnitten)
- Schreiben Sie aussagekräftige Commit-Nachrichten
- Fügen Sie Tests für neue Funktionen hinzu

## Verzeichnisstruktur

```
vmm-cluster-tool/
├── app.py                  # Hauptanwendung
├── docs/                   # Dokumentation
├── data/                   # Datendefinitionen
│   ├── best_practices.py   # Best Practices
│   └── requirements.py     # Hardware- und Software-Anforderungen
├── pages/                  # UI-Seiten
│   ├── hardware_requirements.py
│   ├── software_requirements.py
│   └── ...
└── utils/                  # Hilfsfunktionen
    ├── dependency_checker.py
    ├── system_checker.py
    └── ...
```

## Entwicklungsumgebung einrichten

```bash
# Repository klonen
git clone https://github.com/ihre-organisation/vmm-cluster-tool.git
cd vmm-cluster-tool

# Virtuelle Umgebung erstellen
python -m venv venv
source venv/bin/activate  # Unter Windows: venv\Scripts\activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Anwendung starten
streamlit run app.py
```

## Tests

Vor dem Einreichen eines Pull-Requests stellen Sie bitte sicher, dass:

1. Alle vorhandenen Tests weiterhin bestehen
2. Neue Funktionen mit Tests abgedeckt sind
3. Die Anwendung lokal ohne Fehler läuft

## Dokumentation

Gute Dokumentation ist entscheidend. Wenn Sie Änderungen am Code vornehmen:

1. Aktualisieren Sie die entsprechenden Docstrings
2. Passen Sie bei Bedarf die Nutzerhandbücher oder README an
3. Dokumentieren Sie Änderungen an der API oder Benutzeroberfläche

## Verhaltenskodex

Wir erwarten von allen Mitwirkenden respektvolles und inklusives Verhalten. Bitte halten Sie sich an folgende Grundsätze:

- Verwenden Sie eine einladende und inklusive Sprache
- Respektieren Sie unterschiedliche Standpunkte und Erfahrungen
- Akzeptieren Sie konstruktive Kritik dankbar
- Konzentrieren Sie sich auf das, was für die Community am besten ist

## Fragen?

Wenn Sie Fragen haben, können Sie gerne ein Issue öffnen oder eine E-Mail an [kontakt@beispiel.com](mailto:kontakt@beispiel.com) senden.

Vielen Dank für Ihre Beiträge!