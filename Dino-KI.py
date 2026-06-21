#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DINO KI - EINE Datei. Gratis & lokal ueber Ollama, mit Gideon-Sprachausgabe
und dem Agenten-Team. Starten:  python Dino-KI.py
"""

# -*- coding: utf-8 -*-
"""
🦖 dino_core — das gemeinsame Gehirn von Dino KI.

Wird von BEIDEN Oberflächen benutzt:
  • dino.py      — Dino im Terminal
  • dino_app.py  — Dino als Fenster (Klick-Oberfläche)

Enthält: Einstellungen, Gedächtnis, Kunden-/Auftragsverwaltung, und die
Anbindung an die stärksten KIs (Claude / ChatGPT / Gemini).
Reines Python (Standardbibliothek) — keine Extra-Pakete nötig.
"""

import json
import os
import re
import shutil
import subprocess
import time
import uuid
import datetime
import webbrowser
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(HERE, "dino_config.json")
MEMORY_FILE = os.path.join(HERE, "dino_memory.json")

# ── Modelle ────────────────────────────────────────────────────────────
CLAUDE_MODELS = {
    "1": ("claude-opus-4-8", "Claude Opus 4.8 — stark & schnell (empfohlen)"),
    "2": ("claude-fable-5",  "Claude Fable 5 — das STÄRKSTE Modell der Welt (langsamer)"),
    "3": ("claude-sonnet-4-6", "Claude Sonnet 4.6 — schnell & günstig"),
}

# Gratis lokale Modelle (Ollama). Empfehlung richtet sich nach PC-Stärke.
OLLAMA_MODELS = {
    "1": ("llama3.2",     "Klein & flott (3B) — für schwächere PCs"),
    "2": ("qwen2.5:7b",   "Stark & ausgewogen (7B) — EMPFOHLEN für deinen PC"),
    "3": ("llama3.1:8b",  "Stark, sehr gut auf Deutsch (8B)"),
    "4": ("qwen2.5:14b",  "Am schlausten (14B) — braucht ~12 GB Grafikkarte"),
}
# Das empfohlene, stärkere Standard-Modell (läuft gut auf 12-GB-Grafikkarten).
RECOMMENDED_OLLAMA = "qwen2.5:7b"

# ── Dinos Team aus Spezial-Agenten ─────────────────────────────────────
# Jeder Agent ist eine Rolle, die Dino bei einer Aufgabe einnehmen kann.
# (emoji, anzeigename, rollen-anweisung)
AGENTS = {
    "stratege":    ("🧭", "Stratege",
                    "Du bist Dinos Stratege. Du setzt Prioritäten, baust den klaren Weg zum "
                    "Ziel und erkennst, was ZUERST den meisten Hebel hat. Denk in Schritten."),
    "verkaeufer":  ("📈", "Verkäufer",
                    "Du bist Dinos Akquise- & Verkaufs-Profi: neue Kunden finden, anschreiben, "
                    "Einwände entkräften, Abschlüsse holen. Liefer FERTIGE Nachrichten/Skripte."),
    "content":     ("🎬", "Content-Creator",
                    "Du bist Dinos Content-Profi: Hooks, kurze Skripte, Captions und Post-Ideen "
                    "für CleanLines, die Kunden anziehen. Liefer fertige, sofort nutzbare Texte."),
    "geld":        ("💰", "Geld-Manager",
                    "Du bist Dinos Geld-Manager: Preise, Pakete, Umsatz-Mathe und der realistische "
                    "Weg zum Geld-Ziel. Rechne mit ECHTEN Zahlen — keine Luftschlösser."),
    "rechercheur": ("🔎", "Rechercheur",
                    "Du bist Dinos Rechercheur: Ideen, Marktwinkel, Zielgruppen und was gerade "
                    "funktioniert. Konkrete, umsetzbare Vorschläge statt Theorie."),
    "kritiker":    ("🛡️", "Kritiker",
                    "Du bist Dinos ehrlicher Kritiker: du findest Schwachstellen, Risiken und "
                    "unrealistische Annahmen — und sagst klar, wie man sie behebt."),
}
# Wortvarianten -> Agenten-Schlüssel (falls das Modell anders schreibt)
_AGENT_ALIASES = {
    "sales": "verkaeufer", "verkauf": "verkaeufer", "verkäufer": "verkaeufer", "vertrieb": "verkaeufer",
    "strategy": "stratege", "strateg": "stratege", "planer": "stratege",
    "money": "geld", "geld-manager": "geld", "finanzen": "geld", "finance": "geld",
    "content-creator": "content", "creator": "content", "marketing": "content",
    "research": "rechercheur", "recherche": "rechercheur", "researcher": "rechercheur",
    "critic": "kritiker", "kritik": "kritiker",
}

# ── PC-Steuerung (Dino als Jarvis — Ausführung NUR nach Klick-Bestätigung) ─
# Sicherer Arbeitsordner für Datei-Aktionen (kein Zugriff ausserhalb davon).
DINO_FILES_DIR = os.path.join(os.path.expanduser("~"), "Dino-Dateien")

# Aktion -> (Anzeigename, Kurzbeschreibung für den Prompt, braucht_extra_warnung)
ACTIONS = {
    "app_oeffnen":     ("Programm öffnen", "öffnet ein Programm (z.B. notepad, rechner, explorer, browser)", False),
    "web_oeffnen":     ("Webseite öffnen", "öffnet eine Webseite im Browser", False),
    "ordner_oeffnen":  ("Ordner öffnen", "öffnet einen Ordner im Datei-Explorer", False),
    "datei_schreiben": ("Datei schreiben", "legt eine Textdatei in 'Dino-Dateien' an (Format: name ::: inhalt)", False),
    "datei_lesen":     ("Datei lesen", "liest eine Textdatei aus 'Dino-Dateien'", False),
    "dateien_liste":   ("Dateien auflisten", "listet Dateien in 'Dino-Dateien' (oder einem Unterordner)", False),
    "system_info":     ("System-Info", "zeigt PC-Infos (Betriebssystem, CPU, Speicher, Festplatte)", False),
    "befehl":          ("Befehl ausführen", "führt einen beliebigen Konsolen-Befehl aus — mit Vorsicht", True),
}

# ── Web-Recherche (frisches Wissen aus dem Internet) ──────────────────
WEB_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# ── Govee-Lampen (offizielle API — Dino steuert das Licht) ─────────────
GOVEE_BASE = "https://openapi.api.govee.com/router/api/v1"
GOVEE_ACTIONS = {
    "licht_an":         ("Licht an", "schaltet die Govee-Lampen an", False),
    "licht_aus":        ("Licht aus", "schaltet die Govee-Lampen aus", False),
    "licht_farbe":      ("Lichtfarbe", "setzt die Farbe der Lampen (z.B. blau, rot, warm)", False),
    "licht_helligkeit": ("Helligkeit", "setzt die Helligkeit der Lampen (0–100)", False),
}
# Farbnamen (deutsch) -> RGB
GOVEE_COLORS = {
    "rot": (255, 0, 0), "grün": (0, 255, 0), "gruen": (0, 255, 0), "blau": (0, 0, 255),
    "weiß": (255, 255, 255), "weiss": (255, 255, 255), "gelb": (255, 220, 0),
    "orange": (255, 110, 0), "lila": (150, 0, 255), "violett": (150, 0, 255),
    "pink": (255, 0, 150), "rosa": (255, 105, 180), "türkis": (0, 230, 200),
    "tuerkis": (0, 230, 200), "cyan": (0, 255, 255), "magenta": (255, 0, 255),
    "warm": (255, 170, 90), "warmweiß": (255, 170, 90), "warmweiss": (255, 170, 90),
    "kalt": (200, 220, 255), "kaltweiß": (200, 220, 255), "grün-gelb": (180, 255, 0),
}
# Alle Aktionen zusammen (für Erkennung/Ausführung)
ALL_ACTIONS = {**ACTIONS, **GOVEE_ACTIONS}

# ── Kunden ─────────────────────────────────────────────────────────────
CUSTOMER_STATUS = ["Lead", "Angebot", "Aktiv", "Bezahlt", "Pausiert", "Beendet"]
ACTIVE_STATUS = {"Aktiv", "Bezahlt"}  # zählt zum laufenden Umsatz

DEFAULT_CONFIG = {
    "provider": "ollama",  # ab Werk gratis & lokal (kein Schlüssel nötig)
    "claude_model": "claude-opus-4-8",
    "openai_model": "",
    "gemini_model": "gemini-2.5-pro",
    "ollama_model": "qwen2.5:7b",
    "ollama_url": "http://127.0.0.1:11434",
    "keys": {"claude": "", "openai": "", "gemini": ""},
    "persona": {
        "user_name": "Boss",
        "assistant_name": "Dino",
        "business": "CleanLines Studio — monatliche KI-Content-Pakete für lokale Betriebe",
        "humor": "locker, direkt, mit Humor, Du-Form, gelegentlich Emojis, motivierend statt geschwollen",
    },
    "goal": "Mindestens 5000 € pro Woche mit CleanLines Studio — realistisch über Wochen aufgebaut",
    "pc_control": True,  # Dino darf PC-Aktionen vorschlagen (Ausführung nur mit Klick-Bestätigung)
    "govee_key": "",     # Schlüssel für die Govee-Lampen (Licht steuern)
}

DEFAULT_MEMORY = {
    "facts": [],
    "journal": [],
    "customers": [],
    "next_customer_id": 1,
}


def today():
    return datetime.date.today().isoformat()


def _load(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(default, dict):
            for k, v in default.items():
                data.setdefault(k, v)
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return json.loads(json.dumps(default))


def _save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _http_msg(e):
    """Holt die ECHTE Fehlermeldung aus der Antwort (auch wenn 'error' ein String ist,
    wie bei Ollama). Vorher wurde nur 'Fehler 500' angezeigt — jetzt der echte Grund."""
    msg = ""
    try:
        body = e.read().decode("utf-8")
        try:
            info = json.loads(body)
            err = info.get("error")
            if isinstance(err, dict):
                msg = err.get("message") or err.get("type") or json.dumps(err, ensure_ascii=False)
            elif isinstance(err, str):
                msg = err
            else:
                msg = body
        except Exception:
            msg = body
    except Exception:
        msg = str(e)
    code = getattr(e, "code", "?")
    if code == 401:
        return f"Schlüssel ungültig (401). Prüf ihn in den Einstellungen.  [{msg}]"
    if code == 429:
        return f"Zu viele Anfragen / Guthaben leer (429).  [{msg}]"
    return f"Fehler {code}: {msg}"


def euro(x):
    try:
        return f"{float(x):,.0f} €".replace(",", ".")
    except (ValueError, TypeError):
        return "0 €"


def _model_too_big(name):
    """Grobe Einschätzung: Modelle ab ~20 Mrd. Parametern sind für normale PCs zu groß."""
    import re
    n = (name or "").lower()
    if "qwen3.6" in n or ":70b" in n or ":72b" in n or ":405b" in n:
        return True
    for num in re.findall(r"(\d+)\s*b", n):
        try:
            if int(num) >= 20:
                return True
        except ValueError:
            pass
    return False


class Dino:
    """Das Gehirn. Hält Einstellungen + Gedächtnis und kann mit den KIs reden."""

    def __init__(self):
        self.config = _load(CONFIG_FILE, DEFAULT_CONFIG)
        self.memory = _load(MEMORY_FILE, DEFAULT_MEMORY)

    # ── Speichern ──────────────────────────────────────────────────────
    def save_config(self):
        _save(CONFIG_FILE, self.config)

    def save_memory(self):
        _save(MEMORY_FILE, self.memory)

    # ── Status-Helfer ──────────────────────────────────────────────────
    def has_any_key(self):
        return any(self.config["keys"].values())

    def is_ready(self):
        """Kann Dino jetzt denken? (Ollama braucht keinen Schlüssel.)"""
        prov = self.config["provider"]
        if prov == "ollama":
            return True
        if prov == "openai":
            return bool(self.config["keys"]["openai"] and self.config["openai_model"])
        if prov == "gemini":
            return bool(self.config["keys"]["gemini"])
        return bool(self.config["keys"]["claude"])

    def ollama_status(self):
        """Läuft Ollama lokal? Welche Modelle sind installiert? (für das Setup im Fenster)"""
        url = self.config.get("ollama_url", "http://127.0.0.1:11434").rstrip("/") + "/api/tags"
        current = self.config.get("ollama_model", "llama3.2")
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            models = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
            return {"running": True, "models": models, "current_model": current,
                    "url": self.config.get("ollama_url", "http://127.0.0.1:11434")}
        except Exception:
            return {"running": False, "models": [], "current_model": current,
                    "url": self.config.get("ollama_url", "http://127.0.0.1:11434")}

    def ensure_ollama(self, log=print):
        """Auto-Setup: startet Ollama falls nötig und lädt das Modell, wenn es fehlt.
        Der Modell-Download läuft über die Ollama-HTTP-Schnittstelle — unabhängig
        davon, ob das 'ollama'-Kommando im PATH liegt."""
        if self.config["provider"] != "ollama":
            return
        st = self.ollama_status()
        if not st["running"]:
            exe = shutil.which("ollama")
            if exe:
                log("  Starte das lokale Gehirn (Ollama)…")
                try:
                    kwargs = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
                    if os.name == "nt":
                        kwargs["creationflags"] = 0x00000008  # DETACHED_PROCESS
                    subprocess.Popen([exe, "serve"], **kwargs)
                except Exception:
                    pass
                for _ in range(20):
                    time.sleep(1)
                    if self.ollama_status()["running"]:
                        break
            st = self.ollama_status()
        if not st["running"]:
            log("  ⚠ Ollama läuft noch nicht. Öffne die Ollama-App einmal — "
                "oder installier es: https://ollama.com/download")
            return
        model = self.config.get("ollama_model", RECOMMENDED_OLLAMA)
        # Auto-Upgrade: das schwache Auto-Fallback llama3.2 auf das empfohlene,
        # stärkere Modell heben — außer der Nutzer hat selbst eins gewählt.
        if model in ("llama3.2", "llama3.2:latest", "") and not self.config.get("ollama_locked"):
            log(f"  Rüste Dino auf ein stärkeres Modell auf: {RECOMMENDED_OLLAMA}")
            model = RECOMMENDED_OLLAMA
            self.config["ollama_model"] = model
            self.save_config()
        # Zu großes Modell? Automatisch auf das kleine, sichere llama3.2 wechseln.
        if _model_too_big(model):
            log(f"  Modell '{model}' ist zu groß für die meisten PCs —")
            log("  wechsle automatisch auf das kleine 'llama3.2' (läuft auf deinem PC).")
            model = "llama3.2"
            self.config["ollama_model"] = model
            self.save_config()

        if ":" in model:
            have = model in st["models"]
        else:
            have = any(m == model or m.split(":")[0] == model for m in st["models"])
        if have:
            log(f"  ✓ Dinos Gehirn ist bereit: {model}")
            return
        log(f"  Lade Dinos Gehirn herunter: {model}")
        log("  (einmalig, ein paar Minuten — bitte dieses Fenster offen lassen)…")
        if self._ollama_pull_http(model, log):
            log("  ✓ Modell geladen. Los geht's!")
        else:
            log(f"    Falls es klemmt, im Terminal:  ollama pull {model}")

    def _ollama_pull_http(self, model, log=print):
        """Lädt ein Modell über die Ollama-HTTP-API und zeigt den Fortschritt in %."""
        url = self.config.get("ollama_url", "http://127.0.0.1:11434").rstrip("/") + "/api/pull"
        body = json.dumps({"name": model, "stream": True}).encode("utf-8")
        req = urllib.request.Request(url, data=body,
                                     headers={"content-type": "application/json"}, method="POST")
        last_status, last_pct = "", -10
        try:
            with urllib.request.urlopen(req, timeout=3600) as resp:
                for raw in resp:
                    raw = raw.strip()
                    if not raw:
                        continue
                    try:
                        obj = json.loads(raw.decode("utf-8"))
                    except Exception:
                        continue
                    if obj.get("error"):
                        log("    Fehler: " + str(obj["error"]))
                        return False
                    status = obj.get("status", "")
                    total, completed = obj.get("total"), obj.get("completed")
                    if total and completed:
                        pct = int(completed * 100 / total)
                        if pct >= last_pct + 5:
                            log(f"    … {pct}%")
                            last_pct = pct
                    elif status and status != last_status:
                        log("    … " + status)
                        last_status = status
            return True
        except Exception as e:
            log("    Konnte das Modell nicht laden: " + str(e))
            return False

    def provider_label(self):
        prov = self.config["provider"]
        if prov == "openai":
            return f"ChatGPT · {self.config['openai_model'] or '(kein Modell)'}"
        if prov == "gemini":
            return f"Gemini · {self.config['gemini_model']}"
        if prov == "ollama":
            return f"Gratis lokal · {self.config.get('ollama_model', 'llama3.2')}"
        return f"Claude · {self.config['claude_model']}"

    # ── Kunden / Aufträge ──────────────────────────────────────────────
    def customers(self):
        return self.memory.setdefault("customers", [])

    def add_customer(self, name, branche="", kontakt="", paket="", preis=0.0,
                     status="Lead", naechster_schritt="", notizen=""):
        cid = self.memory.get("next_customer_id", 1)
        self.memory["next_customer_id"] = cid + 1
        cust = {
            "id": cid,
            "name": name.strip() or f"Kunde {cid}",
            "branche": branche.strip(),
            "kontakt": kontakt.strip(),
            "paket": paket.strip(),
            "preis": _to_float(preis),
            "status": status if status in CUSTOMER_STATUS else "Lead",
            "naechster_schritt": naechster_schritt.strip(),
            "notizen": notizen.strip(),
            "erstellt": today(),
        }
        self.customers().append(cust)
        self.save_memory()
        self.add_journal(f"Kunde angelegt: {cust['name']} ({cust['status']})")
        return cust

    def update_customer(self, cid, **fields):
        for c in self.customers():
            if c["id"] == cid:
                if "preis" in fields:
                    fields["preis"] = _to_float(fields["preis"])
                c.update({k: v for k, v in fields.items() if k in c})
                self.save_memory()
                return c
        return None

    def delete_customer(self, cid):
        before = len(self.customers())
        self.memory["customers"] = [c for c in self.customers() if c["id"] != cid]
        self.save_memory()
        return len(self.memory["customers"]) < before

    def get_customer(self, cid):
        for c in self.customers():
            if c["id"] == cid:
                return c
        return None

    def revenue(self):
        monthly = sum(_to_float(c.get("preis", 0))
                      for c in self.customers() if c.get("status") in ACTIVE_STATUS)
        return {
            "monthly": monthly,
            "weekly": monthly / 4.33,
            "active": sum(1 for c in self.customers() if c.get("status") in ACTIVE_STATUS),
            "leads": sum(1 for c in self.customers() if c.get("status") in ("Lead", "Angebot")),
            "total": len(self.customers()),
        }

    def _customers_for_prompt(self):
        custs = self.customers()
        if not custs:
            return "(noch keine Kunden eingetragen)"
        lines = []
        for c in custs:
            preis = euro(c["preis"]) + "/Monat" if c.get("preis") else "kein Preis"
            schritt = f" — nächster Schritt: {c['naechster_schritt']}" if c.get("naechster_schritt") else ""
            branche = f" ({c['branche']})" if c.get("branche") else ""
            paket = f" — {c['paket']}" if c.get("paket") else ""
            lines.append(f"- [{c['status']}] {c['name']}{branche}{paket} — {preis}{schritt}")
        r = self.revenue()
        lines.append(f"Aktiver Monatsumsatz: {euro(r['monthly'])} (~{euro(r['weekly'])}/Woche) "
                     f"aus {r['active']} zahlenden Kunden, {r['leads']} offene Leads.")
        return "\n".join(lines)

    # ── Gedächtnis ─────────────────────────────────────────────────────
    def add_journal(self, note):
        self.memory.setdefault("journal", []).append({"date": today(), "note": str(note)[:280]})
        self.memory["journal"] = self.memory["journal"][-200:]
        self.save_memory()

    def clear_memory(self):
        self.memory["facts"] = []
        self.memory["journal"] = []
        self.save_memory()

    # ── System-Prompt (hier wird Dino persönlich & schlau) ─────────────
    def build_system(self):
        p = self.config["persona"]
        facts = self.memory.get("facts", [])
        journal = self.memory.get("journal", [])[-20:]
        facts_txt = "\n".join(f"- {x}" for x in facts) if facts else "- (noch nichts gelernt)"
        journal_txt = "\n".join(f"- [{j['date']}] {j['note']}" for j in journal) if journal else "- (leer)"
        return f"""Du bist {p['assistant_name']} KI — die persönliche, eigene KI von {p['user_name']}.
Du bist kein Konzern-Bot, sondern {p['user_name']}s eigener Assistent. Du nutzt das
Wissen der stärksten KIs der Welt, um {p['user_name']} wirklich nach vorne zu bringen.

DEIN STIL / HUMOR (genau so antworten):
{p['humor']}
Sprache: Deutsch. Sei konkret und ehrlich. Keine leeren Versprechen, kein Geschwafel.
Wenn du etwas nicht sicher weißt, sag es. Bei Geld/Erfolg: realistisch bleiben.
Denk bei kniffligen Fragen erst kurz Schritt für Schritt durch, bevor du antwortest —
gib dann eine klare, gut durchdachte Antwort. Lieber richtig als schnell.

DAS BUSINESS:
{p['business']}

DAS ZIEL:
{self.config['goal']}

DEINE KUNDEN & AUFTRÄGE (Stand jetzt):
{self._customers_for_prompt()}

WAS DU ÜBER {p['user_name'].upper()} GELERNT HAST (dauerhaftes Gedächtnis):
{facts_txt}

LETZTE NOTIZEN:
{journal_txt}

Wichtig: Du handelst nie eigenmächtig nach außen (keine Mails/Posts ohne Freigabe).
Du machst Vorschläge und {p['user_name']} entscheidet. Du kennst die Kundenliste oben
und kannst damit rechnen, Inhalte für einzelne Kunden schreiben und den Weg zum
Ziel planen.
{self._pc_help()}{self._govee_help()}"""

    def _pc_help(self):
        """Erklärt Dino, wie er PC-Aktionen vorschlägt (Ausführung nur nach Klick)."""
        if not self.config.get("pc_control", True):
            return ""
        lines = "\n".join(f"  [AKTION] {name} | <wert>   — {desc}"
                          for name, (_t, desc, _w) in ACTIONS.items())
        return f"""

DU KANNST {self.config['persona']['user_name'].upper()}S PC STEUERN (wie Jarvis).
Wenn eine Aufgabe eine Aktion am Computer braucht, schreib sie in einer EIGENEN Zeile
in GENAU diesem Format (eine Aktion pro Zeile):
  [AKTION] <name> | <wert>
Verfügbare Aktionen:
{lines}
Beispiele:
  [AKTION] app_oeffnen | notepad
  [AKTION] web_oeffnen | youtube.com
  [AKTION] datei_schreiben | ideen.txt ::: Meine 3 besten Content-Ideen ...
  [AKTION] befehl | echo hallo
WICHTIG: Du FÜHRST nichts selbst aus. {self.config['persona']['user_name']} sieht jede
Aktion als Knopf und bestätigt sie per Klick. Schlag die Aktion vor, erklär in einem
kurzen Satz, was sie bewirkt, und behaupte NIE, etwas sei schon erledigt, bevor die
Bestätigung kam. Schlag bei heiklen Befehlen lieber den kleinsten, sichersten Schritt vor.

NUR-AUF-BEFEHL-REGEL: Schlag das Öffnen von Webseiten oder Programmen (web_oeffnen,
app_oeffnen, ordner_oeffnen) AUSSCHLIESSLICH dann vor, wenn {self.config['persona']['user_name']}
dich ausdrücklich darum bittet (z.B. »öffne …«, »mach … auf«, »starte …«, »zeig mir …«).
Niemals ungefragt von dir aus. Ohne klare Bitte: keine Öffnen-Aktion vorschlagen, sondern
einfach normal antworten."""

    def _govee_help(self):
        """Govee-Licht-Aktionen — nur wenn ein Govee-Schlüssel hinterlegt ist."""
        if not self.config.get("govee_key", "").strip():
            return ""
        gl = "\n".join(f"  [AKTION] {name} | <wert>   — {desc}"
                       for name, (_t, desc, _w) in GOVEE_ACTIONS.items())
        return f"""

DU STEUERST AUCH {self.config['persona']['user_name'].upper()}S GOVEE-LAMPEN.
Wenn {self.config['persona']['user_name']} das Licht ändern will, nutze diese Aktionen:
{gl}
Beispiele:
  [AKTION] licht_an |
  [AKTION] licht_aus |
  [AKTION] licht_farbe | blau
  [AKTION] licht_helligkeit | 60
