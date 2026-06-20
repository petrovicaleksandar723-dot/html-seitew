# 🦖 Dino KI — deine eigene KI

Dino KI ist **dein eigener KI-Assistent** — ein echtes Programm auf deinem PC.

**Wichtig & ehrlich:** Dino ist kein eigenes KI-Modell (ein Modell stärker als
Fable 5 kann niemand auf einem normalen PC bauen — das braucht Rechenzentren für
hunderte Millionen €). Dino ist **deine eigene KI, die das Wissen der stärksten
KIs der Welt benutzt** (Claude, ChatGPT, Gemini), sich **jeden Tag dein Wissen
merkt** und dadurch schlauer wird, deinen **Humor** übernimmt, deine **Kunden &
Aufträge verwaltet** und dir **realistische Geld-Pläne** für CleanLines baut.

Es gibt Dino in **drei Varianten** — nimm die, die dir passt:

- ⚡ **Jarvis-Chatfenster (App)** — du startest die App, ein edles dunkles
  Chat-Fenster öffnet sich automatisch im Browser. **Mit Mikro (reden) und
  Sprachausgabe.** Das ist die Hauptversion. **Empfohlen.**
- 🖱️ **Klassisches Fenster** — einfache Klick-Oberfläche (tkinter).
- ⌨️ **Terminal** — die schnelle Tastatur-Variante.

---

## In 3 Schritten starten

### 1) Python installieren (einmalig, gratis)
- Hol dir Python: https://www.python.org/downloads/
- Bei der Installation **unbedingt den Haken „Add Python to PATH"** setzen.
- (Auf den meisten Macs ist Python schon dabei.)

### 2) Einen API-Schlüssel holen (das ist „das Gehirn")
Such dir **mindestens einen** aus — Claude wird empfohlen:

| KI | Schlüssel holen | Hinweis |
|----|------------------|---------|
| **Claude** (empfohlen) | https://console.anthropic.com/ → *API Keys* | Stärkstes Standard-Gehirn |
| ChatGPT (OpenAI) | https://platform.openai.com/api-keys | Optional, zweites Gehirn |
| Gemini (Google) | https://aistudio.google.com/apikey | Optional, drittes Gehirn |

> Der Schlüssel ist gratis zu erstellen. Du zahlst nur deine Nutzung
> (Cent-Beträge pro Gespräch). Der Schlüssel bleibt **nur lokal** auf deinem PC
> (in `dino_config.json`) und wird **nie** hochgeladen.

> **🆓 Lieber komplett gratis ohne Schlüssel?** Geht auch! Siehe Abschnitt
> **„Gratis-Modus (Ollama)"** weiter unten.

### 3) Dino starten
- ⚡ **Jarvis-Chatfenster (empfohlen):** Doppelklick auf **`Dino-KI-Start.bat`**
  - oder im Terminal:  `python3 dino_server.py`
  - Es öffnet sich automatisch das Chat-Fenster im Browser (Adresse `127.0.0.1`,
    läuft nur lokal auf deinem PC). **Das Fenster, das im Hintergrund aufgeht,
    offen lassen** — das ist Dinos Motor. Schließen = Dino aus.
- 🖱️ **Klassisches Fenster:** `python3 dino_app.py`
- ⌨️ **Terminal:** Doppelklick auf **`Dino-KI-Terminal.bat`**  (oder `python3 dino.py`)

Beim ersten Start trägst du deinen Schlüssel ein (unter **»⚙ Einstellungen«**),
dann kann's losgehen. 🦖

---

## Das Jarvis-Chatfenster (App)

Ein edles, dunkles Chat-Fenster — wie ein echter KI-Assistent:

- **💬 Chat in der Mitte** — einfach reden, Dino antwortet. Mit Tipp-Animation
  und leuchtendem „Core", der pulsiert während Dino denkt.
