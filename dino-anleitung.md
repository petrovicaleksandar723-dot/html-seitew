# 🦖 Dino KI — deine eigene KI

Dino KI ist **dein eigener KI-Assistent** — ein echtes Programm auf deinem PC.

**Wichtig & ehrlich:** Dino ist kein eigenes KI-Modell (ein Modell stärker als
Fable 5 kann niemand auf einem normalen PC bauen — das braucht Rechenzentren für
hunderte Millionen €). Dino ist **deine eigene KI, die das Wissen der stärksten
KIs der Welt benutzt** (Claude, ChatGPT, Gemini), sich **jeden Tag dein Wissen
merkt** und dadurch schlauer wird, deinen **Humor** übernimmt und dir
**realistische Geld-Pläne** für CleanLines baut.

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
> (in `dino_config.json`).

### 3) Dino starten
- **Windows:** Doppelklick auf **`Dino-KI-Start.bat`**
- **Mac/Linux / sonst:** Terminal im Ordner öffnen und eingeben:
  ```
  python3 dino.py
  ```

Beim ersten Start fragt Dino nach deinem Schlüssel — eintragen, fertig. 🦖

---

## Was Dino kann (einfach im Chat tippen)

| Befehl | Was passiert |
|--------|--------------|
| *einfach schreiben* | ganz normal mit Dino reden |
| `/plan` | **realistischer Wochen-Geldplan** zu deinem Ziel |
| `/tag` | Tages-Check-in: die **3 wichtigsten Geld-Aktionen** für heute |
| `/rat <frage>` | **alle KIs gleichzeitig fragen** (Claude+ChatGPT+Gemini) + Fazit |
| `/lernen` | Dino merkt sich dauerhaft, was er gelernt hat 🧠 |
| `/gedächtnis` | zeigt, was Dino über dich & dein Business weiß |
| `/persona` | Dinos Name, **Humor** & Business einstellen |
| `/ziel` | dein Geld-Ziel festlegen (z. B. 5000 €/Woche) |
| `/modell` | Gehirn wählen (Claude / ChatGPT / Gemini) |
| `/key` | API-Schlüssel eintragen/ändern |
| `/hilfe` | alle Befehle |
| `/ende` | beenden (Dino lernt beim Beenden automatisch dazu) |

---

## Wie Dino „jeden Tag schlauer wird"

Echte KI-Modelle trainiert man nicht auf einem PC neu — aber Dino wird trotzdem
mit der Zeit besser, weil er ein **wachsendes Gedächtnis** hat:

- Jedes Gespräch landet als kurze Notiz im **Tagebuch** (`dino_memory.json`).
- Mit `/lernen` (oder automatisch beim Beenden) macht Dino daraus **dauerhaftes
  Wissen** über dich, dein Business, deine Ziele und deinen Stil.
- Dieses Wissen steckt Dino bei **jeder** Antwort wieder mit rein — je länger du
  ihn nutzt, desto persönlicher und treffsicherer wird er.

Das ist die ehrliche, echte Version von „lernt jeden Tag dazu". 💪

---

## Deine Dateien (bleiben lokal bei dir)
- `dino.py` — das Programm
- `dino_config.json` — deine Einstellungen + API-Schlüssel
- `dino_memory.json` — Dinos Gedächtnis (wächst mit der Zeit)