Diese Licht-Aktionen sind harmlos und laufen sofort (ohne extra Bestätigung)."""

    # ── Die drei Gehirne ───────────────────────────────────────────────
    @staticmethod
    def _post(url, headers, body, timeout=300):
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def ask_claude(self, system, messages, max_tokens=4096, effort="medium"):
        key = self.config["keys"]["claude"]
        if not key:
            return None, "Kein Claude-Schlüssel hinterlegt (Einstellungen → Schlüssel)."
        body = {
            "model": self.config["claude_model"],
            "max_tokens": max_tokens,
            "system": system,
            "messages": messages,
            "output_config": {"effort": effort},
        }
        headers = {
            "content-type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "anthropic-dangerous-direct-browser-access": "true",
        }
        try:
            data = self._post("https://api.anthropic.com/v1/messages", headers, body)
            if data.get("stop_reason") == "refusal":
                return None, "Claude hat aus Sicherheitsgründen abgelehnt. Formulier es anders."
            parts = [b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"]
            return "".join(parts).strip(), None
        except urllib.error.HTTPError as e:
            return None, _http_msg(e)
        except Exception as e:
            return None, f"Verbindungsfehler: {e}"

    def ask_openai(self, system, messages, max_tokens=4096):
        key = self.config["keys"]["openai"]
        if not key:
            return None, "Kein OpenAI-Schlüssel hinterlegt."
        if not self.config["openai_model"]:
            return None, "Kein OpenAI-Modell gesetzt (Einstellungen)."
        msgs = [{"role": "system", "content": system}] + messages
        body = {"model": self.config["openai_model"], "messages": msgs, "max_tokens": max_tokens}
        headers = {"content-type": "application/json", "authorization": f"Bearer {key}"}
        try:
            data = self._post("https://api.openai.com/v1/chat/completions", headers, body)
            return data["choices"][0]["message"]["content"].strip(), None
        except urllib.error.HTTPError as e:
            return None, _http_msg(e)
        except Exception as e:
            return None, f"Verbindungsfehler: {e}"

    def ask_gemini(self, system, messages, max_tokens=4096):
        key = self.config["keys"]["gemini"]
        if not key:
            return None, "Kein Gemini-Schlüssel hinterlegt."
        contents = [{"role": "user" if m["role"] == "user" else "model",
                     "parts": [{"text": m["content"]}]} for m in messages]
        body = {
            "system_instruction": {"parts": [{"text": system}]},
            "contents": contents,
            "generationConfig": {"maxOutputTokens": max_tokens},
        }
        model = self.config["gemini_model"]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        try:
            data = self._post(url, {"content-type": "application/json"}, body)
            parts = data["candidates"][0]["content"]["parts"]
            return "".join(p.get("text", "") for p in parts).strip(), None
        except urllib.error.HTTPError as e:
            return None, _http_msg(e)
        except Exception as e:
            return None, f"Verbindungsfehler: {e}"

    def ask_ollama(self, system, messages, max_tokens=4096):
        """Gratis-Gehirn: ein KI-Modell, das lokal über Ollama läuft (kein Schlüssel).
        Robust: wartet beim ersten Laden des Modells und versucht es bei 5xx nochmal."""
        url = self.config.get("ollama_url", "http://127.0.0.1:11434").rstrip("/") + "/api/chat"
        model = self.config.get("ollama_model", "llama3.2")
        msgs = [{"role": "system", "content": system}] + messages
        # Tempo: Modell 30 Min geladen halten (kein Neu-Laden zwischen den Team-Runden)
        # und einen schlanken, aber ausreichenden Kontext nutzen.
        body = {"model": model, "messages": msgs, "stream": False,
                "keep_alive": "30m",
                "options": {"num_predict": max_tokens, "num_ctx": 4096}}
        headers = {"content-type": "application/json"}
        last_err = None
        for attempt in range(3):
            try:
                data = self._post(url, headers, body, timeout=600)
                return (data.get("message", {}).get("content", "") or "").strip(), None
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return None, (f"Modell »{model}« ist nicht installiert. Wähl in ⚙ Einstellungen "
                                  f"ein vorhandenes Modell — oder im Terminal:  ollama pull {model}")
                last_err = _http_msg(e)
                low = last_err.lower()
                if ("memory" in low or "out of" in low) and model.split(":")[0] != "llama3.2":
                    return None, (last_err + "  →  Das Modell ist zu groß für deinen Speicher. "
                                  "Stell in ⚙ Einstellungen das Modell auf  llama3.2  (klein) und speichere.")
                if e.code >= 500 and attempt < 2:
                    time.sleep(2.5)  # Modell lädt evtl. gerade — kurz warten und nochmal
                    continue
                return None, last_err
            except urllib.error.URLError:
                return None, ("Ollama läuft nicht. Öffne die Ollama-App einmal — "
                              "oder installier es gratis: https://ollama.com/download")
            except Exception as e:
                return None, f"Verbindungsfehler zu Ollama: {e}"
        return None, (last_err or "Unbekannter Fehler beim lokalen Modell.")

    def ask_provider(self, system, messages, max_tokens=4096, effort="medium"):
        prov = self.config["provider"]
        if prov == "openai":
            return self.ask_openai(system, messages, max_tokens)
        if prov == "gemini":
            return self.ask_gemini(system, messages, max_tokens)
        if prov == "ollama":
            return self.ask_ollama(system, messages, max_tokens)
        return self.ask_claude(system, messages, max_tokens, effort)

    # ── Hohe Funktionen ────────────────────────────────────────────────
    def chat(self, history, max_tokens=4096, effort="medium"):
        text, err = self.ask_provider(self.build_system(), history, max_tokens, effort)
        # Selbstheilung: bei Speicher-Fehler im Gratis-Modus auf ein kleineres
        # installiertes Modell wechseln und nochmal versuchen.
        if err and self.config["provider"] == "ollama" and \
                ("memory" in err.lower() or "out of" in err.lower() or "too large" in err.lower()):
            st = self.ollama_status()
            cur = self.config.get("ollama_model", "")
            order = ("llama3.2", "phi3", "qwen3", "gemma4", "llama3.1")
            smaller = None
            for base in order:
                smaller = next((m for m in st["models"]
                                if m.split(":")[0] == base and m != cur), None)
                if smaller:
                    break
            if smaller:
                self.config["ollama_model"] = smaller
                self.save_config()
                text2, err2 = self.ask_provider(self.build_system(), history, max_tokens, effort)
                if not err2:
                    note = ("(Hinweis: Dino ist automatisch auf das kleinere Modell " + smaller +
                            " umgestiegen, weil das andere zu groß für deinen Speicher war.)\n\n")
                    return note + text2, None
                return text2, err2
        return text, err

    def learn(self, history):
        """Gespräch zu dauerhaftem Wissen verdichten. -> (anzahl_fakten, fehler)"""
        if not history:
            return 0, "Noch kein Gespräch zum Lernen."
        convo = "\n".join(f"{m['role']}: {m['content']}" for m in history[-20:])
        facts_now = "\n".join(f"- {x}" for x in self.memory.get("facts", [])) or "(noch nichts)"
        sys_p = ("Du bist ein Gedächtnis-Helfer. Lies das Gespräch und das bisherige Wissen. "
                 "Gib AUSSCHLIESSLICH eine kurze Liste der wichtigsten DAUERHAFTEN Fakten über "
                 "den Nutzer und sein Business zurück (Vorlieben, Ziele, Stil, Business-Details, "
                 "Entscheidungen). Eine Zeile pro Fakt, beginnend mit '- '. Keine Erklärung, "
                 "keine Wiederholungen, max. 40 Zeilen.")
        user_p = f"BISHERIGES WISSEN:\n{facts_now}\n\nNEUES GESPRÄCH:\n{convo}\n\nAktualisierte Faktenliste:"
        msgs = [{"role": "user", "content": user_p}]
        if self.config["keys"]["claude"]:
            text, err = self.ask_claude(sys_p, msgs, max_tokens=1500, effort="high")
        else:
            text, err = self.ask_provider(sys_p, msgs, max_tokens=1500)
        if err:
            return 0, err
        facts = [ln.strip()[2:].strip() for ln in text.splitlines() if ln.strip().startswith("- ")]
        if facts:
            self.memory["facts"] = facts[:60]
            self.save_memory()
            return len(self.memory["facts"]), None
        return 0, None

    def plan(self):
        user_p = (f"Bau mir einen konkreten, REALISTISCHEN Wochenplan, um meinem Ziel näher zu "
                  f"kommen: {self.config['goal']}. Nutze meine echte Kundenliste oben. "
                  "Gib: 1) ehrliche Einschätzung was diese Woche realistisch drin ist, "
                  "2) Tag-für-Tag Aufgaben (Mo–So), 3) welche meiner Kunden/Leads ich wie "
                  "voranbringe und wie viele neue Kunden ich fürs Ziel noch brauche, "
                  "4) welche Texte/Inhalte du mir sofort schreiben kannst. "
                  "Keine Garantien, keine Abzock-Versprechen — echte Schritte.")
        text, err = self.ask_provider(self.build_system(), [{"role": "user", "content": user_p}],
                                      max_tokens=4096, effort="high")
        if not err:
            self.add_journal("Wochen-Geldplan erstellt.")
        return text, err

    def tagescheckin(self):
        user_p = ("Mach jetzt meinen Tages-Check-in. Schau auf mein Ziel, meine Kunden und dein "
                  "Gedächtnis. Gib mir die 3 wichtigsten, realistischen Aktionen für HEUTE, die "
                  "mich dem Geld-Ziel näher bringen. Kurz, konkret, machbar in ein paar Stunden. "
                  "Danach eine Zeile Motivation in meinem Humor.")
        text, err = self.ask_provider(self.build_system(), [{"role": "user", "content": user_p}],
                                      max_tokens=1200, effort="high")
        if not err:
            self.add_journal("Tages-Check-in gemacht.")
        return text, err

    def rat(self, history, frage):
        """Fragt alle eingerichteten KIs. -> (answers_dict, synthese_oder_None, fehler_oder_None)"""
        sys_p = self.build_system()
        msgs = history + [{"role": "user", "content": frage}]
        brains = []
        if self.config["keys"]["claude"]:
            brains.append(("Claude", lambda: self.ask_claude(sys_p, msgs, 1500, "medium")))
        if self.config["keys"]["openai"] and self.config["openai_model"]:
            brains.append(("ChatGPT", lambda: self.ask_openai(sys_p, msgs, 1500)))
        if self.config["keys"]["gemini"]:
            brains.append(("Gemini", lambda: self.ask_gemini(sys_p, msgs, 1500)))
        if self.config["provider"] == "ollama":
            brains.append(("Dino lokal", lambda: self.ask_ollama(sys_p, msgs, 1500)))
        if not brains:
            return {}, None, "Kein KI-Gehirn eingerichtet (Einstellungen → Schlüssel oder Gratis-Modus)."
        answers = {}
        for name, fn in brains:
            text, err = fn()
            answers[name] = text if text else f"(Fehler: {err})"
        synthese = None
        if len(answers) > 1:
            joined = "\n\n".join(f"### {k}\n{v}" for k, v in answers.items())
            syn_p = ("Hier sind Antworten mehrerer KIs auf dieselbe Frage. Fasse das BESTE aus allen "
                     "zu einer einzigen, klaren Empfehlung zusammen. Sag, worin sie sich einig sind und "
                     "was die stärkste Idee ist. Im Stil des Nutzers.")
            syn_msgs = [{"role": "user", "content": f"FRAGE: {frage}\n\n{joined}\n\n{syn_p}"}]
            if self.config["keys"]["claude"]:
                synthese, _ = self.ask_claude(sys_p, syn_msgs, 1500, "high")
            else:
                synthese, _ = self.ask_provider(sys_p, syn_msgs, 1500)
        return answers, synthese, None

    # ── Agenten-Team: Planer → Spezialisten → Dinos Synthese ───────────
    def _parse_plan(self, text):
        """Liest die Planer-Antwort (Zeilen 'AGENT: x | AUFGABE: y') -> [(key, teilaufgabe)]."""
        chosen, seen = [], set()
        for ln in (text or "").splitlines():
            if "agent:" not in ln.lower():
                continue
            m = re.search(r"agent:\s*([a-zA-Zäöü\-]+)", ln, re.I)
            if not m:
                continue
            key = m.group(1).strip().lower()
            key = _AGENT_ALIASES.get(key, key)
            if key not in AGENTS or key in seen:
                continue
            tm = re.search(r"aufgabe:\s*(.+)$", ln, re.I)
            subtask = (tm.group(1).strip() if tm else "Hilf konkret bei dieser Aufgabe.")
            chosen.append((key, subtask))
            seen.add(key)
            if len(chosen) >= 3:
                break
        return chosen

    def _fallback_agents(self, task):
        """Wenn der Planer nichts Brauchbares liefert: Agenten per Stichworten wählen."""
        t = (task or "").lower()
        picked = []

        def add(k, why):
            if k not in [p[0] for p in picked]:
                picked.append((k, why))
        if any(w in t for w in ("kunde", "akquise", "verkauf", "lead", "anschreib",
                                "kalt", "outreach", "dm", "angebot", "abschluss")):
            add("verkaeufer", "Hol oder aktiviere passende Kunden für diese Aufgabe.")
        if any(w in t for w in ("content", "video", "reel", "post", "hook", "script",
                                "caption", "tiktok", "insta", "clip", "thumbnail")):
            add("content", "Liefer fertige Inhalte/Texte für diese Aufgabe.")
        if any(w in t for w in ("geld", "preis", "umsatz", "einnahm", "5000", "rechn",
                                "kalkul", "paket", "euro", "budget")):
            add("geld", "Rechne den realistischen Geld-Weg für diese Aufgabe.")
        if any(w in t for w in ("idee", "recherche", "markt", "konkurrenz", "zielgrupp", "nische")):
            add("rechercheur", "Liefer Ideen und Marktwinkel für diese Aufgabe.")
        if not picked:
            picked = [("stratege", "Plane den besten Weg."),
                      ("verkaeufer", "Hol/aktiviere Kunden."),
                      ("geld", "Rechne den Weg zum Ziel.")]
        if "stratege" not in [p[0] for p in picked]:
            picked = [("stratege", "Setz Prioritäten und den Weg zum Ziel.")] + picked
        return picked[:3]

    def team(self, task, progress=None):
        """Dinos Agenten-Team bearbeitet eine Aufgabe gemeinsam.
        Ablauf: 1) Planer wählt 2–3 Spezialisten + Teilaufgaben, 2) jeder Spezialist
        liefert seinen Beitrag, 3) Dino fasst alles zu EINEM Plan zusammen.
        -> (steps, final_oder_None, fehler_oder_None).  steps = Liste von dicts."""
        task = (task or "").strip()
        if not task:
            return [], None, "Keine Aufgabe angegeben."

        def tick(msg):
            if progress:
                try:
                    progress(msg)
                except Exception:
                    pass

        base = self.build_system()

        # 1) Planer
        tick("Dino plant, wer im Team ran muss…")
        keys = ", ".join(AGENTS.keys())
        roster = "\n".join(f"  - {k}: {v[1]}" for k, v in AGENTS.items())
        plan_sys = base + (
            "\n\nDU BIST GERADE DER PLANER von Dinos Team. Wähle die 2–3 Spezialisten, die für "
            "die Aufgabe am meisten bringen, und gib jedem eine klare, konkrete Teilaufgabe.\n"
            f"Verfügbare Spezialisten (benutze GENAU diese Schlüssel):\n{roster}\n\n"
            "Antworte AUSSCHLIESSLICH in genau diesem Format — eine Zeile pro Spezialist, "
            "nichts davor, nichts danach:\n"
            f"AGENT: <schluessel aus: {keys}> | AUFGABE: <konkrete teilaufgabe>")
        plan_txt, err = self.ask_provider(
            plan_sys, [{"role": "user", "content": f"AUFGABE: {task}"}], max_tokens=300)
        chosen = self._parse_plan(plan_txt) if (plan_txt and not err) else []
        if not chosen:
            chosen = self._fallback_agents(task)
        chosen = chosen[:2]  # Tempo: 2 Spezialisten reichen für einen klaren Plan

        # 2) Spezialisten arbeiten nacheinander
        steps = []
        for key, subtask in chosen:
            emoji, name, role = AGENTS[key]
            tick(f"{emoji} {name} arbeitet…")
            sys_p = base + (f"\n\nDEINE ROLLE GERADE: {name}. {role}\n"
                            "Antworte kurz, konkret und sofort umsetzbar — keine Theorie, kein Geschwafel.")
            usr = f"Gesamt-Aufgabe vom Boss: {task}\n\nDeine Teilaufgabe: {subtask}"
            out, e2 = self.ask_provider(sys_p, [{"role": "user", "content": usr}], max_tokens=700)
            steps.append({"key": key, "emoji": emoji, "name": name,
                          "task": subtask, "output": out if out else f"(Fehler: {e2})"})

        # 3) Dino fasst zusammen
        tick("Dino fasst den Plan zusammen…")
        joined = "\n\n".join(
            f"### {s['emoji']} {s['name']} (Auftrag: {s['task']})\n{s['output']}" for s in steps)
        syn_sys = base + (
            "\n\nDu bist jetzt wieder DINO, der Chef des Teams. Fasse die Beiträge deiner "
            "Spezialisten zu EINEM klaren Plan zusammen: die wichtigsten konkreten Schritte in "
            "der richtigen Reihenfolge, in deiner Sprache und deinem Humor. Keine Wiederholungen, "
            "kein Geschwafel — sag dem Boss klipp und klar, was er als Nächstes tut.")
        syn_usr = (f"AUFGABE: {task}\n\nBEITRÄGE DEINES TEAMS:\n{joined}\n\n"
                   "Dein zusammengefasster Plan (mit nummerierten nächsten Schritten):")
        final, e3 = self.ask_provider(syn_sys, [{"role": "user", "content": syn_usr}], max_tokens=1300)
        if not e3 and final:
            self.add_journal(f"Team-Auftrag bearbeitet: {task[:120]}")
        return steps, (final if not e3 else None), (e3 if e3 else None)

    # ── PC-Steuerung: Aktionen erkennen & (nach Bestätigung) ausführen ──
    @staticmethod
    def parse_actions(text):
        """Findet '[AKTION] name | wert'-Zeilen in Dinos Antwort.
        -> Liste von dicts {name, arg, label, warn}. (Wird NICHT ausgeführt.)"""
        out = []
        for ln in (text or "").splitlines():
            m = re.search(r"\[?\s*AKTION\s*\]?\s*[:\-]?\s*([a-zA-Z_äöü]+)\s*\|\s*(.*)$", ln, re.I)
            if not m:
                continue
            name = m.group(1).strip().lower()
            arg = m.group(2).strip()
            if name not in ALL_ACTIONS:
                continue
            label, _desc, warn = ALL_ACTIONS[name]
            out.append({"name": name, "arg": arg, "label": label, "warn": bool(warn)})
        return out

    def _safe_path(self, name):
        """Begrenzt Datei-Aktionen sicher auf den Ordner 'Dino-Dateien'.
        Nutzt realpath -> löst auch Symlinks auf, damit man nicht über einen
        Link aus dem Ordner ausbrechen kann."""
        os.makedirs(DINO_FILES_DIR, exist_ok=True)
        base = os.path.realpath(DINO_FILES_DIR)
        target = os.path.realpath(os.path.join(base, (name or "").strip().lstrip("/\\")))
        if target != base and not target.startswith(base + os.sep):
            return None
        return target

    def run_action(self, name, arg):
        """Führt EINE Aktion aus (wird nur nach Klick-Bestätigung aufgerufen).
        -> (ok: bool, ausgabe: str)."""
        name = (name or "").strip().lower()
        arg = (arg or "").strip()
        if name not in ALL_ACTIONS:
            return False, f"Unbekannte Aktion: {name}"
        # Govee-Licht: unabhängig von der PC-Steuerung
        if name in GOVEE_ACTIONS:
            return self._run_govee(name, arg)
        if not self.config.get("pc_control", True):
            return False, "PC-Steuerung ist in den Einstellungen ausgeschaltet."
        try:
            if name == "app_oeffnen":
                return self._act_open_app(arg)
            if name == "web_oeffnen":
                url = arg if re.match(r"^https?://", arg, re.I) else "https://" + arg
                webbrowser.open(url)
                return True, f"Webseite geöffnet: {url}"
            if name == "ordner_oeffnen":
                path = os.path.expanduser(arg or "~")
                if not os.path.isdir(path):
                    return False, f"Ordner gibt es nicht: {path}"
                self._os_open(path)
                return True, f"Ordner geöffnet: {path}"
            if name == "datei_schreiben":
                if ":::" in arg:
                    fname, content = arg.split(":::", 1)
                else:
                    fname, content = arg, ""
                target = self._safe_path(fname.strip())
                if not target:
                    return False, "Ungültiger Dateiname (nur im Ordner 'Dino-Dateien' erlaubt)."
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with open(target, "w", encoding="utf-8") as f:
                    f.write(content.strip("\n"))
                return True, f"Datei gespeichert: {target}"
            if name == "datei_lesen":
                target = self._safe_path(arg)
                if not target or not os.path.isfile(target):
                    return False, "Datei nicht gefunden in 'Dino-Dateien'."
                with open(target, "r", encoding="utf-8", errors="replace") as f:
                    return True, f.read()[:4000]
            if name == "dateien_liste":
                base = self._safe_path(arg or "")
                if not base or not os.path.isdir(base):
                    base = os.path.abspath(DINO_FILES_DIR)
                    os.makedirs(base, exist_ok=True)
                items = sorted(os.listdir(base))
                return True, ("Inhalt von " + base + ":\n" +
                              ("\n".join("- " + i for i in items) if items else "(leer)"))
            if name == "system_info":
                return True, self._system_info()
            if name == "befehl":
                if not arg:
                    return False, "Kein Befehl angegeben."
                proc = subprocess.run(arg, shell=True, capture_output=True, text=True,
                                      timeout=60, cwd=os.path.expanduser("~"))
                out = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
                out = out.strip() or f"(fertig, Code {proc.returncode})"
                return (proc.returncode == 0), out[:4000]
        except subprocess.TimeoutExpired:
            return False, "Befehl hat zu lange gebraucht (über 60s) und wurde gestoppt."
        except Exception as e:
            return False, f"Fehler bei der Aktion: {e}"
        return False, "Aktion nicht umgesetzt."

    def _os_open(self, path):
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys_platform() == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def _act_open_app(self, arg):
        alias = {
            "editor": "notepad", "texteditor": "notepad", "notizen": "notepad",
            "rechner": "calc", "taschenrechner": "calc",
            "explorer": "explorer", "dateien": "explorer", "datei-explorer": "explorer",
            "browser": "__browser__", "internet": "__browser__",
            "paint": "mspaint", "kamera": "microsoft.windows.camera:",
            "einstellungen": "ms-settings:",
        }
        prog = alias.get(arg.lower(), arg)
        if prog == "__browser__":
            webbrowser.open("https://www.google.com")
            return True, "Browser geöffnet."
        try:
            if os.name == "nt":
                os.startfile(prog)  # type: ignore[attr-defined]
            else:
                subprocess.Popen([prog])
            return True, f"Programm gestartet: {prog}"
        except Exception as e:
            return False, f"Konnte '{prog}' nicht starten: {e}"

    def _system_info(self):
        import platform
        lines = [f"Betriebssystem: {platform.system()} {platform.release()}",
                 f"Rechnername: {platform.node()}",
                 f"Prozessor: {platform.processor() or '—'}",
                 f"CPU-Kerne: {os.cpu_count()}"]
        try:
            total, used, free = shutil.disk_usage(os.path.expanduser("~"))
            gb = 1024 ** 3
            lines.append(f"Festplatte: {free // gb} GB frei von {total // gb} GB")
        except Exception:
            pass
        return "\n".join(lines)

    # ── Web-Recherche (Dino schaut im Internet nach -> frisches Wissen) ─
    def web_search(self, query, n=5):
        """Sucht im Web über DuckDuckGo. -> (treffer_liste, fehler)."""
        import urllib.parse
        import html as _html
        query = (query or "").strip()
        if not query:
            return [], "Keine Suchanfrage."
        url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": WEB_UA})
            with urllib.request.urlopen(req, timeout=12) as r:
                page = r.read().decode("utf-8", "replace")
        except Exception as e:
            return [], f"Konnte das Web gerade nicht erreichen ({e})."

        def clean(s):
            return re.sub(r"<.*?>", "", _html.unescape(s or "")).strip()
        links = re.findall(r'result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', page, re.S)
        snips = re.findall(r'result__snippet"[^>]*>(.*?)</a>', page, re.S)
        out = []
        for i, (href, title) in enumerate(links[:n]):
            out.append({"title": clean(title),
                        "snippet": clean(snips[i]) if i < len(snips) else "",
                        "url": href})
        return out, None

    def web_answer(self, query):
        """Sucht im Web und lässt Dino mit den frischen Treffern antworten.
        -> (text, fehler)."""
        results, err = self.web_search(query)
        if not results:
            return None, (err or "Keine Web-Treffer gefunden.")
        ctx = "\n\n".join(f"[{i + 1}] {r['title']}\n{r['snippet']}\n{r['url']}"
                          for i, r in enumerate(results))
        usr = (f"FRAGE: {query}\n\nFRISCHE WEB-TREFFER (gerade aus dem Internet):\n{ctx}\n\n"
               "Beantworte die Frage in deinem Stil mit Hilfe dieser Treffer. Nenn die "
               "wichtigsten Fakten ehrlich und kurz. Wenn die Treffer nichts taugen, sag es offen.")
        text, e2 = self.ask_provider(self.build_system(),
                                     [{"role": "user", "content": usr}], max_tokens=1200)
        if not e2:
            self.add_journal(f"Web-Recherche: {query[:120]}")
        return text, e2

    # ── Govee-Lampen (Licht steuern über die offizielle Govee-API) ─────
    def govee_devices(self):
        """Holt die Govee-Geräte des Nutzers. -> (liste, fehler)."""
        key = self.config.get("govee_key", "").strip()
        if not key:
            return None, ("Kein Govee-Schlüssel. Hol ihn dir in der Govee-App "
                          "(Profil → Einstellungen → »Apply for API Key«) und trag ihn in ⚙ ein.")
        req = urllib.request.Request(GOVEE_BASE + "/user/devices",
                                     headers={"Govee-API-Key": key,
                                              "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return None, _http_msg(e)
        except Exception as e:
            return None, f"Verbindungsfehler zu Govee: {e}"
        return (data.get("data") or []), None

    def _govee_send(self, instance, captype, value):
        """Schickt einen Befehl an ALLE passenden Govee-Geräte. -> (ok, text)."""
        devs, err = self.govee_devices()
        if err:
            return False, err
        if not devs:
            return False, "Keine Govee-Geräte gefunden (in der Govee-App eingerichtet?)."
        key = self.config.get("govee_key", "").strip()
        ok, names, last_err = 0, [], None
        for dv in devs:
            caps = {c.get("instance") for c in (dv.get("capabilities") or [])}
            if caps and instance not in caps:
                continue  # Gerät kann das nicht (z.B. kein Farb-Licht)
            body = {"requestId": str(uuid.uuid4()),
                    "payload": {"sku": dv.get("sku"), "device": dv.get("device"),
                                "capability": {"type": captype, "instance": instance, "value": value}}}
            req = urllib.request.Request(GOVEE_BASE + "/device/control",
                                         data=json.dumps(body).encode("utf-8"), method="POST",
                                         headers={"Govee-API-Key": key, "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=15) as r:
                    rd = json.loads(r.read().decode("utf-8"))
                if rd.get("code") == 200:
                    ok += 1
                    names.append(dv.get("deviceName") or dv.get("sku") or "Lampe")
                else:
                    last_err = rd.get("message") or str(rd)
            except urllib.error.HTTPError as e:
                last_err = _http_msg(e)
            except Exception as e:
                last_err = str(e)
        if ok:
            return True, "Licht gesteuert: " + ", ".join(names)
        return False, last_err or "Govee-Steuerung hat nicht geklappt."

    def _run_govee(self, name, arg):
        a = (arg or "").strip().lower()
        if name == "licht_an":
            return self._govee_send("powerSwitch", "devices.capabilities.on_off", 1)
        if name == "licht_aus":
            return self._govee_send("powerSwitch", "devices.capabilities.on_off", 0)
        if name == "licht_helligkeit":
            m = re.search(r"\d+", a)
            if not m:
                return False, "Sag eine Zahl von 0 bis 100 (z.B. 60)."
            val = max(0, min(100, int(m.group(0))))
            return self._govee_send("brightness", "devices.capabilities.range", val)
        if name == "licht_farbe":
            rgb = self._parse_color(a)
            if not rgb:
                return False, f"Farbe »{arg}« kenn ich nicht. Probier z.B. blau, rot, grün, warm, pink."
            r, g, b = rgb
            return self._govee_send("colorRgb", "devices.capabilities.color_setting",
                                    (r << 16) | (g << 8) | b)
        return False, "Unbekannte Licht-Aktion."

    @staticmethod
    def _parse_color(text):
        t = (text or "").strip().lower()
        if t in GOVEE_COLORS:
            return GOVEE_COLORS[t]
        for nm, rgb in GOVEE_COLORS.items():  # Teiltreffer ("mach blau")
            if nm in t:
                return rgb
        m = re.match(r"^\s*(\d{1,3})[,\s]+(\d{1,3})[,\s]+(\d{1,3})\s*$", t)  # "255,0,0"
        if m:
            return tuple(max(0, min(255, int(x))) for x in m.groups())
        return None


def sys_platform():
    import sys as _sys
    return _sys.platform


def _to_float(x):
    try:
        if isinstance(x, str):
            x = x.replace("€", "").replace(",", ".").strip()
            if not x:
                return 0.0
        return float(x)
    except (ValueError, TypeError):
        return 0.0

import base64 as _b64
DINO_HTML = _b64.b64decode("PCFET0NUWVBFIGh0bWw+CjxodG1sIGxhbmc9ImRlIj4KPGhlYWQ+CjxtZXRhIGNoYXJzZXQ9IlVURi04Ij4KPG1ldGEgbmFtZT0idmlld3BvcnQiIGNvbnRlbnQ9IndpZHRoPWRldmljZS13aWR0aCwgaW5pdGlhbC1zY2FsZT0xLjAiPgo8bWV0YSBuYW1lPSJkaW5vLWNzcmYiIGNvbnRlbnQ9Il9fRElOT19DU1JGX18iPgo8dGl0bGU+8J+mliBEaW5vIEtJPC90aXRsZT4KPHN0eWxlPgovKiA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KICAgRElOTyBLSSDigJQgSmFydmlzL1NjaS1GaSBGcm9udGVuZCAoZWluZSBlaWdlbnN0w6RuZGlnZSBEYXRlaSkKICAgUmVpbmVzIEhUTUwvQ1NTL0pTLCBrZWluZSBleHRlcm5lbiBCaWJsaW90aGVrZW4uCiAgID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PSAqLwoKLyogLS0tLSBEZXNpZ24tVmFyaWFibGVuIC0tLS0gKi8KOnJvb3R7CiAgLS1iZzojMDQwNjBkOyAgICAgICAgICAgIC8qIGZhc3Qgc2Nod2FyeiAqLwogIC0tYmcyOiMwNjBhMTY7CiAgLS1wYW5lbDpyZ2JhKDE0LDIyLDQyLC42Mik7ICAgLyogR2xhc21vcnBoaXNtdXMtUGFuZWwgKi8KICAtLXBhbmVsLXNvbGlkOiMwYTExMjQ7CiAgLS1saW5lOnJnYmEoNTYsMTg5LDI0OCwuMjIpOyAgLyogbGV1Y2h0ZW5kZXIgZMO8bm5lciBSYW5kICovCiAgLS1jeWFuOiMyMmQzZWU7CiAgLS1ibHVlOiMzOGJkZjg7CiAgLS1ibHVlMjojNjBhNWZhOwogIC0tdHh0OiNlOGYxZmY7CiAgLS1tdXQ6IzdjOGRiNTsKICAtLWdyZWVuOiMzNGQzOTk7CiAgLS1yb3NlOiNmYjcxODU7CiAgLS1hbWJlcjojZmJiZjI0OwogIC0tZ2xvdzowIDAgMThweCByZ2JhKDM0LDIxMSwyMzgsLjU1KTsKfQoKKntib3gtc2l6aW5nOmJvcmRlci1ib3h9Cmh0bWwsYm9keXtoZWlnaHQ6MTAwJX0KYm9keXsKICBtYXJnaW46MDsKICBmb250LWZhbWlseToiU2Vnb2UgVUkiLHN5c3RlbS11aSwtYXBwbGUtc3lzdGVtLCJIZWx2ZXRpY2EgTmV1ZSIsQXJpYWwsc2Fucy1zZXJpZjsKICBjb2xvcjp2YXIoLS10eHQpOwogIGJhY2tncm91bmQ6CiAgICByYWRpYWwtZ3JhZGllbnQoMTIwMHB4IDYwMHB4IGF0IDUwJSAtMTAlLCByZ2JhKDM0LDIxMSwyMzgsLjEwKSwgdHJhbnNwYXJlbnQgNjAlKSwKICAgIHJhZGlhbC1ncmFkaWVudCg5MDBweCA1MDBweCBhdCA5MCUgMTEwJSwgcmdiYSg5NiwxNjUsMjUwLC4wOCksIHRyYW5zcGFyZW50IDYwJSksCiAgICB2YXIoLS1iZyk7CiAgb3ZlcmZsb3c6aGlkZGVuOwp9Ci8qIGRlemVudGVzIEdyaWQgaW0gSGludGVyZ3J1bmQgKi8KYm9keTo6YmVmb3JlewogIGNvbnRlbnQ6IiI7cG9zaXRpb246Zml4ZWQ7aW5zZXQ6MDt6LWluZGV4OjA7cG9pbnRlci1ldmVudHM6bm9uZTtvcGFjaXR5Oi4zNTsKICBiYWNrZ3JvdW5kLWltYWdlOgogICAgbGluZWFyLWdyYWRpZW50KHJnYmEoNTYsMTg5LDI0OCwuMDYpIDFweCx0cmFuc3BhcmVudCAxcHgpLAogICAgbGluZWFyLWdyYWRpZW50KDkwZGVnLHJnYmEoNTYsMTg5LDI0OCwuMDYpIDFweCx0cmFuc3BhcmVudCAxcHgpOwogIGJhY2tncm91bmQtc2l6ZTo0NHB4IDQ0cHg7CiAgbWFzay1pbWFnZTpyYWRpYWwtZ3JhZGllbnQoY2lyY2xlIGF0IDUwJSAzMCUsIzAwMCAwJSx0cmFuc3BhcmVudCA4MCUpOwp9CgouYXBwe3Bvc2l0aW9uOnJlbGF0aXZlO3otaW5kZXg6MTtkaXNwbGF5OmZsZXg7ZmxleC1kaXJlY3Rpb246Y29sdW1uO2hlaWdodDoxMDB2aDttYXgtd2lkdGg6MTE4MHB4O21hcmdpbjowIGF1dG87cGFkZGluZzoxNHB4IDE4cHggMTZweH0KCi8qID09PT09PT09PT09PT09PT09IEtvcGZ6ZWlsZSA9PT09PT09PT09PT09PT09PSAqLwouaGVhZGVye2Rpc3BsYXk6ZmxleDthbGlnbi1pdGVtczpjZW50ZXI7Z2FwOjE4cHg7cGFkZGluZzo2cHggNHB4IDEycHh9Ci5icmFuZHtkaXNwbGF5OmZsZXg7YWxpZ24taXRlbXM6Y2VudGVyO2dhcDoxNHB4O21pbi13aWR0aDowfQoud29yZG1hcmt7CiAgZm9udC1zaXplOjI2cHg7Zm9udC13ZWlnaHQ6ODAwO2xldHRlci1zcGFjaW5nOjVweDsKICBiYWNrZ3JvdW5kOmxpbmVhci1ncmFkaWVudCg5MGRlZywjNjdlOGY5LCMzOGJkZjgsIzgxOGNmOCk7CiAgLXdlYmtpdC1iYWNrZ3JvdW5kLWNsaXA6dGV4dDtiYWNrZ3JvdW5kLWNsaXA6dGV4dDtjb2xvcjp0cmFuc3BhcmVudDsKICB0ZXh0LXNoYWRvdzowIDAgMjRweCByZ2JhKDU2LDE4OSwyNDgsLjM1KTsKICBmaWx0ZXI6ZHJvcC1zaGFkb3coMCAwIDEwcHggcmdiYSgzNCwyMTEsMjM4LC40KSk7Cn0KLnRhZ2xpbmV7CiAgZm9udC1zaXplOjExcHg7bGV0dGVyLXNwYWNpbmc6MS41cHg7bWFyZ2luLXRvcDoxcHg7Zm9udC13ZWlnaHQ6NjAwOwogIGJhY2tncm91bmQ6bGluZWFyLWdyYWRpZW50KDkwZGVnLCM2N2U4ZjksIzYwYTVmYSk7CiAgLXdlYmtpdC1iYWNrZ3JvdW5kLWNsaXA6dGV4dDtiYWNrZ3JvdW5kLWNsaXA6dGV4dDtjb2xvcjp0cmFuc3BhcmVudDsKICB0ZXh0LXNoYWRvdzowIDAgMTJweCByZ2JhKDU2LDE4OSwyNDgsLjI1KTtvcGFjaXR5Oi45MjsKfQouc3RhdHVzbGluZXtkaXNwbGF5OmZsZXg7YWxpZ24taXRlbXM6Y2VudGVyO2dhcDo4cHg7Zm9udC1zaXplOjEyLjVweDtjb2xvcjp2YXIoLS1tdXQpO21hcmdpbi10b3A6M3B4O2ZsZXgtd3JhcDp3cmFwfQouZG90e3dpZHRoOjlweDtoZWlnaHQ6OXB4O2JvcmRlci1yYWRpdXM6NTAlO2JhY2tncm91bmQ6dmFyKC0tbXV0KTtib3gtc2hhZG93OjAgMCA4cHggY3VycmVudENvbG9yO3RyYW5zaXRpb246LjNzfQouZG90Lm9re2JhY2tncm91bmQ6dmFyKC0tZ3JlZW4pO2NvbG9yOnZhcigtLWdyZWVuKX0KLmRvdC5iYWR7YmFja2dyb3VuZDp2YXIoLS1yb3NlKTtjb2xvcjp2YXIoLS1yb3NlKX0KLyoga2xlaW5lciBPbGxhbWEtSW5kaWthdG9yIG9iZW4gKi8KLm9sbGFtYS1waWxse2Rpc3BsYXk6aW5saW5lLWZsZXg7YWxpZ24taXRlbXM6Y2VudGVyO2dhcDo2cHg7Zm9udC1zaXplOjExcHg7cGFkZGluZzoycHggOXB4O2JvcmRlci1yYWRpdXM6OTk5cHg7CiAgYm9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtiYWNrZ3JvdW5kOnZhcigtLXBhbmVsKTtiYWNrZHJvcC1maWx0ZXI6Ymx1cig4cHgpO2NvbG9yOnZhcigtLW11dCl9Ci5vbGxhbWEtcGlsbCAub3Bkb3R7d2lkdGg6N3B4O2hlaWdodDo3cHg7Ym9yZGVyLXJhZGl1czo1MCU7YmFja2dyb3VuZDp2YXIoLS1tdXQpO2JveC1zaGFkb3c6MCAwIDdweCBjdXJyZW50Q29sb3I7dHJhbnNpdGlvbjouM3N9Ci5vbGxhbWEtcGlsbC5va3tjb2xvcjojYmZmNGZmO2JvcmRlci1jb2xvcjpyZ2JhKDUyLDIxMSwxNTMsLjUpfQoub2xsYW1hLXBpbGwub2sgLm9wZG90e2JhY2tncm91bmQ6dmFyKC0tZ3JlZW4pO2NvbG9yOnZhcigtLWdyZWVuKX0KLm9sbGFtYS1waWxsLndhcm57Y29sb3I6I2ZmZTliODtib3JkZXItY29sb3I6cmdiYSgyNTEsMTkxLDM2LC41KX0KLm9sbGFtYS1waWxsLndhcm4gLm9wZG90e2JhY2tncm91bmQ6dmFyKC0tYW1iZXIpO2NvbG9yOnZhcigtLWFtYmVyKX0KLm9sbGFtYS1waWxsLmJhZHtjb2xvcjojZmZkOWRmO2JvcmRlci1jb2xvcjpyZ2JhKDI1MSwxMTMsMTMzLC41KX0KLm9sbGFtYS1waWxsLmJhZCAub3Bkb3R7YmFja2dyb3VuZDp2YXIoLS1yb3NlKTtjb2xvcjp2YXIoLS1yb3NlKX0KLmhlYWRlciAuc3BhY2Vye2ZsZXg6MX0KLmljb25idG5ze2Rpc3BsYXk6ZmxleDtnYXA6OHB4fQouaWNvbmJ0bnsKICB3aWR0aDo0MnB4O2hlaWdodDo0MnB4O2JvcmRlci1yYWRpdXM6MTJweDtib3JkZXI6MXB4IHNvbGlkIHZhcigtLWxpbmUpOwogIGJhY2tncm91bmQ6dmFyKC0tcGFuZWwpO2JhY2tkcm9wLWZpbHRlcjpibHVyKDhweCk7CiAgY29sb3I6dmFyKC0tdHh0KTtmb250LXNpemU6MThweDtjdXJzb3I6cG9pbnRlcjtkaXNwbGF5OmdyaWQ7cGxhY2UtaXRlbXM6Y2VudGVyOwogIHRyYW5zaXRpb246LjE4czsKfQouaWNvbmJ0bjpob3Zlcntib3JkZXItY29sb3I6dmFyKC0tY3lhbik7Ym94LXNoYWRvdzp2YXIoLS1nbG93KTt0cmFuc2Zvcm06dHJhbnNsYXRlWSgtMXB4KX0KCi8qID09PT09PT09PT09PT09PT09IENvcmUgLyBPcmIgPT09PT09PT09PT09PT09PT0gKi8KLmNvcmUtd3JhcHtkaXNwbGF5OmZsZXg7anVzdGlmeS1jb250ZW50OmNlbnRlcjthbGlnbi1pdGVtczpjZW50ZXI7aGVpZ2h0OjExOHB4O21hcmdpbjotNHB4IDAgNnB4O3Bvc2l0aW9uOnJlbGF0aXZlfQouY29yZXtwb3NpdGlvbjpyZWxhdGl2ZTt3aWR0aDo5NnB4O2hlaWdodDo5NnB4O2Rpc3BsYXk6Z3JpZDtwbGFjZS1pdGVtczpjZW50ZXJ9Ci5jb3JlIC5yaW5newogIHBvc2l0aW9uOmFic29sdXRlO2JvcmRlci1yYWRpdXM6NTAlO2JvcmRlcjoycHggc29saWQgcmdiYSg1NiwxODksMjQ4LC4zNSk7CiAgYW5pbWF0aW9uOnNwaW4gNnMgbGluZWFyIGluZmluaXRlOwp9Ci5jb3JlIC5yMXtpbnNldDowO2JvcmRlci10b3AtY29sb3I6dmFyKC0tY3lhbik7Ym9yZGVyLXJpZ2h0LWNvbG9yOnRyYW5zcGFyZW50fQouY29yZSAucjJ7aW5zZXQ6MTJweDtib3JkZXItYm90dG9tLWNvbG9yOnZhcigtLWJsdWUyKTtib3JkZXItbGVmdC1jb2xvcjp0cmFuc3BhcmVudDthbmltYXRpb24tZHVyYXRpb246NHM7YW5pbWF0aW9uLWRpcmVjdGlvbjpyZXZlcnNlfQouY29yZSAucjN7aW5zZXQ6MjRweDtib3JkZXItdG9wLWNvbG9yOnZhcigtLWJsdWUpO2JvcmRlci1sZWZ0LWNvbG9yOnRyYW5zcGFyZW50O2FuaW1hdGlvbi1kdXJhdGlvbjo4c30KLmNvcmUgLm51Y2xldXN7CiAgd2lkdGg6MzhweDtoZWlnaHQ6MzhweDtib3JkZXItcmFkaXVzOjUwJTsKICBiYWNrZ3JvdW5kOnJhZGlhbC1ncmFkaWVudChjaXJjbGUgYXQgMzUlIDMwJSwjYmZmNGZmLCMyMmQzZWUgNDUlLCMxZDRlZDggMTAwJSk7CiAgYm94LXNoYWRvdzowIDAgMjZweCA2cHggcmdiYSgzNCwyMTEsMjM4LC42NSksMCAwIDYwcHggMTJweCByZ2JhKDU2LDE4OSwyNDgsLjI1KTsKICBhbmltYXRpb246cHVsc2UgMi42cyBlYXNlLWluLW91dCBpbmZpbml0ZTsKfQpAa2V5ZnJhbWVzIHNwaW57dG97dHJhbnNmb3JtOnJvdGF0ZSgzNjBkZWcpfX0KQGtleWZyYW1lcyBwdWxzZXswJSwxMDAle3RyYW5zZm9ybTpzY2FsZSgxKTtvcGFjaXR5Oi45Mn01MCV7dHJhbnNmb3JtOnNjYWxlKDEuMTYpO29wYWNpdHk6MX19Ci8qIFp1c3TDpG5kZTogbmFjaGRlbmtlbiAoc2NobmVsbGVyKSAvIHNwcmVjaGVuICovCi5jb3JlLnRoaW5raW5nIC5yaW5ne2FuaW1hdGlvbi1kdXJhdGlvbjoxLjRzIWltcG9ydGFudH0KLmNvcmUudGhpbmtpbmcgLnIye2FuaW1hdGlvbi1kdXJhdGlvbjoxcyFpbXBvcnRhbnR9Ci5jb3JlLnRoaW5raW5nIC5udWNsZXVze2FuaW1hdGlvbi1kdXJhdGlvbjouOHN9Ci5jb3JlLnNwZWFraW5nIC5udWNsZXVze2FuaW1hdGlvbjpzcGVhayAuNXMgZWFzZS1pbi1vdXQgaW5maW5pdGV9CkBrZXlmcmFtZXMgc3BlYWt7MCUsMTAwJXt0cmFuc2Zvcm06c2NhbGUoMSl9NTAle3RyYW5zZm9ybTpzY2FsZSgxLjI4KTtib3gtc2hhZG93OjAgMCAzNHB4IDEwcHggcmdiYSgzNCwyMTEsMjM4LC44NSl9fQoKLyogPT09PT09PT09PT09PT09PT0gQ2hhdCA9PT09PT09PT09PT09PT09PSAqLwouY2hhdHsKICBmbGV4OjE7b3ZlcmZsb3cteTphdXRvO3BhZGRpbmc6MTBweCA2cHggNHB4O2Rpc3BsYXk6ZmxleDtmbGV4LWRpcmVjdGlvbjpjb2x1bW47Z2FwOjE0cHg7CiAgc2Nyb2xsYmFyLXdpZHRoOnRoaW47c2Nyb2xsYmFyLWNvbG9yOnJnYmEoNTYsMTg5LDI0OCwuNCkgdHJhbnNwYXJlbnQ7Cn0KLmNoYXQ6Oi13ZWJraXQtc2Nyb2xsYmFye3dpZHRoOjhweH0KLmNoYXQ6Oi13ZWJraXQtc2Nyb2xsYmFyLXRodW1ie2JhY2tncm91bmQ6cmdiYSg1NiwxODksMjQ4LC4zNSk7Ym9yZGVyLXJhZGl1czo4cHh9CgoubXNne2Rpc3BsYXk6ZmxleDtnYXA6MTBweDttYXgtd2lkdGg6ODIlO2FuaW1hdGlvbjpmYWRlaW4gLjM1cyBlYXNlIGJvdGh9CkBrZXlmcmFtZXMgZmFkZWlue2Zyb217b3BhY2l0eTowO3RyYW5zZm9ybTp0cmFuc2xhdGVZKDEwcHgpfXRve29wYWNpdHk6MTt0cmFuc2Zvcm06bm9uZX19Ci5tc2cudXNlcnthbGlnbi1zZWxmOmZsZXgtZW5kO2ZsZXgtZGlyZWN0aW9uOnJvdy1yZXZlcnNlfQouYXZhdGFye2ZsZXg6bm9uZTt3aWR0aDozMHB4O2hlaWdodDozMHB4O2JvcmRlci1yYWRpdXM6OXB4O2Rpc3BsYXk6Z3JpZDtwbGFjZS1pdGVtczpjZW50ZXI7Zm9udC1zaXplOjE1cHg7CiAgYmFja2dyb3VuZDp2YXIoLS1wYW5lbCk7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKX0KLmJ1YmJsZXsKICBwYWRkaW5nOjExcHggMTRweDtib3JkZXItcmFkaXVzOjE0cHg7Zm9udC1zaXplOjE0LjVweDtsaW5lLWhlaWdodDoxLjU7CiAgd2hpdGUtc3BhY2U6cHJlLXdyYXA7d29yZC1icmVhazpicmVhay13b3JkOwp9Ci8qIERpbm86IEdsYXMtQnViYmxlICovCi5tc2cuZGlubyAuYnViYmxlewogIGJhY2tncm91bmQ6dmFyKC0tcGFuZWwpO2JhY2tkcm9wLWZpbHRlcjpibHVyKDEwcHgpOwogIGJvcmRlcjoxcHggc29saWQgdmFyKC0tbGluZSk7Ym9yZGVyLXRvcC1sZWZ0LXJhZGl1czo0cHg7CiAgYm94LXNoYWRvdzowIDRweCAyMnB4IHJnYmEoMCwwLDAsLjM1KTsKfQovKiBOdXR6ZXI6IEFremVudC1CdWJibGUgKi8KLm1zZy51c2VyIC5idWJibGV7CiAgYmFja2dyb3VuZDpsaW5lYXItZ3JhZGllbnQoMTM1ZGVnLHJnYmEoMzQsMjExLDIzOCwuMjIpLHJnYmEoOTYsMTY1LDI1MCwuMjApKTsKICBib3JkZXI6MXB4IHNvbGlkIHJnYmEoMzQsMjExLDIzOCwuNDUpO2JvcmRlci10b3AtcmlnaHQtcmFkaXVzOjRweDsKICBib3gtc2hhZG93OjAgMCAxOHB4IHJnYmEoMzQsMjExLDIzOCwuMTgpOwp9Ci8qIEluZm8gLyBGZWhsZXIgLyBMYWJlbCAvIFN5bnRoZXNlICovCi5tc2cuaW5mbyAuYnViYmxle2JhY2tncm91bmQ6dHJhbnNwYXJlbnQ7Ym9yZGVyOjFweCBkYXNoZWQgcmdiYSgxMjQsMTQxLDE4MSwuNCk7Y29sb3I6dmFyKC0tbXV0KTtmb250LXN0eWxlOml0YWxpYztmb250LXNpemU6MTNweH0KLm1zZy5lcnJvciAuYnViYmxle2JhY2tncm91bmQ6cmdiYSgyNTEsMTEzLDEzMywuMTIpO2JvcmRlcjoxcHggc29saWQgdmFyKC0tcm9zZSk7Y29sb3I6I2ZmZDlkZn0KLm1zZy5lcnJvciAuYXZhdGFye2JvcmRlci1jb2xvcjp2YXIoLS1yb3NlKX0KLmxhYmVse2ZvbnQtc2l6ZToxMXB4O2xldHRlci1zcGFjaW5nOi41cHg7dGV4dC10cmFuc2Zvcm06dXBwZXJjYXNlO2NvbG9yOnZhcigtLWN5YW4pO21hcmdpbi1ib3R0b206M3B4O2ZvbnQtd2VpZ2h0OjcwMDtvcGFjaXR5Oi45fQoubXNnLnN5bnRoIC5idWJibGV7CiAgYmFja2dyb3VuZDpsaW5lYXItZ3JhZGllbnQoMTM1ZGVnLHJnYmEoMzQsMjExLDIzOCwuMTYpLHJnYmEoMTI5LDE0MCwyNDgsLjE0KSk7CiAgYm9yZGVyOjFweCBzb2xpZCB2YXIoLS1jeWFuKTtib3gtc2hhZG93OnZhcigtLWdsb3cpOwp9CgovKiBUaXBwLUluZGlrYXRvciAqLwoudHlwaW5ne2Rpc3BsYXk6ZmxleDtnYXA6NXB4O2FsaWduLWl0ZW1zOmNlbnRlcjtwYWRkaW5nOjEzcHggMTZweH0KLnR5cGluZyBzcGFue3dpZHRoOjhweDtoZWlnaHQ6OHB4O2JvcmRlci1yYWRpdXM6NTAlO2JhY2tncm91bmQ6dmFyKC0tY3lhbik7b3BhY2l0eTouNTthbmltYXRpb246Ym91bmNlIDEuMnMgaW5maW5pdGV9Ci50eXBpbmcgc3BhbjpudGgtY2hpbGQoMil7YW5pbWF0aW9uLWRlbGF5Oi4xOHN9Ci50eXBpbmcgc3BhbjpudGgtY2hpbGQoMyl7YW5pbWF0aW9uLWRlbGF5Oi4zNnN9CkBrZXlmcmFtZXMgYm91bmNlezAlLDYwJSwxMDAle3RyYW5zZm9ybTp0cmFuc2xhdGVZKDApO29wYWNpdHk6LjR9MzAle3RyYW5zZm9ybTp0cmFuc2xhdGVZKC02cHgpO29wYWNpdHk6MX19CgovKiA9PT09PT09PT09PT09PT09PSBEaW5vLVNldHVwLUthcnRlID09PT09PT09PT09PT09PT09ICovCi5zZXR1cC1jYXJkewogIGFsaWduLXNlbGY6c3RyZXRjaDttYXgtd2lkdGg6MTAwJTsKICBib3JkZXI6MXB4IHNvbGlkIHZhcigtLWN5YW4pO2JvcmRlci1yYWRpdXM6MTZweDtwYWRkaW5nOjE4cHggMjBweDsKICBiYWNrZ3JvdW5kOmxpbmVhci1ncmFkaWVudCgxNTBkZWcscmdiYSgzNCwyMTEsMjM4LC4xMCkscmdiYSgxMjksMTQwLDI0OCwuMDgpKTsKICBiYWNrZHJvcC1maWx0ZXI6Ymx1cigxMnB4KTtib3gtc2hhZG93OjAgMCAzMHB4IHJnYmEoMzQsMjExLDIzOCwuMTgpLDAgNnB4IDI4cHggcmdiYSgwLDAsMCwuNCk7CiAgYW5pbWF0aW9uOmZhZGVpbiAuNHMgZWFzZSBib3RoOwp9Ci5zZXR1cC1jYXJkIC5zYy10aXRsZXtmb250LXNpemU6MTdweDtmb250LXdlaWdodDo4MDA7bGV0dGVyLXNwYWNpbmc6LjRweDsKICBiYWNrZ3JvdW5kOmxpbmVhci1ncmFkaWVudCg5MGRlZywjYmZmNGZmLCM2MGE1ZmEpOy13ZWJraXQtYmFja2dyb3VuZC1jbGlwOnRleHQ7YmFja2dyb3VuZC1jbGlwOnRleHQ7Y29sb3I6dHJhbnNwYXJlbnQ7CiAgdGV4dC1zaGFkb3c6MCAwIDE4cHggcmdiYSg1NiwxODksMjQ4LC4zKTttYXJnaW4tYm90dG9tOjZweH0KLnNldHVwLWNhcmQgLnNjLXN1Yntmb250LXNpemU6MTNweDtjb2xvcjp2YXIoLS1tdXQpO2xpbmUtaGVpZ2h0OjEuNjttYXJnaW4tYm90dG9tOjE0cHh9Ci5zZXR1cC1jYXJkIC5zYy1zdGVwe21hcmdpbjoxMnB4IDB9Ci5zZXR1cC1jYXJkIC5zYy1zdGVwLWh7Zm9udC1zaXplOjEzLjVweDtmb250LXdlaWdodDo3MDA7Y29sb3I6dmFyKC0tdHh0KTttYXJnaW4tYm90dG9tOjZweDtkaXNwbGF5OmZsZXg7YWxpZ24taXRlbXM6Y2VudGVyO2dhcDo3cHh9Ci5zZXR1cC1jYXJkIC5zYy1zdGVwLWggLm51bXtmbGV4Om5vbmU7d2lkdGg6MjJweDtoZWlnaHQ6MjJweDtib3JkZXItcmFkaXVzOjUwJTtkaXNwbGF5OmdyaWQ7cGxhY2UtaXRlbXM6Y2VudGVyOwogIGZvbnQtc2l6ZToxMnB4O2JhY2tncm91bmQ6cmdiYSgzNCwyMTEsMjM4LC4xNik7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtjb2xvcjp2YXIoLS1jeWFuKX0KLnNldHVwLWNhcmQgYS5zYy1saW5re2NvbG9yOnZhcigtLWJsdWUyKTt0ZXh0LWRlY29yYXRpb246bm9uZTtib3JkZXItYm90dG9tOjFweCBkb3R0ZWQgcmdiYSg5NiwxNjUsMjUwLC41KX0KLnNldHVwLWNhcmQgYS5zYy1saW5rOmhvdmVye2NvbG9yOiNiZmY0ZmY7Ym9yZGVyLWJvdHRvbS1jb2xvcjp2YXIoLS1jeWFuKX0KLnNldHVwLWNhcmQgLnNjLWNvZGVib3h7ZGlzcGxheTpmbGV4O2FsaWduLWl0ZW1zOmNlbnRlcjtnYXA6OHB4O21hcmdpbi10b3A6NnB4fQouc2V0dXAtY2FyZCAuc2MtY29kZXsKICBmbGV4OjE7Zm9udC1mYW1pbHk6IkNvbnNvbGFzIiwiU0YgTW9ubyIsdWktbW9ub3NwYWNlLG1vbm9zcGFjZTtmb250LXNpemU6MTMuNXB4O2NvbG9yOiNiZmY0ZmY7CiAgYmFja2dyb3VuZDpyZ2JhKDIsOCwyMCwuNyk7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtib3JkZXItcmFkaXVzOjEwcHg7cGFkZGluZzo5cHggMTJweDsKICB3aGl0ZS1zcGFjZTpub3dyYXA7b3ZlcmZsb3cteDphdXRvO2JveC1zaGFkb3c6aW5zZXQgMCAwIDE0cHggcmdiYSgzNCwyMTEsMjM4LC4wOCk7Cn0KLnNldHVwLWNhcmQgLnNjLWNvcHl7ZmxleDpub25lO3BhZGRpbmc6OXB4IDExcHg7Ym9yZGVyLXJhZGl1czoxMHB4O2JvcmRlcjoxcHggc29saWQgdmFyKC0tbGluZSk7CiAgYmFja2dyb3VuZDp2YXIoLS1wYW5lbCk7Y29sb3I6dmFyKC0tdHh0KTtmb250OmluaGVyaXQ7Zm9udC1zaXplOjEzcHg7Y3Vyc29yOnBvaW50ZXI7dHJhbnNpdGlvbjouMTZzfQouc2V0dXAtY2FyZCAuc2MtY29weTpob3Zlcntib3JkZXItY29sb3I6dmFyKC0tY3lhbik7Ym94LXNoYWRvdzp2YXIoLS1nbG93KX0KLnNldHVwLWNhcmQgLnNjLW1vZGVsc3tkaXNwbGF5OmZsZXg7ZmxleC13cmFwOndyYXA7Z2FwOjhweDttYXJnaW4tdG9wOjhweH0KLnNldHVwLWNhcmQgLnNjLW1vZGVse3BhZGRpbmc6NnB4IDEycHg7Ym9yZGVyLXJhZGl1czo5OTlweDtib3JkZXI6MXB4IHNvbGlkIHZhcigtLWxpbmUpOwogIGJhY2tncm91bmQ6dmFyKC0tcGFuZWwpO2NvbG9yOnZhcigtLXR4dCk7Zm9udDppbmhlcml0O2ZvbnQtc2l6ZToxMi41cHg7Y3Vyc29yOnBvaW50ZXI7dHJhbnNpdGlvbjouMTZzfQouc2V0dXAtY2FyZCAuc2MtbW9kZWw6aG92ZXJ7Ym9yZGVyLWNvbG9yOnZhcigtLWN5YW4pO2JveC1zaGFkb3c6dmFyKC0tZ2xvdyk7Y29sb3I6I2JmZjRmZn0KLnNldHVwLWNhcmQgLnNjLWFjdGlvbnN7ZGlzcGxheTpmbGV4O2FsaWduLWl0ZW1zOmNlbnRlcjtnYXA6MTBweDtmbGV4LXdyYXA6d3JhcDttYXJnaW4tdG9wOjE2cHh9Ci5zZXR1cC1jYXJkIC5zYy1yZWNoZWNre3BhZGRpbmc6OXB4IDE2cHg7Ym9yZGVyLXJhZGl1czoxMHB4O2JvcmRlcjpub25lO2N1cnNvcjpwb2ludGVyO2ZvbnQ6aW5oZXJpdDtmb250LXNpemU6MTMuNXB4O2ZvbnQtd2VpZ2h0OjYwMDsKICBiYWNrZ3JvdW5kOmxpbmVhci1ncmFkaWVudCgxMzVkZWcsdmFyKC0tY3lhbiksdmFyKC0tYmx1ZTIpKTtjb2xvcjojMDQxMDFmO2JveC1zaGFkb3c6MCAwIDE4cHggcmdiYSgzNCwyMTEsMjM4LC40KTt0cmFuc2l0aW9uOi4xNnN9Ci5zZXR1cC1jYXJkIC5zYy1yZWNoZWNrOmhvdmVye2ZpbHRlcjpicmlnaHRuZXNzKDEuMSl9Ci5zZXR1cC1jYXJkIC5zYy1yZWNoZWNrOmRpc2FibGVke29wYWNpdHk6LjU1O2N1cnNvcjp3YWl0O2JveC1zaGFkb3c6bm9uZX0KLnNldHVwLWNhcmQgLnNjLXNldHRpbmdze2ZvbnQtc2l6ZToxMi41cHg7Y29sb3I6dmFyKC0tbXV0KTtiYWNrZ3JvdW5kOm5vbmU7Ym9yZGVyOm5vbmU7Y3Vyc29yOnBvaW50ZXI7Zm9udDppbmhlcml0OwogIHRleHQtZGVjb3JhdGlvbjp1bmRlcmxpbmU7dGV4dC1kZWNvcmF0aW9uLXN0eWxlOmRvdHRlZDtwYWRkaW5nOjB9Ci5zZXR1cC1jYXJkIC5zYy1zZXR0aW5nczpob3Zlcntjb2xvcjp2YXIoLS1ibHVlMil9Ci5zZXR1cC1jYXJkIC5zYy1zdGF0ZXtmb250LXNpemU6MTIuNXB4O2NvbG9yOnZhcigtLWN5YW4pO21pbi1oZWlnaHQ6MWVtfQoKLyogPT09PT09PT09PT09PT09PT0gUXVpY2stQ2hpcHMgPT09PT09PT09PT09PT09PT0gKi8KLmNoaXBze2Rpc3BsYXk6ZmxleDtmbGV4LXdyYXA6d3JhcDtnYXA6OHB4O3BhZGRpbmc6MTBweCA0cHggOHB4fQouY2hpcHsKICBwYWRkaW5nOjdweCAxM3B4O2JvcmRlci1yYWRpdXM6OTk5cHg7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTsKICBiYWNrZ3JvdW5kOnZhcigtLXBhbmVsKTtjb2xvcjp2YXIoLS10eHQpO2ZvbnQtc2l6ZToxM3B4O2N1cnNvcjpwb2ludGVyO3RyYW5zaXRpb246LjE2czsKICBiYWNrZHJvcC1maWx0ZXI6Ymx1cig4cHgpOwp9Ci5jaGlwOmhvdmVye2JvcmRlci1jb2xvcjp2YXIoLS1jeWFuKTtib3gtc2hhZG93OnZhcigtLWdsb3cpO2NvbG9yOiNiZmY0ZmZ9Ci5jaGlwOmRpc2FibGVke29wYWNpdHk6LjQ7Y3Vyc29yOm5vdC1hbGxvd2VkO2JveC1zaGFkb3c6bm9uZX0KCi8qID09PT09PT09PT09PT09PT09IEVpbmdhYmVsZWlzdGUgPT09PT09PT09PT09PT09PT0gKi8KLmlucHV0YmFyewogIGRpc3BsYXk6ZmxleDthbGlnbi1pdGVtczpmbGV4LWVuZDtnYXA6OXB4O3BhZGRpbmc6MTBweDtib3JkZXItcmFkaXVzOjE2cHg7CiAgYm9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtiYWNrZ3JvdW5kOnZhcigtLXBhbmVsKTtiYWNrZHJvcC1maWx0ZXI6Ymx1cigxMnB4KTsKICBib3gtc2hhZG93OjAgMCAyNnB4IHJnYmEoMzQsMjExLDIzOCwuMTApOwp9CiNpbnB1dHsKICBmbGV4OjE7cmVzaXplOm5vbmU7bWF4LWhlaWdodDoxNDBweDttaW4taGVpZ2h0OjI0cHg7Ym9yZGVyOm5vbmU7b3V0bGluZTpub25lOwogIGJhY2tncm91bmQ6dHJhbnNwYXJlbnQ7Y29sb3I6dmFyKC0tdHh0KTtmb250OmluaGVyaXQ7Zm9udC1zaXplOjE0LjVweDtsaW5lLWhlaWdodDoxLjQ1OwogIHBhZGRpbmc6NnB4IDRweDsKfQojaW5wdXQ6OnBsYWNlaG9sZGVye2NvbG9yOnZhcigtLW11dCl9Ci5pYnRuewogIGZsZXg6bm9uZTt3aWR0aDo0MnB4O2hlaWdodDo0MnB4O2JvcmRlci1yYWRpdXM6MTFweDtib3JkZXI6MXB4IHNvbGlkIHZhcigtLWxpbmUpOwogIGJhY2tncm91bmQ6cmdiYSgyNTUsMjU1LDI1NSwuMDMpO2NvbG9yOnZhcigtLXR4dCk7Zm9udC1zaXplOjE4cHg7Y3Vyc29yOnBvaW50ZXI7CiAgZGlzcGxheTpncmlkO3BsYWNlLWl0ZW1zOmNlbnRlcjt0cmFuc2l0aW9uOi4xNnM7Cn0KLmlidG46aG92ZXJ7Ym9yZGVyLWNvbG9yOnZhcigtLWN5YW4pO2JveC1zaGFkb3c6dmFyKC0tZ2xvdyl9Ci5pYnRuLmFjdGl2ZXtib3JkZXItY29sb3I6dmFyKC0tY3lhbik7Y29sb3I6dmFyKC0tY3lhbik7YmFja2dyb3VuZDpyZ2JhKDM0LDIxMSwyMzgsLjEyKTtib3gtc2hhZG93OnZhcigtLWdsb3cpfQouaWJ0bi5taWMubGlzdGVuaW5ne2NvbG9yOnZhcigtLXJvc2UpO2JvcmRlci1jb2xvcjp2YXIoLS1yb3NlKTtib3gtc2hhZG93OjAgMCAxNnB4IHJnYmEoMjUxLDExMywxMzMsLjYpO2FuaW1hdGlvbjptaWNwdWxzZSAxcyBpbmZpbml0ZX0KQGtleWZyYW1lcyBtaWNwdWxzZXs1MCV7YmFja2dyb3VuZDpyZ2JhKDI1MSwxMTMsMTMzLC4xOCl9fQouaWJ0bi5zZW5kewogIGJhY2tncm91bmQ6bGluZWFyLWdyYWRpZW50KDEzNWRlZyx2YXIoLS1jeWFuKSx2YXIoLS1ibHVlMikpO2NvbG9yOiMwNDEwMWY7Ym9yZGVyOm5vbmU7CiAgYm94LXNoYWRvdzowIDAgMThweCByZ2JhKDM0LDIxMSwyMzgsLjUpOwp9Ci5pYnRuLnNlbmQ6aG92ZXJ7ZmlsdGVyOmJyaWdodG5lc3MoMS4xKX0KLmlidG46ZGlzYWJsZWR7b3BhY2l0eTouNDtjdXJzb3I6bm90LWFsbG93ZWQ7Ym94LXNoYWRvdzpub25lfQoKLyogPT09PT09PT09PT09PT09PT0gUGFuZWxzIChTbGlkZS1PdmVyKSA9PT09PT09PT09PT09PT09PSAqLwoub3ZlcmxheXtwb3NpdGlvbjpmaXhlZDtpbnNldDowO3otaW5kZXg6NDA7YmFja2dyb3VuZDpyZ2JhKDIsNCwxMCwuNik7YmFja2Ryb3AtZmlsdGVyOmJsdXIoM3B4KTsKICBvcGFjaXR5OjA7cG9pbnRlci1ldmVudHM6bm9uZTt0cmFuc2l0aW9uOi4yNXN9Ci5vdmVybGF5Lm9wZW57b3BhY2l0eToxO3BvaW50ZXItZXZlbnRzOmF1dG99Ci5wYW5lbHsKICBwb3NpdGlvbjpmaXhlZDt0b3A6MDtyaWdodDowO2hlaWdodDoxMDAlO3dpZHRoOm1pbig0NjBweCw5NHZ3KTt6LWluZGV4OjQxOwogIGJhY2tncm91bmQ6bGluZWFyLWdyYWRpZW50KDE4MGRlZyx2YXIoLS1iZzIpLHZhcigtLWJnKSk7CiAgYm9yZGVyLWxlZnQ6MXB4IHNvbGlkIHZhcigtLWxpbmUpO2JveC1zaGFkb3c6LTIwcHggMCA2MHB4IHJnYmEoMCwwLDAsLjU1KTsKICB0cmFuc2Zvcm06dHJhbnNsYXRlWCgxMDAlKTt0cmFuc2l0aW9uOnRyYW5zZm9ybSAuMjhzIGN1YmljLWJlemllciguNCwuMCwuMiwxKTsKICBkaXNwbGF5OmZsZXg7ZmxleC1kaXJlY3Rpb246Y29sdW1uOwp9Ci5wYW5lbC5vcGVue3RyYW5zZm9ybTpub25lfQoucGFuZWwtaGVhZHtkaXNwbGF5OmZsZXg7YWxpZ24taXRlbXM6Y2VudGVyO2dhcDoxMHB4O3BhZGRpbmc6MThweCAyMHB4IDEycHg7Ym9yZGVyLWJvdHRvbToxcHggc29saWQgdmFyKC0tbGluZSl9Ci5wYW5lbC1oZWFkIGgye21hcmdpbjowO2ZvbnQtc2l6ZToxN3B4O2ZvbnQtd2VpZ2h0OjcwMDtsZXR0ZXItc3BhY2luZzouNXB4fQoucGFuZWwtaGVhZCAuY2xvc2V7bWFyZ2luLWxlZnQ6YXV0bzt3aWR0aDozNHB4O2hlaWdodDozNHB4O2JvcmRlci1yYWRpdXM6OXB4O2JvcmRlcjoxcHggc29saWQgdmFyKC0tbGluZSk7CiAgYmFja2dyb3VuZDp0cmFuc3BhcmVudDtjb2xvcjp2YXIoLS10eHQpO2ZvbnQtc2l6ZToxOHB4O2N1cnNvcjpwb2ludGVyfQoucGFuZWwtaGVhZCAuY2xvc2U6aG92ZXJ7Ym9yZGVyLWNvbG9yOnZhcigtLXJvc2UpO2NvbG9yOnZhcigtLXJvc2UpfQoucGFuZWwtYm9keXtmbGV4OjE7b3ZlcmZsb3cteTphdXRvO3BhZGRpbmc6MTZweCAyMHB4IDI4cHg7c2Nyb2xsYmFyLXdpZHRoOnRoaW47c2Nyb2xsYmFyLWNvbG9yOnJnYmEoNTYsMTg5LDI0OCwuNCkgdHJhbnNwYXJlbnR9Ci5wYW5lbC1ib2R5Ojotd2Via2l0LXNjcm9sbGJhcnt3aWR0aDo4cHh9Ci5wYW5lbC1ib2R5Ojotd2Via2l0LXNjcm9sbGJhci10aHVtYntiYWNrZ3JvdW5kOnJnYmEoNTYsMTg5LDI0OCwuMzUpO2JvcmRlci1yYWRpdXM6OHB4fQoKLnNlY3R7Y29sb3I6dmFyKC0tY3lhbik7Zm9udC1zaXplOjEycHg7bGV0dGVyLXNwYWNpbmc6LjZweDt0ZXh0LXRyYW5zZm9ybTp1cHBlcmNhc2U7Zm9udC13ZWlnaHQ6NzAwO21hcmdpbjoxOHB4IDAgOHB4fQouc2VjdDpmaXJzdC1jaGlsZHttYXJnaW4tdG9wOjB9Ci5maWVsZHttYXJnaW4tYm90dG9tOjExcHh9Ci5maWVsZCBsYWJlbHtkaXNwbGF5OmJsb2NrO2ZvbnQtc2l6ZToxMnB4O2NvbG9yOnZhcigtLW11dCk7bWFyZ2luLWJvdHRvbTo0cHh9Ci5maWVsZCBpbnB1dCwuZmllbGQgc2VsZWN0LC5maWVsZCB0ZXh0YXJlYXsKICB3aWR0aDoxMDAlO3BhZGRpbmc6OXB4IDExcHg7Ym9yZGVyLXJhZGl1czo5cHg7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTsKICBiYWNrZ3JvdW5kOnJnYmEoMjU1LDI1NSwyNTUsLjAzKTtjb2xvcjp2YXIoLS10eHQpO2ZvbnQ6aW5oZXJpdDtmb250LXNpemU6MTMuNXB4O291dGxpbmU6bm9uZTsKfQouZmllbGQgaW5wdXQ6Zm9jdXMsLmZpZWxkIHNlbGVjdDpmb2N1cywuZmllbGQgdGV4dGFyZWE6Zm9jdXN7Ym9yZGVyLWNvbG9yOnZhcigtLWN5YW4pO2JveC1zaGFkb3c6MCAwIDAgMnB4IHJnYmEoMzQsMjExLDIzOCwuMTgpfQouZmllbGQgc2VsZWN0IG9wdGlvbntiYWNrZ3JvdW5kOnZhcigtLXBhbmVsLXNvbGlkKX0KLmZpZWxkIHRleHRhcmVhe3Jlc2l6ZTp2ZXJ0aWNhbDttaW4taGVpZ2h0OjU0cHh9Ci5oaW50e2ZvbnQtc2l6ZToxMS41cHg7Y29sb3I6dmFyKC0tbXV0KTtsaW5lLWhlaWdodDoxLjY7bWFyZ2luLXRvcDo2cHh9Ci5oaW50IGNvZGV7Y29sb3I6dmFyKC0tYmx1ZTIpO2JhY2tncm91bmQ6cmdiYSg1NiwxODksMjQ4LC4wOCk7cGFkZGluZzoxcHggNXB4O2JvcmRlci1yYWRpdXM6NXB4fQoKLmJ0bnsKICBwYWRkaW5nOjEwcHggMTZweDtib3JkZXItcmFkaXVzOjEwcHg7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTsKICBiYWNrZ3JvdW5kOnZhcigtLXBhbmVsKTtjb2xvcjp2YXIoLS10eHQpO2ZvbnQ6aW5oZXJpdDtmb250LXNpemU6MTMuNXB4O2ZvbnQtd2VpZ2h0OjYwMDtjdXJzb3I6cG9pbnRlcjt0cmFuc2l0aW9uOi4xNnM7Cn0KLmJ0bjpob3Zlcntib3JkZXItY29sb3I6dmFyKC0tY3lhbik7Ym94LXNoYWRvdzp2YXIoLS1nbG93KX0KLmJ0bi5wcmltYXJ5e2JhY2tncm91bmQ6bGluZWFyLWdyYWRpZW50KDEzNWRlZyx2YXIoLS1jeWFuKSx2YXIoLS1ibHVlMikpO2NvbG9yOiMwNDEwMWY7Ym9yZGVyOm5vbmU7Ym94LXNoYWRvdzowIDAgMThweCByZ2JhKDM0LDIxMSwyMzgsLjQpfQouYnRuLmRhbmdlcntib3JkZXItY29sb3I6cmdiYSgyNTEsMTEzLDEzMywuNSk7Y29sb3I6I2ZmZDlkZn0KLmJ0bi5kYW5nZXI6aG92ZXJ7Ym9yZGVyLWNvbG9yOnZhcigtLXJvc2UpO2JveC1zaGFkb3c6MCAwIDE0cHggcmdiYSgyNTEsMTEzLDEzMywuNCl9Ci5idG4uc217cGFkZGluZzo2cHggMTFweDtmb250LXNpemU6MTJweH0KLmJ0bnJvd3tkaXNwbGF5OmZsZXg7Z2FwOjlweDtmbGV4LXdyYXA6d3JhcDttYXJnaW4tdG9wOjE0cHh9CgovKiBVbXNhdHotQmFubmVyIChLdW5kZW4pICovCi5yZXZlbnVlewogIGJvcmRlcjoxcHggc29saWQgdmFyKC0tbGluZSk7Ym9yZGVyLXJhZGl1czoxM3B4O3BhZGRpbmc6MTRweCAxNnB4O21hcmdpbi1ib3R0b206MTRweDsKICBiYWNrZ3JvdW5kOmxpbmVhci1ncmFkaWVudCgxMzVkZWcscmdiYSg1MiwyMTEsMTUzLC4xMCkscmdiYSgzNCwyMTEsMjM4LC4wNikpOwp9Ci5yZXZlbnVlIC5iaWd7Zm9udC1zaXplOjI0cHg7Zm9udC13ZWlnaHQ6ODAwO2NvbG9yOnZhcigtLWdyZWVuKTt0ZXh0LXNoYWRvdzowIDAgMTZweCByZ2JhKDUyLDIxMSwxNTMsLjM1KX0KLnJldmVudWUgLnN1Yntmb250LXNpemU6MTJweDtjb2xvcjp2YXIoLS1tdXQpO21hcmdpbi10b3A6M3B4fQoKLyogS3VuZGVuLUthcnRlbiAqLwouY3VzdHtib3JkZXI6MXB4IHNvbGlkIHZhcigtLWxpbmUpO2JvcmRlci1yYWRpdXM6MTJweDtwYWRkaW5nOjEycHggMTRweDttYXJnaW4tYm90dG9tOjEwcHg7YmFja2dyb3VuZDp2YXIoLS1wYW5lbCl9Ci5jdXN0IC50b3B7ZGlzcGxheTpmbGV4O2FsaWduLWl0ZW1zOmNlbnRlcjtnYXA6OHB4O2ZsZXgtd3JhcDp3cmFwfQouY3VzdCAubmFtZXtmb250LXdlaWdodDo3MDA7Zm9udC1zaXplOjE0LjVweH0KLmN1c3QgLmJhZGdle2ZvbnQtc2l6ZToxMC41cHg7cGFkZGluZzoycHggOHB4O2JvcmRlci1yYWRpdXM6OTk5cHg7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtjb2xvcjp2YXIoLS1jeWFuKX0KLmN1c3QgLm1ldGF7Zm9udC1zaXplOjEyLjVweDtjb2xvcjp2YXIoLS1tdXQpO21hcmdpbi10b3A6NHB4O2xpbmUtaGVpZ2h0OjEuNX0KLmN1c3QgLnByaWNle2NvbG9yOnZhcigtLWdyZWVuKTtmb250LXdlaWdodDo2MDB9Ci5jdXN0IC5hY3Rpb25ze2Rpc3BsYXk6ZmxleDtnYXA6N3B4O21hcmdpbi10b3A6OXB4fQoKLyogR2Vkw6RjaHRuaXMgKi8KLmZhY3RsaXN0e2xpc3Qtc3R5bGU6bm9uZTttYXJnaW46MDtwYWRkaW5nOjB9Ci5mYWN0bGlzdCBsaXtwYWRkaW5nOjhweCAxMXB4O2JvcmRlcjoxcHggc29saWQgdmFyKC0tbGluZSk7Ym9yZGVyLXJhZGl1czo5cHg7bWFyZ2luLWJvdHRvbTo3cHg7Zm9udC1zaXplOjEzLjVweDtiYWNrZ3JvdW5kOnZhcigtLXBhbmVsKX0KLmZhY3RsaXN0IGxpOjpiZWZvcmV7Y29udGVudDoi4oCiICI7Y29sb3I6dmFyKC0tY3lhbil9Ci5qb3VybmFse2ZvbnQtc2l6ZToxMi41cHg7Y29sb3I6dmFyKC0tbXV0KTtsaW5lLWhlaWdodDoxLjd9Ci5qb3VybmFsIC5ke2NvbG9yOnZhcigtLWJsdWUyKX0KLmVtcHR5e2NvbG9yOnZhcigtLW11dCk7Zm9udC1zdHlsZTppdGFsaWM7Zm9udC1zaXplOjEzcHg7cGFkZGluZzo2cHggMH0KCkBtZWRpYShtYXgtd2lkdGg6NTYwcHgpewogIC53b3JkbWFya3tmb250LXNpemU6MjJweDtsZXR0ZXItc3BhY2luZzozcHh9CiAgLm1zZ3ttYXgtd2lkdGg6OTIlfQogIC5jb3JlLXdyYXB7aGVpZ2h0Ojk2cHh9CiAgLmNvcmV7d2lkdGg6NzhweDtoZWlnaHQ6NzhweH0KfQo8L3N0eWxlPgo8L2hlYWQ+Cjxib2R5Pgo8ZGl2IGNsYXNzPSJhcHAiPgoKICA8IS0tIEtvcGZ6ZWlsZSAtLT4KICA8ZGl2IGNsYXNzPSJoZWFkZXIiPgogICAgPGRpdiBjbGFzcz0iYnJhbmQiPgogICAgICA8ZGl2PgogICAgICAgIDxkaXYgY2xhc3M9IndvcmRtYXJrIj5ESU5PPC9kaXY+CiAgICAgICAgPGRpdiBjbGFzcz0idGFnbGluZSI+ZGVpbiBlaWdlbmVyIEphcnZpcyDCtyBsw6R1ZnQgbG9rYWw8L2Rpdj4KICAgICAgICA8ZGl2IGNsYXNzPSJzdGF0dXNsaW5lIj4KICAgICAgICAgIDxzcGFuIGlkPSJzdGF0dXNEb3QiIGNsYXNzPSJkb3QiPjwvc3Bhbj4KICAgICAgICAgIDxzcGFuIGlkPSJicmFpblRleHQiPnZlcmJpbmRl4oCmPC9zcGFuPgogICAgICAgICAgPHNwYW4gaWQ9Im9sbGFtYVBpbGwiIGNsYXNzPSJvbGxhbWEtcGlsbCIgc3R5bGU9ImRpc3BsYXk6bm9uZSI+PHNwYW4gY2xhc3M9Im9wZG90Ij48L3NwYW4+PHNwYW4gaWQ9Im9sbGFtYVBpbGxUZXh0Ij5sb2thbDwvc3Bhbj48L3NwYW4+CiAgICAgICAgPC9kaXY+CiAgICAgIDwvZGl2PgogICAgPC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJzcGFjZXIiPjwvZGl2PgogICAgPGRpdiBjbGFzcz0iaWNvbmJ0bnMiPgogICAgICA8YnV0dG9uIGNsYXNzPSJpY29uYnRuIiB0aXRsZT0iUEMtU3RldWVydW5nIiBvbmNsaWNrPSJvcGVuUGFuZWwoJ3BjJykiPvCflqXvuI88L2J1dHRvbj4KICAgICAgPGJ1dHRvbiBjbGFzcz0iaWNvbmJ0biIgdGl0bGU9Ikt1bmRlbiIgb25jbGljaz0ib3BlblBhbmVsKCdjdXN0b21lcnMnKSI+8J+RpTwvYnV0dG9uPgogICAgICA8YnV0dG9uIGNsYXNzPSJpY29uYnRuIiB0aXRsZT0iR2Vkw6RjaHRuaXMiIG9uY2xpY2s9Im9wZW5QYW5lbCgnbWVtb3J5JykiPvCfp6A8L2J1dHRvbj4KICAgICAgPGJ1dHRvbiBjbGFzcz0iaWNvbmJ0biIgdGl0bGU9IkVpbnN0ZWxsdW5nZW4iIG9uY2xpY2s9Im9wZW5QYW5lbCgnc2V0dGluZ3MnKSI+4pqZPC9idXR0b24+CiAgICA8L2Rpdj4KICA8L2Rpdj4KCiAgPCEtLSBDb3JlIC8gT3JiIC0tPgogIDxkaXYgY2xhc3M9ImNvcmUtd3JhcCI+CiAgICA8ZGl2IGNsYXNzPSJjb3JlIiBpZD0iY29yZSI+CiAgICAgIDxkaXYgY2xhc3M9InJpbmcgcjEiPjwvZGl2PgogICAgICA8ZGl2IGNsYXNzPSJyaW5nIHIyIj48L2Rpdj4KICAgICAgPGRpdiBjbGFzcz0icmluZyByMyI+PC9kaXY+CiAgICAgIDxkaXYgY2xhc3M9Im51Y2xldXMiPjwvZGl2PgogICAgPC9kaXY+CiAgPC9kaXY+CgogIDwhLS0gQ2hhdCAtLT4KICA8ZGl2IGNsYXNzPSJjaGF0IiBpZD0iY2hhdCI+PC9kaXY+CgogIDwhLS0gUXVpY2stQ2hpcHMgLS0+CiAgPGRpdiBjbGFzcz0iY2hpcHMiPgogICAgPGJ1dHRvbiBjbGFzcz0iY2hpcCIgb25jbGljaz0icXVpY2tQbGFuKCkiPvCfk4UgV29jaGVucGxhbjwvYnV0dG9uPgogICAgPGJ1dHRvbiBjbGFzcz0iY2hpcCIgb25jbGljaz0icXVpY2tUb2RheSgpIj7imIDvuI8gSGV1dGU8L2J1dHRvbj4KICAgIDxidXR0b24gY2xhc3M9ImNoaXAiIG9uY2xpY2s9InF1aWNrVGVhbSgpIj7wn6SWIFRlYW0tQXVmdHJhZzwvYnV0dG9uPgogICAgPGJ1dHRvbiBjbGFzcz0iY2hpcCIgb25jbGljaz0icXVpY2tXZWIoKSI+8J+UjiBXZWItUmVjaGVyY2hlPC9idXR0b24+CiAgICA8YnV0dG9uIGNsYXNzPSJjaGlwIiBvbmNsaWNrPSJxdWlja0xlYXJuKCkiPvCfp6AgTGVybmVuPC9idXR0b24+CiAgICA8YnV0dG9uIGNsYXNzPSJjaGlwIiBvbmNsaWNrPSJxdWlja0NvdW5jaWwoKSI+8J+noPCfp6Dwn6egIFJhdCBkZXIgS0lzPC9idXR0b24+CiAgPC9kaXY+CgogIDwhLS0gRWluZ2FiZWxlaXN0ZSAtLT4KICA8ZGl2IGNsYXNzPSJpbnB1dGJhciI+CiAgICA8dGV4dGFyZWEgaWQ9ImlucHV0IiByb3dzPSIxIiBwbGFjZWhvbGRlcj0iU2NocmVpYiBEaW5vIHdhc+KApiAoRW50ZXIgc2VuZGVuIMK3IFNoaWZ0K0VudGVyIG5ldWUgWmVpbGUpIj48L3RleHRhcmVhPgogICAgPGJ1dHRvbiBjbGFzcz0iaWJ0biBtaWMiIGlkPSJtaWNCdG4iIHRpdGxlPSJTcHJlY2hlbiAoZWlubWFsKSIgb25jbGljaz0idG9nZ2xlTWljKCkiPvCfjqQ8L2J1dHRvbj4KICAgIDxidXR0b24gY2xhc3M9ImlidG4gbWljIiBpZD0iaGZCdG4iIHRpdGxlPSJGcmVpc3ByZWNoLU1vZHVzOiBEYXVlci1NaWtybyArIMK7SGV5IERpbm/CqyIgb25jbGljaz0idG9nZ2xlSGFuZHNGcmVlKCkiPvCfjqc8L2J1dHRvbj4KICAgIDxidXR0b24gY2xhc3M9ImlidG4iIGlkPSJ2b2ljZUJ0biIgdGl0bGU9IlNwcmFjaGF1c2dhYmUgYW4vYXVzIiBvbmNsaWNrPSJ0b2dnbGVWb2ljZSgpIj7wn5SKPC9idXR0b24+CiAgICA8c2VsZWN0IGlkPSJ2b2ljZVNlbGVjdCIgdGl0bGU9IlN0aW1tZSB3w6RobGVuIOKAlCBTdGFuZGFyZDogYXV0b21hdGlzY2ggZGllIGJlc3RlLCBmbMO8c3NpZ2UgZGV1dHNjaGUgU3RpbW1lIiBvbmNoYW5nZT0ib25Wb2ljZVNlbGVjdCgpIiBzdHlsZT0ibWF4LXdpZHRoOjE2MHB4O2JhY2tncm91bmQ6IzBiMTUyNjtjb2xvcjojYmZlOWY1O2JvcmRlcjoxcHggc29saWQgcmdiYSgxMjAsMjAwLDIzMCwuMjgpO2JvcmRlci1yYWRpdXM6OXB4O2ZvbnQtc2l6ZToxMXB4O3BhZGRpbmc6NXB4IDZweDtvdXRsaW5lOm5vbmU7Ij48L3NlbGVjdD4KICAgIDxidXR0b24gY2xhc3M9ImlidG4gc2VuZCIgaWQ9InNlbmRCdG4iIHRpdGxlPSJTZW5kZW4iIG9uY2xpY2s9InNlbmQoKSI+4p6kPC9idXR0b24+CiAgPC9kaXY+CjwvZGl2PgoKPCEtLSA9PT09PT09PT09PT09PT09PT09PT0gUGFuZWxzID09PT09PT09PT09PT09PT09PT09PSAtLT4KPGRpdiBjbGFzcz0ib3ZlcmxheSIgaWQ9Im92ZXJsYXkiIG9uY2xpY2s9ImNsb3NlUGFuZWxzKCkiPjwvZGl2PgoKPCEtLSBFaW5zdGVsbHVuZ2VuIC0tPgo8YXNpZGUgY2xhc3M9InBhbmVsIiBpZD0icGFuZWwtc2V0dGluZ3MiPgogIDxkaXYgY2xhc3M9InBhbmVsLWhlYWQiPjxzcGFuPuKamTwvc3Bhbj48aDI+RWluc3RlbGx1bmdlbjwvaDI+PGJ1dHRvbiBjbGFzcz0iY2xvc2UiIG9uY2xpY2s9ImNsb3NlUGFuZWxzKCkiPuKclTwvYnV0dG9uPjwvZGl2PgogIDxkaXYgY2xhc3M9InBhbmVsLWJvZHkiIGlkPSJzZXR0aW5nc0JvZHkiPjxkaXYgY2xhc3M9ImVtcHR5Ij5sw6RkdOKApjwvZGl2PjwvZGl2Pgo8L2FzaWRlPgoKPCEtLSBLdW5kZW4gLS0+Cjxhc2lkZSBjbGFzcz0icGFuZWwiIGlkPSJwYW5lbC1jdXN0b21lcnMiPgogIDxkaXYgY2xhc3M9InBhbmVsLWhlYWQiPjxzcGFuPvCfkaU8L3NwYW4+PGgyPkt1bmRlbjwvaDI+PGJ1dHRvbiBjbGFzcz0iY2xvc2UiIG9uY2xpY2s9ImNsb3NlUGFuZWxzKCkiPuKclTwvYnV0dG9uPjwvZGl2PgogIDxkaXYgY2xhc3M9InBhbmVsLWJvZHkiIGlkPSJjdXN0b21lcnNCb2R5Ij48ZGl2IGNsYXNzPSJlbXB0eSI+bMOkZHTigKY8L2Rpdj48L2Rpdj4KPC9hc2lkZT4KCjwhLS0gR2Vkw6RjaHRuaXMgLS0+Cjxhc2lkZSBjbGFzcz0icGFuZWwiIGlkPSJwYW5lbC1tZW1vcnkiPgogIDxkaXYgY2xhc3M9InBhbmVsLWhlYWQiPjxzcGFuPvCfp6A8L3NwYW4+PGgyPkdlZMOkY2h0bmlzPC9oMj48YnV0dG9uIGNsYXNzPSJjbG9zZSIgb25jbGljaz0iY2xvc2VQYW5lbHMoKSI+4pyVPC9idXR0b24+PC9kaXY+CiAgPGRpdiBjbGFzcz0icGFuZWwtYm9keSIgaWQ9Im1lbW9yeUJvZHkiPjxkaXYgY2xhc3M9ImVtcHR5Ij5sw6RkdOKApjwvZGl2PjwvZGl2Pgo8L2FzaWRlPgoKPCEtLSBQQy1TdGV1ZXJ1bmcgLS0+Cjxhc2lkZSBjbGFzcz0icGFuZWwiIGlkPSJwYW5lbC1wYyI+CiAgPGRpdiBjbGFzcz0icGFuZWwtaGVhZCI+PHNwYW4+8J+Wpe+4jzwvc3Bhbj48aDI+UEMtU3RldWVydW5nPC9oMj48YnV0dG9uIGNsYXNzPSJjbG9zZSIgb25jbGljaz0iY2xvc2VQYW5lbHMoKSI+4pyVPC9idXR0b24+PC9kaXY+CiAgPGRpdiBjbGFzcz0icGFuZWwtYm9keSIgaWQ9InBjQm9keSI+PGRpdiBjbGFzcz0iZW1wdHkiPmzDpGR04oCmPC9kaXY+PC9kaXY+CjwvYXNpZGU+Cgo8c2NyaXB0PgoidXNlIHN0cmljdCI7Ci8qID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQogICBESU5PIEtJIOKAlCBGcm9udGVuZC1Mb2dpawogICBTcHJpY2h0IHBlciBmZXRjaCgpIG1pdCBkZW0gbG9rYWxlbiBTZXJ2ZXIgKGdsZWljaGVyIE9yaWdpbikuCiAgID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PSAqLwoKLy8gLS0tLSBadXN0YW5kIC0tLS0KY29uc3Qgc3RhdGUgPSB7CiAgbWVzc2FnZXM6IFtdLCAgICAgICAgICAvLyBDaGF0LUhpc3RvcmllIHtyb2xlLCBjb250ZW50fQogIHJlYWR5OiBmYWxzZSwKICBhc3Npc3RhbnROYW1lOiAiRGlubyIsCiAgdXNlck5hbWU6ICJCb3NzIiwKICBidXN5OiBmYWxzZSwKICB2b2ljZU9uOiBmYWxzZSwgICAgICAgIC8vIFNwcmFjaGF1c2dhYmUgYW4vYXVzCiAgc3RhdHVzVmFsdWVzOiBbIkxlYWQiLCJBbmdlYm90IiwiQWt0aXYiLCJCZXphaGx0IiwiUGF1c2llcnQiLCJCZWVuZGV0Il0sCiAgcHJvdmlkZXI6IG51bGwsICAgICAgICAvLyAib2xsYW1hIiB8ICJjbGF1ZGUiIHwgIm9wZW5haSIgfCAiZ2VtaW5pIgogIGF1dG9SZWNoZWNrRG9uZTogZmFsc2UsLy8gZWlubWFsaWdlcyBBdXRvLVJlY2hlY2sgYmVpbSBlcnN0ZW4gTGFkZW4KICBwY0NvbnRyb2w6IHRydWUsICAgICAgIC8vIGRhcmYgRGlubyBQQy1Ba3Rpb25lbiB2b3JzY2hsYWdlbj8KICBnb3ZlZUNoZWNrZWQ6IGZhbHNlLCAgIC8vIEdvdmVlLVZlcmJpbmR1bmcgYmVpbSBTdGFydCBzY2hvbiBnZXByw7xmdD8KfTsKCi8vIC0tLS0gRE9NLUt1cnpoZWxmZXIgLS0tLQpjb25zdCAkID0gKGlkKSA9PiBkb2N1bWVudC5nZXRFbGVtZW50QnlJZChpZCk7CmNvbnN0IGNoYXRFbCA9ICQoImNoYXQiKTsKY29uc3QgY29yZUVsID0gJCgiY29yZSIpOwpjb25zdCBpbnB1dEVsID0gJCgiaW5wdXQiKTsKCi8vIC0tLS0gSGlsZnNmdW5rdGlvbmVuIC0tLS0KZnVuY3Rpb24gZXVybyh4KXsKICBjb25zdCBuID0gTnVtYmVyKHgpIHx8IDA7CiAgcmV0dXJuIG4udG9Mb2NhbGVTdHJpbmcoImRlLURFIix7bWF4aW11bUZyYWN0aW9uRGlnaXRzOjB9KSArICIg4oKsIjsKfQpmdW5jdGlvbiBlc2Mocyl7IC8vIHdpciBudXR6ZW4gb2huZWhpbiB0ZXh0Q29udGVudCwgZGllcyBudXIgZsO8ciBzaWNoZXJlIEF0dHJpYnV0LWZyZWllIEFuemVpZ2UKICByZXR1cm4gU3RyaW5nKHMgPT0gbnVsbCA/ICIiIDogcyk7Cn0KCi8vIC0tLS0gQ29yZS1BbmltYXRpb25lbiAtLS0tCmZ1bmN0aW9uIHNldFRoaW5raW5nKG9uKXsgY29yZUVsLmNsYXNzTGlzdC50b2dnbGUoInRoaW5raW5nIiwgb24pOyB9CmZ1bmN0aW9uIHNldFNwZWFraW5nKG9uKXsgY29yZUVsLmNsYXNzTGlzdC50b2dnbGUoInNwZWFraW5nIiwgb24pOyB9CgovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KLy8gIENoYXQtQW56ZWlnZQovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KLyoqCiAqIEbDvGd0IGVpbmUgQnViYmxlIGhpbnp1LiBJbmhhbHQgd2lyZCB2aWEgdGV4dENvbnRlbnQgZ2VzZXR6dCAoa2VpbiBYU1MpLgogKiBraW5kOiAiZGlubyIgfCAidXNlciIgfCAiaW5mbyIgfCAiZXJyb3IiIHwgInN5bnRoIiB8ICJjb3VuY2lsIgogKiBsYWJlbDogb3B0aW9uYWxlcyBMYWJlbCAoei5CLiBLSS1OYW1lKQogKi8KZnVuY3Rpb24gYWRkQnViYmxlKGtpbmQsIHRleHQsIGxhYmVsKXsKICBjb25zdCB3cmFwID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7CiAgY29uc3QgY2xzID0gKGtpbmQgPT09ICJzeW50aCIgfHwga2luZCA9PT0gImNvdW5jaWwiKSA/ICJkaW5vIiA6IGtpbmQ7CiAgd3JhcC5jbGFzc05hbWUgPSAibXNnICIgKyAoa2luZCA9PT0gInN5bnRoIiA/ICJkaW5vIHN5bnRoIiA6IGNscyk7CgogIC8vIEF2YXRhciBudXIgZsO8ciBEaW5vLS9OdXR6ZXItL0ZlaGxlci1CdWJibGVzCiAgaWYgKGtpbmQgPT09ICJkaW5vIiB8fCBraW5kID09PSAic3ludGgiIHx8IGtpbmQgPT09ICJjb3VuY2lsIil7CiAgICBjb25zdCBhID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IGEuY2xhc3NOYW1lPSJhdmF0YXIiOyBhLnRleHRDb250ZW50PSLwn6aWIjsgd3JhcC5hcHBlbmRDaGlsZChhKTsKICB9IGVsc2UgaWYgKGtpbmQgPT09ICJ1c2VyIil7CiAgICBjb25zdCBhID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IGEuY2xhc3NOYW1lPSJhdmF0YXIiOyBhLnRleHRDb250ZW50PSLwn6eRIjsgd3JhcC5hcHBlbmRDaGlsZChhKTsKICB9IGVsc2UgaWYgKGtpbmQgPT09ICJlcnJvciIpewogICAgY29uc3QgYSA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBhLmNsYXNzTmFtZT0iYXZhdGFyIjsgYS50ZXh0Q29udGVudD0i4pqg77iPIjsgd3JhcC5hcHBlbmRDaGlsZChhKTsKICB9CgogIGNvbnN0IGIgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgYi5jbGFzc05hbWU9ImJ1YmJsZSI7CiAgaWYgKGxhYmVsKXsKICAgIGNvbnN0IGwgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgbC5jbGFzc05hbWU9ImxhYmVsIjsgbC50ZXh0Q29udGVudCA9IGxhYmVsOwogICAgYi5hcHBlbmRDaGlsZChsKTsKICAgIGNvbnN0IHQgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgdC50ZXh0Q29udGVudCA9IHRleHQ7IGIuYXBwZW5kQ2hpbGQodCk7CiAgfSBlbHNlIHsKICAgIGIudGV4dENvbnRlbnQgPSB0ZXh0OwogIH0KICB3cmFwLmFwcGVuZENoaWxkKGIpOwogIGNoYXRFbC5hcHBlbmRDaGlsZCh3cmFwKTsKICBzY3JvbGxEb3duKCk7CiAgcmV0dXJuIHdyYXA7Cn0KCmZ1bmN0aW9uIHNjcm9sbERvd24oKXsgcmVxdWVzdEFuaW1hdGlvbkZyYW1lKCgpPT57IGNoYXRFbC5zY3JvbGxUb3AgPSBjaGF0RWwuc2Nyb2xsSGVpZ2h0OyB9KTsgfQoKLy8gVGlwcC1JbmRpa2F0b3IKbGV0IHR5cGluZ0VsID0gbnVsbDsKZnVuY3Rpb24gc2hvd1R5cGluZygpewogIGlmICh0eXBpbmdFbCkgcmV0dXJuOwogIHR5cGluZ0VsID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7CiAgdHlwaW5nRWwuY2xhc3NOYW1lID0gIm1zZyBkaW5vIjsKICB0eXBpbmdFbC5pbm5lckhUTUwgPSAnPGRpdiBjbGFzcz0iYXZhdGFyIj7wn6aWPC9kaXY+PGRpdiBjbGFzcz0iYnViYmxlIj48ZGl2IGNsYXNzPSJ0eXBpbmciPjxzcGFuPjwvc3Bhbj48c3Bhbj48L3NwYW4+PHNwYW4+PC9zcGFuPjwvZGl2PjwvZGl2Pic7CiAgY2hhdEVsLmFwcGVuZENoaWxkKHR5cGluZ0VsKTsKICBzY3JvbGxEb3duKCk7Cn0KZnVuY3Rpb24gaGlkZVR5cGluZygpeyBpZiAodHlwaW5nRWwpeyB0eXBpbmdFbC5yZW1vdmUoKTsgdHlwaW5nRWwgPSBudWxsOyB9IH0KCi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQovLyAgTmV0endlcmsKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09CmNvbnN0IERJTk9fQ1NSRiA9IChkb2N1bWVudC5xdWVyeVNlbGVjdG9yKCdtZXRhW25hbWU9ImRpbm8tY3NyZiJdJykgfHwge30pLmNvbnRlbnQgfHwgIiI7CmFzeW5jIGZ1bmN0aW9uIGFwaShwYXRoLCBtZXRob2QsIGJvZHkpewogIGNvbnN0IG9wdCA9IHsgbWV0aG9kOiBtZXRob2QgfHwgIkdFVCIsIGhlYWRlcnM6eyAiWC1EaW5vLVRva2VuIjogRElOT19DU1JGIH0gfTsKICBpZiAoYm9keSAhPT0gdW5kZWZpbmVkKXsgb3B0LmhlYWRlcnNbIkNvbnRlbnQtVHlwZSJdPSJhcHBsaWNhdGlvbi9qc29uIjsgb3B0LmJvZHkgPSBKU09OLnN0cmluZ2lmeShib2R5KTsgfQogIGNvbnN0IHJlcyA9IGF3YWl0IGZldGNoKHBhdGgsIG9wdCk7CiAgLy8gVmVyc3VjaGUgSlNPTiB6dSBsZXNlbiDigJMgYXVjaCBiZWkgNHh4LzV4eCBrYW5uIGVpbiB7ZXJyb3J9IGtvbW1lbgogIGxldCBkYXRhOwogIHRyeSB7IGRhdGEgPSBhd2FpdCByZXMuanNvbigpOyB9CiAgY2F0Y2goZSl7IHRocm93IG5ldyBFcnJvcigiVW5nw7xsdGlnZSBBbnR3b3J0IHZvbSBTZXJ2ZXIgKGtlaW4gSlNPTikuIik7IH0KICByZXR1cm4gZGF0YTsKfQoKLy8gQnVzeS1adXN0YW5kIChzcGVycnQgU2VuZGVuICsgQ2hpcHMgd8OkaHJlbmQgZWluZXIgQW5mcmFnZSkKZnVuY3Rpb24gc2V0QnVzeShvbil7CiAgc3RhdGUuYnVzeSA9IG9uOwogIHNldFRoaW5raW5nKG9uKTsKICAkKCJzZW5kQnRuIikuZGlzYWJsZWQgPSBvbjsKICBkb2N1bWVudC5xdWVyeVNlbGVjdG9yQWxsKCIuY2hpcCIpLmZvckVhY2goYyA9PiBjLmRpc2FibGVkID0gb24pOwogIGlmIChvbikgc2hvd1R5cGluZygpOyBlbHNlIGhpZGVUeXBpbmcoKTsKfQoKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09Ci8vICBTdGFydDogU3RhdHVzIGxhZGVuCi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQphc3luYyBmdW5jdGlvbiBsb2FkU3RhdHVzKCl7CiAgdHJ5ewogICAgY29uc3QgcyA9IGF3YWl0IGFwaSgiL2FwaS9zdGF0dXMiKTsKICAgIGlmIChzLmVycm9yKXsgbWFya1N0YXR1cyhmYWxzZSwgIkZlaGxlcjogIitzLmVycm9yKTsgcmV0dXJuOyB9CiAgICBzdGF0ZS5yZWFkeSA9ICEhcy5yZWFkeTsKICAgIHN0YXRlLmFzc2lzdGFudE5hbWUgPSBzLmFzc2lzdGFudF9uYW1lIHx8ICJEaW5vIjsKICAgIHN0YXRlLnVzZXJOYW1lID0gcy51c2VyX25hbWUgfHwgIkJvc3MiOwogICAgc3RhdGUucHJvdmlkZXIgPSBzLnByb3ZpZGVyIHx8IG51bGw7CiAgICBzdGF0ZS5wY0NvbnRyb2wgPSAocy5wY19jb250cm9sICE9PSBmYWxzZSk7CiAgICBtYXJrU3RhdHVzKHMucmVhZHksIHMuYnJhaW4gfHwgIuKAlCIpOwogICAgaWYgKHMuZ292ZWVfc2V0ICYmICFzdGF0ZS5nb3ZlZUNoZWNrZWQpeyBzdGF0ZS5nb3ZlZUNoZWNrZWQgPSB0cnVlOyBjaGVja0dvdmVlKCk7IH0KCiAgICBpZiAoc3RhdGUucHJvdmlkZXIgPT09ICJvbGxhbWEiKXsKICAgICAgLy8gTG9rYWxlcyBHZWhpcm4gLT4gZWlnZW5lIE9uYm9hcmRpbmctL1NldHVwLUxvZ2lrIChrw7xtbWVydCBzaWNoIHVtIEJlZ3LDvMOfdW5nL0thcnRlKQogICAgICBhd2FpdCBjaGVja09sbGFtYSgpOwogICAgICByZXR1cm47CiAgICB9CgogICAgLy8gQW5kZXJlIEFuYmlldGVyIChDbGF1ZGUgZXRjLik6IFZlcmhhbHRlbiB3aWUgYmlzaGVyCiAgICBoaWRlT2xsYW1hUGlsbCgpOwogICAgaWYgKCFzdGF0ZS5yZWFkeSl7CiAgICAgIC8vIE5pY2h0IGJlcmVpdCAtPiBmcmV1bmRsaWNoZSBTdGFydG5hY2hyaWNodCArIEVpbnN0ZWxsdW5nZW4gw7ZmZm5lbgogICAgICBpZiAoY2hhdEVsLmNoaWxkcmVuLmxlbmd0aCA9PT0gMCkKICAgICAgICBhZGRCdWJibGUoImRpbm8iLCAiVHJhZyB6dWVyc3QgZGVpbmVuIEFQSS1TY2hsw7xzc2VsIHVudGVyIOKamSBlaW4sIGRhbm4gbGVnZSBpY2ggbG9zLiDwn6aWIik7CiAgICAgIG9wZW5QYW5lbCgic2V0dGluZ3MiKTsKICAgIH0gZWxzZSBpZiAoY2hhdEVsLmNoaWxkcmVuLmxlbmd0aCA9PT0gMCl7CiAgICAgIC8vIEJlcmVpdCAtPiBCZWdyw7zDn3VuZwogICAgICBncmVldCgpOwogICAgfQogIH1jYXRjaChlKXsKICAgIG1hcmtTdGF0dXMoZmFsc2UsICJvZmZsaW5lIik7CiAgICBhZGRCdWJibGUoImVycm9yIiwgIktvbW1lIG5pY2h0IGFuIGRlbiBEaW5vLVNlcnZlciByYW4gKCIrZS5tZXNzYWdlKyIpLiBMw6R1ZnQgZGVyIGxva2FsZSBTZXJ2ZXI/Iik7CiAgfQp9CgpmdW5jdGlvbiBtYXJrU3RhdHVzKHJlYWR5LCBicmFpbil7CiAgY29uc3QgZG90ID0gJCgic3RhdHVzRG90Iik7CiAgZG90LmNsYXNzTmFtZSA9ICJkb3QgIiArIChyZWFkeSA/ICJvayIgOiAiYmFkIik7CiAgJCgiYnJhaW5UZXh0IikudGV4dENvbnRlbnQgPSBicmFpbiArIChyZWFkeSA/ICIgIMK3ICBvbmxpbmUiIDogIiAgwrcgIG9mZmxpbmUiKTsKfQoKLy8gQmVncsO8w591bmcgKG51ciBmYWxscyBDaGF0IG5vY2ggbGVlcikg4oCUIHplbnRyYWwsIGRhbWl0IMO8YmVyYWxsIHdpZWRlcnZlcndlbmRiYXIKZnVuY3Rpb24gZ3JlZXQoKXsKICBpZiAoY2hhdEVsLmNoaWxkcmVuLmxlbmd0aCA9PT0gMCkKICAgIGFkZEJ1YmJsZSgiZGlubyIsIGBEaW5vIGlzdCBvbmxpbmUsICR7c3RhdGUudXNlck5hbWV9ISBXb3JhdWYgaGFzdCBkdSBCb2NrPyDimqFgKTsKfQoKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09Ci8vICBPbGxhbWEtT25ib2FyZGluZyAobG9rYWxlcyBHZWhpcm4pCi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQpjb25zdCBPTExBTUFfREVGQVVMVF9NT0RFTCA9ICJxd2VuMi41OjdiIjsKbGV0IHNldHVwQ2FyZEVsID0gbnVsbDsKCi8vIFRvbGVyYW50OiBnaWx0IGN1cnJlbnRfbW9kZWwgYWxzIGluc3RhbGxpZXJ0PyAoei5CLiAibGxhbWEzLjIiIG1hdGNodCAibGxhbWEzLjI6bGF0ZXN0IikKZnVuY3Rpb24gbW9kZWxJbnN0YWxsZWQobW9kZWxzLCBjdXJyZW50KXsKICBpZiAoIUFycmF5LmlzQXJyYXkobW9kZWxzKSB8fCAhbW9kZWxzLmxlbmd0aCkgcmV0dXJuIGZhbHNlOwogIGlmICghY3VycmVudCkgcmV0dXJuIGZhbHNlOwogIHJldHVybiBtb2RlbHMuc29tZShtID0+IHsKICAgIGNvbnN0IGEgPSBTdHJpbmcobSksIGIgPSBTdHJpbmcoY3VycmVudCk7CiAgICByZXR1cm4gYSA9PT0gYiB8fCBhLnN0YXJ0c1dpdGgoYikgfHwgYi5zdGFydHNXaXRoKGEpOwogIH0pOwp9CgovLyBrbGVpbmVyIFN0YXR1cy1JbmRpa2F0b3Igb2JlbgpmdW5jdGlvbiBzZXRPbGxhbWFQaWxsKGtpbmQsIGxhYmVsKXsKICBjb25zdCBwaWxsID0gJCgib2xsYW1hUGlsbCIpOwogIGlmICghcGlsbCkgcmV0dXJuOwogIHBpbGwuc3R5bGUuZGlzcGxheSA9ICJpbmxpbmUtZmxleCI7CiAgcGlsbC5jbGFzc05hbWUgPSAib2xsYW1hLXBpbGwgIiArIChraW5kIHx8ICIiKTsKICAkKCJvbGxhbWFQaWxsVGV4dCIpLnRleHRDb250ZW50ID0gbGFiZWw7Cn0KZnVuY3Rpb24gaGlkZU9sbGFtYVBpbGwoKXsKICBjb25zdCBwaWxsID0gJCgib2xsYW1hUGlsbCIpOwogIGlmIChwaWxsKSBwaWxsLnN0eWxlLmRpc3BsYXkgPSAibm9uZSI7Cn0KCi8vIEVudGZlcm50IGVpbmUgZ2dmLiB2b3JoYW5kZW5lIFNldHVwLUthcnRlCmZ1bmN0aW9uIHJlbW92ZVNldHVwQ2FyZCgpewogIGlmIChzZXR1cENhcmRFbCl7IHNldHVwQ2FyZEVsLnJlbW92ZSgpOyBzZXR1cENhcmRFbCA9IG51bGw7IH0KfQoKLy8gUHLDvGZ0IC9hcGkvb2xsYW1hIHVuZCBlbnRzY2hlaWRldCDDvGJlciBLYXJ0ZS9CZWdyw7zDn3VuZwphc3luYyBmdW5jdGlvbiBjaGVja09sbGFtYSgpewogIGxldCBvOwogIHRyeXsKICAgIG8gPSBhd2FpdCBhcGkoIi9hcGkvb2xsYW1hIik7CiAgfWNhdGNoKGUpewogICAgLy8gS29ubnRlIE9sbGFtYS1JbmZvIG5pY2h0IGxhZGVuIC0+IGJlaGFuZGVsbiB3aWUgImzDpHVmdCBuaWNodCIKICAgIG8gPSB7IHJ1bm5pbmc6ZmFsc2UsIG1vZGVsczpbXSwgY3VycmVudF9tb2RlbDpPTExBTUFfREVGQVVMVF9NT0RFTCB9OwogIH0KICBpZiAobyAmJiBvLmVycm9yKXsgbyA9IHsgcnVubmluZzpmYWxzZSwgbW9kZWxzOltdLCBjdXJyZW50X21vZGVsOk9MTEFNQV9ERUZBVUxUX01PREVMIH07IH0KCiAgY29uc3QgcnVubmluZyA9ICEhKG8gJiYgby5ydW5uaW5nKTsKICBjb25zdCBtb2RlbHMgPSAobyAmJiBBcnJheS5pc0FycmF5KG8ubW9kZWxzKSkgPyBvLm1vZGVscyA6IFtdOwogIGNvbnN0IGN1cnJlbnQgPSAobyAmJiBvLmN1cnJlbnRfbW9kZWwpIHx8IE9MTEFNQV9ERUZBVUxUX01PREVMOwogIGNvbnN0IGhhc01vZGVsID0gbW9kZWxJbnN0YWxsZWQobW9kZWxzLCBjdXJyZW50KTsKCiAgaWYgKHJ1bm5pbmcgJiYgaGFzTW9kZWwpewogICAgLy8gQWxsZXMgYmVyZWl0IC0+IGtlaW5lIEthcnRlLCBub3JtYWxlIEJlZ3LDvMOfdW5nCiAgICBzZXRPbGxhbWFQaWxsKCJvayIsICJsb2thbCBha3RpdiIpOwogICAgcmVtb3ZlU2V0dXBDYXJkKCk7CiAgICBncmVldCgpOwogICAgcmV0dXJuIHRydWU7CiAgfQoKICBpZiAoIXJ1bm5pbmcpewogICAgc2V0T2xsYW1hUGlsbCgiYmFkIiwgIlNldHVwIG7DtnRpZyIpOwogICAgc2hvd1NldHVwQ2FyZCgibm90LXJ1bm5pbmciLCB7IG1vZGVscywgY3VycmVudCB9KTsKICB9IGVsc2UgewogICAgLy8gbMOkdWZ0LCBhYmVyIGtlaW4gcGFzc2VuZGVzIE1vZGVsbAogICAgc2V0T2xsYW1hUGlsbCgid2FybiIsICJNb2RlbGwgZmVobHQiKTsKICAgIHNob3dTZXR1cENhcmQoIm5vLW1vZGVsIiwgeyBtb2RlbHMsIGN1cnJlbnQgfSk7CiAgfQoKICAvLyBFaW5tYWxpZ2VzIEF1dG8tUmVjaGVjayBuYWNoIH4ycyBiZWltIGVyc3RlbiBMYWRlbiAoa2VpbiBEYXVlci1Qb2xsaW5nKQogIGlmICghc3RhdGUuYXV0b1JlY2hlY2tEb25lKXsKICAgIHN0YXRlLmF1dG9SZWNoZWNrRG9uZSA9IHRydWU7CiAgICBzZXRUaW1lb3V0KCgpPT57IGlmIChzZXR1cENhcmRFbCkgcmVjaGVja09sbGFtYSgpOyB9LCAyMDAwKTsKICB9CiAgcmV0dXJuIGZhbHNlOwp9CgovLyBCYXV0L2FrdHVhbGlzaWVydCBkaWUgU2V0dXAtS2FydGUgKHN0YXRpc2NoZXMgTWFya3VwID0gaW5uZXJIVE1MOyBkeW5hbWlzY2hlIFRleHRlIHZpYSB0ZXh0Q29udGVudCkKZnVuY3Rpb24gc2hvd1NldHVwQ2FyZChtb2RlLCBpbmZvKXsKICByZW1vdmVTZXR1cENhcmQoKTsKICBjb25zdCBjYXJkID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7CiAgY2FyZC5jbGFzc05hbWUgPSAic2V0dXAtY2FyZCI7CgogIGlmIChtb2RlID09PSAibm8tbW9kZWwiKXsKICAgIGNhcmQuaW5uZXJIVE1MID0gYAogICAgICA8ZGl2IGNsYXNzPSJzYy10aXRsZSI+8J+noCBEaW5vIGZlaGx0IG5vY2ggZWluIE1vZGVsbDwvZGl2PgogICAgICA8ZGl2IGNsYXNzPSJzYy1zdWIiPk9sbGFtYSBsw6R1ZnQgc2Nob24g4oCUIERpbm8gYnJhdWNodCBudXIgbm9jaCBlaW4gU3ByYWNobW9kZWxsLiBIb2wgZGlyIGRhcyBTdGFuZGFyZG1vZGVsbCBvZGVyIHfDpGhsIGVpbnMgZGVyIGluc3RhbGxpZXJ0ZW4uPC9kaXY+CiAgICAgIDxkaXYgY2xhc3M9InNjLXN0ZXAiPgogICAgICAgIDxkaXYgY2xhc3M9InNjLXN0ZXAtaCI+PHNwYW4gY2xhc3M9Im51bSI+4oaTPC9zcGFuPjxzcGFuPk1vZGVsbCBsYWRlbiAoZ3JhdGlzKTwvc3Bhbj48L2Rpdj4KICAgICAgICA8ZGl2IGNsYXNzPSJzYy1jb2RlYm94Ij4KICAgICAgICAgIDxjb2RlIGNsYXNzPSJzYy1jb2RlIiBpZD0ic2MtY21kIj48L2NvZGU+CiAgICAgICAgICA8YnV0dG9uIGNsYXNzPSJzYy1jb3B5IiBpZD0ic2MtY29weSI+8J+TiyBLb3BpZXJlbjwvYnV0dG9uPgogICAgICAgIDwvZGl2PgogICAgICAgIDxkaXYgY2xhc3M9InNjLW1vZGVscyIgaWQ9InNjLW1vZGVscyI+PC9kaXY+CiAgICAgIDwvZGl2PgogICAgICA8ZGl2IGNsYXNzPSJzYy1hY3Rpb25zIj4KICAgICAgICA8YnV0dG9uIGNsYXNzPSJzYy1yZWNoZWNrIiBpZD0ic2MtcmVjaGVjayI+8J+UhCBOb2NobWFsIHByw7xmZW48L2J1dHRvbj4KICAgICAgICA8c3BhbiBjbGFzcz0ic2Mtc3RhdGUiIGlkPSJzYy1zdGF0ZSI+PC9zcGFuPgogICAgICA8L2Rpdj4KICAgIGA7CiAgfSBlbHNlIHsKICAgIGNhcmQuaW5uZXJIVE1MID0gYAogICAgICA8ZGl2IGNsYXNzPSJzYy10aXRsZSI+8J+mliBGYXN0IGZlcnRpZyDigJQgRGlubyBicmF1Y2h0IG5vY2ggc2VpbiBHZWhpcm48L2Rpdj4KICAgICAgPGRpdiBjbGFzcz0ic2Mtc3ViIj5EaW5vIGzDpHVmdCBzdGFuZGFyZG3DpMOfaWcgZ3JhdGlzIHVuZCBsb2thbCDDvGJlciBPbGxhbWEuIFp3ZWkga3VyemUgU2Nocml0dGUsIGRhbm4gZ2VodCdzIGxvcy48L2Rpdj4KICAgICAgPGRpdiBjbGFzcz0ic2Mtc3RlcCI+CiAgICAgICAgPGRpdiBjbGFzcz0ic2Mtc3RlcC1oIj48c3BhbiBjbGFzcz0ibnVtIj4xPC9zcGFuPjxzcGFuPk9sbGFtYSBpbnN0YWxsaWVyZW4gKGdyYXRpcyk8L3NwYW4+PC9kaXY+CiAgICAgICAgPGRpdiBjbGFzcz0ic2Mtc3ViIiBzdHlsZT0ibWFyZ2luOjAiPgogICAgICAgICAgTGFkZSBlcyBoaWVyIGhlcnVudGVyOiA8YSBjbGFzcz0ic2MtbGluayIgaWQ9InNjLWRsIiBocmVmPSJodHRwczovL29sbGFtYS5jb20vZG93bmxvYWQiIHRhcmdldD0iX2JsYW5rIiByZWw9Im5vb3BlbmVyIG5vcmVmZXJyZXIiPm9sbGFtYS5jb20vZG93bmxvYWQ8L2E+CiAgICAgICAgPC9kaXY+CiAgICAgIDwvZGl2PgogICAgICA8ZGl2IGNsYXNzPSJzYy1zdGVwIj4KICAgICAgICA8ZGl2IGNsYXNzPSJzYy1zdGVwLWgiPjxzcGFuIGNsYXNzPSJudW0iPjI8L3NwYW4+PHNwYW4+RGllc2VzIEtvbW1hbmRvIGltIFRlcm1pbmFsIC8gaW4gZGVyIEVpbmdhYmVhdWZmb3JkZXJ1bmcgYXVzZsO8aHJlbjo8L3NwYW4+PC9kaXY+CiAgICAgICAgPGRpdiBjbGFzcz0ic2MtY29kZWJveCI+CiAgICAgICAgICA8Y29kZSBjbGFzcz0ic2MtY29kZSIgaWQ9InNjLWNtZCI+PC9jb2RlPgogICAgICAgICAgPGJ1dHRvbiBjbGFzcz0ic2MtY29weSIgaWQ9InNjLWNvcHkiPvCfk4sgS29waWVyZW48L2J1dHRvbj4KICAgICAgICA8L2Rpdj4KICAgICAgPC9kaXY+CiAgICAgIDxkaXYgY2xhc3M9InNjLWFjdGlvbnMiPgogICAgICAgIDxidXR0b24gY2xhc3M9InNjLXJlY2hlY2siIGlkPSJzYy1yZWNoZWNrIj7wn5SEIE5vY2htYWwgcHLDvGZlbjwvYnV0dG9uPgogICAgICAgIDxidXR0b24gY2xhc3M9InNjLXNldHRpbmdzIiBpZD0ic2Mtc2V0dGluZ3MiPkxpZWJlciBkZW4gc3RhcmtlbiBDbGF1ZGUgbnV0emVuPyDihpIg4pqZIEVpbnN0ZWxsdW5nZW48L2J1dHRvbj4KICAgICAgICA8c3BhbiBjbGFzcz0ic2Mtc3RhdGUiIGlkPSJzYy1zdGF0ZSI+PC9zcGFuPgogICAgICA8L2Rpdj4KICAgIGA7CiAgfQoKICAvLyBLYXJ0ZSBvYmVuIGltIENoYXQgcGxhdHppZXJlbiwgZGFtaXQgc2llIGd1dCBzaWNodGJhciBpc3QKICBjaGF0RWwucHJlcGVuZChjYXJkKTsKICBzZXR1cENhcmRFbCA9IGNhcmQ7CiAgc2Nyb2xsRG93bigpOwoKICAvLyBLb21tYW5kby1UZXh0IChkeW5hbWlzY2ggLT4gdGV4dENvbnRlbnQsIGtlaW4gaW5uZXJIVE1MKQogIGNvbnN0IGNtZCA9IChtb2RlID09PSAibm8tbW9kZWwiKQogICAgPyAoIm9sbGFtYSBwdWxsICIgKyAoaW5mbyAmJiBpbmZvLmN1cnJlbnQgPyBpbmZvLmN1cnJlbnQgOiBPTExBTUFfREVGQVVMVF9NT0RFTCkpCiAgICA6ICgib2xsYW1hIHJ1biAiICsgT0xMQU1BX0RFRkFVTFRfTU9ERUwpOwogIGNvbnN0IGNtZEVsID0gY2FyZC5xdWVyeVNlbGVjdG9yKCIjc2MtY21kIik7CiAgaWYgKGNtZEVsKSBjbWRFbC50ZXh0Q29udGVudCA9IGNtZDsKCiAgLy8gS29waWVyZW4tQnV0dG9uCiAgY29uc3QgY29weUJ0biA9IGNhcmQucXVlcnlTZWxlY3RvcigiI3NjLWNvcHkiKTsKICBpZiAoY29weUJ0bikgY29weUJ0bi5vbmNsaWNrID0gKCk9PiBjb3B5VG9DbGlwYm9hcmQoY21kLCBjb3B5QnRuKTsKCiAgLy8gUmVjaGVjay1CdXR0b24KICBjb25zdCByZWNoZWNrQnRuID0gY2FyZC5xdWVyeVNlbGVjdG9yKCIjc2MtcmVjaGVjayIpOwogIGlmIChyZWNoZWNrQnRuKSByZWNoZWNrQnRuLm9uY2xpY2sgPSByZWNoZWNrT2xsYW1hOwoKICAvLyBFaW5zdGVsbHVuZ2VuLUxpbmsKICBjb25zdCBzZXRCdG4gPSBjYXJkLnF1ZXJ5U2VsZWN0b3IoIiNzYy1zZXR0aW5ncyIpOwogIGlmIChzZXRCdG4pIHNldEJ0bi5vbmNsaWNrID0gKCk9PiBvcGVuUGFuZWwoInNldHRpbmdzIik7CgogIC8vIEluc3RhbGxpZXJ0ZSBNb2RlbGxlIGFscyBCdXR0b25zIChudXIgaW0gbm8tbW9kZWwtRmFsbCB1bmQgd2VubiB2b3JoYW5kZW4pCiAgaWYgKG1vZGUgPT09ICJuby1tb2RlbCIpewogICAgY29uc3Qgd3JhcCA9IGNhcmQucXVlcnlTZWxlY3RvcigiI3NjLW1vZGVscyIpOwogICAgY29uc3QgbW9kZWxzID0gKGluZm8gJiYgQXJyYXkuaXNBcnJheShpbmZvLm1vZGVscykpID8gaW5mby5tb2RlbHMgOiBbXTsKICAgIGlmICh3cmFwICYmIG1vZGVscy5sZW5ndGgpewogICAgICBjb25zdCBsYmwgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJzcGFuIik7CiAgICAgIGxibC5zdHlsZS5jc3NUZXh0ID0gImZvbnQtc2l6ZToxMnB4O2NvbG9yOnZhcigtLW11dCk7YWxpZ24tc2VsZjpjZW50ZXI7bWFyZ2luLXJpZ2h0OjJweCI7CiAgICAgIGxibC50ZXh0Q29udGVudCA9ICJTY2hvbiBpbnN0YWxsaWVydDoiOwogICAgICB3cmFwLmFwcGVuZENoaWxkKGxibCk7CiAgICAgIG1vZGVscy5mb3JFYWNoKG09PnsKICAgICAgICBjb25zdCBiID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiYnV0dG9uIik7CiAgICAgICAgYi5jbGFzc05hbWUgPSAic2MtbW9kZWwiOwogICAgICAgIGIudGV4dENvbnRlbnQgPSBtOyAgICAgICAgICAgICAgICAgLy8gZHluYW1pc2NoIC0+IHRleHRDb250ZW50CiAgICAgICAgYi5vbmNsaWNrID0gKCk9PiBwaWNrT2xsYW1hTW9kZWwobSwgYik7CiAgICAgICAgd3JhcC5hcHBlbmRDaGlsZChiKTsKICAgICAgfSk7CiAgICB9CiAgfQp9CgovLyBJbiBad2lzY2hlbmFibGFnZSBrb3BpZXJlbiAobWl0IEZhbGxiYWNrKQpmdW5jdGlvbiBjb3B5VG9DbGlwYm9hcmQodGV4dCwgYnRuKXsKICBjb25zdCBkb25lID0gKCk9PnsKICAgIGlmICghYnRuKSByZXR1cm47CiAgICBjb25zdCBvbGQgPSBidG4udGV4dENvbnRlbnQ7CiAgICBidG4udGV4dENvbnRlbnQgPSAi4pyTIEtvcGllcnQiOwogICAgc2V0VGltZW91dCgoKT0+eyBidG4udGV4dENvbnRlbnQgPSBvbGQ7IH0sIDE1MDApOwogIH07CiAgdHJ5ewogICAgaWYgKG5hdmlnYXRvci5jbGlwYm9hcmQgJiYgbmF2aWdhdG9yLmNsaXBib2FyZC53cml0ZVRleHQpewogICAgICBuYXZpZ2F0b3IuY2xpcGJvYXJkLndyaXRlVGV4dCh0ZXh0KS50aGVuKGRvbmUsICgpPT5mYWxsYmFja0NvcHkodGV4dCwgZG9uZSkpOwogICAgfSBlbHNlIHsKICAgICAgZmFsbGJhY2tDb3B5KHRleHQsIGRvbmUpOwogICAgfQogIH1jYXRjaChlKXsgZmFsbGJhY2tDb3B5KHRleHQsIGRvbmUpOyB9Cn0KZnVuY3Rpb24gZmFsbGJhY2tDb3B5KHRleHQsIGRvbmUpewogIHRyeXsKICAgIGNvbnN0IHRhID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgidGV4dGFyZWEiKTsKICAgIHRhLnZhbHVlID0gdGV4dDsgdGEuc3R5bGUucG9zaXRpb249ImZpeGVkIjsgdGEuc3R5bGUub3BhY2l0eT0iMCI7CiAgICBkb2N1bWVudC5ib2R5LmFwcGVuZENoaWxkKHRhKTsgdGEuZm9jdXMoKTsgdGEuc2VsZWN0KCk7CiAgICBkb2N1bWVudC5leGVjQ29tbWFuZCgiY29weSIpOwogICAgZG9jdW1lbnQuYm9keS5yZW1vdmVDaGlsZCh0YSk7CiAgICBkb25lICYmIGRvbmUoKTsKICB9Y2F0Y2goZSl7IC8qIHN0aWxsICovIH0KfQoKLy8gSW5zdGFsbGllcnRlcyBNb2RlbGwgd8OkaGxlbiAtPiBzZXR6ZW4sIFN0YXR1cyBuZXUgbGFkZW4sIEthcnRlIGF1c2JsZW5kZW4KYXN5bmMgZnVuY3Rpb24gcGlja09sbGFtYU1vZGVsKG5hbWUsIGJ0bil7CiAgY29uc3Qgc3RhdGVFbCA9IHNldHVwQ2FyZEVsID8gc2V0dXBDYXJkRWwucXVlcnlTZWxlY3RvcigiI3NjLXN0YXRlIikgOiBudWxsOwogIGlmIChidG4pIGJ0bi5kaXNhYmxlZCA9IHRydWU7CiAgaWYgKHN0YXRlRWwpIHN0YXRlRWwudGV4dENvbnRlbnQgPSAic2V0emUgTW9kZWxsIOKApiI7CiAgdHJ5ewogICAgY29uc3QgciA9IGF3YWl0IGFwaSgiL2FwaS9zZXR0aW5ncyIsICJQT1NUIiwgeyBvbGxhbWFfbW9kZWw6IG5hbWUgfSk7CiAgICBpZiAociAmJiByLmVycm9yKXsKICAgICAgaWYgKHN0YXRlRWwpIHN0YXRlRWwudGV4dENvbnRlbnQgPSAi4pqgICIgKyByLmVycm9yOwogICAgICBpZiAoYnRuKSBidG4uZGlzYWJsZWQgPSBmYWxzZTsKICAgICAgcmV0dXJuOwogICAgfQogICAgcmVtb3ZlU2V0dXBDYXJkKCk7CiAgICBhd2FpdCBsb2FkU3RhdHVzKCk7ICAgICAgICAgIC8vIGzDpGR0IFN0YXR1cyArIE9sbGFtYSBuZXUsIGJlZ3LDvMOfdCBiZWkgRXJmb2xnCiAgfWNhdGNoKGUpewogICAgaWYgKHN0YXRlRWwpIHN0YXRlRWwudGV4dENvbnRlbnQgPSAi4pqgICIgKyBlLm1lc3NhZ2U7CiAgICBpZiAoYnRuKSBidG4uZGlzYWJsZWQgPSBmYWxzZTsKICB9Cn0KCi8vICJOb2NobWFsIHByw7xmZW4iIOKAlCByb2J1c3QsIGtlaW4gRGF1ZXItUG9sbGluZwphc3luYyBmdW5jdGlvbiByZWNoZWNrT2xsYW1hKCl7CiAgaWYgKCFzZXR1cENhcmRFbCkgcmV0dXJuOwogIGNvbnN0IHJlY2hlY2tCdG4gPSBzZXR1cENhcmRFbC5xdWVyeVNlbGVjdG9yKCIjc2MtcmVjaGVjayIpOwogIGNvbnN0IHN0YXRlRWwgPSBzZXR1cENhcmRFbC5xdWVyeVNlbGVjdG9yKCIjc2Mtc3RhdGUiKTsKICBpZiAocmVjaGVja0J0bikgcmVjaGVja0J0bi5kaXNhYmxlZCA9IHRydWU7CiAgaWYgKHN0YXRlRWwpIHN0YXRlRWwudGV4dENvbnRlbnQgPSAicHLDvGZlIOKApiI7CiAgbGV0IG87CiAgdHJ5ewogICAgbyA9IGF3YWl0IGFwaSgiL2FwaS9vbGxhbWEiKTsKICB9Y2F0Y2goZSl7CiAgICBpZiAoc3RhdGVFbCkgc3RhdGVFbC50ZXh0Q29udGVudCA9ICJOb2NoIG5pY2h0IGVycmVpY2hiYXIg4oCUIHN0YXJ0ZSBPbGxhbWEgdW5kIHZlcnN1Y2gncyBnbGVpY2ggbm9jaG1hbC4iOwogICAgaWYgKHJlY2hlY2tCdG4pIHJlY2hlY2tCdG4uZGlzYWJsZWQgPSBmYWxzZTsKICAgIHNldE9sbGFtYVBpbGwoImJhZCIsICJTZXR1cCBuw7Z0aWciKTsKICAgIHJldHVybjsKICB9CiAgaWYgKG8gJiYgby5lcnJvcil7CiAgICBpZiAoc3RhdGVFbCkgc3RhdGVFbC50ZXh0Q29udGVudCA9ICLimqAgIiArIG8uZXJyb3I7CiAgICBpZiAocmVjaGVja0J0bikgcmVjaGVja0J0bi5kaXNhYmxlZCA9IGZhbHNlOwogICAgcmV0dXJuOwogIH0KCiAgY29uc3QgcnVubmluZyA9ICEhKG8gJiYgby5ydW5uaW5nKTsKICBjb25zdCBtb2RlbHMgPSAobyAmJiBBcnJheS5pc0FycmF5KG8ubW9kZWxzKSkgPyBvLm1vZGVscyA6IFtdOwogIGNvbnN0IGN1cnJlbnQgPSAobyAmJiBvLmN1cnJlbnRfbW9kZWwpIHx8IE9MTEFNQV9ERUZBVUxUX01PREVMOwogIGNvbnN0IGhhc01vZGVsID0gbW9kZWxJbnN0YWxsZWQobW9kZWxzLCBjdXJyZW50KTsKCiAgaWYgKHJ1bm5pbmcgJiYgaGFzTW9kZWwpewogICAgc2V0T2xsYW1hUGlsbCgib2siLCAibG9rYWwgYWt0aXYiKTsKICAgIHJlbW92ZVNldHVwQ2FyZCgpOwogICAgc3RhdGUucmVhZHkgPSB0cnVlOwogICAgYWRkQnViYmxlKCJkaW5vIiwgYERpbm8gaXN0IG9ubGluZSwgJHtzdGF0ZS51c2VyTmFtZX0hIFdvcmF1ZiBoYXN0IGR1IEJvY2s/IOKaoWApOwogICAgcmV0dXJuOwogIH0KCiAgLy8gTm9jaCBuaWNodCBmZXJ0aWcgLT4gS2FydGUgcGFzc2VuZCBha3R1YWxpc2llcmVuCiAgaWYgKCFydW5uaW5nKXsKICAgIHNldE9sbGFtYVBpbGwoImJhZCIsICJTZXR1cCBuw7Z0aWciKTsKICAgIHNob3dTZXR1cENhcmQoIm5vdC1ydW5uaW5nIiwgeyBtb2RlbHMsIGN1cnJlbnQgfSk7CiAgfSBlbHNlIHsKICAgIHNldE9sbGFtYVBpbGwoIndhcm4iLCAiTW9kZWxsIGZlaGx0Iik7CiAgICBzaG93U2V0dXBDYXJkKCJuby1tb2RlbCIsIHsgbW9kZWxzLCBjdXJyZW50IH0pOwogIH0KICBjb25zdCBucyA9IHNldHVwQ2FyZEVsID8gc2V0dXBDYXJkRWwucXVlcnlTZWxlY3RvcigiI3NjLXN0YXRlIikgOiBudWxsOwogIGlmIChucykgbnMudGV4dENvbnRlbnQgPSBydW5uaW5nID8gIkzDpHVmdCDigJQgYWJlciBlcyBmZWhsdCBub2NoIGRhcyBNb2RlbGwuIiA6ICJPbGxhbWEgbMOkdWZ0IG5vY2ggbmljaHQuIjsKfQoKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09Ci8vICBDaGF0IHNlbmRlbgovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KYXN5bmMgZnVuY3Rpb24gc2VuZCgpewogIGlmIChzdGF0ZS5idXN5KSByZXR1cm47CiAgY29uc3QgdGV4dCA9IGlucHV0RWwudmFsdWUudHJpbSgpOwogIGlmICghdGV4dCkgcmV0dXJuOwogIGlucHV0RWwudmFsdWUgPSAiIjsgYXV0b0dyb3coKTsKCiAgYWRkQnViYmxlKCJ1c2VyIiwgdGV4dCk7CiAgc3RhdGUubWVzc2FnZXMucHVzaCh7IHJvbGU6InVzZXIiLCBjb250ZW50OnRleHQgfSk7CgogIHNldEJ1c3kodHJ1ZSk7CiAgdHJ5ewogICAgY29uc3QgZGF0YSA9IGF3YWl0IGFwaSgiL2FwaS9jaGF0IiwgIlBPU1QiLCB7IG1lc3NhZ2VzOiBzdGF0ZS5tZXNzYWdlcyB9KTsKICAgIGhpZGVUeXBpbmcoKTsKICAgIGlmIChkYXRhLmVycm9yKXsKICAgICAgYWRkQnViYmxlKCJlcnJvciIsIGRhdGEuZXJyb3IpOwogICAgICAvLyBsZXR6dGUgTnV0emVyLU5hY2hyaWNodCBuaWNodCBkYXVlcmhhZnQgYmVoYWx0ZW4KICAgICAgc3RhdGUubWVzc2FnZXMucG9wKCk7CiAgICB9IGVsc2UgewogICAgICBjb25zdCByZXBseSA9IGRhdGEucmVwbHkgfHwgIiI7CiAgICAgIGNvbnN0IHNob3duID0gc3RyaXBBY3Rpb25MaW5lcyhyZXBseSkgfHwgcmVwbHk7CiAgICAgIGFkZEJ1YmJsZSgiZGlubyIsIHNob3duKTsKICAgICAgc3RhdGUubWVzc2FnZXMucHVzaCh7IHJvbGU6ImFzc2lzdGFudCIsIGNvbnRlbnQ6cmVwbHkgfSk7CiAgICAgIHNwZWFrKHNob3duKTsKICAgICAgcmVuZGVyQWN0aW9ucyhkYXRhLmFjdGlvbnMsIHJlcGx5KTsKICAgIH0KICB9Y2F0Y2goZSl7CiAgICBoaWRlVHlwaW5nKCk7CiAgICBhZGRCdWJibGUoImVycm9yIiwgIk5ldHp3ZXJrZmVobGVyOiAiK2UubWVzc2FnZSk7CiAgICBzdGF0ZS5tZXNzYWdlcy5wb3AoKTsKICB9ZmluYWxseXsKICAgIHNldEJ1c3koZmFsc2UpOwogICAgaW5wdXRFbC5mb2N1cygpOwogIH0KfQoKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09Ci8vICBQQy1TdGV1ZXJ1bmc6IERpbm9zIHZvcmdlc2NobGFnZW5lIEFrdGlvbmVuIGFscyBCZXN0w6R0aWd1bmdzLUtuw7ZwZmUKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09CmNvbnN0IEFDVElPTl9NRVRBID0gewogIGFwcF9vZWZmbmVuOiAgICAgeyBlbW9qaToi8J+TgiIsIGxhYmVsOiJQcm9ncmFtbSDDtmZmbmVuIiB9LAogIHdlYl9vZWZmbmVuOiAgICAgeyBlbW9qaToi8J+MkCIsIGxhYmVsOiJXZWJzZWl0ZSDDtmZmbmVuIiB9LAogIG9yZG5lcl9vZWZmbmVuOiAgeyBlbW9qaToi8J+Xgu+4jyIsIGxhYmVsOiJPcmRuZXIgw7ZmZm5lbiIgfSwKICBkYXRlaV9zY2hyZWliZW46IHsgZW1vamk6IvCfk50iLCBsYWJlbDoiRGF0ZWkgc2NocmVpYmVuIiB9LAogIGRhdGVpX2xlc2VuOiAgICAgeyBlbW9qaToi8J+TliIsIGxhYmVsOiJEYXRlaSBsZXNlbiIgfSwKICBkYXRlaWVuX2xpc3RlOiAgIHsgZW1vamk6IvCfk4siLCBsYWJlbDoiRGF0ZWllbiBhdWZsaXN0ZW4iIH0sCiAgc3lzdGVtX2luZm86ICAgICB7IGVtb2ppOiLwn5K7IiwgbGFiZWw6IlN5c3RlbS1JbmZvIiB9LAogIGJlZmVobDogICAgICAgICAgeyBlbW9qaToi4pqhIiwgbGFiZWw6IkJlZmVobCBhdXNmw7xocmVuIiB9LAogIGxpY2h0X2FuOiAgICAgICAgeyBlbW9qaToi8J+SoSIsIGxhYmVsOiJMaWNodCBhbiIsIGF1dG86dHJ1ZSB9LAogIGxpY2h0X2F1czogICAgICAgeyBlbW9qaToi8J+MmSIsIGxhYmVsOiJMaWNodCBhdXMiLCBhdXRvOnRydWUgfSwKICBsaWNodF9mYXJiZTogICAgIHsgZW1vamk6IvCfjqgiLCBsYWJlbDoiTGljaHRmYXJiZSIsIGF1dG86dHJ1ZSB9LAogIGxpY2h0X2hlbGxpZ2tlaXQ6eyBlbW9qaToi8J+UhiIsIGxhYmVsOiJIZWxsaWdrZWl0IiwgYXV0bzp0cnVlIH0sCn07CmNvbnN0IEFDVElPTl9XQVJOID0geyBiZWZlaGw6dHJ1ZSB9OwoKLy8gRGllIFtBS1RJT05dLVplaWxlbiBhdXMgZGVtIEFuemVpZ2UtVGV4dCBlbnRmZXJuZW4gKHdlcmRlbiB6dSBLbsO2cGZlbikKY29uc3QgQUNUSU9OX1JFID0gL1xbP1xzKkFLVElPTlxzKlxdP1xzKls6XC1dP1xzKlthLXpBLVpfw6TDtsO8XStccypcfC9pOwpmdW5jdGlvbiBzdHJpcEFjdGlvbkxpbmVzKHRleHQpewogIHJldHVybiAodGV4dCB8fCAiIikuc3BsaXQoIlxuIikuZmlsdGVyKGxuID0+ICFBQ1RJT05fUkUudGVzdChsbikpCiAgICAuam9pbigiXG4iKS5yZXBsYWNlKC9cbnszLH0vZywgIlxuXG4iKS50cmltKCk7Cn0KCi8vIEFrdGlvbmVuIGF1cyBEaW5vcyBUZXh0IGVya2VubmVuIChmYWxscyBkZXIgU2VydmVyIGtlaW5lIG1pdGdpYnQpCmZ1bmN0aW9uIHBhcnNlQWN0aW9ucyh0ZXh0KXsKICBjb25zdCBvdXQgPSBbXTsKICAodGV4dCB8fCAiIikuc3BsaXQoIlxuIikuZm9yRWFjaChsbiA9PiB7CiAgICBjb25zdCBtID0gbG4ubWF0Y2goL1xbP1xzKkFLVElPTlxzKlxdP1xzKls6XC1dP1xzKihbYS16QS1aX8Okw7bDvF0rKVxzKlx8XHMqKC4qKSQvaSk7CiAgICBpZiAoIW0pIHJldHVybjsKICAgIGNvbnN0IG5hbWUgPSBtWzFdLnRyaW0oKS50b0xvd2VyQ2FzZSgpOwogICAgaWYgKCFBQ1RJT05fTUVUQVtuYW1lXSkgcmV0dXJuOwogICAgb3V0LnB1c2goeyBuYW1lLCBhcmc6IG1bMl0udHJpbSgpLCB3YXJuOiAhIUFDVElPTl9XQVJOW25hbWVdIH0pOwogIH0pOwogIHJldHVybiBvdXQ7Cn0KCmZ1bmN0aW9uIHJlbmRlckFjdGlvbnMoYWN0aW9ucywgcmVwbHlUZXh0KXsKICBsZXQgbGlzdCA9IChhY3Rpb25zICYmIGFjdGlvbnMubGVuZ3RoKSA/IGFjdGlvbnMgOiBwYXJzZUFjdGlvbnMocmVwbHlUZXh0KTsKICBpZiAoIWxpc3QgfHwgIWxpc3QubGVuZ3RoKSByZXR1cm47CiAgbGlzdC5mb3JFYWNoKGEgPT4gewogICAgY29uc3QgbWV0YSA9IEFDVElPTl9NRVRBW2EubmFtZV0gfHwge307CiAgICBpZiAobWV0YS5hdXRvKSBhdXRvUnVuQWN0aW9uKGEpOyAgICAgICAgICAvLyB6LkIuIEdvdmVlLUxpY2h0OiBzb2ZvcnQsIG9obmUgS2xpY2sKICAgIGVsc2UgaWYgKHN0YXRlLnBjQ29udHJvbCkgYWRkQWN0aW9uQ2FyZChhKTsgLy8gUEMtQWt0aW9uZW46IG1pdCBCZXN0w6R0aWd1bmcKICB9KTsKfQoKLy8gQXV0by1Ba3Rpb24gKGhhcm1sb3MsIHouQi4gTGljaHQpOiBzb2ZvcnQgYXVzZsO8aHJlbiwgRXJnZWJuaXMgYWxzIGtsZWluZSBaZWlsZSB6ZWlnZW4KYXN5bmMgZnVuY3Rpb24gYXV0b1J1bkFjdGlvbihhKXsKICBjb25zdCBtZXRhID0gQUNUSU9OX01FVEFbYS5uYW1lXSB8fCB7IGVtb2ppOiLwn5KhIiwgbGFiZWw6YS5uYW1lIH07CiAgY29uc3Qgd3JhcCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOwogIHdyYXAuY2xhc3NOYW1lID0gIm1zZyBkaW5vIjsKICB3cmFwLmlubmVySFRNTCA9ICc8ZGl2IGNsYXNzPSJhdmF0YXIiPicrbWV0YS5lbW9qaSsnPC9kaXY+JzsKICBjb25zdCBiID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IGIuY2xhc3NOYW1lID0gImJ1YmJsZSI7CiAgY29uc3QgdCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOwogIHQuc3R5bGUuY3NzVGV4dCA9ICJmb250LXNpemU6MTNweDtjb2xvcjojYmZlOWY1IjsKICB0LnRleHRDb250ZW50ID0gbWV0YS5sYWJlbCArIChhLmFyZyA/ICIgwrcgIiArIGEuYXJnIDogIiIpICsgIiDigKYiOwogIGIuYXBwZW5kQ2hpbGQodCk7IHdyYXAuYXBwZW5kQ2hpbGQoYik7IGNoYXRFbC5hcHBlbmRDaGlsZCh3cmFwKTsgc2Nyb2xsRG93bigpOwogIHRyeXsKICAgIGNvbnN0IGRhdGEgPSBhd2FpdCBhcGkoIi9hcGkvYWN0aW9uIiwgIlBPU1QiLCB7IG5hbWU6YS5uYW1lLCBhcmc6YS5hcmcgfSk7CiAgICB0LnN0eWxlLmNvbG9yID0gZGF0YS5vayA/ICIjMzRkMzk5IiA6ICIjZmI3MTg1IjsKICAgIHQudGV4dENvbnRlbnQgPSAoZGF0YS5vayA/ICLinJMgIiA6ICLinJYgIikgKyBtZXRhLmxhYmVsICsgKGEuYXJnID8gIiDCtyAiICsgYS5hcmcgOiAiIikgKwogICAgICAgICAgICAgICAgICAgIChkYXRhLm91dHB1dCA/ICIg4oCUICIgKyBkYXRhLm91dHB1dCA6ICIiKTsKICB9Y2F0Y2goZSl7IHQuc3R5bGUuY29sb3IgPSAiI2ZiNzE4NSI7IHQudGV4dENvbnRlbnQgPSAi4pyWICIgKyBtZXRhLmxhYmVsICsgIjogIiArIGUubWVzc2FnZTsgfQogIHNjcm9sbERvd24oKTsKfQoKZnVuY3Rpb24gYWRkQWN0aW9uQ2FyZChhKXsKICBjb25zdCBtZXRhID0gQUNUSU9OX01FVEFbYS5uYW1lXSB8fCB7IGVtb2ppOiLwn5ug77iPIiwgbGFiZWw6YS5uYW1lIH07CiAgY29uc3Qgd3JhcCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOwogIHdyYXAuY2xhc3NOYW1lID0gIm1zZyBkaW5vIjsKICB3cmFwLmlubmVySFRNTCA9ICc8ZGl2IGNsYXNzPSJhdmF0YXIiPvCflqXvuI88L2Rpdj4nOwogIGNvbnN0IGNhcmQgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsKICBjYXJkLmNsYXNzTmFtZSA9ICJidWJibGUiOwogIGNhcmQuc3R5bGUuYm9yZGVyQ29sb3IgPSBhLndhcm4gPyAicmdiYSgyNTEsMTEzLDEzMywuNSkiIDogInJnYmEoNTYsMTg5LDI0OCwuMzUpIjsKCiAgY29uc3QgdGl0bGUgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsKICB0aXRsZS5jbGFzc05hbWUgPSAibGFiZWwiOwogIHRpdGxlLnRleHRDb250ZW50ID0gKGEud2FybiA/ICLimqDvuI8gIiA6ICIiKSArIG1ldGEuZW1vamkgKyAiICIgKyBtZXRhLmxhYmVsOwogIGNhcmQuYXBwZW5kQ2hpbGQodGl0bGUpOwoKICBjb25zdCBhcmcgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsKICBhcmcuc3R5bGUuY3NzVGV4dCA9ICJmb250LXNpemU6MTNweDtjb2xvcjojYmZlOWY1O21hcmdpbjoycHggMCA4cHg7d29yZC1icmVhazpicmVhay13b3JkO3doaXRlLXNwYWNlOnByZS13cmFwIjsKICBhcmcudGV4dENvbnRlbnQgPSBhLmFyZyB8fCAiKG9obmUgV2VydCkiOwogIGNhcmQuYXBwZW5kQ2hpbGQoYXJnKTsKCiAgY29uc3Qgcm93ID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7CiAgcm93LnN0eWxlLmNzc1RleHQgPSAiZGlzcGxheTpmbGV4O2dhcDo4cHg7ZmxleC13cmFwOndyYXAiOwogIGNvbnN0IHJ1biA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImJ1dHRvbiIpOwogIHJ1bi5jbGFzc05hbWUgPSAiYnRuIHByaW1hcnkiOwogIHJ1bi50ZXh0Q29udGVudCA9IGEud2FybiA/ICLilrYgVHJvdHpkZW0gYXVzZsO8aHJlbiIgOiAi4pa2IEF1c2bDvGhyZW4iOwogIHJ1bi5vbmNsaWNrID0gKCkgPT4gcnVuQWN0aW9uKGEsIHJ1biwgY2FyZCk7CiAgY29uc3Qgc2tpcCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImJ1dHRvbiIpOwogIHNraXAuY2xhc3NOYW1lID0gImJ0biI7CiAgc2tpcC50ZXh0Q29udGVudCA9ICLinJYgVmVyd2VyZmVuIjsKICBza2lwLm9uY2xpY2sgPSAoKSA9PiB7IGNhcmQucmVtb3ZlQ2hpbGQocm93KTsgc3RhdHVzLnRleHRDb250ZW50ID0gIlZlcndvcmZlbi4iOyB9OwogIHJvdy5hcHBlbmRDaGlsZChydW4pOyByb3cuYXBwZW5kQ2hpbGQoc2tpcCk7CiAgY2FyZC5hcHBlbmRDaGlsZChyb3cpOwoKICBjb25zdCBzdGF0dXMgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsKICBzdGF0dXMuc3R5bGUuY3NzVGV4dCA9ICJmb250LXNpemU6MTJweDtjb2xvcjojN2M4ZGI1O21hcmdpbi10b3A6N3B4O3doaXRlLXNwYWNlOnByZS13cmFwO3dvcmQtYnJlYWs6YnJlYWstd29yZCI7CiAgY2FyZC5hcHBlbmRDaGlsZChzdGF0dXMpOwoKICB3cmFwLmFwcGVuZENoaWxkKGNhcmQpOwogIGNoYXRFbC5hcHBlbmRDaGlsZCh3cmFwKTsKICBzY3JvbGxEb3duKCk7CiAgY2FyZC5fc3RhdHVzID0gc3RhdHVzOyBjYXJkLl9yb3cgPSByb3c7Cn0KCmFzeW5jIGZ1bmN0aW9uIHJ1bkFjdGlvbihhLCBidG4sIGNhcmQpewogIGlmIChhLndhcm4pewogICAgY29uc3Qgb2sgPSB3aW5kb3cuY29uZmlybSgiRGlubyB3aWxsIGRpZXNlbiBCZWZlaGwgYXVmIGRlaW5lbSBQQyBhdXNmw7xocmVuOlxuXG4iICsgYS5hcmcgKwogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAiXG5cbk51ciBiZXN0w6R0aWdlbiwgd2VubiBkdSBnZW5hdSB3ZWnDn3QsIHdhcyBlciB0dXQuIEF1c2bDvGhyZW4/Iik7CiAgICBpZiAoIW9rKSByZXR1cm47CiAgfQogIGJ0bi5kaXNhYmxlZCA9IHRydWU7CiAgY29uc3Qgc3RhdHVzID0gY2FyZC5fc3RhdHVzOwogIHN0YXR1cy50ZXh0Q29udGVudCA9ICJsw6R1ZnTigKYiOwogIHRyeXsKICAgIGNvbnN0IGRhdGEgPSBhd2FpdCBhcGkoIi9hcGkvYWN0aW9uIiwgIlBPU1QiLCB7IG5hbWU6YS5uYW1lLCBhcmc6YS5hcmcgfSk7CiAgICBpZiAoZGF0YS5vayl7CiAgICAgIHN0YXR1cy5zdHlsZS5jb2xvciA9ICIjMzRkMzk5IjsKICAgICAgc3RhdHVzLnRleHRDb250ZW50ID0gIuKckyAiICsgKGRhdGEub3V0cHV0IHx8ICJFcmxlZGlndC4iKTsKICAgICAgaWYgKGNhcmQuX3JvdykgY2FyZC5fcm93LnN0eWxlLmRpc3BsYXkgPSAibm9uZSI7CiAgICAgIC8vIEVyZ2VibmlzIGluIGRlbiBHZXNwcsOkY2hzLUtvbnRleHQgZ2ViZW4sIGRhbWl0IERpbm8gZXMga2VubnQKICAgICAgc3RhdGUubWVzc2FnZXMucHVzaCh7IHJvbGU6InVzZXIiLCBjb250ZW50OiJbUEMtRXJnZWJuaXMgIithLm5hbWUrIl06ICIgKyAoZGF0YS5vdXRwdXR8fCJvayIpLnNsaWNlKDAsMTUwMCkgfSk7CiAgICB9IGVsc2UgewogICAgICBzdGF0dXMuc3R5bGUuY29sb3IgPSAiI2ZiNzE4NSI7CiAgICAgIHN0YXR1cy50ZXh0Q29udGVudCA9ICLinJYgIiArIChkYXRhLm91dHB1dCB8fCAiRmVobGdlc2NobGFnZW4uIik7CiAgICAgIGJ0bi5kaXNhYmxlZCA9IGZhbHNlOwogICAgfQogIH1jYXRjaChlKXsKICAgIHN0YXR1cy5zdHlsZS5jb2xvciA9ICIjZmI3MTg1IjsKICAgIHN0YXR1cy50ZXh0Q29udGVudCA9ICLinJYgTmV0endlcmtmZWhsZXI6ICIgKyBlLm1lc3NhZ2U7CiAgICBidG4uZGlzYWJsZWQgPSBmYWxzZTsKICB9CiAgc2Nyb2xsRG93bigpOwp9CgovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KLy8gIFF1aWNrLUFjdGlvbnMKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09Ci8vIEdlbmVyaXNjaGVyIEhlbGZlciBmw7xyIC9wbGFuIHVuZCAvdGFnIChCb2R5IHt9IC0+IHt0ZXh0fSkKYXN5bmMgZnVuY3Rpb24gc2ltcGxlQWN0aW9uKHBhdGgpewogIGlmIChzdGF0ZS5idXN5KSByZXR1cm47CiAgc2V0QnVzeSh0cnVlKTsKICB0cnl7CiAgICBjb25zdCBkYXRhID0gYXdhaXQgYXBpKHBhdGgsICJQT1NUIiwge30pOwogICAgaGlkZVR5cGluZygpOwogICAgaWYgKGRhdGEuZXJyb3IpIGFkZEJ1YmJsZSgiZXJyb3IiLCBkYXRhLmVycm9yKTsKICAgIGVsc2V7CiAgICAgIGNvbnN0IHR4dCA9IGRhdGEudGV4dCB8fCAiIjsKICAgICAgYWRkQnViYmxlKCJkaW5vIiwgdHh0KTsKICAgICAgc3RhdGUubWVzc2FnZXMucHVzaCh7IHJvbGU6ImFzc2lzdGFudCIsIGNvbnRlbnQ6dHh0IH0pOwogICAgICBzcGVhayh0eHQpOwogICAgICByZW5kZXJBY3Rpb25zKG51bGwsIHR4dCk7CiAgICB9CiAgfWNhdGNoKGUpeyBoaWRlVHlwaW5nKCk7IGFkZEJ1YmJsZSgiZXJyb3IiLCJOZXR6d2Vya2ZlaGxlcjogIitlLm1lc3NhZ2UpOyB9CiAgZmluYWxseXsgc2V0QnVzeShmYWxzZSk7IH0KfQpmdW5jdGlvbiBxdWlja1BsYW4oKXsgc2ltcGxlQWN0aW9uKCIvYXBpL3BsYW4iKTsgfQpmdW5jdGlvbiBxdWlja1RvZGF5KCl7IHNpbXBsZUFjdGlvbigiL2FwaS90YWciKTsgfQoKLy8gTGVybmVuIC0+IHZlcmRpY2h0ZXQgR2VzcHLDpGNoIHp1IEZha3Rlbgphc3luYyBmdW5jdGlvbiBxdWlja0xlYXJuKCl7CiAgaWYgKHN0YXRlLmJ1c3kpIHJldHVybjsKICBpZiAoIXN0YXRlLm1lc3NhZ2VzLmxlbmd0aCl7IGFkZEJ1YmJsZSgiaW5mbyIsIldpciBoYWJlbiBub2NoIG5pY2h0IGdlcmVkZXQg4oCUIG5pY2h0cyB6dSBsZXJuZW4uIPCfmIkiKTsgcmV0dXJuOyB9CiAgc2V0QnVzeSh0cnVlKTsKICB0cnl7CiAgICBjb25zdCBkYXRhID0gYXdhaXQgYXBpKCIvYXBpL2xlYXJuIiwgIlBPU1QiLCB7IG1lc3NhZ2VzOiBzdGF0ZS5tZXNzYWdlcyB9KTsKICAgIGhpZGVUeXBpbmcoKTsKICAgIGlmIChkYXRhLmVycm9yKSBhZGRCdWJibGUoImVycm9yIiwgZGF0YS5lcnJvcik7CiAgICBlbHNlIGFkZEJ1YmJsZSgiaW5mbyIsIGBHZW1lcmt0ISBEaW5vIGtlbm50IGpldHp0ICR7ZGF0YS5jb3VudCA/PyAwfSBGYWt0ZW4uIPCfp6BgKTsKICB9Y2F0Y2goZSl7IGhpZGVUeXBpbmcoKTsgYWRkQnViYmxlKCJlcnJvciIsIk5ldHp3ZXJrZmVobGVyOiAiK2UubWVzc2FnZSk7IH0KICBmaW5hbGx5eyBzZXRCdXN5KGZhbHNlKTsgfQp9CgovLyBSYXQgZGVyIEtJcyAtPiBuaW1tdCBha3R1ZWxsZW4gRWluZ2FiZXRleHQgYWxzIEZyYWdlCmFzeW5jIGZ1bmN0aW9uIHF1aWNrQ291bmNpbCgpewogIGlmIChzdGF0ZS5idXN5KSByZXR1cm47CiAgY29uc3QgZnJhZ2UgPSBpbnB1dEVsLnZhbHVlLnRyaW0oKTsKICBpZiAoIWZyYWdlKXsgYWRkQnViYmxlKCJpbmZvIiwiU2NocmVpYiB6dWVyc3QgZGVpbmUgRnJhZ2UgaW5zIEZlbGQsIGRhbm4gwrtSYXQgZGVyIEtJc8KrLiDwn6egIik7IHJldHVybjsgfQogIGlucHV0RWwudmFsdWU9IiI7IGF1dG9Hcm93KCk7CiAgYWRkQnViYmxlKCJ1c2VyIiwgZnJhZ2UpOwoKICBzZXRCdXN5KHRydWUpOwogIHRyeXsKICAgIGNvbnN0IGRhdGEgPSBhd2FpdCBhcGkoIi9hcGkvY291bmNpbCIsICJQT1NUIiwgeyBtZXNzYWdlczogc3RhdGUubWVzc2FnZXMsIGZyYWdlIH0pOwogICAgaGlkZVR5cGluZygpOwogICAgaWYgKGRhdGEuZXJyb3IpeyBhZGRCdWJibGUoImVycm9yIiwgZGF0YS5lcnJvcik7IHNldEJ1c3koZmFsc2UpOyByZXR1cm47IH0KICAgIGNvbnN0IGFuc3dlcnMgPSBkYXRhLmFuc3dlcnMgfHwge307CiAgICAvLyBSZWloZW5mb2xnZTogQ2xhdWRlLCBDaGF0R1BULCBHZW1pbmkgKGZhbGxzIHZvcmhhbmRlbikKICAgIFsiQ2xhdWRlIiwiQ2hhdEdQVCIsIkdlbWluaSJdLmZvckVhY2gobmFtZT0+ewogICAgICBpZiAoYW5zd2Vyc1tuYW1lXSAhPSBudWxsKSBhZGRCdWJibGUoImNvdW5jaWwiLCBhbnN3ZXJzW25hbWVdLCAi4pa4ICIrbmFtZSk7CiAgICB9KTsKICAgIC8vIGV2dGwuIHdlaXRlcmUgdW5iZWthbm50ZSBTY2hsw7xzc2VsCiAgICBPYmplY3Qua2V5cyhhbnN3ZXJzKS5mb3JFYWNoKG5hbWU9PnsKICAgICAgaWYgKCFbIkNsYXVkZSIsIkNoYXRHUFQiLCJHZW1pbmkiXS5pbmNsdWRlcyhuYW1lKSkgYWRkQnViYmxlKCJjb3VuY2lsIiwgYW5zd2Vyc1tuYW1lXSwgIuKWuCAiK25hbWUpOwogICAgfSk7CiAgICBpZiAoZGF0YS5zeW50aGVzZSl7CiAgICAgIGFkZEJ1YmJsZSgic3ludGgiLCBkYXRhLnN5bnRoZXNlLCAi4pymIERpbm9zIEZheml0Iik7CiAgICAgIHN0YXRlLm1lc3NhZ2VzLnB1c2goeyByb2xlOiJhc3Npc3RhbnQiLCBjb250ZW50OmRhdGEuc3ludGhlc2UgfSk7CiAgICAgIHNwZWFrKGRhdGEuc3ludGhlc2UpOwogICAgICByZW5kZXJBY3Rpb25zKG51bGwsIGRhdGEuc3ludGhlc2UpOwogICAgfQogIH1jYXRjaChlKXsgaGlkZVR5cGluZygpOyBhZGRCdWJibGUoImVycm9yIiwiTmV0endlcmtmZWhsZXI6ICIrZS5tZXNzYWdlKTsgfQogIGZpbmFsbHl7IHNldEJ1c3koZmFsc2UpOyB9Cn0KCi8vIFRlYW0tQXVmdHJhZyAtPiBQbGFuZXIgKyBTcGV6aWFsaXN0ZW4gKyBEaW5vcyBQbGFuIChuaW1tdCBFaW5nYWJldGV4dCBhbHMgQXVmZ2FiZSkKYXN5bmMgZnVuY3Rpb24gcXVpY2tUZWFtKCl7CiAgaWYgKHN0YXRlLmJ1c3kpIHJldHVybjsKICBjb25zdCB0YXNrID0gaW5wdXRFbC52YWx1ZS50cmltKCk7CiAgaWYgKCF0YXNrKXsgYWRkQnViYmxlKCJpbmZvIiwiU2NocmVpYiBkZWluZSBBdWZnYWJlIGlucyBGZWxkICh6LkIuIMK7aG9sIG1pciAzIG5ldWUgS3VuZGVuIGRpZXNlIFdvY2hlwqspLCBkYW5uIMK7VGVhbS1BdWZ0cmFnwqsuIPCfpJYiKTsgcmV0dXJuOyB9CiAgaW5wdXRFbC52YWx1ZT0iIjsgYXV0b0dyb3coKTsKICBhZGRCdWJibGUoInVzZXIiLCB0YXNrKTsKICBhZGRCdWJibGUoImluZm8iLCJEaW5vIHJ1ZnQgc2VpbiBUZWFtIHp1c2FtbWVuIPCfpJYg4oCUIFBsYW5lciwgU3BlemlhbGlzdGVuIHVuZCBhbSBFbmRlIERpbm9zIFBsYW4uIERhcyBkYXVlcnQgZWluZW4gTW9tZW50LCB3ZWlsIG1laHJlcmUgbmFjaGVpbmFuZGVyIGFyYmVpdGVu4oCmIik7CgogIHNldEJ1c3kodHJ1ZSk7CiAgdHJ5ewogICAgY29uc3QgZGF0YSA9IGF3YWl0IGFwaSgiL2FwaS90ZWFtIiwgIlBPU1QiLCB7IHRhc2ssIG1lc3NhZ2VzOiBzdGF0ZS5tZXNzYWdlcyB9KTsKICAgIGhpZGVUeXBpbmcoKTsKICAgIGlmIChkYXRhLmVycm9yICYmICEoZGF0YS5zdGVwcyAmJiBkYXRhLnN0ZXBzLmxlbmd0aCkpeyBhZGRCdWJibGUoImVycm9yIiwgZGF0YS5lcnJvcik7IHNldEJ1c3koZmFsc2UpOyByZXR1cm47IH0KICAgIChkYXRhLnN0ZXBzIHx8IFtdKS5mb3JFYWNoKHM9PnsKICAgICAgYWRkQnViYmxlKCJjb3VuY2lsIiwgcy5vdXRwdXQsIChzLmVtb2ppfHwi4oCiIikrIiAiK3MubmFtZSsiIOKAlCAiK3MudGFzayk7CiAgICB9KTsKICAgIGlmIChkYXRhLmZpbmFsKXsKICAgICAgYWRkQnViYmxlKCJzeW50aCIsIGRhdGEuZmluYWwsICLinKYgRGlub3MgUGxhbiAoVGVhbS1FcmdlYm5pcykiKTsKICAgICAgc3RhdGUubWVzc2FnZXMucHVzaCh7IHJvbGU6ImFzc2lzdGFudCIsIGNvbnRlbnQ6ZGF0YS5maW5hbCB9KTsKICAgICAgc3BlYWsoZGF0YS5maW5hbCk7CiAgICAgIHJlbmRlckFjdGlvbnMobnVsbCwgZGF0YS5maW5hbCk7CiAgICB9IGVsc2UgaWYgKGRhdGEuZXJyb3IpewogICAgICBhZGRCdWJibGUoImVycm9yIiwgZGF0YS5lcnJvcik7CiAgICB9CiAgfWNhdGNoKGUpeyBoaWRlVHlwaW5nKCk7IGFkZEJ1YmJsZSgiZXJyb3IiLCJOZXR6d2Vya2ZlaGxlcjogIitlLm1lc3NhZ2UpOyB9CiAgZmluYWxseXsgc2V0QnVzeShmYWxzZSk7IH0KfQoKLy8gQmVpbSBTdGFydDogcHLDvGZlbiwgb2IgZGllIEdvdmVlLUxhbXBlbiB2ZXJidW5kZW4gc2luZAphc3luYyBmdW5jdGlvbiBjaGVja0dvdmVlKCl7CiAgdHJ5ewogICAgY29uc3QgZyA9IGF3YWl0IGFwaSgiL2FwaS9nb3ZlZSIpOwogICAgaWYgKGcuY29ubmVjdGVkKXsKICAgICAgYWRkQnViYmxlKCJpbmZvIiwgYPCfkqEgR292ZWUgdmVyYnVuZGVuIOKAlCAke2cuY291bnR9IExhbXBlKG4pIGJlcmVpdDogJHsoZy5uYW1lc3x8W10pLmpvaW4oIiwgIil9YCk7CiAgICB9IGVsc2UgewogICAgICBhZGRCdWJibGUoImluZm8iLCAi8J+SoSBHb3ZlZS1TY2hsw7xzc2VsIGlzdCBkYSwgYWJlciBkaWUgVmVyYmluZHVuZyBrbGVtbXQ6ICIgKyAoZy5lcnJvciB8fCAidW5iZWthbm50IikpOwogICAgfQogIH1jYXRjaChlKXsgLyogc3RpbGwgKi8gfQp9CgovLyBXZWItUmVjaGVyY2hlIC0+IERpbm8gc2NoYXV0IGltIEludGVybmV0IG5hY2ggKG5pbW10IEVpbmdhYmV0ZXh0IGFscyBGcmFnZSkKYXN5bmMgZnVuY3Rpb24gcXVpY2tXZWIoKXsKICBpZiAoc3RhdGUuYnVzeSkgcmV0dXJuOwogIGNvbnN0IGZyYWdlID0gaW5wdXRFbC52YWx1ZS50cmltKCk7CiAgaWYgKCFmcmFnZSl7IGFkZEJ1YmJsZSgiaW5mbyIsIlNjaHJlaWIgZGVpbmUgRnJhZ2UgaW5zIEZlbGQsIGRhbm4gwrtXZWItUmVjaGVyY2hlwqsuIPCflI4iKTsgcmV0dXJuOyB9CiAgaW5wdXRFbC52YWx1ZT0iIjsgYXV0b0dyb3coKTsKICBhZGRCdWJibGUoInVzZXIiLCBmcmFnZSk7CiAgYWRkQnViYmxlKCJpbmZvIiwiRGlubyBzY2hhdXQgaW0gV2ViIG5hY2jigKYg8J+UjiIpOwogIHNldEJ1c3kodHJ1ZSk7CiAgdHJ5ewogICAgY29uc3QgZGF0YSA9IGF3YWl0IGFwaSgiL2FwaS93ZWIiLCAiUE9TVCIsIHsgZnJhZ2UgfSk7CiAgICBoaWRlVHlwaW5nKCk7CiAgICBpZiAoZGF0YS5lcnJvcil7IGFkZEJ1YmJsZSgiZXJyb3IiLCBkYXRhLmVycm9yKTsgfQogICAgZWxzZSB7CiAgICAgIGNvbnN0IHR4dCA9IGRhdGEudGV4dCB8fCAiIjsKICAgICAgY29uc3Qgc2hvd24gPSBzdHJpcEFjdGlvbkxpbmVzKHR4dCkgfHwgdHh0OwogICAgICBhZGRCdWJibGUoImRpbm8iLCBzaG93bik7CiAgICAgIHN0YXRlLm1lc3NhZ2VzLnB1c2goeyByb2xlOiJhc3Npc3RhbnQiLCBjb250ZW50OnR4dCB9KTsKICAgICAgc3BlYWsoc2hvd24pOwogICAgICByZW5kZXJBY3Rpb25zKG51bGwsIHR4dCk7CiAgICB9CiAgfWNhdGNoKGUpeyBoaWRlVHlwaW5nKCk7IGFkZEJ1YmJsZSgiZXJyb3IiLCJOZXR6d2Vya2ZlaGxlcjogIitlLm1lc3NhZ2UpOyB9CiAgZmluYWxseXsgc2V0QnVzeShmYWxzZSk7IH0KfQoKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09Ci8vICBFaW5nYWJlZmVsZDogQXV0by1Hcm93ICsgVGFzdGF0dXIKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09CmZ1bmN0aW9uIGF1dG9Hcm93KCl7CiAgaW5wdXRFbC5zdHlsZS5oZWlnaHQgPSAiYXV0byI7CiAgaW5wdXRFbC5zdHlsZS5oZWlnaHQgPSBNYXRoLm1pbihpbnB1dEVsLnNjcm9sbEhlaWdodCwgMTQwKSArICJweCI7Cn0KaW5wdXRFbC5hZGRFdmVudExpc3RlbmVyKCJpbnB1dCIsIGF1dG9Hcm93KTsKaW5wdXRFbC5hZGRFdmVudExpc3RlbmVyKCJrZXlkb3duIiwgKGUpPT57CiAgaWYgKGUua2V5ID09PSAiRW50ZXIiICYmICFlLnNoaWZ0S2V5KXsgZS5wcmV2ZW50RGVmYXVsdCgpOyBzZW5kKCk7IH0KfSk7CgovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KLy8gIFNwcmFjaGF1c2dhYmUgKHNwZWVjaFN5bnRoZXNpcykKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09CmxldCBhbGxWb2ljZXMgPSBbXTsKbGV0IHZvaWNlREUgPSBudWxsOyAgICAgICAgLy8gYmVzdGUgZGV1dHNjaGUgU3RpbW1lIChEaW5vIHNwcmljaHQgRGV1dHNjaCkKbGV0IHZvaWNlRU4gPSBudWxsOyAgICAgICAgLy8gYmVzdGUgZW5nbGlzY2hlIFN0aW1tZQpsZXQgc2VsZWN0ZWRWb2ljZSA9IG51bGw7ICAvLyBtYW51ZWxsIGdld2FlaGx0ZSBTdGltbWUgKHNvbnN0IGF1dG9tYXRpc2NoKQpsZXQgdm9pY2VNYW51YWwgPSBmYWxzZTsKCi8vIEJld2VydHVuZzogd2llIG5hdHVlcmxpY2gvaG9jaHdlcnRpZyBpc3QgZGllIFN0aW1tZSBpbiBkZXIgZ2V3dWVuc2NodGVuIFNwcmFjaGU/Ci8vIFdpY2h0aWc6IGVpbmUgRU5HTElTQ0hFIFN0aW1tZSwgZGllIERFVVRTQ0ggbGllc3QsIGtsaW5ndCBhYmdlaGFja3QgLT4gaGFydGUgU3RyYWZlLgpmdW5jdGlvbiB2b2ljZVJhbmsodiwgd2FudCl7CiAgY29uc3QgbGFuZyA9ICh2LmxhbmcgfHwgIiIpLnRvTG93ZXJDYXNlKCkucmVwbGFjZSgiXyIsICItIik7CiAgY29uc3QgbmFtZSA9ICh2Lm5hbWUgfHwgIiIpLnRvTG93ZXJDYXNlKCk7CiAgbGV0IHMgPSAwOwogIGlmIChsYW5nLnN0YXJ0c1dpdGgod2FudCkpIHMgKz0gMTQwOyAgICAgICAgICAvLyByaWNodGlnZSBTcHJhY2hlID0gZmx1ZXNzaWcKICBlbHNlIHMgLT0gMTIwOyAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgLy8gZmFsc2NoZSBTcHJhY2hlID0gYWJnZWhhY2t0CiAgaWYgKC9uYXR1cmFsfG5ldXJhbC8udGVzdChuYW1lKSkgcyArPSAxMjA7ICAgIC8vIEVkZ2UtTmV1cmFsLVN0aW1tZW46IGFtIG5hdHVlcmxpY2hzdGVuCiAgaWYgKC9vbmxpbmUvLnRlc3QobmFtZSkpICAgICAgICBzICs9IDcwOyAgICAgIC8vIE9ubGluZS1TdGltbWVuIGtsaW5nZW4gbmF0dWVybGljaGVyCiAgaWYgKC9nb29nbGUvLnRlc3QobmFtZSkpICAgICAgICBzICs9IDM1OyAgICAgIC8vIEdvb2dsZS1TdGltbWVuIGJlc3NlciBhbHMgYWx0ZSBsb2thbGUKICBpZiAod2FudCA9PT0gImRlIiAmJiAvKGthdGphfHNlcmFwaGluYXxoZWRkYXxnaXNlbGF8YW1hbGF8bWFybGVuZXxjaHJpc3RlbHxwZXRyYXxmZW1hbGV8ZnJhdSkvLnRlc3QobmFtZSkpIHMgKz0gNDU7CiAgaWYgKHdhbnQgPT09ICJlbiIgJiYgLyhzb25pYXxsaWJieXxoYXplbHxhcmlhfGplbm55fGVtbWF8ZmVtYWxlKS8udGVzdChuYW1lKSkgcyArPSA0NTsKICByZXR1cm4gczsKfQoKZnVuY3Rpb24gYmVzdFZvaWNlKHdhbnQpewogIGxldCBiZXN0ID0gbnVsbCwgYnMgPSAtMWU5OwogIGFsbFZvaWNlcy5mb3JFYWNoKHYgPT4geyBjb25zdCByID0gdm9pY2VSYW5rKHYsIHdhbnQpOyBpZiAociA+IGJzKXsgYnMgPSByOyBiZXN0ID0gdjsgfSB9KTsKICByZXR1cm4gYmVzdDsKfQoKZnVuY3Rpb24gYnVpbGRWb2ljZUxpc3QoKXsKICBpZiAoISgic3BlZWNoU3ludGhlc2lzIiBpbiB3aW5kb3cpKSByZXR1cm47CiAgYWxsVm9pY2VzID0gc3BlZWNoU3ludGhlc2lzLmdldFZvaWNlcygpIHx8IFtdOwogIGlmICghYWxsVm9pY2VzLmxlbmd0aCkgcmV0dXJuOwogIHZvaWNlREUgPSBiZXN0Vm9pY2UoImRlIik7CiAgdm9pY2VFTiA9IGJlc3RWb2ljZSgiZW4iKTsKICAvLyBEcm9wZG93bjogYmVzdGUgKGRldXRzY2hlLCBuYXR1ZXJsaWNoZSkgU3RpbW1lbiB6dWVyc3Q7ICJBdXRvbWF0aXNjaCIgZ2FueiBvYmVuCiAgY29uc3Qgc29ydGVkID0gYWxsVm9pY2VzLnNsaWNlKCkuc29ydCgoYSwgYikgPT4KICAgIE1hdGgubWF4KHZvaWNlUmFuayhiLCJkZSIpLCB2b2ljZVJhbmsoYiwiZW4iKSkgLSBNYXRoLm1heCh2b2ljZVJhbmsoYSwiZGUiKSwgdm9pY2VSYW5rKGEsImVuIikpKTsKICBjb25zdCBzZWwgPSAkKCJ2b2ljZVNlbGVjdCIpOwogIGlmIChzZWwpewogICAgc2VsLmlubmVySFRNTCA9ICIiOwogICAgY29uc3QgYXV0byA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoIm9wdGlvbiIpOwogICAgYXV0by52YWx1ZSA9ICJfX2F1dG9fXyI7IGF1dG8udGV4dENvbnRlbnQgPSAiQXV0b21hdGlzY2ggKGJlc3RlIFN0aW1tZSkiOwogICAgc2VsLmFwcGVuZENoaWxkKGF1dG8pOwogICAgc29ydGVkLmZvckVhY2godiA9PiB7CiAgICAgIGNvbnN0IG8gPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJvcHRpb24iKTsKICAgICAgby52YWx1ZSA9IHYudm9pY2VVUkk7CiAgICAgIG8udGV4dENvbnRlbnQgPSB2Lm5hbWUgKyAiICgiICsgdi5sYW5nICsgIikiOwogICAgICBzZWwuYXBwZW5kQ2hpbGQobyk7CiAgICB9KTsKICB9CiAgY29uc3Qgc2F2ZWQgPSBsb2NhbFN0b3JhZ2UuZ2V0SXRlbSgiZGlub192b2ljZSIpOwogIGlmIChzYXZlZCAmJiBzYXZlZCAhPT0gIl9fYXV0b19fIil7CiAgICBzZWxlY3RlZFZvaWNlID0gYWxsVm9pY2VzLmZpbmQodiA9PiB2LnZvaWNlVVJJID09PSBzYXZlZCkgfHwgbnVsbDsKICAgIHZvaWNlTWFudWFsID0gISFzZWxlY3RlZFZvaWNlOwogIH0gZWxzZSB7CiAgICBzZWxlY3RlZFZvaWNlID0gbnVsbDsgdm9pY2VNYW51YWwgPSBmYWxzZTsKICB9CiAgaWYgKHNlbCkgc2VsLnZhbHVlID0gKHZvaWNlTWFudWFsICYmIHNlbGVjdGVkVm9pY2UpID8gc2VsZWN0ZWRWb2ljZS52b2ljZVVSSSA6ICJfX2F1dG9fXyI7Cn0KCmZ1bmN0aW9uIG9uVm9pY2VTZWxlY3QoKXsKICBjb25zdCBzZWwgPSAkKCJ2b2ljZVNlbGVjdCIpOwogIGlmIChzZWwudmFsdWUgPT09ICJfX2F1dG9fXyIpewogICAgc2VsZWN0ZWRWb2ljZSA9IG51bGw7IHZvaWNlTWFudWFsID0gZmFsc2U7CiAgICBsb2NhbFN0b3JhZ2Uuc2V0SXRlbSgiZGlub192b2ljZSIsICJfX2F1dG9fXyIpOwogIH0gZWxzZSB7CiAgICBzZWxlY3RlZFZvaWNlID0gYWxsVm9pY2VzLmZpbmQodiA9PiB2LnZvaWNlVVJJID09PSBzZWwudmFsdWUpIHx8IG51bGw7CiAgICB2b2ljZU1hbnVhbCA9ICEhc2VsZWN0ZWRWb2ljZTsKICAgIGlmIChzZWxlY3RlZFZvaWNlKSBsb2NhbFN0b3JhZ2Uuc2V0SXRlbSgiZGlub192b2ljZSIsIHNlbGVjdGVkVm9pY2Uudm9pY2VVUkkpOwogIH0KICBjb25zdCBwcmV2ID0gc3RhdGUudm9pY2VPbjsgc3RhdGUudm9pY2VPbiA9IHRydWU7CiAgc3BlYWsoIkhhbGxvLCBpY2ggYmluIERpbm8sIGRlaW5lIGVpZ2VuZSBLSS4iKTsKICBzdGF0ZS52b2ljZU9uID0gcHJldjsKfQoKaWYgKCJzcGVlY2hTeW50aGVzaXMiIGluIHdpbmRvdyl7CiAgYnVpbGRWb2ljZUxpc3QoKTsKICBzcGVlY2hTeW50aGVzaXMub252b2ljZXNjaGFuZ2VkID0gYnVpbGRWb2ljZUxpc3Q7Cn0gZWxzZSB7CiAgJCgidm9pY2VCdG4iKS5zdHlsZS5kaXNwbGF5ID0gIm5vbmUiOwogIGNvbnN0IHZzID0gJCgidm9pY2VTZWxlY3QiKTsgaWYgKHZzKSB2cy5zdHlsZS5kaXNwbGF5ID0gIm5vbmUiOwp9CgpmdW5jdGlvbiB0b2dnbGVWb2ljZSgpewogIHN0YXRlLnZvaWNlT24gPSAhc3RhdGUudm9pY2VPbjsKICAkKCJ2b2ljZUJ0biIpLmNsYXNzTGlzdC50b2dnbGUoImFjdGl2ZSIsIHN0YXRlLnZvaWNlT24pOwogIGlmICghc3RhdGUudm9pY2VPbiAmJiAic3BlZWNoU3ludGhlc2lzIiBpbiB3aW5kb3cpeyBzcGVlY2hTeW50aGVzaXMuY2FuY2VsKCk7IHJldHVybjsgfQogIGlmIChzdGF0ZS52b2ljZU9uKSBzcGVhaygiU3ByYWNoYXVzZ2FiZSBha3Rpdi4iKTsKfQoKLy8gU3ByYWNoZSBkZXMgVGV4dGVzIGdyb2IgZXJrZW5uZW4gKERpbm8gc3ByaWNodCBzdGFuZGFyZG1hZXNzaWcgRGV1dHNjaCkuCmZ1bmN0aW9uIGRldGVjdExhbmcodGV4dCl7CiAgY29uc3QgdCA9ICh0ZXh0IHx8ICIiKS50b0xvd2VyQ2FzZSgpOwogIGlmICgvW8Okw7bDvMOfXS8udGVzdCh0KSkgcmV0dXJuICJkZSI7CiAgaWYgKC9cYih1bmR8aWNofG5pY2h0fGRlcnxkaWV8ZGFzfGlzdHxlaW58bWl0fGbDvHJ8YXVmfGRlaW58ZGVpbmV8d2lyfGhhc3R8bWFjaHxrdW5kZW58Z2VsZHx3b2NoZXxoZXV0ZSlcYi8udGVzdCh0KSkgcmV0dXJuICJkZSI7CiAgaWYgKC9cYih0aGV8eW91fGFuZHx5b3VyfHdpdGh8Zm9yfHRoaXN8dGhhdHxhcmV8bGV0fG1ha2V8bW9uZXkpXGIvLnRlc3QodCkpIHJldHVybiAiZW4iOwogIHJldHVybiAiZGUiOwp9CgovLyBUZXh0IHZvcmxlc2VmcmV1bmRsaWNoIG1hY2hlbjogRW1vamlzLCBNYXJrZG93biwgTGlua3MgJiBTeW1ib2xlIHJhdXMuCmZ1bmN0aW9uIGNsZWFuRm9yU3BlZWNoKHRleHQpewogIGxldCB0ID0gdGV4dCB8fCAiIjsKICB0ID0gdC5zcGxpdCgiXG4iKS5maWx0ZXIobG4gPT4gIS9cWz9ccypBS1RJT05ccypcXT9ccypbOlwtXT9ccypbYS16QS1aX8Okw7bDvF0rXHMqXHwvaS50ZXN0KGxuKSkuam9pbigiXG4iKTsgLy8gQUtUSU9OLVplaWxlbiBuaWNodCB2b3JsZXNlbgogIHQgPSB0LnJlcGxhY2UoL2BgYFtcc1xTXSo/YGBgL2csICIgIik7ICAgICAgICAgICAgICAgICAvLyBDb2RlYmxvZWNrZQogIHQgPSB0LnJlcGxhY2UoL2AoW15gXSopYC9nLCAiJDEiKTsgICAgICAgICAgICAgICAgICAgICAgLy8gSW5saW5lLUNvZGUKICB0ID0gdC5yZXBsYWNlKC8hP1xbKFteXF1dKilcXVwoW14pXSpcKS9nLCAiJDEiKTsgICAgICAgIC8vIE1hcmtkb3duLUxpbmtzIC0+IG51ciBUZXh0CiAgdCA9IHQucmVwbGFjZSgvaHR0cHM/OlwvXC9cUysvZywgIiAiKTsgICAgICAgICAgICAgICAgICAvLyBuYWNrdGUgVVJMcwogIHQgPSB0LnJlcGxhY2UoL1tccHtFeHRlbmRlZF9QaWN0b2dyYXBoaWN9XHV7MUYxRTZ9LVx1ezFGMUZGfe+4j+KDo10vZ3UsICIgIik7IC8vIEVtb2ppcwogIHQgPSB0LnJlcGxhY2UoL1sqXyM+fnxdL2csICIgIik7ICAgICAgICAgICAgICAgICAgICAgICAgLy8gTWFya2Rvd24tWmVpY2hlbgogIHQgPSB0LnJlcGxhY2UoLyhefFxuKVsgXHRdKltcLeKAk+KAosK3XStbIFx0XS9nLCAiJDEiKTsgICAgICAvLyBBdWZ6YWVobHVuZ3NwdW5rdGUKICB0ID0gdC5yZXBsYWNlKC/igqwvZywgIiBFdXJvIik7ICAgICAgICAgICAgICAgICAgICAgICAgICAgLy8gU3ltYm9sIHNhdWJlciBhdXNzcHJlY2hlbgogIHQgPSB0LnJlcGxhY2UoL1sgXHRdKy9nLCAiICIpLnJlcGxhY2UoL1xzKlxuXHMqL2csICIuICIpLnRyaW0oKTsKICByZXR1cm4gdDsKfQoKLy8gSW4ga3VyemUgSGFlcHBjaGVuIHRlaWxlbiAtPiBrZWluIEFic2NobmVpZGVuIGJlaSBsYW5nZW4gVGV4dGVuIChzb25zdCAiYWJnZWhhY2t0IikuCmZ1bmN0aW9uIHNwbGl0U3BlZWNoKHRleHQpewogIGNvbnN0IHBhcnRzID0gdGV4dC5zcGxpdCgvKD88PVtcLlwhXD9cOlw7XSlccysvKTsKICBjb25zdCBvdXQgPSBbXTsgbGV0IGJ1ZiA9ICIiOwogIHBhcnRzLmZvckVhY2gocCA9PiB7CiAgICBwID0gcC50cmltKCk7IGlmICghcCkgcmV0dXJuOwogICAgaWYgKChidWYgKyAiICIgKyBwKS50cmltKCkubGVuZ3RoIDw9IDE4MCkgYnVmID0gYnVmID8gYnVmICsgIiAiICsgcCA6IHA7CiAgICBlbHNlIHsgaWYgKGJ1Zikgb3V0LnB1c2goYnVmKTsgYnVmID0gcDsgfQogIH0pOwogIGlmIChidWYpIG91dC5wdXNoKGJ1Zik7CiAgcmV0dXJuIG91dDsKfQoKZnVuY3Rpb24gc3BlYWsodGV4dCwgb25Eb25lKXsKICBjb25zdCBkb25lID0gKCkgPT4geyB0cnl7IG9uRG9uZSAmJiBvbkRvbmUoKTsgfWNhdGNoKGUpe30gfTsKICBpZiAoIXN0YXRlLnZvaWNlT24gfHwgIXRleHQgfHwgISgic3BlZWNoU3ludGhlc2lzIiBpbiB3aW5kb3cpKXsgZG9uZSgpOyByZXR1cm47IH0KICBjb25zdCBjbGVhbiA9IGNsZWFuRm9yU3BlZWNoKHRleHQpOwogIGlmICghY2xlYW4peyBkb25lKCk7IHJldHVybjsgfQogIC8vIEF1dG9tYXRpc2NoIGRpZSB6dXIgU3ByYWNoZSBwYXNzZW5kZSBTdGltbWUgbmVobWVuIChlbmdsLiBTdGltbWUgKyBkdC4gVGV4dCA9IGFiZ2VoYWNrdCEpCiAgbGV0IHZvaWNlID0gc2VsZWN0ZWRWb2ljZTsKICBpZiAoIXZvaWNlTWFudWFsIHx8ICF2b2ljZSl7CiAgICB2b2ljZSA9IChkZXRlY3RMYW5nKGNsZWFuKSA9PT0gImVuIikgPyAodm9pY2VFTiB8fCB2b2ljZURFKSA6ICh2b2ljZURFIHx8IHZvaWNlRU4pOwogIH0KICB0cnl7CiAgICBzcGVlY2hTeW50aGVzaXMuY2FuY2VsKCk7CiAgICBjb25zdCBjaHVua3MgPSBzcGxpdFNwZWVjaChjbGVhbik7CiAgICBpZiAoIWNodW5rcy5sZW5ndGgpeyBkb25lKCk7IHJldHVybjsgfQogICAgY2h1bmtzLmZvckVhY2goKGMsIGkpID0+IHsKICAgICAgY29uc3QgdSA9IG5ldyBTcGVlY2hTeW50aGVzaXNVdHRlcmFuY2UoYyk7CiAgICAgIGlmICh2b2ljZSl7IHUudm9pY2UgPSB2b2ljZTsgdS5sYW5nID0gdm9pY2UubGFuZzsgfQogICAgICBlbHNlIHsgdS5sYW5nID0gZGV0ZWN0TGFuZyhjbGVhbikgPT09ICJlbiIgPyAiZW4tR0IiIDogImRlLURFIjsgfQogICAgICB1LnJhdGUgPSAxLjA7ICAgICAvLyBuYXR1ZXJsaWNoZXMgVGVtcG8KICAgICAgdS5waXRjaCA9IDEuMDM7ICAgLy8gbGVpY2h0IGhvZWhlciAtPiBydWhpZ2UgS0ktQXNzaXN0ZW50aW4KICAgICAgaWYgKGkgPT09IDApIHUub25zdGFydCA9ICgpID0+IHNldFNwZWFraW5nKHRydWUpOwogICAgICBpZiAoaSA9PT0gY2h1bmtzLmxlbmd0aCAtIDEpIHUub25lbmQgPSAoKSA9PiB7IHNldFNwZWFraW5nKGZhbHNlKTsgZG9uZSgpOyB9OwogICAgICB1Lm9uZXJyb3IgPSAoKSA9PiB7IHNldFNwZWFraW5nKGZhbHNlKTsgaWYgKGkgPT09IGNodW5rcy5sZW5ndGggLSAxKSBkb25lKCk7IH07CiAgICAgIHNwZWVjaFN5bnRoZXNpcy5zcGVhayh1KTsKICAgIH0pOwogIH1jYXRjaChlKXsgZG9uZSgpOyB9Cn0KCi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQovLyAgU3ByYWNoZXJrZW5udW5nIChTcGVlY2hSZWNvZ25pdGlvbikKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09CmxldCByZWNvZyA9IG51bGwsIGxpc3RlbmluZyA9IGZhbHNlOwooZnVuY3Rpb24gaW5pdE1pYygpewogIGNvbnN0IFNSID0gd2luZG93LlNwZWVjaFJlY29nbml0aW9uIHx8IHdpbmRvdy53ZWJraXRTcGVlY2hSZWNvZ25pdGlvbjsKICBpZiAoIVNSKXsgJCgibWljQnRuIikuc3R5bGUuZGlzcGxheSA9ICJub25lIjsgcmV0dXJuOyB9IC8vIG5pY2h0IHVudGVyc3TDvHR6dCAtPiBlbGVnYW50IGF1c2JsZW5kZW4KICByZWNvZyA9IG5ldyBTUigpOwogIHJlY29nLmxhbmcgPSAiZGUtREUiOwogIHJlY29nLmludGVyaW1SZXN1bHRzID0gZmFsc2U7CiAgcmVjb2cubWF4QWx0ZXJuYXRpdmVzID0gMTsKICByZWNvZy5vbnJlc3VsdCA9IChlKT0+ewogICAgY29uc3QgdCA9IGUucmVzdWx0c1swXVswXS50cmFuc2NyaXB0OwogICAgaW5wdXRFbC52YWx1ZSA9IChpbnB1dEVsLnZhbHVlID8gaW5wdXRFbC52YWx1ZSsiICIgOiAiIikgKyB0OwogICAgYXV0b0dyb3coKTsgaW5wdXRFbC5mb2N1cygpOwogIH07CiAgcmVjb2cub25lcnJvciA9ICgpPT4gc3RvcE1pYygpOwogIHJlY29nLm9uZW5kID0gKCk9PiBzdG9wTWljKCk7Cn0pKCk7CmZ1bmN0aW9uIHRvZ2dsZU1pYygpewogIGlmICghcmVjb2cpIHJldHVybjsKICBpZiAobGlzdGVuaW5nKXsgcmVjb2cuc3RvcCgpOyBzdG9wTWljKCk7IH0KICBlbHNlIHsgdHJ5eyByZWNvZy5zdGFydCgpOyBsaXN0ZW5pbmcgPSB0cnVlOyAkKCJtaWNCdG4iKS5jbGFzc0xpc3QuYWRkKCJsaXN0ZW5pbmciKTsgfWNhdGNoKGUpeyBzdG9wTWljKCk7IH0gfQp9CmZ1bmN0aW9uIHN0b3BNaWMoKXsgbGlzdGVuaW5nID0gZmFsc2U7ICQoIm1pY0J0biIpLmNsYXNzTGlzdC5yZW1vdmUoImxpc3RlbmluZyIpOyB9CgovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KLy8gIEZyZWlzcHJlY2gtTW9kdXMgKERhdWVyLU1pa3JvICsgV2Vja3dvcnQgIkhleSBEaW5vIikKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09CmNvbnN0IGhmID0geyBvbjpmYWxzZSwgcmVjb2c6bnVsbCwgc3BlYWtpbmc6ZmFsc2UgfTsKY29uc3QgV0FLRV9SRSA9IC9cYihoZXl8aGVqfGhlfG9rfG9rYXl8aGFsbG98aGl8eW8pXHMrKGRpbm98ZHlub3xkZWlub3x0aW5vfGRpbmEpXGIvaTsKZnVuY3Rpb24gd2FrZU9ubHkoKXsgcmV0dXJuIGxvY2FsU3RvcmFnZS5nZXRJdGVtKCJkaW5vX3dha2UiKSAhPT0gIjAiOyB9IC8vIFN0YW5kYXJkOiBudXIgYXVmICJIZXkgRGlubyIKCmZ1bmN0aW9uIGJ1aWxkSEZSZWNvZygpewogIGNvbnN0IFNSID0gd2luZG93LlNwZWVjaFJlY29nbml0aW9uIHx8IHdpbmRvdy53ZWJraXRTcGVlY2hSZWNvZ25pdGlvbjsKICBpZiAoIVNSKSByZXR1cm4gbnVsbDsKICBjb25zdCByID0gbmV3IFNSKCk7CiAgci5sYW5nID0gImRlLURFIjsgci5jb250aW51b3VzID0gdHJ1ZTsgci5pbnRlcmltUmVzdWx0cyA9IHRydWU7IHIubWF4QWx0ZXJuYXRpdmVzID0gMTsKICByLm9ucmVzdWx0ID0gb25IRlJlc3VsdDsKICByLm9uZXJyb3IgPSAoKT0+e307ICAgLy8gYmVpIEZlaGxlciBlaW5mYWNoIHdlaXRlciAob25lbmQgc3RhcnRldCBuZXUpCiAgci5vbmVuZCA9ICgpPT57IGlmIChoZi5vbiAmJiAhaGYuc3BlYWtpbmcpeyB0cnl7IHIuc3RhcnQoKTsgfWNhdGNoKGUpe30gfSB9OwogIHJldHVybiByOwp9CgpmdW5jdGlvbiB0b2dnbGVIYW5kc0ZyZWUoKXsKICBjb25zdCBTUiA9IHdpbmRvdy5TcGVlY2hSZWNvZ25pdGlvbiB8fCB3aW5kb3cud2Via2l0U3BlZWNoUmVjb2duaXRpb247CiAgaWYgKCFTUil7IGFkZEJ1YmJsZSgiaW5mbyIsIkRlaW4gQnJvd3NlciBrYW5uIGtlaW4gRGF1ZXItTWlrcm8uIE5pbW0gQ2hyb21lIG9kZXIgRWRnZS4g8J+OpyIpOyByZXR1cm47IH0KICBoZi5vbiA9ICFoZi5vbjsKICAkKCJoZkJ0biIpLmNsYXNzTGlzdC50b2dnbGUoImxpc3RlbmluZyIsIGhmLm9uKTsKICBpZiAoaGYub24pewogICAgaWYgKCFoZi5yZWNvZykgaGYucmVjb2cgPSBidWlsZEhGUmVjb2coKTsKICAgIHN0YXRlLnZvaWNlT24gPSB0cnVlOyAkKCJ2b2ljZUJ0biIpLmNsYXNzTGlzdC5hZGQoImFjdGl2ZSIpOyAgLy8gQW50d29ydCBrb21tdCBwZXIgU3ByYWNoZQogICAgaGYuc3BlYWtpbmcgPSBmYWxzZTsKICAgIHRyeXsgaGYucmVjb2cuc3RhcnQoKTsgfWNhdGNoKGUpe30KICAgIGFkZEJ1YmJsZSgiaW5mbyIsIHdha2VPbmx5KCkKICAgICAgPyAiRnJlaXNwcmVjaC1Nb2R1cyBBTiDwn46nIOKAlCBzYWcgwrtIZXkgRGlub8KrIHVuZCBkYW5uIGRlaW5lIEZyYWdlLiIKICAgICAgOiAiRnJlaXNwcmVjaC1Nb2R1cyBBTiDwn46nIOKAlCBzcHJpY2ggZWluZmFjaCwgaWNoIGjDtnJlIGR1cmNoZ2VoZW5kIHp1LiIpOwogICAgc3BlYWsoIkZyZWlzcHJlY2ggYW4uIEljaCBow7ZyZSB6dS4iKTsKICB9IGVsc2UgewogICAgdHJ5eyBoZi5yZWNvZyAmJiBoZi5yZWNvZy5zdG9wKCk7IH1jYXRjaChlKXt9CiAgICBhZGRCdWJibGUoImluZm8iLCJGcmVpc3ByZWNoLU1vZHVzIGF1cy4g8J+OpCIpOwogIH0KfQoKZnVuY3Rpb24gb25IRlJlc3VsdChlKXsKICBpZiAoIWhmLm9uIHx8IGhmLnNwZWFraW5nIHx8IHN0YXRlLmJ1c3kpIHJldHVybjsKICBsZXQgZmluYWxUZXh0ID0gIiI7CiAgZm9yIChsZXQgaT1lLnJlc3VsdEluZGV4OyBpPGUucmVzdWx0cy5sZW5ndGg7IGkrKyl7CiAgICBpZiAoZS5yZXN1bHRzW2ldLmlzRmluYWwpIGZpbmFsVGV4dCArPSBlLnJlc3VsdHNbaV1bMF0udHJhbnNjcmlwdCArICIgIjsKICB9CiAgZmluYWxUZXh0ID0gZmluYWxUZXh0LnRyaW0oKTsKICBpZiAoZmluYWxUZXh0Lmxlbmd0aCA8IDIpIHJldHVybjsKICBjb25zdCBtID0gZmluYWxUZXh0Lm1hdGNoKFdBS0VfUkUpOwogIGxldCBjbWQgPSBmaW5hbFRleHQ7CiAgaWYgKHdha2VPbmx5KCkgJiYgIW0pIHJldHVybjsgICAvLyBvaG5lICJIZXkgRGlubyIgaWdub3JpZXJlbgogIGlmIChtKXsgY21kID0gZmluYWxUZXh0LnNsaWNlKGZpbmFsVGV4dC50b0xvd2VyQ2FzZSgpLmluZGV4T2YobVswXS50b0xvd2VyQ2FzZSgpKSArIG1bMF0ubGVuZ3RoKTsgfQogIGNtZCA9IGNtZC5yZXBsYWNlKC9eW1xzLDouIT/igJMtXSsvLCAiIikudHJpbSgpOwogIGlmICghY21kKXsgaWYgKG0peyBoZi5zcGVha2luZyA9IHRydWU7IHRyeXsgaGYucmVjb2cuc3RvcCgpOyB9Y2F0Y2goXyl7fSBzcGVhaygiSmEsIEJvc3M/IiwgcmVzdW1lSEYpOyB9IHJldHVybjsgfQogIHZvaWNlU2VuZChjbWQpOwp9CgpmdW5jdGlvbiByZXN1bWVIRigpewogIGhmLnNwZWFraW5nID0gZmFsc2U7CiAgaWYgKGhmLm9uKXsgdHJ5eyBoZi5yZWNvZy5zdGFydCgpOyB9Y2F0Y2goZSl7fSB9Cn0KCmFzeW5jIGZ1bmN0aW9uIHZvaWNlU2VuZCh0ZXh0KXsKICBpZiAoc3RhdGUuYnVzeSkgcmV0dXJuOwogIGhmLnNwZWFraW5nID0gdHJ1ZTsgICAgICAgICAgICAgICAgICAgICAgICAgIC8vIE1pYy1WZXJhcmJlaXR1bmcgcGF1c2llcmVuCiAgdHJ5eyBoZi5yZWNvZyAmJiBoZi5yZWNvZy5zdG9wKCk7IH1jYXRjaChlKXt9CiAgYWRkQnViYmxlKCJ1c2VyIiwgdGV4dCk7CiAgc3RhdGUubWVzc2FnZXMucHVzaCh7IHJvbGU6InVzZXIiLCBjb250ZW50OnRleHQgfSk7CiAgc2V0QnVzeSh0cnVlKTsKICBsZXQgcmVzdW1lZCA9IGZhbHNlOwogIGNvbnN0IHJlc3VtZU9uY2UgPSAoKT0+eyBpZiAoIXJlc3VtZWQpeyByZXN1bWVkID0gdHJ1ZTsgcmVzdW1lSEYoKTsgfSB9OwogIHNldFRpbWVvdXQocmVzdW1lT25jZSwgMjAwMDApOyAgICAgICAgICAgICAgIC8vIFNpY2hlcmhlaXRzbmV0ejogc3BhZXRlc3RlbnMgbmFjaCAyMHMgd2llZGVyIHp1aG9lcmVuCiAgdHJ5ewogICAgY29uc3QgZGF0YSA9IGF3YWl0IGFwaSgiL2FwaS9jaGF0IiwgIlBPU1QiLCB7IG1lc3NhZ2VzOiBzdGF0ZS5tZXNzYWdlcyB9KTsKICAgIGhpZGVUeXBpbmcoKTsKICAgIGlmIChkYXRhLmVycm9yKXsgYWRkQnViYmxlKCJlcnJvciIsIGRhdGEuZXJyb3IpOyBzdGF0ZS5tZXNzYWdlcy5wb3AoKTsgcmVzdW1lT25jZSgpOyB9CiAgICBlbHNlIHsKICAgICAgY29uc3QgcmVwbHkgPSBkYXRhLnJlcGx5IHx8ICIiOwogICAgICBjb25zdCBzaG93biA9IHN0cmlwQWN0aW9uTGluZXMocmVwbHkpIHx8IHJlcGx5OwogICAgICBhZGRCdWJibGUoImRpbm8iLCBzaG93bik7CiAgICAgIHN0YXRlLm1lc3NhZ2VzLnB1c2goeyByb2xlOiJhc3Npc3RhbnQiLCBjb250ZW50OnJlcGx5IH0pOwogICAgICByZW5kZXJBY3Rpb25zKGRhdGEuYWN0aW9ucywgcmVwbHkpOwogICAgICBzcGVhayhzaG93biwgcmVzdW1lT25jZSk7ICAgICAgICAgICAgICAgIC8vIHNwcmVjaGVuLCBkYW5hY2ggd2llZGVyIHp1aG9lcmVuCiAgICB9CiAgfWNhdGNoKGUpeyBoaWRlVHlwaW5nKCk7IGFkZEJ1YmJsZSgiZXJyb3IiLCJOZXR6d2Vya2ZlaGxlcjogIitlLm1lc3NhZ2UpOyBzdGF0ZS5tZXNzYWdlcy5wb3AoKTsgcmVzdW1lT25jZSgpOyB9CiAgZmluYWxseXsgc2V0QnVzeShmYWxzZSk7IH0KfQoKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09Ci8vICBQYW5lbHMgKFNsaWRlLU92ZXIpCi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQpmdW5jdGlvbiBvcGVuUGFuZWwobmFtZSl7CiAgY2xvc2VQYW5lbHMoKTsKICAkKCJvdmVybGF5IikuY2xhc3NMaXN0LmFkZCgib3BlbiIpOwogIGNvbnN0IHAgPSAkKCJwYW5lbC0iK25hbWUpOwogIGlmIChwKSBwLmNsYXNzTGlzdC5hZGQoIm9wZW4iKTsKICBpZiAobmFtZSA9PT0gInNldHRpbmdzIikgbG9hZFNldHRpbmdzKCk7CiAgaWYgKG5hbWUgPT09ICJjdXN0b21lcnMiKSBsb2FkQ3VzdG9tZXJzKCk7CiAgaWYgKG5hbWUgPT09ICJtZW1vcnkiKSBsb2FkTWVtb3J5KCk7CiAgaWYgKG5hbWUgPT09ICJwYyIpIGxvYWRQQygpOwp9CmZ1bmN0aW9uIGNsb3NlUGFuZWxzKCl7CiAgJCgib3ZlcmxheSIpLmNsYXNzTGlzdC5yZW1vdmUoIm9wZW4iKTsKICBkb2N1bWVudC5xdWVyeVNlbGVjdG9yQWxsKCIucGFuZWwiKS5mb3JFYWNoKHAgPT4gcC5jbGFzc0xpc3QucmVtb3ZlKCJvcGVuIikpOwp9CmRvY3VtZW50LmFkZEV2ZW50TGlzdGVuZXIoImtleWRvd24iLCBlID0+IHsgaWYgKGUua2V5ID09PSAiRXNjYXBlIikgY2xvc2VQYW5lbHMoKTsgfSk7CgovLyAtLS0tLS0tLS0tIEVpbnN0ZWxsdW5nZW4gLS0tLS0tLS0tLQphc3luYyBmdW5jdGlvbiBsb2FkU2V0dGluZ3MoKXsKICBjb25zdCBib2R5ID0gJCgic2V0dGluZ3NCb2R5Iik7CiAgYm9keS5pbm5lckhUTUwgPSAnPGRpdiBjbGFzcz0iZW1wdHkiPmzDpGR04oCmPC9kaXY+JzsKICBsZXQgczsKICB0cnkgeyBzID0gYXdhaXQgYXBpKCIvYXBpL3NldHRpbmdzIik7IH0KICBjYXRjaChlKXsgYm9keS5pbm5lckhUTUwgPSAiIjsgYm9keS5hcHBlbmRDaGlsZChlcnJCb3goIktvbm50ZSBFaW5zdGVsbHVuZ2VuIG5pY2h0IGxhZGVuOiAiK2UubWVzc2FnZSkpOyByZXR1cm47IH0KICBpZiAocy5lcnJvcil7IGJvZHkuaW5uZXJIVE1MPSIiOyBib2R5LmFwcGVuZENoaWxkKGVyckJveChzLmVycm9yKSk7IHJldHVybjsgfQoKICBjb25zdCBrZXlzID0gcy5rZXlzIHx8IHt9OwogIGNvbnN0IHBlcnNvbmEgPSBzLnBlcnNvbmEgfHwge307CiAgY29uc3QgY2xhdWRlTW9kZWxzID0gcy5jbGF1ZGVfbW9kZWxzIHx8IFtdOwoKICAvLyBDbGF1ZGUtTW9kZWxsLU9wdGlvbmVuCiAgY29uc3QgY21PcHRzID0gY2xhdWRlTW9kZWxzLm1hcChtID0+CiAgICBgPG9wdGlvbiB2YWx1ZT0iJHtlc2MobVswXSl9IiAke21bMF09PT1zLmNsYXVkZV9tb2RlbD8ic2VsZWN0ZWQiOiIifT4ke2VzYyhtWzFdKX08L29wdGlvbj5gKS5qb2luKCIiKTsKCiAgLy8gR3JhdGlzLU1vZGVsbC1PcHRpb25lbiAoT2xsYW1hKS4gQWt0dWVsbGVzIE1vZGVsbCBhdWZuZWhtZW4sIGZhbGxzIGVpZ2VuZXMuCiAgY29uc3Qgb2xsYW1hTW9kZWxzID0gcy5vbGxhbWFfbW9kZWxzIHx8IFtdOwogIGNvbnN0IG9tQ3VyID0gcy5vbGxhbWFfbW9kZWwgfHwgIiI7CiAgbGV0IG9tSXRlbXMgPSBvbGxhbWFNb2RlbHMuc2xpY2UoKTsKICBpZiAob21DdXIgJiYgIW9tSXRlbXMuc29tZShtID0+IG1bMF0gPT09IG9tQ3VyKSkgb21JdGVtcyA9IFtbb21DdXIsIG9tQ3VyICsgIiAoZWlnZW5lcykiXV0uY29uY2F0KG9tSXRlbXMpOwogIGNvbnN0IG9tT3B0cyA9IG9tSXRlbXMubWFwKG0gPT4KICAgIGA8b3B0aW9uIHZhbHVlPSIke2VzYyhtWzBdKX0iICR7bVswXT09PW9tQ3VyPyJzZWxlY3RlZCI6IiJ9PiR7ZXNjKG1bMV0pfTwvb3B0aW9uPmApLmpvaW4oIiIpOwoKICBjb25zdCBwcm92U2VsID0gKHApPT4gYDxvcHRpb24gdmFsdWU9IiR7cH0iICR7cy5wcm92aWRlcj09PXA/InNlbGVjdGVkIjoiIn0+YDsKCiAgYm9keS5pbm5lckhUTUwgPSBgCiAgICA8ZGl2IGNsYXNzPSJzZWN0Ij7wn5SRIEFQSS1TY2hsw7xzc2VsPC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPkNsYXVkZSAoZW1wZm9obGVuKTwvbGFiZWw+PGlucHV0IGlkPSJzdC1rZXktY2xhdWRlIiB0eXBlPSJwYXNzd29yZCIgcGxhY2Vob2xkZXI9InNrLWFudC3igKYiPjwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5DaGF0R1BUIC8gT3BlbkFJPC9sYWJlbD48aW5wdXQgaWQ9InN0LWtleS1vcGVuYWkiIHR5cGU9InBhc3N3b3JkIiBwbGFjZWhvbGRlcj0ic2st4oCmIj48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+R29vZ2xlIEdlbWluaTwvbGFiZWw+PGlucHV0IGlkPSJzdC1rZXktZ2VtaW5pIiB0eXBlPSJwYXNzd29yZCIgcGxhY2Vob2xkZXI9IkFJemHigKYiPjwvZGl2PgogICAgPGRpdiBjbGFzcz0iaGludCI+U2NobMO8c3NlbCBob2xlbjogPGNvZGU+Y29uc29sZS5hbnRocm9waWMuY29tPC9jb2RlPiDCtyA8Y29kZT5wbGF0Zm9ybS5vcGVuYWkuY29tL2FwaS1rZXlzPC9jb2RlPiDCtyA8Y29kZT5haXN0dWRpby5nb29nbGUuY29tL2FwaWtleTwvY29kZT48YnI+U2llIGJsZWliZW4gbG9rYWwgYXVmIGRlaW5lbSBQQy48L2Rpdj4KCiAgICA8ZGl2IGNsYXNzPSJzZWN0Ij7wn6egIFdlbGNoZXMgR2VoaXJuPzwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5BbmJpZXRlcjwvbGFiZWw+PHNlbGVjdCBpZD0ic3QtcHJvdmlkZXIiPgogICAgICAke3Byb3ZTZWwoImNsYXVkZSIpfUNsYXVkZTwvb3B0aW9uPiR7cHJvdlNlbCgib2xsYW1hIil98J+GkyBHcmF0aXMgbG9rYWwgKE9sbGFtYSk8L29wdGlvbj4ke3Byb3ZTZWwoIm9wZW5haSIpfUNoYXRHUFQgLyBPcGVuQUk8L29wdGlvbj4ke3Byb3ZTZWwoImdlbWluaSIpfUdlbWluaTwvb3B0aW9uPgogICAgPC9zZWxlY3Q+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPkNsYXVkZS1Nb2RlbGw8L2xhYmVsPjxzZWxlY3QgaWQ9InN0LWNsYXVkZS1tb2RlbCI+JHtjbU9wdHN9PC9zZWxlY3Q+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPk9wZW5BSS1Nb2RlbGw8L2xhYmVsPjxpbnB1dCBpZD0ic3Qtb3BlbmFpLW1vZGVsIiBwbGFjZWhvbGRlcj0iei5CLiBncHQtNS4xIj48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+R2VtaW5pLU1vZGVsbDwvbGFiZWw+PGlucHV0IGlkPSJzdC1nZW1pbmktbW9kZWwiIHBsYWNlaG9sZGVyPSJ6LkIuIGdlbWluaS0yLjUtcHJvIj48L2Rpdj4KCiAgICA8ZGl2IGNsYXNzPSJzZWN0Ij7wn4aTIEdyYXRpcyBsb2thbCAoT2xsYW1hKSDigJQgb2huZSBTY2hsw7xzc2VsPC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPkdyYXRpcy1Nb2RlbGw8L2xhYmVsPjxzZWxlY3QgaWQ9InN0LW9sbGFtYS1tb2RlbCI+JHtvbU9wdHN9PC9zZWxlY3Q+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJoaW50Ij5TdWNoIGRpciBkYXMgTW9kZWxsIG5hY2ggZGVpbmVtIFBDIGF1cy4gPGI+cXdlbjIuNTo3YjwvYj4gaXN0IGbDvHIgZGVpbmUgMTItR0ItR3JhZmlra2FydGUgZW1wZm9obGVuIOKAlCBkZXV0bGljaCBzY2hsYXVlciBhbHMgZGFzIGtsZWluZSBsbGFtYTMuMiB1bmQgdHJvdHpkZW0gZmxvdHQuIFdlbm4gZHUgYXVmIGVpbiBuZXVlcyBNb2RlbGwgd2VjaHNlbHN0LCBsw6RkdCBEaW5vIGVzIGJlaW0gbsOkY2hzdGVuIFN0YXJ0IDxiPmVpbm1hbGlnPC9iPiBoZXJ1bnRlciAoZWluIHBhYXIgTWludXRlbikuIEtvbXBsZXR0IGdyYXRpcyAmIG9mZmxpbmUuPC9kaXY+CgogICAgPGRpdiBjbGFzcz0ic2VjdCI+8J+SoSBHb3ZlZS1MYW1wZW4gKExpY2h0IHN0ZXVlcm4pPC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPkdvdmVlLVNjaGzDvHNzZWw8L2xhYmVsPjxpbnB1dCBpZD0ic3QtZ292ZWUta2V5IiB0eXBlPSJwYXNzd29yZCIgcGxhY2Vob2xkZXI9IkdvdmVlLUFQSS1LZXkiPjwvZGl2PgogICAgPGRpdiBjbGFzcz0iaGludCI+RGFtaXQgc3RldWVydCBEaW5vIGRlaW4gTGljaHQgKMK7bWFjaCBkYXMgTGljaHQgYmxhdcKrKS4gU2NobMO8c3NlbCBob2xlbjogPGI+R292ZWUtQXBwIOKGkiBQcm9maWwg4oaSIEVpbnN0ZWxsdW5nZW4g4oaSIEFwcGx5IGZvciBBUEkgS2V5PC9iPiDigJQga29tbXQgcGVyIEUtTWFpbC4gRGFuYWNoIGhpZXIgZWluZsO8Z2VuICYgc3BlaWNoZXJuLjwvZGl2PgoKICAgIDxkaXYgY2xhc3M9InNlY3QiPvCfjqcgRnJlaXNwcmVjaCAoRGF1ZXItTWlrcm8pPC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCIgc3R5bGU9ImRpc3BsYXk6ZmxleDthbGlnbi1pdGVtczpjZW50ZXI7Z2FwOjEwcHg7anVzdGlmeS1jb250ZW50OnNwYWNlLWJldHdlZW4iPjxsYWJlbCBzdHlsZT0ibWFyZ2luOjAiPk51ciBhdWYg4oCeSGV5IERpbm8iIHJlYWdpZXJlbjwvbGFiZWw+PGlucHV0IHR5cGU9ImNoZWNrYm94IiBpZD0ic3Qtd2FrZSIgc3R5bGU9IndpZHRoOjIwcHg7aGVpZ2h0OjIwcHgiPjwvZGl2PgogICAgPGRpdiBjbGFzcz0iaGludCI+PGI+QW48L2I+IChlbXBmb2hsZW4pOiBEaW5vIHJlYWdpZXJ0IG51ciwgd2VubiBkdSBtaXQgwrtIZXkgRGlub8KrIGFuZsOkbmdzdC4gPGI+QXVzPC9iPjogRGlubyBhbnR3b3J0ZXQgYXVmIGFsbGVzLCB3YXMgZHUgc2Fnc3QuIERlbiDwn46nLUtub3BmIHVudGVuIGRyw7xja2VuIHN0YXJ0ZXQgZGVuIERhdWVyLU1vZHVzLjwvZGl2PgoKICAgIDxkaXYgY2xhc3M9InNlY3QiPvCfjq0gUGVyc29uYTwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5OYW1lIGRlciBLSTwvbGFiZWw+PGlucHV0IGlkPSJzdC1hc3Npc3RhbnQiPjwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5XaWUgRGlubyBkaWNoIG5lbm50PC9sYWJlbD48aW5wdXQgaWQ9InN0LXVzZXIiPjwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5EZWluIEJ1c2luZXNzPC9sYWJlbD48dGV4dGFyZWEgaWQ9InN0LWJ1c2luZXNzIj48L3RleHRhcmVhPjwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5TdGlsIC8gSHVtb3I8L2xhYmVsPjx0ZXh0YXJlYSBpZD0ic3QtaHVtb3IiPjwvdGV4dGFyZWE+PC9kaXY+CgogICAgPGRpdiBjbGFzcz0ic2VjdCI+8J+OryBaaWVsPC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PHRleHRhcmVhIGlkPSJzdC1nb2FsIj48L3RleHRhcmVhPjwvZGl2PgoKICAgIDxkaXYgY2xhc3M9ImJ0bnJvdyI+CiAgICAgIDxidXR0b24gY2xhc3M9ImJ0biBwcmltYXJ5IiBpZD0ic3Qtc2F2ZSI+8J+SviBTcGVpY2hlcm48L2J1dHRvbj4KICAgICAgPHNwYW4gaWQ9InN0LW1zZyIgY2xhc3M9ImhpbnQiIHN0eWxlPSJhbGlnbi1zZWxmOmNlbnRlciI+PC9zcGFuPgogICAgPC9kaXY+CiAgYDsKICAvLyBXZXJ0ZSBlaW5zZXR6ZW4gKHBlciAudmFsdWUsIG5pY2h0IGluIGlubmVySFRNTCAtPiBzaWNoZXIpCiAgJCgic3Qta2V5LWNsYXVkZSIpLnZhbHVlID0ga2V5cy5jbGF1ZGUgfHwgIiI7CiAgJCgic3Qta2V5LW9wZW5haSIpLnZhbHVlID0ga2V5cy5vcGVuYWkgfHwgIiI7CiAgJCgic3Qta2V5LWdlbWluaSIpLnZhbHVlID0ga2V5cy5nZW1pbmkgfHwgIiI7CiAgJCgic3Qtb3BlbmFpLW1vZGVsIikudmFsdWUgPSBzLm9wZW5haV9tb2RlbCB8fCAiIjsKICAkKCJzdC1nZW1pbmktbW9kZWwiKS52YWx1ZSA9IHMuZ2VtaW5pX21vZGVsIHx8ICIiOwogICQoInN0LW9sbGFtYS1tb2RlbCIpLnZhbHVlID0gcy5vbGxhbWFfbW9kZWwgfHwgIiI7CiAgJCgic3QtZ292ZWUta2V5IikudmFsdWUgPSBzLmdvdmVlX2tleSB8fCAiIjsKICAkKCJzdC13YWtlIikuY2hlY2tlZCA9IChsb2NhbFN0b3JhZ2UuZ2V0SXRlbSgiZGlub193YWtlIikgIT09ICIwIik7CiAgJCgic3QtYXNzaXN0YW50IikudmFsdWUgPSBwZXJzb25hLmFzc2lzdGFudF9uYW1lIHx8ICIiOwogICQoInN0LXVzZXIiKS52YWx1ZSA9IHBlcnNvbmEudXNlcl9uYW1lIHx8ICIiOwogICQoInN0LWJ1c2luZXNzIikudmFsdWUgPSBwZXJzb25hLmJ1c2luZXNzIHx8ICIiOwogICQoInN0LWh1bW9yIikudmFsdWUgPSBwZXJzb25hLmh1bW9yIHx8ICIiOwogICQoInN0LWdvYWwiKS52YWx1ZSA9IHMuZ29hbCB8fCAiIjsKCiAgJCgic3Qtc2F2ZSIpLm9uY2xpY2sgPSBzYXZlU2V0dGluZ3M7Cn0KCmFzeW5jIGZ1bmN0aW9uIHNhdmVTZXR0aW5ncygpewogIGNvbnN0IGJ0biA9ICQoInN0LXNhdmUiKTsgYnRuLmRpc2FibGVkID0gdHJ1ZTsKICBjb25zdCB3ayA9ICQoInN0LXdha2UiKTsgaWYgKHdrKSBsb2NhbFN0b3JhZ2Uuc2V0SXRlbSgiZGlub193YWtlIiwgd2suY2hlY2tlZCA/ICIxIiA6ICIwIik7CiAgY29uc3QgcGF5bG9hZCA9IHsKICAgIHByb3ZpZGVyOiAkKCJzdC1wcm92aWRlciIpLnZhbHVlLAogICAgY2xhdWRlX21vZGVsOiAkKCJzdC1jbGF1ZGUtbW9kZWwiKS52YWx1ZSwKICAgIG9wZW5haV9tb2RlbDogJCgic3Qtb3BlbmFpLW1vZGVsIikudmFsdWUudHJpbSgpLAogICAgZ2VtaW5pX21vZGVsOiAkKCJzdC1nZW1pbmktbW9kZWwiKS52YWx1ZS50cmltKCksCiAgICBvbGxhbWFfbW9kZWw6ICQoInN0LW9sbGFtYS1tb2RlbCIpLnZhbHVlLnRyaW0oKSwKICAgIGdvdmVlX2tleTogJCgic3QtZ292ZWUta2V5IikudmFsdWUudHJpbSgpLAogICAga2V5czogewogICAgICBjbGF1ZGU6ICQoInN0LWtleS1jbGF1ZGUiKS52YWx1ZS50cmltKCksCiAgICAgIG9wZW5haTogJCgic3Qta2V5LW9wZW5haSIpLnZhbHVlLnRyaW0oKSwKICAgICAgZ2VtaW5pOiAkKCJzdC1rZXktZ2VtaW5pIikudmFsdWUudHJpbSgpLAogICAgfSwKICAgIHBlcnNvbmE6IHsKICAgICAgYXNzaXN0YW50X25hbWU6ICQoInN0LWFzc2lzdGFudCIpLnZhbHVlLnRyaW0oKSwKICAgICAgdXNlcl9uYW1lOiAkKCJzdC11c2VyIikudmFsdWUudHJpbSgpLAogICAgICBidXNpbmVzczogJCgic3QtYnVzaW5lc3MiKS52YWx1ZS50cmltKCksCiAgICAgIGh1bW9yOiAkKCJzdC1odW1vciIpLnZhbHVlLnRyaW0oKSwKICAgIH0sCiAgICBnb2FsOiAkKCJzdC1nb2FsIikudmFsdWUudHJpbSgpLAogIH07CiAgY29uc3QgbXNnID0gJCgic3QtbXNnIik7CiAgdHJ5ewogICAgY29uc3QgciA9IGF3YWl0IGFwaSgiL2FwaS9zZXR0aW5ncyIsICJQT1NUIiwgcGF5bG9hZCk7CiAgICBpZiAoci5lcnJvcil7IG1zZy50ZXh0Q29udGVudCA9ICLimqAgIityLmVycm9yOyBtc2cuc3R5bGUuY29sb3I9InZhcigtLXJvc2UpIjsgfQogICAgZWxzZXsKICAgICAgbXNnLnRleHRDb250ZW50ID0gIkdlc3BlaWNoZXJ0IOKckyI7IG1zZy5zdHlsZS5jb2xvcj0idmFyKC0tZ3JlZW4pIjsKICAgICAgYXdhaXQgbG9hZFN0YXR1cygpOyAgICAgICAgICAgIC8vIFN0YXR1cyBvYmVuIG5ldSBsYWRlbiAoa8O8bW1lcnQgc2ljaCB1bSBCZWdyw7zDn3VuZy9TZXR1cC1LYXJ0ZSkKICAgIH0KICB9Y2F0Y2goZSl7IG1zZy50ZXh0Q29udGVudCA9ICLimqAgIitlLm1lc3NhZ2U7IG1zZy5zdHlsZS5jb2xvcj0idmFyKC0tcm9zZSkiOyB9CiAgZmluYWxseXsgYnRuLmRpc2FibGVkID0gZmFsc2U7IH0KfQoKLy8gLS0tLS0tLS0tLSBLdW5kZW4gLS0tLS0tLS0tLQphc3luYyBmdW5jdGlvbiBsb2FkQ3VzdG9tZXJzKCl7CiAgY29uc3QgYm9keSA9ICQoImN1c3RvbWVyc0JvZHkiKTsKICBib2R5LmlubmVySFRNTCA9ICc8ZGl2IGNsYXNzPSJlbXB0eSI+bMOkZHTigKY8L2Rpdj4nOwogIGxldCBkOwogIHRyeSB7IGQgPSBhd2FpdCBhcGkoIi9hcGkvY3VzdG9tZXJzIik7IH0KICBjYXRjaChlKXsgYm9keS5pbm5lckhUTUw9IiI7IGJvZHkuYXBwZW5kQ2hpbGQoZXJyQm94KCJLb25udGUgS3VuZGVuIG5pY2h0IGxhZGVuOiAiK2UubWVzc2FnZSkpOyByZXR1cm47IH0KICBpZiAoZC5lcnJvcil7IGJvZHkuaW5uZXJIVE1MPSIiOyBib2R5LmFwcGVuZENoaWxkKGVyckJveChkLmVycm9yKSk7IHJldHVybjsgfQogIHJlbmRlckN1c3RvbWVycyhkKTsKfQoKZnVuY3Rpb24gcmVuZGVyQ3VzdG9tZXJzKGQpewogIGNvbnN0IGJvZHkgPSAkKCJjdXN0b21lcnNCb2R5Iik7CiAgYm9keS5pbm5lckhUTUwgPSAiIjsKICBjb25zdCByID0gZC5yZXZlbnVlIHx8IHt9OwogIGNvbnN0IGN1c3RzID0gZC5jdXN0b21lcnMgfHwgW107CgogIC8vIFVtc2F0ei1CYW5uZXIKICBjb25zdCByZXYgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsKICByZXYuY2xhc3NOYW1lID0gInJldmVudWUiOwogIHJldi5pbm5lckhUTUwgPQogICAgYDxkaXYgY2xhc3M9ImJpZyI+JHtldXJvKHIubW9udGhseSl9PC9kaXY+YCsKICAgIGA8ZGl2IGNsYXNzPSJzdWIiPk1vbmF0c3Vtc2F0eiDCtyB+JHtldXJvKHIud2Vla2x5KX0vV29jaGUgwrcgJHtyLmFjdGl2ZXx8MH0gYWt0aXYgwrcgJHtyLmxlYWRzfHwwfSBMZWFkcyDCtyAke3IudG90YWx8fDB9IGdlc2FtdDwvZGl2PmA7CiAgYm9keS5hcHBlbmRDaGlsZChyZXYpOwoKICAvLyAiTmV1ZXIgS3VuZGUiCiAgY29uc3QgbmV3QnRuID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiYnV0dG9uIik7CiAgbmV3QnRuLmNsYXNzTmFtZSA9ICJidG4gcHJpbWFyeSI7IG5ld0J0bi5zdHlsZS5tYXJnaW5Cb3R0b209IjE0cHgiOyBuZXdCdG4udGV4dENvbnRlbnQgPSAi4p6VIE5ldWVyIEt1bmRlIjsKICBuZXdCdG4ub25jbGljayA9ICgpPT4gc2hvd0N1c3RvbWVyRm9ybShudWxsKTsKICBib2R5LmFwcGVuZENoaWxkKG5ld0J0bik7CgogIGlmICghY3VzdHMubGVuZ3RoKXsKICAgIGNvbnN0IGUgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgZS5jbGFzc05hbWU9ImVtcHR5IjsgZS50ZXh0Q29udGVudD0iTm9jaCBrZWluZSBLdW5kZW4uIExlZyBlaW5lbiBhbi4g8J+RpSI7CiAgICBib2R5LmFwcGVuZENoaWxkKGUpOwogICAgcmV0dXJuOwogIH0KICBjdXN0cy5mb3JFYWNoKGMgPT4gYm9keS5hcHBlbmRDaGlsZChjdXN0Q2FyZChjKSkpOwp9CgpmdW5jdGlvbiBjdXN0Q2FyZChjKXsKICBjb25zdCBjYXJkID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IGNhcmQuY2xhc3NOYW1lID0gImN1c3QiOwogIGNvbnN0IHRvcCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyB0b3AuY2xhc3NOYW1lPSJ0b3AiOwogIGNvbnN0IG5tID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgic3BhbiIpOyBubS5jbGFzc05hbWU9Im5hbWUiOyBubS50ZXh0Q29udGVudCA9IGMubmFtZSB8fCAi4oCUIjsKICBjb25zdCBiZCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoInNwYW4iKTsgYmQuY2xhc3NOYW1lPSJiYWRnZSI7IGJkLnRleHRDb250ZW50ID0gYy5zdGF0dXMgfHwgIuKAlCI7CiAgdG9wLmFwcGVuZENoaWxkKG5tKTsgdG9wLmFwcGVuZENoaWxkKGJkKTsgY2FyZC5hcHBlbmRDaGlsZCh0b3ApOwoKICBjb25zdCBtZXRhID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IG1ldGEuY2xhc3NOYW1lPSJtZXRhIjsKICBjb25zdCBwYXJ0cyA9IFtdOwogIGlmIChjLmJyYW5jaGUpIHBhcnRzLnB1c2goYy5icmFuY2hlKTsKICBpZiAoYy5wYWtldCkgcGFydHMucHVzaChjLnBha2V0KTsKICBtZXRhLnRleHRDb250ZW50ID0gcGFydHMuam9pbigiIMK3ICIpOwogIGlmIChjLnByZWlzKXsKICAgIGNvbnN0IHAgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJzcGFuIik7IHAuY2xhc3NOYW1lPSJwcmljZSI7IHAudGV4dENvbnRlbnQgPSAocGFydHMubGVuZ3RoPyIgwrcgIjoiIikgKyBldXJvKGMucHJlaXMpKyIvTW9uYXQiOwogICAgbWV0YS5hcHBlbmRDaGlsZChwKTsKICB9CiAgY2FyZC5hcHBlbmRDaGlsZChtZXRhKTsKCiAgaWYgKGMubmFlY2hzdGVyX3NjaHJpdHQpewogICAgY29uc3QgbnMgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgbnMuY2xhc3NOYW1lPSJtZXRhIjsgbnMudGV4dENvbnRlbnQgPSAi4oaSICIgKyBjLm5hZWNoc3Rlcl9zY2hyaXR0OwogICAgY2FyZC5hcHBlbmRDaGlsZChucyk7CiAgfQogIGlmIChjLmtvbnRha3QpewogICAgY29uc3QgayA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBrLmNsYXNzTmFtZT0ibWV0YSI7IGsudGV4dENvbnRlbnQgPSAi4pyJICIgKyBjLmtvbnRha3Q7CiAgICBjYXJkLmFwcGVuZENoaWxkKGspOwogIH0KCiAgY29uc3QgYWN0ID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IGFjdC5jbGFzc05hbWU9ImFjdGlvbnMiOwogIGNvbnN0IGVkaXQgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJidXR0b24iKTsgZWRpdC5jbGFzc05hbWU9ImJ0biBzbSI7IGVkaXQudGV4dENvbnRlbnQ9IuKcj++4jyBCZWFyYmVpdGVuIjsKICBlZGl0Lm9uY2xpY2sgPSAoKT0+IHNob3dDdXN0b21lckZvcm0oYyk7CiAgY29uc3QgZGVsID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiYnV0dG9uIik7IGRlbC5jbGFzc05hbWU9ImJ0biBzbSBkYW5nZXIiOyBkZWwudGV4dENvbnRlbnQ9IvCfl5EgTMO2c2NoZW4iOwogIGRlbC5vbmNsaWNrID0gKCk9PiBkZWxldGVDdXN0b21lcihjKTsKICBhY3QuYXBwZW5kQ2hpbGQoZWRpdCk7IGFjdC5hcHBlbmRDaGlsZChkZWwpOwogIGNhcmQuYXBwZW5kQ2hpbGQoYWN0KTsKICByZXR1cm4gY2FyZDsKfQoKLy8gSW5saW5lLUZvcm11bGFyIChuZXUvYmVhcmJlaXRlbikgYWxzIEthcnRlCmZ1bmN0aW9uIHNob3dDdXN0b21lckZvcm0oYyl7CiAgY29uc3QgaXNFZGl0ID0gISFjOwogIGMgPSBjIHx8IHt9OwogIGNvbnN0IGJvZHkgPSAkKCJjdXN0b21lcnNCb2R5Iik7CiAgY29uc3QgZm9ybSA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBmb3JtLmNsYXNzTmFtZT0iY3VzdCI7CiAgY29uc3Qgc3RhdHVzT3B0cyA9IHN0YXRlLnN0YXR1c1ZhbHVlcy5tYXAocyA9PgogICAgYDxvcHRpb24gdmFsdWU9IiR7c30iICR7IChjLnN0YXR1c3x8IkxlYWQiKT09PXMgPyAic2VsZWN0ZWQiOiIiIH0+JHtzfTwvb3B0aW9uPmApLmpvaW4oIiIpOwogIGZvcm0uaW5uZXJIVE1MID0gYAogICAgPGRpdiBjbGFzcz0ic2VjdCIgc3R5bGU9Im1hcmdpbi10b3A6MCI+JHtpc0VkaXQgPyAi4pyP77iPIEt1bmRlIGJlYXJiZWl0ZW4iIDogIuKelSBOZXVlciBLdW5kZSJ9PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPk5hbWUgKjwvbGFiZWw+PGlucHV0IGlkPSJjZi1uYW1lIj48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+QnJhbmNoZTwvbGFiZWw+PGlucHV0IGlkPSJjZi1icmFuY2hlIj48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+S29udGFrdDwvbGFiZWw+PGlucHV0IGlkPSJjZi1rb250YWt0Ij48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+UGFrZXQ8L2xhYmVsPjxpbnB1dCBpZD0iY2YtcGFrZXQiPjwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5QcmVpcyDigqwgLyBNb25hdDwvbGFiZWw+PGlucHV0IGlkPSJjZi1wcmVpcyIgdHlwZT0ibnVtYmVyIiBzdGVwPSJhbnkiPjwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5TdGF0dXM8L2xhYmVsPjxzZWxlY3QgaWQ9ImNmLXN0YXR1cyI+JHtzdGF0dXNPcHRzfTwvc2VsZWN0PjwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5Ow6RjaHN0ZXIgU2Nocml0dDwvbGFiZWw+PGlucHV0IGlkPSJjZi1zY2hyaXR0Ij48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+Tm90aXplbjwvbGFiZWw+PHRleHRhcmVhIGlkPSJjZi1ub3RpemVuIj48L3RleHRhcmVhPjwvZGl2PgogICAgPGRpdiBjbGFzcz0iYnRucm93Ij4KICAgICAgPGJ1dHRvbiBjbGFzcz0iYnRuIHByaW1hcnkiIGlkPSJjZi1zYXZlIj7inJMgU3BlaWNoZXJuPC9idXR0b24+CiAgICAgIDxidXR0b24gY2xhc3M9ImJ0biIgaWQ9ImNmLWNhbmNlbCI+QWJicmVjaGVuPC9idXR0b24+CiAgICAgIDxzcGFuIGlkPSJjZi1tc2ciIGNsYXNzPSJoaW50IiBzdHlsZT0iYWxpZ24tc2VsZjpjZW50ZXIiPjwvc3Bhbj4KICAgIDwvZGl2PgogIGA7CiAgYm9keS5wcmVwZW5kKGZvcm0pOwogIC8vIFdlcnRlIGVpbnNldHplbiAoc2ljaGVyLCB2aWEgLnZhbHVlKQogICQoImNmLW5hbWUiKS52YWx1ZSA9IGMubmFtZSB8fCAiIjsKICAkKCJjZi1icmFuY2hlIikudmFsdWUgPSBjLmJyYW5jaGUgfHwgIiI7CiAgJCgiY2Yta29udGFrdCIpLnZhbHVlID0gYy5rb250YWt0IHx8ICIiOwogICQoImNmLXBha2V0IikudmFsdWUgPSBjLnBha2V0IHx8ICIiOwogICQoImNmLXByZWlzIikudmFsdWUgPSBjLnByZWlzICE9IG51bGwgPyBjLnByZWlzIDogIiI7CiAgJCgiY2Ytc2Nocml0dCIpLnZhbHVlID0gYy5uYWVjaHN0ZXJfc2Nocml0dCB8fCAiIjsKICAkKCJjZi1ub3RpemVuIikudmFsdWUgPSBjLm5vdGl6ZW4gfHwgIiI7CiAgZm9ybS5zY3JvbGxJbnRvVmlldyh7YmVoYXZpb3I6InNtb290aCIsIGJsb2NrOiJzdGFydCJ9KTsKCiAgJCgiY2YtY2FuY2VsIikub25jbGljayA9ICgpPT4gbG9hZEN1c3RvbWVycygpOwogICQoImNmLXNhdmUiKS5vbmNsaWNrID0gYXN5bmMgKCk9PnsKICAgIGNvbnN0IG5hbWUgPSAkKCJjZi1uYW1lIikudmFsdWUudHJpbSgpOwogICAgY29uc3QgbXNnID0gJCgiY2YtbXNnIik7CiAgICBpZiAoIW5hbWUpeyBtc2cudGV4dENvbnRlbnQ9Ik5hbWUgZmVobHQuIjsgbXNnLnN0eWxlLmNvbG9yPSJ2YXIoLS1yb3NlKSI7IHJldHVybjsgfQogICAgY29uc3QgZmllbGRzID0gewogICAgICBuYW1lLAogICAgICBicmFuY2hlOiAkKCJjZi1icmFuY2hlIikudmFsdWUudHJpbSgpLAogICAgICBrb250YWt0OiAkKCJjZi1rb250YWt0IikudmFsdWUudHJpbSgpLAogICAgICBwYWtldDogJCgiY2YtcGFrZXQiKS52YWx1ZS50cmltKCksCiAgICAgIHByZWlzOiAkKCJjZi1wcmVpcyIpLnZhbHVlLnRyaW0oKSwKICAgICAgc3RhdHVzOiAkKCJjZi1zdGF0dXMiKS52YWx1ZSwKICAgICAgbmFlY2hzdGVyX3NjaHJpdHQ6ICQoImNmLXNjaHJpdHQiKS52YWx1ZS50cmltKCksCiAgICAgIG5vdGl6ZW46ICQoImNmLW5vdGl6ZW4iKS52YWx1ZS50cmltKCksCiAgICB9OwogICAgY29uc3QgcGF5bG9hZCA9IGlzRWRpdCA/IE9iamVjdC5hc3NpZ24oeyBvcDoidXBkYXRlIiwgaWQ6Yy5pZCB9LCBmaWVsZHMpIDogT2JqZWN0LmFzc2lnbih7IG9wOiJhZGQiIH0sIGZpZWxkcyk7CiAgICAkKCJjZi1zYXZlIikuZGlzYWJsZWQgPSB0cnVlOwogICAgdHJ5ewogICAgICBjb25zdCByID0gYXdhaXQgYXBpKCIvYXBpL2N1c3RvbWVycyIsICJQT1NUIiwgcGF5bG9hZCk7CiAgICAgIGlmIChyLmVycm9yKXsgbXNnLnRleHRDb250ZW50PSLimqAgIityLmVycm9yOyBtc2cuc3R5bGUuY29sb3I9InZhcigtLXJvc2UpIjsgJCgiY2Ytc2F2ZSIpLmRpc2FibGVkPWZhbHNlOyB9CiAgICAgIGVsc2UgcmVuZGVyQ3VzdG9tZXJzKHIpOyAgICAgLy8gQW50d29ydCBlbnRow6RsdCBjdXN0b21lcnMgKyByZXZlbnVlCiAgICB9Y2F0Y2goZSl7IG1zZy50ZXh0Q29udGVudD0i4pqgICIrZS5tZXNzYWdlOyBtc2cuc3R5bGUuY29sb3I9InZhcigtLXJvc2UpIjsgJCgiY2Ytc2F2ZSIpLmRpc2FibGVkPWZhbHNlOyB9CiAgfTsKfQoKYXN5bmMgZnVuY3Rpb24gZGVsZXRlQ3VzdG9tZXIoYyl7CiAgaWYgKCFjb25maXJtKGBLdW5kZSDCuyR7Yy5uYW1lfcKrIHdpcmtsaWNoIGzDtnNjaGVuP2ApKSByZXR1cm47CiAgdHJ5ewogICAgY29uc3QgciA9IGF3YWl0IGFwaSgiL2FwaS9jdXN0b21lcnMiLCAiUE9TVCIsIHsgb3A6ImRlbGV0ZSIsIGlkOmMuaWQgfSk7CiAgICBpZiAoci5lcnJvcil7IGNvbnN0IGI9JCgiY3VzdG9tZXJzQm9keSIpOyBiLnByZXBlbmQoZXJyQm94KHIuZXJyb3IpKTsgfQogICAgZWxzZSByZW5kZXJDdXN0b21lcnMocik7CiAgfWNhdGNoKGUpeyAkKCJjdXN0b21lcnNCb2R5IikucHJlcGVuZChlcnJCb3goIk5ldHp3ZXJrZmVobGVyOiAiK2UubWVzc2FnZSkpOyB9Cn0KCi8vIC0tLS0tLS0tLS0gR2Vkw6RjaHRuaXMgLS0tLS0tLS0tLQphc3luYyBmdW5jdGlvbiBsb2FkTWVtb3J5KCl7CiAgY29uc3QgYm9keSA9ICQoIm1lbW9yeUJvZHkiKTsKICBib2R5LmlubmVySFRNTCA9ICc8ZGl2IGNsYXNzPSJlbXB0eSI+bMOkZHTigKY8L2Rpdj4nOwogIGxldCBkOwogIHRyeSB7IGQgPSBhd2FpdCBhcGkoIi9hcGkvbWVtb3J5Iik7IH0KICBjYXRjaChlKXsgYm9keS5pbm5lckhUTUw9IiI7IGJvZHkuYXBwZW5kQ2hpbGQoZXJyQm94KCJLb25udGUgR2Vkw6RjaHRuaXMgbmljaHQgbGFkZW46ICIrZS5tZXNzYWdlKSk7IHJldHVybjsgfQogIGlmIChkLmVycm9yKXsgYm9keS5pbm5lckhUTUw9IiI7IGJvZHkuYXBwZW5kQ2hpbGQoZXJyQm94KGQuZXJyb3IpKTsgcmV0dXJuOyB9CgogIGJvZHkuaW5uZXJIVE1MID0gIiI7CiAgY29uc3QgZmFjdHMgPSBkLmZhY3RzIHx8IFtdOwogIGNvbnN0IGpvdXJuYWwgPSBkLmpvdXJuYWwgfHwgW107CgogIGNvbnN0IGgxID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IGgxLmNsYXNzTmFtZT0ic2VjdCI7IGgxLnRleHRDb250ZW50PSLwn6egIFdhcyBEaW5vIMO8YmVyIGRpY2ggd2Vpw58iOwogIGJvZHkuYXBwZW5kQ2hpbGQoaDEpOwogIGlmIChmYWN0cy5sZW5ndGgpewogICAgY29uc3QgdWwgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJ1bCIpOyB1bC5jbGFzc05hbWU9ImZhY3RsaXN0IjsKICAgIGZhY3RzLmZvckVhY2goZiA9PiB7IGNvbnN0IGxpPWRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImxpIik7IGxpLnRleHRDb250ZW50PWY7IHVsLmFwcGVuZENoaWxkKGxpKTsgfSk7CiAgICBib2R5LmFwcGVuZENoaWxkKHVsKTsKICB9IGVsc2UgewogICAgY29uc3QgZT1kb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgZS5jbGFzc05hbWU9ImVtcHR5IjsgZS50ZXh0Q29udGVudD0iTm9jaCBsZWVyIOKAlCBrbGljayBpbSBDaGF0IGF1ZiDCu/Cfp6AgTGVybmVuwqsuIjsKICAgIGJvZHkuYXBwZW5kQ2hpbGQoZSk7CiAgfQoKICBjb25zdCBoMiA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBoMi5jbGFzc05hbWU9InNlY3QiOyBoMi50ZXh0Q29udGVudD0i8J+TkyBMZXR6dGUgTm90aXplbiAoVGFnZWJ1Y2gpIjsKICBib2R5LmFwcGVuZENoaWxkKGgyKTsKICBjb25zdCBqV3JhcCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBqV3JhcC5jbGFzc05hbWU9ImpvdXJuYWwiOwogIGNvbnN0IGxhc3QgPSBqb3VybmFsLnNsaWNlKC0xNSkucmV2ZXJzZSgpOwogIGlmIChsYXN0Lmxlbmd0aCl7CiAgICBsYXN0LmZvckVhY2goaj0+ewogICAgICBjb25zdCBsaW5lID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7CiAgICAgIGNvbnN0IGQyID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgic3BhbiIpOyBkMi5jbGFzc05hbWU9ImQiOyBkMi50ZXh0Q29udGVudCA9ICJbIisoai5kYXRlfHwiIikrIl0gIjsKICAgICAgbGluZS5hcHBlbmRDaGlsZChkMik7CiAgICAgIGxpbmUuYXBwZW5kQ2hpbGQoZG9jdW1lbnQuY3JlYXRlVGV4dE5vZGUoai5ub3RlfHwiIikpOwogICAgICBqV3JhcC5hcHBlbmRDaGlsZChsaW5lKTsKICAgIH0pOwogIH0gZWxzZSB7CiAgICBqV3JhcC5pbm5lckhUTUwgPSAnPGRpdiBjbGFzcz0iZW1wdHkiPihsZWVyKTwvZGl2Pic7CiAgfQogIGJvZHkuYXBwZW5kQ2hpbGQoaldyYXApOwp9CgovLyAtLS0tLS0tLS0tIFBDLVN0ZXVlcnVuZyAtLS0tLS0tLS0tCmFzeW5jIGZ1bmN0aW9uIGxvYWRQQygpewogIGNvbnN0IGJvZHkgPSAkKCJwY0JvZHkiKTsKICBib2R5LmlubmVySFRNTCA9ICIiOwoKICBjb25zdCBpbnRybyA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBpbnRyby5jbGFzc05hbWUgPSAiaGludCI7CiAgaW50cm8uaW5uZXJIVE1MID0gIkRpbm8gc3RldWVydCBkZWluZW4gUEMgd2llIGVpbiBDby1QaWxvdDogUHJvZ3JhbW1lICZhbXA7IE9yZG5lciDDtmZmbmVuLCBEYXRlaWVuIHNjaHJlaWJlbi9sZXNlbiwgQmVmZWhsZSBhdXNmw7xocmVuLiA8Yj5EdSBiZXN0w6R0aWdzdCBqZWRlIEFrdGlvbiBwZXIgS2xpY2s8L2I+IOKAlCBEaW5vIG1hY2h0IG5pY2h0cyB1bmdlZnJhZ3QuIFNhZyBpaG0gaW0gQ2hhdCBlaW5mYWNoLCB3YXMgZXIgdHVuIHNvbGwgKHouQi4gwrvDtmZmbmUgZGVuIEVkaXRvcsKrIG9kZXIgwrtzY2hyZWliIG1pciBkaWUgSWRlZW4gaW4gZWluZSBEYXRlacKrKSDigJQgZGFubiBlcnNjaGVpbmVuIEJlc3TDpHRpZ3VuZ3MtS27DtnBmZS4iOwogIGJvZHkuYXBwZW5kQ2hpbGQoaW50cm8pOwoKICBjb25zdCBzdyA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBzdy5jbGFzc05hbWUgPSAiZmllbGQiOwogIHN3LnN0eWxlLmNzc1RleHQgPSAiZGlzcGxheTpmbGV4O2FsaWduLWl0ZW1zOmNlbnRlcjtnYXA6MTBweDtqdXN0aWZ5LWNvbnRlbnQ6c3BhY2UtYmV0d2VlbiI7CiAgY29uc3Qgc3dsID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgibGFiZWwiKTsgc3dsLnRleHRDb250ZW50ID0gIlBDLVN0ZXVlcnVuZyBlcmxhdWJlbiI7IHN3bC5zdHlsZS5tYXJnaW4gPSAiMCI7CiAgY29uc3Qgc3diID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiYnV0dG9uIik7CiAgc3diLmNsYXNzTmFtZSA9ICJidG4iICsgKHN0YXRlLnBjQ29udHJvbCA/ICIgcHJpbWFyeSIgOiAiIik7CiAgc3diLnRleHRDb250ZW50ID0gc3RhdGUucGNDb250cm9sID8gIkFOIiA6ICJBVVMiOwogIHN3Yi5vbmNsaWNrID0gYXN5bmMgKCkgPT4gewogICAgY29uc3QgbnYgPSAhc3RhdGUucGNDb250cm9sOwogICAgdHJ5ewogICAgICBhd2FpdCBhcGkoIi9hcGkvc2V0dGluZ3MiLCAiUE9TVCIsIHsgcGNfY29udHJvbDogbnYgfSk7CiAgICAgIHN0YXRlLnBjQ29udHJvbCA9IG52OwogICAgICBzd2IudGV4dENvbnRlbnQgPSBudiA/ICJBTiIgOiAiQVVTIjsKICAgICAgc3diLmNsYXNzTmFtZSA9ICJidG4iICsgKG52ID8gIiBwcmltYXJ5IiA6ICIiKTsKICAgIH1jYXRjaChlKXsgLyogc3RpbGwgKi8gfQogIH07CiAgc3cuYXBwZW5kQ2hpbGQoc3dsKTsgc3cuYXBwZW5kQ2hpbGQoc3diKTsgYm9keS5hcHBlbmRDaGlsZChzdyk7CgogIGNvbnN0IGggPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgaC5jbGFzc05hbWUgPSAic2VjdCI7IGgudGV4dENvbnRlbnQgPSAi4pqhIFNjaG5lbGwtQWt0aW9uZW4iOyBib2R5LmFwcGVuZENoaWxkKGgpOwogIGNvbnN0IGdyaWQgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsKICBncmlkLnN0eWxlLmNzc1RleHQgPSAiZGlzcGxheTpmbGV4O2ZsZXgtd3JhcDp3cmFwO2dhcDo4cHgiOwogIGNvbnN0IG91dCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOwogIG91dC5zdHlsZS5jc3NUZXh0ID0gImZvbnQtc2l6ZToxMnB4O2NvbG9yOiNiZmU5ZjU7d2hpdGUtc3BhY2U6cHJlLXdyYXA7d29yZC1icmVhazpicmVhay13b3JkO2JhY2tncm91bmQ6IzBiMTUyNjtib3JkZXI6MXB4IHNvbGlkIHJnYmEoMTIwLDIwMCwyMzAsLjE4KTtib3JkZXItcmFkaXVzOjlweDtwYWRkaW5nOjhweDttYXJnaW46OHB4IDA7bWluLWhlaWdodDoyMHB4IjsKICBvdXQudGV4dENvbnRlbnQgPSAiKEVyZ2Vibmlzc2UgZXJzY2hlaW5lbiBoaWVyKSI7CiAgY29uc3QgcXVpY2sgPSBbCiAgICBbIvCfk50gRWRpdG9yIiwgImFwcF9vZWZmbmVuIiwgIm5vdGVwYWQiXSwKICAgIFsi8J+nriBSZWNobmVyIiwgImFwcF9vZWZmbmVuIiwgInJlY2huZXIiXSwKICAgIFsi8J+Xgu+4jyBFeHBsb3JlciIsICJhcHBfb2VmZm5lbiIsICJleHBsb3JlciJdLAogICAgWyLwn4yQIEJyb3dzZXIiLCAiYXBwX29lZmZuZW4iLCAiYnJvd3NlciJdLAogICAgWyLwn5K7IFN5c3RlbS1JbmZvIiwgInN5c3RlbV9pbmZvIiwgIiJdLAogICAgWyLwn5OLIERpbm8tRGF0ZWllbiIsICJkYXRlaWVuX2xpc3RlIiwgIiJdLAogIF07CiAgcXVpY2suZm9yRWFjaCgoW2xibCwgbmFtZSwgYXJnXSkgPT4gewogICAgY29uc3QgYiA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImJ1dHRvbiIpOyBiLmNsYXNzTmFtZSA9ICJjaGlwIjsgYi50ZXh0Q29udGVudCA9IGxibDsKICAgIGIub25jbGljayA9ICgpID0+IHBhbmVsUnVuKG5hbWUsIGFyZywgb3V0LCBiKTsKICAgIGdyaWQuYXBwZW5kQ2hpbGQoYik7CiAgfSk7CiAgYm9keS5hcHBlbmRDaGlsZChncmlkKTsKICBib2R5LmFwcGVuZENoaWxkKG91dCk7CgogIGNvbnN0IGhsID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IGhsLmNsYXNzTmFtZSA9ICJzZWN0IjsgaGwudGV4dENvbnRlbnQgPSAi8J+SoSBHb3ZlZS1MaWNodCI7IGJvZHkuYXBwZW5kQ2hpbGQoaGwpOwogIGNvbnN0IGxncmlkID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7CiAgbGdyaWQuc3R5bGUuY3NzVGV4dCA9ICJkaXNwbGF5OmZsZXg7ZmxleC13cmFwOndyYXA7Z2FwOjhweCI7CiAgY29uc3QgbGlnaHRzID0gWwogICAgWyLwn5KhIEFuIiwgImxpY2h0X2FuIiwgIiJdLCBbIvCfjJkgQXVzIiwgImxpY2h0X2F1cyIsICIiXSwKICAgIFsi8J+UtSBCbGF1IiwgImxpY2h0X2ZhcmJlIiwgImJsYXUiXSwgWyLwn5S0IFJvdCIsICJsaWNodF9mYXJiZSIsICJyb3QiXSwKICAgIFsi8J+foiBHcsO8biIsICJsaWNodF9mYXJiZSIsICJncsO8biJdLCBbIvCfn6MgTGlsYSIsICJsaWNodF9mYXJiZSIsICJsaWxhIl0sCiAgICBbIvCfn6AgV2FybSIsICJsaWNodF9mYXJiZSIsICJ3YXJtIl0sIFsi8J+UhiAxMDAlIiwgImxpY2h0X2hlbGxpZ2tlaXQiLCAiMTAwIl0sCiAgXTsKICBsaWdodHMuZm9yRWFjaCgoW2xibCwgbmFtZSwgYXJnXSkgPT4gewogICAgY29uc3QgYiA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImJ1dHRvbiIpOyBiLmNsYXNzTmFtZSA9ICJjaGlwIjsgYi50ZXh0Q29udGVudCA9IGxibDsKICAgIGIub25jbGljayA9ICgpID0+IHBhbmVsUnVuKG5hbWUsIGFyZywgb3V0LCBiKTsKICAgIGxncmlkLmFwcGVuZENoaWxkKGIpOwogIH0pOwogIGJvZHkuYXBwZW5kQ2hpbGQobGdyaWQpOwogIGNvbnN0IGxoaW50ID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IGxoaW50LmNsYXNzTmFtZSA9ICJoaW50IjsKICBsaGludC5pbm5lckhUTUwgPSAiRnVua3Rpb25pZXJ0LCBzb2JhbGQgZGVpbiA8Yj5Hb3ZlZS1TY2hsw7xzc2VsPC9iPiBpbiDimpkgRWluc3RlbGx1bmdlbiBzdGVodC4gRGFubiByZWljaHQgaW0gQ2hhdCBhdWNoOiDCu21hY2ggZGFzIExpY2h0IGJsYXXCqy4iOwogIGJvZHkuYXBwZW5kQ2hpbGQobGhpbnQpOwoKICBjb25zdCBoMiA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBoMi5jbGFzc05hbWUgPSAic2VjdCI7IGgyLnRleHRDb250ZW50ID0gIuKMqO+4jyBFaWdlbmVyIEJlZmVobCI7IGJvZHkuYXBwZW5kQ2hpbGQoaDIpOwogIGNvbnN0IGNpID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiaW5wdXQiKTsKICBjaS5wbGFjZWhvbGRlciA9ICJ6LkIuIGVjaG8gaGFsbG8gICBvZGVyICAgZGlyIjsKICBjaS5zdHlsZS5jc3NUZXh0ID0gIndpZHRoOjEwMCU7YmFja2dyb3VuZDojMGIxNTI2O2NvbG9yOiNlOGYxZmY7Ym9yZGVyOjFweCBzb2xpZCByZ2JhKDEyMCwyMDAsMjMwLC4yOCk7Ym9yZGVyLXJhZGl1czo5cHg7cGFkZGluZzo5cHg7b3V0bGluZTpub25lIjsKICBib2R5LmFwcGVuZENoaWxkKGNpKTsKICBjb25zdCBjYiA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImJ1dHRvbiIpOyBjYi5jbGFzc05hbWUgPSAiYnRuIjsgY2IudGV4dENvbnRlbnQgPSAi4pa2IEJlZmVobCBhdXNmw7xocmVuIjsKICBjYi5zdHlsZS5tYXJnaW5Ub3AgPSAiOHB4IjsKICBjYi5vbmNsaWNrID0gKCkgPT4gewogICAgY29uc3QgY21kID0gY2kudmFsdWUudHJpbSgpOyBpZiAoIWNtZCkgcmV0dXJuOwogICAgaWYgKCF3aW5kb3cuY29uZmlybSgiRGllc2VuIEJlZmVobCB3aXJrbGljaCBhdWYgZGVpbmVtIFBDIGF1c2bDvGhyZW4/XG5cbiIgKyBjbWQpKSByZXR1cm47CiAgICBwYW5lbFJ1bigiYmVmZWhsIiwgY21kLCBvdXQsIGNiKTsKICB9OwogIGJvZHkuYXBwZW5kQ2hpbGQoY2IpOwogIGNvbnN0IHdhcm4gPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgd2Fybi5jbGFzc05hbWUgPSAiaGludCI7CiAgd2Fybi5zdHlsZS5jb2xvciA9ICIjZmJiZjI0IjsKICB3YXJuLnRleHRDb250ZW50ID0gIlZvcnNpY2h0OiBCZWZlaGxlIGxhdWZlbiBlY2h0IGF1ZiBkZWluZW0gUEMuIE51ciBhdXNmw7xocmVuLCB3ZW5uIGR1IHdlacOfdCwgd2FzIHNpZSB0dW4uIjsKICBib2R5LmFwcGVuZENoaWxkKHdhcm4pOwp9Cgphc3luYyBmdW5jdGlvbiBwYW5lbFJ1bihuYW1lLCBhcmcsIG91dCwgYnRuKXsKICBjb25zdCBpc0xpZ2h0ID0gbmFtZS5pbmRleE9mKCJsaWNodF8iKSA9PT0gMDsKICBpZiAoIXN0YXRlLnBjQ29udHJvbCAmJiAhaXNMaWdodCl7IG91dC5zdHlsZS5jb2xvciA9ICIjZmJiZjI0Ijsgb3V0LnRleHRDb250ZW50ID0gIlBDLVN0ZXVlcnVuZyBpc3QgQVVTIOKAlCBvYmVuIGVpbnNjaGFsdGVuLiI7IHJldHVybjsgfQogIGlmIChidG4pIGJ0bi5kaXNhYmxlZCA9IHRydWU7CiAgb3V0LnN0eWxlLmNvbG9yID0gIiNiZmU5ZjUiOyBvdXQudGV4dENvbnRlbnQgPSAibMOkdWZ04oCmIjsKICB0cnl7CiAgICBjb25zdCBkYXRhID0gYXdhaXQgYXBpKCIvYXBpL2FjdGlvbiIsICJQT1NUIiwgeyBuYW1lLCBhcmcgfSk7CiAgICBvdXQuc3R5bGUuY29sb3IgPSBkYXRhLm9rID8gIiMzNGQzOTkiIDogIiNmYjcxODUiOwogICAgb3V0LnRleHRDb250ZW50ID0gKGRhdGEub2sgPyAi4pyTICIgOiAi4pyWICIpICsgKGRhdGEub3V0cHV0IHx8ICIiKTsKICB9Y2F0Y2goZSl7IG91dC5zdHlsZS5jb2xvciA9ICIjZmI3MTg1Ijsgb3V0LnRleHRDb250ZW50ID0gIuKcliBOZXR6d2Vya2ZlaGxlcjogIiArIGUubWVzc2FnZTsgfQogIGlmIChidG4pIGJ0bi5kaXNhYmxlZCA9IGZhbHNlOwp9CgovLyBrbGVpbmUgcm90ZSBGZWhsZXJib3ggZsO8ciBQYW5lbHMKZnVuY3Rpb24gZXJyQm94KHRleHQpewogIGNvbnN0IGUgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsKICBlLmNsYXNzTmFtZSA9ICJtc2cgZXJyb3IiOyBlLnN0eWxlLm1heFdpZHRoPSIxMDAlIjsKICBjb25zdCBiID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IGIuY2xhc3NOYW1lPSJidWJibGUiOyBiLnRleHRDb250ZW50ID0gdGV4dDsKICBlLmFwcGVuZENoaWxkKGIpOwogIHJldHVybiBlOwp9CgovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KLy8gIFN0YXJ0Ci8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQpsb2FkU3RhdHVzKCk7CmlucHV0RWwuZm9jdXMoKTsKPC9zY3JpcHQ+CjwvYm9keT4KPC9odG1sPgo=").decode("utf-8")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦖 Dino KI — App-Kern (lokaler Server) für das Jarvis-Chatfenster.

Startet einen kleinen lokalen Server auf deinem PC, öffnet automatisch das
schicke Chat-Fenster (dino_chat.html) im Browser und reicht deine Nachrichten
ans Gehirn (dino_core) weiter. Dein API-Schlüssel bleibt dabei auf dem Server
(nicht im Browser sichtbar) und alles läuft nur auf 127.0.0.1 — also nur lokal.

Reines Python (Standardbibliothek). Starten:  python dino_server.py
"""

