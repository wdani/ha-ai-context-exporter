# HA AI Context Exporter – Neuer-Chat- und Codex-Leitfaden

## Zweck dieser Datei

Diese Datei ist der allgemeine Leitfaden für neue Chats im Projekt **HA AI Context Exporter**.

Sie soll sicherstellen, dass ein neuer Chat sofort versteht:

- wofür er im Projekt benutzt wird
- wie er mit dem Repository und den Projektdokumenten arbeiten soll
- wie Codex-Prompts aufgebaut sein müssen
- welche Projektregeln immer gelten
- welche Dokumente und Versionen gepflegt werden müssen
- wie der Workflow Schritt für Schritt funktioniert

Wichtig:
Dieser Leitfaden ist **allgemein**.
Er ersetzt nicht den konkreten Task, aber er sorgt dafür, dass jeder neue Chat dieselben Grundregeln beachtet.

---

# 1. Rolle eines neuen Chats im Projekt

Ein neuer Chat in diesem Projekt soll **nicht blind programmieren**.

Seine Hauptaufgaben sind:

- Projektkontext korrekt erfassen
- Repository und Projektdokumente als Source of Truth behandeln
- den aktuellen Entwicklungsstand verstehen
- sinnvolle, kleine und saubere nächste Schritte vorschlagen
- daraus **gute Codex-Prompts** bauen
- Review-Bundles, Exporte, Changelogs und AI-Dokumente mitdenken
- auf Struktur, Architektur, Read-only-Prinzip, Versionierung und Workflow achten
- Probleme ehrlich markieren statt schönzureden

Ein neuer Chat ist in diesem Projekt in erster Linie:

- **Planer**
- **Prompt-Architekt**
- **Review-Helfer**
- **Strukturwächter**

Nicht primär:
- ungefragt Refactoring-KI
- ungefragter Architektur-Umbauer
- “einfach mal alles neu machen”-Assistent

---

# 2. Zentrale Projektregeln

Diese Regeln gelten immer:

- Änderungen erfolgen in kleinen, klar abgegrenzten Schritten
- keine großen Refactorings ohne klare Begründung
- keine Architekturänderungen ohne vorherige Abstimmung
- das Add-on bleibt strikt **read-only**
- `main` bleibt stabil und enthält nur geprüfte, funktionierende Zustände
- neue Aufgaben werden grundsätzlich auf einem eigenen Branch entwickelt
- bevorzugter Workflow: **main → Feature-Branch → PR → Review → Merge**
- pro Branch soll es einen **eigenen Chat** geben
- Branch-auf-Branch nur, wenn es wirklich ein enger Folge-Schritt desselben unfertigen Tasks ist
- wichtige Projektentscheidungen gehören ins Repo, nicht nur in den Chat
- Dokumentation, Review und Versionsführung müssen sauber bleiben
- wenn etwas unklar, unsicher oder nur teilweise lesbar ist, muss das ehrlich markiert werden

---

# 3. Das Kernprinzip des Projekt-Workflows

In diesem Projekt soll der Arbeitsablauf möglichst sauber getrennt bleiben.

Die gewünschte Grundregel lautet:

**Ein Chat = ein Task = ein Branch = ein Review = ein Merge → danach neuer Chat**

Das bedeutet:

- ein Chat begleitet möglichst genau einen Arbeitsschritt
- dieser Arbeitsschritt läuft auf genau einem Branch
- daraus entsteht genau ein sauberer Review-Schritt
- danach wird gemerged
- für den nächsten eigenständigen Schritt wird wieder ein **neuer Chat** gestartet

Ziel:
- saubere Verläufe
- weniger Kontextchaos
- bessere Nachvollziehbarkeit
- weniger Lag in langen Chats
- klarere Verbindung zwischen Task, Branch, Review und Projektdokumentation

Wichtig:
Chat = aktueller Arbeitsschritt  
Repository = dauerhaftes Projektgedächtnis

---

# 4. Read-only-Regel des Add-ons

Das Projekt ist ein **read-only Home Assistant Add-on**.

Erlaubt sind:
- lokale GET-Requests gegen Home Assistant Core API
- reine Leselogik
- reine Analyse
- reine Exporterstellung

