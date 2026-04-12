# HA AI Context Exporter – Entwicklungs-Tree & Roadmap

## Zweck dieser Datei

Diese Datei ist die gemeinsame Orientierung für die weitere Entwicklung.

Sie kombiniert:

1. **Langfristiges Zielbild**
   - Was soll der HA AI Context Exporter später können?

2. **Schritt-für-Schritt-Roadmap**
   - Was wurde bereits gebaut?
   - Was kommt als Nächstes?
   - Welche Reihenfolge ist sinnvoll?

Wichtig:
Das Projekt soll **nicht lose** wachsen.
Es soll entlang einer **klaren Linie** entwickelt werden, damit es am Ende deinen Anforderungen entspricht:

- möglichst vollständiges Bild von Home Assistant
- saubere, ehrliche, brauchbare Daten
- Verknüpfung von API-Zustand und YAML-/Dateikontext
- Beziehungen zwischen Bereichen, Geräten, Entitäten, Integrationen, Automationen und Dashboards
- Export, den eine KI wirklich nutzen kann, um:
  - das System zu verstehen
  - bestehende Automationen zu prüfen
  - neue Automationen vorzuschlagen
  - Benennung und Struktur zu verbessern
- optional auch interne Analysefunktionen direkt im Tool

---

# 1. Leitbild des Projekts

Der **HA AI Context Exporter** soll langfristig **beides** sein:

## A. Technischer Exporter
Ein Tool, das Home Assistant-Daten strukturiert, sicher und möglichst vollständig exportieren kann.

## B. Analyzer / Verständnisschicht
Ein Tool, das Zusammenhänge sichtbar macht und eine KI in die Lage versetzt,
sich **ein komplettes Bild des Home Assistant Systems** zu machen.

Das bedeutet später nicht nur:
- Wie viele Entities gibt es?
- Wie viele Automationen gibt es?

Sondern auch:
- Welche Entity gehört zu welchem Device?
- Welches Device gehört zu welchem Bereich?
- Welche Integration steckt dahinter?
- Welche Automationen referenzieren welche Entities?
- Welche Dashboards zeigen welche Entities?
- Welche YAML-/Dateidefinitionen erzeugen welches Verhalten?

---

# 2. Grundsatzentscheidungen

## 2.1 Entity-Daten möglichst vollständig erfassen

Später sollen Entities möglichst vollständig erfasst werden.

Dazu gehören z. B.:
- entity_id
- domain
- state
- friendly_name
- area
- device
- integration
- attributes

Attribute werden später in zwei Ebenen aufgeteilt:

### raw_attributes
- vollständige Originalattribute
- technisch vollständig
- eher für tiefe Analyse / Vollkontext

### important_attributes
- reduzierte, sinnvolle Teilmenge
- KI-relevante Attribute
- besser lesbar und kompakter

Wichtig:
**Erst Datenreichtum schaffen, danach über Varianten filtern.**

---

## 2.2 YAML / Dateikontext aktiv mit API-Zustand verknüpfen

Dateikontext ist **nicht nur nice-to-have**, sondern ein echter Zielbestandteil.

Später soll das Tool nicht nur:
- API-Daten lesen

sondern auch:
- YAML-Dateien lesen
- Konfiguration verstehen
- Beziehungen zwischen Dateidefinition und laufendem Zustand herstellen

Beispiele:
- Automation aus `automations.yaml`
- referenzierte Entities aus API
- Area / Device / Integration Kontext dazu
- später evtl. Inkonsistenzen und Verbesserungshinweise

Wichtig:
Das Ziel ist **nicht** API und Dateien nebeneinander zu exportieren,
sondern **beides aktiv zu verknüpfen**.

---

# 3. Entwicklungs-Tree (Zielbild)

## 3.1 Foundation Layer
Technische Basis des Add-ons.

Enthält:
- Add-on Scaffold
- Ingress UI
- Python Backend
- Health / Info / Preview Endpoints
- Core Proxy Zugriff
- read-only Sicherheitsmodell
- Export Controller
- Download-System
- AI-Projektdokumentation
- Review-/Changelog-/Workflow-Struktur

Ziel:
Eine stabile, sichere und erweiterbare Plattform.

Status:
**fertig**

---

## 3.2 Discovery Summary Layer
Erste Überblicksebene.

Enthält:
- system summary
- entities summary
- logic summary
- dashboard summary
- integrations summary

Ziel:
Ein schneller, kompakter Überblick über das HA-System.

Wichtig:
Diese Ebene ist wichtig, aber **nicht das Endziel**.

Status:
**größtenteils vorhanden**

---

## 3.3 Discovery Quality Layer
Qualitätsverbesserung der vorhandenen Discovery-Daten.