import json
import os
import sys
import secrets
import subprocess
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Geheimes Token gegen fremde Webseiten: wird in Dinos eigene Seite eingebaut.
# Eine fremde Seite kann es nicht lesen -> kann keine PC-Aktionen auslösen.
CSRF_TOKEN = secrets.token_hex(16)

# Konsole auf UTF-8 stellen, damit Emojis/Umlaute in Windows nie crashen
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


HOST = "127.0.0.1"
PORT_RANGE = range(8765, 8800)

d = Dino()
_lock = threading.Lock()  # Schreibzugriffe auf Gedächtnis/Config absichern


# ── Daten für die Oberfläche ───────────────────────────────────────────
def status_payload():
    p = d.config["persona"]
    return {
        "ready": d.is_ready(),
        "brain": d.provider_label(),
        "provider": d.config["provider"],
        "assistant_name": p["assistant_name"],
        "user_name": p["user_name"],
        "facts": len(d.memory.get("facts", [])),
        "customers": len(d.customers()),
        "goal": d.config["goal"],
        "revenue": d.revenue(),
        "pc_control": d.config.get("pc_control", True),
        "govee_set": bool(d.config.get("govee_key", "").strip()),
    }


def customers_payload():
    return {"customers": d.customers(), "revenue": d.revenue()}


