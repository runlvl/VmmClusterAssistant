# VMM Cluster Implementation Tool - Installationsanleitung

Diese Anleitung führt Sie durch den Prozess der Installation und Einrichtung des VMM Cluster Implementation Tools.

## Systemanforderungen

Um das VMM Cluster Implementation Tool ordnungsgemäß auszuführen, müssen folgende Systemanforderungen erfüllt sein:

* Python 3.8 oder höher
* 4 GB RAM (Minimum)
* 2 GB freier Festplattenspeicher
* Internetverbindung (für die Installation von Abhängigkeiten)

## Installationsschritte

### 1. Python Installation

Falls Python noch nicht auf Ihrem System installiert ist:

1. Laden Sie Python von [python.org](https://www.python.org/downloads/) herunter
2. Führen Sie das Installationsprogramm aus und aktivieren Sie die Option "Add Python to PATH"
3. Überprüfen Sie die Installation mit dem Befehl: `python --version`

### 2. Tool herunterladen

1. Klonen Sie das Repository oder laden Sie es als ZIP-Datei herunter:
   ```
   git clone https://github.com/ihre-organisation/vmm-cluster-tool.git
   ```

2. Wechseln Sie in das Projektverzeichnis:
   ```
   cd vmm-cluster-tool
   ```

### 3. Abhängigkeiten installieren

Das Tool installiert die benötigten Abhängigkeiten automatisch, Sie können diesen Schritt aber auch manuell durchführen:

1. Installation aller Abhängigkeiten:
   ```
   pip install -r requirements.txt
   ```

Alternativ installieren Sie die folgenden Pakete individuell:
```
pip install streamlit pandas networkx plotly psutil pyyaml requests streamlit-option-menu
```

### 4. Tool starten

1. Starten Sie das Tool mit folgendem Befehl:
   ```
   streamlit run app.py
   ```

2. Das Tool wird automatisch in Ihrem Standardbrowser unter der Adresse `http://localhost:8501` geöffnet.

## Offline-Installation

Für Umgebungen ohne Internetzugang ist eine Offline-Installation möglich:

1. Laden Sie alle benötigten Pakete auf einem Computer mit Internetzugang herunter:
   ```
   pip download -r requirements.txt -d ./offline_packages
   ```

2. Übertragen Sie den Projektordner und den Ordner `offline_packages` auf den Zielcomputer

3. Installieren Sie die Pakete offline:
   ```
   pip install --no-index --find-links=./offline_packages -r requirements.txt
   ```

## Fehlerbehebung

### Fehlende Abhängigkeiten
Wenn beim Start eine Fehlermeldung wegen fehlender Abhängigkeiten erscheint:
1. Klicken Sie im Tool auf "Check Dependencies" im Seitenmenü
2. Installieren Sie fehlende Abhängigkeiten manuell mit pip

### Port bereits in Benutzung
Falls Port 8501 bereits verwendet wird:
1. Starten Sie das Tool mit einem anderen Port:
   ```
   streamlit run app.py --server.port=8502
   ```

## Sicherheitshinweise

* Das Tool speichert alle eingegebenen Daten lokal
* Es werden keine Daten an externe Server übertragen
* Für eine Verwendung in Produktionsumgebungen empfehlen wir, den Zugriff auf das Tool zu beschränken

## Nächste Schritte

Nach erfolgreicher Installation können Sie mit der Verwendung des Tools beginnen:
1. Durchlaufen Sie die Einführung
2. Folgen Sie den Implementierungsschritten in der Seitenleiste
3. Generieren Sie am Ende Ihre Dokumentation