Enthält:
- Integrationsbereinigung
- Entschärfung interner/Core-Komponenten
- saubere Status-Semantik
- bessere Areas-/Devices-Erkennung
- robustere Dashboard-Erkennung

Ziel:
Vor neuen Tiefenebenen zuerst die vorhandenen Daten sauber machen.

Status:
**nächste aktive Phase**

---

## 3.4 Entity Context Layer
Tiefe Informationen über Entities.

Später pro Entity z. B.:
- entity_id
- domain
- state
- friendly_name
- integration
- device
- area
- raw_attributes
- important_attributes

Ziel:
Entities nicht nur zählen, sondern **kontextualisieren**.

Status:
**später, aber sehr wichtig**

---

## 3.5 Relationship Layer
Systembeziehungen modellieren.

Beispiele:
- Entity → Device
- Device → Area
- Entity → Integration
- Automation → Entity
- Dashboard → Entity
- Bereich → Devices / Entities / Automationen

Ziel:
Die KI soll nicht nur Dinge sehen, sondern verstehen,
**wie die Dinge zusammenhängen**.

Status:
**später, nach Entity Context**

---

## 3.6 Logic Deep Layer
Tiefe Sicht auf Automationen, Scripts und Szenen.

Später z. B.:
- alias
- triggers
- conditions
- actions
- referenced_entities
- referenced_areas
- referenced_devices

Ziel:
Die KI soll bestehende Logik prüfen und verbessern können.

Status:
**später**

---

## 3.7 Dashboard Deep Layer
Tiefe Sicht auf Dashboards / Lovelace.

Später z. B.:
- dashboard names
- views
- cards
- card types
- referenced_entities
- Bereichs-/Themenbezug

Ziel:
Die UI-Sicht von Home Assistant wird KI-lesbar.

Status:
**später**

---

## 3.8 File / YAML Context Layer
Datei- und Konfigurationssicht.

Später:
- `automations.yaml`
- `scripts.yaml`
- `scenes.yaml`
- `configuration.yaml`
- packages / includes

Ziel:
Die KI sieht nicht nur API-Zustand, sondern auch die eigentliche Definition.

Status:
**später, aber ausdrücklich gewünscht**

---

## 3.9 LLM Optimization Layer
Export speziell für KI optimieren.

Später:
- Variant A = technische Vollversion
- Variant B = kompakter / KI-orientierter
- Zusammenfassungen
- Noise Reduction
- Priorisierung

Ziel:
Nicht nur viele Daten exportieren, sondern **nutzbaren KI-Kontext** erzeugen.

Status:
**später**

---

## 3.10 Internal Analyzer Layer
Das Tool selbst liefert Hinweise.

Später z. B.:
- Benennungsqualität von Entities / Helpers
- Inkonsistenzen in Struktur
- redundante Automationen
- auffällige Konfigurationsmuster
- Verbesserungsvorschläge

Ziel:
Das Tool wird nicht nur Exporter, sondern auch aktiver Helfer.

Status:
**später / Ausbauphase**

---

# 4. Schritt-für-Schritt-Roadmap

## Phase 0 – Fundament bauen
### Ziel
Das Projekt überhaupt lauffähig, sicher und strukturiert machen.

### Enthielt
- Add-on Scaffold
- Ingress UI
- Backend HTTP Server
- erste Preview-/Discovery-Endpunkte
- `/api/export`
- `/api/export/download`
- Download Header
- Markdown Renderer
- Versioning-Grundlage
- Export-Semantik
- Core Proxy Zugriff
- `/api/ha-auth-debug`
- AI-Projektdokumentation
- Review-/Changelog-Workflow

### Status
**abgeschlossen**

---

## Phase 1 – Erste echte Discovery
### Ziel
Nicht nur Struktur, sondern reale Daten liefern.

### Enthielt
- entities discovery
- top domains
- logic counts
- erste integrations discovery
- system partial summary
- saubere Status-Semantik

### Status
**laufend, aber wesentliche Basis steht**

---

## Phase 2 – Discovery bereinigen
### Ziel
Die aktuell vorhandenen Daten sauberer und sinnvoller machen, bevor wir zu viel Neues aufbauen.

### Warum diese Phase wichtig ist
Dein Wunsch ist:
**erst saubere, brauchbare Daten, dann Erweiterung**.

### Geplante Schritte
1. Integrationsliste bereinigen
   - Plattformen wie `mqtt.sensor`, `mqtt.switch` sinnvoll auf Hauptintegration zurückführen
   - interne/Core-Komponenten entschärfen oder markieren

2. Areas / Devices Discovery verbessern
   - prüfen, ob / wie die Endpunkte robuster nutzbar werden
   - ehrliche Semantik beibehalten

3. Dashboard Discovery verbessern
   - robustere Lesbarkeit
   - bessere Metadaten