def settings_payload():
    cfg = d.config
    return {
        "provider": cfg["provider"],
        "claude_model": cfg["claude_model"],
        "openai_model": cfg["openai_model"],
        "gemini_model": cfg["gemini_model"],
        "ollama_model": cfg.get("ollama_model", "llama3.2"),
        "ollama_url": cfg.get("ollama_url", "http://127.0.0.1:11434"),
        "keys": dict(cfg["keys"]),
        "persona": dict(cfg["persona"]),
        "goal": cfg["goal"],
        "pc_control": cfg.get("pc_control", True),
        "govee_key": cfg.get("govee_key", ""),
        "claude_models": [[mid, desc] for mid, desc in CLAUDE_MODELS.values()],
        "ollama_models": [[mid, desc] for mid, desc in OLLAMA_MODELS.values()],
    }


# ── Endpunkt-Logik ─────────────────────────────────────────────────────
def handle_chat(body):
    messages = body.get("messages", [])
    if not isinstance(messages, list) or not messages:
        return {"error": "Keine Nachricht erhalten."}
    last = messages[-1]
    if last.get("role") == "user":
        d.add_journal(f"hat geschrieben: {last.get('content', '')}")
    text, err = d.chat(messages)
    if err:
        return {"error": err}
    # PC-Aktionen erkennen (werden im Browser als Bestätigungs-Knöpfe gezeigt)
    actions = Dino.parse_actions(text) if d.config.get("pc_control", True) else []
    return {"reply": text, "actions": actions}


