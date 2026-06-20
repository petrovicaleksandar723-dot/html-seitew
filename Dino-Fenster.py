#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DINO KI - Fenster-Version in EINER Datei.

Oeffnet ein echtes Programm-Fenster (kein Browser, keine Adresse, kein Port).
Gratis & lokal ueber Ollama; richtet das Modell beim Start selbst ein.
Starten: Doppelklick auf Dino-Fenster-Start.bat  (oder: python Dino-Fenster.py)
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

# ── Kunden ─────────────────────────────────────────────────────────────
CUSTOMER_STATUS = ["Lead", "Angebot", "Aktiv", "Bezahlt", "Pausiert", "Beendet"]
ACTIVE_STATUS = {"Aktiv", "Bezahlt"}  # zählt zum laufenden Umsatz

DEFAULT_CONFIG = {
    "provider": "ollama",  # ab Werk gratis & lokal (kein Schlüssel nötig)
    "claude_model": "claude-opus-4-8",
    "openai_model": "",
    "gemini_model": "gemini-2.5-pro",
    "ollama_model": "llama3.2",
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
        model = self.config.get("ollama_model", "llama3.2")
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
        body = {"model": model, "messages": msgs, "stream": False,
                "options": {"num_predict": max_tokens}}
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


def _to_float(x):
    try:
        if isinstance(x, str):
            x = x.replace("€", "").replace(",", ".").strip()
            if not x:
                return 0.0
        return float(x)
    except (ValueError, TypeError):
        return 0.0


import threading

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox
except Exception:
    raise SystemExit(
        "Konnte das Fenster-Modul 'tkinter' nicht laden.\n"
        "Windows/Mac: ist normalerweise dabei.\n"
        "Linux: 'sudo apt install python3-tk' — oder nutze die Terminal-Version: python3 dino.py"
    )


# ── Farben (dunkles Theme, passend zu CleanLines) ──────────────────────
BG = "#0c0f1c"; CARD = "#141a2e"; FG = "#f4f6fb"; MUT = "#98a2b8"
ACCENT = "#60a5fa"; PURPLE = "#a78bfa"; GREEN = "#34d399"; AMBER = "#fbbf24"; ROSE = "#fb7185"
FONT = ("Segoe UI", 10); FONT_B = ("Segoe UI", 10, "bold"); FONT_H = ("Segoe UI", 15, "bold")


class DinoApp:
    def __init__(self, root):
        self.d = Dino()
        self.root = root
        self.history = []
        self.busy = False

        root.title("🦖 Dino KI")
        root.geometry("1040x720")
        root.minsize(900, 600)
        root.configure(bg=BG)

        self._setup_style()
        self._build_header()
        self._build_tabs()
        self._build_statusbar()

        self.refresh_customers()
        self.refresh_memory()
        self.load_settings_into_form()

        try:
            root.lift()
            root.attributes("-topmost", True)
            root.after(800, lambda: root.attributes("-topmost", False))
        except Exception:
            pass

        p = self.d.config["persona"]
        self.append_chat("dino", f"Hi {p['user_name']}! Ich bin {p['assistant_name']}. 🦖")
        if self.d.config["provider"] == "ollama":
            self.append_chat("info", "Ich richte mein lokales Gehirn ein — beim ersten Mal lade "
                                     "ich das KI-Modell (~2 GB, ein paar Minuten). Bitte warten…")
            self.root.after(400, self._startup_setup)
        elif not self.d.is_ready():
            self.append_chat("info", "Trag deinen API-Schlüssel unter »⚙ Einstellungen« ein, dann geht's los.")
        else:
            self.append_chat("dino", "Bin bereit — frag mich was! 🦖")

    # ── Start-Einrichtung (Ollama im Hintergrund) ──────────────────────
    def _log_to_chat(self, msg):
        self.root.after(0, lambda m=str(msg).strip(): self.append_chat("info", m) if m else None)

    def _startup_setup(self):
        def work():
            try:
                self.d.ensure_ollama(log=self._log_to_chat)
            except Exception as e:
                self._log_to_chat(f"Hinweis beim Einrichten: {e}")
            self.root.after(0, self._after_setup)
        threading.Thread(target=work, daemon=True).start()

    def _after_setup(self):
        self.update_brain_label()
        self.load_settings_into_form()
        self.append_chat("dino", f"So, alles bereit! Frag mich was, "
                                 f"{self.d.config['persona']['user_name']}. 🦖")

    # ── Style ──────────────────────────────────────────────────────────
    def _setup_style(self):
        st = ttk.Style()
        try:
            st.theme_use("clam")
        except tk.TclError:
            pass
        st.configure("TNotebook", background=BG, borderwidth=0)
        st.configure("TNotebook.Tab", background=CARD, foreground=MUT,
                     padding=(16, 8), font=FONT_B, borderwidth=0)
        st.map("TNotebook.Tab", background=[("selected", BG)], foreground=[("selected", ACCENT)])
        st.configure("TFrame", background=BG)
        st.configure("Card.TFrame", background=CARD)
        st.configure("TLabel", background=BG, foreground=FG, font=FONT)
        st.configure("Muted.TLabel", background=BG, foreground=MUT, font=FONT)
        st.configure("Head.TLabel", background=BG, foreground=FG, font=FONT_H)
        st.configure("TButton", background=CARD, foreground=FG, font=FONT_B, borderwidth=0, padding=8)
        st.map("TButton", background=[("active", "#1e2540")])
        st.configure("Accent.TButton", background=ACCENT, foreground="#06101f")
        st.map("Accent.TButton", background=[("active", "#7cb4ff")])
        st.configure("TEntry", fieldbackground=CARD, foreground=FG, insertcolor=FG, borderwidth=0)
        st.configure("TCombobox", fieldbackground=CARD, background=CARD, foreground=FG, borderwidth=0)
        st.configure("Treeview", background=CARD, fieldbackground=CARD, foreground=FG,
                     borderwidth=0, rowheight=26, font=FONT)
        st.configure("Treeview.Heading", background=BG, foreground=ACCENT, font=FONT_B, borderwidth=0)
        st.map("Treeview", background=[("selected", "#21407a")], foreground=[("selected", "#ffffff")])

    # ── Kopfzeile ──────────────────────────────────────────────────────
    def _build_header(self):
        head = tk.Frame(self.root, bg=BG)
        head.pack(fill="x", padx=16, pady=(12, 4))
        tk.Label(head, text="🦖 Dino KI", bg=BG, fg=FG, font=FONT_H).pack(side="left")
        self.brain_lbl = tk.Label(head, text="", bg=BG, fg=MUT, font=FONT)
        self.brain_lbl.pack(side="right")
        self.update_brain_label()

    def update_brain_label(self):
        r = self.d.revenue()
        self.brain_lbl.config(
            text=f"Gehirn: {self.d.provider_label()}   ·   "
                 f"{len(self.d.memory.get('facts', []))} Fakten   ·   "
                 f"{r['total']} Kunden")

    # ── Tabs ───────────────────────────────────────────────────────────
    def _build_tabs(self):
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True, padx=16, pady=8)
        self._tab_chat()
        self._tab_customers()
        self._tab_plan()
        self._tab_memory()
        self._tab_settings()

    # ── Tab: Chat ──────────────────────────────────────────────────────
    def _tab_chat(self):
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="💬 Chat")

        self.chat_box = scrolledtext.ScrolledText(
            f, wrap="word", bg=CARD, fg=FG, insertbackground=FG, relief="flat",
            font=("Segoe UI", 11), padx=14, pady=12, state="disabled", height=20)
        self.chat_box.pack(fill="both", expand=True, padx=4, pady=4)
        self.chat_box.tag_config("user", foreground=AMBER, font=("Segoe UI", 11, "bold"))
        self.chat_box.tag_config("dino", foreground=GREEN, font=("Segoe UI", 11, "bold"))
        self.chat_box.tag_config("body", foreground=FG, font=("Segoe UI", 11))
        self.chat_box.tag_config("info", foreground=MUT, font=("Segoe UI", 10, "italic"))
        self.chat_box.tag_config("error", foreground=ROSE, font=("Segoe UI", 10, "bold"))

        quick = tk.Frame(f, bg=BG)
        quick.pack(fill="x", padx=4)
        ttk.Button(quick, text="🧠 Lernen (merken)", command=self.on_learn).pack(side="left", padx=(0, 6))
        ttk.Button(quick, text="🧠🧠🧠 Rat der KIs", command=self.on_council).pack(side="left", padx=6)

        bar = tk.Frame(f, bg=BG)
        bar.pack(fill="x", padx=4, pady=(6, 4))
        self.entry = tk.Entry(bar, bg=CARD, fg=FG, insertbackground=FG, relief="flat", font=("Segoe UI", 11))
        self.entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        self.entry.bind("<Return>", lambda e: self.on_send())
        self.send_btn = ttk.Button(bar, text="Senden ➤", style="Accent.TButton", command=self.on_send)
        self.send_btn.pack(side="right")
        self.entry.focus_set()

    def append_chat(self, who, text):
        self.chat_box.config(state="normal")
        if who == "user":
            self.chat_box.insert("end", f"\n{self.d.config['persona']['user_name']}\n", "user")
            self.chat_box.insert("end", text + "\n", "body")
        elif who == "dino":
            self.chat_box.insert("end", f"\n🦖 {self.d.config['persona']['assistant_name']}\n", "dino")
            self.chat_box.insert("end", text + "\n", "body")
        else:
            self.chat_box.insert("end", f"\n{text}\n", who)
        self.chat_box.config(state="disabled")
        self.chat_box.see("end")

    def on_send(self):
        if self.busy:
            return
        msg = self.entry.get().strip()
        if not msg:
            return
        if not self.d.is_ready():
            self.append_chat("error", "Kein API-Schlüssel. Geh auf »⚙ Einstellungen« und trag einen ein.")
            return
        self.entry.delete(0, "end")
        self.append_chat("user", msg)
        self.history.append({"role": "user", "content": msg})
        self.d.add_journal(f"hat geschrieben: {msg}")
        self.run_bg(lambda: self.d.chat(self.history), self._on_chat_done)

    def _on_chat_done(self, result):
        text, err = result
        if err:
            self.append_chat("error", err)
            if self.history and self.history[-1]["role"] == "user":
                self.history.pop()
        else:
            self.append_chat("dino", text)
            self.history.append({"role": "assistant", "content": text})

    def on_learn(self):
        if self.busy:
            return
        if not self.history:
            self.append_chat("info", "Wir haben noch nicht geredet — nichts zu lernen. 😉")
            return
        self.append_chat("info", "🦖 Dino merkt sich gerade, was er gelernt hat…")
        self.run_bg(lambda: self.d.learn(self.history), self._on_learn_done)

    def _on_learn_done(self, result):
        count, err = result
        if err:
            self.append_chat("error", err)
        elif count:
            self.append_chat("info", f"Gemerkt! 🧠 Dino kennt jetzt {count} Fakten über dich.")
            self.refresh_memory()
            self.update_brain_label()
        else:
            self.append_chat("info", "Nichts Neues zum Merken gefunden.")

    def on_council(self):
        if self.busy:
            return
        frage = self.entry.get().strip()
        if not frage:
            messagebox.showinfo("Rat der KIs", "Schreib zuerst deine Frage ins Eingabefeld, dann »Rat der KIs«.")
            return
        self.entry.delete(0, "end")
        self.append_chat("user", frage)
        self.append_chat("info", "🧠🧠🧠 Frage Claude, ChatGPT & Gemini…")
        self.run_bg(lambda: self.d.rat(self.history, frage), self._on_council_done)

    def _on_council_done(self, result):
        answers, synthese, err = result
        if err:
            self.append_chat("error", err)
            return
        for name, ans in answers.items():
            self.append_chat("info", f"▸ {name}:")
            self.append_chat("dino", ans) if name == "Claude" else self._plain(ans)
        if synthese:
            self.append_chat("info", "✦ Dinos Fazit aus allen KIs:")
            self.append_chat("dino", synthese)
            self.history.append({"role": "assistant", "content": synthese})

    def _plain(self, text):
        self.chat_box.config(state="normal")
        self.chat_box.insert("end", text + "\n", "body")
        self.chat_box.config(state="disabled")
        self.chat_box.see("end")

    # ── Tab: Kunden ────────────────────────────────────────────────────
    def _tab_customers(self):
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="👥 Kunden")

        top = tk.Frame(f, bg=BG)
        top.pack(fill="x", padx=4, pady=(4, 0))
        ttk.Button(top, text="➕ Neuer Kunde", style="Accent.TButton",
                   command=self.customer_new).pack(side="left")
        ttk.Button(top, text="✏️ Bearbeiten", command=self.customer_edit).pack(side="left", padx=6)
        ttk.Button(top, text="🗑 Löschen", command=self.customer_delete).pack(side="left")
        self.rev_lbl = tk.Label(top, text="", bg=BG, fg=GREEN, font=FONT_B)
        self.rev_lbl.pack(side="right")

        cols = ("name", "branche", "paket", "preis", "status", "schritt")
        titles = ("Kunde", "Branche", "Paket", "€/Monat", "Status", "Nächster Schritt")
        widths = (170, 120, 150, 90, 90, 230)
        self.tree = ttk.Treeview(f, columns=cols, show="headings", height=16)
        for cidx, title, w in zip(cols, titles, widths):
            self.tree.heading(cidx, text=title)
            self.tree.column(cidx, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=4, pady=8)
        self.tree.bind("<Double-1>", lambda e: self.customer_edit())

    def refresh_customers(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for c in self.d.customers():
            self.tree.insert("", "end", iid=str(c["id"]), values=(
                c["name"], c.get("branche", ""), c.get("paket", ""),
                euro(c.get("preis", 0)), c.get("status", ""), c.get("naechster_schritt", "")))
        r = self.d.revenue()
        self.rev_lbl.config(text=f"💰 Monatsumsatz: {euro(r['monthly'])}  "
                                 f"(~{euro(r['weekly'])}/Woche)  ·  "
                                 f"{r['active']} aktiv, {r['leads']} Leads")
        self.update_brain_label()

    def _selected_customer_id(self):
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def customer_new(self):
        data = CustomerDialog(self.root, None).result
        if data:
            self.d.add_customer(**data)
            self.refresh_customers()

    def customer_edit(self):
        cid = self._selected_customer_id()
        if cid is None:
            messagebox.showinfo("Kunde", "Wähle zuerst einen Kunden in der Liste aus.")
            return
        cust = self.d.get_customer(cid)
        data = CustomerDialog(self.root, cust).result
        if data:
            self.d.update_customer(cid, **data)
            self.refresh_customers()

    def customer_delete(self):
        cid = self._selected_customer_id()
        if cid is None:
            messagebox.showinfo("Kunde", "Wähle zuerst einen Kunden aus.")
            return
        cust = self.d.get_customer(cid)
        if messagebox.askyesno("Löschen", f"Kunde »{cust['name']}« wirklich löschen?"):
            self.d.delete_customer(cid)
            self.refresh_customers()

    # ── Tab: Plan & Heute ──────────────────────────────────────────────
    def _tab_plan(self):
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="📈 Plan & Heute")

        top = tk.Frame(f, bg=BG)
        top.pack(fill="x", padx=4, pady=(4, 0))
        ttk.Button(top, text="📅 Wochen-Geldplan", style="Accent.TButton",
                   command=self.on_plan).pack(side="left")
        ttk.Button(top, text="☀️ Tages-Check-in (heute)", command=self.on_today).pack(side="left", padx=6)
        ttk.Button(top, text="🎯 Ziel ändern", command=self.on_goal).pack(side="left")

        self.goal_lbl = tk.Label(f, text="", bg=BG, fg=AMBER, font=FONT, wraplength=960, justify="left")
        self.goal_lbl.pack(fill="x", padx=6, pady=(8, 0))
        self.update_goal_label()

        self.plan_box = scrolledtext.ScrolledText(
            f, wrap="word", bg=CARD, fg=FG, relief="flat", font=("Segoe UI", 11),
            padx=14, pady=12, state="disabled")
        self.plan_box.pack(fill="both", expand=True, padx=4, pady=8)

    def update_goal_label(self):
        self.goal_lbl.config(text="🎯 Ziel: " + self.d.config["goal"])

    def _plan_out(self, text, clear=True):
        self.plan_box.config(state="normal")
        if clear:
            self.plan_box.delete("1.0", "end")
        self.plan_box.insert("end", text)
        self.plan_box.config(state="disabled")
        self.plan_box.see("1.0")

    def on_plan(self):
        if self.busy:
            return
        if not self.d.is_ready():
            messagebox.showinfo("Plan", "Trag zuerst einen Schlüssel unter Einstellungen ein.")
            return
        self._plan_out("🦖 Dino baut deinen Wochenplan…")
        self.run_bg(self.d.plan, lambda r: self._plan_done(r))

    def on_today(self):
        if self.busy:
            return
        if not self.d.is_ready():
            messagebox.showinfo("Heute", "Trag zuerst einen Schlüssel unter Einstellungen ein.")
            return
        self._plan_out("🦖 Dino schaut auf heute…")
        self.run_bg(self.d.tagescheckin, lambda r: self._plan_done(r))

    def _plan_done(self, result):
        text, err = result
        self._plan_out(("⚠ " + err) if err else text)
        self.refresh_memory()

    def on_goal(self):
        new = SimpleAsk(self.root, "Ziel ändern", "Was ist dein Ziel?", self.d.config["goal"]).result
        if new:
            self.d.config["goal"] = new.strip()
            self.d.save_config()
            self.update_goal_label()

    # ── Tab: Gedächtnis ────────────────────────────────────────────────
    def _tab_memory(self):
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="🧠 Gedächtnis")
        top = tk.Frame(f, bg=BG)
        top.pack(fill="x", padx=4, pady=(4, 0))
        ttk.Button(top, text="🔄 Aktualisieren", command=self.refresh_memory).pack(side="left")
        ttk.Button(top, text="🗑 Gedächtnis löschen", command=self.on_forget).pack(side="left", padx=6)
        self.mem_box = scrolledtext.ScrolledText(
            f, wrap="word", bg=CARD, fg=FG, relief="flat", font=("Segoe UI", 11),
            padx=14, pady=12, state="disabled")
        self.mem_box.pack(fill="both", expand=True, padx=4, pady=8)

    def refresh_memory(self):
        facts = self.d.memory.get("facts", [])
        journal = self.d.memory.get("journal", [])
        lines = ["WAS DINO ÜBER DICH WEISS\n"]
        lines += [f"• {x}" for x in facts] if facts else ["(noch leer — klick im Chat auf »Lernen«)"]
        lines.append("\n\nLETZTE NOTIZEN (Tagebuch)\n")
        lines += [f"[{j['date']}] {j['note']}" for j in journal[-15:]] if journal else ["(leer)"]
        self.mem_box.config(state="normal")
        self.mem_box.delete("1.0", "end")
        self.mem_box.insert("end", "\n".join(lines))
        self.mem_box.config(state="disabled")
        self.update_brain_label()

    def on_forget(self):
        if messagebox.askyesno("Gedächtnis löschen", "Wirklich Dinos ganzes Gedächtnis löschen?\n"
                                                      "(Kunden bleiben erhalten.)"):
            self.d.clear_memory()
            self.refresh_memory()

    # ── Tab: Einstellungen ─────────────────────────────────────────────
    def _tab_settings(self):
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="⚙ Einstellungen")
        wrap = tk.Frame(f, bg=BG)
        wrap.pack(fill="both", expand=True, padx=8, pady=8)

        self.s_vars = {}

        def section(title):
            tk.Label(wrap, text=title, bg=BG, fg=ACCENT, font=FONT_B).pack(anchor="w", pady=(12, 2))

        def field(label, key, show=None, width=64):
            row = tk.Frame(wrap, bg=BG)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, bg=BG, fg=MUT, font=FONT, width=22, anchor="w").pack(side="left")
            var = tk.StringVar()
            ent = tk.Entry(row, textvariable=var, bg=CARD, fg=FG, insertbackground=FG,
                           relief="flat", font=FONT, show=show)
            ent.pack(side="left", fill="x", expand=True, ipady=5)
            self.s_vars[key] = var
            return var

        section("🔑 API-Schlüssel (bleiben lokal auf deinem PC)")
        field("Claude (empfohlen)", "key_claude")
        field("ChatGPT / OpenAI", "key_openai")
        field("Google Gemini", "key_gemini")
        tk.Label(wrap, text="Schlüssel holen: console.anthropic.com · platform.openai.com/api-keys · aistudio.google.com/apikey",
                 bg=BG, fg=MUT, font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 0))

        section("🧠 Welches Gehirn?")
        prow = tk.Frame(wrap, bg=BG); prow.pack(fill="x", pady=2)
        tk.Label(prow, text="Anbieter", bg=BG, fg=MUT, font=FONT, width=22, anchor="w").pack(side="left")
        self.prov_var = tk.StringVar(value="claude")
        prov_box = ttk.Combobox(prow, textvariable=self.prov_var, state="readonly",
                                values=["claude", "ollama", "openai", "gemini"], width=14)
        prov_box.pack(side="left")
        mrow = tk.Frame(wrap, bg=BG); mrow.pack(fill="x", pady=2)
        tk.Label(mrow, text="Claude-Modell", bg=BG, fg=MUT, font=FONT, width=22, anchor="w").pack(side="left")
        self.cmodel_var = tk.StringVar()
        ttk.Combobox(mrow, textvariable=self.cmodel_var, state="readonly", width=22,
                     values=[m[0] for m in CLAUDE_MODELS.values()]).pack(side="left")
        field("OpenAI-Modell (z.B. gpt-5.1)", "openai_model", width=30)
        field("Gemini-Modell", "gemini_model", width=30)
        field("Gratis-Modell (Ollama)", "ollama_model", width=30)

        section("🎭 Persönlichkeit & Humor")
        field("Name der KI", "assistant_name", width=30)
        field("Wie Dino DICH nennt", "user_name", width=30)
        field("Dein Business", "business")
        field("Stil / Humor", "humor")

        section("🎯 Ziel")
        field("Dein Ziel", "goal")

        btnrow = tk.Frame(wrap, bg=BG); btnrow.pack(fill="x", pady=14)
        ttk.Button(btnrow, text="💾 Alles speichern", style="Accent.TButton",
                   command=self.save_settings).pack(side="left")

    def load_settings_into_form(self):
        cfg = self.d.config
        v = self.s_vars
        v["key_claude"].set(cfg["keys"]["claude"])
        v["key_openai"].set(cfg["keys"]["openai"])
        v["key_gemini"].set(cfg["keys"]["gemini"])
        v["openai_model"].set(cfg["openai_model"])
        v["gemini_model"].set(cfg["gemini_model"])
        v["ollama_model"].set(cfg.get("ollama_model", "llama3.2"))
        v["assistant_name"].set(cfg["persona"]["assistant_name"])
        v["user_name"].set(cfg["persona"]["user_name"])
        v["business"].set(cfg["persona"]["business"])
        v["humor"].set(cfg["persona"]["humor"])
        v["goal"].set(cfg["goal"])
        self.prov_var.set(cfg["provider"])
        self.cmodel_var.set(cfg["claude_model"])

    def save_settings(self):
        cfg = self.d.config
        v = self.s_vars
        cfg["keys"]["claude"] = v["key_claude"].get().strip()
        cfg["keys"]["openai"] = v["key_openai"].get().strip()
        cfg["keys"]["gemini"] = v["key_gemini"].get().strip()
        cfg["openai_model"] = v["openai_model"].get().strip()
        cfg["gemini_model"] = v["gemini_model"].get().strip() or "gemini-2.5-pro"
        cfg["ollama_model"] = v["ollama_model"].get().strip() or "llama3.2"
        cfg["claude_model"] = self.cmodel_var.get() or "claude-opus-4-8"
        cfg["provider"] = self.prov_var.get() or "claude"
        cfg["persona"]["assistant_name"] = v["assistant_name"].get().strip() or "Dino"
        cfg["persona"]["user_name"] = v["user_name"].get().strip() or "Boss"
        cfg["persona"]["business"] = v["business"].get().strip()
        cfg["persona"]["humor"] = v["humor"].get().strip()
        cfg["goal"] = v["goal"].get().strip()
        self.d.save_config()
        self.update_brain_label()
        self.update_goal_label()
        messagebox.showinfo("Gespeichert", "Einstellungen gespeichert. 🦖")

    # ── Statusleiste + Hintergrund-Aufgaben ────────────────────────────
    def _build_statusbar(self):
        self.status = tk.Label(self.root, text="bereit", bg=BG, fg=MUT, font=("Segoe UI", 9), anchor="w")
        self.status.pack(fill="x", side="bottom", padx=18, pady=(0, 6))

    def set_busy(self, busy):
        self.busy = busy
        self.status.config(text="🦖 Dino denkt nach…" if busy else "bereit",
                           fg=AMBER if busy else MUT)
        try:
            self.send_btn.config(state="disabled" if busy else "normal")
        except Exception:
            pass

    def run_bg(self, work, on_done):
        self.set_busy(True)

        def task():
            try:
                result = work()
            except Exception as e:
                result = ("__error__", str(e))
            self.root.after(0, lambda: self._finish(result, on_done))

        threading.Thread(target=task, daemon=True).start()

    def _finish(self, result, on_done):
        self.set_busy(False)
        if isinstance(result, tuple) and len(result) == 2 and result[0] == "__error__":
            self.append_chat("error", f"Unerwarteter Fehler: {result[1]}")
            return
        on_done(result)


