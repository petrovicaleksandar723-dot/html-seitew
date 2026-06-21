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
{self._pc_help()}"""

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
Bestätigung kam. Schlag bei heiklen Befehlen lieber den kleinsten, sichersten Schritt vor."""

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
            if name not in ACTIONS:
                continue
            label, _desc, warn = ACTIONS[name]
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
        if not self.config.get("pc_control", True):
            return False, "PC-Steuerung ist in den Einstellungen ausgeschaltet."
        name = (name or "").strip().lower()
        arg = (arg or "").strip()
        if name not in ACTIONS:
            return False, f"Unbekannte Aktion: {name}"
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