def handle_action(body):
    name = (body.get("name") or "").strip()
    arg = body.get("arg", "")
    ok, output = d.run_action(name, arg)
    if ok:
        d.add_journal(f"PC-Aktion ausgeführt: {name} | {str(arg)[:80]}")
    return {"ok": ok, "output": output}


def handle_web(body):
    frage = (body.get("frage") or "").strip()
    if not frage:
        msgs = body.get("messages", [])
        if msgs and msgs[-1].get("role") == "user":
            frage = (msgs[-1].get("content") or "").strip()
    if not frage:
        return {"error": "Keine Frage angegeben."}
    text, err = d.web_answer(frage)
    return {"error": err} if err else {"text": text}


def govee_payload():
    devs, err = d.govee_devices()
    if err:
        return {"connected": False, "count": 0, "error": err}
    names = [x.get("deviceName") or x.get("sku") or "Lampe" for x in devs]
    return {"connected": True, "count": len(devs), "names": names[:12]}


def handle_plan(_body):
    text, err = d.plan()
    return {"error": err} if err else {"text": text}


def handle_tag(_body):
    text, err = d.tagescheckin()
    return {"error": err} if err else {"text": text}


def handle_learn(body):
    messages = body.get("messages", [])
    count, err = d.learn(messages)
    return {"error": err} if err else {"count": count}