# ── Dialog: Kunde anlegen / bearbeiten ─────────────────────────────────
class CustomerDialog:
    def __init__(self, parent, cust):
        self.result = None
        top = self.top = tk.Toplevel(parent)
        top.title("Kunde bearbeiten" if cust else "Neuer Kunde")
        top.configure(bg=BG)
        top.geometry("460x520")
        top.transient(parent)
        top.grab_set()

        self.vars = {}

        def row(label, key, default=""):
            tk.Label(top, text=label, bg=BG, fg=MUT, font=FONT).pack(anchor="w", padx=18, pady=(10, 0))
            var = tk.StringVar(value=str(default))
            tk.Entry(top, textvariable=var, bg=CARD, fg=FG, insertbackground=FG,
                     relief="flat", font=FONT).pack(fill="x", padx=18, ipady=5)
            self.vars[key] = var

        c = cust or {}
        row("Name *", "name", c.get("name", ""))
        row("Branche", "branche", c.get("branche", ""))
        row("Kontakt (Mail/Tel/@)", "kontakt", c.get("kontakt", ""))
        row("Paket", "paket", c.get("paket", ""))
        row("Preis € / Monat", "preis", c.get("preis", ""))

        tk.Label(top, text="Status", bg=BG, fg=MUT, font=FONT).pack(anchor="w", padx=18, pady=(10, 0))
        self.status_var = tk.StringVar(value=c.get("status", "Lead"))
        ttk.Combobox(top, textvariable=self.status_var, state="readonly",
                     values=CUSTOMER_STATUS).pack(fill="x", padx=18)

        row("Nächster Schritt", "naechster_schritt", c.get("naechster_schritt", ""))
        row("Notizen", "notizen", c.get("notizen", ""))

        btns = tk.Frame(top, bg=BG)
        btns.pack(fill="x", padx=18, pady=18)
        ttk.Button(btns, text="✓ Speichern", style="Accent.TButton", command=self._save).pack(side="left")
        ttk.Button(btns, text="Abbrechen", command=top.destroy).pack(side="right")

        top.bind("<Return>", lambda e: self._save())
        parent.wait_window(top)

    def _save(self):
        name = self.vars["name"].get().strip()
        if not name:
            messagebox.showinfo("Kunde", "Bitte einen Namen eingeben.")
            return
        self.result = {
            "name": name,
            "branche": self.vars["branche"].get(),
            "kontakt": self.vars["kontakt"].get(),
            "paket": self.vars["paket"].get(),
            "preis": self.vars["preis"].get(),
            "status": self.status_var.get(),
            "naechster_schritt": self.vars["naechster_schritt"].get(),
            "notizen": self.vars["notizen"].get(),
        }
        self.top.destroy()


# ── kleiner Eingabe-Dialog (mehrzeilig-tauglich) ───────────────────────
class SimpleAsk:
    def __init__(self, parent, title, label, default=""):
        self.result = None
        top = self.top = tk.Toplevel(parent)
        top.title(title); top.configure(bg=BG); top.geometry("520x200")
        top.transient(parent); top.grab_set()
        tk.Label(top, text=label, bg=BG, fg=FG, font=FONT).pack(anchor="w", padx=16, pady=(14, 4))
        self.txt = tk.Text(top, height=4, bg=CARD, fg=FG, insertbackground=FG, relief="flat", font=FONT)
        self.txt.pack(fill="both", expand=True, padx=16)
        self.txt.insert("1.0", default)
        btns = tk.Frame(top, bg=BG); btns.pack(fill="x", padx=16, pady=12)
        ttk.Button(btns, text="✓ OK", style="Accent.TButton", command=self._ok).pack(side="left")
        ttk.Button(btns, text="Abbrechen", command=top.destroy).pack(side="right")
        parent.wait_window(top)

    def _ok(self):
        self.result = self.txt.get("1.0", "end").strip()
        self.top.destroy()


def main():
    root = tk.Tk()
    DinoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