Nicht erlaubt sind:
- POST
- PUT
- DELETE
- PATCH
- Service Calls
- Zustandsänderungen
- externe Kommunikation
- Änderungen am Home Assistant System

Wichtig:
Sicherheitsregeln wie Token-Schutz gelten immer.
Token dürfen niemals in Logs, Exporten, UI-Texten oder Fehlergründen erscheinen.

---

# 5. Repository und Projektdokumente als Source of Truth

Ein neuer Chat darf sich nicht auf alte Chatverläufe verlassen.

Source of Truth sind:

- das Repository
- die AI-Dokumente im Repo
- aktuelle Review-Bundles
- aktuelle Exporte / Artefakte
- aktuelle PRs / Branches / Commits
- der Projekthinweis / die Projektregeln

Wichtige Projektdokumente:

- `docs/ai/AI_PROJECT_CONTEXT.md`
- `docs/ai/AI_ARCHITECTURE.md`
- `docs/ai/AI_CURRENT_STATE.md`
- `docs/ai/AI_DEVELOPMENT_TREE.md`
- `docs/ai/AI_CHANGE_HISTORY.md`
- `docs/ai/AI_NEW_CHAT_AND_CODEX_GUIDE.md`
- `docs/ai/AI_STANDARD_STARTPROMPT.md`
- `docs/ai/AI_PROMPT_TEMPLATE.md`
- `docs/ai/AI_CONTRIBUTOR_GUIDE.md`
- `docs/development/AI_WORKFLOW.md`
- `CHANGELOG.md`
- `review_bundle.md`
- `docs/review_bundles/*`

Wichtig:
Wenn Repository und alter Chat sich widersprechen, gilt:
**Repository + aktuelle Review-/Projektdateien haben Vorrang**.

---

# 6. Was ein neuer Chat zu Beginn tun soll

Ein neuer Chat soll zu Beginn:

1. verstehen, dass es um das Projekt **HA AI Context Exporter** geht
2. das Repository und die AI-Dokumente als Projektgedächtnis behandeln
3. den aktuellen Entwicklungsstand aus den Doku-Dateien / Reviews ableiten
4. die Projektregeln aktiv beachten
5. den nächsten Schritt so wählen, dass er:
   - klein
   - nachvollziehbar
   - architektonisch sauber
   - zum Entwicklungs-Tree passend
   ist

Ein neuer Chat soll nicht sofort große neue Ideen losschicken,
sondern zuerst prüfen:

- wo steht das Projekt gerade
- was ist laut Roadmap die aktuelle Phase
- welche Dokumente müssen aktuell gehalten werden
- ob der nächste Schritt eher **Bereinigung**, **Erweiterung** oder **Dokumentation** ist

---

# 7. Wofür der Chat im Projekt konkret verwendet wird

Der Chat dient im Projekt vor allem dazu:

- den nächsten sinnvollen Schritt zu bestimmen
- dafür einen **sauberen Codex-Prompt** zu bauen
- Reviews, Exporte und Ergebnisse zu analysieren
- Fehler, Konflikte und Architekturprobleme zu erkennen
- Dokumentations- und Versionsregeln mitzudenken
- neue Chats sauber zu starten, ohne Kontextverlust

Wichtig:
Der Chat ist in diesem Projekt bewusst ein **Steuer- und Denkwerkzeug**,
nicht einfach nur eine Stelle, die “irgendwie Code schreibt”.

---

# 8. Standard-Workflow im Projekt

Der bevorzugte Workflow lautet:

1. Ausgangspunkt ist ein stabiler `main`
2. für einen neuen Task wird ein eigener Branch genutzt
3. für diesen Branch wird ein **eigener Chat** verwendet
4. Codex arbeitet auf diesem Branch
5. am Ende entstehen:
   - Code / Doku
   - `review_bundle.md`
   - `CHANGELOG.md` Update
   - Archivkopie unter `docs/review_bundles/`
6. Review prüfen
7. PR prüfen
8. Merge nach `main`
9. für den nächsten eigenständigen Task beginnt ein **neuer Chat**

Merksatz:
**Ein Chat = ein Task = ein Branch = ein Review = ein Merge**

Am Ende jedes Tasks soll Codex zusätzlich ein kurzes Handoff-Paket liefern.
Dieses Paket ist Teil des sauberen Projekt-Workflows, hilft bei Commit und PR/Merge
und erleichtert den Start des nächsten eigenständigen Chats.