def handle_council(body):
    messages = body.get("messages", [])
    frage = (body.get("frage") or "").strip()
    if not frage:
        return {"error": "Keine Frage angegeben."}
    answers, synthese, err = d.rat(messages, frage)
    return {"error": err} if err else {"answers": answers, "synthese": synthese}


def handle_team(body):
    task = (body.get("task") or "").strip()
    if not task:
        messages = body.get("messages", [])
        if messages and messages[-1].get("role") == "user":
            task = (messages[-1].get("content") or "").strip()
    if not task:
        return {"error": "Keine Aufgabe angegeben."}
    steps, final, err = d.team(task)
    if err and not steps:
        return {"error": err}
    return {"steps": steps, "final": final, "error": err}


def handle_memory():
    return {
        "facts": d.memory.get("facts", []),
        "journal": d.memory.get("journal", [])[-30:],
    }


def handle_customers_post(body):
    op = body.get("op")
    if op == "add":
        d.add_customer(
            name=body.get("name", ""), branche=body.get("branche", ""),
            kontakt=body.get("kontakt", ""), paket=body.get("paket", ""),
            preis=body.get("preis", 0), status=body.get("status", "Lead"),
            naechster_schritt=body.get("naechster_schritt", ""),
            notizen=body.get("notizen", ""))
    elif op == "update":
        cid = body.get("id")
        fields = {k: body[k] for k in ("name", "branche", "kontakt", "paket", "preis",
                                       "status", "naechster_schritt", "notizen") if k in body}
        d.update_customer(int(cid), **fields)
    elif op == "delete":
        d.delete_customer(int(body.get("id")))
    else:
        return {"error": "Unbekannte Aktion."}
    return customers_payload()


