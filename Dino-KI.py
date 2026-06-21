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
import datetime
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
Ziel planen."""

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
DINO_HTML = _b64.b64decode("PCFET0NUWVBFIGh0bWw+CjxodG1sIGxhbmc9ImRlIj4KPGhlYWQ+CjxtZXRhIGNoYXJzZXQ9IlVURi04Ij4KPG1ldGEgbmFtZT0idmlld3BvcnQiIGNvbnRlbnQ9IndpZHRoPWRldmljZS13aWR0aCwgaW5pdGlhbC1zY2FsZT0xLjAiPgo8dGl0bGU+8J+mliBEaW5vIEtJPC90aXRsZT4KPHN0eWxlPgovKiA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KICAgRElOTyBLSSDigJQgSmFydmlzL1NjaS1GaSBGcm9udGVuZCAoZWluZSBlaWdlbnN0w6RuZGlnZSBEYXRlaSkKICAgUmVpbmVzIEhUTUwvQ1NTL0pTLCBrZWluZSBleHRlcm5lbiBCaWJsaW90aGVrZW4uCiAgID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PSAqLwoKLyogLS0tLSBEZXNpZ24tVmFyaWFibGVuIC0tLS0gKi8KOnJvb3R7CiAgLS1iZzojMDQwNjBkOyAgICAgICAgICAgIC8qIGZhc3Qgc2Nod2FyeiAqLwogIC0tYmcyOiMwNjBhMTY7CiAgLS1wYW5lbDpyZ2JhKDE0LDIyLDQyLC42Mik7ICAgLyogR2xhc21vcnBoaXNtdXMtUGFuZWwgKi8KICAtLXBhbmVsLXNvbGlkOiMwYTExMjQ7CiAgLS1saW5lOnJnYmEoNTYsMTg5LDI0OCwuMjIpOyAgLyogbGV1Y2h0ZW5kZXIgZMO8bm5lciBSYW5kICovCiAgLS1jeWFuOiMyMmQzZWU7CiAgLS1ibHVlOiMzOGJkZjg7CiAgLS1ibHVlMjojNjBhNWZhOwogIC0tdHh0OiNlOGYxZmY7CiAgLS1tdXQ6IzdjOGRiNTsKICAtLWdyZWVuOiMzNGQzOTk7CiAgLS1yb3NlOiNmYjcxODU7CiAgLS1hbWJlcjojZmJiZjI0OwogIC0tZ2xvdzowIDAgMThweCByZ2JhKDM0LDIxMSwyMzgsLjU1KTsKfQoKKntib3gtc2l6aW5nOmJvcmRlci1ib3h9Cmh0bWwsYm9keXtoZWlnaHQ6MTAwJX0KYm9keXsKICBtYXJnaW46MDsKICBmb250LWZhbWlseToiU2Vnb2UgVUkiLHN5c3RlbS11aSwtYXBwbGUtc3lzdGVtLCJIZWx2ZXRpY2EgTmV1ZSIsQXJpYWwsc2Fucy1zZXJpZjsKICBjb2xvcjp2YXIoLS10eHQpOwogIGJhY2tncm91bmQ6CiAgICByYWRpYWwtZ3JhZGllbnQoMTIwMHB4IDYwMHB4IGF0IDUwJSAtMTAlLCByZ2JhKDM0LDIxMSwyMzgsLjEwKSwgdHJhbnNwYXJlbnQgNjAlKSwKICAgIHJhZGlhbC1ncmFkaWVudCg5MDBweCA1MDBweCBhdCA5MCUgMTEwJSwgcmdiYSg5NiwxNjUsMjUwLC4wOCksIHRyYW5zcGFyZW50IDYwJSksCiAgICB2YXIoLS1iZyk7CiAgb3ZlcmZsb3c6aGlkZGVuOwp9Ci8qIGRlemVudGVzIEdyaWQgaW0gSGludGVyZ3J1bmQgKi8KYm9keTo6YmVmb3JlewogIGNvbnRlbnQ6IiI7cG9zaXRpb246Zml4ZWQ7aW5zZXQ6MDt6LWluZGV4OjA7cG9pbnRlci1ldmVudHM6bm9uZTtvcGFjaXR5Oi4zNTsKICBiYWNrZ3JvdW5kLWltYWdlOgogICAgbGluZWFyLWdyYWRpZW50KHJnYmEoNTYsMTg5LDI0OCwuMDYpIDFweCx0cmFuc3BhcmVudCAxcHgpLAogICAgbGluZWFyLWdyYWRpZW50KDkwZGVnLHJnYmEoNTYsMTg5LDI0OCwuMDYpIDFweCx0cmFuc3BhcmVudCAxcHgpOwogIGJhY2tncm91bmQtc2l6ZTo0NHB4IDQ0cHg7CiAgbWFzay1pbWFnZTpyYWRpYWwtZ3JhZGllbnQoY2lyY2xlIGF0IDUwJSAzMCUsIzAwMCAwJSx0cmFuc3BhcmVudCA4MCUpOwp9CgouYXBwe3Bvc2l0aW9uOnJlbGF0aXZlO3otaW5kZXg6MTtkaXNwbGF5OmZsZXg7ZmxleC1kaXJlY3Rpb246Y29sdW1uO2hlaWdodDoxMDB2aDttYXgtd2lkdGg6MTE4MHB4O21hcmdpbjowIGF1dG87cGFkZGluZzoxNHB4IDE4cHggMTZweH0KCi8qID09PT09PT09PT09PT09PT09IEtvcGZ6ZWlsZSA9PT09PT09PT09PT09PT09PSAqLwouaGVhZGVye2Rpc3BsYXk6ZmxleDthbGlnbi1pdGVtczpjZW50ZXI7Z2FwOjE4cHg7cGFkZGluZzo2cHggNHB4IDEycHh9Ci5icmFuZHtkaXNwbGF5OmZsZXg7YWxpZ24taXRlbXM6Y2VudGVyO2dhcDoxNHB4O21pbi13aWR0aDowfQoud29yZG1hcmt7CiAgZm9udC1zaXplOjI2cHg7Zm9udC13ZWlnaHQ6ODAwO2xldHRlci1zcGFjaW5nOjVweDsKICBiYWNrZ3JvdW5kOmxpbmVhci1ncmFkaWVudCg5MGRlZywjNjdlOGY5LCMzOGJkZjgsIzgxOGNmOCk7CiAgLXdlYmtpdC1iYWNrZ3JvdW5kLWNsaXA6dGV4dDtiYWNrZ3JvdW5kLWNsaXA6dGV4dDtjb2xvcjp0cmFuc3BhcmVudDsKICB0ZXh0LXNoYWRvdzowIDAgMjRweCByZ2JhKDU2LDE4OSwyNDgsLjM1KTsKICBmaWx0ZXI6ZHJvcC1zaGFkb3coMCAwIDEwcHggcmdiYSgzNCwyMTEsMjM4LC40KSk7Cn0KLnRhZ2xpbmV7CiAgZm9udC1zaXplOjExcHg7bGV0dGVyLXNwYWNpbmc6MS41cHg7bWFyZ2luLXRvcDoxcHg7Zm9udC13ZWlnaHQ6NjAwOwogIGJhY2tncm91bmQ6bGluZWFyLWdyYWRpZW50KDkwZGVnLCM2N2U4ZjksIzYwYTVmYSk7CiAgLXdlYmtpdC1iYWNrZ3JvdW5kLWNsaXA6dGV4dDtiYWNrZ3JvdW5kLWNsaXA6dGV4dDtjb2xvcjp0cmFuc3BhcmVudDsKICB0ZXh0LXNoYWRvdzowIDAgMTJweCByZ2JhKDU2LDE4OSwyNDgsLjI1KTtvcGFjaXR5Oi45MjsKfQouc3RhdHVzbGluZXtkaXNwbGF5OmZsZXg7YWxpZ24taXRlbXM6Y2VudGVyO2dhcDo4cHg7Zm9udC1zaXplOjEyLjVweDtjb2xvcjp2YXIoLS1tdXQpO21hcmdpbi10b3A6M3B4O2ZsZXgtd3JhcDp3cmFwfQouZG90e3dpZHRoOjlweDtoZWlnaHQ6OXB4O2JvcmRlci1yYWRpdXM6NTAlO2JhY2tncm91bmQ6dmFyKC0tbXV0KTtib3gtc2hhZG93OjAgMCA4cHggY3VycmVudENvbG9yO3RyYW5zaXRpb246LjNzfQouZG90Lm9re2JhY2tncm91bmQ6dmFyKC0tZ3JlZW4pO2NvbG9yOnZhcigtLWdyZWVuKX0KLmRvdC5iYWR7YmFja2dyb3VuZDp2YXIoLS1yb3NlKTtjb2xvcjp2YXIoLS1yb3NlKX0KLyoga2xlaW5lciBPbGxhbWEtSW5kaWthdG9yIG9iZW4gKi8KLm9sbGFtYS1waWxse2Rpc3BsYXk6aW5saW5lLWZsZXg7YWxpZ24taXRlbXM6Y2VudGVyO2dhcDo2cHg7Zm9udC1zaXplOjExcHg7cGFkZGluZzoycHggOXB4O2JvcmRlci1yYWRpdXM6OTk5cHg7CiAgYm9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtiYWNrZ3JvdW5kOnZhcigtLXBhbmVsKTtiYWNrZHJvcC1maWx0ZXI6Ymx1cig4cHgpO2NvbG9yOnZhcigtLW11dCl9Ci5vbGxhbWEtcGlsbCAub3Bkb3R7d2lkdGg6N3B4O2hlaWdodDo3cHg7Ym9yZGVyLXJhZGl1czo1MCU7YmFja2dyb3VuZDp2YXIoLS1tdXQpO2JveC1zaGFkb3c6MCAwIDdweCBjdXJyZW50Q29sb3I7dHJhbnNpdGlvbjouM3N9Ci5vbGxhbWEtcGlsbC5va3tjb2xvcjojYmZmNGZmO2JvcmRlci1jb2xvcjpyZ2JhKDUyLDIxMSwxNTMsLjUpfQoub2xsYW1hLXBpbGwub2sgLm9wZG90e2JhY2tncm91bmQ6dmFyKC0tZ3JlZW4pO2NvbG9yOnZhcigtLWdyZWVuKX0KLm9sbGFtYS1waWxsLndhcm57Y29sb3I6I2ZmZTliODtib3JkZXItY29sb3I6cmdiYSgyNTEsMTkxLDM2LC41KX0KLm9sbGFtYS1waWxsLndhcm4gLm9wZG90e2JhY2tncm91bmQ6dmFyKC0tYW1iZXIpO2NvbG9yOnZhcigtLWFtYmVyKX0KLm9sbGFtYS1waWxsLmJhZHtjb2xvcjojZmZkOWRmO2JvcmRlci1jb2xvcjpyZ2JhKDI1MSwxMTMsMTMzLC41KX0KLm9sbGFtYS1waWxsLmJhZCAub3Bkb3R7YmFja2dyb3VuZDp2YXIoLS1yb3NlKTtjb2xvcjp2YXIoLS1yb3NlKX0KLmhlYWRlciAuc3BhY2Vye2ZsZXg6MX0KLmljb25idG5ze2Rpc3BsYXk6ZmxleDtnYXA6OHB4fQouaWNvbmJ0bnsKICB3aWR0aDo0MnB4O2hlaWdodDo0MnB4O2JvcmRlci1yYWRpdXM6MTJweDtib3JkZXI6MXB4IHNvbGlkIHZhcigtLWxpbmUpOwogIGJhY2tncm91bmQ6dmFyKC0tcGFuZWwpO2JhY2tkcm9wLWZpbHRlcjpibHVyKDhweCk7CiAgY29sb3I6dmFyKC0tdHh0KTtmb250LXNpemU6MThweDtjdXJzb3I6cG9pbnRlcjtkaXNwbGF5OmdyaWQ7cGxhY2UtaXRlbXM6Y2VudGVyOwogIHRyYW5zaXRpb246LjE4czsKfQouaWNvbmJ0bjpob3Zlcntib3JkZXItY29sb3I6dmFyKC0tY3lhbik7Ym94LXNoYWRvdzp2YXIoLS1nbG93KTt0cmFuc2Zvcm06dHJhbnNsYXRlWSgtMXB4KX0KCi8qID09PT09PT09PT09PT09PT09IENvcmUgLyBPcmIgPT09PT09PT09PT09PT09PT0gKi8KLmNvcmUtd3JhcHtkaXNwbGF5OmZsZXg7anVzdGlmeS1jb250ZW50OmNlbnRlcjthbGlnbi1pdGVtczpjZW50ZXI7aGVpZ2h0OjExOHB4O21hcmdpbjotNHB4IDAgNnB4O3Bvc2l0aW9uOnJlbGF0aXZlfQouY29yZXtwb3NpdGlvbjpyZWxhdGl2ZTt3aWR0aDo5NnB4O2hlaWdodDo5NnB4O2Rpc3BsYXk6Z3JpZDtwbGFjZS1pdGVtczpjZW50ZXJ9Ci5jb3JlIC5yaW5newogIHBvc2l0aW9uOmFic29sdXRlO2JvcmRlci1yYWRpdXM6NTAlO2JvcmRlcjoycHggc29saWQgcmdiYSg1NiwxODksMjQ4LC4zNSk7CiAgYW5pbWF0aW9uOnNwaW4gNnMgbGluZWFyIGluZmluaXRlOwp9Ci5jb3JlIC5yMXtpbnNldDowO2JvcmRlci10b3AtY29sb3I6dmFyKC0tY3lhbik7Ym9yZGVyLXJpZ2h0LWNvbG9yOnRyYW5zcGFyZW50fQouY29yZSAucjJ7aW5zZXQ6MTJweDtib3JkZXItYm90dG9tLWNvbG9yOnZhcigtLWJsdWUyKTtib3JkZXItbGVmdC1jb2xvcjp0cmFuc3BhcmVudDthbmltYXRpb24tZHVyYXRpb246NHM7YW5pbWF0aW9uLWRpcmVjdGlvbjpyZXZlcnNlfQouY29yZSAucjN7aW5zZXQ6MjRweDtib3JkZXItdG9wLWNvbG9yOnZhcigtLWJsdWUpO2JvcmRlci1sZWZ0LWNvbG9yOnRyYW5zcGFyZW50O2FuaW1hdGlvbi1kdXJhdGlvbjo4c30KLmNvcmUgLm51Y2xldXN7CiAgd2lkdGg6MzhweDtoZWlnaHQ6MzhweDtib3JkZXItcmFkaXVzOjUwJTsKICBiYWNrZ3JvdW5kOnJhZGlhbC1ncmFkaWVudChjaXJjbGUgYXQgMzUlIDMwJSwjYmZmNGZmLCMyMmQzZWUgNDUlLCMxZDRlZDggMTAwJSk7CiAgYm94LXNoYWRvdzowIDAgMjZweCA2cHggcmdiYSgzNCwyMTEsMjM4LC42NSksMCAwIDYwcHggMTJweCByZ2JhKDU2LDE4OSwyNDgsLjI1KTsKICBhbmltYXRpb246cHVsc2UgMi42cyBlYXNlLWluLW91dCBpbmZpbml0ZTsKfQpAa2V5ZnJhbWVzIHNwaW57dG97dHJhbnNmb3JtOnJvdGF0ZSgzNjBkZWcpfX0KQGtleWZyYW1lcyBwdWxzZXswJSwxMDAle3RyYW5zZm9ybTpzY2FsZSgxKTtvcGFjaXR5Oi45Mn01MCV7dHJhbnNmb3JtOnNjYWxlKDEuMTYpO29wYWNpdHk6MX19Ci8qIFp1c3TDpG5kZTogbmFjaGRlbmtlbiAoc2NobmVsbGVyKSAvIHNwcmVjaGVuICovCi5jb3JlLnRoaW5raW5nIC5yaW5ne2FuaW1hdGlvbi1kdXJhdGlvbjoxLjRzIWltcG9ydGFudH0KLmNvcmUudGhpbmtpbmcgLnIye2FuaW1hdGlvbi1kdXJhdGlvbjoxcyFpbXBvcnRhbnR9Ci5jb3JlLnRoaW5raW5nIC5udWNsZXVze2FuaW1hdGlvbi1kdXJhdGlvbjouOHN9Ci5jb3JlLnNwZWFraW5nIC5udWNsZXVze2FuaW1hdGlvbjpzcGVhayAuNXMgZWFzZS1pbi1vdXQgaW5maW5pdGV9CkBrZXlmcmFtZXMgc3BlYWt7MCUsMTAwJXt0cmFuc2Zvcm06c2NhbGUoMSl9NTAle3RyYW5zZm9ybTpzY2FsZSgxLjI4KTtib3gtc2hhZG93OjAgMCAzNHB4IDEwcHggcmdiYSgzNCwyMTEsMjM4LC44NSl9fQoKLyogPT09PT09PT09PT09PT09PT0gQ2hhdCA9PT09PT09PT09PT09PT09PSAqLwouY2hhdHsKICBmbGV4OjE7b3ZlcmZsb3cteTphdXRvO3BhZGRpbmc6MTBweCA2cHggNHB4O2Rpc3BsYXk6ZmxleDtmbGV4LWRpcmVjdGlvbjpjb2x1bW47Z2FwOjE0cHg7CiAgc2Nyb2xsYmFyLXdpZHRoOnRoaW47c2Nyb2xsYmFyLWNvbG9yOnJnYmEoNTYsMTg5LDI0OCwuNCkgdHJhbnNwYXJlbnQ7Cn0KLmNoYXQ6Oi13ZWJraXQtc2Nyb2xsYmFye3dpZHRoOjhweH0KLmNoYXQ6Oi13ZWJraXQtc2Nyb2xsYmFyLXRodW1ie2JhY2tncm91bmQ6cmdiYSg1NiwxODksMjQ4LC4zNSk7Ym9yZGVyLXJhZGl1czo4cHh9CgoubXNne2Rpc3BsYXk6ZmxleDtnYXA6MTBweDttYXgtd2lkdGg6ODIlO2FuaW1hdGlvbjpmYWRlaW4gLjM1cyBlYXNlIGJvdGh9CkBrZXlmcmFtZXMgZmFkZWlue2Zyb217b3BhY2l0eTowO3RyYW5zZm9ybTp0cmFuc2xhdGVZKDEwcHgpfXRve29wYWNpdHk6MTt0cmFuc2Zvcm06bm9uZX19Ci5tc2cudXNlcnthbGlnbi1zZWxmOmZsZXgtZW5kO2ZsZXgtZGlyZWN0aW9uOnJvdy1yZXZlcnNlfQouYXZhdGFye2ZsZXg6bm9uZTt3aWR0aDozMHB4O2hlaWdodDozMHB4O2JvcmRlci1yYWRpdXM6OXB4O2Rpc3BsYXk6Z3JpZDtwbGFjZS1pdGVtczpjZW50ZXI7Zm9udC1zaXplOjE1cHg7CiAgYmFja2dyb3VuZDp2YXIoLS1wYW5lbCk7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKX0KLmJ1YmJsZXsKICBwYWRkaW5nOjExcHggMTRweDtib3JkZXItcmFkaXVzOjE0cHg7Zm9udC1zaXplOjE0LjVweDtsaW5lLWhlaWdodDoxLjU7CiAgd2hpdGUtc3BhY2U6cHJlLXdyYXA7d29yZC1icmVhazpicmVhay13b3JkOwp9Ci8qIERpbm86IEdsYXMtQnViYmxlICovCi5tc2cuZGlubyAuYnViYmxlewogIGJhY2tncm91bmQ6dmFyKC0tcGFuZWwpO2JhY2tkcm9wLWZpbHRlcjpibHVyKDEwcHgpOwogIGJvcmRlcjoxcHggc29saWQgdmFyKC0tbGluZSk7Ym9yZGVyLXRvcC1sZWZ0LXJhZGl1czo0cHg7CiAgYm94LXNoYWRvdzowIDRweCAyMnB4IHJnYmEoMCwwLDAsLjM1KTsKfQovKiBOdXR6ZXI6IEFremVudC1CdWJibGUgKi8KLm1zZy51c2VyIC5idWJibGV7CiAgYmFja2dyb3VuZDpsaW5lYXItZ3JhZGllbnQoMTM1ZGVnLHJnYmEoMzQsMjExLDIzOCwuMjIpLHJnYmEoOTYsMTY1LDI1MCwuMjApKTsKICBib3JkZXI6MXB4IHNvbGlkIHJnYmEoMzQsMjExLDIzOCwuNDUpO2JvcmRlci10b3AtcmlnaHQtcmFkaXVzOjRweDsKICBib3gtc2hhZG93OjAgMCAxOHB4IHJnYmEoMzQsMjExLDIzOCwuMTgpOwp9Ci8qIEluZm8gLyBGZWhsZXIgLyBMYWJlbCAvIFN5bnRoZXNlICovCi5tc2cuaW5mbyAuYnViYmxle2JhY2tncm91bmQ6dHJhbnNwYXJlbnQ7Ym9yZGVyOjFweCBkYXNoZWQgcmdiYSgxMjQsMTQxLDE4MSwuNCk7Y29sb3I6dmFyKC0tbXV0KTtmb250LXN0eWxlOml0YWxpYztmb250LXNpemU6MTNweH0KLm1zZy5lcnJvciAuYnViYmxle2JhY2tncm91bmQ6cmdiYSgyNTEsMTEzLDEzMywuMTIpO2JvcmRlcjoxcHggc29saWQgdmFyKC0tcm9zZSk7Y29sb3I6I2ZmZDlkZn0KLm1zZy5lcnJvciAuYXZhdGFye2JvcmRlci1jb2xvcjp2YXIoLS1yb3NlKX0KLmxhYmVse2ZvbnQtc2l6ZToxMXB4O2xldHRlci1zcGFjaW5nOi41cHg7dGV4dC10cmFuc2Zvcm06dXBwZXJjYXNlO2NvbG9yOnZhcigtLWN5YW4pO21hcmdpbi1ib3R0b206M3B4O2ZvbnQtd2VpZ2h0OjcwMDtvcGFjaXR5Oi45fQoubXNnLnN5bnRoIC5idWJibGV7CiAgYmFja2dyb3VuZDpsaW5lYXItZ3JhZGllbnQoMTM1ZGVnLHJnYmEoMzQsMjExLDIzOCwuMTYpLHJnYmEoMTI5LDE0MCwyNDgsLjE0KSk7CiAgYm9yZGVyOjFweCBzb2xpZCB2YXIoLS1jeWFuKTtib3gtc2hhZG93OnZhcigtLWdsb3cpOwp9CgovKiBUaXBwLUluZGlrYXRvciAqLwoudHlwaW5ne2Rpc3BsYXk6ZmxleDtnYXA6NXB4O2FsaWduLWl0ZW1zOmNlbnRlcjtwYWRkaW5nOjEzcHggMTZweH0KLnR5cGluZyBzcGFue3dpZHRoOjhweDtoZWlnaHQ6OHB4O2JvcmRlci1yYWRpdXM6NTAlO2JhY2tncm91bmQ6dmFyKC0tY3lhbik7b3BhY2l0eTouNTthbmltYXRpb246Ym91bmNlIDEuMnMgaW5maW5pdGV9Ci50eXBpbmcgc3BhbjpudGgtY2hpbGQoMil7YW5pbWF0aW9uLWRlbGF5Oi4xOHN9Ci50eXBpbmcgc3BhbjpudGgtY2hpbGQoMyl7YW5pbWF0aW9uLWRlbGF5Oi4zNnN9CkBrZXlmcmFtZXMgYm91bmNlezAlLDYwJSwxMDAle3RyYW5zZm9ybTp0cmFuc2xhdGVZKDApO29wYWNpdHk6LjR9MzAle3RyYW5zZm9ybTp0cmFuc2xhdGVZKC02cHgpO29wYWNpdHk6MX19CgovKiA9PT09PT09PT09PT09PT09PSBEaW5vLVNldHVwLUthcnRlID09PT09PT09PT09PT09PT09ICovCi5zZXR1cC1jYXJkewogIGFsaWduLXNlbGY6c3RyZXRjaDttYXgtd2lkdGg6MTAwJTsKICBib3JkZXI6MXB4IHNvbGlkIHZhcigtLWN5YW4pO2JvcmRlci1yYWRpdXM6MTZweDtwYWRkaW5nOjE4cHggMjBweDsKICBiYWNrZ3JvdW5kOmxpbmVhci1ncmFkaWVudCgxNTBkZWcscmdiYSgzNCwyMTEsMjM4LC4xMCkscmdiYSgxMjksMTQwLDI0OCwuMDgpKTsKICBiYWNrZHJvcC1maWx0ZXI6Ymx1cigxMnB4KTtib3gtc2hhZG93OjAgMCAzMHB4IHJnYmEoMzQsMjExLDIzOCwuMTgpLDAgNnB4IDI4cHggcmdiYSgwLDAsMCwuNCk7CiAgYW5pbWF0aW9uOmZhZGVpbiAuNHMgZWFzZSBib3RoOwp9Ci5zZXR1cC1jYXJkIC5zYy10aXRsZXtmb250LXNpemU6MTdweDtmb250LXdlaWdodDo4MDA7bGV0dGVyLXNwYWNpbmc6LjRweDsKICBiYWNrZ3JvdW5kOmxpbmVhci1ncmFkaWVudCg5MGRlZywjYmZmNGZmLCM2MGE1ZmEpOy13ZWJraXQtYmFja2dyb3VuZC1jbGlwOnRleHQ7YmFja2dyb3VuZC1jbGlwOnRleHQ7Y29sb3I6dHJhbnNwYXJlbnQ7CiAgdGV4dC1zaGFkb3c6MCAwIDE4cHggcmdiYSg1NiwxODksMjQ4LC4zKTttYXJnaW4tYm90dG9tOjZweH0KLnNldHVwLWNhcmQgLnNjLXN1Yntmb250LXNpemU6MTNweDtjb2xvcjp2YXIoLS1tdXQpO2xpbmUtaGVpZ2h0OjEuNjttYXJnaW4tYm90dG9tOjE0cHh9Ci5zZXR1cC1jYXJkIC5zYy1zdGVwe21hcmdpbjoxMnB4IDB9Ci5zZXR1cC1jYXJkIC5zYy1zdGVwLWh7Zm9udC1zaXplOjEzLjVweDtmb250LXdlaWdodDo3MDA7Y29sb3I6dmFyKC0tdHh0KTttYXJnaW4tYm90dG9tOjZweDtkaXNwbGF5OmZsZXg7YWxpZ24taXRlbXM6Y2VudGVyO2dhcDo3cHh9Ci5zZXR1cC1jYXJkIC5zYy1zdGVwLWggLm51bXtmbGV4Om5vbmU7d2lkdGg6MjJweDtoZWlnaHQ6MjJweDtib3JkZXItcmFkaXVzOjUwJTtkaXNwbGF5OmdyaWQ7cGxhY2UtaXRlbXM6Y2VudGVyOwogIGZvbnQtc2l6ZToxMnB4O2JhY2tncm91bmQ6cmdiYSgzNCwyMTEsMjM4LC4xNik7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtjb2xvcjp2YXIoLS1jeWFuKX0KLnNldHVwLWNhcmQgYS5zYy1saW5re2NvbG9yOnZhcigtLWJsdWUyKTt0ZXh0LWRlY29yYXRpb246bm9uZTtib3JkZXItYm90dG9tOjFweCBkb3R0ZWQgcmdiYSg5NiwxNjUsMjUwLC41KX0KLnNldHVwLWNhcmQgYS5zYy1saW5rOmhvdmVye2NvbG9yOiNiZmY0ZmY7Ym9yZGVyLWJvdHRvbS1jb2xvcjp2YXIoLS1jeWFuKX0KLnNldHVwLWNhcmQgLnNjLWNvZGVib3h7ZGlzcGxheTpmbGV4O2FsaWduLWl0ZW1zOmNlbnRlcjtnYXA6OHB4O21hcmdpbi10b3A6NnB4fQouc2V0dXAtY2FyZCAuc2MtY29kZXsKICBmbGV4OjE7Zm9udC1mYW1pbHk6IkNvbnNvbGFzIiwiU0YgTW9ubyIsdWktbW9ub3NwYWNlLG1vbm9zcGFjZTtmb250LXNpemU6MTMuNXB4O2NvbG9yOiNiZmY0ZmY7CiAgYmFja2dyb3VuZDpyZ2JhKDIsOCwyMCwuNyk7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtib3JkZXItcmFkaXVzOjEwcHg7cGFkZGluZzo5cHggMTJweDsKICB3aGl0ZS1zcGFjZTpub3dyYXA7b3ZlcmZsb3cteDphdXRvO2JveC1zaGFkb3c6aW5zZXQgMCAwIDE0cHggcmdiYSgzNCwyMTEsMjM4LC4wOCk7Cn0KLnNldHVwLWNhcmQgLnNjLWNvcHl7ZmxleDpub25lO3BhZGRpbmc6OXB4IDExcHg7Ym9yZGVyLXJhZGl1czoxMHB4O2JvcmRlcjoxcHggc29saWQgdmFyKC0tbGluZSk7CiAgYmFja2dyb3VuZDp2YXIoLS1wYW5lbCk7Y29sb3I6dmFyKC0tdHh0KTtmb250OmluaGVyaXQ7Zm9udC1zaXplOjEzcHg7Y3Vyc29yOnBvaW50ZXI7dHJhbnNpdGlvbjouMTZzfQouc2V0dXAtY2FyZCAuc2MtY29weTpob3Zlcntib3JkZXItY29sb3I6dmFyKC0tY3lhbik7Ym94LXNoYWRvdzp2YXIoLS1nbG93KX0KLnNldHVwLWNhcmQgLnNjLW1vZGVsc3tkaXNwbGF5OmZsZXg7ZmxleC13cmFwOndyYXA7Z2FwOjhweDttYXJnaW4tdG9wOjhweH0KLnNldHVwLWNhcmQgLnNjLW1vZGVse3BhZGRpbmc6NnB4IDEycHg7Ym9yZGVyLXJhZGl1czo5OTlweDtib3JkZXI6MXB4IHNvbGlkIHZhcigtLWxpbmUpOwogIGJhY2tncm91bmQ6dmFyKC0tcGFuZWwpO2NvbG9yOnZhcigtLXR4dCk7Zm9udDppbmhlcml0O2ZvbnQtc2l6ZToxMi41cHg7Y3Vyc29yOnBvaW50ZXI7dHJhbnNpdGlvbjouMTZzfQouc2V0dXAtY2FyZCAuc2MtbW9kZWw6aG92ZXJ7Ym9yZGVyLWNvbG9yOnZhcigtLWN5YW4pO2JveC1zaGFkb3c6dmFyKC0tZ2xvdyk7Y29sb3I6I2JmZjRmZn0KLnNldHVwLWNhcmQgLnNjLWFjdGlvbnN7ZGlzcGxheTpmbGV4O2FsaWduLWl0ZW1zOmNlbnRlcjtnYXA6MTBweDtmbGV4LXdyYXA6d3JhcDttYXJnaW4tdG9wOjE2cHh9Ci5zZXR1cC1jYXJkIC5zYy1yZWNoZWNre3BhZGRpbmc6OXB4IDE2cHg7Ym9yZGVyLXJhZGl1czoxMHB4O2JvcmRlcjpub25lO2N1cnNvcjpwb2ludGVyO2ZvbnQ6aW5oZXJpdDtmb250LXNpemU6MTMuNXB4O2ZvbnQtd2VpZ2h0OjYwMDsKICBiYWNrZ3JvdW5kOmxpbmVhci1ncmFkaWVudCgxMzVkZWcsdmFyKC0tY3lhbiksdmFyKC0tYmx1ZTIpKTtjb2xvcjojMDQxMDFmO2JveC1zaGFkb3c6MCAwIDE4cHggcmdiYSgzNCwyMTEsMjM4LC40KTt0cmFuc2l0aW9uOi4xNnN9Ci5zZXR1cC1jYXJkIC5zYy1yZWNoZWNrOmhvdmVye2ZpbHRlcjpicmlnaHRuZXNzKDEuMSl9Ci5zZXR1cC1jYXJkIC5zYy1yZWNoZWNrOmRpc2FibGVke29wYWNpdHk6LjU1O2N1cnNvcjp3YWl0O2JveC1zaGFkb3c6bm9uZX0KLnNldHVwLWNhcmQgLnNjLXNldHRpbmdze2ZvbnQtc2l6ZToxMi41cHg7Y29sb3I6dmFyKC0tbXV0KTtiYWNrZ3JvdW5kOm5vbmU7Ym9yZGVyOm5vbmU7Y3Vyc29yOnBvaW50ZXI7Zm9udDppbmhlcml0OwogIHRleHQtZGVjb3JhdGlvbjp1bmRlcmxpbmU7dGV4dC1kZWNvcmF0aW9uLXN0eWxlOmRvdHRlZDtwYWRkaW5nOjB9Ci5zZXR1cC1jYXJkIC5zYy1zZXR0aW5nczpob3Zlcntjb2xvcjp2YXIoLS1ibHVlMil9Ci5zZXR1cC1jYXJkIC5zYy1zdGF0ZXtmb250LXNpemU6MTIuNXB4O2NvbG9yOnZhcigtLWN5YW4pO21pbi1oZWlnaHQ6MWVtfQoKLyogPT09PT09PT09PT09PT09PT0gUXVpY2stQ2hpcHMgPT09PT09PT09PT09PT09PT0gKi8KLmNoaXBze2Rpc3BsYXk6ZmxleDtmbGV4LXdyYXA6d3JhcDtnYXA6OHB4O3BhZGRpbmc6MTBweCA0cHggOHB4fQouY2hpcHsKICBwYWRkaW5nOjdweCAxM3B4O2JvcmRlci1yYWRpdXM6OTk5cHg7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTsKICBiYWNrZ3JvdW5kOnZhcigtLXBhbmVsKTtjb2xvcjp2YXIoLS10eHQpO2ZvbnQtc2l6ZToxM3B4O2N1cnNvcjpwb2ludGVyO3RyYW5zaXRpb246LjE2czsKICBiYWNrZHJvcC1maWx0ZXI6Ymx1cig4cHgpOwp9Ci5jaGlwOmhvdmVye2JvcmRlci1jb2xvcjp2YXIoLS1jeWFuKTtib3gtc2hhZG93OnZhcigtLWdsb3cpO2NvbG9yOiNiZmY0ZmZ9Ci5jaGlwOmRpc2FibGVke29wYWNpdHk6LjQ7Y3Vyc29yOm5vdC1hbGxvd2VkO2JveC1zaGFkb3c6bm9uZX0KCi8qID09PT09PT09PT09PT09PT09IEVpbmdhYmVsZWlzdGUgPT09PT09PT09PT09PT09PT0gKi8KLmlucHV0YmFyewogIGRpc3BsYXk6ZmxleDthbGlnbi1pdGVtczpmbGV4LWVuZDtnYXA6OXB4O3BhZGRpbmc6MTBweDtib3JkZXItcmFkaXVzOjE2cHg7CiAgYm9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtiYWNrZ3JvdW5kOnZhcigtLXBhbmVsKTtiYWNrZHJvcC1maWx0ZXI6Ymx1cigxMnB4KTsKICBib3gtc2hhZG93OjAgMCAyNnB4IHJnYmEoMzQsMjExLDIzOCwuMTApOwp9CiNpbnB1dHsKICBmbGV4OjE7cmVzaXplOm5vbmU7bWF4LWhlaWdodDoxNDBweDttaW4taGVpZ2h0OjI0cHg7Ym9yZGVyOm5vbmU7b3V0bGluZTpub25lOwogIGJhY2tncm91bmQ6dHJhbnNwYXJlbnQ7Y29sb3I6dmFyKC0tdHh0KTtmb250OmluaGVyaXQ7Zm9udC1zaXplOjE0LjVweDtsaW5lLWhlaWdodDoxLjQ1OwogIHBhZGRpbmc6NnB4IDRweDsKfQojaW5wdXQ6OnBsYWNlaG9sZGVye2NvbG9yOnZhcigtLW11dCl9Ci5pYnRuewogIGZsZXg6bm9uZTt3aWR0aDo0MnB4O2hlaWdodDo0MnB4O2JvcmRlci1yYWRpdXM6MTFweDtib3JkZXI6MXB4IHNvbGlkIHZhcigtLWxpbmUpOwogIGJhY2tncm91bmQ6cmdiYSgyNTUsMjU1LDI1NSwuMDMpO2NvbG9yOnZhcigtLXR4dCk7Zm9udC1zaXplOjE4cHg7Y3Vyc29yOnBvaW50ZXI7CiAgZGlzcGxheTpncmlkO3BsYWNlLWl0ZW1zOmNlbnRlcjt0cmFuc2l0aW9uOi4xNnM7Cn0KLmlidG46aG92ZXJ7Ym9yZGVyLWNvbG9yOnZhcigtLWN5YW4pO2JveC1zaGFkb3c6dmFyKC0tZ2xvdyl9Ci5pYnRuLmFjdGl2ZXtib3JkZXItY29sb3I6dmFyKC0tY3lhbik7Y29sb3I6dmFyKC0tY3lhbik7YmFja2dyb3VuZDpyZ2JhKDM0LDIxMSwyMzgsLjEyKTtib3gtc2hhZG93OnZhcigtLWdsb3cpfQouaWJ0bi5taWMubGlzdGVuaW5ne2NvbG9yOnZhcigtLXJvc2UpO2JvcmRlci1jb2xvcjp2YXIoLS1yb3NlKTtib3gtc2hhZG93OjAgMCAxNnB4IHJnYmEoMjUxLDExMywxMzMsLjYpO2FuaW1hdGlvbjptaWNwdWxzZSAxcyBpbmZpbml0ZX0KQGtleWZyYW1lcyBtaWNwdWxzZXs1MCV7YmFja2dyb3VuZDpyZ2JhKDI1MSwxMTMsMTMzLC4xOCl9fQouaWJ0bi5zZW5kewogIGJhY2tncm91bmQ6bGluZWFyLWdyYWRpZW50KDEzNWRlZyx2YXIoLS1jeWFuKSx2YXIoLS1ibHVlMikpO2NvbG9yOiMwNDEwMWY7Ym9yZGVyOm5vbmU7CiAgYm94LXNoYWRvdzowIDAgMThweCByZ2JhKDM0LDIxMSwyMzgsLjUpOwp9Ci5pYnRuLnNlbmQ6aG92ZXJ7ZmlsdGVyOmJyaWdodG5lc3MoMS4xKX0KLmlidG46ZGlzYWJsZWR7b3BhY2l0eTouNDtjdXJzb3I6bm90LWFsbG93ZWQ7Ym94LXNoYWRvdzpub25lfQoKLyogPT09PT09PT09PT09PT09PT0gUGFuZWxzIChTbGlkZS1PdmVyKSA9PT09PT09PT09PT09PT09PSAqLwoub3ZlcmxheXtwb3NpdGlvbjpmaXhlZDtpbnNldDowO3otaW5kZXg6NDA7YmFja2dyb3VuZDpyZ2JhKDIsNCwxMCwuNik7YmFja2Ryb3AtZmlsdGVyOmJsdXIoM3B4KTsKICBvcGFjaXR5OjA7cG9pbnRlci1ldmVudHM6bm9uZTt0cmFuc2l0aW9uOi4yNXN9Ci5vdmVybGF5Lm9wZW57b3BhY2l0eToxO3BvaW50ZXItZXZlbnRzOmF1dG99Ci5wYW5lbHsKICBwb3NpdGlvbjpmaXhlZDt0b3A6MDtyaWdodDowO2hlaWdodDoxMDAlO3dpZHRoOm1pbig0NjBweCw5NHZ3KTt6LWluZGV4OjQxOwogIGJhY2tncm91bmQ6bGluZWFyLWdyYWRpZW50KDE4MGRlZyx2YXIoLS1iZzIpLHZhcigtLWJnKSk7CiAgYm9yZGVyLWxlZnQ6MXB4IHNvbGlkIHZhcigtLWxpbmUpO2JveC1zaGFkb3c6LTIwcHggMCA2MHB4IHJnYmEoMCwwLDAsLjU1KTsKICB0cmFuc2Zvcm06dHJhbnNsYXRlWCgxMDAlKTt0cmFuc2l0aW9uOnRyYW5zZm9ybSAuMjhzIGN1YmljLWJlemllciguNCwuMCwuMiwxKTsKICBkaXNwbGF5OmZsZXg7ZmxleC1kaXJlY3Rpb246Y29sdW1uOwp9Ci5wYW5lbC5vcGVue3RyYW5zZm9ybTpub25lfQoucGFuZWwtaGVhZHtkaXNwbGF5OmZsZXg7YWxpZ24taXRlbXM6Y2VudGVyO2dhcDoxMHB4O3BhZGRpbmc6MThweCAyMHB4IDEycHg7Ym9yZGVyLWJvdHRvbToxcHggc29saWQgdmFyKC0tbGluZSl9Ci5wYW5lbC1oZWFkIGgye21hcmdpbjowO2ZvbnQtc2l6ZToxN3B4O2ZvbnQtd2VpZ2h0OjcwMDtsZXR0ZXItc3BhY2luZzouNXB4fQoucGFuZWwtaGVhZCAuY2xvc2V7bWFyZ2luLWxlZnQ6YXV0bzt3aWR0aDozNHB4O2hlaWdodDozNHB4O2JvcmRlci1yYWRpdXM6OXB4O2JvcmRlcjoxcHggc29saWQgdmFyKC0tbGluZSk7CiAgYmFja2dyb3VuZDp0cmFuc3BhcmVudDtjb2xvcjp2YXIoLS10eHQpO2ZvbnQtc2l6ZToxOHB4O2N1cnNvcjpwb2ludGVyfQoucGFuZWwtaGVhZCAuY2xvc2U6aG92ZXJ7Ym9yZGVyLWNvbG9yOnZhcigtLXJvc2UpO2NvbG9yOnZhcigtLXJvc2UpfQoucGFuZWwtYm9keXtmbGV4OjE7b3ZlcmZsb3cteTphdXRvO3BhZGRpbmc6MTZweCAyMHB4IDI4cHg7c2Nyb2xsYmFyLXdpZHRoOnRoaW47c2Nyb2xsYmFyLWNvbG9yOnJnYmEoNTYsMTg5LDI0OCwuNCkgdHJhbnNwYXJlbnR9Ci5wYW5lbC1ib2R5Ojotd2Via2l0LXNjcm9sbGJhcnt3aWR0aDo4cHh9Ci5wYW5lbC1ib2R5Ojotd2Via2l0LXNjcm9sbGJhci10aHVtYntiYWNrZ3JvdW5kOnJnYmEoNTYsMTg5LDI0OCwuMzUpO2JvcmRlci1yYWRpdXM6OHB4fQoKLnNlY3R7Y29sb3I6dmFyKC0tY3lhbik7Zm9udC1zaXplOjEycHg7bGV0dGVyLXNwYWNpbmc6LjZweDt0ZXh0LXRyYW5zZm9ybTp1cHBlcmNhc2U7Zm9udC13ZWlnaHQ6NzAwO21hcmdpbjoxOHB4IDAgOHB4fQouc2VjdDpmaXJzdC1jaGlsZHttYXJnaW4tdG9wOjB9Ci5maWVsZHttYXJnaW4tYm90dG9tOjExcHh9Ci5maWVsZCBsYWJlbHtkaXNwbGF5OmJsb2NrO2ZvbnQtc2l6ZToxMnB4O2NvbG9yOnZhcigtLW11dCk7bWFyZ2luLWJvdHRvbTo0cHh9Ci5maWVsZCBpbnB1dCwuZmllbGQgc2VsZWN0LC5maWVsZCB0ZXh0YXJlYXsKICB3aWR0aDoxMDAlO3BhZGRpbmc6OXB4IDExcHg7Ym9yZGVyLXJhZGl1czo5cHg7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTsKICBiYWNrZ3JvdW5kOnJnYmEoMjU1LDI1NSwyNTUsLjAzKTtjb2xvcjp2YXIoLS10eHQpO2ZvbnQ6aW5oZXJpdDtmb250LXNpemU6MTMuNXB4O291dGxpbmU6bm9uZTsKfQouZmllbGQgaW5wdXQ6Zm9jdXMsLmZpZWxkIHNlbGVjdDpmb2N1cywuZmllbGQgdGV4dGFyZWE6Zm9jdXN7Ym9yZGVyLWNvbG9yOnZhcigtLWN5YW4pO2JveC1zaGFkb3c6MCAwIDAgMnB4IHJnYmEoMzQsMjExLDIzOCwuMTgpfQouZmllbGQgc2VsZWN0IG9wdGlvbntiYWNrZ3JvdW5kOnZhcigtLXBhbmVsLXNvbGlkKX0KLmZpZWxkIHRleHRhcmVhe3Jlc2l6ZTp2ZXJ0aWNhbDttaW4taGVpZ2h0OjU0cHh9Ci5oaW50e2ZvbnQtc2l6ZToxMS41cHg7Y29sb3I6dmFyKC0tbXV0KTtsaW5lLWhlaWdodDoxLjY7bWFyZ2luLXRvcDo2cHh9Ci5oaW50IGNvZGV7Y29sb3I6dmFyKC0tYmx1ZTIpO2JhY2tncm91bmQ6cmdiYSg1NiwxODksMjQ4LC4wOCk7cGFkZGluZzoxcHggNXB4O2JvcmRlci1yYWRpdXM6NXB4fQoKLmJ0bnsKICBwYWRkaW5nOjEwcHggMTZweDtib3JkZXItcmFkaXVzOjEwcHg7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTsKICBiYWNrZ3JvdW5kOnZhcigtLXBhbmVsKTtjb2xvcjp2YXIoLS10eHQpO2ZvbnQ6aW5oZXJpdDtmb250LXNpemU6MTMuNXB4O2ZvbnQtd2VpZ2h0OjYwMDtjdXJzb3I6cG9pbnRlcjt0cmFuc2l0aW9uOi4xNnM7Cn0KLmJ0bjpob3Zlcntib3JkZXItY29sb3I6dmFyKC0tY3lhbik7Ym94LXNoYWRvdzp2YXIoLS1nbG93KX0KLmJ0bi5wcmltYXJ5e2JhY2tncm91bmQ6bGluZWFyLWdyYWRpZW50KDEzNWRlZyx2YXIoLS1jeWFuKSx2YXIoLS1ibHVlMikpO2NvbG9yOiMwNDEwMWY7Ym9yZGVyOm5vbmU7Ym94LXNoYWRvdzowIDAgMThweCByZ2JhKDM0LDIxMSwyMzgsLjQpfQouYnRuLmRhbmdlcntib3JkZXItY29sb3I6cmdiYSgyNTEsMTEzLDEzMywuNSk7Y29sb3I6I2ZmZDlkZn0KLmJ0bi5kYW5nZXI6aG92ZXJ7Ym9yZGVyLWNvbG9yOnZhcigtLXJvc2UpO2JveC1zaGFkb3c6MCAwIDE0cHggcmdiYSgyNTEsMTEzLDEzMywuNCl9Ci5idG4uc217cGFkZGluZzo2cHggMTFweDtmb250LXNpemU6MTJweH0KLmJ0bnJvd3tkaXNwbGF5OmZsZXg7Z2FwOjlweDtmbGV4LXdyYXA6d3JhcDttYXJnaW4tdG9wOjE0cHh9CgovKiBVbXNhdHotQmFubmVyIChLdW5kZW4pICovCi5yZXZlbnVlewogIGJvcmRlcjoxcHggc29saWQgdmFyKC0tbGluZSk7Ym9yZGVyLXJhZGl1czoxM3B4O3BhZGRpbmc6MTRweCAxNnB4O21hcmdpbi1ib3R0b206MTRweDsKICBiYWNrZ3JvdW5kOmxpbmVhci1ncmFkaWVudCgxMzVkZWcscmdiYSg1MiwyMTEsMTUzLC4xMCkscmdiYSgzNCwyMTEsMjM4LC4wNikpOwp9Ci5yZXZlbnVlIC5iaWd7Zm9udC1zaXplOjI0cHg7Zm9udC13ZWlnaHQ6ODAwO2NvbG9yOnZhcigtLWdyZWVuKTt0ZXh0LXNoYWRvdzowIDAgMTZweCByZ2JhKDUyLDIxMSwxNTMsLjM1KX0KLnJldmVudWUgLnN1Yntmb250LXNpemU6MTJweDtjb2xvcjp2YXIoLS1tdXQpO21hcmdpbi10b3A6M3B4fQoKLyogS3VuZGVuLUthcnRlbiAqLwouY3VzdHtib3JkZXI6MXB4IHNvbGlkIHZhcigtLWxpbmUpO2JvcmRlci1yYWRpdXM6MTJweDtwYWRkaW5nOjEycHggMTRweDttYXJnaW4tYm90dG9tOjEwcHg7YmFja2dyb3VuZDp2YXIoLS1wYW5lbCl9Ci5jdXN0IC50b3B7ZGlzcGxheTpmbGV4O2FsaWduLWl0ZW1zOmNlbnRlcjtnYXA6OHB4O2ZsZXgtd3JhcDp3cmFwfQouY3VzdCAubmFtZXtmb250LXdlaWdodDo3MDA7Zm9udC1zaXplOjE0LjVweH0KLmN1c3QgLmJhZGdle2ZvbnQtc2l6ZToxMC41cHg7cGFkZGluZzoycHggOHB4O2JvcmRlci1yYWRpdXM6OTk5cHg7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtjb2xvcjp2YXIoLS1jeWFuKX0KLmN1c3QgLm1ldGF7Zm9udC1zaXplOjEyLjVweDtjb2xvcjp2YXIoLS1tdXQpO21hcmdpbi10b3A6NHB4O2xpbmUtaGVpZ2h0OjEuNX0KLmN1c3QgLnByaWNle2NvbG9yOnZhcigtLWdyZWVuKTtmb250LXdlaWdodDo2MDB9Ci5jdXN0IC5hY3Rpb25ze2Rpc3BsYXk6ZmxleDtnYXA6N3B4O21hcmdpbi10b3A6OXB4fQoKLyogR2Vkw6RjaHRuaXMgKi8KLmZhY3RsaXN0e2xpc3Qtc3R5bGU6bm9uZTttYXJnaW46MDtwYWRkaW5nOjB9Ci5mYWN0bGlzdCBsaXtwYWRkaW5nOjhweCAxMXB4O2JvcmRlcjoxcHggc29saWQgdmFyKC0tbGluZSk7Ym9yZGVyLXJhZGl1czo5cHg7bWFyZ2luLWJvdHRvbTo3cHg7Zm9udC1zaXplOjEzLjVweDtiYWNrZ3JvdW5kOnZhcigtLXBhbmVsKX0KLmZhY3RsaXN0IGxpOjpiZWZvcmV7Y29udGVudDoi4oCiICI7Y29sb3I6dmFyKC0tY3lhbil9Ci5qb3VybmFse2ZvbnQtc2l6ZToxMi41cHg7Y29sb3I6dmFyKC0tbXV0KTtsaW5lLWhlaWdodDoxLjd9Ci5qb3VybmFsIC5ke2NvbG9yOnZhcigtLWJsdWUyKX0KLmVtcHR5e2NvbG9yOnZhcigtLW11dCk7Zm9udC1zdHlsZTppdGFsaWM7Zm9udC1zaXplOjEzcHg7cGFkZGluZzo2cHggMH0KCkBtZWRpYShtYXgtd2lkdGg6NTYwcHgpewogIC53b3JkbWFya3tmb250LXNpemU6MjJweDtsZXR0ZXItc3BhY2luZzozcHh9CiAgLm1zZ3ttYXgtd2lkdGg6OTIlfQogIC5jb3JlLXdyYXB7aGVpZ2h0Ojk2cHh9CiAgLmNvcmV7d2lkdGg6NzhweDtoZWlnaHQ6NzhweH0KfQo8L3N0eWxlPgo8L2hlYWQ+Cjxib2R5Pgo8ZGl2IGNsYXNzPSJhcHAiPgoKICA8IS0tIEtvcGZ6ZWlsZSAtLT4KICA8ZGl2IGNsYXNzPSJoZWFkZXIiPgogICAgPGRpdiBjbGFzcz0iYnJhbmQiPgogICAgICA8ZGl2PgogICAgICAgIDxkaXYgY2xhc3M9IndvcmRtYXJrIj5ESU5PPC9kaXY+CiAgICAgICAgPGRpdiBjbGFzcz0idGFnbGluZSI+ZGVpbiBlaWdlbmVyIEphcnZpcyDCtyBsw6R1ZnQgbG9rYWw8L2Rpdj4KICAgICAgICA8ZGl2IGNsYXNzPSJzdGF0dXNsaW5lIj4KICAgICAgICAgIDxzcGFuIGlkPSJzdGF0dXNEb3QiIGNsYXNzPSJkb3QiPjwvc3Bhbj4KICAgICAgICAgIDxzcGFuIGlkPSJicmFpblRleHQiPnZlcmJpbmRl4oCmPC9zcGFuPgogICAgICAgICAgPHNwYW4gaWQ9Im9sbGFtYVBpbGwiIGNsYXNzPSJvbGxhbWEtcGlsbCIgc3R5bGU9ImRpc3BsYXk6bm9uZSI+PHNwYW4gY2xhc3M9Im9wZG90Ij48L3NwYW4+PHNwYW4gaWQ9Im9sbGFtYVBpbGxUZXh0Ij5sb2thbDwvc3Bhbj48L3NwYW4+CiAgICAgICAgPC9kaXY+CiAgICAgIDwvZGl2PgogICAgPC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJzcGFjZXIiPjwvZGl2PgogICAgPGRpdiBjbGFzcz0iaWNvbmJ0bnMiPgogICAgICA8YnV0dG9uIGNsYXNzPSJpY29uYnRuIiB0aXRsZT0iS3VuZGVuIiBvbmNsaWNrPSJvcGVuUGFuZWwoJ2N1c3RvbWVycycpIj7wn5GlPC9idXR0b24+CiAgICAgIDxidXR0b24gY2xhc3M9Imljb25idG4iIHRpdGxlPSJHZWTDpGNodG5pcyIgb25jbGljaz0ib3BlblBhbmVsKCdtZW1vcnknKSI+8J+noDwvYnV0dG9uPgogICAgICA8YnV0dG9uIGNsYXNzPSJpY29uYnRuIiB0aXRsZT0iRWluc3RlbGx1bmdlbiIgb25jbGljaz0ib3BlblBhbmVsKCdzZXR0aW5ncycpIj7impk8L2J1dHRvbj4KICAgIDwvZGl2PgogIDwvZGl2PgoKICA8IS0tIENvcmUgLyBPcmIgLS0+CiAgPGRpdiBjbGFzcz0iY29yZS13cmFwIj4KICAgIDxkaXYgY2xhc3M9ImNvcmUiIGlkPSJjb3JlIj4KICAgICAgPGRpdiBjbGFzcz0icmluZyByMSI+PC9kaXY+CiAgICAgIDxkaXYgY2xhc3M9InJpbmcgcjIiPjwvZGl2PgogICAgICA8ZGl2IGNsYXNzPSJyaW5nIHIzIj48L2Rpdj4KICAgICAgPGRpdiBjbGFzcz0ibnVjbGV1cyI+PC9kaXY+CiAgICA8L2Rpdj4KICA8L2Rpdj4KCiAgPCEtLSBDaGF0IC0tPgogIDxkaXYgY2xhc3M9ImNoYXQiIGlkPSJjaGF0Ij48L2Rpdj4KCiAgPCEtLSBRdWljay1DaGlwcyAtLT4KICA8ZGl2IGNsYXNzPSJjaGlwcyI+CiAgICA8YnV0dG9uIGNsYXNzPSJjaGlwIiBvbmNsaWNrPSJxdWlja1BsYW4oKSI+8J+ThSBXb2NoZW5wbGFuPC9idXR0b24+CiAgICA8YnV0dG9uIGNsYXNzPSJjaGlwIiBvbmNsaWNrPSJxdWlja1RvZGF5KCkiPuKYgO+4jyBIZXV0ZTwvYnV0dG9uPgogICAgPGJ1dHRvbiBjbGFzcz0iY2hpcCIgb25jbGljaz0icXVpY2tUZWFtKCkiPvCfpJYgVGVhbS1BdWZ0cmFnPC9idXR0b24+CiAgICA8YnV0dG9uIGNsYXNzPSJjaGlwIiBvbmNsaWNrPSJxdWlja0xlYXJuKCkiPvCfp6AgTGVybmVuPC9idXR0b24+CiAgICA8YnV0dG9uIGNsYXNzPSJjaGlwIiBvbmNsaWNrPSJxdWlja0NvdW5jaWwoKSI+8J+noPCfp6Dwn6egIFJhdCBkZXIgS0lzPC9idXR0b24+CiAgPC9kaXY+CgogIDwhLS0gRWluZ2FiZWxlaXN0ZSAtLT4KICA8ZGl2IGNsYXNzPSJpbnB1dGJhciI+CiAgICA8dGV4dGFyZWEgaWQ9ImlucHV0IiByb3dzPSIxIiBwbGFjZWhvbGRlcj0iU2NocmVpYiBEaW5vIHdhc+KApiAoRW50ZXIgc2VuZGVuIMK3IFNoaWZ0K0VudGVyIG5ldWUgWmVpbGUpIj48L3RleHRhcmVhPgogICAgPGJ1dHRvbiBjbGFzcz0iaWJ0biBtaWMiIGlkPSJtaWNCdG4iIHRpdGxlPSJTcHJlY2hlbiIgb25jbGljaz0idG9nZ2xlTWljKCkiPvCfjqQ8L2J1dHRvbj4KICAgIDxidXR0b24gY2xhc3M9ImlidG4iIGlkPSJ2b2ljZUJ0biIgdGl0bGU9IlNwcmFjaGF1c2dhYmUgYW4vYXVzIiBvbmNsaWNrPSJ0b2dnbGVWb2ljZSgpIj7wn5SKPC9idXR0b24+CiAgICA8c2VsZWN0IGlkPSJ2b2ljZVNlbGVjdCIgdGl0bGU9IlN0aW1tZSB3w6RobGVuIOKAlCBTdGFuZGFyZDogYXV0b21hdGlzY2ggZGllIGJlc3RlLCBmbMO8c3NpZ2UgZGV1dHNjaGUgU3RpbW1lIiBvbmNoYW5nZT0ib25Wb2ljZVNlbGVjdCgpIiBzdHlsZT0ibWF4LXdpZHRoOjE2MHB4O2JhY2tncm91bmQ6IzBiMTUyNjtjb2xvcjojYmZlOWY1O2JvcmRlcjoxcHggc29saWQgcmdiYSgxMjAsMjAwLDIzMCwuMjgpO2JvcmRlci1yYWRpdXM6OXB4O2ZvbnQtc2l6ZToxMXB4O3BhZGRpbmc6NXB4IDZweDtvdXRsaW5lOm5vbmU7Ij48L3NlbGVjdD4KICAgIDxidXR0b24gY2xhc3M9ImlidG4gc2VuZCIgaWQ9InNlbmRCdG4iIHRpdGxlPSJTZW5kZW4iIG9uY2xpY2s9InNlbmQoKSI+4p6kPC9idXR0b24+CiAgPC9kaXY+CjwvZGl2PgoKPCEtLSA9PT09PT09PT09PT09PT09PT09PT0gUGFuZWxzID09PT09PT09PT09PT09PT09PT09PSAtLT4KPGRpdiBjbGFzcz0ib3ZlcmxheSIgaWQ9Im92ZXJsYXkiIG9uY2xpY2s9ImNsb3NlUGFuZWxzKCkiPjwvZGl2PgoKPCEtLSBFaW5zdGVsbHVuZ2VuIC0tPgo8YXNpZGUgY2xhc3M9InBhbmVsIiBpZD0icGFuZWwtc2V0dGluZ3MiPgogIDxkaXYgY2xhc3M9InBhbmVsLWhlYWQiPjxzcGFuPuKamTwvc3Bhbj48aDI+RWluc3RlbGx1bmdlbjwvaDI+PGJ1dHRvbiBjbGFzcz0iY2xvc2UiIG9uY2xpY2s9ImNsb3NlUGFuZWxzKCkiPuKclTwvYnV0dG9uPjwvZGl2PgogIDxkaXYgY2xhc3M9InBhbmVsLWJvZHkiIGlkPSJzZXR0aW5nc0JvZHkiPjxkaXYgY2xhc3M9ImVtcHR5Ij5sw6RkdOKApjwvZGl2PjwvZGl2Pgo8L2FzaWRlPgoKPCEtLSBLdW5kZW4gLS0+Cjxhc2lkZSBjbGFzcz0icGFuZWwiIGlkPSJwYW5lbC1jdXN0b21lcnMiPgogIDxkaXYgY2xhc3M9InBhbmVsLWhlYWQiPjxzcGFuPvCfkaU8L3NwYW4+PGgyPkt1bmRlbjwvaDI+PGJ1dHRvbiBjbGFzcz0iY2xvc2UiIG9uY2xpY2s9ImNsb3NlUGFuZWxzKCkiPuKclTwvYnV0dG9uPjwvZGl2PgogIDxkaXYgY2xhc3M9InBhbmVsLWJvZHkiIGlkPSJjdXN0b21lcnNCb2R5Ij48ZGl2IGNsYXNzPSJlbXB0eSI+bMOkZHTigKY8L2Rpdj48L2Rpdj4KPC9hc2lkZT4KCjwhLS0gR2Vkw6RjaHRuaXMgLS0+Cjxhc2lkZSBjbGFzcz0icGFuZWwiIGlkPSJwYW5lbC1tZW1vcnkiPgogIDxkaXYgY2xhc3M9InBhbmVsLWhlYWQiPjxzcGFuPvCfp6A8L3NwYW4+PGgyPkdlZMOkY2h0bmlzPC9oMj48YnV0dG9uIGNsYXNzPSJjbG9zZSIgb25jbGljaz0iY2xvc2VQYW5lbHMoKSI+4pyVPC9idXR0b24+PC9kaXY+CiAgPGRpdiBjbGFzcz0icGFuZWwtYm9keSIgaWQ9Im1lbW9yeUJvZHkiPjxkaXYgY2xhc3M9ImVtcHR5Ij5sw6RkdOKApjwvZGl2PjwvZGl2Pgo8L2FzaWRlPgoKPHNjcmlwdD4KInVzZSBzdHJpY3QiOwovKiA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KICAgRElOTyBLSSDigJQgRnJvbnRlbmQtTG9naWsKICAgU3ByaWNodCBwZXIgZmV0Y2goKSBtaXQgZGVtIGxva2FsZW4gU2VydmVyIChnbGVpY2hlciBPcmlnaW4pLgogICA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0gKi8KCi8vIC0tLS0gWnVzdGFuZCAtLS0tCmNvbnN0IHN0YXRlID0gewogIG1lc3NhZ2VzOiBbXSwgICAgICAgICAgLy8gQ2hhdC1IaXN0b3JpZSB7cm9sZSwgY29udGVudH0KICByZWFkeTogZmFsc2UsCiAgYXNzaXN0YW50TmFtZTogIkRpbm8iLAogIHVzZXJOYW1lOiAiQm9zcyIsCiAgYnVzeTogZmFsc2UsCiAgdm9pY2VPbjogZmFsc2UsICAgICAgICAvLyBTcHJhY2hhdXNnYWJlIGFuL2F1cwogIHN0YXR1c1ZhbHVlczogWyJMZWFkIiwiQW5nZWJvdCIsIkFrdGl2IiwiQmV6YWhsdCIsIlBhdXNpZXJ0IiwiQmVlbmRldCJdLAogIHByb3ZpZGVyOiBudWxsLCAgICAgICAgLy8gIm9sbGFtYSIgfCAiY2xhdWRlIiB8ICJvcGVuYWkiIHwgImdlbWluaSIKICBhdXRvUmVjaGVja0RvbmU6IGZhbHNlLC8vIGVpbm1hbGlnZXMgQXV0by1SZWNoZWNrIGJlaW0gZXJzdGVuIExhZGVuCn07CgovLyAtLS0tIERPTS1LdXJ6aGVsZmVyIC0tLS0KY29uc3QgJCA9IChpZCkgPT4gZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoaWQpOwpjb25zdCBjaGF0RWwgPSAkKCJjaGF0Iik7CmNvbnN0IGNvcmVFbCA9ICQoImNvcmUiKTsKY29uc3QgaW5wdXRFbCA9ICQoImlucHV0Iik7CgovLyAtLS0tIEhpbGZzZnVua3Rpb25lbiAtLS0tCmZ1bmN0aW9uIGV1cm8oeCl7CiAgY29uc3QgbiA9IE51bWJlcih4KSB8fCAwOwogIHJldHVybiBuLnRvTG9jYWxlU3RyaW5nKCJkZS1ERSIse21heGltdW1GcmFjdGlvbkRpZ2l0czowfSkgKyAiIOKCrCI7Cn0KZnVuY3Rpb24gZXNjKHMpeyAvLyB3aXIgbnV0emVuIG9obmVoaW4gdGV4dENvbnRlbnQsIGRpZXMgbnVyIGbDvHIgc2ljaGVyZSBBdHRyaWJ1dC1mcmVpZSBBbnplaWdlCiAgcmV0dXJuIFN0cmluZyhzID09IG51bGwgPyAiIiA6IHMpOwp9CgovLyAtLS0tIENvcmUtQW5pbWF0aW9uZW4gLS0tLQpmdW5jdGlvbiBzZXRUaGlua2luZyhvbil7IGNvcmVFbC5jbGFzc0xpc3QudG9nZ2xlKCJ0aGlua2luZyIsIG9uKTsgfQpmdW5jdGlvbiBzZXRTcGVha2luZyhvbil7IGNvcmVFbC5jbGFzc0xpc3QudG9nZ2xlKCJzcGVha2luZyIsIG9uKTsgfQoKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09Ci8vICBDaGF0LUFuemVpZ2UKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09Ci8qKgogKiBGw7xndCBlaW5lIEJ1YmJsZSBoaW56dS4gSW5oYWx0IHdpcmQgdmlhIHRleHRDb250ZW50IGdlc2V0enQgKGtlaW4gWFNTKS4KICoga2luZDogImRpbm8iIHwgInVzZXIiIHwgImluZm8iIHwgImVycm9yIiB8ICJzeW50aCIgfCAiY291bmNpbCIKICogbGFiZWw6IG9wdGlvbmFsZXMgTGFiZWwgKHouQi4gS0ktTmFtZSkKICovCmZ1bmN0aW9uIGFkZEJ1YmJsZShraW5kLCB0ZXh0LCBsYWJlbCl7CiAgY29uc3Qgd3JhcCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOwogIGNvbnN0IGNscyA9IChraW5kID09PSAic3ludGgiIHx8IGtpbmQgPT09ICJjb3VuY2lsIikgPyAiZGlubyIgOiBraW5kOwogIHdyYXAuY2xhc3NOYW1lID0gIm1zZyAiICsgKGtpbmQgPT09ICJzeW50aCIgPyAiZGlubyBzeW50aCIgOiBjbHMpOwoKICAvLyBBdmF0YXIgbnVyIGbDvHIgRGluby0vTnV0emVyLS9GZWhsZXItQnViYmxlcwogIGlmIChraW5kID09PSAiZGlubyIgfHwga2luZCA9PT0gInN5bnRoIiB8fCBraW5kID09PSAiY291bmNpbCIpewogICAgY29uc3QgYSA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBhLmNsYXNzTmFtZT0iYXZhdGFyIjsgYS50ZXh0Q29udGVudD0i8J+mliI7IHdyYXAuYXBwZW5kQ2hpbGQoYSk7CiAgfSBlbHNlIGlmIChraW5kID09PSAidXNlciIpewogICAgY29uc3QgYSA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBhLmNsYXNzTmFtZT0iYXZhdGFyIjsgYS50ZXh0Q29udGVudD0i8J+nkSI7IHdyYXAuYXBwZW5kQ2hpbGQoYSk7CiAgfSBlbHNlIGlmIChraW5kID09PSAiZXJyb3IiKXsKICAgIGNvbnN0IGEgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgYS5jbGFzc05hbWU9ImF2YXRhciI7IGEudGV4dENvbnRlbnQ9IuKaoO+4jyI7IHdyYXAuYXBwZW5kQ2hpbGQoYSk7CiAgfQoKICBjb25zdCBiID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IGIuY2xhc3NOYW1lPSJidWJibGUiOwogIGlmIChsYWJlbCl7CiAgICBjb25zdCBsID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IGwuY2xhc3NOYW1lPSJsYWJlbCI7IGwudGV4dENvbnRlbnQgPSBsYWJlbDsKICAgIGIuYXBwZW5kQ2hpbGQobCk7CiAgICBjb25zdCB0ID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IHQudGV4dENvbnRlbnQgPSB0ZXh0OyBiLmFwcGVuZENoaWxkKHQpOwogIH0gZWxzZSB7CiAgICBiLnRleHRDb250ZW50ID0gdGV4dDsKICB9CiAgd3JhcC5hcHBlbmRDaGlsZChiKTsKICBjaGF0RWwuYXBwZW5kQ2hpbGQod3JhcCk7CiAgc2Nyb2xsRG93bigpOwogIHJldHVybiB3cmFwOwp9CgpmdW5jdGlvbiBzY3JvbGxEb3duKCl7IHJlcXVlc3RBbmltYXRpb25GcmFtZSgoKT0+eyBjaGF0RWwuc2Nyb2xsVG9wID0gY2hhdEVsLnNjcm9sbEhlaWdodDsgfSk7IH0KCi8vIFRpcHAtSW5kaWthdG9yCmxldCB0eXBpbmdFbCA9IG51bGw7CmZ1bmN0aW9uIHNob3dUeXBpbmcoKXsKICBpZiAodHlwaW5nRWwpIHJldHVybjsKICB0eXBpbmdFbCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOwogIHR5cGluZ0VsLmNsYXNzTmFtZSA9ICJtc2cgZGlubyI7CiAgdHlwaW5nRWwuaW5uZXJIVE1MID0gJzxkaXYgY2xhc3M9ImF2YXRhciI+8J+mljwvZGl2PjxkaXYgY2xhc3M9ImJ1YmJsZSI+PGRpdiBjbGFzcz0idHlwaW5nIj48c3Bhbj48L3NwYW4+PHNwYW4+PC9zcGFuPjxzcGFuPjwvc3Bhbj48L2Rpdj48L2Rpdj4nOwogIGNoYXRFbC5hcHBlbmRDaGlsZCh0eXBpbmdFbCk7CiAgc2Nyb2xsRG93bigpOwp9CmZ1bmN0aW9uIGhpZGVUeXBpbmcoKXsgaWYgKHR5cGluZ0VsKXsgdHlwaW5nRWwucmVtb3ZlKCk7IHR5cGluZ0VsID0gbnVsbDsgfSB9CgovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KLy8gIE5ldHp3ZXJrCi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQphc3luYyBmdW5jdGlvbiBhcGkocGF0aCwgbWV0aG9kLCBib2R5KXsKICBjb25zdCBvcHQgPSB7IG1ldGhvZDogbWV0aG9kIHx8ICJHRVQiLCBoZWFkZXJzOnt9IH07CiAgaWYgKGJvZHkgIT09IHVuZGVmaW5lZCl7IG9wdC5oZWFkZXJzWyJDb250ZW50LVR5cGUiXT0iYXBwbGljYXRpb24vanNvbiI7IG9wdC5ib2R5ID0gSlNPTi5zdHJpbmdpZnkoYm9keSk7IH0KICBjb25zdCByZXMgPSBhd2FpdCBmZXRjaChwYXRoLCBvcHQpOwogIC8vIFZlcnN1Y2hlIEpTT04genUgbGVzZW4g4oCTIGF1Y2ggYmVpIDR4eC81eHgga2FubiBlaW4ge2Vycm9yfSBrb21tZW4KICBsZXQgZGF0YTsKICB0cnkgeyBkYXRhID0gYXdhaXQgcmVzLmpzb24oKTsgfQogIGNhdGNoKGUpeyB0aHJvdyBuZXcgRXJyb3IoIlVuZ8O8bHRpZ2UgQW50d29ydCB2b20gU2VydmVyIChrZWluIEpTT04pLiIpOyB9CiAgcmV0dXJuIGRhdGE7Cn0KCi8vIEJ1c3ktWnVzdGFuZCAoc3BlcnJ0IFNlbmRlbiArIENoaXBzIHfDpGhyZW5kIGVpbmVyIEFuZnJhZ2UpCmZ1bmN0aW9uIHNldEJ1c3kob24pewogIHN0YXRlLmJ1c3kgPSBvbjsKICBzZXRUaGlua2luZyhvbik7CiAgJCgic2VuZEJ0biIpLmRpc2FibGVkID0gb247CiAgZG9jdW1lbnQucXVlcnlTZWxlY3RvckFsbCgiLmNoaXAiKS5mb3JFYWNoKGMgPT4gYy5kaXNhYmxlZCA9IG9uKTsKICBpZiAob24pIHNob3dUeXBpbmcoKTsgZWxzZSBoaWRlVHlwaW5nKCk7Cn0KCi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQovLyAgU3RhcnQ6IFN0YXR1cyBsYWRlbgovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KYXN5bmMgZnVuY3Rpb24gbG9hZFN0YXR1cygpewogIHRyeXsKICAgIGNvbnN0IHMgPSBhd2FpdCBhcGkoIi9hcGkvc3RhdHVzIik7CiAgICBpZiAocy5lcnJvcil7IG1hcmtTdGF0dXMoZmFsc2UsICJGZWhsZXI6ICIrcy5lcnJvcik7IHJldHVybjsgfQogICAgc3RhdGUucmVhZHkgPSAhIXMucmVhZHk7CiAgICBzdGF0ZS5hc3Npc3RhbnROYW1lID0gcy5hc3Npc3RhbnRfbmFtZSB8fCAiRGlubyI7CiAgICBzdGF0ZS51c2VyTmFtZSA9IHMudXNlcl9uYW1lIHx8ICJCb3NzIjsKICAgIHN0YXRlLnByb3ZpZGVyID0gcy5wcm92aWRlciB8fCBudWxsOwogICAgbWFya1N0YXR1cyhzLnJlYWR5LCBzLmJyYWluIHx8ICLigJQiKTsKCiAgICBpZiAoc3RhdGUucHJvdmlkZXIgPT09ICJvbGxhbWEiKXsKICAgICAgLy8gTG9rYWxlcyBHZWhpcm4gLT4gZWlnZW5lIE9uYm9hcmRpbmctL1NldHVwLUxvZ2lrIChrw7xtbWVydCBzaWNoIHVtIEJlZ3LDvMOfdW5nL0thcnRlKQogICAgICBhd2FpdCBjaGVja09sbGFtYSgpOwogICAgICByZXR1cm47CiAgICB9CgogICAgLy8gQW5kZXJlIEFuYmlldGVyIChDbGF1ZGUgZXRjLik6IFZlcmhhbHRlbiB3aWUgYmlzaGVyCiAgICBoaWRlT2xsYW1hUGlsbCgpOwogICAgaWYgKCFzdGF0ZS5yZWFkeSl7CiAgICAgIC8vIE5pY2h0IGJlcmVpdCAtPiBmcmV1bmRsaWNoZSBTdGFydG5hY2hyaWNodCArIEVpbnN0ZWxsdW5nZW4gw7ZmZm5lbgogICAgICBpZiAoY2hhdEVsLmNoaWxkcmVuLmxlbmd0aCA9PT0gMCkKICAgICAgICBhZGRCdWJibGUoImRpbm8iLCAiVHJhZyB6dWVyc3QgZGVpbmVuIEFQSS1TY2hsw7xzc2VsIHVudGVyIOKamSBlaW4sIGRhbm4gbGVnZSBpY2ggbG9zLiDwn6aWIik7CiAgICAgIG9wZW5QYW5lbCgic2V0dGluZ3MiKTsKICAgIH0gZWxzZSBpZiAoY2hhdEVsLmNoaWxkcmVuLmxlbmd0aCA9PT0gMCl7CiAgICAgIC8vIEJlcmVpdCAtPiBCZWdyw7zDn3VuZwogICAgICBncmVldCgpOwogICAgfQogIH1jYXRjaChlKXsKICAgIG1hcmtTdGF0dXMoZmFsc2UsICJvZmZsaW5lIik7CiAgICBhZGRCdWJibGUoImVycm9yIiwgIktvbW1lIG5pY2h0IGFuIGRlbiBEaW5vLVNlcnZlciByYW4gKCIrZS5tZXNzYWdlKyIpLiBMw6R1ZnQgZGVyIGxva2FsZSBTZXJ2ZXI/Iik7CiAgfQp9CgpmdW5jdGlvbiBtYXJrU3RhdHVzKHJlYWR5LCBicmFpbil7CiAgY29uc3QgZG90ID0gJCgic3RhdHVzRG90Iik7CiAgZG90LmNsYXNzTmFtZSA9ICJkb3QgIiArIChyZWFkeSA/ICJvayIgOiAiYmFkIik7CiAgJCgiYnJhaW5UZXh0IikudGV4dENvbnRlbnQgPSBicmFpbiArIChyZWFkeSA/ICIgIMK3ICBvbmxpbmUiIDogIiAgwrcgIG9mZmxpbmUiKTsKfQoKLy8gQmVncsO8w591bmcgKG51ciBmYWxscyBDaGF0IG5vY2ggbGVlcikg4oCUIHplbnRyYWwsIGRhbWl0IMO8YmVyYWxsIHdpZWRlcnZlcndlbmRiYXIKZnVuY3Rpb24gZ3JlZXQoKXsKICBpZiAoY2hhdEVsLmNoaWxkcmVuLmxlbmd0aCA9PT0gMCkKICAgIGFkZEJ1YmJsZSgiZGlubyIsIGBEaW5vIGlzdCBvbmxpbmUsICR7c3RhdGUudXNlck5hbWV9ISBXb3JhdWYgaGFzdCBkdSBCb2NrPyDimqFgKTsKfQoKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09Ci8vICBPbGxhbWEtT25ib2FyZGluZyAobG9rYWxlcyBHZWhpcm4pCi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQpjb25zdCBPTExBTUFfREVGQVVMVF9NT0RFTCA9ICJxd2VuMi41OjdiIjsKbGV0IHNldHVwQ2FyZEVsID0gbnVsbDsKCi8vIFRvbGVyYW50OiBnaWx0IGN1cnJlbnRfbW9kZWwgYWxzIGluc3RhbGxpZXJ0PyAoei5CLiAibGxhbWEzLjIiIG1hdGNodCAibGxhbWEzLjI6bGF0ZXN0IikKZnVuY3Rpb24gbW9kZWxJbnN0YWxsZWQobW9kZWxzLCBjdXJyZW50KXsKICBpZiAoIUFycmF5LmlzQXJyYXkobW9kZWxzKSB8fCAhbW9kZWxzLmxlbmd0aCkgcmV0dXJuIGZhbHNlOwogIGlmICghY3VycmVudCkgcmV0dXJuIGZhbHNlOwogIHJldHVybiBtb2RlbHMuc29tZShtID0+IHsKICAgIGNvbnN0IGEgPSBTdHJpbmcobSksIGIgPSBTdHJpbmcoY3VycmVudCk7CiAgICByZXR1cm4gYSA9PT0gYiB8fCBhLnN0YXJ0c1dpdGgoYikgfHwgYi5zdGFydHNXaXRoKGEpOwogIH0pOwp9CgovLyBrbGVpbmVyIFN0YXR1cy1JbmRpa2F0b3Igb2JlbgpmdW5jdGlvbiBzZXRPbGxhbWFQaWxsKGtpbmQsIGxhYmVsKXsKICBjb25zdCBwaWxsID0gJCgib2xsYW1hUGlsbCIpOwogIGlmICghcGlsbCkgcmV0dXJuOwogIHBpbGwuc3R5bGUuZGlzcGxheSA9ICJpbmxpbmUtZmxleCI7CiAgcGlsbC5jbGFzc05hbWUgPSAib2xsYW1hLXBpbGwgIiArIChraW5kIHx8ICIiKTsKICAkKCJvbGxhbWFQaWxsVGV4dCIpLnRleHRDb250ZW50ID0gbGFiZWw7Cn0KZnVuY3Rpb24gaGlkZU9sbGFtYVBpbGwoKXsKICBjb25zdCBwaWxsID0gJCgib2xsYW1hUGlsbCIpOwogIGlmIChwaWxsKSBwaWxsLnN0eWxlLmRpc3BsYXkgPSAibm9uZSI7Cn0KCi8vIEVudGZlcm50IGVpbmUgZ2dmLiB2b3JoYW5kZW5lIFNldHVwLUthcnRlCmZ1bmN0aW9uIHJlbW92ZVNldHVwQ2FyZCgpewogIGlmIChzZXR1cENhcmRFbCl7IHNldHVwQ2FyZEVsLnJlbW92ZSgpOyBzZXR1cENhcmRFbCA9IG51bGw7IH0KfQoKLy8gUHLDvGZ0IC9hcGkvb2xsYW1hIHVuZCBlbnRzY2hlaWRldCDDvGJlciBLYXJ0ZS9CZWdyw7zDn3VuZwphc3luYyBmdW5jdGlvbiBjaGVja09sbGFtYSgpewogIGxldCBvOwogIHRyeXsKICAgIG8gPSBhd2FpdCBhcGkoIi9hcGkvb2xsYW1hIik7CiAgfWNhdGNoKGUpewogICAgLy8gS29ubnRlIE9sbGFtYS1JbmZvIG5pY2h0IGxhZGVuIC0+IGJlaGFuZGVsbiB3aWUgImzDpHVmdCBuaWNodCIKICAgIG8gPSB7IHJ1bm5pbmc6ZmFsc2UsIG1vZGVsczpbXSwgY3VycmVudF9tb2RlbDpPTExBTUFfREVGQVVMVF9NT0RFTCB9OwogIH0KICBpZiAobyAmJiBvLmVycm9yKXsgbyA9IHsgcnVubmluZzpmYWxzZSwgbW9kZWxzOltdLCBjdXJyZW50X21vZGVsOk9MTEFNQV9ERUZBVUxUX01PREVMIH07IH0KCiAgY29uc3QgcnVubmluZyA9ICEhKG8gJiYgby5ydW5uaW5nKTsKICBjb25zdCBtb2RlbHMgPSAobyAmJiBBcnJheS5pc0FycmF5KG8ubW9kZWxzKSkgPyBvLm1vZGVscyA6IFtdOwogIGNvbnN0IGN1cnJlbnQgPSAobyAmJiBvLmN1cnJlbnRfbW9kZWwpIHx8IE9MTEFNQV9ERUZBVUxUX01PREVMOwogIGNvbnN0IGhhc01vZGVsID0gbW9kZWxJbnN0YWxsZWQobW9kZWxzLCBjdXJyZW50KTsKCiAgaWYgKHJ1bm5pbmcgJiYgaGFzTW9kZWwpewogICAgLy8gQWxsZXMgYmVyZWl0IC0+IGtlaW5lIEthcnRlLCBub3JtYWxlIEJlZ3LDvMOfdW5nCiAgICBzZXRPbGxhbWFQaWxsKCJvayIsICJsb2thbCBha3RpdiIpOwogICAgcmVtb3ZlU2V0dXBDYXJkKCk7CiAgICBncmVldCgpOwogICAgcmV0dXJuIHRydWU7CiAgfQoKICBpZiAoIXJ1bm5pbmcpewogICAgc2V0T2xsYW1hUGlsbCgiYmFkIiwgIlNldHVwIG7DtnRpZyIpOwogICAgc2hvd1NldHVwQ2FyZCgibm90LXJ1bm5pbmciLCB7IG1vZGVscywgY3VycmVudCB9KTsKICB9IGVsc2UgewogICAgLy8gbMOkdWZ0LCBhYmVyIGtlaW4gcGFzc2VuZGVzIE1vZGVsbAogICAgc2V0T2xsYW1hUGlsbCgid2FybiIsICJNb2RlbGwgZmVobHQiKTsKICAgIHNob3dTZXR1cENhcmQoIm5vLW1vZGVsIiwgeyBtb2RlbHMsIGN1cnJlbnQgfSk7CiAgfQoKICAvLyBFaW5tYWxpZ2VzIEF1dG8tUmVjaGVjayBuYWNoIH4ycyBiZWltIGVyc3RlbiBMYWRlbiAoa2VpbiBEYXVlci1Qb2xsaW5nKQogIGlmICghc3RhdGUuYXV0b1JlY2hlY2tEb25lKXsKICAgIHN0YXRlLmF1dG9SZWNoZWNrRG9uZSA9IHRydWU7CiAgICBzZXRUaW1lb3V0KCgpPT57IGlmIChzZXR1cENhcmRFbCkgcmVjaGVja09sbGFtYSgpOyB9LCAyMDAwKTsKICB9CiAgcmV0dXJuIGZhbHNlOwp9CgovLyBCYXV0L2FrdHVhbGlzaWVydCBkaWUgU2V0dXAtS2FydGUgKHN0YXRpc2NoZXMgTWFya3VwID0gaW5uZXJIVE1MOyBkeW5hbWlzY2hlIFRleHRlIHZpYSB0ZXh0Q29udGVudCkKZnVuY3Rpb24gc2hvd1NldHVwQ2FyZChtb2RlLCBpbmZvKXsKICByZW1vdmVTZXR1cENhcmQoKTsKICBjb25zdCBjYXJkID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7CiAgY2FyZC5jbGFzc05hbWUgPSAic2V0dXAtY2FyZCI7CgogIGlmIChtb2RlID09PSAibm8tbW9kZWwiKXsKICAgIGNhcmQuaW5uZXJIVE1MID0gYAogICAgICA8ZGl2IGNsYXNzPSJzYy10aXRsZSI+8J+noCBEaW5vIGZlaGx0IG5vY2ggZWluIE1vZGVsbDwvZGl2PgogICAgICA8ZGl2IGNsYXNzPSJzYy1zdWIiPk9sbGFtYSBsw6R1ZnQgc2Nob24g4oCUIERpbm8gYnJhdWNodCBudXIgbm9jaCBlaW4gU3ByYWNobW9kZWxsLiBIb2wgZGlyIGRhcyBTdGFuZGFyZG1vZGVsbCBvZGVyIHfDpGhsIGVpbnMgZGVyIGluc3RhbGxpZXJ0ZW4uPC9kaXY+CiAgICAgIDxkaXYgY2xhc3M9InNjLXN0ZXAiPgogICAgICAgIDxkaXYgY2xhc3M9InNjLXN0ZXAtaCI+PHNwYW4gY2xhc3M9Im51bSI+4oaTPC9zcGFuPjxzcGFuPk1vZGVsbCBsYWRlbiAoZ3JhdGlzKTwvc3Bhbj48L2Rpdj4KICAgICAgICA8ZGl2IGNsYXNzPSJzYy1jb2RlYm94Ij4KICAgICAgICAgIDxjb2RlIGNsYXNzPSJzYy1jb2RlIiBpZD0ic2MtY21kIj48L2NvZGU+CiAgICAgICAgICA8YnV0dG9uIGNsYXNzPSJzYy1jb3B5IiBpZD0ic2MtY29weSI+8J+TiyBLb3BpZXJlbjwvYnV0dG9uPgogICAgICAgIDwvZGl2PgogICAgICAgIDxkaXYgY2xhc3M9InNjLW1vZGVscyIgaWQ9InNjLW1vZGVscyI+PC9kaXY+CiAgICAgIDwvZGl2PgogICAgICA8ZGl2IGNsYXNzPSJzYy1hY3Rpb25zIj4KICAgICAgICA8YnV0dG9uIGNsYXNzPSJzYy1yZWNoZWNrIiBpZD0ic2MtcmVjaGVjayI+8J+UhCBOb2NobWFsIHByw7xmZW48L2J1dHRvbj4KICAgICAgICA8c3BhbiBjbGFzcz0ic2Mtc3RhdGUiIGlkPSJzYy1zdGF0ZSI+PC9zcGFuPgogICAgICA8L2Rpdj4KICAgIGA7CiAgfSBlbHNlIHsKICAgIGNhcmQuaW5uZXJIVE1MID0gYAogICAgICA8ZGl2IGNsYXNzPSJzYy10aXRsZSI+8J+mliBGYXN0IGZlcnRpZyDigJQgRGlubyBicmF1Y2h0IG5vY2ggc2VpbiBHZWhpcm48L2Rpdj4KICAgICAgPGRpdiBjbGFzcz0ic2Mtc3ViIj5EaW5vIGzDpHVmdCBzdGFuZGFyZG3DpMOfaWcgZ3JhdGlzIHVuZCBsb2thbCDDvGJlciBPbGxhbWEuIFp3ZWkga3VyemUgU2Nocml0dGUsIGRhbm4gZ2VodCdzIGxvcy48L2Rpdj4KICAgICAgPGRpdiBjbGFzcz0ic2Mtc3RlcCI+CiAgICAgICAgPGRpdiBjbGFzcz0ic2Mtc3RlcC1oIj48c3BhbiBjbGFzcz0ibnVtIj4xPC9zcGFuPjxzcGFuPk9sbGFtYSBpbnN0YWxsaWVyZW4gKGdyYXRpcyk8L3NwYW4+PC9kaXY+CiAgICAgICAgPGRpdiBjbGFzcz0ic2Mtc3ViIiBzdHlsZT0ibWFyZ2luOjAiPgogICAgICAgICAgTGFkZSBlcyBoaWVyIGhlcnVudGVyOiA8YSBjbGFzcz0ic2MtbGluayIgaWQ9InNjLWRsIiBocmVmPSJodHRwczovL29sbGFtYS5jb20vZG93bmxvYWQiIHRhcmdldD0iX2JsYW5rIiByZWw9Im5vb3BlbmVyIG5vcmVmZXJyZXIiPm9sbGFtYS5jb20vZG93bmxvYWQ8L2E+CiAgICAgICAgPC9kaXY+CiAgICAgIDwvZGl2PgogICAgICA8ZGl2IGNsYXNzPSJzYy1zdGVwIj4KICAgICAgICA8ZGl2IGNsYXNzPSJzYy1zdGVwLWgiPjxzcGFuIGNsYXNzPSJudW0iPjI8L3NwYW4+PHNwYW4+RGllc2VzIEtvbW1hbmRvIGltIFRlcm1pbmFsIC8gaW4gZGVyIEVpbmdhYmVhdWZmb3JkZXJ1bmcgYXVzZsO8aHJlbjo8L3NwYW4+PC9kaXY+CiAgICAgICAgPGRpdiBjbGFzcz0ic2MtY29kZWJveCI+CiAgICAgICAgICA8Y29kZSBjbGFzcz0ic2MtY29kZSIgaWQ9InNjLWNtZCI+PC9jb2RlPgogICAgICAgICAgPGJ1dHRvbiBjbGFzcz0ic2MtY29weSIgaWQ9InNjLWNvcHkiPvCfk4sgS29waWVyZW48L2J1dHRvbj4KICAgICAgICA8L2Rpdj4KICAgICAgPC9kaXY+CiAgICAgIDxkaXYgY2xhc3M9InNjLWFjdGlvbnMiPgogICAgICAgIDxidXR0b24gY2xhc3M9InNjLXJlY2hlY2siIGlkPSJzYy1yZWNoZWNrIj7wn5SEIE5vY2htYWwgcHLDvGZlbjwvYnV0dG9uPgogICAgICAgIDxidXR0b24gY2xhc3M9InNjLXNldHRpbmdzIiBpZD0ic2Mtc2V0dGluZ3MiPkxpZWJlciBkZW4gc3RhcmtlbiBDbGF1ZGUgbnV0emVuPyDihpIg4pqZIEVpbnN0ZWxsdW5nZW48L2J1dHRvbj4KICAgICAgICA8c3BhbiBjbGFzcz0ic2Mtc3RhdGUiIGlkPSJzYy1zdGF0ZSI+PC9zcGFuPgogICAgICA8L2Rpdj4KICAgIGA7CiAgfQoKICAvLyBLYXJ0ZSBvYmVuIGltIENoYXQgcGxhdHppZXJlbiwgZGFtaXQgc2llIGd1dCBzaWNodGJhciBpc3QKICBjaGF0RWwucHJlcGVuZChjYXJkKTsKICBzZXR1cENhcmRFbCA9IGNhcmQ7CiAgc2Nyb2xsRG93bigpOwoKICAvLyBLb21tYW5kby1UZXh0IChkeW5hbWlzY2ggLT4gdGV4dENvbnRlbnQsIGtlaW4gaW5uZXJIVE1MKQogIGNvbnN0IGNtZCA9IChtb2RlID09PSAibm8tbW9kZWwiKQogICAgPyAoIm9sbGFtYSBwdWxsICIgKyAoaW5mbyAmJiBpbmZvLmN1cnJlbnQgPyBpbmZvLmN1cnJlbnQgOiBPTExBTUFfREVGQVVMVF9NT0RFTCkpCiAgICA6ICgib2xsYW1hIHJ1biAiICsgT0xMQU1BX0RFRkFVTFRfTU9ERUwpOwogIGNvbnN0IGNtZEVsID0gY2FyZC5xdWVyeVNlbGVjdG9yKCIjc2MtY21kIik7CiAgaWYgKGNtZEVsKSBjbWRFbC50ZXh0Q29udGVudCA9IGNtZDsKCiAgLy8gS29waWVyZW4tQnV0dG9uCiAgY29uc3QgY29weUJ0biA9IGNhcmQucXVlcnlTZWxlY3RvcigiI3NjLWNvcHkiKTsKICBpZiAoY29weUJ0bikgY29weUJ0bi5vbmNsaWNrID0gKCk9PiBjb3B5VG9DbGlwYm9hcmQoY21kLCBjb3B5QnRuKTsKCiAgLy8gUmVjaGVjay1CdXR0b24KICBjb25zdCByZWNoZWNrQnRuID0gY2FyZC5xdWVyeVNlbGVjdG9yKCIjc2MtcmVjaGVjayIpOwogIGlmIChyZWNoZWNrQnRuKSByZWNoZWNrQnRuLm9uY2xpY2sgPSByZWNoZWNrT2xsYW1hOwoKICAvLyBFaW5zdGVsbHVuZ2VuLUxpbmsKICBjb25zdCBzZXRCdG4gPSBjYXJkLnF1ZXJ5U2VsZWN0b3IoIiNzYy1zZXR0aW5ncyIpOwogIGlmIChzZXRCdG4pIHNldEJ0bi5vbmNsaWNrID0gKCk9PiBvcGVuUGFuZWwoInNldHRpbmdzIik7CgogIC8vIEluc3RhbGxpZXJ0ZSBNb2RlbGxlIGFscyBCdXR0b25zIChudXIgaW0gbm8tbW9kZWwtRmFsbCB1bmQgd2VubiB2b3JoYW5kZW4pCiAgaWYgKG1vZGUgPT09ICJuby1tb2RlbCIpewogICAgY29uc3Qgd3JhcCA9IGNhcmQucXVlcnlTZWxlY3RvcigiI3NjLW1vZGVscyIpOwogICAgY29uc3QgbW9kZWxzID0gKGluZm8gJiYgQXJyYXkuaXNBcnJheShpbmZvLm1vZGVscykpID8gaW5mby5tb2RlbHMgOiBbXTsKICAgIGlmICh3cmFwICYmIG1vZGVscy5sZW5ndGgpewogICAgICBjb25zdCBsYmwgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJzcGFuIik7CiAgICAgIGxibC5zdHlsZS5jc3NUZXh0ID0gImZvbnQtc2l6ZToxMnB4O2NvbG9yOnZhcigtLW11dCk7YWxpZ24tc2VsZjpjZW50ZXI7bWFyZ2luLXJpZ2h0OjJweCI7CiAgICAgIGxibC50ZXh0Q29udGVudCA9ICJTY2hvbiBpbnN0YWxsaWVydDoiOwogICAgICB3cmFwLmFwcGVuZENoaWxkKGxibCk7CiAgICAgIG1vZGVscy5mb3JFYWNoKG09PnsKICAgICAgICBjb25zdCBiID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiYnV0dG9uIik7CiAgICAgICAgYi5jbGFzc05hbWUgPSAic2MtbW9kZWwiOwogICAgICAgIGIudGV4dENvbnRlbnQgPSBtOyAgICAgICAgICAgICAgICAgLy8gZHluYW1pc2NoIC0+IHRleHRDb250ZW50CiAgICAgICAgYi5vbmNsaWNrID0gKCk9PiBwaWNrT2xsYW1hTW9kZWwobSwgYik7CiAgICAgICAgd3JhcC5hcHBlbmRDaGlsZChiKTsKICAgICAgfSk7CiAgICB9CiAgfQp9CgovLyBJbiBad2lzY2hlbmFibGFnZSBrb3BpZXJlbiAobWl0IEZhbGxiYWNrKQpmdW5jdGlvbiBjb3B5VG9DbGlwYm9hcmQodGV4dCwgYnRuKXsKICBjb25zdCBkb25lID0gKCk9PnsKICAgIGlmICghYnRuKSByZXR1cm47CiAgICBjb25zdCBvbGQgPSBidG4udGV4dENvbnRlbnQ7CiAgICBidG4udGV4dENvbnRlbnQgPSAi4pyTIEtvcGllcnQiOwogICAgc2V0VGltZW91dCgoKT0+eyBidG4udGV4dENvbnRlbnQgPSBvbGQ7IH0sIDE1MDApOwogIH07CiAgdHJ5ewogICAgaWYgKG5hdmlnYXRvci5jbGlwYm9hcmQgJiYgbmF2aWdhdG9yLmNsaXBib2FyZC53cml0ZVRleHQpewogICAgICBuYXZpZ2F0b3IuY2xpcGJvYXJkLndyaXRlVGV4dCh0ZXh0KS50aGVuKGRvbmUsICgpPT5mYWxsYmFja0NvcHkodGV4dCwgZG9uZSkpOwogICAgfSBlbHNlIHsKICAgICAgZmFsbGJhY2tDb3B5KHRleHQsIGRvbmUpOwogICAgfQogIH1jYXRjaChlKXsgZmFsbGJhY2tDb3B5KHRleHQsIGRvbmUpOyB9Cn0KZnVuY3Rpb24gZmFsbGJhY2tDb3B5KHRleHQsIGRvbmUpewogIHRyeXsKICAgIGNvbnN0IHRhID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgidGV4dGFyZWEiKTsKICAgIHRhLnZhbHVlID0gdGV4dDsgdGEuc3R5bGUucG9zaXRpb249ImZpeGVkIjsgdGEuc3R5bGUub3BhY2l0eT0iMCI7CiAgICBkb2N1bWVudC5ib2R5LmFwcGVuZENoaWxkKHRhKTsgdGEuZm9jdXMoKTsgdGEuc2VsZWN0KCk7CiAgICBkb2N1bWVudC5leGVjQ29tbWFuZCgiY29weSIpOwogICAgZG9jdW1lbnQuYm9keS5yZW1vdmVDaGlsZCh0YSk7CiAgICBkb25lICYmIGRvbmUoKTsKICB9Y2F0Y2goZSl7IC8qIHN0aWxsICovIH0KfQoKLy8gSW5zdGFsbGllcnRlcyBNb2RlbGwgd8OkaGxlbiAtPiBzZXR6ZW4sIFN0YXR1cyBuZXUgbGFkZW4sIEthcnRlIGF1c2JsZW5kZW4KYXN5bmMgZnVuY3Rpb24gcGlja09sbGFtYU1vZGVsKG5hbWUsIGJ0bil7CiAgY29uc3Qgc3RhdGVFbCA9IHNldHVwQ2FyZEVsID8gc2V0dXBDYXJkRWwucXVlcnlTZWxlY3RvcigiI3NjLXN0YXRlIikgOiBudWxsOwogIGlmIChidG4pIGJ0bi5kaXNhYmxlZCA9IHRydWU7CiAgaWYgKHN0YXRlRWwpIHN0YXRlRWwudGV4dENvbnRlbnQgPSAic2V0emUgTW9kZWxsIOKApiI7CiAgdHJ5ewogICAgY29uc3QgciA9IGF3YWl0IGFwaSgiL2FwaS9zZXR0aW5ncyIsICJQT1NUIiwgeyBvbGxhbWFfbW9kZWw6IG5hbWUgfSk7CiAgICBpZiAociAmJiByLmVycm9yKXsKICAgICAgaWYgKHN0YXRlRWwpIHN0YXRlRWwudGV4dENvbnRlbnQgPSAi4pqgICIgKyByLmVycm9yOwogICAgICBpZiAoYnRuKSBidG4uZGlzYWJsZWQgPSBmYWxzZTsKICAgICAgcmV0dXJuOwogICAgfQogICAgcmVtb3ZlU2V0dXBDYXJkKCk7CiAgICBhd2FpdCBsb2FkU3RhdHVzKCk7ICAgICAgICAgIC8vIGzDpGR0IFN0YXR1cyArIE9sbGFtYSBuZXUsIGJlZ3LDvMOfdCBiZWkgRXJmb2xnCiAgfWNhdGNoKGUpewogICAgaWYgKHN0YXRlRWwpIHN0YXRlRWwudGV4dENvbnRlbnQgPSAi4pqgICIgKyBlLm1lc3NhZ2U7CiAgICBpZiAoYnRuKSBidG4uZGlzYWJsZWQgPSBmYWxzZTsKICB9Cn0KCi8vICJOb2NobWFsIHByw7xmZW4iIOKAlCByb2J1c3QsIGtlaW4gRGF1ZXItUG9sbGluZwphc3luYyBmdW5jdGlvbiByZWNoZWNrT2xsYW1hKCl7CiAgaWYgKCFzZXR1cENhcmRFbCkgcmV0dXJuOwogIGNvbnN0IHJlY2hlY2tCdG4gPSBzZXR1cENhcmRFbC5xdWVyeVNlbGVjdG9yKCIjc2MtcmVjaGVjayIpOwogIGNvbnN0IHN0YXRlRWwgPSBzZXR1cENhcmRFbC5xdWVyeVNlbGVjdG9yKCIjc2Mtc3RhdGUiKTsKICBpZiAocmVjaGVja0J0bikgcmVjaGVja0J0bi5kaXNhYmxlZCA9IHRydWU7CiAgaWYgKHN0YXRlRWwpIHN0YXRlRWwudGV4dENvbnRlbnQgPSAicHLDvGZlIOKApiI7CiAgbGV0IG87CiAgdHJ5ewogICAgbyA9IGF3YWl0IGFwaSgiL2FwaS9vbGxhbWEiKTsKICB9Y2F0Y2goZSl7CiAgICBpZiAoc3RhdGVFbCkgc3RhdGVFbC50ZXh0Q29udGVudCA9ICJOb2NoIG5pY2h0IGVycmVpY2hiYXIg4oCUIHN0YXJ0ZSBPbGxhbWEgdW5kIHZlcnN1Y2gncyBnbGVpY2ggbm9jaG1hbC4iOwogICAgaWYgKHJlY2hlY2tCdG4pIHJlY2hlY2tCdG4uZGlzYWJsZWQgPSBmYWxzZTsKICAgIHNldE9sbGFtYVBpbGwoImJhZCIsICJTZXR1cCBuw7Z0aWciKTsKICAgIHJldHVybjsKICB9CiAgaWYgKG8gJiYgby5lcnJvcil7CiAgICBpZiAoc3RhdGVFbCkgc3RhdGVFbC50ZXh0Q29udGVudCA9ICLimqAgIiArIG8uZXJyb3I7CiAgICBpZiAocmVjaGVja0J0bikgcmVjaGVja0J0bi5kaXNhYmxlZCA9IGZhbHNlOwogICAgcmV0dXJuOwogIH0KCiAgY29uc3QgcnVubmluZyA9ICEhKG8gJiYgby5ydW5uaW5nKTsKICBjb25zdCBtb2RlbHMgPSAobyAmJiBBcnJheS5pc0FycmF5KG8ubW9kZWxzKSkgPyBvLm1vZGVscyA6IFtdOwogIGNvbnN0IGN1cnJlbnQgPSAobyAmJiBvLmN1cnJlbnRfbW9kZWwpIHx8IE9MTEFNQV9ERUZBVUxUX01PREVMOwogIGNvbnN0IGhhc01vZGVsID0gbW9kZWxJbnN0YWxsZWQobW9kZWxzLCBjdXJyZW50KTsKCiAgaWYgKHJ1bm5pbmcgJiYgaGFzTW9kZWwpewogICAgc2V0T2xsYW1hUGlsbCgib2siLCAibG9rYWwgYWt0aXYiKTsKICAgIHJlbW92ZVNldHVwQ2FyZCgpOwogICAgc3RhdGUucmVhZHkgPSB0cnVlOwogICAgYWRkQnViYmxlKCJkaW5vIiwgYERpbm8gaXN0IG9ubGluZSwgJHtzdGF0ZS51c2VyTmFtZX0hIFdvcmF1ZiBoYXN0IGR1IEJvY2s/IOKaoWApOwogICAgcmV0dXJuOwogIH0KCiAgLy8gTm9jaCBuaWNodCBmZXJ0aWcgLT4gS2FydGUgcGFzc2VuZCBha3R1YWxpc2llcmVuCiAgaWYgKCFydW5uaW5nKXsKICAgIHNldE9sbGFtYVBpbGwoImJhZCIsICJTZXR1cCBuw7Z0aWciKTsKICAgIHNob3dTZXR1cENhcmQoIm5vdC1ydW5uaW5nIiwgeyBtb2RlbHMsIGN1cnJlbnQgfSk7CiAgfSBlbHNlIHsKICAgIHNldE9sbGFtYVBpbGwoIndhcm4iLCAiTW9kZWxsIGZlaGx0Iik7CiAgICBzaG93U2V0dXBDYXJkKCJuby1tb2RlbCIsIHsgbW9kZWxzLCBjdXJyZW50IH0pOwogIH0KICBjb25zdCBucyA9IHNldHVwQ2FyZEVsID8gc2V0dXBDYXJkRWwucXVlcnlTZWxlY3RvcigiI3NjLXN0YXRlIikgOiBudWxsOwogIGlmIChucykgbnMudGV4dENvbnRlbnQgPSBydW5uaW5nID8gIkzDpHVmdCDigJQgYWJlciBlcyBmZWhsdCBub2NoIGRhcyBNb2RlbGwuIiA6ICJPbGxhbWEgbMOkdWZ0IG5vY2ggbmljaHQuIjsKfQoKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09Ci8vICBDaGF0IHNlbmRlbgovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KYXN5bmMgZnVuY3Rpb24gc2VuZCgpewogIGlmIChzdGF0ZS5idXN5KSByZXR1cm47CiAgY29uc3QgdGV4dCA9IGlucHV0RWwudmFsdWUudHJpbSgpOwogIGlmICghdGV4dCkgcmV0dXJuOwogIGlucHV0RWwudmFsdWUgPSAiIjsgYXV0b0dyb3coKTsKCiAgYWRkQnViYmxlKCJ1c2VyIiwgdGV4dCk7CiAgc3RhdGUubWVzc2FnZXMucHVzaCh7IHJvbGU6InVzZXIiLCBjb250ZW50OnRleHQgfSk7CgogIHNldEJ1c3kodHJ1ZSk7CiAgdHJ5ewogICAgY29uc3QgZGF0YSA9IGF3YWl0IGFwaSgiL2FwaS9jaGF0IiwgIlBPU1QiLCB7IG1lc3NhZ2VzOiBzdGF0ZS5tZXNzYWdlcyB9KTsKICAgIGhpZGVUeXBpbmcoKTsKICAgIGlmIChkYXRhLmVycm9yKXsKICAgICAgYWRkQnViYmxlKCJlcnJvciIsIGRhdGEuZXJyb3IpOwogICAgICAvLyBsZXR6dGUgTnV0emVyLU5hY2hyaWNodCBuaWNodCBkYXVlcmhhZnQgYmVoYWx0ZW4KICAgICAgc3RhdGUubWVzc2FnZXMucG9wKCk7CiAgICB9IGVsc2UgewogICAgICBjb25zdCByZXBseSA9IGRhdGEucmVwbHkgfHwgIiI7CiAgICAgIGFkZEJ1YmJsZSgiZGlubyIsIHJlcGx5KTsKICAgICAgc3RhdGUubWVzc2FnZXMucHVzaCh7IHJvbGU6ImFzc2lzdGFudCIsIGNvbnRlbnQ6cmVwbHkgfSk7CiAgICAgIHNwZWFrKHJlcGx5KTsKICAgIH0KICB9Y2F0Y2goZSl7CiAgICBoaWRlVHlwaW5nKCk7CiAgICBhZGRCdWJibGUoImVycm9yIiwgIk5ldHp3ZXJrZmVobGVyOiAiK2UubWVzc2FnZSk7CiAgICBzdGF0ZS5tZXNzYWdlcy5wb3AoKTsKICB9ZmluYWxseXsKICAgIHNldEJ1c3koZmFsc2UpOwogICAgaW5wdXRFbC5mb2N1cygpOwogIH0KfQoKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09Ci8vICBRdWljay1BY3Rpb25zCi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQovLyBHZW5lcmlzY2hlciBIZWxmZXIgZsO8ciAvcGxhbiB1bmQgL3RhZyAoQm9keSB7fSAtPiB7dGV4dH0pCmFzeW5jIGZ1bmN0aW9uIHNpbXBsZUFjdGlvbihwYXRoKXsKICBpZiAoc3RhdGUuYnVzeSkgcmV0dXJuOwogIHNldEJ1c3kodHJ1ZSk7CiAgdHJ5ewogICAgY29uc3QgZGF0YSA9IGF3YWl0IGFwaShwYXRoLCAiUE9TVCIsIHt9KTsKICAgIGhpZGVUeXBpbmcoKTsKICAgIGlmIChkYXRhLmVycm9yKSBhZGRCdWJibGUoImVycm9yIiwgZGF0YS5lcnJvcik7CiAgICBlbHNlewogICAgICBjb25zdCB0eHQgPSBkYXRhLnRleHQgfHwgIiI7CiAgICAgIGFkZEJ1YmJsZSgiZGlubyIsIHR4dCk7CiAgICAgIHN0YXRlLm1lc3NhZ2VzLnB1c2goeyByb2xlOiJhc3Npc3RhbnQiLCBjb250ZW50OnR4dCB9KTsKICAgICAgc3BlYWsodHh0KTsKICAgIH0KICB9Y2F0Y2goZSl7IGhpZGVUeXBpbmcoKTsgYWRkQnViYmxlKCJlcnJvciIsIk5ldHp3ZXJrZmVobGVyOiAiK2UubWVzc2FnZSk7IH0KICBmaW5hbGx5eyBzZXRCdXN5KGZhbHNlKTsgfQp9CmZ1bmN0aW9uIHF1aWNrUGxhbigpeyBzaW1wbGVBY3Rpb24oIi9hcGkvcGxhbiIpOyB9CmZ1bmN0aW9uIHF1aWNrVG9kYXkoKXsgc2ltcGxlQWN0aW9uKCIvYXBpL3RhZyIpOyB9CgovLyBMZXJuZW4gLT4gdmVyZGljaHRldCBHZXNwcsOkY2ggenUgRmFrdGVuCmFzeW5jIGZ1bmN0aW9uIHF1aWNrTGVhcm4oKXsKICBpZiAoc3RhdGUuYnVzeSkgcmV0dXJuOwogIGlmICghc3RhdGUubWVzc2FnZXMubGVuZ3RoKXsgYWRkQnViYmxlKCJpbmZvIiwiV2lyIGhhYmVuIG5vY2ggbmljaHQgZ2VyZWRldCDigJQgbmljaHRzIHp1IGxlcm5lbi4g8J+YiSIpOyByZXR1cm47IH0KICBzZXRCdXN5KHRydWUpOwogIHRyeXsKICAgIGNvbnN0IGRhdGEgPSBhd2FpdCBhcGkoIi9hcGkvbGVhcm4iLCAiUE9TVCIsIHsgbWVzc2FnZXM6IHN0YXRlLm1lc3NhZ2VzIH0pOwogICAgaGlkZVR5cGluZygpOwogICAgaWYgKGRhdGEuZXJyb3IpIGFkZEJ1YmJsZSgiZXJyb3IiLCBkYXRhLmVycm9yKTsKICAgIGVsc2UgYWRkQnViYmxlKCJpbmZvIiwgYEdlbWVya3QhIERpbm8ga2VubnQgamV0enQgJHtkYXRhLmNvdW50ID8/IDB9IEZha3Rlbi4g8J+noGApOwogIH1jYXRjaChlKXsgaGlkZVR5cGluZygpOyBhZGRCdWJibGUoImVycm9yIiwiTmV0endlcmtmZWhsZXI6ICIrZS5tZXNzYWdlKTsgfQogIGZpbmFsbHl7IHNldEJ1c3koZmFsc2UpOyB9Cn0KCi8vIFJhdCBkZXIgS0lzIC0+IG5pbW10IGFrdHVlbGxlbiBFaW5nYWJldGV4dCBhbHMgRnJhZ2UKYXN5bmMgZnVuY3Rpb24gcXVpY2tDb3VuY2lsKCl7CiAgaWYgKHN0YXRlLmJ1c3kpIHJldHVybjsKICBjb25zdCBmcmFnZSA9IGlucHV0RWwudmFsdWUudHJpbSgpOwogIGlmICghZnJhZ2UpeyBhZGRCdWJibGUoImluZm8iLCJTY2hyZWliIHp1ZXJzdCBkZWluZSBGcmFnZSBpbnMgRmVsZCwgZGFubiDCu1JhdCBkZXIgS0lzwqsuIPCfp6AiKTsgcmV0dXJuOyB9CiAgaW5wdXRFbC52YWx1ZT0iIjsgYXV0b0dyb3coKTsKICBhZGRCdWJibGUoInVzZXIiLCBmcmFnZSk7CgogIHNldEJ1c3kodHJ1ZSk7CiAgdHJ5ewogICAgY29uc3QgZGF0YSA9IGF3YWl0IGFwaSgiL2FwaS9jb3VuY2lsIiwgIlBPU1QiLCB7IG1lc3NhZ2VzOiBzdGF0ZS5tZXNzYWdlcywgZnJhZ2UgfSk7CiAgICBoaWRlVHlwaW5nKCk7CiAgICBpZiAoZGF0YS5lcnJvcil7IGFkZEJ1YmJsZSgiZXJyb3IiLCBkYXRhLmVycm9yKTsgc2V0QnVzeShmYWxzZSk7IHJldHVybjsgfQogICAgY29uc3QgYW5zd2VycyA9IGRhdGEuYW5zd2VycyB8fCB7fTsKICAgIC8vIFJlaWhlbmZvbGdlOiBDbGF1ZGUsIENoYXRHUFQsIEdlbWluaSAoZmFsbHMgdm9yaGFuZGVuKQogICAgWyJDbGF1ZGUiLCJDaGF0R1BUIiwiR2VtaW5pIl0uZm9yRWFjaChuYW1lPT57CiAgICAgIGlmIChhbnN3ZXJzW25hbWVdICE9IG51bGwpIGFkZEJ1YmJsZSgiY291bmNpbCIsIGFuc3dlcnNbbmFtZV0sICLilrggIituYW1lKTsKICAgIH0pOwogICAgLy8gZXZ0bC4gd2VpdGVyZSB1bmJla2FubnRlIFNjaGzDvHNzZWwKICAgIE9iamVjdC5rZXlzKGFuc3dlcnMpLmZvckVhY2gobmFtZT0+ewogICAgICBpZiAoIVsiQ2xhdWRlIiwiQ2hhdEdQVCIsIkdlbWluaSJdLmluY2x1ZGVzKG5hbWUpKSBhZGRCdWJibGUoImNvdW5jaWwiLCBhbnN3ZXJzW25hbWVdLCAi4pa4ICIrbmFtZSk7CiAgICB9KTsKICAgIGlmIChkYXRhLnN5bnRoZXNlKXsKICAgICAgYWRkQnViYmxlKCJzeW50aCIsIGRhdGEuc3ludGhlc2UsICLinKYgRGlub3MgRmF6aXQiKTsKICAgICAgc3RhdGUubWVzc2FnZXMucHVzaCh7IHJvbGU6ImFzc2lzdGFudCIsIGNvbnRlbnQ6ZGF0YS5zeW50aGVzZSB9KTsKICAgICAgc3BlYWsoZGF0YS5zeW50aGVzZSk7CiAgICB9CiAgfWNhdGNoKGUpeyBoaWRlVHlwaW5nKCk7IGFkZEJ1YmJsZSgiZXJyb3IiLCJOZXR6d2Vya2ZlaGxlcjogIitlLm1lc3NhZ2UpOyB9CiAgZmluYWxseXsgc2V0QnVzeShmYWxzZSk7IH0KfQoKLy8gVGVhbS1BdWZ0cmFnIC0+IFBsYW5lciArIFNwZXppYWxpc3RlbiArIERpbm9zIFBsYW4gKG5pbW10IEVpbmdhYmV0ZXh0IGFscyBBdWZnYWJlKQphc3luYyBmdW5jdGlvbiBxdWlja1RlYW0oKXsKICBpZiAoc3RhdGUuYnVzeSkgcmV0dXJuOwogIGNvbnN0IHRhc2sgPSBpbnB1dEVsLnZhbHVlLnRyaW0oKTsKICBpZiAoIXRhc2speyBhZGRCdWJibGUoImluZm8iLCJTY2hyZWliIGRlaW5lIEF1ZmdhYmUgaW5zIEZlbGQgKHouQi4gwrtob2wgbWlyIDMgbmV1ZSBLdW5kZW4gZGllc2UgV29jaGXCqyksIGRhbm4gwrtUZWFtLUF1ZnRyYWfCqy4g8J+kliIpOyByZXR1cm47IH0KICBpbnB1dEVsLnZhbHVlPSIiOyBhdXRvR3JvdygpOwogIGFkZEJ1YmJsZSgidXNlciIsIHRhc2spOwogIGFkZEJ1YmJsZSgiaW5mbyIsIkRpbm8gcnVmdCBzZWluIFRlYW0genVzYW1tZW4g8J+kliDigJQgUGxhbmVyLCBTcGV6aWFsaXN0ZW4gdW5kIGFtIEVuZGUgRGlub3MgUGxhbi4gRGFzIGRhdWVydCBlaW5lbiBNb21lbnQsIHdlaWwgbWVocmVyZSBuYWNoZWluYW5kZXIgYXJiZWl0ZW7igKYiKTsKCiAgc2V0QnVzeSh0cnVlKTsKICB0cnl7CiAgICBjb25zdCBkYXRhID0gYXdhaXQgYXBpKCIvYXBpL3RlYW0iLCAiUE9TVCIsIHsgdGFzaywgbWVzc2FnZXM6IHN0YXRlLm1lc3NhZ2VzIH0pOwogICAgaGlkZVR5cGluZygpOwogICAgaWYgKGRhdGEuZXJyb3IgJiYgIShkYXRhLnN0ZXBzICYmIGRhdGEuc3RlcHMubGVuZ3RoKSl7IGFkZEJ1YmJsZSgiZXJyb3IiLCBkYXRhLmVycm9yKTsgc2V0QnVzeShmYWxzZSk7IHJldHVybjsgfQogICAgKGRhdGEuc3RlcHMgfHwgW10pLmZvckVhY2gocz0+ewogICAgICBhZGRCdWJibGUoImNvdW5jaWwiLCBzLm91dHB1dCwgKHMuZW1vaml8fCLigKIiKSsiICIrcy5uYW1lKyIg4oCUICIrcy50YXNrKTsKICAgIH0pOwogICAgaWYgKGRhdGEuZmluYWwpewogICAgICBhZGRCdWJibGUoInN5bnRoIiwgZGF0YS5maW5hbCwgIuKcpiBEaW5vcyBQbGFuIChUZWFtLUVyZ2VibmlzKSIpOwogICAgICBzdGF0ZS5tZXNzYWdlcy5wdXNoKHsgcm9sZToiYXNzaXN0YW50IiwgY29udGVudDpkYXRhLmZpbmFsIH0pOwogICAgICBzcGVhayhkYXRhLmZpbmFsKTsKICAgIH0gZWxzZSBpZiAoZGF0YS5lcnJvcil7CiAgICAgIGFkZEJ1YmJsZSgiZXJyb3IiLCBkYXRhLmVycm9yKTsKICAgIH0KICB9Y2F0Y2goZSl7IGhpZGVUeXBpbmcoKTsgYWRkQnViYmxlKCJlcnJvciIsIk5ldHp3ZXJrZmVobGVyOiAiK2UubWVzc2FnZSk7IH0KICBmaW5hbGx5eyBzZXRCdXN5KGZhbHNlKTsgfQp9CgovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KLy8gIEVpbmdhYmVmZWxkOiBBdXRvLUdyb3cgKyBUYXN0YXR1cgovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KZnVuY3Rpb24gYXV0b0dyb3coKXsKICBpbnB1dEVsLnN0eWxlLmhlaWdodCA9ICJhdXRvIjsKICBpbnB1dEVsLnN0eWxlLmhlaWdodCA9IE1hdGgubWluKGlucHV0RWwuc2Nyb2xsSGVpZ2h0LCAxNDApICsgInB4IjsKfQppbnB1dEVsLmFkZEV2ZW50TGlzdGVuZXIoImlucHV0IiwgYXV0b0dyb3cpOwppbnB1dEVsLmFkZEV2ZW50TGlzdGVuZXIoImtleWRvd24iLCAoZSk9PnsKICBpZiAoZS5rZXkgPT09ICJFbnRlciIgJiYgIWUuc2hpZnRLZXkpeyBlLnByZXZlbnREZWZhdWx0KCk7IHNlbmQoKTsgfQp9KTsKCi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQovLyAgU3ByYWNoYXVzZ2FiZSAoc3BlZWNoU3ludGhlc2lzKQovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KbGV0IGFsbFZvaWNlcyA9IFtdOwpsZXQgdm9pY2VERSA9IG51bGw7ICAgICAgICAvLyBiZXN0ZSBkZXV0c2NoZSBTdGltbWUgKERpbm8gc3ByaWNodCBEZXV0c2NoKQpsZXQgdm9pY2VFTiA9IG51bGw7ICAgICAgICAvLyBiZXN0ZSBlbmdsaXNjaGUgU3RpbW1lCmxldCBzZWxlY3RlZFZvaWNlID0gbnVsbDsgIC8vIG1hbnVlbGwgZ2V3YWVobHRlIFN0aW1tZSAoc29uc3QgYXV0b21hdGlzY2gpCmxldCB2b2ljZU1hbnVhbCA9IGZhbHNlOwoKLy8gQmV3ZXJ0dW5nOiB3aWUgbmF0dWVybGljaC9ob2Nod2VydGlnIGlzdCBkaWUgU3RpbW1lIGluIGRlciBnZXd1ZW5zY2h0ZW4gU3ByYWNoZT8KLy8gV2ljaHRpZzogZWluZSBFTkdMSVNDSEUgU3RpbW1lLCBkaWUgREVVVFNDSCBsaWVzdCwga2xpbmd0IGFiZ2VoYWNrdCAtPiBoYXJ0ZSBTdHJhZmUuCmZ1bmN0aW9uIHZvaWNlUmFuayh2LCB3YW50KXsKICBjb25zdCBsYW5nID0gKHYubGFuZyB8fCAiIikudG9Mb3dlckNhc2UoKS5yZXBsYWNlKCJfIiwgIi0iKTsKICBjb25zdCBuYW1lID0gKHYubmFtZSB8fCAiIikudG9Mb3dlckNhc2UoKTsKICBsZXQgcyA9IDA7CiAgaWYgKGxhbmcuc3RhcnRzV2l0aCh3YW50KSkgcyArPSAxNDA7ICAgICAgICAgIC8vIHJpY2h0aWdlIFNwcmFjaGUgPSBmbHVlc3NpZwogIGVsc2UgcyAtPSAxMjA7ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAvLyBmYWxzY2hlIFNwcmFjaGUgPSBhYmdlaGFja3QKICBpZiAoL25hdHVyYWx8bmV1cmFsLy50ZXN0KG5hbWUpKSBzICs9IDEyMDsgICAgLy8gRWRnZS1OZXVyYWwtU3RpbW1lbjogYW0gbmF0dWVybGljaHN0ZW4KICBpZiAoL29ubGluZS8udGVzdChuYW1lKSkgICAgICAgIHMgKz0gNzA7ICAgICAgLy8gT25saW5lLVN0aW1tZW4ga2xpbmdlbiBuYXR1ZXJsaWNoZXIKICBpZiAoL2dvb2dsZS8udGVzdChuYW1lKSkgICAgICAgIHMgKz0gMzU7ICAgICAgLy8gR29vZ2xlLVN0aW1tZW4gYmVzc2VyIGFscyBhbHRlIGxva2FsZQogIGlmICh3YW50ID09PSAiZGUiICYmIC8oa2F0amF8c2VyYXBoaW5hfGhlZGRhfGdpc2VsYXxhbWFsYXxtYXJsZW5lfGNocmlzdGVsfHBldHJhfGZlbWFsZXxmcmF1KS8udGVzdChuYW1lKSkgcyArPSA0NTsKICBpZiAod2FudCA9PT0gImVuIiAmJiAvKHNvbmlhfGxpYmJ5fGhhemVsfGFyaWF8amVubnl8ZW1tYXxmZW1hbGUpLy50ZXN0KG5hbWUpKSBzICs9IDQ1OwogIHJldHVybiBzOwp9CgpmdW5jdGlvbiBiZXN0Vm9pY2Uod2FudCl7CiAgbGV0IGJlc3QgPSBudWxsLCBicyA9IC0xZTk7CiAgYWxsVm9pY2VzLmZvckVhY2godiA9PiB7IGNvbnN0IHIgPSB2b2ljZVJhbmsodiwgd2FudCk7IGlmIChyID4gYnMpeyBicyA9IHI7IGJlc3QgPSB2OyB9IH0pOwogIHJldHVybiBiZXN0Owp9CgpmdW5jdGlvbiBidWlsZFZvaWNlTGlzdCgpewogIGlmICghKCJzcGVlY2hTeW50aGVzaXMiIGluIHdpbmRvdykpIHJldHVybjsKICBhbGxWb2ljZXMgPSBzcGVlY2hTeW50aGVzaXMuZ2V0Vm9pY2VzKCkgfHwgW107CiAgaWYgKCFhbGxWb2ljZXMubGVuZ3RoKSByZXR1cm47CiAgdm9pY2VERSA9IGJlc3RWb2ljZSgiZGUiKTsKICB2b2ljZUVOID0gYmVzdFZvaWNlKCJlbiIpOwogIC8vIERyb3Bkb3duOiBiZXN0ZSAoZGV1dHNjaGUsIG5hdHVlcmxpY2hlKSBTdGltbWVuIHp1ZXJzdDsgIkF1dG9tYXRpc2NoIiBnYW56IG9iZW4KICBjb25zdCBzb3J0ZWQgPSBhbGxWb2ljZXMuc2xpY2UoKS5zb3J0KChhLCBiKSA9PgogICAgTWF0aC5tYXgodm9pY2VSYW5rKGIsImRlIiksIHZvaWNlUmFuayhiLCJlbiIpKSAtIE1hdGgubWF4KHZvaWNlUmFuayhhLCJkZSIpLCB2b2ljZVJhbmsoYSwiZW4iKSkpOwogIGNvbnN0IHNlbCA9ICQoInZvaWNlU2VsZWN0Iik7CiAgaWYgKHNlbCl7CiAgICBzZWwuaW5uZXJIVE1MID0gIiI7CiAgICBjb25zdCBhdXRvID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgib3B0aW9uIik7CiAgICBhdXRvLnZhbHVlID0gIl9fYXV0b19fIjsgYXV0by50ZXh0Q29udGVudCA9ICJBdXRvbWF0aXNjaCAoYmVzdGUgU3RpbW1lKSI7CiAgICBzZWwuYXBwZW5kQ2hpbGQoYXV0byk7CiAgICBzb3J0ZWQuZm9yRWFjaCh2ID0+IHsKICAgICAgY29uc3QgbyA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoIm9wdGlvbiIpOwogICAgICBvLnZhbHVlID0gdi52b2ljZVVSSTsKICAgICAgby50ZXh0Q29udGVudCA9IHYubmFtZSArICIgKCIgKyB2LmxhbmcgKyAiKSI7CiAgICAgIHNlbC5hcHBlbmRDaGlsZChvKTsKICAgIH0pOwogIH0KICBjb25zdCBzYXZlZCA9IGxvY2FsU3RvcmFnZS5nZXRJdGVtKCJkaW5vX3ZvaWNlIik7CiAgaWYgKHNhdmVkICYmIHNhdmVkICE9PSAiX19hdXRvX18iKXsKICAgIHNlbGVjdGVkVm9pY2UgPSBhbGxWb2ljZXMuZmluZCh2ID0+IHYudm9pY2VVUkkgPT09IHNhdmVkKSB8fCBudWxsOwogICAgdm9pY2VNYW51YWwgPSAhIXNlbGVjdGVkVm9pY2U7CiAgfSBlbHNlIHsKICAgIHNlbGVjdGVkVm9pY2UgPSBudWxsOyB2b2ljZU1hbnVhbCA9IGZhbHNlOwogIH0KICBpZiAoc2VsKSBzZWwudmFsdWUgPSAodm9pY2VNYW51YWwgJiYgc2VsZWN0ZWRWb2ljZSkgPyBzZWxlY3RlZFZvaWNlLnZvaWNlVVJJIDogIl9fYXV0b19fIjsKfQoKZnVuY3Rpb24gb25Wb2ljZVNlbGVjdCgpewogIGNvbnN0IHNlbCA9ICQoInZvaWNlU2VsZWN0Iik7CiAgaWYgKHNlbC52YWx1ZSA9PT0gIl9fYXV0b19fIil7CiAgICBzZWxlY3RlZFZvaWNlID0gbnVsbDsgdm9pY2VNYW51YWwgPSBmYWxzZTsKICAgIGxvY2FsU3RvcmFnZS5zZXRJdGVtKCJkaW5vX3ZvaWNlIiwgIl9fYXV0b19fIik7CiAgfSBlbHNlIHsKICAgIHNlbGVjdGVkVm9pY2UgPSBhbGxWb2ljZXMuZmluZCh2ID0+IHYudm9pY2VVUkkgPT09IHNlbC52YWx1ZSkgfHwgbnVsbDsKICAgIHZvaWNlTWFudWFsID0gISFzZWxlY3RlZFZvaWNlOwogICAgaWYgKHNlbGVjdGVkVm9pY2UpIGxvY2FsU3RvcmFnZS5zZXRJdGVtKCJkaW5vX3ZvaWNlIiwgc2VsZWN0ZWRWb2ljZS52b2ljZVVSSSk7CiAgfQogIGNvbnN0IHByZXYgPSBzdGF0ZS52b2ljZU9uOyBzdGF0ZS52b2ljZU9uID0gdHJ1ZTsKICBzcGVhaygiSGFsbG8sIGljaCBiaW4gRGlubywgZGVpbmUgZWlnZW5lIEtJLiIpOwogIHN0YXRlLnZvaWNlT24gPSBwcmV2Owp9CgppZiAoInNwZWVjaFN5bnRoZXNpcyIgaW4gd2luZG93KXsKICBidWlsZFZvaWNlTGlzdCgpOwogIHNwZWVjaFN5bnRoZXNpcy5vbnZvaWNlc2NoYW5nZWQgPSBidWlsZFZvaWNlTGlzdDsKfSBlbHNlIHsKICAkKCJ2b2ljZUJ0biIpLnN0eWxlLmRpc3BsYXkgPSAibm9uZSI7CiAgY29uc3QgdnMgPSAkKCJ2b2ljZVNlbGVjdCIpOyBpZiAodnMpIHZzLnN0eWxlLmRpc3BsYXkgPSAibm9uZSI7Cn0KCmZ1bmN0aW9uIHRvZ2dsZVZvaWNlKCl7CiAgc3RhdGUudm9pY2VPbiA9ICFzdGF0ZS52b2ljZU9uOwogICQoInZvaWNlQnRuIikuY2xhc3NMaXN0LnRvZ2dsZSgiYWN0aXZlIiwgc3RhdGUudm9pY2VPbik7CiAgaWYgKCFzdGF0ZS52b2ljZU9uICYmICJzcGVlY2hTeW50aGVzaXMiIGluIHdpbmRvdyl7IHNwZWVjaFN5bnRoZXNpcy5jYW5jZWwoKTsgcmV0dXJuOyB9CiAgaWYgKHN0YXRlLnZvaWNlT24pIHNwZWFrKCJTcHJhY2hhdXNnYWJlIGFrdGl2LiIpOwp9CgovLyBTcHJhY2hlIGRlcyBUZXh0ZXMgZ3JvYiBlcmtlbm5lbiAoRGlubyBzcHJpY2h0IHN0YW5kYXJkbWFlc3NpZyBEZXV0c2NoKS4KZnVuY3Rpb24gZGV0ZWN0TGFuZyh0ZXh0KXsKICBjb25zdCB0ID0gKHRleHQgfHwgIiIpLnRvTG93ZXJDYXNlKCk7CiAgaWYgKC9bw6TDtsO8w59dLy50ZXN0KHQpKSByZXR1cm4gImRlIjsKICBpZiAoL1xiKHVuZHxpY2h8bmljaHR8ZGVyfGRpZXxkYXN8aXN0fGVpbnxtaXR8ZsO8cnxhdWZ8ZGVpbnxkZWluZXx3aXJ8aGFzdHxtYWNofGt1bmRlbnxnZWxkfHdvY2hlfGhldXRlKVxiLy50ZXN0KHQpKSByZXR1cm4gImRlIjsKICBpZiAoL1xiKHRoZXx5b3V8YW5kfHlvdXJ8d2l0aHxmb3J8dGhpc3x0aGF0fGFyZXxsZXR8bWFrZXxtb25leSlcYi8udGVzdCh0KSkgcmV0dXJuICJlbiI7CiAgcmV0dXJuICJkZSI7Cn0KCi8vIFRleHQgdm9ybGVzZWZyZXVuZGxpY2ggbWFjaGVuOiBFbW9qaXMsIE1hcmtkb3duLCBMaW5rcyAmIFN5bWJvbGUgcmF1cy4KZnVuY3Rpb24gY2xlYW5Gb3JTcGVlY2godGV4dCl7CiAgbGV0IHQgPSB0ZXh0IHx8ICIiOwogIHQgPSB0LnJlcGxhY2UoL2BgYFtcc1xTXSo/YGBgL2csICIgIik7ICAgICAgICAgICAgICAgICAvLyBDb2RlYmxvZWNrZQogIHQgPSB0LnJlcGxhY2UoL2AoW15gXSopYC9nLCAiJDEiKTsgICAgICAgICAgICAgICAgICAgICAgLy8gSW5saW5lLUNvZGUKICB0ID0gdC5yZXBsYWNlKC8hP1xbKFteXF1dKilcXVwoW14pXSpcKS9nLCAiJDEiKTsgICAgICAgIC8vIE1hcmtkb3duLUxpbmtzIC0+IG51ciBUZXh0CiAgdCA9IHQucmVwbGFjZSgvaHR0cHM/OlwvXC9cUysvZywgIiAiKTsgICAgICAgICAgICAgICAgICAvLyBuYWNrdGUgVVJMcwogIHQgPSB0LnJlcGxhY2UoL1tccHtFeHRlbmRlZF9QaWN0b2dyYXBoaWN9XHV7MUYxRTZ9LVx1ezFGMUZGfe+4j+KDo10vZ3UsICIgIik7IC8vIEVtb2ppcwogIHQgPSB0LnJlcGxhY2UoL1sqXyM+fnxdL2csICIgIik7ICAgICAgICAgICAgICAgICAgICAgICAgLy8gTWFya2Rvd24tWmVpY2hlbgogIHQgPSB0LnJlcGxhY2UoLyhefFxuKVsgXHRdKltcLeKAk+KAosK3XStbIFx0XS9nLCAiJDEiKTsgICAgICAvLyBBdWZ6YWVobHVuZ3NwdW5rdGUKICB0ID0gdC5yZXBsYWNlKC/igqwvZywgIiBFdXJvIik7ICAgICAgICAgICAgICAgICAgICAgICAgICAgLy8gU3ltYm9sIHNhdWJlciBhdXNzcHJlY2hlbgogIHQgPSB0LnJlcGxhY2UoL1sgXHRdKy9nLCAiICIpLnJlcGxhY2UoL1xzKlxuXHMqL2csICIuICIpLnRyaW0oKTsKICByZXR1cm4gdDsKfQoKLy8gSW4ga3VyemUgSGFlcHBjaGVuIHRlaWxlbiAtPiBrZWluIEFic2NobmVpZGVuIGJlaSBsYW5nZW4gVGV4dGVuIChzb25zdCAiYWJnZWhhY2t0IikuCmZ1bmN0aW9uIHNwbGl0U3BlZWNoKHRleHQpewogIGNvbnN0IHBhcnRzID0gdGV4dC5zcGxpdCgvKD88PVtcLlwhXD9cOlw7XSlccysvKTsKICBjb25zdCBvdXQgPSBbXTsgbGV0IGJ1ZiA9ICIiOwogIHBhcnRzLmZvckVhY2gocCA9PiB7CiAgICBwID0gcC50cmltKCk7IGlmICghcCkgcmV0dXJuOwogICAgaWYgKChidWYgKyAiICIgKyBwKS50cmltKCkubGVuZ3RoIDw9IDE4MCkgYnVmID0gYnVmID8gYnVmICsgIiAiICsgcCA6IHA7CiAgICBlbHNlIHsgaWYgKGJ1Zikgb3V0LnB1c2goYnVmKTsgYnVmID0gcDsgfQogIH0pOwogIGlmIChidWYpIG91dC5wdXNoKGJ1Zik7CiAgcmV0dXJuIG91dDsKfQoKZnVuY3Rpb24gc3BlYWsodGV4dCl7CiAgaWYgKCFzdGF0ZS52b2ljZU9uIHx8ICF0ZXh0IHx8ICEoInNwZWVjaFN5bnRoZXNpcyIgaW4gd2luZG93KSkgcmV0dXJuOwogIGNvbnN0IGNsZWFuID0gY2xlYW5Gb3JTcGVlY2godGV4dCk7CiAgaWYgKCFjbGVhbikgcmV0dXJuOwogIC8vIEF1dG9tYXRpc2NoIGRpZSB6dXIgU3ByYWNoZSBwYXNzZW5kZSBTdGltbWUgbmVobWVuIChlbmdsLiBTdGltbWUgKyBkdC4gVGV4dCA9IGFiZ2VoYWNrdCEpCiAgbGV0IHZvaWNlID0gc2VsZWN0ZWRWb2ljZTsKICBpZiAoIXZvaWNlTWFudWFsIHx8ICF2b2ljZSl7CiAgICB2b2ljZSA9IChkZXRlY3RMYW5nKGNsZWFuKSA9PT0gImVuIikgPyAodm9pY2VFTiB8fCB2b2ljZURFKSA6ICh2b2ljZURFIHx8IHZvaWNlRU4pOwogIH0KICB0cnl7CiAgICBzcGVlY2hTeW50aGVzaXMuY2FuY2VsKCk7CiAgICBjb25zdCBjaHVua3MgPSBzcGxpdFNwZWVjaChjbGVhbik7CiAgICBjaHVua3MuZm9yRWFjaCgoYywgaSkgPT4gewogICAgICBjb25zdCB1ID0gbmV3IFNwZWVjaFN5bnRoZXNpc1V0dGVyYW5jZShjKTsKICAgICAgaWYgKHZvaWNlKXsgdS52b2ljZSA9IHZvaWNlOyB1LmxhbmcgPSB2b2ljZS5sYW5nOyB9CiAgICAgIGVsc2UgeyB1LmxhbmcgPSBkZXRlY3RMYW5nKGNsZWFuKSA9PT0gImVuIiA/ICJlbi1HQiIgOiAiZGUtREUiOyB9CiAgICAgIHUucmF0ZSA9IDEuMDsgICAgIC8vIG5hdHVlcmxpY2hlcyBUZW1wbwogICAgICB1LnBpdGNoID0gMS4wMzsgICAvLyBsZWljaHQgaG9laGVyIC0+IHJ1aGlnZSBLSS1Bc3Npc3RlbnRpbgogICAgICBpZiAoaSA9PT0gMCkgdS5vbnN0YXJ0ID0gKCkgPT4gc2V0U3BlYWtpbmcodHJ1ZSk7CiAgICAgIGlmIChpID09PSBjaHVua3MubGVuZ3RoIC0gMSkgdS5vbmVuZCA9ICgpID0+IHNldFNwZWFraW5nKGZhbHNlKTsKICAgICAgdS5vbmVycm9yID0gKCkgPT4gc2V0U3BlYWtpbmcoZmFsc2UpOwogICAgICBzcGVlY2hTeW50aGVzaXMuc3BlYWsodSk7CiAgICB9KTsKICB9Y2F0Y2goZSl7IC8qIHN0aWxsICovIH0KfQoKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09Ci8vICBTcHJhY2hlcmtlbm51bmcgKFNwZWVjaFJlY29nbml0aW9uKQovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KbGV0IHJlY29nID0gbnVsbCwgbGlzdGVuaW5nID0gZmFsc2U7CihmdW5jdGlvbiBpbml0TWljKCl7CiAgY29uc3QgU1IgPSB3aW5kb3cuU3BlZWNoUmVjb2duaXRpb24gfHwgd2luZG93LndlYmtpdFNwZWVjaFJlY29nbml0aW9uOwogIGlmICghU1IpeyAkKCJtaWNCdG4iKS5zdHlsZS5kaXNwbGF5ID0gIm5vbmUiOyByZXR1cm47IH0gLy8gbmljaHQgdW50ZXJzdMO8dHp0IC0+IGVsZWdhbnQgYXVzYmxlbmRlbgogIHJlY29nID0gbmV3IFNSKCk7CiAgcmVjb2cubGFuZyA9ICJkZS1ERSI7CiAgcmVjb2cuaW50ZXJpbVJlc3VsdHMgPSBmYWxzZTsKICByZWNvZy5tYXhBbHRlcm5hdGl2ZXMgPSAxOwogIHJlY29nLm9ucmVzdWx0ID0gKGUpPT57CiAgICBjb25zdCB0ID0gZS5yZXN1bHRzWzBdWzBdLnRyYW5zY3JpcHQ7CiAgICBpbnB1dEVsLnZhbHVlID0gKGlucHV0RWwudmFsdWUgPyBpbnB1dEVsLnZhbHVlKyIgIiA6ICIiKSArIHQ7CiAgICBhdXRvR3JvdygpOyBpbnB1dEVsLmZvY3VzKCk7CiAgfTsKICByZWNvZy5vbmVycm9yID0gKCk9PiBzdG9wTWljKCk7CiAgcmVjb2cub25lbmQgPSAoKT0+IHN0b3BNaWMoKTsKfSkoKTsKZnVuY3Rpb24gdG9nZ2xlTWljKCl7CiAgaWYgKCFyZWNvZykgcmV0dXJuOwogIGlmIChsaXN0ZW5pbmcpeyByZWNvZy5zdG9wKCk7IHN0b3BNaWMoKTsgfQogIGVsc2UgeyB0cnl7IHJlY29nLnN0YXJ0KCk7IGxpc3RlbmluZyA9IHRydWU7ICQoIm1pY0J0biIpLmNsYXNzTGlzdC5hZGQoImxpc3RlbmluZyIpOyB9Y2F0Y2goZSl7IHN0b3BNaWMoKTsgfSB9Cn0KZnVuY3Rpb24gc3RvcE1pYygpeyBsaXN0ZW5pbmcgPSBmYWxzZTsgJCgibWljQnRuIikuY2xhc3NMaXN0LnJlbW92ZSgibGlzdGVuaW5nIik7IH0KCi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQovLyAgUGFuZWxzIChTbGlkZS1PdmVyKQovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KZnVuY3Rpb24gb3BlblBhbmVsKG5hbWUpewogIGNsb3NlUGFuZWxzKCk7CiAgJCgib3ZlcmxheSIpLmNsYXNzTGlzdC5hZGQoIm9wZW4iKTsKICBjb25zdCBwID0gJCgicGFuZWwtIituYW1lKTsKICBpZiAocCkgcC5jbGFzc0xpc3QuYWRkKCJvcGVuIik7CiAgaWYgKG5hbWUgPT09ICJzZXR0aW5ncyIpIGxvYWRTZXR0aW5ncygpOwogIGlmIChuYW1lID09PSAiY3VzdG9tZXJzIikgbG9hZEN1c3RvbWVycygpOwogIGlmIChuYW1lID09PSAibWVtb3J5IikgbG9hZE1lbW9yeSgpOwp9CmZ1bmN0aW9uIGNsb3NlUGFuZWxzKCl7CiAgJCgib3ZlcmxheSIpLmNsYXNzTGlzdC5yZW1vdmUoIm9wZW4iKTsKICBkb2N1bWVudC5xdWVyeVNlbGVjdG9yQWxsKCIucGFuZWwiKS5mb3JFYWNoKHAgPT4gcC5jbGFzc0xpc3QucmVtb3ZlKCJvcGVuIikpOwp9CmRvY3VtZW50LmFkZEV2ZW50TGlzdGVuZXIoImtleWRvd24iLCBlID0+IHsgaWYgKGUua2V5ID09PSAiRXNjYXBlIikgY2xvc2VQYW5lbHMoKTsgfSk7CgovLyAtLS0tLS0tLS0tIEVpbnN0ZWxsdW5nZW4gLS0tLS0tLS0tLQphc3luYyBmdW5jdGlvbiBsb2FkU2V0dGluZ3MoKXsKICBjb25zdCBib2R5ID0gJCgic2V0dGluZ3NCb2R5Iik7CiAgYm9keS5pbm5lckhUTUwgPSAnPGRpdiBjbGFzcz0iZW1wdHkiPmzDpGR04oCmPC9kaXY+JzsKICBsZXQgczsKICB0cnkgeyBzID0gYXdhaXQgYXBpKCIvYXBpL3NldHRpbmdzIik7IH0KICBjYXRjaChlKXsgYm9keS5pbm5lckhUTUwgPSAiIjsgYm9keS5hcHBlbmRDaGlsZChlcnJCb3goIktvbm50ZSBFaW5zdGVsbHVuZ2VuIG5pY2h0IGxhZGVuOiAiK2UubWVzc2FnZSkpOyByZXR1cm47IH0KICBpZiAocy5lcnJvcil7IGJvZHkuaW5uZXJIVE1MPSIiOyBib2R5LmFwcGVuZENoaWxkKGVyckJveChzLmVycm9yKSk7IHJldHVybjsgfQoKICBjb25zdCBrZXlzID0gcy5rZXlzIHx8IHt9OwogIGNvbnN0IHBlcnNvbmEgPSBzLnBlcnNvbmEgfHwge307CiAgY29uc3QgY2xhdWRlTW9kZWxzID0gcy5jbGF1ZGVfbW9kZWxzIHx8IFtdOwoKICAvLyBDbGF1ZGUtTW9kZWxsLU9wdGlvbmVuCiAgY29uc3QgY21PcHRzID0gY2xhdWRlTW9kZWxzLm1hcChtID0+CiAgICBgPG9wdGlvbiB2YWx1ZT0iJHtlc2MobVswXSl9IiAke21bMF09PT1zLmNsYXVkZV9tb2RlbD8ic2VsZWN0ZWQiOiIifT4ke2VzYyhtWzFdKX08L29wdGlvbj5gKS5qb2luKCIiKTsKCiAgLy8gR3JhdGlzLU1vZGVsbC1PcHRpb25lbiAoT2xsYW1hKS4gQWt0dWVsbGVzIE1vZGVsbCBhdWZuZWhtZW4sIGZhbGxzIGVpZ2VuZXMuCiAgY29uc3Qgb2xsYW1hTW9kZWxzID0gcy5vbGxhbWFfbW9kZWxzIHx8IFtdOwogIGNvbnN0IG9tQ3VyID0gcy5vbGxhbWFfbW9kZWwgfHwgIiI7CiAgbGV0IG9tSXRlbXMgPSBvbGxhbWFNb2RlbHMuc2xpY2UoKTsKICBpZiAob21DdXIgJiYgIW9tSXRlbXMuc29tZShtID0+IG1bMF0gPT09IG9tQ3VyKSkgb21JdGVtcyA9IFtbb21DdXIsIG9tQ3VyICsgIiAoZWlnZW5lcykiXV0uY29uY2F0KG9tSXRlbXMpOwogIGNvbnN0IG9tT3B0cyA9IG9tSXRlbXMubWFwKG0gPT4KICAgIGA8b3B0aW9uIHZhbHVlPSIke2VzYyhtWzBdKX0iICR7bVswXT09PW9tQ3VyPyJzZWxlY3RlZCI6IiJ9PiR7ZXNjKG1bMV0pfTwvb3B0aW9uPmApLmpvaW4oIiIpOwoKICBjb25zdCBwcm92U2VsID0gKHApPT4gYDxvcHRpb24gdmFsdWU9IiR7cH0iICR7cy5wcm92aWRlcj09PXA/InNlbGVjdGVkIjoiIn0+YDsKCiAgYm9keS5pbm5lckhUTUwgPSBgCiAgICA8ZGl2IGNsYXNzPSJzZWN0Ij7wn5SRIEFQSS1TY2hsw7xzc2VsPC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPkNsYXVkZSAoZW1wZm9obGVuKTwvbGFiZWw+PGlucHV0IGlkPSJzdC1rZXktY2xhdWRlIiB0eXBlPSJwYXNzd29yZCIgcGxhY2Vob2xkZXI9InNrLWFudC3igKYiPjwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5DaGF0R1BUIC8gT3BlbkFJPC9sYWJlbD48aW5wdXQgaWQ9InN0LWtleS1vcGVuYWkiIHR5cGU9InBhc3N3b3JkIiBwbGFjZWhvbGRlcj0ic2st4oCmIj48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+R29vZ2xlIEdlbWluaTwvbGFiZWw+PGlucHV0IGlkPSJzdC1rZXktZ2VtaW5pIiB0eXBlPSJwYXNzd29yZCIgcGxhY2Vob2xkZXI9IkFJemHigKYiPjwvZGl2PgogICAgPGRpdiBjbGFzcz0iaGludCI+U2NobMO8c3NlbCBob2xlbjogPGNvZGU+Y29uc29sZS5hbnRocm9waWMuY29tPC9jb2RlPiDCtyA8Y29kZT5wbGF0Zm9ybS5vcGVuYWkuY29tL2FwaS1rZXlzPC9jb2RlPiDCtyA8Y29kZT5haXN0dWRpby5nb29nbGUuY29tL2FwaWtleTwvY29kZT48YnI+U2llIGJsZWliZW4gbG9rYWwgYXVmIGRlaW5lbSBQQy48L2Rpdj4KCiAgICA8ZGl2IGNsYXNzPSJzZWN0Ij7wn6egIFdlbGNoZXMgR2VoaXJuPzwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5BbmJpZXRlcjwvbGFiZWw+PHNlbGVjdCBpZD0ic3QtcHJvdmlkZXIiPgogICAgICAke3Byb3ZTZWwoImNsYXVkZSIpfUNsYXVkZTwvb3B0aW9uPiR7cHJvdlNlbCgib2xsYW1hIil98J+GkyBHcmF0aXMgbG9rYWwgKE9sbGFtYSk8L29wdGlvbj4ke3Byb3ZTZWwoIm9wZW5haSIpfUNoYXRHUFQgLyBPcGVuQUk8L29wdGlvbj4ke3Byb3ZTZWwoImdlbWluaSIpfUdlbWluaTwvb3B0aW9uPgogICAgPC9zZWxlY3Q+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPkNsYXVkZS1Nb2RlbGw8L2xhYmVsPjxzZWxlY3QgaWQ9InN0LWNsYXVkZS1tb2RlbCI+JHtjbU9wdHN9PC9zZWxlY3Q+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPk9wZW5BSS1Nb2RlbGw8L2xhYmVsPjxpbnB1dCBpZD0ic3Qtb3BlbmFpLW1vZGVsIiBwbGFjZWhvbGRlcj0iei5CLiBncHQtNS4xIj48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+R2VtaW5pLU1vZGVsbDwvbGFiZWw+PGlucHV0IGlkPSJzdC1nZW1pbmktbW9kZWwiIHBsYWNlaG9sZGVyPSJ6LkIuIGdlbWluaS0yLjUtcHJvIj48L2Rpdj4KCiAgICA8ZGl2IGNsYXNzPSJzZWN0Ij7wn4aTIEdyYXRpcyBsb2thbCAoT2xsYW1hKSDigJQgb2huZSBTY2hsw7xzc2VsPC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPkdyYXRpcy1Nb2RlbGw8L2xhYmVsPjxzZWxlY3QgaWQ9InN0LW9sbGFtYS1tb2RlbCI+JHtvbU9wdHN9PC9zZWxlY3Q+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJoaW50Ij5TdWNoIGRpciBkYXMgTW9kZWxsIG5hY2ggZGVpbmVtIFBDIGF1cy4gPGI+cXdlbjIuNTo3YjwvYj4gaXN0IGbDvHIgZGVpbmUgMTItR0ItR3JhZmlra2FydGUgZW1wZm9obGVuIOKAlCBkZXV0bGljaCBzY2hsYXVlciBhbHMgZGFzIGtsZWluZSBsbGFtYTMuMiB1bmQgdHJvdHpkZW0gZmxvdHQuIFdlbm4gZHUgYXVmIGVpbiBuZXVlcyBNb2RlbGwgd2VjaHNlbHN0LCBsw6RkdCBEaW5vIGVzIGJlaW0gbsOkY2hzdGVuIFN0YXJ0IDxiPmVpbm1hbGlnPC9iPiBoZXJ1bnRlciAoZWluIHBhYXIgTWludXRlbikuIEtvbXBsZXR0IGdyYXRpcyAmIG9mZmxpbmUuPC9kaXY+CgogICAgPGRpdiBjbGFzcz0ic2VjdCI+8J+OrSBQZXJzb25hPC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPk5hbWUgZGVyIEtJPC9sYWJlbD48aW5wdXQgaWQ9InN0LWFzc2lzdGFudCI+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPldpZSBEaW5vIGRpY2ggbmVubnQ8L2xhYmVsPjxpbnB1dCBpZD0ic3QtdXNlciI+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPkRlaW4gQnVzaW5lc3M8L2xhYmVsPjx0ZXh0YXJlYSBpZD0ic3QtYnVzaW5lc3MiPjwvdGV4dGFyZWE+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPlN0aWwgLyBIdW1vcjwvbGFiZWw+PHRleHRhcmVhIGlkPSJzdC1odW1vciI+PC90ZXh0YXJlYT48L2Rpdj4KCiAgICA8ZGl2IGNsYXNzPSJzZWN0Ij7wn46vIFppZWw8L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48dGV4dGFyZWEgaWQ9InN0LWdvYWwiPjwvdGV4dGFyZWE+PC9kaXY+CgogICAgPGRpdiBjbGFzcz0iYnRucm93Ij4KICAgICAgPGJ1dHRvbiBjbGFzcz0iYnRuIHByaW1hcnkiIGlkPSJzdC1zYXZlIj7wn5K+IFNwZWljaGVybjwvYnV0dG9uPgogICAgICA8c3BhbiBpZD0ic3QtbXNnIiBjbGFzcz0iaGludCIgc3R5bGU9ImFsaWduLXNlbGY6Y2VudGVyIj48L3NwYW4+CiAgICA8L2Rpdj4KICBgOwogIC8vIFdlcnRlIGVpbnNldHplbiAocGVyIC52YWx1ZSwgbmljaHQgaW4gaW5uZXJIVE1MIC0+IHNpY2hlcikKICAkKCJzdC1rZXktY2xhdWRlIikudmFsdWUgPSBrZXlzLmNsYXVkZSB8fCAiIjsKICAkKCJzdC1rZXktb3BlbmFpIikudmFsdWUgPSBrZXlzLm9wZW5haSB8fCAiIjsKICAkKCJzdC1rZXktZ2VtaW5pIikudmFsdWUgPSBrZXlzLmdlbWluaSB8fCAiIjsKICAkKCJzdC1vcGVuYWktbW9kZWwiKS52YWx1ZSA9IHMub3BlbmFpX21vZGVsIHx8ICIiOwogICQoInN0LWdlbWluaS1tb2RlbCIpLnZhbHVlID0gcy5nZW1pbmlfbW9kZWwgfHwgIiI7CiAgJCgic3Qtb2xsYW1hLW1vZGVsIikudmFsdWUgPSBzLm9sbGFtYV9tb2RlbCB8fCAiIjsKICAkKCJzdC1hc3Npc3RhbnQiKS52YWx1ZSA9IHBlcnNvbmEuYXNzaXN0YW50X25hbWUgfHwgIiI7CiAgJCgic3QtdXNlciIpLnZhbHVlID0gcGVyc29uYS51c2VyX25hbWUgfHwgIiI7CiAgJCgic3QtYnVzaW5lc3MiKS52YWx1ZSA9IHBlcnNvbmEuYnVzaW5lc3MgfHwgIiI7CiAgJCgic3QtaHVtb3IiKS52YWx1ZSA9IHBlcnNvbmEuaHVtb3IgfHwgIiI7CiAgJCgic3QtZ29hbCIpLnZhbHVlID0gcy5nb2FsIHx8ICIiOwoKICAkKCJzdC1zYXZlIikub25jbGljayA9IHNhdmVTZXR0aW5nczsKfQoKYXN5bmMgZnVuY3Rpb24gc2F2ZVNldHRpbmdzKCl7CiAgY29uc3QgYnRuID0gJCgic3Qtc2F2ZSIpOyBidG4uZGlzYWJsZWQgPSB0cnVlOwogIGNvbnN0IHBheWxvYWQgPSB7CiAgICBwcm92aWRlcjogJCgic3QtcHJvdmlkZXIiKS52YWx1ZSwKICAgIGNsYXVkZV9tb2RlbDogJCgic3QtY2xhdWRlLW1vZGVsIikudmFsdWUsCiAgICBvcGVuYWlfbW9kZWw6ICQoInN0LW9wZW5haS1tb2RlbCIpLnZhbHVlLnRyaW0oKSwKICAgIGdlbWluaV9tb2RlbDogJCgic3QtZ2VtaW5pLW1vZGVsIikudmFsdWUudHJpbSgpLAogICAgb2xsYW1hX21vZGVsOiAkKCJzdC1vbGxhbWEtbW9kZWwiKS52YWx1ZS50cmltKCksCiAgICBrZXlzOiB7CiAgICAgIGNsYXVkZTogJCgic3Qta2V5LWNsYXVkZSIpLnZhbHVlLnRyaW0oKSwKICAgICAgb3BlbmFpOiAkKCJzdC1rZXktb3BlbmFpIikudmFsdWUudHJpbSgpLAogICAgICBnZW1pbmk6ICQoInN0LWtleS1nZW1pbmkiKS52YWx1ZS50cmltKCksCiAgICB9LAogICAgcGVyc29uYTogewogICAgICBhc3Npc3RhbnRfbmFtZTogJCgic3QtYXNzaXN0YW50IikudmFsdWUudHJpbSgpLAogICAgICB1c2VyX25hbWU6ICQoInN0LXVzZXIiKS52YWx1ZS50cmltKCksCiAgICAgIGJ1c2luZXNzOiAkKCJzdC1idXNpbmVzcyIpLnZhbHVlLnRyaW0oKSwKICAgICAgaHVtb3I6ICQoInN0LWh1bW9yIikudmFsdWUudHJpbSgpLAogICAgfSwKICAgIGdvYWw6ICQoInN0LWdvYWwiKS52YWx1ZS50cmltKCksCiAgfTsKICBjb25zdCBtc2cgPSAkKCJzdC1tc2ciKTsKICB0cnl7CiAgICBjb25zdCByID0gYXdhaXQgYXBpKCIvYXBpL3NldHRpbmdzIiwgIlBPU1QiLCBwYXlsb2FkKTsKICAgIGlmIChyLmVycm9yKXsgbXNnLnRleHRDb250ZW50ID0gIuKaoCAiK3IuZXJyb3I7IG1zZy5zdHlsZS5jb2xvcj0idmFyKC0tcm9zZSkiOyB9CiAgICBlbHNlewogICAgICBtc2cudGV4dENvbnRlbnQgPSAiR2VzcGVpY2hlcnQg4pyTIjsgbXNnLnN0eWxlLmNvbG9yPSJ2YXIoLS1ncmVlbikiOwogICAgICBhd2FpdCBsb2FkU3RhdHVzKCk7ICAgICAgICAgICAgLy8gU3RhdHVzIG9iZW4gbmV1IGxhZGVuIChrw7xtbWVydCBzaWNoIHVtIEJlZ3LDvMOfdW5nL1NldHVwLUthcnRlKQogICAgfQogIH1jYXRjaChlKXsgbXNnLnRleHRDb250ZW50ID0gIuKaoCAiK2UubWVzc2FnZTsgbXNnLnN0eWxlLmNvbG9yPSJ2YXIoLS1yb3NlKSI7IH0KICBmaW5hbGx5eyBidG4uZGlzYWJsZWQgPSBmYWxzZTsgfQp9CgovLyAtLS0tLS0tLS0tIEt1bmRlbiAtLS0tLS0tLS0tCmFzeW5jIGZ1bmN0aW9uIGxvYWRDdXN0b21lcnMoKXsKICBjb25zdCBib2R5ID0gJCgiY3VzdG9tZXJzQm9keSIpOwogIGJvZHkuaW5uZXJIVE1MID0gJzxkaXYgY2xhc3M9ImVtcHR5Ij5sw6RkdOKApjwvZGl2Pic7CiAgbGV0IGQ7CiAgdHJ5IHsgZCA9IGF3YWl0IGFwaSgiL2FwaS9jdXN0b21lcnMiKTsgfQogIGNhdGNoKGUpeyBib2R5LmlubmVySFRNTD0iIjsgYm9keS5hcHBlbmRDaGlsZChlcnJCb3goIktvbm50ZSBLdW5kZW4gbmljaHQgbGFkZW46ICIrZS5tZXNzYWdlKSk7IHJldHVybjsgfQogIGlmIChkLmVycm9yKXsgYm9keS5pbm5lckhUTUw9IiI7IGJvZHkuYXBwZW5kQ2hpbGQoZXJyQm94KGQuZXJyb3IpKTsgcmV0dXJuOyB9CiAgcmVuZGVyQ3VzdG9tZXJzKGQpOwp9CgpmdW5jdGlvbiByZW5kZXJDdXN0b21lcnMoZCl7CiAgY29uc3QgYm9keSA9ICQoImN1c3RvbWVyc0JvZHkiKTsKICBib2R5LmlubmVySFRNTCA9ICIiOwogIGNvbnN0IHIgPSBkLnJldmVudWUgfHwge307CiAgY29uc3QgY3VzdHMgPSBkLmN1c3RvbWVycyB8fCBbXTsKCiAgLy8gVW1zYXR6LUJhbm5lcgogIGNvbnN0IHJldiA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOwogIHJldi5jbGFzc05hbWUgPSAicmV2ZW51ZSI7CiAgcmV2LmlubmVySFRNTCA9CiAgICBgPGRpdiBjbGFzcz0iYmlnIj4ke2V1cm8oci5tb250aGx5KX08L2Rpdj5gKwogICAgYDxkaXYgY2xhc3M9InN1YiI+TW9uYXRzdW1zYXR6IMK3IH4ke2V1cm8oci53ZWVrbHkpfS9Xb2NoZSDCtyAke3IuYWN0aXZlfHwwfSBha3RpdiDCtyAke3IubGVhZHN8fDB9IExlYWRzIMK3ICR7ci50b3RhbHx8MH0gZ2VzYW10PC9kaXY+YDsKICBib2R5LmFwcGVuZENoaWxkKHJldik7CgogIC8vICJOZXVlciBLdW5kZSIKICBjb25zdCBuZXdCdG4gPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJidXR0b24iKTsKICBuZXdCdG4uY2xhc3NOYW1lID0gImJ0biBwcmltYXJ5IjsgbmV3QnRuLnN0eWxlLm1hcmdpbkJvdHRvbT0iMTRweCI7IG5ld0J0bi50ZXh0Q29udGVudCA9ICLinpUgTmV1ZXIgS3VuZGUiOwogIG5ld0J0bi5vbmNsaWNrID0gKCk9PiBzaG93Q3VzdG9tZXJGb3JtKG51bGwpOwogIGJvZHkuYXBwZW5kQ2hpbGQobmV3QnRuKTsKCiAgaWYgKCFjdXN0cy5sZW5ndGgpewogICAgY29uc3QgZSA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBlLmNsYXNzTmFtZT0iZW1wdHkiOyBlLnRleHRDb250ZW50PSJOb2NoIGtlaW5lIEt1bmRlbi4gTGVnIGVpbmVuIGFuLiDwn5GlIjsKICAgIGJvZHkuYXBwZW5kQ2hpbGQoZSk7CiAgICByZXR1cm47CiAgfQogIGN1c3RzLmZvckVhY2goYyA9PiBib2R5LmFwcGVuZENoaWxkKGN1c3RDYXJkKGMpKSk7Cn0KCmZ1bmN0aW9uIGN1c3RDYXJkKGMpewogIGNvbnN0IGNhcmQgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgY2FyZC5jbGFzc05hbWUgPSAiY3VzdCI7CiAgY29uc3QgdG9wID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IHRvcC5jbGFzc05hbWU9InRvcCI7CiAgY29uc3Qgbm0gPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJzcGFuIik7IG5tLmNsYXNzTmFtZT0ibmFtZSI7IG5tLnRleHRDb250ZW50ID0gYy5uYW1lIHx8ICLigJQiOwogIGNvbnN0IGJkID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgic3BhbiIpOyBiZC5jbGFzc05hbWU9ImJhZGdlIjsgYmQudGV4dENvbnRlbnQgPSBjLnN0YXR1cyB8fCAi4oCUIjsKICB0b3AuYXBwZW5kQ2hpbGQobm0pOyB0b3AuYXBwZW5kQ2hpbGQoYmQpOyBjYXJkLmFwcGVuZENoaWxkKHRvcCk7CgogIGNvbnN0IG1ldGEgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgbWV0YS5jbGFzc05hbWU9Im1ldGEiOwogIGNvbnN0IHBhcnRzID0gW107CiAgaWYgKGMuYnJhbmNoZSkgcGFydHMucHVzaChjLmJyYW5jaGUpOwogIGlmIChjLnBha2V0KSBwYXJ0cy5wdXNoKGMucGFrZXQpOwogIG1ldGEudGV4dENvbnRlbnQgPSBwYXJ0cy5qb2luKCIgwrcgIik7CiAgaWYgKGMucHJlaXMpewogICAgY29uc3QgcCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoInNwYW4iKTsgcC5jbGFzc05hbWU9InByaWNlIjsgcC50ZXh0Q29udGVudCA9IChwYXJ0cy5sZW5ndGg/IiDCtyAiOiIiKSArIGV1cm8oYy5wcmVpcykrIi9Nb25hdCI7CiAgICBtZXRhLmFwcGVuZENoaWxkKHApOwogIH0KICBjYXJkLmFwcGVuZENoaWxkKG1ldGEpOwoKICBpZiAoYy5uYWVjaHN0ZXJfc2Nocml0dCl7CiAgICBjb25zdCBucyA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBucy5jbGFzc05hbWU9Im1ldGEiOyBucy50ZXh0Q29udGVudCA9ICLihpIgIiArIGMubmFlY2hzdGVyX3NjaHJpdHQ7CiAgICBjYXJkLmFwcGVuZENoaWxkKG5zKTsKICB9CiAgaWYgKGMua29udGFrdCl7CiAgICBjb25zdCBrID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IGsuY2xhc3NOYW1lPSJtZXRhIjsgay50ZXh0Q29udGVudCA9ICLinIkgIiArIGMua29udGFrdDsKICAgIGNhcmQuYXBwZW5kQ2hpbGQoayk7CiAgfQoKICBjb25zdCBhY3QgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgYWN0LmNsYXNzTmFtZT0iYWN0aW9ucyI7CiAgY29uc3QgZWRpdCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImJ1dHRvbiIpOyBlZGl0LmNsYXNzTmFtZT0iYnRuIHNtIjsgZWRpdC50ZXh0Q29udGVudD0i4pyP77iPIEJlYXJiZWl0ZW4iOwogIGVkaXQub25jbGljayA9ICgpPT4gc2hvd0N1c3RvbWVyRm9ybShjKTsKICBjb25zdCBkZWwgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJidXR0b24iKTsgZGVsLmNsYXNzTmFtZT0iYnRuIHNtIGRhbmdlciI7IGRlbC50ZXh0Q29udGVudD0i8J+XkSBMw7ZzY2hlbiI7CiAgZGVsLm9uY2xpY2sgPSAoKT0+IGRlbGV0ZUN1c3RvbWVyKGMpOwogIGFjdC5hcHBlbmRDaGlsZChlZGl0KTsgYWN0LmFwcGVuZENoaWxkKGRlbCk7CiAgY2FyZC5hcHBlbmRDaGlsZChhY3QpOwogIHJldHVybiBjYXJkOwp9CgovLyBJbmxpbmUtRm9ybXVsYXIgKG5ldS9iZWFyYmVpdGVuKSBhbHMgS2FydGUKZnVuY3Rpb24gc2hvd0N1c3RvbWVyRm9ybShjKXsKICBjb25zdCBpc0VkaXQgPSAhIWM7CiAgYyA9IGMgfHwge307CiAgY29uc3QgYm9keSA9ICQoImN1c3RvbWVyc0JvZHkiKTsKICBjb25zdCBmb3JtID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IGZvcm0uY2xhc3NOYW1lPSJjdXN0IjsKICBjb25zdCBzdGF0dXNPcHRzID0gc3RhdGUuc3RhdHVzVmFsdWVzLm1hcChzID0+CiAgICBgPG9wdGlvbiB2YWx1ZT0iJHtzfSIgJHsgKGMuc3RhdHVzfHwiTGVhZCIpPT09cyA/ICJzZWxlY3RlZCI6IiIgfT4ke3N9PC9vcHRpb24+YCkuam9pbigiIik7CiAgZm9ybS5pbm5lckhUTUwgPSBgCiAgICA8ZGl2IGNsYXNzPSJzZWN0IiBzdHlsZT0ibWFyZ2luLXRvcDowIj4ke2lzRWRpdCA/ICLinI/vuI8gS3VuZGUgYmVhcmJlaXRlbiIgOiAi4p6VIE5ldWVyIEt1bmRlIn08L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+TmFtZSAqPC9sYWJlbD48aW5wdXQgaWQ9ImNmLW5hbWUiPjwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5CcmFuY2hlPC9sYWJlbD48aW5wdXQgaWQ9ImNmLWJyYW5jaGUiPjwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5Lb250YWt0PC9sYWJlbD48aW5wdXQgaWQ9ImNmLWtvbnRha3QiPjwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5QYWtldDwvbGFiZWw+PGlucHV0IGlkPSJjZi1wYWtldCI+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPlByZWlzIOKCrCAvIE1vbmF0PC9sYWJlbD48aW5wdXQgaWQ9ImNmLXByZWlzIiB0eXBlPSJudW1iZXIiIHN0ZXA9ImFueSI+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPlN0YXR1czwvbGFiZWw+PHNlbGVjdCBpZD0iY2Ytc3RhdHVzIj4ke3N0YXR1c09wdHN9PC9zZWxlY3Q+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPk7DpGNoc3RlciBTY2hyaXR0PC9sYWJlbD48aW5wdXQgaWQ9ImNmLXNjaHJpdHQiPjwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5Ob3RpemVuPC9sYWJlbD48dGV4dGFyZWEgaWQ9ImNmLW5vdGl6ZW4iPjwvdGV4dGFyZWE+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJidG5yb3ciPgogICAgICA8YnV0dG9uIGNsYXNzPSJidG4gcHJpbWFyeSIgaWQ9ImNmLXNhdmUiPuKckyBTcGVpY2hlcm48L2J1dHRvbj4KICAgICAgPGJ1dHRvbiBjbGFzcz0iYnRuIiBpZD0iY2YtY2FuY2VsIj5BYmJyZWNoZW48L2J1dHRvbj4KICAgICAgPHNwYW4gaWQ9ImNmLW1zZyIgY2xhc3M9ImhpbnQiIHN0eWxlPSJhbGlnbi1zZWxmOmNlbnRlciI+PC9zcGFuPgogICAgPC9kaXY+CiAgYDsKICBib2R5LnByZXBlbmQoZm9ybSk7CiAgLy8gV2VydGUgZWluc2V0emVuIChzaWNoZXIsIHZpYSAudmFsdWUpCiAgJCgiY2YtbmFtZSIpLnZhbHVlID0gYy5uYW1lIHx8ICIiOwogICQoImNmLWJyYW5jaGUiKS52YWx1ZSA9IGMuYnJhbmNoZSB8fCAiIjsKICAkKCJjZi1rb250YWt0IikudmFsdWUgPSBjLmtvbnRha3QgfHwgIiI7CiAgJCgiY2YtcGFrZXQiKS52YWx1ZSA9IGMucGFrZXQgfHwgIiI7CiAgJCgiY2YtcHJlaXMiKS52YWx1ZSA9IGMucHJlaXMgIT0gbnVsbCA/IGMucHJlaXMgOiAiIjsKICAkKCJjZi1zY2hyaXR0IikudmFsdWUgPSBjLm5hZWNoc3Rlcl9zY2hyaXR0IHx8ICIiOwogICQoImNmLW5vdGl6ZW4iKS52YWx1ZSA9IGMubm90aXplbiB8fCAiIjsKICBmb3JtLnNjcm9sbEludG9WaWV3KHtiZWhhdmlvcjoic21vb3RoIiwgYmxvY2s6InN0YXJ0In0pOwoKICAkKCJjZi1jYW5jZWwiKS5vbmNsaWNrID0gKCk9PiBsb2FkQ3VzdG9tZXJzKCk7CiAgJCgiY2Ytc2F2ZSIpLm9uY2xpY2sgPSBhc3luYyAoKT0+ewogICAgY29uc3QgbmFtZSA9ICQoImNmLW5hbWUiKS52YWx1ZS50cmltKCk7CiAgICBjb25zdCBtc2cgPSAkKCJjZi1tc2ciKTsKICAgIGlmICghbmFtZSl7IG1zZy50ZXh0Q29udGVudD0iTmFtZSBmZWhsdC4iOyBtc2cuc3R5bGUuY29sb3I9InZhcigtLXJvc2UpIjsgcmV0dXJuOyB9CiAgICBjb25zdCBmaWVsZHMgPSB7CiAgICAgIG5hbWUsCiAgICAgIGJyYW5jaGU6ICQoImNmLWJyYW5jaGUiKS52YWx1ZS50cmltKCksCiAgICAgIGtvbnRha3Q6ICQoImNmLWtvbnRha3QiKS52YWx1ZS50cmltKCksCiAgICAgIHBha2V0OiAkKCJjZi1wYWtldCIpLnZhbHVlLnRyaW0oKSwKICAgICAgcHJlaXM6ICQoImNmLXByZWlzIikudmFsdWUudHJpbSgpLAogICAgICBzdGF0dXM6ICQoImNmLXN0YXR1cyIpLnZhbHVlLAogICAgICBuYWVjaHN0ZXJfc2Nocml0dDogJCgiY2Ytc2Nocml0dCIpLnZhbHVlLnRyaW0oKSwKICAgICAgbm90aXplbjogJCgiY2Ytbm90aXplbiIpLnZhbHVlLnRyaW0oKSwKICAgIH07CiAgICBjb25zdCBwYXlsb2FkID0gaXNFZGl0ID8gT2JqZWN0LmFzc2lnbih7IG9wOiJ1cGRhdGUiLCBpZDpjLmlkIH0sIGZpZWxkcykgOiBPYmplY3QuYXNzaWduKHsgb3A6ImFkZCIgfSwgZmllbGRzKTsKICAgICQoImNmLXNhdmUiKS5kaXNhYmxlZCA9IHRydWU7CiAgICB0cnl7CiAgICAgIGNvbnN0IHIgPSBhd2FpdCBhcGkoIi9hcGkvY3VzdG9tZXJzIiwgIlBPU1QiLCBwYXlsb2FkKTsKICAgICAgaWYgKHIuZXJyb3IpeyBtc2cudGV4dENvbnRlbnQ9IuKaoCAiK3IuZXJyb3I7IG1zZy5zdHlsZS5jb2xvcj0idmFyKC0tcm9zZSkiOyAkKCJjZi1zYXZlIikuZGlzYWJsZWQ9ZmFsc2U7IH0KICAgICAgZWxzZSByZW5kZXJDdXN0b21lcnMocik7ICAgICAvLyBBbnR3b3J0IGVudGjDpGx0IGN1c3RvbWVycyArIHJldmVudWUKICAgIH1jYXRjaChlKXsgbXNnLnRleHRDb250ZW50PSLimqAgIitlLm1lc3NhZ2U7IG1zZy5zdHlsZS5jb2xvcj0idmFyKC0tcm9zZSkiOyAkKCJjZi1zYXZlIikuZGlzYWJsZWQ9ZmFsc2U7IH0KICB9Owp9Cgphc3luYyBmdW5jdGlvbiBkZWxldGVDdXN0b21lcihjKXsKICBpZiAoIWNvbmZpcm0oYEt1bmRlIMK7JHtjLm5hbWV9wqsgd2lya2xpY2ggbMO2c2NoZW4/YCkpIHJldHVybjsKICB0cnl7CiAgICBjb25zdCByID0gYXdhaXQgYXBpKCIvYXBpL2N1c3RvbWVycyIsICJQT1NUIiwgeyBvcDoiZGVsZXRlIiwgaWQ6Yy5pZCB9KTsKICAgIGlmIChyLmVycm9yKXsgY29uc3QgYj0kKCJjdXN0b21lcnNCb2R5Iik7IGIucHJlcGVuZChlcnJCb3goci5lcnJvcikpOyB9CiAgICBlbHNlIHJlbmRlckN1c3RvbWVycyhyKTsKICB9Y2F0Y2goZSl7ICQoImN1c3RvbWVyc0JvZHkiKS5wcmVwZW5kKGVyckJveCgiTmV0endlcmtmZWhsZXI6ICIrZS5tZXNzYWdlKSk7IH0KfQoKLy8gLS0tLS0tLS0tLSBHZWTDpGNodG5pcyAtLS0tLS0tLS0tCmFzeW5jIGZ1bmN0aW9uIGxvYWRNZW1vcnkoKXsKICBjb25zdCBib2R5ID0gJCgibWVtb3J5Qm9keSIpOwogIGJvZHkuaW5uZXJIVE1MID0gJzxkaXYgY2xhc3M9ImVtcHR5Ij5sw6RkdOKApjwvZGl2Pic7CiAgbGV0IGQ7CiAgdHJ5IHsgZCA9IGF3YWl0IGFwaSgiL2FwaS9tZW1vcnkiKTsgfQogIGNhdGNoKGUpeyBib2R5LmlubmVySFRNTD0iIjsgYm9keS5hcHBlbmRDaGlsZChlcnJCb3goIktvbm50ZSBHZWTDpGNodG5pcyBuaWNodCBsYWRlbjogIitlLm1lc3NhZ2UpKTsgcmV0dXJuOyB9CiAgaWYgKGQuZXJyb3IpeyBib2R5LmlubmVySFRNTD0iIjsgYm9keS5hcHBlbmRDaGlsZChlcnJCb3goZC5lcnJvcikpOyByZXR1cm47IH0KCiAgYm9keS5pbm5lckhUTUwgPSAiIjsKICBjb25zdCBmYWN0cyA9IGQuZmFjdHMgfHwgW107CiAgY29uc3Qgam91cm5hbCA9IGQuam91cm5hbCB8fCBbXTsKCiAgY29uc3QgaDEgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgaDEuY2xhc3NOYW1lPSJzZWN0IjsgaDEudGV4dENvbnRlbnQ9IvCfp6AgV2FzIERpbm8gw7xiZXIgZGljaCB3ZWnDnyI7CiAgYm9keS5hcHBlbmRDaGlsZChoMSk7CiAgaWYgKGZhY3RzLmxlbmd0aCl7CiAgICBjb25zdCB1bCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoInVsIik7IHVsLmNsYXNzTmFtZT0iZmFjdGxpc3QiOwogICAgZmFjdHMuZm9yRWFjaChmID0+IHsgY29uc3QgbGk9ZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgibGkiKTsgbGkudGV4dENvbnRlbnQ9ZjsgdWwuYXBwZW5kQ2hpbGQobGkpOyB9KTsKICAgIGJvZHkuYXBwZW5kQ2hpbGQodWwpOwogIH0gZWxzZSB7CiAgICBjb25zdCBlPWRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBlLmNsYXNzTmFtZT0iZW1wdHkiOyBlLnRleHRDb250ZW50PSJOb2NoIGxlZXIg4oCUIGtsaWNrIGltIENoYXQgYXVmIMK78J+noCBMZXJuZW7Cqy4iOwogICAgYm9keS5hcHBlbmRDaGlsZChlKTsKICB9CgogIGNvbnN0IGgyID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IGgyLmNsYXNzTmFtZT0ic2VjdCI7IGgyLnRleHRDb250ZW50PSLwn5OTIExldHp0ZSBOb3RpemVuIChUYWdlYnVjaCkiOwogIGJvZHkuYXBwZW5kQ2hpbGQoaDIpOwogIGNvbnN0IGpXcmFwID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IGpXcmFwLmNsYXNzTmFtZT0iam91cm5hbCI7CiAgY29uc3QgbGFzdCA9IGpvdXJuYWwuc2xpY2UoLTE1KS5yZXZlcnNlKCk7CiAgaWYgKGxhc3QubGVuZ3RoKXsKICAgIGxhc3QuZm9yRWFjaChqPT57CiAgICAgIGNvbnN0IGxpbmUgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsKICAgICAgY29uc3QgZDIgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJzcGFuIik7IGQyLmNsYXNzTmFtZT0iZCI7IGQyLnRleHRDb250ZW50ID0gIlsiKyhqLmRhdGV8fCIiKSsiXSAiOwogICAgICBsaW5lLmFwcGVuZENoaWxkKGQyKTsKICAgICAgbGluZS5hcHBlbmRDaGlsZChkb2N1bWVudC5jcmVhdGVUZXh0Tm9kZShqLm5vdGV8fCIiKSk7CiAgICAgIGpXcmFwLmFwcGVuZENoaWxkKGxpbmUpOwogICAgfSk7CiAgfSBlbHNlIHsKICAgIGpXcmFwLmlubmVySFRNTCA9ICc8ZGl2IGNsYXNzPSJlbXB0eSI+KGxlZXIpPC9kaXY+JzsKICB9CiAgYm9keS5hcHBlbmRDaGlsZChqV3JhcCk7Cn0KCi8vIGtsZWluZSByb3RlIEZlaGxlcmJveCBmw7xyIFBhbmVscwpmdW5jdGlvbiBlcnJCb3godGV4dCl7CiAgY29uc3QgZSA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOwogIGUuY2xhc3NOYW1lID0gIm1zZyBlcnJvciI7IGUuc3R5bGUubWF4V2lkdGg9IjEwMCUiOwogIGNvbnN0IGIgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgYi5jbGFzc05hbWU9ImJ1YmJsZSI7IGIudGV4dENvbnRlbnQgPSB0ZXh0OwogIGUuYXBwZW5kQ2hpbGQoYik7CiAgcmV0dXJuIGU7Cn0KCi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQovLyAgU3RhcnQKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09CmxvYWRTdGF0dXMoKTsKaW5wdXRFbC5mb2N1cygpOwo8L3NjcmlwdD4KPC9ib2R5Pgo8L2h0bWw+Cg==").decode("utf-8")

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
import subprocess
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

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
    return {"error": err} if err else {"reply": text}


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
        data = text.encode("utf-8")
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
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _body(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length:
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
        elif path == "/favicon.ico":
            self.send_response(204); self.end_headers()
        else:
            self.send_response(404); self.end_headers()

    def do_POST(self):
        path = self.path.split("?")[0]
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