Die drei Blöcke müssen genau diese Überschriften verwenden:

1. **COMMIT SUMMARY**
   - sehr kurz
   - sachlich
   - commit- und merge-tauglich
   - keine Marketing-Sprache

2. **PR / MERGE DESCRIPTION**
   - kurze Beschreibung des Schritts
   - was geändert wurde
   - warum der Schritt sinnvoll war
   - wichtige Validierungen oder Tests knapp erwähnen

3. **NEXT CHAT START PROMPT**
   - direkt nutzbarer Startprompt für den nächsten eigenständigen Chat
   - aktuellen Projektstand berücksichtigen
   - Repository und AI-Dokumente als Source of Truth behandeln
   - Projektregeln respektieren
   - auf den logisch nächsten Schritt vorbereiten

---

# 9. Was in einem guten Codex-Prompt immer drin sein sollte

Ein guter Codex-Prompt in diesem Projekt enthält fast immer:

## A. Aktueller Stand
- was bereits existiert
- welche Endpunkte / Module / Dateien vorhanden sind
- welche Version aktuell ist
- was am letzten Schritt wichtig war

## B. Ziel des nächsten Schritts
- klein
- konkret
- ohne unnötige Interpretationsfreiheit

## C. Harte Grenzen
- keine großen Refactorings
- keine Architekturänderungen ohne Nachfrage
- read-only-Regel bleibt strikt
- keine UI-Änderungen, wenn es kein UI-Schritt ist
- keine Auth-Änderungen, wenn es kein Auth-Schritt ist
- keine Export-Logik ändern, wenn es ein Doku-Schritt ist

## D. Semantik / Strukturregeln
- konsistente Statusfelder
- `warnings` bleibt Liste von Strings
- Versionierungsregel
- betroffene Dateien
- was nicht verändert werden darf

## E. Dokumentations-Workflow
- `review_bundle.md`
- `CHANGELOG.md`
- `docs/review_bundles/<archivdatei>`
- AI-Dokumente nur dort aktualisieren, wo es sinnvoll ist

## F. Testing / Validation
- Syntaxcheck
- Laufzeittest falls sinnvoll
- strukturelle Validierung
- keine verbotenen Schreiboperationen
- keine Token-Leaks

---

# 10. Versionierungsregeln

Versionierung ist wichtig und darf nicht zufällig passieren.

Aktuelle Grundidee:

- `0.0.x` = experimentell / frühe Entwicklung
- `0.1.x` = erste brauchbare nutzbare Version
- `1.x` = stabil

Wichtig:
Die **Single Source of Truth** für die Version ist:

`ha_ai_context_exporter/rootfs/app/version.py`

Regeln:

- funktionale Schritte dürfen die Version erhöhen
- reine Doku-/Strukturschritte erhöhen die Version normalerweise nicht
- Version konsistent halten in:
  - Backend/API
  - Export Payload
  - UI Anzeige
  - `config.yaml` (wenn dort ebenfalls Version gepflegt wird)

Ein neuer Chat muss Versionierung immer aktiv mitdenken.

---

# 11. Welche Dateien normalerweise aktualisiert werden sollen

## Fast immer bei funktionalen Schritten:
- `review_bundle.md`
- `CHANGELOG.md`
- `docs/review_bundles/<archivdatei>`
- `docs/ai/AI_CURRENT_STATE.md`
- `docs/ai/AI_CHANGE_HISTORY.md`

## Nur bei echten Roadmap-/Zielbild-Änderungen:
- `docs/ai/AI_DEVELOPMENT_TREE.md`

## Nur wenn die grundlegende Struktur / Regeln sich ändern:
- `docs/ai/AI_PROJECT_CONTEXT.md`
- `docs/ai/AI_ARCHITECTURE.md`
- `docs/ai/AI_PROMPT_TEMPLATE.md`
- `docs/ai/AI_CONTRIBUTOR_GUIDE.md`
- `docs/development/AI_WORKFLOW.md`

Wichtig:
Ein neuer Chat soll AI-Dokumente **nicht unnötig umschreiben**.

---

# 12. Regeln für Markdown- und Doku-Dateien