def handle_settings_post(body):
    cfg = d.config
    keys = body.get("keys", {})
    for k in ("claude", "openai", "gemini"):
        if k in keys:
            cfg["keys"][k] = (keys[k] or "").strip()
    if "provider" in body:
        cfg["provider"] = body["provider"] or "claude"
    if "claude_model" in body:
        cfg["claude_model"] = body["claude_model"] or "claude-opus-4-8"
    if "openai_model" in body:
        cfg["openai_model"] = (body["openai_model"] or "").strip()
    if "gemini_model" in body:
        cfg["gemini_model"] = (body["gemini_model"] or "").strip() or "gemini-2.5-pro"
    if "ollama_model" in body:
        cfg["ollama_model"] = (body["ollama_model"] or "").strip() or "llama3.2"
        cfg["ollama_locked"] = True  # eigene Wahl -> Auto-Upgrade nicht mehr überschreiben
    if "ollama_url" in body:
        cfg["ollama_url"] = (body["ollama_url"] or "").strip() or "http://127.0.0.1:11434"
    if "goal" in body:
        cfg["goal"] = (body["goal"] or "").strip()
    if "pc_control" in body:
        cfg["pc_control"] = bool(body["pc_control"])
    if "govee_key" in body:
        cfg["govee_key"] = (body["govee_key"] or "").strip()
    persona = body.get("persona", {})
    for k in ("assistant_name", "user_name", "business", "humor"):
        if k in persona:
            cfg["persona"][k] = (persona[k] or "").strip() or cfg["persona"][k]
    d.save_config()
    return {"ok": True, "brain": d.provider_label(), "ready": d.is_ready()}


