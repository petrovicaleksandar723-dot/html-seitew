# 🦖 Dino KI — deine eigene KI

Dino KI ist **dein eigener KI-Assistent** — ein echtes Programm auf deinem PC.

**Wichtig & ehrlich:** Dino ist kein eigenes KI-Modell (ein Modell stärker als
Fable 5 kann niemand auf einem normalen PC bauen — das braucht Rechenzentren für
hunderte Millionen €). Dino ist **deine eigene KI, die das Wissen der stärksten
KIs der Welt benutzt** (Claude, ChatGPT, Gemini), sich **jeden Tag dein Wissen
merkt** und dadurch schlauer wird, deinen **Humor** übernimmt, deine **Kunden &
Aufträge verwaltet** und dir **realistische Geld-Pläne** für CleanLines baut.

Es gibt Dino in **zwei Varianten** — nimm die, die dir passt:

- 🖱️ **Fenster (Klick-Oberfläche)** — kein Tippen von Befehlen, alles per Klick. **Empfohlen.**
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

### 3) Dino starten
- 🖱️ **Fenster (empfohlen):** Doppelklick auf **`Dino-KI-Start.bat`**
  - oder im Terminal:  `python3 dino_app.py`
- ⌨️ **Terminal:** Doppelklick auf **`Dino-KI-Terminal.bat`**
  - oder:  `python3 dino.py`

Beim ersten Start trägst du deinen Schlüssel ein (im Fenster unter **»⚙ Einstellungen«**),
dann kann's losgehen. 🦖

---

## Das Fenster (Klick-Oberfläche)

Oben gibt es Reiter:

- **💬 Chat** — ganz normal mit Dino reden. Buttons: *Lernen* und *Rat der KIs*.
- **👥 Kunden** — deine **Kunden & Aufträge verwalten**: anlegen, bearbeiten,
  löschen. Dino sieht unten direkt deinen **Monatsumsatz** und kennt deine
  Kundenliste beim Planen.
- **📈 Plan & Heute** — Knopf für den **Wochen-Geldplan** und den
  **Tages-Check-in** (3 wichtigste Aktionen für heute).
- **🧠 Gedächtnis** — was Dino über dich weiß.
- **⚙ Einstellungen** — Schlüssel, Gehirn (Claude/ChatGPT/Gemini), Humor, Ziel.

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
| `dino_app.py` | die Fenster-Version (Klick-Oberfläche) |
| `dino.py` | die Terminal-Version |
| `dino_core.py` | das gemeinsame Gehirn (von beiden genutzt) |
| `Dino-KI-Start.bat` | Doppelklick-Start fürs Fenster |
| `Dino-KI-Terminal.bat` | Doppelklick-Start fürs Terminal |
| `dino_config.json` | deine Einstellungen + API-Schlüssel *(wird nicht hochgeladen)* |
| `dino_memory.json` | Dinos Gedächtnis + Kunden *(wird nicht hochgeladen)* |