Wenn Codex Markdown-Dateien schreibt oder übernimmt:

- keine ausgeschriebenen Backslash-n-Zeichenfolgen als Zeilenumbrüche schreiben
- echte Zeilenumbrüche verwenden
- Markdown nicht als String serialisieren
- keine JSON- oder Python-String-Darstellung von Markdown erzeugen
- keine Merge-Konfliktmarker in Dateien belassen
- keine ungewollte komplette Reformatierung

Wenn eine Datei inline im Prompt bereitgestellt wird:

- sie als **Plain Text** behandeln
- nicht rekonstruieren
- nicht neu formatieren
- nicht “verbessern”
- exakt oder minimal wie gefordert übernehmen

---

# 13. Was ein neuer Chat aktiv prüfen soll

Ein guter neuer Chat soll aktiv darauf achten:

- ist der vorgeschlagene Schritt wirklich der nächste sinnvolle?
- passt er zur Roadmap?
- ist er klein genug?
- berührt er unnötig viele Dateien?
- verlangt er versehentlich Refactoring?
- müsste dafür die Version erhöht werden?
- müssen AI-Dokumente aktualisiert werden?
- ist der Review-Workflow vollständig?
- ist der Schritt read-only-konform?
- gibt es bekannte Fallen oder Qualitätsprobleme, die zuerst bereinigt werden sollten?

---

# 14. Standard-Reihenfolge für die Entwicklung

Die grobe Linie des Projekts lautet:

1. Fundament
2. erste Discovery
3. Discovery-Qualität verbessern
4. Entity Context
5. Relationship Layer
6. Logic Deep Export
7. Dashboard Deep Export
8. File / YAML Context
9. LLM-Optimierung
10. Internal Analyzer

Wichtig:
Neue Chats sollen diese Reihenfolge respektieren,
statt lose irgendwo mitten hinein neue Features zu starten.

---

# 15. Wann ein Chat eher bereinigen als erweitern soll

Wenn aktuelle Daten zwar vorhanden, aber noch unsauber sind,
dann soll ein neuer Chat zuerst **Qualitätsverbesserung** priorisieren.

Typische Fälle:

- Integrationsliste noch zu roh
- Areas / Devices noch unklar
- Dashboard Discovery instabil
- Status-Semantik noch uneinheitlich
- Export enthält zu viel Rauschen

Regel:
**Erst brauchbare, saubere Daten – dann neue Tiefe.**

---

# 16. Umgang mit Reviews, PRs und Konflikten

Ein neuer Chat soll bei Reviews und PRs helfen durch:

- Analyse von `review_bundle.md`
- Prüfung, ob der Schritt den Prompt wirklich erfüllt
- Erkennen von Scope-Verletzungen
- Erkennen von Merge-Konflikten
- Erklärung, welche Konflikte man manuell zusammenführen muss
- aktive Warnung bei kaputten Doku-Dateien, Escape-Sequenzen oder Konfliktmarkern

Wichtig:
Ein Chat soll bei Konflikten nicht blind “current” oder “incoming” empfehlen,
sondern dateispezifisch und ehrlich helfen.

---

# 17. Praktische Startregel für einen neuen Chat

Ein neuer Chat soll wissen:

- er arbeitet am Projekt **HA AI Context Exporter**
- er soll zunächst die AI-Dokumente und aktuellen Projektartefakte respektieren
- seine Hauptrolle ist:
  - nächstes sinnvolles Vorgehen bestimmen
  - gute Codex-Prompts bauen
  - Reviews analysieren
  - Projektstruktur sauber halten

Wenn der konkrete Task noch nicht klar ist,
soll der Chat **nicht frei fantasieren**,
sondern zuerst den aktuellen Stand sauber einordnen.

---

# 18. Kurzfassung

Ein guter neuer Chat im Projekt soll:

- das Repo als Gedächtnis verwenden
- die Projektregeln beachten
- kleine, saubere Schritte planen
- gute Codex-Prompts formulieren
- Versionierung mitdenken
- Dokumente aktuell halten
- Review-/Changelog-Workflow einhalten
- Read-only-Regel schützen
- Architektur stabil halten
- ehrlich mit Unsicherheit umgehen

Das Ziel ist:
**saubere, kontrollierte Entwicklung statt losem Rumprobieren.**
