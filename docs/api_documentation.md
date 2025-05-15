# VMM Cluster Implementation Tool - API-Dokumentation

Diese Dokumentation beschreibt die wichtigsten Module, Funktionen und Datenstrukturen des VMM Cluster Implementation Tools.

## Modul-Übersicht

Das Tool ist in mehrere Hauptmodule unterteilt:

### 1. Datenmodule (`data/`)

Module für die Definition von Anforderungen und Best Practices.

- `best_practices.py`: Definiert Best Practices für die VMM-Implementierung
- `requirements.py`: Definiert Hardware- und Software-Anforderungen

### 2. Seitenmodule (`pages/`)

Module für die unterschiedlichen Seiten der Benutzeroberfläche.

- `hardware_requirements.py`: UI für Hardware-Anforderungen
- `software_requirements.py`: UI für Software-Anforderungen
- `network_configuration.py`: UI für Netzwerkkonfiguration
- `storage_configuration.py`: UI für Speicherkonfiguration
- `security_settings.py`: UI für Sicherheitseinstellungen
- `high_availability.py`: UI für Hochverfügbarkeitskonfiguration
- `backup_restore.py`: UI für Backup- und Wiederherstellungskonfiguration
- `roles_permissions.py`: UI für Rollen- und Berechtigungskonfiguration
- `monitoring.py`: UI für Überwachungskonfiguration
- `documentation.py`: UI für Dokumentationsgenerierung
- `installation.py`: UI für Installationsanleitung

### 3. Hilfsmodule (`utils/`)

Module mit Hilfsfunktionen für das Tool.

- `dependency_checker.py`: Überprüfung und Installation von Abhängigkeiten
- `system_checker.py`: Überprüfung der Systemanforderungen
- `documentation_generator.py`: Generierung von Dokumentationen und Skripten
- `network_validator.py`: Validierung von Netzwerkkonfigurationen
- `storage_validator.py`: Validierung von Speicherkonfigurationen
- `security_validator.py`: Validierung von Sicherheitseinstellungen
- `high_availability_validator.py`: Validierung von Hochverfügbarkeitskonfigurationen

## Hauptfunktionen

### Dependency-Checking

```python
from utils.dependency_checker import check_dependencies, install_dependency, install_all_dependencies

# Überprüfen von Abhängigkeiten
dependency_status = check_dependencies()
# Rückgabe: {"status": True/False, "missing": ["package1", "package2"]}

# Installation einer einzelnen Abhängigkeit
install_result = install_dependency("package_name")
# Rückgabe: True/False

# Installation aller fehlenden Abhängigkeiten
install_result = install_all_dependencies()
# Rückgabe: {"status": True/False, "failed": ["package1"], "installed": ["package2"]}
```

### Netzwerkvalidierung

```python
from utils.network_validator import validate_network_configuration, validate_ip_address, create_network_visualization

# Validieren einer IP-Adresse
valid, message = validate_ip_address("192.168.1.1")

# Validieren einer Netzwerkkonfiguration
network_config = {
    "management_network": {"cidr": "192.168.1.0/24"},
    "migration_network": {"cidr": "10.0.0.0/24"},
    "vm_network": {"cidr": "172.16.0.0/24"},
    "dedicated_nics": True
}
validation_results = validate_network_configuration(network_config)
# Rückgabe: {"status": True/False, "errors": [], "warnings": [], "recommendations": []}

# Erstellen einer Netzwerkvisualisierung
fig = create_network_visualization(network_config)
```

### Dokumentationsgenerierung

```python
from utils.documentation_generator import generate_implementation_documentation, generate_powershell_scripts

# Generieren einer Implementierungsdokumentation
config = {...}  # Vollständige Konfiguration
html_content = generate_implementation_documentation(config)

# Generieren von PowerShell-Skripten
scripts = generate_powershell_scripts(config)
# Rückgabe: {"script1.ps1": "Script-Inhalt", "script2.ps1": "Script-Inhalt"}
```

## Datenstrukturen

### Konfigurationsobjekt

Die Hauptkonfiguration wird in `st.session_state.configuration` gespeichert und hat folgende Struktur:

```python
configuration = {
    "hardware": {
        "cpu_cores": 8,
        "memory_gb": 16,
        "servers": 2,
        # weitere Hardware-Konfigurationen
    },
    "software": {
        "vmm_version": "2022",
        "sql_version": "2022",
        "service_account": "DOMAIN\\svc_vmm",
        # weitere Software-Konfigurationen
    },
    "network": {
        "management_network": {"cidr": "192.168.1.0/24"},
        "migration_network": {"cidr": "10.0.0.0/24"},
        "vm_network": {"cidr": "172.16.0.0/24"},
        "dedicated_nics": True,
        # weitere Netzwerk-Konfigurationen
    },
    "storage": {
        "storage_type": "SAN",
        "capacity_tb": 10,
        # weitere Storage-Konfigurationen
    },
    "security": {
        "host_hardening": True,
        "network_isolation": True,
        # weitere Sicherheits-Konfigurationen
    },
    "ha": {
        "enabled": True,
        "node_count": 2,
        # weitere HA-Konfigurationen
    },
    "backup": {
        "method": "DPM",
        "retention_days": 30,
        # weitere Backup-Konfigurationen
    },
    "roles": {
        # Rollenkonfigurationen
    },
    "monitoring": {
        # Überwachungskonfigurationen
    }
}
```

## Best Practices für die Entwicklung

### Hinzufügen neuer Validierungen

1. Erstellen Sie eine neue Funktion im entsprechenden Validator-Modul:

```python
def validate_new_feature(config):
    """
    Validiert eine neue Funktion.
    
    Args:
        config: Konfigurationsobjekt
        
    Returns:
        Dictionary mit Validierungsergebnissen
    """
    results = {
        "status": True,
        "errors": [],
        "warnings": [],
        "recommendations": []
    }
    
    # Validierungslogik
    
    return results
```

2. Rufen Sie die Funktion von der entsprechenden Seite aus auf:

```python
validation_results = validate_new_feature(feature_config)

if not validation_results["status"]:
    st.error("Fehler in der Konfiguration")
    for error in validation_results["errors"]:
        st.error(error)
```

### Hinzufügen neuer Visualisierungen

Erstellen Sie eine neue Funktion zur Visualisierung:

```python
def create_new_visualization(config):
    """
    Erstellt eine Visualisierung.
    
    Args:
        config: Konfigurationsobjekt
        
    Returns:
        Plotly-Figur
    """
    # Erstellen der Figur
    fig = go.Figure()
    
    # Figur konfigurieren
    
    return fig
```

## Erweiterung des Tools

Wenn Sie das Tool um neue Funktionen erweitern möchten:

1. Erstellen Sie ein neues Modul in dem entsprechenden Verzeichnis
2. Implementieren Sie die Funktionalität 
3. Integrieren Sie das Modul in die Hauptanwendung (`app.py`)
4. Aktualisieren Sie die Dokumentation