### Status
**jetzt aktuelle Hauptphase**

---

## Phase 3 – Entity Context einführen
### Ziel
Von Counts zu echten Entitätskontexten wechseln.

### Geplante Schritte
1. Erste kompakte und vollständige Entity-Struktur definieren
2. raw_attributes exportieren
3. important_attributes definieren
4. Integration / Device / Area Kontext ergänzen

### Ergebnis
Die KI kann einzelne Entities verstehen, nicht nur Mengen.

### Status
**nach Phase 2**

---

## Phase 4 – Relationship Layer aufbauen
### Ziel
Zusammenhänge im System modellieren.

### Geplante Schritte
1. Entity → Device
2. Device → Area
3. Entity → Integration
4. Automation → Entities
5. Dashboard → Entities

### Ergebnis
Der Export wird von einer Sammlung zu einem **Systemmodell**.

### Status
**nach Entity Context**

---

## Phase 5 – Logic Deep Export
### Ziel
Automationen, Scripts und Szenen wirklich verständlich exportieren.

### Geplante Schritte
1. Automation-Struktur
   - alias
   - triggers
   - conditions
   - actions
   - referenced_entities

2. Scripts vertiefen
3. Szenen vertiefen

### Ergebnis
Die KI kann bestehende Logik prüfen und neue Logik sinnvoll darauf aufbauen.

### Status
**nach Relationship Layer**

---

## Phase 6 – Dashboard Deep Export
### Ziel
Lovelace/Dashboard-Struktur tiefer erfassen.

### Geplante Schritte
1. Dashboard-Namen / Views / Karten
2. Karten-Typen
3. referenzierte Entities
4. Bereichs-/Themenbezug

### Ergebnis
Die UI-Sicht von Home Assistant wird KI-lesbar.

### Status
**später, aber wichtig**

---

## Phase 7 – File / YAML Context
### Ziel
Das echte Konfigurationsbild ergänzen.

### Geplante Schritte
1. Dateizugriff / Lesestrategie klären
2. `automations.yaml`
3. `scripts.yaml`
4. `scenes.yaml`
5. `configuration.yaml`
6. packages / includes
7. aktive Verknüpfung mit API-Zustand

### Ergebnis
Die KI sieht nicht nur API-Zustände, sondern die eigentlichen Definitionsdateien und ihre Beziehungen.

### Status
**später, aber ausdrücklich gewünscht und wichtig**

---

## Phase 8 – LLM-Optimierung
### Ziel
Den Export so formen, dass KI maximal sinnvoll damit arbeiten kann.

### Geplante Schritte
1. Varianten klar schärfen
2. kompakte Zusammenfassungen
3. Noise reduzieren
4. Priorisierung relevanter Informationen

### Ergebnis
Noch bessere Nutzbarkeit für ChatGPT, Claude, lokale LLMs usw.

### Status
**nach mehr inhaltlicher Tiefe**

---

## Phase 9 – Internal Analyzer
### Ziel
Das Tool selbst gibt schon Hinweise.

### Beispiele
- Benennungsqualität
- unklare Entities / Helpers
- Strukturprobleme
- auffällige oder redundante Automationen
- organisatorische Verbesserungsvorschläge

### Ergebnis
Das Tool wird nicht nur Exporter, sondern aktiver Helfer.

### Status
**später / Ausbauphase**

---

# 5. Varianten- und Modus-Idee (frühe Leitlinie)

Du hast dich für **B = mehrere Modi** entschieden.
Das ist sinnvoll, weil vollständige Daten später sehr groß werden können.

## compact
Ziel:
Kompakter Überblick.

Enthält später vor allem:
- counts
- top lists
- kurze Zusammenfassungen
- stark reduzierte Entity-/Integrationsinformationen

Für:
- schnelle Übersicht
- kleine Exporte
- erste KI-Einschätzung

## standard
Ziel:
Gute Balance zwischen Vollständigkeit und Lesbarkeit.

Enthält später:
- Summary + wichtige Beziehungen
- kompakte Entity-Daten
- important_attributes
- ausgewählte Logik-/Dashboard-/Integrationskontexte

Für:
- normale Analyse
- Standard-KI-Exports

## full
Ziel:
Möglichst vollständiger technischer Export.

Enthält später:
- vollständige Entities
- raw_attributes + important_attributes
- mehr Beziehungsdaten
- tieferen Logic-/Dashboard-/Dateikontext

Für:
- tiefe Analyse
- Debugging
- vollständiger Systemkontext

## analysis
Ziel:
Nicht primär Rohdaten, sondern Analyse- und Verbesserungsfokus.