# ── HTTP-Handler ───────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # ruhiges Log
        pass

    def _send_json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_inline(self, text, ctype="text/html; charset=utf-8"):
        data = text.replace("__DINO_CSRF__", CSRF_TOKEN).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_file(self, path, ctype="text/html; charset=utf-8"):
        try:
            with open(path, "rb") as f:
                data = f.read()
        except FileNotFoundError:
            self.send_response(404); self.end_headers()
            self.wfile.write(b"dino_chat.html fehlt.")
            return
        data = data.replace(b"__DINO_CSRF__", CSRF_TOKEN.encode("ascii"))
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _body(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            if 0 < length <= 4_000_000:  # Obergrenze gegen Speicher-Überlauf
                return json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            pass
        return {}

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/index.html", "/dino_chat.html"):
            self._send_inline(DINO_HTML)
        elif path == "/api/status":
            self._send_json(status_payload())
        elif path == "/api/settings":
            self._send_json(settings_payload())
        elif path == "/api/customers":
            self._send_json(customers_payload())
        elif path == "/api/memory":
            self._send_json(handle_memory())
        elif path == "/api/ollama":
            self._send_json(d.ollama_status())
        elif path == "/api/govee":
            self._send_json(govee_payload())
        elif path == "/favicon.ico":
            self.send_response(204); self.end_headers()
        else:
            self.send_response(404); self.end_headers()

    def _request_ok(self):
        """Schützt vor fremden Webseiten, die heimlich (PC-)Aktionen auslösen wollen
        (CSRF / DNS-Rebinding). Drei Schichten:
          1) geheimes Token, das nur in Dinos eigener Seite steht (fremde Seite kennt es nicht),
          2) Herkunft (Origin) muss lokal sein,
          3) Inhaltstyp muss JSON sein (verhindert simple Formular-POSTs)."""
        # 1) Token — die eigentliche Sperre
        if self.headers.get("X-Dino-Token") != CSRF_TOKEN:
            return False
        # 2) Origin (falls vorhanden) muss lokal sein
        origin = (self.headers.get("Origin") or "").lower()
        if origin and not (origin.startswith("http://127.0.0.1") or origin.startswith("http://localhost")):
            return False
        # 3) Host muss lokal sein (gegen DNS-Rebinding)
        host = (self.headers.get("Host") or "").split(":")[0].lower()
        if host and host not in ("127.0.0.1", "localhost"):
            return False
        # 4) nur JSON-Anfragen
        ctype = (self.headers.get("Content-Type") or "").lower()
        if "application/json" not in ctype:
            return False
        return True

    def do_POST(self):
        path = self.path.split("?")[0]
        if not self._request_ok():
            self._send_json({"error": "Abgelehnt: Anfrage kommt nicht von Dinos lokaler Seite."}, code=403)
            return
        body = self._body()
        with _lock:
            try:
                if path == "/api/chat":
                    out = handle_chat(body)
                elif path == "/api/plan":
                    out = handle_plan(body)
                elif path == "/api/tag":
                    out = handle_tag(body)
                elif path == "/api/learn":
                    out = handle_learn(body)
                elif path == "/api/council":
                    out = handle_council(body)
                elif path == "/api/team":
                    out = handle_team(body)
                elif path == "/api/web":
                    out = handle_web(body)
                elif path == "/api/action":
                    out = handle_action(body)
                elif path == "/api/customers":
                    out = handle_customers_post(body)
                elif path == "/api/settings":
                    out = handle_settings_post(body)
                else:
                    self.send_response(404); self.end_headers(); return
            except Exception as e:
                out = {"error": f"Interner Fehler: {e}"}
        self._send_json(out)


def _open_browser(url):
    """Öffnet das Chat-Fenster mit mehreren Methoden (eine davon klappt fast immer)."""
    try:
        if webbrowser.open(url):
            return
    except Exception:
        pass
    if os.name == "nt":
        try:
            os.startfile(url)  # Windows-Standardbrowser
            return
        except Exception:
            pass
        try:
            subprocess.Popen(["cmd", "/c", "start", "", url])
        except Exception:
            pass


def main():
    httpd = None
    for port in PORT_RANGE:
        try:
            httpd = ThreadingHTTPServer((HOST, port), Handler)
            break
        except OSError:
            continue
    if httpd is None:
        print("Konnte keinen freien Port finden (8765-8799)."); sys.exit(1)

    print("\n  Dino wird gestartet - richte mich kurz selbst ein...\n")
    try:
        d.ensure_ollama()
    except Exception as e:
        print(f"  (Auto-Setup uebersprungen: {e})")

    url = f"http://{HOST}:{httpd.server_address[1]}/"
    # Log schreiben, falls das Fenster zu schnell weg ist
    try:
        with open(os.path.join(HERE, "Dino-Log.txt"), "w", encoding="utf-8") as lf:
            lf.write("Dino laeuft.\n")
            lf.write("Oeffne diese Adresse im Browser, falls kein Fenster aufgeht:\n")
            lf.write("   " + url + "\n")
    except Exception:
        pass

    print("\n" + "=" * 52)
    print("   DINO KI LAEUFT!")
    print("   Falls KEIN Browser-Fenster aufgeht, oeffne deinen")
    print("   Browser und tippe oben rein:")
    print("   >>>   " + url)
    print("=" * 52)
    print("  (Dieses Fenster offen lassen. Stoppen: Strg+C)\n")
    _open_browser(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Dino macht Feierabend. Bis spaeter!")
        httpd.shutdown()


if __name__ == "__main__":
    main()