- **🎤 Mikro** — reinsprechen statt tippen (Spracherkennung im Browser).
- **🔊 Sprachausgabe** — Dino liest seine Antworten vor (an-/ausschaltbar).
- **Schnell-Knöpfe:** 📅 Wochenplan · ☀️ Heute · 🧠 Lernen · 🧠🧠🧠 Rat der KIs.
- **👥 Kunden** — Kunden & Aufträge verwalten, Umsatz im Blick.
- **🧠 Gedächtnis** — was Dino über dich weiß.
- **⚙ Einstellungen** — Schlüssel, Gehirn (Claude/ChatGPT/Gemini), Humor, Ziel.

> Hinweis: Mikro & Sprachausgabe brauchen einen modernen Browser (Chrome/Edge).
> Beim ersten Mikro-Klick fragt der Browser nach der Mikrofon-Erlaubnis.

---

## Terminal-Befehle (für die ⌨️-Variante)

| Befehl | Was passiert |
|--------|--------------|
| *einfach schreiben* | normal mit Dino reden |
| `/plan` | realistischer Wochen-Geldplan |
| `/tag` | Tages-Check-in (3 Aktionen für heute) |
| `/kunden` | Kunden & Aufträge verwalten |
| `/rat <frage>` | alle KIs fragen + Fazit |
| `/lernen` | Dino merkt sich dauerhaft, was er gelernt hat 🧠 |
| `/gedächtnis` | zeigt, was Dino weiß |
| `/persona` | Name, Humor & Business einstellen |
| `/ziel` | Geld-Ziel festlegen |
| `/modell` | Gehirn wählen |
| `/key` | API-Schlüssel eintragen |
| `/ende` | beenden (Dino lernt beim Beenden dazu) |

---

## 🆓 Gratis-Modus (Ollama) — ohne Schlüssel, ohne Bezahlung

Wenn du **keinen API-Schlüssel** nutzen willst, kann Dino ein KI-Modell
**direkt auf deinem PC** laufen lassen — gratis und offline.

1. **Ollama installieren** (kostenlos): https://ollama.com/download
2. **Ein Modell laden** — Terminal/Eingabeaufforderung öffnen und eintippen:
   ```
   ollama run llama3.2
   ```
   (lädt das Modell einmalig herunter und startet es)
3. **In Dino umschalten:** Dino starten → **⚙ Einstellungen** → Anbieter
   **„🆓 Gratis lokal (Ollama)"** wählen → **Speichern**. Fertig. 🦖

**Ehrlich:** Das Gratis-Modell ist **schwächer und langsamer** als Claude und
dein PC sollte halbwegs aktuell sein (am besten 8 GB RAM+). Für den Anfang
reicht es — und du kannst jederzeit auf den starken Claude umschalten.

---

## Wie Dino „jeden Tag schlauer wird"

Echte KI-Modelle trainiert man nicht auf einem PC neu — aber Dino wird trotzdem
besser, weil er ein **wachsendes Gedächtnis** hat:

- Jedes Gespräch landet als Notiz im **Tagebuch** (`dino_memory.json`).
- Mit **Lernen** (oder automatisch beim Beenden) macht Dino daraus **dauerhaftes
  Wissen** über dich, dein Business, deine Kunden und deinen Stil.
- Dieses Wissen + deine **Kundenliste** steckt Dino bei **jeder** Antwort wieder
  mit rein — je länger du ihn nutzt, desto persönlicher und treffsicherer.

Das ist die ehrliche, echte Version von „lernt jeden Tag dazu". 💪

---

## Deine Dateien (bleiben lokal bei dir)
| Datei | Was es ist |
|-------|------------|
| `dino_server.py` | die Jarvis-App (startet Server + Chat-Fenster) |
| `dino_chat.html` | das Jarvis-Chatfenster (Oberfläche) |
| `dino_app.py` | klassisches Fenster (tkinter) |
| `dino.py` | die Terminal-Version |
| `dino_core.py` | das gemeinsame Gehirn (von allen genutzt) |
| `Dino-KI-Start.bat` | Doppelklick-Start für die Jarvis-App |
| `Dino-KI-Terminal.bat` | Doppelklick-Start fürs Terminal |
| `dino_config.json` | deine Einstellungen + API-Schlüssel *(wird nicht hochgeladen)* |
| `dino_memory.json` | Dinos Gedächtnis + Kunden *(wird nicht hochgeladen)* |