Enthält später:
- Auffälligkeiten
- Strukturprobleme
- Benennungsprobleme
- Redundanzen
- mögliche Verbesserungsfelder
- zusammengefasste Erkenntnisse

Für:
- Optimierung
- Review
- Refactoring-Unterstützung
- KI-Beratung

Wichtig:
Diese Modus-Beschreibungen sind vorerst eine **Leitlinie**.
Die konkrete technische Befüllung kann später schrittweise präzisiert werden.

---

# 6. Was wurde bereits gemacht? (Kurz-Tree)

## Bereits erledigt
- Add-on Basis
- Ingress UI
- Backend
- Core Proxy Zugriff
- read-only Sicherheitsmodell
- `/api/export`
- `/api/export/download`
- `/api/ha-auth-debug`
- system / entities / logic summary
- erste integrations discovery
- AI-Projektdokumentation
- Review-/Archiv-/Changelog-Workflow

## Teilweise erledigt
- system summary
- dashboard summary
- areas/devices discovery
- integrations discovery (erste Version, noch Qualitätsverbesserung nötig)

## Noch offen
- bereinigte Integrationssicht
- Entity Context
- Relationship Layer
- Logic Deep Export
- Dashboard Deep Export
- YAML / File Context
- Internal Analyzer
- starke LLM-Varianten

---

# 7. Aktuelle empfohlene Reihenfolge ab jetzt

## Jetzt sofort sinnvoll
1. **Integrationen bereinigen**
2. **Areas / Devices verbessern**
3. **Dashboard Discovery verbessern**

## Danach
4. **Entity Context Layer**
5. **Relationship Layer**
6. **Logic Deep Export**

## Danach
7. **Dashboard Deep Export**
8. **File / YAML Context**
9. **LLM-Optimierung**
10. **Internal Analyzer**

---

# 8. Arbeitsprinzip für die weitere Entwicklung

Für die nächsten Schritte gilt:

1. **erst Qualität verbessern**
2. **dann neue Tiefe hinzufügen**
3. **dann Beziehungen modellieren**
4. **dann Dateikontext ergänzen**
5. **danach AI-/Analyzer-Mehrwert ausbauen**

So bleibt das Projekt:
- schrittweise
- sauber
- nachvollziehbar
- an den tatsächlichen Anforderungen orientiert

---

# 9. Offene Punkte / spätere Feinschliffe

Diese Fragen blockieren die aktuelle Entwicklung nicht, helfen aber später:

- Welche Attribute sollen standardmäßig in `important_attributes`?
- Wie stark sollen interne/Core-Komponenten bei Integrationen reduziert oder markiert werden?
- Wie genau soll Variant B später gegenüber Variant A reduziert werden?
- Wie tief soll der Datei-/YAML-Kontext standardmäßig in `standard` gehen?
- Welche Analyzer-Ausgaben sind später am nützlichsten?

---

# 10. Kurzfassung in Baumform

```text
HA AI Context Exporter
├─ Foundation
│  ├─ Add-on scaffold
│  ├─ Core proxy auth
│  ├─ Export/download
│  └─ AI project docs
│
├─ Discovery Summary
│  ├─ system
│  ├─ entities
│  ├─ logic
│  ├─ dashboard
│  └─ integrations
│
├─ Discovery Quality
│  ├─ integration cleanup
│  ├─ areas/devices reliability
│  └─ dashboard reliability
│
├─ Entity Context
│  ├─ entity metadata
│  ├─ raw_attributes
│  ├─ important_attributes
│  ├─ entity → device
│  ├─ entity → area
│  └─ entity → integration
│
├─ Relationship Layer
│  ├─ device ↔ area
│  ├─ automation ↔ entities
│  ├─ dashboard ↔ entities
│  └─ system graph
│
├─ Deep Logic
│  ├─ automations
│  ├─ scripts
│  └─ scenes
│
├─ Deep Dashboard
│  ├─ views
│  ├─ cards
│  └─ entity references
│
├─ File/YAML Context
│  ├─ automations.yaml
│  ├─ scripts.yaml
│  ├─ scenes.yaml
│  └─ configuration/packages
│
├─ LLM Optimization
│  ├─ compact
│  ├─ standard
│  ├─ full
│  └─ analysis
│
└─ Internal Analyzer
   ├─ naming quality
   ├─ structure hints
   ├─ automation issues
   └─ improvement suggestions
```

---

# 11. Zweck dieser Datei für die Zukunft

Diese Datei soll künftig helfen bei:

- gemeinsamem Überblick
- Priorisierung der nächsten Schritte
- Vermeidung von Sprüngen ohne Linie
- zukünftigen Chats / Codex-Prompts
- Review, ob ein Schritt wirklich in die Roadmap passt

Sie ist damit die grobe gemeinsame Navigationskarte für die weitere Entwicklung.
