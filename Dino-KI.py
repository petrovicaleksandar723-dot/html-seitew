#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DINO KI - EINE Datei. Gratis & lokal ueber Ollama, mit Gideon-Sprachausgabe.
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

import base64 as _b64
DINO_HTML = _b64.b64decode("PCFET0NUWVBFIGh0bWw+CjxodG1sIGxhbmc9ImRlIj4KPGhlYWQ+CjxtZXRhIGNoYXJzZXQ9IlVURi04Ij4KPG1ldGEgbmFtZT0idmlld3BvcnQiIGNvbnRlbnQ9IndpZHRoPWRldmljZS13aWR0aCwgaW5pdGlhbC1zY2FsZT0xLjAiPgo8dGl0bGU+8J+mliBEaW5vIEtJPC90aXRsZT4KPHN0eWxlPgovKiA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KICAgRElOTyBLSSDigJQgSmFydmlzL1NjaS1GaSBGcm9udGVuZCAoZWluZSBlaWdlbnN0w6RuZGlnZSBEYXRlaSkKICAgUmVpbmVzIEhUTUwvQ1NTL0pTLCBrZWluZSBleHRlcm5lbiBCaWJsaW90aGVrZW4uCiAgID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PSAqLwoKLyogLS0tLSBEZXNpZ24tVmFyaWFibGVuIC0tLS0gKi8KOnJvb3R7CiAgLS1iZzojMDQwNjBkOyAgICAgICAgICAgIC8qIGZhc3Qgc2Nod2FyeiAqLwogIC0tYmcyOiMwNjBhMTY7CiAgLS1wYW5lbDpyZ2JhKDE0LDIyLDQyLC42Mik7ICAgLyogR2xhc21vcnBoaXNtdXMtUGFuZWwgKi8KICAtLXBhbmVsLXNvbGlkOiMwYTExMjQ7CiAgLS1saW5lOnJnYmEoNTYsMTg5LDI0OCwuMjIpOyAgLyogbGV1Y2h0ZW5kZXIgZMO8bm5lciBSYW5kICovCiAgLS1jeWFuOiMyMmQzZWU7CiAgLS1ibHVlOiMzOGJkZjg7CiAgLS1ibHVlMjojNjBhNWZhOwogIC0tdHh0OiNlOGYxZmY7CiAgLS1tdXQ6IzdjOGRiNTsKICAtLWdyZWVuOiMzNGQzOTk7CiAgLS1yb3NlOiNmYjcxODU7CiAgLS1hbWJlcjojZmJiZjI0OwogIC0tZ2xvdzowIDAgMThweCByZ2JhKDM0LDIxMSwyMzgsLjU1KTsKfQoKKntib3gtc2l6aW5nOmJvcmRlci1ib3h9Cmh0bWwsYm9keXtoZWlnaHQ6MTAwJX0KYm9keXsKICBtYXJnaW46MDsKICBmb250LWZhbWlseToiU2Vnb2UgVUkiLHN5c3RlbS11aSwtYXBwbGUtc3lzdGVtLCJIZWx2ZXRpY2EgTmV1ZSIsQXJpYWwsc2Fucy1zZXJpZjsKICBjb2xvcjp2YXIoLS10eHQpOwogIGJhY2tncm91bmQ6CiAgICByYWRpYWwtZ3JhZGllbnQoMTIwMHB4IDYwMHB4IGF0IDUwJSAtMTAlLCByZ2JhKDM0LDIxMSwyMzgsLjEwKSwgdHJhbnNwYXJlbnQgNjAlKSwKICAgIHJhZGlhbC1ncmFkaWVudCg5MDBweCA1MDBweCBhdCA5MCUgMTEwJSwgcmdiYSg5NiwxNjUsMjUwLC4wOCksIHRyYW5zcGFyZW50IDYwJSksCiAgICB2YXIoLS1iZyk7CiAgb3ZlcmZsb3c6aGlkZGVuOwp9Ci8qIGRlemVudGVzIEdyaWQgaW0gSGludGVyZ3J1bmQgKi8KYm9keTo6YmVmb3JlewogIGNvbnRlbnQ6IiI7cG9zaXRpb246Zml4ZWQ7aW5zZXQ6MDt6LWluZGV4OjA7cG9pbnRlci1ldmVudHM6bm9uZTtvcGFjaXR5Oi4zNTsKICBiYWNrZ3JvdW5kLWltYWdlOgogICAgbGluZWFyLWdyYWRpZW50KHJnYmEoNTYsMTg5LDI0OCwuMDYpIDFweCx0cmFuc3BhcmVudCAxcHgpLAogICAgbGluZWFyLWdyYWRpZW50KDkwZGVnLHJnYmEoNTYsMTg5LDI0OCwuMDYpIDFweCx0cmFuc3BhcmVudCAxcHgpOwogIGJhY2tncm91bmQtc2l6ZTo0NHB4IDQ0cHg7CiAgbWFzay1pbWFnZTpyYWRpYWwtZ3JhZGllbnQoY2lyY2xlIGF0IDUwJSAzMCUsIzAwMCAwJSx0cmFuc3BhcmVudCA4MCUpOwp9CgouYXBwe3Bvc2l0aW9uOnJlbGF0aXZlO3otaW5kZXg6MTtkaXNwbGF5OmZsZXg7ZmxleC1kaXJlY3Rpb246Y29sdW1uO2hlaWdodDoxMDB2aDttYXgtd2lkdGg6MTE4MHB4O21hcmdpbjowIGF1dG87cGFkZGluZzoxNHB4IDE4cHggMTZweH0KCi8qID09PT09PT09PT09PT09PT09IEtvcGZ6ZWlsZSA9PT09PT09PT09PT09PT09PSAqLwouaGVhZGVye2Rpc3BsYXk6ZmxleDthbGlnbi1pdGVtczpjZW50ZXI7Z2FwOjE4cHg7cGFkZGluZzo2cHggNHB4IDEycHh9Ci5icmFuZHtkaXNwbGF5OmZsZXg7YWxpZ24taXRlbXM6Y2VudGVyO2dhcDoxNHB4O21pbi13aWR0aDowfQoud29yZG1hcmt7CiAgZm9udC1zaXplOjI2cHg7Zm9udC13ZWlnaHQ6ODAwO2xldHRlci1zcGFjaW5nOjVweDsKICBiYWNrZ3JvdW5kOmxpbmVhci1ncmFkaWVudCg5MGRlZywjNjdlOGY5LCMzOGJkZjgsIzgxOGNmOCk7CiAgLXdlYmtpdC1iYWNrZ3JvdW5kLWNsaXA6dGV4dDtiYWNrZ3JvdW5kLWNsaXA6dGV4dDtjb2xvcjp0cmFuc3BhcmVudDsKICB0ZXh0LXNoYWRvdzowIDAgMjRweCByZ2JhKDU2LDE4OSwyNDgsLjM1KTsKICBmaWx0ZXI6ZHJvcC1zaGFkb3coMCAwIDEwcHggcmdiYSgzNCwyMTEsMjM4LC40KSk7Cn0KLnRhZ2xpbmV7CiAgZm9udC1zaXplOjExcHg7bGV0dGVyLXNwYWNpbmc6MS41cHg7bWFyZ2luLXRvcDoxcHg7Zm9udC13ZWlnaHQ6NjAwOwogIGJhY2tncm91bmQ6bGluZWFyLWdyYWRpZW50KDkwZGVnLCM2N2U4ZjksIzYwYTVmYSk7CiAgLXdlYmtpdC1iYWNrZ3JvdW5kLWNsaXA6dGV4dDtiYWNrZ3JvdW5kLWNsaXA6dGV4dDtjb2xvcjp0cmFuc3BhcmVudDsKICB0ZXh0LXNoYWRvdzowIDAgMTJweCByZ2JhKDU2LDE4OSwyNDgsLjI1KTtvcGFjaXR5Oi45MjsKfQouc3RhdHVzbGluZXtkaXNwbGF5OmZsZXg7YWxpZ24taXRlbXM6Y2VudGVyO2dhcDo4cHg7Zm9udC1zaXplOjEyLjVweDtjb2xvcjp2YXIoLS1tdXQpO21hcmdpbi10b3A6M3B4O2ZsZXgtd3JhcDp3cmFwfQouZG90e3dpZHRoOjlweDtoZWlnaHQ6OXB4O2JvcmRlci1yYWRpdXM6NTAlO2JhY2tncm91bmQ6dmFyKC0tbXV0KTtib3gtc2hhZG93OjAgMCA4cHggY3VycmVudENvbG9yO3RyYW5zaXRpb246LjNzfQouZG90Lm9re2JhY2tncm91bmQ6dmFyKC0tZ3JlZW4pO2NvbG9yOnZhcigtLWdyZWVuKX0KLmRvdC5iYWR7YmFja2dyb3VuZDp2YXIoLS1yb3NlKTtjb2xvcjp2YXIoLS1yb3NlKX0KLyoga2xlaW5lciBPbGxhbWEtSW5kaWthdG9yIG9iZW4gKi8KLm9sbGFtYS1waWxse2Rpc3BsYXk6aW5saW5lLWZsZXg7YWxpZ24taXRlbXM6Y2VudGVyO2dhcDo2cHg7Zm9udC1zaXplOjExcHg7cGFkZGluZzoycHggOXB4O2JvcmRlci1yYWRpdXM6OTk5cHg7CiAgYm9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtiYWNrZ3JvdW5kOnZhcigtLXBhbmVsKTtiYWNrZHJvcC1maWx0ZXI6Ymx1cig4cHgpO2NvbG9yOnZhcigtLW11dCl9Ci5vbGxhbWEtcGlsbCAub3Bkb3R7d2lkdGg6N3B4O2hlaWdodDo3cHg7Ym9yZGVyLXJhZGl1czo1MCU7YmFja2dyb3VuZDp2YXIoLS1tdXQpO2JveC1zaGFkb3c6MCAwIDdweCBjdXJyZW50Q29sb3I7dHJhbnNpdGlvbjouM3N9Ci5vbGxhbWEtcGlsbC5va3tjb2xvcjojYmZmNGZmO2JvcmRlci1jb2xvcjpyZ2JhKDUyLDIxMSwxNTMsLjUpfQoub2xsYW1hLXBpbGwub2sgLm9wZG90e2JhY2tncm91bmQ6dmFyKC0tZ3JlZW4pO2NvbG9yOnZhcigtLWdyZWVuKX0KLm9sbGFtYS1waWxsLndhcm57Y29sb3I6I2ZmZTliODtib3JkZXItY29sb3I6cmdiYSgyNTEsMTkxLDM2LC41KX0KLm9sbGFtYS1waWxsLndhcm4gLm9wZG90e2JhY2tncm91bmQ6dmFyKC0tYW1iZXIpO2NvbG9yOnZhcigtLWFtYmVyKX0KLm9sbGFtYS1waWxsLmJhZHtjb2xvcjojZmZkOWRmO2JvcmRlci1jb2xvcjpyZ2JhKDI1MSwxMTMsMTMzLC41KX0KLm9sbGFtYS1waWxsLmJhZCAub3Bkb3R7YmFja2dyb3VuZDp2YXIoLS1yb3NlKTtjb2xvcjp2YXIoLS1yb3NlKX0KLmhlYWRlciAuc3BhY2Vye2ZsZXg6MX0KLmljb25idG5ze2Rpc3BsYXk6ZmxleDtnYXA6OHB4fQouaWNvbmJ0bnsKICB3aWR0aDo0MnB4O2hlaWdodDo0MnB4O2JvcmRlci1yYWRpdXM6MTJweDtib3JkZXI6MXB4IHNvbGlkIHZhcigtLWxpbmUpOwogIGJhY2tncm91bmQ6dmFyKC0tcGFuZWwpO2JhY2tkcm9wLWZpbHRlcjpibHVyKDhweCk7CiAgY29sb3I6dmFyKC0tdHh0KTtmb250LXNpemU6MThweDtjdXJzb3I6cG9pbnRlcjtkaXNwbGF5OmdyaWQ7cGxhY2UtaXRlbXM6Y2VudGVyOwogIHRyYW5zaXRpb246LjE4czsKfQouaWNvbmJ0bjpob3Zlcntib3JkZXItY29sb3I6dmFyKC0tY3lhbik7Ym94LXNoYWRvdzp2YXIoLS1nbG93KTt0cmFuc2Zvcm06dHJhbnNsYXRlWSgtMXB4KX0KCi8qID09PT09PT09PT09PT09PT09IENvcmUgLyBPcmIgPT09PT09PT09PT09PT09PT0gKi8KLmNvcmUtd3JhcHtkaXNwbGF5OmZsZXg7anVzdGlmeS1jb250ZW50OmNlbnRlcjthbGlnbi1pdGVtczpjZW50ZXI7aGVpZ2h0OjExOHB4O21hcmdpbjotNHB4IDAgNnB4O3Bvc2l0aW9uOnJlbGF0aXZlfQouY29yZXtwb3NpdGlvbjpyZWxhdGl2ZTt3aWR0aDo5NnB4O2hlaWdodDo5NnB4O2Rpc3BsYXk6Z3JpZDtwbGFjZS1pdGVtczpjZW50ZXJ9Ci5jb3JlIC5yaW5newogIHBvc2l0aW9uOmFic29sdXRlO2JvcmRlci1yYWRpdXM6NTAlO2JvcmRlcjoycHggc29saWQgcmdiYSg1NiwxODksMjQ4LC4zNSk7CiAgYW5pbWF0aW9uOnNwaW4gNnMgbGluZWFyIGluZmluaXRlOwp9Ci5jb3JlIC5yMXtpbnNldDowO2JvcmRlci10b3AtY29sb3I6dmFyKC0tY3lhbik7Ym9yZGVyLXJpZ2h0LWNvbG9yOnRyYW5zcGFyZW50fQouY29yZSAucjJ7aW5zZXQ6MTJweDtib3JkZXItYm90dG9tLWNvbG9yOnZhcigtLWJsdWUyKTtib3JkZXItbGVmdC1jb2xvcjp0cmFuc3BhcmVudDthbmltYXRpb24tZHVyYXRpb246NHM7YW5pbWF0aW9uLWRpcmVjdGlvbjpyZXZlcnNlfQouY29yZSAucjN7aW5zZXQ6MjRweDtib3JkZXItdG9wLWNvbG9yOnZhcigtLWJsdWUpO2JvcmRlci1sZWZ0LWNvbG9yOnRyYW5zcGFyZW50O2FuaW1hdGlvbi1kdXJhdGlvbjo4c30KLmNvcmUgLm51Y2xldXN7CiAgd2lkdGg6MzhweDtoZWlnaHQ6MzhweDtib3JkZXItcmFkaXVzOjUwJTsKICBiYWNrZ3JvdW5kOnJhZGlhbC1ncmFkaWVudChjaXJjbGUgYXQgMzUlIDMwJSwjYmZmNGZmLCMyMmQzZWUgNDUlLCMxZDRlZDggMTAwJSk7CiAgYm94LXNoYWRvdzowIDAgMjZweCA2cHggcmdiYSgzNCwyMTEsMjM4LC42NSksMCAwIDYwcHggMTJweCByZ2JhKDU2LDE4OSwyNDgsLjI1KTsKICBhbmltYXRpb246cHVsc2UgMi42cyBlYXNlLWluLW91dCBpbmZpbml0ZTsKfQpAa2V5ZnJhbWVzIHNwaW57dG97dHJhbnNmb3JtOnJvdGF0ZSgzNjBkZWcpfX0KQGtleWZyYW1lcyBwdWxzZXswJSwxMDAle3RyYW5zZm9ybTpzY2FsZSgxKTtvcGFjaXR5Oi45Mn01MCV7dHJhbnNmb3JtOnNjYWxlKDEuMTYpO29wYWNpdHk6MX19Ci8qIFp1c3TDpG5kZTogbmFjaGRlbmtlbiAoc2NobmVsbGVyKSAvIHNwcmVjaGVuICovCi5jb3JlLnRoaW5raW5nIC5yaW5ne2FuaW1hdGlvbi1kdXJhdGlvbjoxLjRzIWltcG9ydGFudH0KLmNvcmUudGhpbmtpbmcgLnIye2FuaW1hdGlvbi1kdXJhdGlvbjoxcyFpbXBvcnRhbnR9Ci5jb3JlLnRoaW5raW5nIC5udWNsZXVze2FuaW1hdGlvbi1kdXJhdGlvbjouOHN9Ci5jb3JlLnNwZWFraW5nIC5udWNsZXVze2FuaW1hdGlvbjpzcGVhayAuNXMgZWFzZS1pbi1vdXQgaW5maW5pdGV9CkBrZXlmcmFtZXMgc3BlYWt7MCUsMTAwJXt0cmFuc2Zvcm06c2NhbGUoMSl9NTAle3RyYW5zZm9ybTpzY2FsZSgxLjI4KTtib3gtc2hhZG93OjAgMCAzNHB4IDEwcHggcmdiYSgzNCwyMTEsMjM4LC44NSl9fQoKLyogPT09PT09PT09PT09PT09PT0gQ2hhdCA9PT09PT09PT09PT09PT09PSAqLwouY2hhdHsKICBmbGV4OjE7b3ZlcmZsb3cteTphdXRvO3BhZGRpbmc6MTBweCA2cHggNHB4O2Rpc3BsYXk6ZmxleDtmbGV4LWRpcmVjdGlvbjpjb2x1bW47Z2FwOjE0cHg7CiAgc2Nyb2xsYmFyLXdpZHRoOnRoaW47c2Nyb2xsYmFyLWNvbG9yOnJnYmEoNTYsMTg5LDI0OCwuNCkgdHJhbnNwYXJlbnQ7Cn0KLmNoYXQ6Oi13ZWJraXQtc2Nyb2xsYmFye3dpZHRoOjhweH0KLmNoYXQ6Oi13ZWJraXQtc2Nyb2xsYmFyLXRodW1ie2JhY2tncm91bmQ6cmdiYSg1NiwxODksMjQ4LC4zNSk7Ym9yZGVyLXJhZGl1czo4cHh9CgoubXNne2Rpc3BsYXk6ZmxleDtnYXA6MTBweDttYXgtd2lkdGg6ODIlO2FuaW1hdGlvbjpmYWRlaW4gLjM1cyBlYXNlIGJvdGh9CkBrZXlmcmFtZXMgZmFkZWlue2Zyb217b3BhY2l0eTowO3RyYW5zZm9ybTp0cmFuc2xhdGVZKDEwcHgpfXRve29wYWNpdHk6MTt0cmFuc2Zvcm06bm9uZX19Ci5tc2cudXNlcnthbGlnbi1zZWxmOmZsZXgtZW5kO2ZsZXgtZGlyZWN0aW9uOnJvdy1yZXZlcnNlfQouYXZhdGFye2ZsZXg6bm9uZTt3aWR0aDozMHB4O2hlaWdodDozMHB4O2JvcmRlci1yYWRpdXM6OXB4O2Rpc3BsYXk6Z3JpZDtwbGFjZS1pdGVtczpjZW50ZXI7Zm9udC1zaXplOjE1cHg7CiAgYmFja2dyb3VuZDp2YXIoLS1wYW5lbCk7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKX0KLmJ1YmJsZXsKICBwYWRkaW5nOjExcHggMTRweDtib3JkZXItcmFkaXVzOjE0cHg7Zm9udC1zaXplOjE0LjVweDtsaW5lLWhlaWdodDoxLjU7CiAgd2hpdGUtc3BhY2U6cHJlLXdyYXA7d29yZC1icmVhazpicmVhay13b3JkOwp9Ci8qIERpbm86IEdsYXMtQnViYmxlICovCi5tc2cuZGlubyAuYnViYmxlewogIGJhY2tncm91bmQ6dmFyKC0tcGFuZWwpO2JhY2tkcm9wLWZpbHRlcjpibHVyKDEwcHgpOwogIGJvcmRlcjoxcHggc29saWQgdmFyKC0tbGluZSk7Ym9yZGVyLXRvcC1sZWZ0LXJhZGl1czo0cHg7CiAgYm94LXNoYWRvdzowIDRweCAyMnB4IHJnYmEoMCwwLDAsLjM1KTsKfQovKiBOdXR6ZXI6IEFremVudC1CdWJibGUgKi8KLm1zZy51c2VyIC5idWJibGV7CiAgYmFja2dyb3VuZDpsaW5lYXItZ3JhZGllbnQoMTM1ZGVnLHJnYmEoMzQsMjExLDIzOCwuMjIpLHJnYmEoOTYsMTY1LDI1MCwuMjApKTsKICBib3JkZXI6MXB4IHNvbGlkIHJnYmEoMzQsMjExLDIzOCwuNDUpO2JvcmRlci10b3AtcmlnaHQtcmFkaXVzOjRweDsKICBib3gtc2hhZG93OjAgMCAxOHB4IHJnYmEoMzQsMjExLDIzOCwuMTgpOwp9Ci8qIEluZm8gLyBGZWhsZXIgLyBMYWJlbCAvIFN5bnRoZXNlICovCi5tc2cuaW5mbyAuYnViYmxle2JhY2tncm91bmQ6dHJhbnNwYXJlbnQ7Ym9yZGVyOjFweCBkYXNoZWQgcmdiYSgxMjQsMTQxLDE4MSwuNCk7Y29sb3I6dmFyKC0tbXV0KTtmb250LXN0eWxlOml0YWxpYztmb250LXNpemU6MTNweH0KLm1zZy5lcnJvciAuYnViYmxle2JhY2tncm91bmQ6cmdiYSgyNTEsMTEzLDEzMywuMTIpO2JvcmRlcjoxcHggc29saWQgdmFyKC0tcm9zZSk7Y29sb3I6I2ZmZDlkZn0KLm1zZy5lcnJvciAuYXZhdGFye2JvcmRlci1jb2xvcjp2YXIoLS1yb3NlKX0KLmxhYmVse2ZvbnQtc2l6ZToxMXB4O2xldHRlci1zcGFjaW5nOi41cHg7dGV4dC10cmFuc2Zvcm06dXBwZXJjYXNlO2NvbG9yOnZhcigtLWN5YW4pO21hcmdpbi1ib3R0b206M3B4O2ZvbnQtd2VpZ2h0OjcwMDtvcGFjaXR5Oi45fQoubXNnLnN5bnRoIC5idWJibGV7CiAgYmFja2dyb3VuZDpsaW5lYXItZ3JhZGllbnQoMTM1ZGVnLHJnYmEoMzQsMjExLDIzOCwuMTYpLHJnYmEoMTI5LDE0MCwyNDgsLjE0KSk7CiAgYm9yZGVyOjFweCBzb2xpZCB2YXIoLS1jeWFuKTtib3gtc2hhZG93OnZhcigtLWdsb3cpOwp9CgovKiBUaXBwLUluZGlrYXRvciAqLwoudHlwaW5ne2Rpc3BsYXk6ZmxleDtnYXA6NXB4O2FsaWduLWl0ZW1zOmNlbnRlcjtwYWRkaW5nOjEzcHggMTZweH0KLnR5cGluZyBzcGFue3dpZHRoOjhweDtoZWlnaHQ6OHB4O2JvcmRlci1yYWRpdXM6NTAlO2JhY2tncm91bmQ6dmFyKC0tY3lhbik7b3BhY2l0eTouNTthbmltYXRpb246Ym91bmNlIDEuMnMgaW5maW5pdGV9Ci50eXBpbmcgc3BhbjpudGgtY2hpbGQoMil7YW5pbWF0aW9uLWRlbGF5Oi4xOHN9Ci50eXBpbmcgc3BhbjpudGgtY2hpbGQoMyl7YW5pbWF0aW9uLWRlbGF5Oi4zNnN9CkBrZXlmcmFtZXMgYm91bmNlezAlLDYwJSwxMDAle3RyYW5zZm9ybTp0cmFuc2xhdGVZKDApO29wYWNpdHk6LjR9MzAle3RyYW5zZm9ybTp0cmFuc2xhdGVZKC02cHgpO29wYWNpdHk6MX19CgovKiA9PT09PT09PT09PT09PT09PSBEaW5vLVNldHVwLUthcnRlID09PT09PT09PT09PT09PT09ICovCi5zZXR1cC1jYXJkewogIGFsaWduLXNlbGY6c3RyZXRjaDttYXgtd2lkdGg6MTAwJTsKICBib3JkZXI6MXB4IHNvbGlkIHZhcigtLWN5YW4pO2JvcmRlci1yYWRpdXM6MTZweDtwYWRkaW5nOjE4cHggMjBweDsKICBiYWNrZ3JvdW5kOmxpbmVhci1ncmFkaWVudCgxNTBkZWcscmdiYSgzNCwyMTEsMjM4LC4xMCkscmdiYSgxMjksMTQwLDI0OCwuMDgpKTsKICBiYWNrZHJvcC1maWx0ZXI6Ymx1cigxMnB4KTtib3gtc2hhZG93OjAgMCAzMHB4IHJnYmEoMzQsMjExLDIzOCwuMTgpLDAgNnB4IDI4cHggcmdiYSgwLDAsMCwuNCk7CiAgYW5pbWF0aW9uOmZhZGVpbiAuNHMgZWFzZSBib3RoOwp9Ci5zZXR1cC1jYXJkIC5zYy10aXRsZXtmb250LXNpemU6MTdweDtmb250LXdlaWdodDo4MDA7bGV0dGVyLXNwYWNpbmc6LjRweDsKICBiYWNrZ3JvdW5kOmxpbmVhci1ncmFkaWVudCg5MGRlZywjYmZmNGZmLCM2MGE1ZmEpOy13ZWJraXQtYmFja2dyb3VuZC1jbGlwOnRleHQ7YmFja2dyb3VuZC1jbGlwOnRleHQ7Y29sb3I6dHJhbnNwYXJlbnQ7CiAgdGV4dC1zaGFkb3c6MCAwIDE4cHggcmdiYSg1NiwxODksMjQ4LC4zKTttYXJnaW4tYm90dG9tOjZweH0KLnNldHVwLWNhcmQgLnNjLXN1Yntmb250LXNpemU6MTNweDtjb2xvcjp2YXIoLS1tdXQpO2xpbmUtaGVpZ2h0OjEuNjttYXJnaW4tYm90dG9tOjE0cHh9Ci5zZXR1cC1jYXJkIC5zYy1zdGVwe21hcmdpbjoxMnB4IDB9Ci5zZXR1cC1jYXJkIC5zYy1zdGVwLWh7Zm9udC1zaXplOjEzLjVweDtmb250LXdlaWdodDo3MDA7Y29sb3I6dmFyKC0tdHh0KTttYXJnaW4tYm90dG9tOjZweDtkaXNwbGF5OmZsZXg7YWxpZ24taXRlbXM6Y2VudGVyO2dhcDo3cHh9Ci5zZXR1cC1jYXJkIC5zYy1zdGVwLWggLm51bXtmbGV4Om5vbmU7d2lkdGg6MjJweDtoZWlnaHQ6MjJweDtib3JkZXItcmFkaXVzOjUwJTtkaXNwbGF5OmdyaWQ7cGxhY2UtaXRlbXM6Y2VudGVyOwogIGZvbnQtc2l6ZToxMnB4O2JhY2tncm91bmQ6cmdiYSgzNCwyMTEsMjM4LC4xNik7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtjb2xvcjp2YXIoLS1jeWFuKX0KLnNldHVwLWNhcmQgYS5zYy1saW5re2NvbG9yOnZhcigtLWJsdWUyKTt0ZXh0LWRlY29yYXRpb246bm9uZTtib3JkZXItYm90dG9tOjFweCBkb3R0ZWQgcmdiYSg5NiwxNjUsMjUwLC41KX0KLnNldHVwLWNhcmQgYS5zYy1saW5rOmhvdmVye2NvbG9yOiNiZmY0ZmY7Ym9yZGVyLWJvdHRvbS1jb2xvcjp2YXIoLS1jeWFuKX0KLnNldHVwLWNhcmQgLnNjLWNvZGVib3h7ZGlzcGxheTpmbGV4O2FsaWduLWl0ZW1zOmNlbnRlcjtnYXA6OHB4O21hcmdpbi10b3A6NnB4fQouc2V0dXAtY2FyZCAuc2MtY29kZXsKICBmbGV4OjE7Zm9udC1mYW1pbHk6IkNvbnNvbGFzIiwiU0YgTW9ubyIsdWktbW9ub3NwYWNlLG1vbm9zcGFjZTtmb250LXNpemU6MTMuNXB4O2NvbG9yOiNiZmY0ZmY7CiAgYmFja2dyb3VuZDpyZ2JhKDIsOCwyMCwuNyk7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtib3JkZXItcmFkaXVzOjEwcHg7cGFkZGluZzo5cHggMTJweDsKICB3aGl0ZS1zcGFjZTpub3dyYXA7b3ZlcmZsb3cteDphdXRvO2JveC1zaGFkb3c6aW5zZXQgMCAwIDE0cHggcmdiYSgzNCwyMTEsMjM4LC4wOCk7Cn0KLnNldHVwLWNhcmQgLnNjLWNvcHl7ZmxleDpub25lO3BhZGRpbmc6OXB4IDExcHg7Ym9yZGVyLXJhZGl1czoxMHB4O2JvcmRlcjoxcHggc29saWQgdmFyKC0tbGluZSk7CiAgYmFja2dyb3VuZDp2YXIoLS1wYW5lbCk7Y29sb3I6dmFyKC0tdHh0KTtmb250OmluaGVyaXQ7Zm9udC1zaXplOjEzcHg7Y3Vyc29yOnBvaW50ZXI7dHJhbnNpdGlvbjouMTZzfQouc2V0dXAtY2FyZCAuc2MtY29weTpob3Zlcntib3JkZXItY29sb3I6dmFyKC0tY3lhbik7Ym94LXNoYWRvdzp2YXIoLS1nbG93KX0KLnNldHVwLWNhcmQgLnNjLW1vZGVsc3tkaXNwbGF5OmZsZXg7ZmxleC13cmFwOndyYXA7Z2FwOjhweDttYXJnaW4tdG9wOjhweH0KLnNldHVwLWNhcmQgLnNjLW1vZGVse3BhZGRpbmc6NnB4IDEycHg7Ym9yZGVyLXJhZGl1czo5OTlweDtib3JkZXI6MXB4IHNvbGlkIHZhcigtLWxpbmUpOwogIGJhY2tncm91bmQ6dmFyKC0tcGFuZWwpO2NvbG9yOnZhcigtLXR4dCk7Zm9udDppbmhlcml0O2ZvbnQtc2l6ZToxMi41cHg7Y3Vyc29yOnBvaW50ZXI7dHJhbnNpdGlvbjouMTZzfQouc2V0dXAtY2FyZCAuc2MtbW9kZWw6aG92ZXJ7Ym9yZGVyLWNvbG9yOnZhcigtLWN5YW4pO2JveC1zaGFkb3c6dmFyKC0tZ2xvdyk7Y29sb3I6I2JmZjRmZn0KLnNldHVwLWNhcmQgLnNjLWFjdGlvbnN7ZGlzcGxheTpmbGV4O2FsaWduLWl0ZW1zOmNlbnRlcjtnYXA6MTBweDtmbGV4LXdyYXA6d3JhcDttYXJnaW4tdG9wOjE2cHh9Ci5zZXR1cC1jYXJkIC5zYy1yZWNoZWNre3BhZGRpbmc6OXB4IDE2cHg7Ym9yZGVyLXJhZGl1czoxMHB4O2JvcmRlcjpub25lO2N1cnNvcjpwb2ludGVyO2ZvbnQ6aW5oZXJpdDtmb250LXNpemU6MTMuNXB4O2ZvbnQtd2VpZ2h0OjYwMDsKICBiYWNrZ3JvdW5kOmxpbmVhci1ncmFkaWVudCgxMzVkZWcsdmFyKC0tY3lhbiksdmFyKC0tYmx1ZTIpKTtjb2xvcjojMDQxMDFmO2JveC1zaGFkb3c6MCAwIDE4cHggcmdiYSgzNCwyMTEsMjM4LC40KTt0cmFuc2l0aW9uOi4xNnN9Ci5zZXR1cC1jYXJkIC5zYy1yZWNoZWNrOmhvdmVye2ZpbHRlcjpicmlnaHRuZXNzKDEuMSl9Ci5zZXR1cC1jYXJkIC5zYy1yZWNoZWNrOmRpc2FibGVke29wYWNpdHk6LjU1O2N1cnNvcjp3YWl0O2JveC1zaGFkb3c6bm9uZX0KLnNldHVwLWNhcmQgLnNjLXNldHRpbmdze2ZvbnQtc2l6ZToxMi41cHg7Y29sb3I6dmFyKC0tbXV0KTtiYWNrZ3JvdW5kOm5vbmU7Ym9yZGVyOm5vbmU7Y3Vyc29yOnBvaW50ZXI7Zm9udDppbmhlcml0OwogIHRleHQtZGVjb3JhdGlvbjp1bmRlcmxpbmU7dGV4dC1kZWNvcmF0aW9uLXN0eWxlOmRvdHRlZDtwYWRkaW5nOjB9Ci5zZXR1cC1jYXJkIC5zYy1zZXR0aW5nczpob3Zlcntjb2xvcjp2YXIoLS1ibHVlMil9Ci5zZXR1cC1jYXJkIC5zYy1zdGF0ZXtmb250LXNpemU6MTIuNXB4O2NvbG9yOnZhcigtLWN5YW4pO21pbi1oZWlnaHQ6MWVtfQoKLyogPT09PT09PT09PT09PT09PT0gUXVpY2stQ2hpcHMgPT09PT09PT09PT09PT09PT0gKi8KLmNoaXBze2Rpc3BsYXk6ZmxleDtmbGV4LXdyYXA6d3JhcDtnYXA6OHB4O3BhZGRpbmc6MTBweCA0cHggOHB4fQouY2hpcHsKICBwYWRkaW5nOjdweCAxM3B4O2JvcmRlci1yYWRpdXM6OTk5cHg7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTsKICBiYWNrZ3JvdW5kOnZhcigtLXBhbmVsKTtjb2xvcjp2YXIoLS10eHQpO2ZvbnQtc2l6ZToxM3B4O2N1cnNvcjpwb2ludGVyO3RyYW5zaXRpb246LjE2czsKICBiYWNrZHJvcC1maWx0ZXI6Ymx1cig4cHgpOwp9Ci5jaGlwOmhvdmVye2JvcmRlci1jb2xvcjp2YXIoLS1jeWFuKTtib3gtc2hhZG93OnZhcigtLWdsb3cpO2NvbG9yOiNiZmY0ZmZ9Ci5jaGlwOmRpc2FibGVke29wYWNpdHk6LjQ7Y3Vyc29yOm5vdC1hbGxvd2VkO2JveC1zaGFkb3c6bm9uZX0KCi8qID09PT09PT09PT09PT09PT09IEVpbmdhYmVsZWlzdGUgPT09PT09PT09PT09PT09PT0gKi8KLmlucHV0YmFyewogIGRpc3BsYXk6ZmxleDthbGlnbi1pdGVtczpmbGV4LWVuZDtnYXA6OXB4O3BhZGRpbmc6MTBweDtib3JkZXItcmFkaXVzOjE2cHg7CiAgYm9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtiYWNrZ3JvdW5kOnZhcigtLXBhbmVsKTtiYWNrZHJvcC1maWx0ZXI6Ymx1cigxMnB4KTsKICBib3gtc2hhZG93OjAgMCAyNnB4IHJnYmEoMzQsMjExLDIzOCwuMTApOwp9CiNpbnB1dHsKICBmbGV4OjE7cmVzaXplOm5vbmU7bWF4LWhlaWdodDoxNDBweDttaW4taGVpZ2h0OjI0cHg7Ym9yZGVyOm5vbmU7b3V0bGluZTpub25lOwogIGJhY2tncm91bmQ6dHJhbnNwYXJlbnQ7Y29sb3I6dmFyKC0tdHh0KTtmb250OmluaGVyaXQ7Zm9udC1zaXplOjE0LjVweDtsaW5lLWhlaWdodDoxLjQ1OwogIHBhZGRpbmc6NnB4IDRweDsKfQojaW5wdXQ6OnBsYWNlaG9sZGVye2NvbG9yOnZhcigtLW11dCl9Ci5pYnRuewogIGZsZXg6bm9uZTt3aWR0aDo0MnB4O2hlaWdodDo0MnB4O2JvcmRlci1yYWRpdXM6MTFweDtib3JkZXI6MXB4IHNvbGlkIHZhcigtLWxpbmUpOwogIGJhY2tncm91bmQ6cmdiYSgyNTUsMjU1LDI1NSwuMDMpO2NvbG9yOnZhcigtLXR4dCk7Zm9udC1zaXplOjE4cHg7Y3Vyc29yOnBvaW50ZXI7CiAgZGlzcGxheTpncmlkO3BsYWNlLWl0ZW1zOmNlbnRlcjt0cmFuc2l0aW9uOi4xNnM7Cn0KLmlidG46aG92ZXJ7Ym9yZGVyLWNvbG9yOnZhcigtLWN5YW4pO2JveC1zaGFkb3c6dmFyKC0tZ2xvdyl9Ci5pYnRuLmFjdGl2ZXtib3JkZXItY29sb3I6dmFyKC0tY3lhbik7Y29sb3I6dmFyKC0tY3lhbik7YmFja2dyb3VuZDpyZ2JhKDM0LDIxMSwyMzgsLjEyKTtib3gtc2hhZG93OnZhcigtLWdsb3cpfQouaWJ0bi5taWMubGlzdGVuaW5ne2NvbG9yOnZhcigtLXJvc2UpO2JvcmRlci1jb2xvcjp2YXIoLS1yb3NlKTtib3gtc2hhZG93OjAgMCAxNnB4IHJnYmEoMjUxLDExMywxMzMsLjYpO2FuaW1hdGlvbjptaWNwdWxzZSAxcyBpbmZpbml0ZX0KQGtleWZyYW1lcyBtaWNwdWxzZXs1MCV7YmFja2dyb3VuZDpyZ2JhKDI1MSwxMTMsMTMzLC4xOCl9fQouaWJ0bi5zZW5kewogIGJhY2tncm91bmQ6bGluZWFyLWdyYWRpZW50KDEzNWRlZyx2YXIoLS1jeWFuKSx2YXIoLS1ibHVlMikpO2NvbG9yOiMwNDEwMWY7Ym9yZGVyOm5vbmU7CiAgYm94LXNoYWRvdzowIDAgMThweCByZ2JhKDM0LDIxMSwyMzgsLjUpOwp9Ci5pYnRuLnNlbmQ6aG92ZXJ7ZmlsdGVyOmJyaWdodG5lc3MoMS4xKX0KLmlidG46ZGlzYWJsZWR7b3BhY2l0eTouNDtjdXJzb3I6bm90LWFsbG93ZWQ7Ym94LXNoYWRvdzpub25lfQoKLyogPT09PT09PT09PT09PT09PT0gUGFuZWxzIChTbGlkZS1PdmVyKSA9PT09PT09PT09PT09PT09PSAqLwoub3ZlcmxheXtwb3NpdGlvbjpmaXhlZDtpbnNldDowO3otaW5kZXg6NDA7YmFja2dyb3VuZDpyZ2JhKDIsNCwxMCwuNik7YmFja2Ryb3AtZmlsdGVyOmJsdXIoM3B4KTsKICBvcGFjaXR5OjA7cG9pbnRlci1ldmVudHM6bm9uZTt0cmFuc2l0aW9uOi4yNXN9Ci5vdmVybGF5Lm9wZW57b3BhY2l0eToxO3BvaW50ZXItZXZlbnRzOmF1dG99Ci5wYW5lbHsKICBwb3NpdGlvbjpmaXhlZDt0b3A6MDtyaWdodDowO2hlaWdodDoxMDAlO3dpZHRoOm1pbig0NjBweCw5NHZ3KTt6LWluZGV4OjQxOwogIGJhY2tncm91bmQ6bGluZWFyLWdyYWRpZW50KDE4MGRlZyx2YXIoLS1iZzIpLHZhcigtLWJnKSk7CiAgYm9yZGVyLWxlZnQ6MXB4IHNvbGlkIHZhcigtLWxpbmUpO2JveC1zaGFkb3c6LTIwcHggMCA2MHB4IHJnYmEoMCwwLDAsLjU1KTsKICB0cmFuc2Zvcm06dHJhbnNsYXRlWCgxMDAlKTt0cmFuc2l0aW9uOnRyYW5zZm9ybSAuMjhzIGN1YmljLWJlemllciguNCwuMCwuMiwxKTsKICBkaXNwbGF5OmZsZXg7ZmxleC1kaXJlY3Rpb246Y29sdW1uOwp9Ci5wYW5lbC5vcGVue3RyYW5zZm9ybTpub25lfQoucGFuZWwtaGVhZHtkaXNwbGF5OmZsZXg7YWxpZ24taXRlbXM6Y2VudGVyO2dhcDoxMHB4O3BhZGRpbmc6MThweCAyMHB4IDEycHg7Ym9yZGVyLWJvdHRvbToxcHggc29saWQgdmFyKC0tbGluZSl9Ci5wYW5lbC1oZWFkIGgye21hcmdpbjowO2ZvbnQtc2l6ZToxN3B4O2ZvbnQtd2VpZ2h0OjcwMDtsZXR0ZXItc3BhY2luZzouNXB4fQoucGFuZWwtaGVhZCAuY2xvc2V7bWFyZ2luLWxlZnQ6YXV0bzt3aWR0aDozNHB4O2hlaWdodDozNHB4O2JvcmRlci1yYWRpdXM6OXB4O2JvcmRlcjoxcHggc29saWQgdmFyKC0tbGluZSk7CiAgYmFja2dyb3VuZDp0cmFuc3BhcmVudDtjb2xvcjp2YXIoLS10eHQpO2ZvbnQtc2l6ZToxOHB4O2N1cnNvcjpwb2ludGVyfQoucGFuZWwtaGVhZCAuY2xvc2U6aG92ZXJ7Ym9yZGVyLWNvbG9yOnZhcigtLXJvc2UpO2NvbG9yOnZhcigtLXJvc2UpfQoucGFuZWwtYm9keXtmbGV4OjE7b3ZlcmZsb3cteTphdXRvO3BhZGRpbmc6MTZweCAyMHB4IDI4cHg7c2Nyb2xsYmFyLXdpZHRoOnRoaW47c2Nyb2xsYmFyLWNvbG9yOnJnYmEoNTYsMTg5LDI0OCwuNCkgdHJhbnNwYXJlbnR9Ci5wYW5lbC1ib2R5Ojotd2Via2l0LXNjcm9sbGJhcnt3aWR0aDo4cHh9Ci5wYW5lbC1ib2R5Ojotd2Via2l0LXNjcm9sbGJhci10aHVtYntiYWNrZ3JvdW5kOnJnYmEoNTYsMTg5LDI0OCwuMzUpO2JvcmRlci1yYWRpdXM6OHB4fQoKLnNlY3R7Y29sb3I6dmFyKC0tY3lhbik7Zm9udC1zaXplOjEycHg7bGV0dGVyLXNwYWNpbmc6LjZweDt0ZXh0LXRyYW5zZm9ybTp1cHBlcmNhc2U7Zm9udC13ZWlnaHQ6NzAwO21hcmdpbjoxOHB4IDAgOHB4fQouc2VjdDpmaXJzdC1jaGlsZHttYXJnaW4tdG9wOjB9Ci5maWVsZHttYXJnaW4tYm90dG9tOjExcHh9Ci5maWVsZCBsYWJlbHtkaXNwbGF5OmJsb2NrO2ZvbnQtc2l6ZToxMnB4O2NvbG9yOnZhcigtLW11dCk7bWFyZ2luLWJvdHRvbTo0cHh9Ci5maWVsZCBpbnB1dCwuZmllbGQgc2VsZWN0LC5maWVsZCB0ZXh0YXJlYXsKICB3aWR0aDoxMDAlO3BhZGRpbmc6OXB4IDExcHg7Ym9yZGVyLXJhZGl1czo5cHg7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTsKICBiYWNrZ3JvdW5kOnJnYmEoMjU1LDI1NSwyNTUsLjAzKTtjb2xvcjp2YXIoLS10eHQpO2ZvbnQ6aW5oZXJpdDtmb250LXNpemU6MTMuNXB4O291dGxpbmU6bm9uZTsKfQouZmllbGQgaW5wdXQ6Zm9jdXMsLmZpZWxkIHNlbGVjdDpmb2N1cywuZmllbGQgdGV4dGFyZWE6Zm9jdXN7Ym9yZGVyLWNvbG9yOnZhcigtLWN5YW4pO2JveC1zaGFkb3c6MCAwIDAgMnB4IHJnYmEoMzQsMjExLDIzOCwuMTgpfQouZmllbGQgc2VsZWN0IG9wdGlvbntiYWNrZ3JvdW5kOnZhcigtLXBhbmVsLXNvbGlkKX0KLmZpZWxkIHRleHRhcmVhe3Jlc2l6ZTp2ZXJ0aWNhbDttaW4taGVpZ2h0OjU0cHh9Ci5oaW50e2ZvbnQtc2l6ZToxMS41cHg7Y29sb3I6dmFyKC0tbXV0KTtsaW5lLWhlaWdodDoxLjY7bWFyZ2luLXRvcDo2cHh9Ci5oaW50IGNvZGV7Y29sb3I6dmFyKC0tYmx1ZTIpO2JhY2tncm91bmQ6cmdiYSg1NiwxODksMjQ4LC4wOCk7cGFkZGluZzoxcHggNXB4O2JvcmRlci1yYWRpdXM6NXB4fQoKLmJ0bnsKICBwYWRkaW5nOjEwcHggMTZweDtib3JkZXItcmFkaXVzOjEwcHg7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTsKICBiYWNrZ3JvdW5kOnZhcigtLXBhbmVsKTtjb2xvcjp2YXIoLS10eHQpO2ZvbnQ6aW5oZXJpdDtmb250LXNpemU6MTMuNXB4O2ZvbnQtd2VpZ2h0OjYwMDtjdXJzb3I6cG9pbnRlcjt0cmFuc2l0aW9uOi4xNnM7Cn0KLmJ0bjpob3Zlcntib3JkZXItY29sb3I6dmFyKC0tY3lhbik7Ym94LXNoYWRvdzp2YXIoLS1nbG93KX0KLmJ0bi5wcmltYXJ5e2JhY2tncm91bmQ6bGluZWFyLWdyYWRpZW50KDEzNWRlZyx2YXIoLS1jeWFuKSx2YXIoLS1ibHVlMikpO2NvbG9yOiMwNDEwMWY7Ym9yZGVyOm5vbmU7Ym94LXNoYWRvdzowIDAgMThweCByZ2JhKDM0LDIxMSwyMzgsLjQpfQouYnRuLmRhbmdlcntib3JkZXItY29sb3I6cmdiYSgyNTEsMTEzLDEzMywuNSk7Y29sb3I6I2ZmZDlkZn0KLmJ0bi5kYW5nZXI6aG92ZXJ7Ym9yZGVyLWNvbG9yOnZhcigtLXJvc2UpO2JveC1zaGFkb3c6MCAwIDE0cHggcmdiYSgyNTEsMTEzLDEzMywuNCl9Ci5idG4uc217cGFkZGluZzo2cHggMTFweDtmb250LXNpemU6MTJweH0KLmJ0bnJvd3tkaXNwbGF5OmZsZXg7Z2FwOjlweDtmbGV4LXdyYXA6d3JhcDttYXJnaW4tdG9wOjE0cHh9CgovKiBVbXNhdHotQmFubmVyIChLdW5kZW4pICovCi5yZXZlbnVlewogIGJvcmRlcjoxcHggc29saWQgdmFyKC0tbGluZSk7Ym9yZGVyLXJhZGl1czoxM3B4O3BhZGRpbmc6MTRweCAxNnB4O21hcmdpbi1ib3R0b206MTRweDsKICBiYWNrZ3JvdW5kOmxpbmVhci1ncmFkaWVudCgxMzVkZWcscmdiYSg1MiwyMTEsMTUzLC4xMCkscmdiYSgzNCwyMTEsMjM4LC4wNikpOwp9Ci5yZXZlbnVlIC5iaWd7Zm9udC1zaXplOjI0cHg7Zm9udC13ZWlnaHQ6ODAwO2NvbG9yOnZhcigtLWdyZWVuKTt0ZXh0LXNoYWRvdzowIDAgMTZweCByZ2JhKDUyLDIxMSwxNTMsLjM1KX0KLnJldmVudWUgLnN1Yntmb250LXNpemU6MTJweDtjb2xvcjp2YXIoLS1tdXQpO21hcmdpbi10b3A6M3B4fQoKLyogS3VuZGVuLUthcnRlbiAqLwouY3VzdHtib3JkZXI6MXB4IHNvbGlkIHZhcigtLWxpbmUpO2JvcmRlci1yYWRpdXM6MTJweDtwYWRkaW5nOjEycHggMTRweDttYXJnaW4tYm90dG9tOjEwcHg7YmFja2dyb3VuZDp2YXIoLS1wYW5lbCl9Ci5jdXN0IC50b3B7ZGlzcGxheTpmbGV4O2FsaWduLWl0ZW1zOmNlbnRlcjtnYXA6OHB4O2ZsZXgtd3JhcDp3cmFwfQouY3VzdCAubmFtZXtmb250LXdlaWdodDo3MDA7Zm9udC1zaXplOjE0LjVweH0KLmN1c3QgLmJhZGdle2ZvbnQtc2l6ZToxMC41cHg7cGFkZGluZzoycHggOHB4O2JvcmRlci1yYWRpdXM6OTk5cHg7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtjb2xvcjp2YXIoLS1jeWFuKX0KLmN1c3QgLm1ldGF7Zm9udC1zaXplOjEyLjVweDtjb2xvcjp2YXIoLS1tdXQpO21hcmdpbi10b3A6NHB4O2xpbmUtaGVpZ2h0OjEuNX0KLmN1c3QgLnByaWNle2NvbG9yOnZhcigtLWdyZWVuKTtmb250LXdlaWdodDo2MDB9Ci5jdXN0IC5hY3Rpb25ze2Rpc3BsYXk6ZmxleDtnYXA6N3B4O21hcmdpbi10b3A6OXB4fQoKLyogR2Vkw6RjaHRuaXMgKi8KLmZhY3RsaXN0e2xpc3Qtc3R5bGU6bm9uZTttYXJnaW46MDtwYWRkaW5nOjB9Ci5mYWN0bGlzdCBsaXtwYWRkaW5nOjhweCAxMXB4O2JvcmRlcjoxcHggc29saWQgdmFyKC0tbGluZSk7Ym9yZGVyLXJhZGl1czo5cHg7bWFyZ2luLWJvdHRvbTo3cHg7Zm9udC1zaXplOjEzLjVweDtiYWNrZ3JvdW5kOnZhcigtLXBhbmVsKX0KLmZhY3RsaXN0IGxpOjpiZWZvcmV7Y29udGVudDoi4oCiICI7Y29sb3I6dmFyKC0tY3lhbil9Ci5qb3VybmFse2ZvbnQtc2l6ZToxMi41cHg7Y29sb3I6dmFyKC0tbXV0KTtsaW5lLWhlaWdodDoxLjd9Ci5qb3VybmFsIC5ke2NvbG9yOnZhcigtLWJsdWUyKX0KLmVtcHR5e2NvbG9yOnZhcigtLW11dCk7Zm9udC1zdHlsZTppdGFsaWM7Zm9udC1zaXplOjEzcHg7cGFkZGluZzo2cHggMH0KCkBtZWRpYShtYXgtd2lkdGg6NTYwcHgpewogIC53b3JkbWFya3tmb250LXNpemU6MjJweDtsZXR0ZXItc3BhY2luZzozcHh9CiAgLm1zZ3ttYXgtd2lkdGg6OTIlfQogIC5jb3JlLXdyYXB7aGVpZ2h0Ojk2cHh9CiAgLmNvcmV7d2lkdGg6NzhweDtoZWlnaHQ6NzhweH0KfQo8L3N0eWxlPgo8L2hlYWQ+Cjxib2R5Pgo8ZGl2IGNsYXNzPSJhcHAiPgoKICA8IS0tIEtvcGZ6ZWlsZSAtLT4KICA8ZGl2IGNsYXNzPSJoZWFkZXIiPgogICAgPGRpdiBjbGFzcz0iYnJhbmQiPgogICAgICA8ZGl2PgogICAgICAgIDxkaXYgY2xhc3M9IndvcmRtYXJrIj5ESU5PPC9kaXY+CiAgICAgICAgPGRpdiBjbGFzcz0idGFnbGluZSI+ZGVpbiBlaWdlbmVyIEphcnZpcyDCtyBsw6R1ZnQgbG9rYWw8L2Rpdj4KICAgICAgICA8ZGl2IGNsYXNzPSJzdGF0dXNsaW5lIj4KICAgICAgICAgIDxzcGFuIGlkPSJzdGF0dXNEb3QiIGNsYXNzPSJkb3QiPjwvc3Bhbj4KICAgICAgICAgIDxzcGFuIGlkPSJicmFpblRleHQiPnZlcmJpbmRl4oCmPC9zcGFuPgogICAgICAgICAgPHNwYW4gaWQ9Im9sbGFtYVBpbGwiIGNsYXNzPSJvbGxhbWEtcGlsbCIgc3R5bGU9ImRpc3BsYXk6bm9uZSI+PHNwYW4gY2xhc3M9Im9wZG90Ij48L3NwYW4+PHNwYW4gaWQ9Im9sbGFtYVBpbGxUZXh0Ij5sb2thbDwvc3Bhbj48L3NwYW4+CiAgICAgICAgPC9kaXY+CiAgICAgIDwvZGl2PgogICAgPC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJzcGFjZXIiPjwvZGl2PgogICAgPGRpdiBjbGFzcz0iaWNvbmJ0bnMiPgogICAgICA8YnV0dG9uIGNsYXNzPSJpY29uYnRuIiB0aXRsZT0iS3VuZGVuIiBvbmNsaWNrPSJvcGVuUGFuZWwoJ2N1c3RvbWVycycpIj7wn5GlPC9idXR0b24+CiAgICAgIDxidXR0b24gY2xhc3M9Imljb25idG4iIHRpdGxlPSJHZWTDpGNodG5pcyIgb25jbGljaz0ib3BlblBhbmVsKCdtZW1vcnknKSI+8J+noDwvYnV0dG9uPgogICAgICA8YnV0dG9uIGNsYXNzPSJpY29uYnRuIiB0aXRsZT0iRWluc3RlbGx1bmdlbiIgb25jbGljaz0ib3BlblBhbmVsKCdzZXR0aW5ncycpIj7impk8L2J1dHRvbj4KICAgIDwvZGl2PgogIDwvZGl2PgoKICA8IS0tIENvcmUgLyBPcmIgLS0+CiAgPGRpdiBjbGFzcz0iY29yZS13cmFwIj4KICAgIDxkaXYgY2xhc3M9ImNvcmUiIGlkPSJjb3JlIj4KICAgICAgPGRpdiBjbGFzcz0icmluZyByMSI+PC9kaXY+CiAgICAgIDxkaXYgY2xhc3M9InJpbmcgcjIiPjwvZGl2PgogICAgICA8ZGl2IGNsYXNzPSJyaW5nIHIzIj48L2Rpdj4KICAgICAgPGRpdiBjbGFzcz0ibnVjbGV1cyI+PC9kaXY+CiAgICA8L2Rpdj4KICA8L2Rpdj4KCiAgPCEtLSBDaGF0IC0tPgogIDxkaXYgY2xhc3M9ImNoYXQiIGlkPSJjaGF0Ij48L2Rpdj4KCiAgPCEtLSBRdWljay1DaGlwcyAtLT4KICA8ZGl2IGNsYXNzPSJjaGlwcyI+CiAgICA8YnV0dG9uIGNsYXNzPSJjaGlwIiBvbmNsaWNrPSJxdWlja1BsYW4oKSI+8J+ThSBXb2NoZW5wbGFuPC9idXR0b24+CiAgICA8YnV0dG9uIGNsYXNzPSJjaGlwIiBvbmNsaWNrPSJxdWlja1RvZGF5KCkiPuKYgO+4jyBIZXV0ZTwvYnV0dG9uPgogICAgPGJ1dHRvbiBjbGFzcz0iY2hpcCIgb25jbGljaz0icXVpY2tMZWFybigpIj7wn6egIExlcm5lbjwvYnV0dG9uPgogICAgPGJ1dHRvbiBjbGFzcz0iY2hpcCIgb25jbGljaz0icXVpY2tDb3VuY2lsKCkiPvCfp6Dwn6eg8J+noCBSYXQgZGVyIEtJczwvYnV0dG9uPgogIDwvZGl2PgoKICA8IS0tIEVpbmdhYmVsZWlzdGUgLS0+CiAgPGRpdiBjbGFzcz0iaW5wdXRiYXIiPgogICAgPHRleHRhcmVhIGlkPSJpbnB1dCIgcm93cz0iMSIgcGxhY2Vob2xkZXI9IlNjaHJlaWIgRGlubyB3YXPigKYgKEVudGVyIHNlbmRlbiDCtyBTaGlmdCtFbnRlciBuZXVlIFplaWxlKSI+PC90ZXh0YXJlYT4KICAgIDxidXR0b24gY2xhc3M9ImlidG4gbWljIiBpZD0ibWljQnRuIiB0aXRsZT0iU3ByZWNoZW4iIG9uY2xpY2s9InRvZ2dsZU1pYygpIj7wn46kPC9idXR0b24+CiAgICA8YnV0dG9uIGNsYXNzPSJpYnRuIiBpZD0idm9pY2VCdG4iIHRpdGxlPSJTcHJhY2hhdXNnYWJlIGFuL2F1cyAoR2lkZW9uLVN0aW1tZSkiIG9uY2xpY2s9InRvZ2dsZVZvaWNlKCkiPvCflIo8L2J1dHRvbj4KICAgIDxzZWxlY3QgaWQ9InZvaWNlU2VsZWN0IiB0aXRsZT0iU3RpbW1lIHfDpGhsZW4g4oCUIEdpZGVvbiA9IGJyaXRpc2NoICYgd2VpYmxpY2giIG9uY2hhbmdlPSJvblZvaWNlU2VsZWN0KCkiIHN0eWxlPSJtYXgtd2lkdGg6MTYwcHg7YmFja2dyb3VuZDojMGIxNTI2O2NvbG9yOiNiZmU5ZjU7Ym9yZGVyOjFweCBzb2xpZCByZ2JhKDEyMCwyMDAsMjMwLC4yOCk7Ym9yZGVyLXJhZGl1czo5cHg7Zm9udC1zaXplOjExcHg7cGFkZGluZzo1cHggNnB4O291dGxpbmU6bm9uZTsiPjwvc2VsZWN0PgogICAgPGJ1dHRvbiBjbGFzcz0iaWJ0biBzZW5kIiBpZD0ic2VuZEJ0biIgdGl0bGU9IlNlbmRlbiIgb25jbGljaz0ic2VuZCgpIj7inqQ8L2J1dHRvbj4KICA8L2Rpdj4KPC9kaXY+Cgo8IS0tID09PT09PT09PT09PT09PT09PT09PSBQYW5lbHMgPT09PT09PT09PT09PT09PT09PT09IC0tPgo8ZGl2IGNsYXNzPSJvdmVybGF5IiBpZD0ib3ZlcmxheSIgb25jbGljaz0iY2xvc2VQYW5lbHMoKSI+PC9kaXY+Cgo8IS0tIEVpbnN0ZWxsdW5nZW4gLS0+Cjxhc2lkZSBjbGFzcz0icGFuZWwiIGlkPSJwYW5lbC1zZXR0aW5ncyI+CiAgPGRpdiBjbGFzcz0icGFuZWwtaGVhZCI+PHNwYW4+4pqZPC9zcGFuPjxoMj5FaW5zdGVsbHVuZ2VuPC9oMj48YnV0dG9uIGNsYXNzPSJjbG9zZSIgb25jbGljaz0iY2xvc2VQYW5lbHMoKSI+4pyVPC9idXR0b24+PC9kaXY+CiAgPGRpdiBjbGFzcz0icGFuZWwtYm9keSIgaWQ9InNldHRpbmdzQm9keSI+PGRpdiBjbGFzcz0iZW1wdHkiPmzDpGR04oCmPC9kaXY+PC9kaXY+CjwvYXNpZGU+Cgo8IS0tIEt1bmRlbiAtLT4KPGFzaWRlIGNsYXNzPSJwYW5lbCIgaWQ9InBhbmVsLWN1c3RvbWVycyI+CiAgPGRpdiBjbGFzcz0icGFuZWwtaGVhZCI+PHNwYW4+8J+RpTwvc3Bhbj48aDI+S3VuZGVuPC9oMj48YnV0dG9uIGNsYXNzPSJjbG9zZSIgb25jbGljaz0iY2xvc2VQYW5lbHMoKSI+4pyVPC9idXR0b24+PC9kaXY+CiAgPGRpdiBjbGFzcz0icGFuZWwtYm9keSIgaWQ9ImN1c3RvbWVyc0JvZHkiPjxkaXYgY2xhc3M9ImVtcHR5Ij5sw6RkdOKApjwvZGl2PjwvZGl2Pgo8L2FzaWRlPgoKPCEtLSBHZWTDpGNodG5pcyAtLT4KPGFzaWRlIGNsYXNzPSJwYW5lbCIgaWQ9InBhbmVsLW1lbW9yeSI+CiAgPGRpdiBjbGFzcz0icGFuZWwtaGVhZCI+PHNwYW4+8J+noDwvc3Bhbj48aDI+R2Vkw6RjaHRuaXM8L2gyPjxidXR0b24gY2xhc3M9ImNsb3NlIiBvbmNsaWNrPSJjbG9zZVBhbmVscygpIj7inJU8L2J1dHRvbj48L2Rpdj4KICA8ZGl2IGNsYXNzPSJwYW5lbC1ib2R5IiBpZD0ibWVtb3J5Qm9keSI+PGRpdiBjbGFzcz0iZW1wdHkiPmzDpGR04oCmPC9kaXY+PC9kaXY+CjwvYXNpZGU+Cgo8c2NyaXB0PgoidXNlIHN0cmljdCI7Ci8qID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQogICBESU5PIEtJIOKAlCBGcm9udGVuZC1Mb2dpawogICBTcHJpY2h0IHBlciBmZXRjaCgpIG1pdCBkZW0gbG9rYWxlbiBTZXJ2ZXIgKGdsZWljaGVyIE9yaWdpbikuCiAgID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PSAqLwoKLy8gLS0tLSBadXN0YW5kIC0tLS0KY29uc3Qgc3RhdGUgPSB7CiAgbWVzc2FnZXM6IFtdLCAgICAgICAgICAvLyBDaGF0LUhpc3RvcmllIHtyb2xlLCBjb250ZW50fQogIHJlYWR5OiBmYWxzZSwKICBhc3Npc3RhbnROYW1lOiAiRGlubyIsCiAgdXNlck5hbWU6ICJCb3NzIiwKICBidXN5OiBmYWxzZSwKICB2b2ljZU9uOiBmYWxzZSwgICAgICAgIC8vIFNwcmFjaGF1c2dhYmUgYW4vYXVzCiAgc3RhdHVzVmFsdWVzOiBbIkxlYWQiLCJBbmdlYm90IiwiQWt0aXYiLCJCZXphaGx0IiwiUGF1c2llcnQiLCJCZWVuZGV0Il0sCiAgcHJvdmlkZXI6IG51bGwsICAgICAgICAvLyAib2xsYW1hIiB8ICJjbGF1ZGUiIHwgIm9wZW5haSIgfCAiZ2VtaW5pIgogIGF1dG9SZWNoZWNrRG9uZTogZmFsc2UsLy8gZWlubWFsaWdlcyBBdXRvLVJlY2hlY2sgYmVpbSBlcnN0ZW4gTGFkZW4KfTsKCi8vIC0tLS0gRE9NLUt1cnpoZWxmZXIgLS0tLQpjb25zdCAkID0gKGlkKSA9PiBkb2N1bWVudC5nZXRFbGVtZW50QnlJZChpZCk7CmNvbnN0IGNoYXRFbCA9ICQoImNoYXQiKTsKY29uc3QgY29yZUVsID0gJCgiY29yZSIpOwpjb25zdCBpbnB1dEVsID0gJCgiaW5wdXQiKTsKCi8vIC0tLS0gSGlsZnNmdW5rdGlvbmVuIC0tLS0KZnVuY3Rpb24gZXVybyh4KXsKICBjb25zdCBuID0gTnVtYmVyKHgpIHx8IDA7CiAgcmV0dXJuIG4udG9Mb2NhbGVTdHJpbmcoImRlLURFIix7bWF4aW11bUZyYWN0aW9uRGlnaXRzOjB9KSArICIg4oKsIjsKfQpmdW5jdGlvbiBlc2Mocyl7IC8vIHdpciBudXR6ZW4gb2huZWhpbiB0ZXh0Q29udGVudCwgZGllcyBudXIgZsO8ciBzaWNoZXJlIEF0dHJpYnV0LWZyZWllIEFuemVpZ2UKICByZXR1cm4gU3RyaW5nKHMgPT0gbnVsbCA/ICIiIDogcyk7Cn0KCi8vIC0tLS0gQ29yZS1BbmltYXRpb25lbiAtLS0tCmZ1bmN0aW9uIHNldFRoaW5raW5nKG9uKXsgY29yZUVsLmNsYXNzTGlzdC50b2dnbGUoInRoaW5raW5nIiwgb24pOyB9CmZ1bmN0aW9uIHNldFNwZWFraW5nKG9uKXsgY29yZUVsLmNsYXNzTGlzdC50b2dnbGUoInNwZWFraW5nIiwgb24pOyB9CgovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KLy8gIENoYXQtQW56ZWlnZQovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KLyoqCiAqIEbDvGd0IGVpbmUgQnViYmxlIGhpbnp1LiBJbmhhbHQgd2lyZCB2aWEgdGV4dENvbnRlbnQgZ2VzZXR6dCAoa2VpbiBYU1MpLgogKiBraW5kOiAiZGlubyIgfCAidXNlciIgfCAiaW5mbyIgfCAiZXJyb3IiIHwgInN5bnRoIiB8ICJjb3VuY2lsIgogKiBsYWJlbDogb3B0aW9uYWxlcyBMYWJlbCAoei5CLiBLSS1OYW1lKQogKi8KZnVuY3Rpb24gYWRkQnViYmxlKGtpbmQsIHRleHQsIGxhYmVsKXsKICBjb25zdCB3cmFwID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7CiAgY29uc3QgY2xzID0gKGtpbmQgPT09ICJzeW50aCIgfHwga2luZCA9PT0gImNvdW5jaWwiKSA/ICJkaW5vIiA6IGtpbmQ7CiAgd3JhcC5jbGFzc05hbWUgPSAibXNnICIgKyAoa2luZCA9PT0gInN5bnRoIiA/ICJkaW5vIHN5bnRoIiA6IGNscyk7CgogIC8vIEF2YXRhciBudXIgZsO8ciBEaW5vLS9OdXR6ZXItL0ZlaGxlci1CdWJibGVzCiAgaWYgKGtpbmQgPT09ICJkaW5vIiB8fCBraW5kID09PSAic3ludGgiIHx8IGtpbmQgPT09ICJjb3VuY2lsIil7CiAgICBjb25zdCBhID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IGEuY2xhc3NOYW1lPSJhdmF0YXIiOyBhLnRleHRDb250ZW50PSLwn6aWIjsgd3JhcC5hcHBlbmRDaGlsZChhKTsKICB9IGVsc2UgaWYgKGtpbmQgPT09ICJ1c2VyIil7CiAgICBjb25zdCBhID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IGEuY2xhc3NOYW1lPSJhdmF0YXIiOyBhLnRleHRDb250ZW50PSLwn6eRIjsgd3JhcC5hcHBlbmRDaGlsZChhKTsKICB9IGVsc2UgaWYgKGtpbmQgPT09ICJlcnJvciIpewogICAgY29uc3QgYSA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBhLmNsYXNzTmFtZT0iYXZhdGFyIjsgYS50ZXh0Q29udGVudD0i4pqg77iPIjsgd3JhcC5hcHBlbmRDaGlsZChhKTsKICB9CgogIGNvbnN0IGIgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgYi5jbGFzc05hbWU9ImJ1YmJsZSI7CiAgaWYgKGxhYmVsKXsKICAgIGNvbnN0IGwgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgbC5jbGFzc05hbWU9ImxhYmVsIjsgbC50ZXh0Q29udGVudCA9IGxhYmVsOwogICAgYi5hcHBlbmRDaGlsZChsKTsKICAgIGNvbnN0IHQgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgdC50ZXh0Q29udGVudCA9IHRleHQ7IGIuYXBwZW5kQ2hpbGQodCk7CiAgfSBlbHNlIHsKICAgIGIudGV4dENvbnRlbnQgPSB0ZXh0OwogIH0KICB3cmFwLmFwcGVuZENoaWxkKGIpOwogIGNoYXRFbC5hcHBlbmRDaGlsZCh3cmFwKTsKICBzY3JvbGxEb3duKCk7CiAgcmV0dXJuIHdyYXA7Cn0KCmZ1bmN0aW9uIHNjcm9sbERvd24oKXsgcmVxdWVzdEFuaW1hdGlvbkZyYW1lKCgpPT57IGNoYXRFbC5zY3JvbGxUb3AgPSBjaGF0RWwuc2Nyb2xsSGVpZ2h0OyB9KTsgfQoKLy8gVGlwcC1JbmRpa2F0b3IKbGV0IHR5cGluZ0VsID0gbnVsbDsKZnVuY3Rpb24gc2hvd1R5cGluZygpewogIGlmICh0eXBpbmdFbCkgcmV0dXJuOwogIHR5cGluZ0VsID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7CiAgdHlwaW5nRWwuY2xhc3NOYW1lID0gIm1zZyBkaW5vIjsKICB0eXBpbmdFbC5pbm5lckhUTUwgPSAnPGRpdiBjbGFzcz0iYXZhdGFyIj7wn6aWPC9kaXY+PGRpdiBjbGFzcz0iYnViYmxlIj48ZGl2IGNsYXNzPSJ0eXBpbmciPjxzcGFuPjwvc3Bhbj48c3Bhbj48L3NwYW4+PHNwYW4+PC9zcGFuPjwvZGl2PjwvZGl2Pic7CiAgY2hhdEVsLmFwcGVuZENoaWxkKHR5cGluZ0VsKTsKICBzY3JvbGxEb3duKCk7Cn0KZnVuY3Rpb24gaGlkZVR5cGluZygpeyBpZiAodHlwaW5nRWwpeyB0eXBpbmdFbC5yZW1vdmUoKTsgdHlwaW5nRWwgPSBudWxsOyB9IH0KCi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQovLyAgTmV0endlcmsKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09CmFzeW5jIGZ1bmN0aW9uIGFwaShwYXRoLCBtZXRob2QsIGJvZHkpewogIGNvbnN0IG9wdCA9IHsgbWV0aG9kOiBtZXRob2QgfHwgIkdFVCIsIGhlYWRlcnM6e30gfTsKICBpZiAoYm9keSAhPT0gdW5kZWZpbmVkKXsgb3B0LmhlYWRlcnNbIkNvbnRlbnQtVHlwZSJdPSJhcHBsaWNhdGlvbi9qc29uIjsgb3B0LmJvZHkgPSBKU09OLnN0cmluZ2lmeShib2R5KTsgfQogIGNvbnN0IHJlcyA9IGF3YWl0IGZldGNoKHBhdGgsIG9wdCk7CiAgLy8gVmVyc3VjaGUgSlNPTiB6dSBsZXNlbiDigJMgYXVjaCBiZWkgNHh4LzV4eCBrYW5uIGVpbiB7ZXJyb3J9IGtvbW1lbgogIGxldCBkYXRhOwogIHRyeSB7IGRhdGEgPSBhd2FpdCByZXMuanNvbigpOyB9CiAgY2F0Y2goZSl7IHRocm93IG5ldyBFcnJvcigiVW5nw7xsdGlnZSBBbnR3b3J0IHZvbSBTZXJ2ZXIgKGtlaW4gSlNPTikuIik7IH0KICByZXR1cm4gZGF0YTsKfQoKLy8gQnVzeS1adXN0YW5kIChzcGVycnQgU2VuZGVuICsgQ2hpcHMgd8OkaHJlbmQgZWluZXIgQW5mcmFnZSkKZnVuY3Rpb24gc2V0QnVzeShvbil7CiAgc3RhdGUuYnVzeSA9IG9uOwogIHNldFRoaW5raW5nKG9uKTsKICAkKCJzZW5kQnRuIikuZGlzYWJsZWQgPSBvbjsKICBkb2N1bWVudC5xdWVyeVNlbGVjdG9yQWxsKCIuY2hpcCIpLmZvckVhY2goYyA9PiBjLmRpc2FibGVkID0gb24pOwogIGlmIChvbikgc2hvd1R5cGluZygpOyBlbHNlIGhpZGVUeXBpbmcoKTsKfQoKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09Ci8vICBTdGFydDogU3RhdHVzIGxhZGVuCi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQphc3luYyBmdW5jdGlvbiBsb2FkU3RhdHVzKCl7CiAgdHJ5ewogICAgY29uc3QgcyA9IGF3YWl0IGFwaSgiL2FwaS9zdGF0dXMiKTsKICAgIGlmIChzLmVycm9yKXsgbWFya1N0YXR1cyhmYWxzZSwgIkZlaGxlcjogIitzLmVycm9yKTsgcmV0dXJuOyB9CiAgICBzdGF0ZS5yZWFkeSA9ICEhcy5yZWFkeTsKICAgIHN0YXRlLmFzc2lzdGFudE5hbWUgPSBzLmFzc2lzdGFudF9uYW1lIHx8ICJEaW5vIjsKICAgIHN0YXRlLnVzZXJOYW1lID0gcy51c2VyX25hbWUgfHwgIkJvc3MiOwogICAgc3RhdGUucHJvdmlkZXIgPSBzLnByb3ZpZGVyIHx8IG51bGw7CiAgICBtYXJrU3RhdHVzKHMucmVhZHksIHMuYnJhaW4gfHwgIuKAlCIpOwoKICAgIGlmIChzdGF0ZS5wcm92aWRlciA9PT0gIm9sbGFtYSIpewogICAgICAvLyBMb2thbGVzIEdlaGlybiAtPiBlaWdlbmUgT25ib2FyZGluZy0vU2V0dXAtTG9naWsgKGvDvG1tZXJ0IHNpY2ggdW0gQmVncsO8w591bmcvS2FydGUpCiAgICAgIGF3YWl0IGNoZWNrT2xsYW1hKCk7CiAgICAgIHJldHVybjsKICAgIH0KCiAgICAvLyBBbmRlcmUgQW5iaWV0ZXIgKENsYXVkZSBldGMuKTogVmVyaGFsdGVuIHdpZSBiaXNoZXIKICAgIGhpZGVPbGxhbWFQaWxsKCk7CiAgICBpZiAoIXN0YXRlLnJlYWR5KXsKICAgICAgLy8gTmljaHQgYmVyZWl0IC0+IGZyZXVuZGxpY2hlIFN0YXJ0bmFjaHJpY2h0ICsgRWluc3RlbGx1bmdlbiDDtmZmbmVuCiAgICAgIGlmIChjaGF0RWwuY2hpbGRyZW4ubGVuZ3RoID09PSAwKQogICAgICAgIGFkZEJ1YmJsZSgiZGlubyIsICJUcmFnIHp1ZXJzdCBkZWluZW4gQVBJLVNjaGzDvHNzZWwgdW50ZXIg4pqZIGVpbiwgZGFubiBsZWdlIGljaCBsb3MuIPCfppYiKTsKICAgICAgb3BlblBhbmVsKCJzZXR0aW5ncyIpOwogICAgfSBlbHNlIGlmIChjaGF0RWwuY2hpbGRyZW4ubGVuZ3RoID09PSAwKXsKICAgICAgLy8gQmVyZWl0IC0+IEJlZ3LDvMOfdW5nCiAgICAgIGdyZWV0KCk7CiAgICB9CiAgfWNhdGNoKGUpewogICAgbWFya1N0YXR1cyhmYWxzZSwgIm9mZmxpbmUiKTsKICAgIGFkZEJ1YmJsZSgiZXJyb3IiLCAiS29tbWUgbmljaHQgYW4gZGVuIERpbm8tU2VydmVyIHJhbiAoIitlLm1lc3NhZ2UrIikuIEzDpHVmdCBkZXIgbG9rYWxlIFNlcnZlcj8iKTsKICB9Cn0KCmZ1bmN0aW9uIG1hcmtTdGF0dXMocmVhZHksIGJyYWluKXsKICBjb25zdCBkb3QgPSAkKCJzdGF0dXNEb3QiKTsKICBkb3QuY2xhc3NOYW1lID0gImRvdCAiICsgKHJlYWR5ID8gIm9rIiA6ICJiYWQiKTsKICAkKCJicmFpblRleHQiKS50ZXh0Q29udGVudCA9IGJyYWluICsgKHJlYWR5ID8gIiAgwrcgIG9ubGluZSIgOiAiICDCtyAgb2ZmbGluZSIpOwp9CgovLyBCZWdyw7zDn3VuZyAobnVyIGZhbGxzIENoYXQgbm9jaCBsZWVyKSDigJQgemVudHJhbCwgZGFtaXQgw7xiZXJhbGwgd2llZGVydmVyd2VuZGJhcgpmdW5jdGlvbiBncmVldCgpewogIGlmIChjaGF0RWwuY2hpbGRyZW4ubGVuZ3RoID09PSAwKQogICAgYWRkQnViYmxlKCJkaW5vIiwgYERpbm8gaXN0IG9ubGluZSwgJHtzdGF0ZS51c2VyTmFtZX0hIFdvcmF1ZiBoYXN0IGR1IEJvY2s/IOKaoWApOwp9CgovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KLy8gIE9sbGFtYS1PbmJvYXJkaW5nIChsb2thbGVzIEdlaGlybikKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09CmNvbnN0IE9MTEFNQV9ERUZBVUxUX01PREVMID0gImxsYW1hMy4yIjsKbGV0IHNldHVwQ2FyZEVsID0gbnVsbDsKCi8vIFRvbGVyYW50OiBnaWx0IGN1cnJlbnRfbW9kZWwgYWxzIGluc3RhbGxpZXJ0PyAoei5CLiAibGxhbWEzLjIiIG1hdGNodCAibGxhbWEzLjI6bGF0ZXN0IikKZnVuY3Rpb24gbW9kZWxJbnN0YWxsZWQobW9kZWxzLCBjdXJyZW50KXsKICBpZiAoIUFycmF5LmlzQXJyYXkobW9kZWxzKSB8fCAhbW9kZWxzLmxlbmd0aCkgcmV0dXJuIGZhbHNlOwogIGlmICghY3VycmVudCkgcmV0dXJuIGZhbHNlOwogIHJldHVybiBtb2RlbHMuc29tZShtID0+IHsKICAgIGNvbnN0IGEgPSBTdHJpbmcobSksIGIgPSBTdHJpbmcoY3VycmVudCk7CiAgICByZXR1cm4gYSA9PT0gYiB8fCBhLnN0YXJ0c1dpdGgoYikgfHwgYi5zdGFydHNXaXRoKGEpOwogIH0pOwp9CgovLyBrbGVpbmVyIFN0YXR1cy1JbmRpa2F0b3Igb2JlbgpmdW5jdGlvbiBzZXRPbGxhbWFQaWxsKGtpbmQsIGxhYmVsKXsKICBjb25zdCBwaWxsID0gJCgib2xsYW1hUGlsbCIpOwogIGlmICghcGlsbCkgcmV0dXJuOwogIHBpbGwuc3R5bGUuZGlzcGxheSA9ICJpbmxpbmUtZmxleCI7CiAgcGlsbC5jbGFzc05hbWUgPSAib2xsYW1hLXBpbGwgIiArIChraW5kIHx8ICIiKTsKICAkKCJvbGxhbWFQaWxsVGV4dCIpLnRleHRDb250ZW50ID0gbGFiZWw7Cn0KZnVuY3Rpb24gaGlkZU9sbGFtYVBpbGwoKXsKICBjb25zdCBwaWxsID0gJCgib2xsYW1hUGlsbCIpOwogIGlmIChwaWxsKSBwaWxsLnN0eWxlLmRpc3BsYXkgPSAibm9uZSI7Cn0KCi8vIEVudGZlcm50IGVpbmUgZ2dmLiB2b3JoYW5kZW5lIFNldHVwLUthcnRlCmZ1bmN0aW9uIHJlbW92ZVNldHVwQ2FyZCgpewogIGlmIChzZXR1cENhcmRFbCl7IHNldHVwQ2FyZEVsLnJlbW92ZSgpOyBzZXR1cENhcmRFbCA9IG51bGw7IH0KfQoKLy8gUHLDvGZ0IC9hcGkvb2xsYW1hIHVuZCBlbnRzY2hlaWRldCDDvGJlciBLYXJ0ZS9CZWdyw7zDn3VuZwphc3luYyBmdW5jdGlvbiBjaGVja09sbGFtYSgpewogIGxldCBvOwogIHRyeXsKICAgIG8gPSBhd2FpdCBhcGkoIi9hcGkvb2xsYW1hIik7CiAgfWNhdGNoKGUpewogICAgLy8gS29ubnRlIE9sbGFtYS1JbmZvIG5pY2h0IGxhZGVuIC0+IGJlaGFuZGVsbiB3aWUgImzDpHVmdCBuaWNodCIKICAgIG8gPSB7IHJ1bm5pbmc6ZmFsc2UsIG1vZGVsczpbXSwgY3VycmVudF9tb2RlbDpPTExBTUFfREVGQVVMVF9NT0RFTCB9OwogIH0KICBpZiAobyAmJiBvLmVycm9yKXsgbyA9IHsgcnVubmluZzpmYWxzZSwgbW9kZWxzOltdLCBjdXJyZW50X21vZGVsOk9MTEFNQV9ERUZBVUxUX01PREVMIH07IH0KCiAgY29uc3QgcnVubmluZyA9ICEhKG8gJiYgby5ydW5uaW5nKTsKICBjb25zdCBtb2RlbHMgPSAobyAmJiBBcnJheS5pc0FycmF5KG8ubW9kZWxzKSkgPyBvLm1vZGVscyA6IFtdOwogIGNvbnN0IGN1cnJlbnQgPSAobyAmJiBvLmN1cnJlbnRfbW9kZWwpIHx8IE9MTEFNQV9ERUZBVUxUX01PREVMOwogIGNvbnN0IGhhc01vZGVsID0gbW9kZWxJbnN0YWxsZWQobW9kZWxzLCBjdXJyZW50KTsKCiAgaWYgKHJ1bm5pbmcgJiYgaGFzTW9kZWwpewogICAgLy8gQWxsZXMgYmVyZWl0IC0+IGtlaW5lIEthcnRlLCBub3JtYWxlIEJlZ3LDvMOfdW5nCiAgICBzZXRPbGxhbWFQaWxsKCJvayIsICJsb2thbCBha3RpdiIpOwogICAgcmVtb3ZlU2V0dXBDYXJkKCk7CiAgICBncmVldCgpOwogICAgcmV0dXJuIHRydWU7CiAgfQoKICBpZiAoIXJ1bm5pbmcpewogICAgc2V0T2xsYW1hUGlsbCgiYmFkIiwgIlNldHVwIG7DtnRpZyIpOwogICAgc2hvd1NldHVwQ2FyZCgibm90LXJ1bm5pbmciLCB7IG1vZGVscywgY3VycmVudCB9KTsKICB9IGVsc2UgewogICAgLy8gbMOkdWZ0LCBhYmVyIGtlaW4gcGFzc2VuZGVzIE1vZGVsbAogICAgc2V0T2xsYW1hUGlsbCgid2FybiIsICJNb2RlbGwgZmVobHQiKTsKICAgIHNob3dTZXR1cENhcmQoIm5vLW1vZGVsIiwgeyBtb2RlbHMsIGN1cnJlbnQgfSk7CiAgfQoKICAvLyBFaW5tYWxpZ2VzIEF1dG8tUmVjaGVjayBuYWNoIH4ycyBiZWltIGVyc3RlbiBMYWRlbiAoa2VpbiBEYXVlci1Qb2xsaW5nKQogIGlmICghc3RhdGUuYXV0b1JlY2hlY2tEb25lKXsKICAgIHN0YXRlLmF1dG9SZWNoZWNrRG9uZSA9IHRydWU7CiAgICBzZXRUaW1lb3V0KCgpPT57IGlmIChzZXR1cENhcmRFbCkgcmVjaGVja09sbGFtYSgpOyB9LCAyMDAwKTsKICB9CiAgcmV0dXJuIGZhbHNlOwp9CgovLyBCYXV0L2FrdHVhbGlzaWVydCBkaWUgU2V0dXAtS2FydGUgKHN0YXRpc2NoZXMgTWFya3VwID0gaW5uZXJIVE1MOyBkeW5hbWlzY2hlIFRleHRlIHZpYSB0ZXh0Q29udGVudCkKZnVuY3Rpb24gc2hvd1NldHVwQ2FyZChtb2RlLCBpbmZvKXsKICByZW1vdmVTZXR1cENhcmQoKTsKICBjb25zdCBjYXJkID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7CiAgY2FyZC5jbGFzc05hbWUgPSAic2V0dXAtY2FyZCI7CgogIGlmIChtb2RlID09PSAibm8tbW9kZWwiKXsKICAgIGNhcmQuaW5uZXJIVE1MID0gYAogICAgICA8ZGl2IGNsYXNzPSJzYy10aXRsZSI+8J+noCBEaW5vIGZlaGx0IG5vY2ggZWluIE1vZGVsbDwvZGl2PgogICAgICA8ZGl2IGNsYXNzPSJzYy1zdWIiPk9sbGFtYSBsw6R1ZnQgc2Nob24g4oCUIERpbm8gYnJhdWNodCBudXIgbm9jaCBlaW4gU3ByYWNobW9kZWxsLiBIb2wgZGlyIGRhcyBTdGFuZGFyZG1vZGVsbCBvZGVyIHfDpGhsIGVpbnMgZGVyIGluc3RhbGxpZXJ0ZW4uPC9kaXY+CiAgICAgIDxkaXYgY2xhc3M9InNjLXN0ZXAiPgogICAgICAgIDxkaXYgY2xhc3M9InNjLXN0ZXAtaCI+PHNwYW4gY2xhc3M9Im51bSI+4oaTPC9zcGFuPjxzcGFuPk1vZGVsbCBsYWRlbiAoZ3JhdGlzKTwvc3Bhbj48L2Rpdj4KICAgICAgICA8ZGl2IGNsYXNzPSJzYy1jb2RlYm94Ij4KICAgICAgICAgIDxjb2RlIGNsYXNzPSJzYy1jb2RlIiBpZD0ic2MtY21kIj48L2NvZGU+CiAgICAgICAgICA8YnV0dG9uIGNsYXNzPSJzYy1jb3B5IiBpZD0ic2MtY29weSI+8J+TiyBLb3BpZXJlbjwvYnV0dG9uPgogICAgICAgIDwvZGl2PgogICAgICAgIDxkaXYgY2xhc3M9InNjLW1vZGVscyIgaWQ9InNjLW1vZGVscyI+PC9kaXY+CiAgICAgIDwvZGl2PgogICAgICA8ZGl2IGNsYXNzPSJzYy1hY3Rpb25zIj4KICAgICAgICA8YnV0dG9uIGNsYXNzPSJzYy1yZWNoZWNrIiBpZD0ic2MtcmVjaGVjayI+8J+UhCBOb2NobWFsIHByw7xmZW48L2J1dHRvbj4KICAgICAgICA8c3BhbiBjbGFzcz0ic2Mtc3RhdGUiIGlkPSJzYy1zdGF0ZSI+PC9zcGFuPgogICAgICA8L2Rpdj4KICAgIGA7CiAgfSBlbHNlIHsKICAgIGNhcmQuaW5uZXJIVE1MID0gYAogICAgICA8ZGl2IGNsYXNzPSJzYy10aXRsZSI+8J+mliBGYXN0IGZlcnRpZyDigJQgRGlubyBicmF1Y2h0IG5vY2ggc2VpbiBHZWhpcm48L2Rpdj4KICAgICAgPGRpdiBjbGFzcz0ic2Mtc3ViIj5EaW5vIGzDpHVmdCBzdGFuZGFyZG3DpMOfaWcgZ3JhdGlzIHVuZCBsb2thbCDDvGJlciBPbGxhbWEuIFp3ZWkga3VyemUgU2Nocml0dGUsIGRhbm4gZ2VodCdzIGxvcy48L2Rpdj4KICAgICAgPGRpdiBjbGFzcz0ic2Mtc3RlcCI+CiAgICAgICAgPGRpdiBjbGFzcz0ic2Mtc3RlcC1oIj48c3BhbiBjbGFzcz0ibnVtIj4xPC9zcGFuPjxzcGFuPk9sbGFtYSBpbnN0YWxsaWVyZW4gKGdyYXRpcyk8L3NwYW4+PC9kaXY+CiAgICAgICAgPGRpdiBjbGFzcz0ic2Mtc3ViIiBzdHlsZT0ibWFyZ2luOjAiPgogICAgICAgICAgTGFkZSBlcyBoaWVyIGhlcnVudGVyOiA8YSBjbGFzcz0ic2MtbGluayIgaWQ9InNjLWRsIiBocmVmPSJodHRwczovL29sbGFtYS5jb20vZG93bmxvYWQiIHRhcmdldD0iX2JsYW5rIiByZWw9Im5vb3BlbmVyIG5vcmVmZXJyZXIiPm9sbGFtYS5jb20vZG93bmxvYWQ8L2E+CiAgICAgICAgPC9kaXY+CiAgICAgIDwvZGl2PgogICAgICA8ZGl2IGNsYXNzPSJzYy1zdGVwIj4KICAgICAgICA8ZGl2IGNsYXNzPSJzYy1zdGVwLWgiPjxzcGFuIGNsYXNzPSJudW0iPjI8L3NwYW4+PHNwYW4+RGllc2VzIEtvbW1hbmRvIGltIFRlcm1pbmFsIC8gaW4gZGVyIEVpbmdhYmVhdWZmb3JkZXJ1bmcgYXVzZsO8aHJlbjo8L3NwYW4+PC9kaXY+CiAgICAgICAgPGRpdiBjbGFzcz0ic2MtY29kZWJveCI+CiAgICAgICAgICA8Y29kZSBjbGFzcz0ic2MtY29kZSIgaWQ9InNjLWNtZCI+PC9jb2RlPgogICAgICAgICAgPGJ1dHRvbiBjbGFzcz0ic2MtY29weSIgaWQ9InNjLWNvcHkiPvCfk4sgS29waWVyZW48L2J1dHRvbj4KICAgICAgICA8L2Rpdj4KICAgICAgPC9kaXY+CiAgICAgIDxkaXYgY2xhc3M9InNjLWFjdGlvbnMiPgogICAgICAgIDxidXR0b24gY2xhc3M9InNjLXJlY2hlY2siIGlkPSJzYy1yZWNoZWNrIj7wn5SEIE5vY2htYWwgcHLDvGZlbjwvYnV0dG9uPgogICAgICAgIDxidXR0b24gY2xhc3M9InNjLXNldHRpbmdzIiBpZD0ic2Mtc2V0dGluZ3MiPkxpZWJlciBkZW4gc3RhcmtlbiBDbGF1ZGUgbnV0emVuPyDihpIg4pqZIEVpbnN0ZWxsdW5nZW48L2J1dHRvbj4KICAgICAgICA8c3BhbiBjbGFzcz0ic2Mtc3RhdGUiIGlkPSJzYy1zdGF0ZSI+PC9zcGFuPgogICAgICA8L2Rpdj4KICAgIGA7CiAgfQoKICAvLyBLYXJ0ZSBvYmVuIGltIENoYXQgcGxhdHppZXJlbiwgZGFtaXQgc2llIGd1dCBzaWNodGJhciBpc3QKICBjaGF0RWwucHJlcGVuZChjYXJkKTsKICBzZXR1cENhcmRFbCA9IGNhcmQ7CiAgc2Nyb2xsRG93bigpOwoKICAvLyBLb21tYW5kby1UZXh0IChkeW5hbWlzY2ggLT4gdGV4dENvbnRlbnQsIGtlaW4gaW5uZXJIVE1MKQogIGNvbnN0IGNtZCA9IChtb2RlID09PSAibm8tbW9kZWwiKQogICAgPyAoIm9sbGFtYSBwdWxsICIgKyAoaW5mbyAmJiBpbmZvLmN1cnJlbnQgPyBpbmZvLmN1cnJlbnQgOiBPTExBTUFfREVGQVVMVF9NT0RFTCkpCiAgICA6ICgib2xsYW1hIHJ1biAiICsgT0xMQU1BX0RFRkFVTFRfTU9ERUwpOwogIGNvbnN0IGNtZEVsID0gY2FyZC5xdWVyeVNlbGVjdG9yKCIjc2MtY21kIik7CiAgaWYgKGNtZEVsKSBjbWRFbC50ZXh0Q29udGVudCA9IGNtZDsKCiAgLy8gS29waWVyZW4tQnV0dG9uCiAgY29uc3QgY29weUJ0biA9IGNhcmQucXVlcnlTZWxlY3RvcigiI3NjLWNvcHkiKTsKICBpZiAoY29weUJ0bikgY29weUJ0bi5vbmNsaWNrID0gKCk9PiBjb3B5VG9DbGlwYm9hcmQoY21kLCBjb3B5QnRuKTsKCiAgLy8gUmVjaGVjay1CdXR0b24KICBjb25zdCByZWNoZWNrQnRuID0gY2FyZC5xdWVyeVNlbGVjdG9yKCIjc2MtcmVjaGVjayIpOwogIGlmIChyZWNoZWNrQnRuKSByZWNoZWNrQnRuLm9uY2xpY2sgPSByZWNoZWNrT2xsYW1hOwoKICAvLyBFaW5zdGVsbHVuZ2VuLUxpbmsKICBjb25zdCBzZXRCdG4gPSBjYXJkLnF1ZXJ5U2VsZWN0b3IoIiNzYy1zZXR0aW5ncyIpOwogIGlmIChzZXRCdG4pIHNldEJ0bi5vbmNsaWNrID0gKCk9PiBvcGVuUGFuZWwoInNldHRpbmdzIik7CgogIC8vIEluc3RhbGxpZXJ0ZSBNb2RlbGxlIGFscyBCdXR0b25zIChudXIgaW0gbm8tbW9kZWwtRmFsbCB1bmQgd2VubiB2b3JoYW5kZW4pCiAgaWYgKG1vZGUgPT09ICJuby1tb2RlbCIpewogICAgY29uc3Qgd3JhcCA9IGNhcmQucXVlcnlTZWxlY3RvcigiI3NjLW1vZGVscyIpOwogICAgY29uc3QgbW9kZWxzID0gKGluZm8gJiYgQXJyYXkuaXNBcnJheShpbmZvLm1vZGVscykpID8gaW5mby5tb2RlbHMgOiBbXTsKICAgIGlmICh3cmFwICYmIG1vZGVscy5sZW5ndGgpewogICAgICBjb25zdCBsYmwgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJzcGFuIik7CiAgICAgIGxibC5zdHlsZS5jc3NUZXh0ID0gImZvbnQtc2l6ZToxMnB4O2NvbG9yOnZhcigtLW11dCk7YWxpZ24tc2VsZjpjZW50ZXI7bWFyZ2luLXJpZ2h0OjJweCI7CiAgICAgIGxibC50ZXh0Q29udGVudCA9ICJTY2hvbiBpbnN0YWxsaWVydDoiOwogICAgICB3cmFwLmFwcGVuZENoaWxkKGxibCk7CiAgICAgIG1vZGVscy5mb3JFYWNoKG09PnsKICAgICAgICBjb25zdCBiID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiYnV0dG9uIik7CiAgICAgICAgYi5jbGFzc05hbWUgPSAic2MtbW9kZWwiOwogICAgICAgIGIudGV4dENvbnRlbnQgPSBtOyAgICAgICAgICAgICAgICAgLy8gZHluYW1pc2NoIC0+IHRleHRDb250ZW50CiAgICAgICAgYi5vbmNsaWNrID0gKCk9PiBwaWNrT2xsYW1hTW9kZWwobSwgYik7CiAgICAgICAgd3JhcC5hcHBlbmRDaGlsZChiKTsKICAgICAgfSk7CiAgICB9CiAgfQp9CgovLyBJbiBad2lzY2hlbmFibGFnZSBrb3BpZXJlbiAobWl0IEZhbGxiYWNrKQpmdW5jdGlvbiBjb3B5VG9DbGlwYm9hcmQodGV4dCwgYnRuKXsKICBjb25zdCBkb25lID0gKCk9PnsKICAgIGlmICghYnRuKSByZXR1cm47CiAgICBjb25zdCBvbGQgPSBidG4udGV4dENvbnRlbnQ7CiAgICBidG4udGV4dENvbnRlbnQgPSAi4pyTIEtvcGllcnQiOwogICAgc2V0VGltZW91dCgoKT0+eyBidG4udGV4dENvbnRlbnQgPSBvbGQ7IH0sIDE1MDApOwogIH07CiAgdHJ5ewogICAgaWYgKG5hdmlnYXRvci5jbGlwYm9hcmQgJiYgbmF2aWdhdG9yLmNsaXBib2FyZC53cml0ZVRleHQpewogICAgICBuYXZpZ2F0b3IuY2xpcGJvYXJkLndyaXRlVGV4dCh0ZXh0KS50aGVuKGRvbmUsICgpPT5mYWxsYmFja0NvcHkodGV4dCwgZG9uZSkpOwogICAgfSBlbHNlIHsKICAgICAgZmFsbGJhY2tDb3B5KHRleHQsIGRvbmUpOwogICAgfQogIH1jYXRjaChlKXsgZmFsbGJhY2tDb3B5KHRleHQsIGRvbmUpOyB9Cn0KZnVuY3Rpb24gZmFsbGJhY2tDb3B5KHRleHQsIGRvbmUpewogIHRyeXsKICAgIGNvbnN0IHRhID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgidGV4dGFyZWEiKTsKICAgIHRhLnZhbHVlID0gdGV4dDsgdGEuc3R5bGUucG9zaXRpb249ImZpeGVkIjsgdGEuc3R5bGUub3BhY2l0eT0iMCI7CiAgICBkb2N1bWVudC5ib2R5LmFwcGVuZENoaWxkKHRhKTsgdGEuZm9jdXMoKTsgdGEuc2VsZWN0KCk7CiAgICBkb2N1bWVudC5leGVjQ29tbWFuZCgiY29weSIpOwogICAgZG9jdW1lbnQuYm9keS5yZW1vdmVDaGlsZCh0YSk7CiAgICBkb25lICYmIGRvbmUoKTsKICB9Y2F0Y2goZSl7IC8qIHN0aWxsICovIH0KfQoKLy8gSW5zdGFsbGllcnRlcyBNb2RlbGwgd8OkaGxlbiAtPiBzZXR6ZW4sIFN0YXR1cyBuZXUgbGFkZW4sIEthcnRlIGF1c2JsZW5kZW4KYXN5bmMgZnVuY3Rpb24gcGlja09sbGFtYU1vZGVsKG5hbWUsIGJ0bil7CiAgY29uc3Qgc3RhdGVFbCA9IHNldHVwQ2FyZEVsID8gc2V0dXBDYXJkRWwucXVlcnlTZWxlY3RvcigiI3NjLXN0YXRlIikgOiBudWxsOwogIGlmIChidG4pIGJ0bi5kaXNhYmxlZCA9IHRydWU7CiAgaWYgKHN0YXRlRWwpIHN0YXRlRWwudGV4dENvbnRlbnQgPSAic2V0emUgTW9kZWxsIOKApiI7CiAgdHJ5ewogICAgY29uc3QgciA9IGF3YWl0IGFwaSgiL2FwaS9zZXR0aW5ncyIsICJQT1NUIiwgeyBvbGxhbWFfbW9kZWw6IG5hbWUgfSk7CiAgICBpZiAociAmJiByLmVycm9yKXsKICAgICAgaWYgKHN0YXRlRWwpIHN0YXRlRWwudGV4dENvbnRlbnQgPSAi4pqgICIgKyByLmVycm9yOwogICAgICBpZiAoYnRuKSBidG4uZGlzYWJsZWQgPSBmYWxzZTsKICAgICAgcmV0dXJuOwogICAgfQogICAgcmVtb3ZlU2V0dXBDYXJkKCk7CiAgICBhd2FpdCBsb2FkU3RhdHVzKCk7ICAgICAgICAgIC8vIGzDpGR0IFN0YXR1cyArIE9sbGFtYSBuZXUsIGJlZ3LDvMOfdCBiZWkgRXJmb2xnCiAgfWNhdGNoKGUpewogICAgaWYgKHN0YXRlRWwpIHN0YXRlRWwudGV4dENvbnRlbnQgPSAi4pqgICIgKyBlLm1lc3NhZ2U7CiAgICBpZiAoYnRuKSBidG4uZGlzYWJsZWQgPSBmYWxzZTsKICB9Cn0KCi8vICJOb2NobWFsIHByw7xmZW4iIOKAlCByb2J1c3QsIGtlaW4gRGF1ZXItUG9sbGluZwphc3luYyBmdW5jdGlvbiByZWNoZWNrT2xsYW1hKCl7CiAgaWYgKCFzZXR1cENhcmRFbCkgcmV0dXJuOwogIGNvbnN0IHJlY2hlY2tCdG4gPSBzZXR1cENhcmRFbC5xdWVyeVNlbGVjdG9yKCIjc2MtcmVjaGVjayIpOwogIGNvbnN0IHN0YXRlRWwgPSBzZXR1cENhcmRFbC5xdWVyeVNlbGVjdG9yKCIjc2Mtc3RhdGUiKTsKICBpZiAocmVjaGVja0J0bikgcmVjaGVja0J0bi5kaXNhYmxlZCA9IHRydWU7CiAgaWYgKHN0YXRlRWwpIHN0YXRlRWwudGV4dENvbnRlbnQgPSAicHLDvGZlIOKApiI7CiAgbGV0IG87CiAgdHJ5ewogICAgbyA9IGF3YWl0IGFwaSgiL2FwaS9vbGxhbWEiKTsKICB9Y2F0Y2goZSl7CiAgICBpZiAoc3RhdGVFbCkgc3RhdGVFbC50ZXh0Q29udGVudCA9ICJOb2NoIG5pY2h0IGVycmVpY2hiYXIg4oCUIHN0YXJ0ZSBPbGxhbWEgdW5kIHZlcnN1Y2gncyBnbGVpY2ggbm9jaG1hbC4iOwogICAgaWYgKHJlY2hlY2tCdG4pIHJlY2hlY2tCdG4uZGlzYWJsZWQgPSBmYWxzZTsKICAgIHNldE9sbGFtYVBpbGwoImJhZCIsICJTZXR1cCBuw7Z0aWciKTsKICAgIHJldHVybjsKICB9CiAgaWYgKG8gJiYgby5lcnJvcil7CiAgICBpZiAoc3RhdGVFbCkgc3RhdGVFbC50ZXh0Q29udGVudCA9ICLimqAgIiArIG8uZXJyb3I7CiAgICBpZiAocmVjaGVja0J0bikgcmVjaGVja0J0bi5kaXNhYmxlZCA9IGZhbHNlOwogICAgcmV0dXJuOwogIH0KCiAgY29uc3QgcnVubmluZyA9ICEhKG8gJiYgby5ydW5uaW5nKTsKICBjb25zdCBtb2RlbHMgPSAobyAmJiBBcnJheS5pc0FycmF5KG8ubW9kZWxzKSkgPyBvLm1vZGVscyA6IFtdOwogIGNvbnN0IGN1cnJlbnQgPSAobyAmJiBvLmN1cnJlbnRfbW9kZWwpIHx8IE9MTEFNQV9ERUZBVUxUX01PREVMOwogIGNvbnN0IGhhc01vZGVsID0gbW9kZWxJbnN0YWxsZWQobW9kZWxzLCBjdXJyZW50KTsKCiAgaWYgKHJ1bm5pbmcgJiYgaGFzTW9kZWwpewogICAgc2V0T2xsYW1hUGlsbCgib2siLCAibG9rYWwgYWt0aXYiKTsKICAgIHJlbW92ZVNldHVwQ2FyZCgpOwogICAgc3RhdGUucmVhZHkgPSB0cnVlOwogICAgYWRkQnViYmxlKCJkaW5vIiwgYERpbm8gaXN0IG9ubGluZSwgJHtzdGF0ZS51c2VyTmFtZX0hIFdvcmF1ZiBoYXN0IGR1IEJvY2s/IOKaoWApOwogICAgcmV0dXJuOwogIH0KCiAgLy8gTm9jaCBuaWNodCBmZXJ0aWcgLT4gS2FydGUgcGFzc2VuZCBha3R1YWxpc2llcmVuCiAgaWYgKCFydW5uaW5nKXsKICAgIHNldE9sbGFtYVBpbGwoImJhZCIsICJTZXR1cCBuw7Z0aWciKTsKICAgIHNob3dTZXR1cENhcmQoIm5vdC1ydW5uaW5nIiwgeyBtb2RlbHMsIGN1cnJlbnQgfSk7CiAgfSBlbHNlIHsKICAgIHNldE9sbGFtYVBpbGwoIndhcm4iLCAiTW9kZWxsIGZlaGx0Iik7CiAgICBzaG93U2V0dXBDYXJkKCJuby1tb2RlbCIsIHsgbW9kZWxzLCBjdXJyZW50IH0pOwogIH0KICBjb25zdCBucyA9IHNldHVwQ2FyZEVsID8gc2V0dXBDYXJkRWwucXVlcnlTZWxlY3RvcigiI3NjLXN0YXRlIikgOiBudWxsOwogIGlmIChucykgbnMudGV4dENvbnRlbnQgPSBydW5uaW5nID8gIkzDpHVmdCDigJQgYWJlciBlcyBmZWhsdCBub2NoIGRhcyBNb2RlbGwuIiA6ICJPbGxhbWEgbMOkdWZ0IG5vY2ggbmljaHQuIjsKfQoKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09Ci8vICBDaGF0IHNlbmRlbgovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KYXN5bmMgZnVuY3Rpb24gc2VuZCgpewogIGlmIChzdGF0ZS5idXN5KSByZXR1cm47CiAgY29uc3QgdGV4dCA9IGlucHV0RWwudmFsdWUudHJpbSgpOwogIGlmICghdGV4dCkgcmV0dXJuOwogIGlucHV0RWwudmFsdWUgPSAiIjsgYXV0b0dyb3coKTsKCiAgYWRkQnViYmxlKCJ1c2VyIiwgdGV4dCk7CiAgc3RhdGUubWVzc2FnZXMucHVzaCh7IHJvbGU6InVzZXIiLCBjb250ZW50OnRleHQgfSk7CgogIHNldEJ1c3kodHJ1ZSk7CiAgdHJ5ewogICAgY29uc3QgZGF0YSA9IGF3YWl0IGFwaSgiL2FwaS9jaGF0IiwgIlBPU1QiLCB7IG1lc3NhZ2VzOiBzdGF0ZS5tZXNzYWdlcyB9KTsKICAgIGhpZGVUeXBpbmcoKTsKICAgIGlmIChkYXRhLmVycm9yKXsKICAgICAgYWRkQnViYmxlKCJlcnJvciIsIGRhdGEuZXJyb3IpOwogICAgICAvLyBsZXR6dGUgTnV0emVyLU5hY2hyaWNodCBuaWNodCBkYXVlcmhhZnQgYmVoYWx0ZW4KICAgICAgc3RhdGUubWVzc2FnZXMucG9wKCk7CiAgICB9IGVsc2UgewogICAgICBjb25zdCByZXBseSA9IGRhdGEucmVwbHkgfHwgIiI7CiAgICAgIGFkZEJ1YmJsZSgiZGlubyIsIHJlcGx5KTsKICAgICAgc3RhdGUubWVzc2FnZXMucHVzaCh7IHJvbGU6ImFzc2lzdGFudCIsIGNvbnRlbnQ6cmVwbHkgfSk7CiAgICAgIHNwZWFrKHJlcGx5KTsKICAgIH0KICB9Y2F0Y2goZSl7CiAgICBoaWRlVHlwaW5nKCk7CiAgICBhZGRCdWJibGUoImVycm9yIiwgIk5ldHp3ZXJrZmVobGVyOiAiK2UubWVzc2FnZSk7CiAgICBzdGF0ZS5tZXNzYWdlcy5wb3AoKTsKICB9ZmluYWxseXsKICAgIHNldEJ1c3koZmFsc2UpOwogICAgaW5wdXRFbC5mb2N1cygpOwogIH0KfQoKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09Ci8vICBRdWljay1BY3Rpb25zCi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQovLyBHZW5lcmlzY2hlciBIZWxmZXIgZsO8ciAvcGxhbiB1bmQgL3RhZyAoQm9keSB7fSAtPiB7dGV4dH0pCmFzeW5jIGZ1bmN0aW9uIHNpbXBsZUFjdGlvbihwYXRoKXsKICBpZiAoc3RhdGUuYnVzeSkgcmV0dXJuOwogIHNldEJ1c3kodHJ1ZSk7CiAgdHJ5ewogICAgY29uc3QgZGF0YSA9IGF3YWl0IGFwaShwYXRoLCAiUE9TVCIsIHt9KTsKICAgIGhpZGVUeXBpbmcoKTsKICAgIGlmIChkYXRhLmVycm9yKSBhZGRCdWJibGUoImVycm9yIiwgZGF0YS5lcnJvcik7CiAgICBlbHNlewogICAgICBjb25zdCB0eHQgPSBkYXRhLnRleHQgfHwgIiI7CiAgICAgIGFkZEJ1YmJsZSgiZGlubyIsIHR4dCk7CiAgICAgIHN0YXRlLm1lc3NhZ2VzLnB1c2goeyByb2xlOiJhc3Npc3RhbnQiLCBjb250ZW50OnR4dCB9KTsKICAgICAgc3BlYWsodHh0KTsKICAgIH0KICB9Y2F0Y2goZSl7IGhpZGVUeXBpbmcoKTsgYWRkQnViYmxlKCJlcnJvciIsIk5ldHp3ZXJrZmVobGVyOiAiK2UubWVzc2FnZSk7IH0KICBmaW5hbGx5eyBzZXRCdXN5KGZhbHNlKTsgfQp9CmZ1bmN0aW9uIHF1aWNrUGxhbigpeyBzaW1wbGVBY3Rpb24oIi9hcGkvcGxhbiIpOyB9CmZ1bmN0aW9uIHF1aWNrVG9kYXkoKXsgc2ltcGxlQWN0aW9uKCIvYXBpL3RhZyIpOyB9CgovLyBMZXJuZW4gLT4gdmVyZGljaHRldCBHZXNwcsOkY2ggenUgRmFrdGVuCmFzeW5jIGZ1bmN0aW9uIHF1aWNrTGVhcm4oKXsKICBpZiAoc3RhdGUuYnVzeSkgcmV0dXJuOwogIGlmICghc3RhdGUubWVzc2FnZXMubGVuZ3RoKXsgYWRkQnViYmxlKCJpbmZvIiwiV2lyIGhhYmVuIG5vY2ggbmljaHQgZ2VyZWRldCDigJQgbmljaHRzIHp1IGxlcm5lbi4g8J+YiSIpOyByZXR1cm47IH0KICBzZXRCdXN5KHRydWUpOwogIHRyeXsKICAgIGNvbnN0IGRhdGEgPSBhd2FpdCBhcGkoIi9hcGkvbGVhcm4iLCAiUE9TVCIsIHsgbWVzc2FnZXM6IHN0YXRlLm1lc3NhZ2VzIH0pOwogICAgaGlkZVR5cGluZygpOwogICAgaWYgKGRhdGEuZXJyb3IpIGFkZEJ1YmJsZSgiZXJyb3IiLCBkYXRhLmVycm9yKTsKICAgIGVsc2UgYWRkQnViYmxlKCJpbmZvIiwgYEdlbWVya3QhIERpbm8ga2VubnQgamV0enQgJHtkYXRhLmNvdW50ID8/IDB9IEZha3Rlbi4g8J+noGApOwogIH1jYXRjaChlKXsgaGlkZVR5cGluZygpOyBhZGRCdWJibGUoImVycm9yIiwiTmV0endlcmtmZWhsZXI6ICIrZS5tZXNzYWdlKTsgfQogIGZpbmFsbHl7IHNldEJ1c3koZmFsc2UpOyB9Cn0KCi8vIFJhdCBkZXIgS0lzIC0+IG5pbW10IGFrdHVlbGxlbiBFaW5nYWJldGV4dCBhbHMgRnJhZ2UKYXN5bmMgZnVuY3Rpb24gcXVpY2tDb3VuY2lsKCl7CiAgaWYgKHN0YXRlLmJ1c3kpIHJldHVybjsKICBjb25zdCBmcmFnZSA9IGlucHV0RWwudmFsdWUudHJpbSgpOwogIGlmICghZnJhZ2UpeyBhZGRCdWJibGUoImluZm8iLCJTY2hyZWliIHp1ZXJzdCBkZWluZSBGcmFnZSBpbnMgRmVsZCwgZGFubiDCu1JhdCBkZXIgS0lzwqsuIPCfp6AiKTsgcmV0dXJuOyB9CiAgaW5wdXRFbC52YWx1ZT0iIjsgYXV0b0dyb3coKTsKICBhZGRCdWJibGUoInVzZXIiLCBmcmFnZSk7CgogIHNldEJ1c3kodHJ1ZSk7CiAgdHJ5ewogICAgY29uc3QgZGF0YSA9IGF3YWl0IGFwaSgiL2FwaS9jb3VuY2lsIiwgIlBPU1QiLCB7IG1lc3NhZ2VzOiBzdGF0ZS5tZXNzYWdlcywgZnJhZ2UgfSk7CiAgICBoaWRlVHlwaW5nKCk7CiAgICBpZiAoZGF0YS5lcnJvcil7IGFkZEJ1YmJsZSgiZXJyb3IiLCBkYXRhLmVycm9yKTsgc2V0QnVzeShmYWxzZSk7IHJldHVybjsgfQogICAgY29uc3QgYW5zd2VycyA9IGRhdGEuYW5zd2VycyB8fCB7fTsKICAgIC8vIFJlaWhlbmZvbGdlOiBDbGF1ZGUsIENoYXRHUFQsIEdlbWluaSAoZmFsbHMgdm9yaGFuZGVuKQogICAgWyJDbGF1ZGUiLCJDaGF0R1BUIiwiR2VtaW5pIl0uZm9yRWFjaChuYW1lPT57CiAgICAgIGlmIChhbnN3ZXJzW25hbWVdICE9IG51bGwpIGFkZEJ1YmJsZSgiY291bmNpbCIsIGFuc3dlcnNbbmFtZV0sICLilrggIituYW1lKTsKICAgIH0pOwogICAgLy8gZXZ0bC4gd2VpdGVyZSB1bmJla2FubnRlIFNjaGzDvHNzZWwKICAgIE9iamVjdC5rZXlzKGFuc3dlcnMpLmZvckVhY2gobmFtZT0+ewogICAgICBpZiAoIVsiQ2xhdWRlIiwiQ2hhdEdQVCIsIkdlbWluaSJdLmluY2x1ZGVzKG5hbWUpKSBhZGRCdWJibGUoImNvdW5jaWwiLCBhbnN3ZXJzW25hbWVdLCAi4pa4ICIrbmFtZSk7CiAgICB9KTsKICAgIGlmIChkYXRhLnN5bnRoZXNlKXsKICAgICAgYWRkQnViYmxlKCJzeW50aCIsIGRhdGEuc3ludGhlc2UsICLinKYgRGlub3MgRmF6aXQiKTsKICAgICAgc3RhdGUubWVzc2FnZXMucHVzaCh7IHJvbGU6ImFzc2lzdGFudCIsIGNvbnRlbnQ6ZGF0YS5zeW50aGVzZSB9KTsKICAgICAgc3BlYWsoZGF0YS5zeW50aGVzZSk7CiAgICB9CiAgfWNhdGNoKGUpeyBoaWRlVHlwaW5nKCk7IGFkZEJ1YmJsZSgiZXJyb3IiLCJOZXR6d2Vya2ZlaGxlcjogIitlLm1lc3NhZ2UpOyB9CiAgZmluYWxseXsgc2V0QnVzeShmYWxzZSk7IH0KfQoKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09Ci8vICBFaW5nYWJlZmVsZDogQXV0by1Hcm93ICsgVGFzdGF0dXIKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09CmZ1bmN0aW9uIGF1dG9Hcm93KCl7CiAgaW5wdXRFbC5zdHlsZS5oZWlnaHQgPSAiYXV0byI7CiAgaW5wdXRFbC5zdHlsZS5oZWlnaHQgPSBNYXRoLm1pbihpbnB1dEVsLnNjcm9sbEhlaWdodCwgMTQwKSArICJweCI7Cn0KaW5wdXRFbC5hZGRFdmVudExpc3RlbmVyKCJpbnB1dCIsIGF1dG9Hcm93KTsKaW5wdXRFbC5hZGRFdmVudExpc3RlbmVyKCJrZXlkb3duIiwgKGUpPT57CiAgaWYgKGUua2V5ID09PSAiRW50ZXIiICYmICFlLnNoaWZ0S2V5KXsgZS5wcmV2ZW50RGVmYXVsdCgpOyBzZW5kKCk7IH0KfSk7CgovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KLy8gIFNwcmFjaGF1c2dhYmUgKHNwZWVjaFN5bnRoZXNpcykKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09CmxldCBhbGxWb2ljZXMgPSBbXTsKbGV0IHNlbGVjdGVkVm9pY2UgPSBudWxsOwoKLy8gV2llICJHaWRlb24iIChicml0aXNjaCwgd2VpYmxpY2gpIGlzdCBlaW5lIFN0aW1tZT8gSG9laGVyID0gbmFlaGVyLgpmdW5jdGlvbiBnaWRlb25SYW5rKHYpewogIGNvbnN0IGxhbmcgPSAodi5sYW5nIHx8ICIiKS50b0xvd2VyQ2FzZSgpLnJlcGxhY2UoIl8iLCAiLSIpOwogIGNvbnN0IG5hbWUgPSAodi5uYW1lIHx8ICIiKS50b0xvd2VyQ2FzZSgpOwogIGxldCBzID0gMDsKICBpZiAobGFuZy5zdGFydHNXaXRoKCJlbi1nYiIpKSBzICs9IDEwMDsgICAgICAgICAgLy8gYnJpdGlzY2hlcyBFbmdsaXNjaAogIGVsc2UgaWYgKGxhbmcuc3RhcnRzV2l0aCgiZW4iKSkgcyArPSA0NTsgICAgICAgICAgLy8gc29uc3QgRW5nbGlzY2gKICBpZiAoL2ZlbWFsZXxzb25pYXxsaWJieXxoYXplbHxzdXNhbnxtYWlzaWV8b2xpdmlhfGFyaWF8amVubnl8ZW1tYXxjaGFybG90dGV8YW15fGdvb2dsZSB1ayBlbmdsaXNoIGZlbWFsZS8udGVzdChuYW1lKSkgcyArPSA1NTsKICBpZiAoL25hdHVyYWx8b25saW5lfG5ldXJhbC8udGVzdChuYW1lKSkgcyArPSAxMjsgIC8vIG5hdHVlcmxpY2hlcmUgRWRnZS1TdGltbWVuCiAgcmV0dXJuIHM7Cn0KCmZ1bmN0aW9uIGJ1aWxkVm9pY2VMaXN0KCl7CiAgaWYgKCEoInNwZWVjaFN5bnRoZXNpcyIgaW4gd2luZG93KSkgcmV0dXJuOwogIGFsbFZvaWNlcyA9IHNwZWVjaFN5bnRoZXNpcy5nZXRWb2ljZXMoKSB8fCBbXTsKICBpZiAoIWFsbFZvaWNlcy5sZW5ndGgpIHJldHVybjsKICBjb25zdCBzb3J0ZWQgPSBhbGxWb2ljZXMuc2xpY2UoKS5zb3J0KChhLGIpID0+IGdpZGVvblJhbmsoYikgLSBnaWRlb25SYW5rKGEpKTsKICBjb25zdCBzZWwgPSAkKCJ2b2ljZVNlbGVjdCIpOwogIGlmIChzZWwpewogICAgc2VsLmlubmVySFRNTCA9ICIiOwogICAgc29ydGVkLmZvckVhY2godiA9PiB7CiAgICAgIGNvbnN0IG8gPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJvcHRpb24iKTsKICAgICAgby52YWx1ZSA9IHYudm9pY2VVUkk7CiAgICAgIG8udGV4dENvbnRlbnQgPSB2Lm5hbWUgKyAiICgiICsgdi5sYW5nICsgIikiOwogICAgICBzZWwuYXBwZW5kQ2hpbGQobyk7CiAgICB9KTsKICB9CiAgY29uc3Qgc2F2ZWQgPSBsb2NhbFN0b3JhZ2UuZ2V0SXRlbSgiZGlub192b2ljZSIpOwogIHNlbGVjdGVkVm9pY2UgPSAoc2F2ZWQgJiYgYWxsVm9pY2VzLmZpbmQodiA9PiB2LnZvaWNlVVJJID09PSBzYXZlZCkpIHx8IHNvcnRlZFswXSB8fCBudWxsOwogIGlmIChzZWwgJiYgc2VsZWN0ZWRWb2ljZSkgc2VsLnZhbHVlID0gc2VsZWN0ZWRWb2ljZS52b2ljZVVSSTsKfQoKZnVuY3Rpb24gb25Wb2ljZVNlbGVjdCgpewogIGNvbnN0IHNlbCA9ICQoInZvaWNlU2VsZWN0Iik7CiAgc2VsZWN0ZWRWb2ljZSA9IGFsbFZvaWNlcy5maW5kKHYgPT4gdi52b2ljZVVSSSA9PT0gc2VsLnZhbHVlKSB8fCBudWxsOwogIGlmIChzZWxlY3RlZFZvaWNlKSBsb2NhbFN0b3JhZ2Uuc2V0SXRlbSgiZGlub192b2ljZSIsIHNlbGVjdGVkVm9pY2Uudm9pY2VVUkkpOwogIC8vIGt1cnplIEhvZXItUHJvYmUKICBjb25zdCBwcmV2ID0gc3RhdGUudm9pY2VPbjsgc3RhdGUudm9pY2VPbiA9IHRydWU7CiAgc3BlYWsoIkhhbGxvLCBpY2ggYmluIERpbm8uIik7CiAgc3RhdGUudm9pY2VPbiA9IHByZXY7Cn0KCmlmICgic3BlZWNoU3ludGhlc2lzIiBpbiB3aW5kb3cpewogIGJ1aWxkVm9pY2VMaXN0KCk7CiAgc3BlZWNoU3ludGhlc2lzLm9udm9pY2VzY2hhbmdlZCA9IGJ1aWxkVm9pY2VMaXN0Owp9IGVsc2UgewogICQoInZvaWNlQnRuIikuc3R5bGUuZGlzcGxheSA9ICJub25lIjsKICBjb25zdCB2cyA9ICQoInZvaWNlU2VsZWN0Iik7IGlmICh2cykgdnMuc3R5bGUuZGlzcGxheSA9ICJub25lIjsKfQoKZnVuY3Rpb24gdG9nZ2xlVm9pY2UoKXsKICBzdGF0ZS52b2ljZU9uID0gIXN0YXRlLnZvaWNlT247CiAgJCgidm9pY2VCdG4iKS5jbGFzc0xpc3QudG9nZ2xlKCJhY3RpdmUiLCBzdGF0ZS52b2ljZU9uKTsKICBpZiAoIXN0YXRlLnZvaWNlT24gJiYgInNwZWVjaFN5bnRoZXNpcyIgaW4gd2luZG93KXsgc3BlZWNoU3ludGhlc2lzLmNhbmNlbCgpOyByZXR1cm47IH0KICBpZiAoc3RhdGUudm9pY2VPbikgc3BlYWsoIlNwcmFjaGF1c2dhYmUgYWt0aXYuIik7ICAvLyBHaWRlb24gbWVsZGV0IHNpY2gKfQoKZnVuY3Rpb24gc3BlYWsodGV4dCl7CiAgaWYgKCFzdGF0ZS52b2ljZU9uIHx8ICF0ZXh0IHx8ICEoInNwZWVjaFN5bnRoZXNpcyIgaW4gd2luZG93KSkgcmV0dXJuOwogIHRyeXsKICAgIHNwZWVjaFN5bnRoZXNpcy5jYW5jZWwoKTsKICAgIGNvbnN0IHUgPSBuZXcgU3BlZWNoU3ludGhlc2lzVXR0ZXJhbmNlKHRleHQpOwogICAgaWYgKHNlbGVjdGVkVm9pY2UpeyB1LnZvaWNlID0gc2VsZWN0ZWRWb2ljZTsgdS5sYW5nID0gc2VsZWN0ZWRWb2ljZS5sYW5nOyB9CiAgICBlbHNlIHsgdS5sYW5nID0gImRlLURFIjsgfQogICAgdS5yYXRlID0gMS4wOwogICAgdS5waXRjaCA9IDEuMDY7ICAgLy8gbGVpY2h0IGhvZWhlciAtPiBrbGluZ3QgbWVociBuYWNoIEtJLUFzc2lzdGVudGluCiAgICB1Lm9uc3RhcnQgPSAoKT0+IHNldFNwZWFraW5nKHRydWUpOwogICAgdS5vbmVuZCAgID0gKCk9PiBzZXRTcGVha2luZyhmYWxzZSk7CiAgICB1Lm9uZXJyb3IgPSAoKT0+IHNldFNwZWFraW5nKGZhbHNlKTsKICAgIHNwZWVjaFN5bnRoZXNpcy5zcGVhayh1KTsKICB9Y2F0Y2goZSl7IC8qIHN0aWxsICovIH0KfQoKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09Ci8vICBTcHJhY2hlcmtlbm51bmcgKFNwZWVjaFJlY29nbml0aW9uKQovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KbGV0IHJlY29nID0gbnVsbCwgbGlzdGVuaW5nID0gZmFsc2U7CihmdW5jdGlvbiBpbml0TWljKCl7CiAgY29uc3QgU1IgPSB3aW5kb3cuU3BlZWNoUmVjb2duaXRpb24gfHwgd2luZG93LndlYmtpdFNwZWVjaFJlY29nbml0aW9uOwogIGlmICghU1IpeyAkKCJtaWNCdG4iKS5zdHlsZS5kaXNwbGF5ID0gIm5vbmUiOyByZXR1cm47IH0gLy8gbmljaHQgdW50ZXJzdMO8dHp0IC0+IGVsZWdhbnQgYXVzYmxlbmRlbgogIHJlY29nID0gbmV3IFNSKCk7CiAgcmVjb2cubGFuZyA9ICJkZS1ERSI7CiAgcmVjb2cuaW50ZXJpbVJlc3VsdHMgPSBmYWxzZTsKICByZWNvZy5tYXhBbHRlcm5hdGl2ZXMgPSAxOwogIHJlY29nLm9ucmVzdWx0ID0gKGUpPT57CiAgICBjb25zdCB0ID0gZS5yZXN1bHRzWzBdWzBdLnRyYW5zY3JpcHQ7CiAgICBpbnB1dEVsLnZhbHVlID0gKGlucHV0RWwudmFsdWUgPyBpbnB1dEVsLnZhbHVlKyIgIiA6ICIiKSArIHQ7CiAgICBhdXRvR3JvdygpOyBpbnB1dEVsLmZvY3VzKCk7CiAgfTsKICByZWNvZy5vbmVycm9yID0gKCk9PiBzdG9wTWljKCk7CiAgcmVjb2cub25lbmQgPSAoKT0+IHN0b3BNaWMoKTsKfSkoKTsKZnVuY3Rpb24gdG9nZ2xlTWljKCl7CiAgaWYgKCFyZWNvZykgcmV0dXJuOwogIGlmIChsaXN0ZW5pbmcpeyByZWNvZy5zdG9wKCk7IHN0b3BNaWMoKTsgfQogIGVsc2UgeyB0cnl7IHJlY29nLnN0YXJ0KCk7IGxpc3RlbmluZyA9IHRydWU7ICQoIm1pY0J0biIpLmNsYXNzTGlzdC5hZGQoImxpc3RlbmluZyIpOyB9Y2F0Y2goZSl7IHN0b3BNaWMoKTsgfSB9Cn0KZnVuY3Rpb24gc3RvcE1pYygpeyBsaXN0ZW5pbmcgPSBmYWxzZTsgJCgibWljQnRuIikuY2xhc3NMaXN0LnJlbW92ZSgibGlzdGVuaW5nIik7IH0KCi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQovLyAgUGFuZWxzIChTbGlkZS1PdmVyKQovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KZnVuY3Rpb24gb3BlblBhbmVsKG5hbWUpewogIGNsb3NlUGFuZWxzKCk7CiAgJCgib3ZlcmxheSIpLmNsYXNzTGlzdC5hZGQoIm9wZW4iKTsKICBjb25zdCBwID0gJCgicGFuZWwtIituYW1lKTsKICBpZiAocCkgcC5jbGFzc0xpc3QuYWRkKCJvcGVuIik7CiAgaWYgKG5hbWUgPT09ICJzZXR0aW5ncyIpIGxvYWRTZXR0aW5ncygpOwogIGlmIChuYW1lID09PSAiY3VzdG9tZXJzIikgbG9hZEN1c3RvbWVycygpOwogIGlmIChuYW1lID09PSAibWVtb3J5IikgbG9hZE1lbW9yeSgpOwp9CmZ1bmN0aW9uIGNsb3NlUGFuZWxzKCl7CiAgJCgib3ZlcmxheSIpLmNsYXNzTGlzdC5yZW1vdmUoIm9wZW4iKTsKICBkb2N1bWVudC5xdWVyeVNlbGVjdG9yQWxsKCIucGFuZWwiKS5mb3JFYWNoKHAgPT4gcC5jbGFzc0xpc3QucmVtb3ZlKCJvcGVuIikpOwp9CmRvY3VtZW50LmFkZEV2ZW50TGlzdGVuZXIoImtleWRvd24iLCBlID0+IHsgaWYgKGUua2V5ID09PSAiRXNjYXBlIikgY2xvc2VQYW5lbHMoKTsgfSk7CgovLyAtLS0tLS0tLS0tIEVpbnN0ZWxsdW5nZW4gLS0tLS0tLS0tLQphc3luYyBmdW5jdGlvbiBsb2FkU2V0dGluZ3MoKXsKICBjb25zdCBib2R5ID0gJCgic2V0dGluZ3NCb2R5Iik7CiAgYm9keS5pbm5lckhUTUwgPSAnPGRpdiBjbGFzcz0iZW1wdHkiPmzDpGR04oCmPC9kaXY+JzsKICBsZXQgczsKICB0cnkgeyBzID0gYXdhaXQgYXBpKCIvYXBpL3NldHRpbmdzIik7IH0KICBjYXRjaChlKXsgYm9keS5pbm5lckhUTUwgPSAiIjsgYm9keS5hcHBlbmRDaGlsZChlcnJCb3goIktvbm50ZSBFaW5zdGVsbHVuZ2VuIG5pY2h0IGxhZGVuOiAiK2UubWVzc2FnZSkpOyByZXR1cm47IH0KICBpZiAocy5lcnJvcil7IGJvZHkuaW5uZXJIVE1MPSIiOyBib2R5LmFwcGVuZENoaWxkKGVyckJveChzLmVycm9yKSk7IHJldHVybjsgfQoKICBjb25zdCBrZXlzID0gcy5rZXlzIHx8IHt9OwogIGNvbnN0IHBlcnNvbmEgPSBzLnBlcnNvbmEgfHwge307CiAgY29uc3QgY2xhdWRlTW9kZWxzID0gcy5jbGF1ZGVfbW9kZWxzIHx8IFtdOwoKICAvLyBDbGF1ZGUtTW9kZWxsLU9wdGlvbmVuCiAgY29uc3QgY21PcHRzID0gY2xhdWRlTW9kZWxzLm1hcChtID0+CiAgICBgPG9wdGlvbiB2YWx1ZT0iJHtlc2MobVswXSl9IiAke21bMF09PT1zLmNsYXVkZV9tb2RlbD8ic2VsZWN0ZWQiOiIifT4ke2VzYyhtWzFdKX08L29wdGlvbj5gKS5qb2luKCIiKTsKCiAgY29uc3QgcHJvdlNlbCA9IChwKT0+IGA8b3B0aW9uIHZhbHVlPSIke3B9IiAke3MucHJvdmlkZXI9PT1wPyJzZWxlY3RlZCI6IiJ9PmA7CgogIGJvZHkuaW5uZXJIVE1MID0gYAogICAgPGRpdiBjbGFzcz0ic2VjdCI+8J+UkSBBUEktU2NobMO8c3NlbDwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5DbGF1ZGUgKGVtcGZvaGxlbik8L2xhYmVsPjxpbnB1dCBpZD0ic3Qta2V5LWNsYXVkZSIgdHlwZT0icGFzc3dvcmQiIHBsYWNlaG9sZGVyPSJzay1hbnQt4oCmIj48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+Q2hhdEdQVCAvIE9wZW5BSTwvbGFiZWw+PGlucHV0IGlkPSJzdC1rZXktb3BlbmFpIiB0eXBlPSJwYXNzd29yZCIgcGxhY2Vob2xkZXI9InNrLeKApiI+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPkdvb2dsZSBHZW1pbmk8L2xhYmVsPjxpbnB1dCBpZD0ic3Qta2V5LWdlbWluaSIgdHlwZT0icGFzc3dvcmQiIHBsYWNlaG9sZGVyPSJBSXph4oCmIj48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImhpbnQiPlNjaGzDvHNzZWwgaG9sZW46IDxjb2RlPmNvbnNvbGUuYW50aHJvcGljLmNvbTwvY29kZT4gwrcgPGNvZGU+cGxhdGZvcm0ub3BlbmFpLmNvbS9hcGkta2V5czwvY29kZT4gwrcgPGNvZGU+YWlzdHVkaW8uZ29vZ2xlLmNvbS9hcGlrZXk8L2NvZGU+PGJyPlNpZSBibGVpYmVuIGxva2FsIGF1ZiBkZWluZW0gUEMuPC9kaXY+CgogICAgPGRpdiBjbGFzcz0ic2VjdCI+8J+noCBXZWxjaGVzIEdlaGlybj88L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+QW5iaWV0ZXI8L2xhYmVsPjxzZWxlY3QgaWQ9InN0LXByb3ZpZGVyIj4KICAgICAgJHtwcm92U2VsKCJjbGF1ZGUiKX1DbGF1ZGU8L29wdGlvbj4ke3Byb3ZTZWwoIm9sbGFtYSIpffCfhpMgR3JhdGlzIGxva2FsIChPbGxhbWEpPC9vcHRpb24+JHtwcm92U2VsKCJvcGVuYWkiKX1DaGF0R1BUIC8gT3BlbkFJPC9vcHRpb24+JHtwcm92U2VsKCJnZW1pbmkiKX1HZW1pbmk8L29wdGlvbj4KICAgIDwvc2VsZWN0PjwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5DbGF1ZGUtTW9kZWxsPC9sYWJlbD48c2VsZWN0IGlkPSJzdC1jbGF1ZGUtbW9kZWwiPiR7Y21PcHRzfTwvc2VsZWN0PjwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5PcGVuQUktTW9kZWxsPC9sYWJlbD48aW5wdXQgaWQ9InN0LW9wZW5haS1tb2RlbCIgcGxhY2Vob2xkZXI9InouQi4gZ3B0LTUuMSI+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPkdlbWluaS1Nb2RlbGw8L2xhYmVsPjxpbnB1dCBpZD0ic3QtZ2VtaW5pLW1vZGVsIiBwbGFjZWhvbGRlcj0iei5CLiBnZW1pbmktMi41LXBybyI+PC9kaXY+CgogICAgPGRpdiBjbGFzcz0ic2VjdCI+8J+GkyBHcmF0aXMgbG9rYWwgKE9sbGFtYSkg4oCUIG9obmUgU2NobMO8c3NlbDwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5HcmF0aXMtTW9kZWxsPC9sYWJlbD48aW5wdXQgaWQ9InN0LW9sbGFtYS1tb2RlbCIgcGxhY2Vob2xkZXI9InouQi4gbGxhbWEzLjIiPjwvZGl2PgogICAgPGRpdiBjbGFzcz0iaGludCI+S29tcGxldHQgZ3JhdGlzLCBvaG5lIFNjaGzDvHNzZWw6IGluc3RhbGxpZXJlIDxjb2RlPk9sbGFtYTwvY29kZT4gdm9uIDxjb2RlPm9sbGFtYS5jb208L2NvZGU+LCBkYW5uIGltIFRlcm1pbmFsIDxjb2RlPm9sbGFtYSBydW4gbGxhbWEzLjI8L2NvZGU+IGF1c2bDvGhyZW4gdW5kIG9iZW4gQW5iaWV0ZXIgPGI+8J+GkyBHcmF0aXMgbG9rYWw8L2I+IHfDpGhsZW4uIChTY2h3w6RjaGVyIGFscyBDbGF1ZGUsIGzDpHVmdCBkYWbDvHIgb2ZmbGluZSBhdWYgZGVpbmVtIFBDLik8L2Rpdj4KCiAgICA8ZGl2IGNsYXNzPSJzZWN0Ij7wn46tIFBlcnNvbmE8L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+TmFtZSBkZXIgS0k8L2xhYmVsPjxpbnB1dCBpZD0ic3QtYXNzaXN0YW50Ij48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+V2llIERpbm8gZGljaCBuZW5udDwvbGFiZWw+PGlucHV0IGlkPSJzdC11c2VyIj48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+RGVpbiBCdXNpbmVzczwvbGFiZWw+PHRleHRhcmVhIGlkPSJzdC1idXNpbmVzcyI+PC90ZXh0YXJlYT48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+U3RpbCAvIEh1bW9yPC9sYWJlbD48dGV4dGFyZWEgaWQ9InN0LWh1bW9yIj48L3RleHRhcmVhPjwvZGl2PgoKICAgIDxkaXYgY2xhc3M9InNlY3QiPvCfjq8gWmllbDwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjx0ZXh0YXJlYSBpZD0ic3QtZ29hbCI+PC90ZXh0YXJlYT48L2Rpdj4KCiAgICA8ZGl2IGNsYXNzPSJidG5yb3ciPgogICAgICA8YnV0dG9uIGNsYXNzPSJidG4gcHJpbWFyeSIgaWQ9InN0LXNhdmUiPvCfkr4gU3BlaWNoZXJuPC9idXR0b24+CiAgICAgIDxzcGFuIGlkPSJzdC1tc2ciIGNsYXNzPSJoaW50IiBzdHlsZT0iYWxpZ24tc2VsZjpjZW50ZXIiPjwvc3Bhbj4KICAgIDwvZGl2PgogIGA7CiAgLy8gV2VydGUgZWluc2V0emVuIChwZXIgLnZhbHVlLCBuaWNodCBpbiBpbm5lckhUTUwgLT4gc2ljaGVyKQogICQoInN0LWtleS1jbGF1ZGUiKS52YWx1ZSA9IGtleXMuY2xhdWRlIHx8ICIiOwogICQoInN0LWtleS1vcGVuYWkiKS52YWx1ZSA9IGtleXMub3BlbmFpIHx8ICIiOwogICQoInN0LWtleS1nZW1pbmkiKS52YWx1ZSA9IGtleXMuZ2VtaW5pIHx8ICIiOwogICQoInN0LW9wZW5haS1tb2RlbCIpLnZhbHVlID0gcy5vcGVuYWlfbW9kZWwgfHwgIiI7CiAgJCgic3QtZ2VtaW5pLW1vZGVsIikudmFsdWUgPSBzLmdlbWluaV9tb2RlbCB8fCAiIjsKICAkKCJzdC1vbGxhbWEtbW9kZWwiKS52YWx1ZSA9IHMub2xsYW1hX21vZGVsIHx8ICIiOwogICQoInN0LWFzc2lzdGFudCIpLnZhbHVlID0gcGVyc29uYS5hc3Npc3RhbnRfbmFtZSB8fCAiIjsKICAkKCJzdC11c2VyIikudmFsdWUgPSBwZXJzb25hLnVzZXJfbmFtZSB8fCAiIjsKICAkKCJzdC1idXNpbmVzcyIpLnZhbHVlID0gcGVyc29uYS5idXNpbmVzcyB8fCAiIjsKICAkKCJzdC1odW1vciIpLnZhbHVlID0gcGVyc29uYS5odW1vciB8fCAiIjsKICAkKCJzdC1nb2FsIikudmFsdWUgPSBzLmdvYWwgfHwgIiI7CgogICQoInN0LXNhdmUiKS5vbmNsaWNrID0gc2F2ZVNldHRpbmdzOwp9Cgphc3luYyBmdW5jdGlvbiBzYXZlU2V0dGluZ3MoKXsKICBjb25zdCBidG4gPSAkKCJzdC1zYXZlIik7IGJ0bi5kaXNhYmxlZCA9IHRydWU7CiAgY29uc3QgcGF5bG9hZCA9IHsKICAgIHByb3ZpZGVyOiAkKCJzdC1wcm92aWRlciIpLnZhbHVlLAogICAgY2xhdWRlX21vZGVsOiAkKCJzdC1jbGF1ZGUtbW9kZWwiKS52YWx1ZSwKICAgIG9wZW5haV9tb2RlbDogJCgic3Qtb3BlbmFpLW1vZGVsIikudmFsdWUudHJpbSgpLAogICAgZ2VtaW5pX21vZGVsOiAkKCJzdC1nZW1pbmktbW9kZWwiKS52YWx1ZS50cmltKCksCiAgICBvbGxhbWFfbW9kZWw6ICQoInN0LW9sbGFtYS1tb2RlbCIpLnZhbHVlLnRyaW0oKSwKICAgIGtleXM6IHsKICAgICAgY2xhdWRlOiAkKCJzdC1rZXktY2xhdWRlIikudmFsdWUudHJpbSgpLAogICAgICBvcGVuYWk6ICQoInN0LWtleS1vcGVuYWkiKS52YWx1ZS50cmltKCksCiAgICAgIGdlbWluaTogJCgic3Qta2V5LWdlbWluaSIpLnZhbHVlLnRyaW0oKSwKICAgIH0sCiAgICBwZXJzb25hOiB7CiAgICAgIGFzc2lzdGFudF9uYW1lOiAkKCJzdC1hc3Npc3RhbnQiKS52YWx1ZS50cmltKCksCiAgICAgIHVzZXJfbmFtZTogJCgic3QtdXNlciIpLnZhbHVlLnRyaW0oKSwKICAgICAgYnVzaW5lc3M6ICQoInN0LWJ1c2luZXNzIikudmFsdWUudHJpbSgpLAogICAgICBodW1vcjogJCgic3QtaHVtb3IiKS52YWx1ZS50cmltKCksCiAgICB9LAogICAgZ29hbDogJCgic3QtZ29hbCIpLnZhbHVlLnRyaW0oKSwKICB9OwogIGNvbnN0IG1zZyA9ICQoInN0LW1zZyIpOwogIHRyeXsKICAgIGNvbnN0IHIgPSBhd2FpdCBhcGkoIi9hcGkvc2V0dGluZ3MiLCAiUE9TVCIsIHBheWxvYWQpOwogICAgaWYgKHIuZXJyb3IpeyBtc2cudGV4dENvbnRlbnQgPSAi4pqgICIrci5lcnJvcjsgbXNnLnN0eWxlLmNvbG9yPSJ2YXIoLS1yb3NlKSI7IH0KICAgIGVsc2V7CiAgICAgIG1zZy50ZXh0Q29udGVudCA9ICJHZXNwZWljaGVydCDinJMiOyBtc2cuc3R5bGUuY29sb3I9InZhcigtLWdyZWVuKSI7CiAgICAgIGF3YWl0IGxvYWRTdGF0dXMoKTsgICAgICAgICAgICAvLyBTdGF0dXMgb2JlbiBuZXUgbGFkZW4gKGvDvG1tZXJ0IHNpY2ggdW0gQmVncsO8w591bmcvU2V0dXAtS2FydGUpCiAgICB9CiAgfWNhdGNoKGUpeyBtc2cudGV4dENvbnRlbnQgPSAi4pqgICIrZS5tZXNzYWdlOyBtc2cuc3R5bGUuY29sb3I9InZhcigtLXJvc2UpIjsgfQogIGZpbmFsbHl7IGJ0bi5kaXNhYmxlZCA9IGZhbHNlOyB9Cn0KCi8vIC0tLS0tLS0tLS0gS3VuZGVuIC0tLS0tLS0tLS0KYXN5bmMgZnVuY3Rpb24gbG9hZEN1c3RvbWVycygpewogIGNvbnN0IGJvZHkgPSAkKCJjdXN0b21lcnNCb2R5Iik7CiAgYm9keS5pbm5lckhUTUwgPSAnPGRpdiBjbGFzcz0iZW1wdHkiPmzDpGR04oCmPC9kaXY+JzsKICBsZXQgZDsKICB0cnkgeyBkID0gYXdhaXQgYXBpKCIvYXBpL2N1c3RvbWVycyIpOyB9CiAgY2F0Y2goZSl7IGJvZHkuaW5uZXJIVE1MPSIiOyBib2R5LmFwcGVuZENoaWxkKGVyckJveCgiS29ubnRlIEt1bmRlbiBuaWNodCBsYWRlbjogIitlLm1lc3NhZ2UpKTsgcmV0dXJuOyB9CiAgaWYgKGQuZXJyb3IpeyBib2R5LmlubmVySFRNTD0iIjsgYm9keS5hcHBlbmRDaGlsZChlcnJCb3goZC5lcnJvcikpOyByZXR1cm47IH0KICByZW5kZXJDdXN0b21lcnMoZCk7Cn0KCmZ1bmN0aW9uIHJlbmRlckN1c3RvbWVycyhkKXsKICBjb25zdCBib2R5ID0gJCgiY3VzdG9tZXJzQm9keSIpOwogIGJvZHkuaW5uZXJIVE1MID0gIiI7CiAgY29uc3QgciA9IGQucmV2ZW51ZSB8fCB7fTsKICBjb25zdCBjdXN0cyA9IGQuY3VzdG9tZXJzIHx8IFtdOwoKICAvLyBVbXNhdHotQmFubmVyCiAgY29uc3QgcmV2ID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7CiAgcmV2LmNsYXNzTmFtZSA9ICJyZXZlbnVlIjsKICByZXYuaW5uZXJIVE1MID0KICAgIGA8ZGl2IGNsYXNzPSJiaWciPiR7ZXVybyhyLm1vbnRobHkpfTwvZGl2PmArCiAgICBgPGRpdiBjbGFzcz0ic3ViIj5Nb25hdHN1bXNhdHogwrcgfiR7ZXVybyhyLndlZWtseSl9L1dvY2hlIMK3ICR7ci5hY3RpdmV8fDB9IGFrdGl2IMK3ICR7ci5sZWFkc3x8MH0gTGVhZHMgwrcgJHtyLnRvdGFsfHwwfSBnZXNhbXQ8L2Rpdj5gOwogIGJvZHkuYXBwZW5kQ2hpbGQocmV2KTsKCiAgLy8gIk5ldWVyIEt1bmRlIgogIGNvbnN0IG5ld0J0biA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImJ1dHRvbiIpOwogIG5ld0J0bi5jbGFzc05hbWUgPSAiYnRuIHByaW1hcnkiOyBuZXdCdG4uc3R5bGUubWFyZ2luQm90dG9tPSIxNHB4IjsgbmV3QnRuLnRleHRDb250ZW50ID0gIuKelSBOZXVlciBLdW5kZSI7CiAgbmV3QnRuLm9uY2xpY2sgPSAoKT0+IHNob3dDdXN0b21lckZvcm0obnVsbCk7CiAgYm9keS5hcHBlbmRDaGlsZChuZXdCdG4pOwoKICBpZiAoIWN1c3RzLmxlbmd0aCl7CiAgICBjb25zdCBlID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IGUuY2xhc3NOYW1lPSJlbXB0eSI7IGUudGV4dENvbnRlbnQ9Ik5vY2gga2VpbmUgS3VuZGVuLiBMZWcgZWluZW4gYW4uIPCfkaUiOwogICAgYm9keS5hcHBlbmRDaGlsZChlKTsKICAgIHJldHVybjsKICB9CiAgY3VzdHMuZm9yRWFjaChjID0+IGJvZHkuYXBwZW5kQ2hpbGQoY3VzdENhcmQoYykpKTsKfQoKZnVuY3Rpb24gY3VzdENhcmQoYyl7CiAgY29uc3QgY2FyZCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBjYXJkLmNsYXNzTmFtZSA9ICJjdXN0IjsKICBjb25zdCB0b3AgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgdG9wLmNsYXNzTmFtZT0idG9wIjsKICBjb25zdCBubSA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoInNwYW4iKTsgbm0uY2xhc3NOYW1lPSJuYW1lIjsgbm0udGV4dENvbnRlbnQgPSBjLm5hbWUgfHwgIuKAlCI7CiAgY29uc3QgYmQgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJzcGFuIik7IGJkLmNsYXNzTmFtZT0iYmFkZ2UiOyBiZC50ZXh0Q29udGVudCA9IGMuc3RhdHVzIHx8ICLigJQiOwogIHRvcC5hcHBlbmRDaGlsZChubSk7IHRvcC5hcHBlbmRDaGlsZChiZCk7IGNhcmQuYXBwZW5kQ2hpbGQodG9wKTsKCiAgY29uc3QgbWV0YSA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBtZXRhLmNsYXNzTmFtZT0ibWV0YSI7CiAgY29uc3QgcGFydHMgPSBbXTsKICBpZiAoYy5icmFuY2hlKSBwYXJ0cy5wdXNoKGMuYnJhbmNoZSk7CiAgaWYgKGMucGFrZXQpIHBhcnRzLnB1c2goYy5wYWtldCk7CiAgbWV0YS50ZXh0Q29udGVudCA9IHBhcnRzLmpvaW4oIiDCtyAiKTsKICBpZiAoYy5wcmVpcyl7CiAgICBjb25zdCBwID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgic3BhbiIpOyBwLmNsYXNzTmFtZT0icHJpY2UiOyBwLnRleHRDb250ZW50ID0gKHBhcnRzLmxlbmd0aD8iIMK3ICI6IiIpICsgZXVybyhjLnByZWlzKSsiL01vbmF0IjsKICAgIG1ldGEuYXBwZW5kQ2hpbGQocCk7CiAgfQogIGNhcmQuYXBwZW5kQ2hpbGQobWV0YSk7CgogIGlmIChjLm5hZWNoc3Rlcl9zY2hyaXR0KXsKICAgIGNvbnN0IG5zID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IG5zLmNsYXNzTmFtZT0ibWV0YSI7IG5zLnRleHRDb250ZW50ID0gIuKGkiAiICsgYy5uYWVjaHN0ZXJfc2Nocml0dDsKICAgIGNhcmQuYXBwZW5kQ2hpbGQobnMpOwogIH0KICBpZiAoYy5rb250YWt0KXsKICAgIGNvbnN0IGsgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgay5jbGFzc05hbWU9Im1ldGEiOyBrLnRleHRDb250ZW50ID0gIuKciSAiICsgYy5rb250YWt0OwogICAgY2FyZC5hcHBlbmRDaGlsZChrKTsKICB9CgogIGNvbnN0IGFjdCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBhY3QuY2xhc3NOYW1lPSJhY3Rpb25zIjsKICBjb25zdCBlZGl0ID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiYnV0dG9uIik7IGVkaXQuY2xhc3NOYW1lPSJidG4gc20iOyBlZGl0LnRleHRDb250ZW50PSLinI/vuI8gQmVhcmJlaXRlbiI7CiAgZWRpdC5vbmNsaWNrID0gKCk9PiBzaG93Q3VzdG9tZXJGb3JtKGMpOwogIGNvbnN0IGRlbCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImJ1dHRvbiIpOyBkZWwuY2xhc3NOYW1lPSJidG4gc20gZGFuZ2VyIjsgZGVsLnRleHRDb250ZW50PSLwn5eRIEzDtnNjaGVuIjsKICBkZWwub25jbGljayA9ICgpPT4gZGVsZXRlQ3VzdG9tZXIoYyk7CiAgYWN0LmFwcGVuZENoaWxkKGVkaXQpOyBhY3QuYXBwZW5kQ2hpbGQoZGVsKTsKICBjYXJkLmFwcGVuZENoaWxkKGFjdCk7CiAgcmV0dXJuIGNhcmQ7Cn0KCi8vIElubGluZS1Gb3JtdWxhciAobmV1L2JlYXJiZWl0ZW4pIGFscyBLYXJ0ZQpmdW5jdGlvbiBzaG93Q3VzdG9tZXJGb3JtKGMpewogIGNvbnN0IGlzRWRpdCA9ICEhYzsKICBjID0gYyB8fCB7fTsKICBjb25zdCBib2R5ID0gJCgiY3VzdG9tZXJzQm9keSIpOwogIGNvbnN0IGZvcm0gPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgZm9ybS5jbGFzc05hbWU9ImN1c3QiOwogIGNvbnN0IHN0YXR1c09wdHMgPSBzdGF0ZS5zdGF0dXNWYWx1ZXMubWFwKHMgPT4KICAgIGA8b3B0aW9uIHZhbHVlPSIke3N9IiAkeyAoYy5zdGF0dXN8fCJMZWFkIik9PT1zID8gInNlbGVjdGVkIjoiIiB9PiR7c308L29wdGlvbj5gKS5qb2luKCIiKTsKICBmb3JtLmlubmVySFRNTCA9IGAKICAgIDxkaXYgY2xhc3M9InNlY3QiIHN0eWxlPSJtYXJnaW4tdG9wOjAiPiR7aXNFZGl0ID8gIuKcj++4jyBLdW5kZSBiZWFyYmVpdGVuIiA6ICLinpUgTmV1ZXIgS3VuZGUifTwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5OYW1lICo8L2xhYmVsPjxpbnB1dCBpZD0iY2YtbmFtZSI+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPkJyYW5jaGU8L2xhYmVsPjxpbnB1dCBpZD0iY2YtYnJhbmNoZSI+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPktvbnRha3Q8L2xhYmVsPjxpbnB1dCBpZD0iY2Yta29udGFrdCI+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPlBha2V0PC9sYWJlbD48aW5wdXQgaWQ9ImNmLXBha2V0Ij48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+UHJlaXMg4oKsIC8gTW9uYXQ8L2xhYmVsPjxpbnB1dCBpZD0iY2YtcHJlaXMiIHR5cGU9Im51bWJlciIgc3RlcD0iYW55Ij48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+U3RhdHVzPC9sYWJlbD48c2VsZWN0IGlkPSJjZi1zdGF0dXMiPiR7c3RhdHVzT3B0c308L3NlbGVjdD48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+TsOkY2hzdGVyIFNjaHJpdHQ8L2xhYmVsPjxpbnB1dCBpZD0iY2Ytc2Nocml0dCI+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPk5vdGl6ZW48L2xhYmVsPjx0ZXh0YXJlYSBpZD0iY2Ytbm90aXplbiI+PC90ZXh0YXJlYT48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImJ0bnJvdyI+CiAgICAgIDxidXR0b24gY2xhc3M9ImJ0biBwcmltYXJ5IiBpZD0iY2Ytc2F2ZSI+4pyTIFNwZWljaGVybjwvYnV0dG9uPgogICAgICA8YnV0dG9uIGNsYXNzPSJidG4iIGlkPSJjZi1jYW5jZWwiPkFiYnJlY2hlbjwvYnV0dG9uPgogICAgICA8c3BhbiBpZD0iY2YtbXNnIiBjbGFzcz0iaGludCIgc3R5bGU9ImFsaWduLXNlbGY6Y2VudGVyIj48L3NwYW4+CiAgICA8L2Rpdj4KICBgOwogIGJvZHkucHJlcGVuZChmb3JtKTsKICAvLyBXZXJ0ZSBlaW5zZXR6ZW4gKHNpY2hlciwgdmlhIC52YWx1ZSkKICAkKCJjZi1uYW1lIikudmFsdWUgPSBjLm5hbWUgfHwgIiI7CiAgJCgiY2YtYnJhbmNoZSIpLnZhbHVlID0gYy5icmFuY2hlIHx8ICIiOwogICQoImNmLWtvbnRha3QiKS52YWx1ZSA9IGMua29udGFrdCB8fCAiIjsKICAkKCJjZi1wYWtldCIpLnZhbHVlID0gYy5wYWtldCB8fCAiIjsKICAkKCJjZi1wcmVpcyIpLnZhbHVlID0gYy5wcmVpcyAhPSBudWxsID8gYy5wcmVpcyA6ICIiOwogICQoImNmLXNjaHJpdHQiKS52YWx1ZSA9IGMubmFlY2hzdGVyX3NjaHJpdHQgfHwgIiI7CiAgJCgiY2Ytbm90aXplbiIpLnZhbHVlID0gYy5ub3RpemVuIHx8ICIiOwogIGZvcm0uc2Nyb2xsSW50b1ZpZXcoe2JlaGF2aW9yOiJzbW9vdGgiLCBibG9jazoic3RhcnQifSk7CgogICQoImNmLWNhbmNlbCIpLm9uY2xpY2sgPSAoKT0+IGxvYWRDdXN0b21lcnMoKTsKICAkKCJjZi1zYXZlIikub25jbGljayA9IGFzeW5jICgpPT57CiAgICBjb25zdCBuYW1lID0gJCgiY2YtbmFtZSIpLnZhbHVlLnRyaW0oKTsKICAgIGNvbnN0IG1zZyA9ICQoImNmLW1zZyIpOwogICAgaWYgKCFuYW1lKXsgbXNnLnRleHRDb250ZW50PSJOYW1lIGZlaGx0LiI7IG1zZy5zdHlsZS5jb2xvcj0idmFyKC0tcm9zZSkiOyByZXR1cm47IH0KICAgIGNvbnN0IGZpZWxkcyA9IHsKICAgICAgbmFtZSwKICAgICAgYnJhbmNoZTogJCgiY2YtYnJhbmNoZSIpLnZhbHVlLnRyaW0oKSwKICAgICAga29udGFrdDogJCgiY2Yta29udGFrdCIpLnZhbHVlLnRyaW0oKSwKICAgICAgcGFrZXQ6ICQoImNmLXBha2V0IikudmFsdWUudHJpbSgpLAogICAgICBwcmVpczogJCgiY2YtcHJlaXMiKS52YWx1ZS50cmltKCksCiAgICAgIHN0YXR1czogJCgiY2Ytc3RhdHVzIikudmFsdWUsCiAgICAgIG5hZWNoc3Rlcl9zY2hyaXR0OiAkKCJjZi1zY2hyaXR0IikudmFsdWUudHJpbSgpLAogICAgICBub3RpemVuOiAkKCJjZi1ub3RpemVuIikudmFsdWUudHJpbSgpLAogICAgfTsKICAgIGNvbnN0IHBheWxvYWQgPSBpc0VkaXQgPyBPYmplY3QuYXNzaWduKHsgb3A6InVwZGF0ZSIsIGlkOmMuaWQgfSwgZmllbGRzKSA6IE9iamVjdC5hc3NpZ24oeyBvcDoiYWRkIiB9LCBmaWVsZHMpOwogICAgJCgiY2Ytc2F2ZSIpLmRpc2FibGVkID0gdHJ1ZTsKICAgIHRyeXsKICAgICAgY29uc3QgciA9IGF3YWl0IGFwaSgiL2FwaS9jdXN0b21lcnMiLCAiUE9TVCIsIHBheWxvYWQpOwogICAgICBpZiAoci5lcnJvcil7IG1zZy50ZXh0Q29udGVudD0i4pqgICIrci5lcnJvcjsgbXNnLnN0eWxlLmNvbG9yPSJ2YXIoLS1yb3NlKSI7ICQoImNmLXNhdmUiKS5kaXNhYmxlZD1mYWxzZTsgfQogICAgICBlbHNlIHJlbmRlckN1c3RvbWVycyhyKTsgICAgIC8vIEFudHdvcnQgZW50aMOkbHQgY3VzdG9tZXJzICsgcmV2ZW51ZQogICAgfWNhdGNoKGUpeyBtc2cudGV4dENvbnRlbnQ9IuKaoCAiK2UubWVzc2FnZTsgbXNnLnN0eWxlLmNvbG9yPSJ2YXIoLS1yb3NlKSI7ICQoImNmLXNhdmUiKS5kaXNhYmxlZD1mYWxzZTsgfQogIH07Cn0KCmFzeW5jIGZ1bmN0aW9uIGRlbGV0ZUN1c3RvbWVyKGMpewogIGlmICghY29uZmlybShgS3VuZGUgwrske2MubmFtZX3CqyB3aXJrbGljaCBsw7ZzY2hlbj9gKSkgcmV0dXJuOwogIHRyeXsKICAgIGNvbnN0IHIgPSBhd2FpdCBhcGkoIi9hcGkvY3VzdG9tZXJzIiwgIlBPU1QiLCB7IG9wOiJkZWxldGUiLCBpZDpjLmlkIH0pOwogICAgaWYgKHIuZXJyb3IpeyBjb25zdCBiPSQoImN1c3RvbWVyc0JvZHkiKTsgYi5wcmVwZW5kKGVyckJveChyLmVycm9yKSk7IH0KICAgIGVsc2UgcmVuZGVyQ3VzdG9tZXJzKHIpOwogIH1jYXRjaChlKXsgJCgiY3VzdG9tZXJzQm9keSIpLnByZXBlbmQoZXJyQm94KCJOZXR6d2Vya2ZlaGxlcjogIitlLm1lc3NhZ2UpKTsgfQp9CgovLyAtLS0tLS0tLS0tIEdlZMOkY2h0bmlzIC0tLS0tLS0tLS0KYXN5bmMgZnVuY3Rpb24gbG9hZE1lbW9yeSgpewogIGNvbnN0IGJvZHkgPSAkKCJtZW1vcnlCb2R5Iik7CiAgYm9keS5pbm5lckhUTUwgPSAnPGRpdiBjbGFzcz0iZW1wdHkiPmzDpGR04oCmPC9kaXY+JzsKICBsZXQgZDsKICB0cnkgeyBkID0gYXdhaXQgYXBpKCIvYXBpL21lbW9yeSIpOyB9CiAgY2F0Y2goZSl7IGJvZHkuaW5uZXJIVE1MPSIiOyBib2R5LmFwcGVuZENoaWxkKGVyckJveCgiS29ubnRlIEdlZMOkY2h0bmlzIG5pY2h0IGxhZGVuOiAiK2UubWVzc2FnZSkpOyByZXR1cm47IH0KICBpZiAoZC5lcnJvcil7IGJvZHkuaW5uZXJIVE1MPSIiOyBib2R5LmFwcGVuZENoaWxkKGVyckJveChkLmVycm9yKSk7IHJldHVybjsgfQoKICBib2R5LmlubmVySFRNTCA9ICIiOwogIGNvbnN0IGZhY3RzID0gZC5mYWN0cyB8fCBbXTsKICBjb25zdCBqb3VybmFsID0gZC5qb3VybmFsIHx8IFtdOwoKICBjb25zdCBoMSA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBoMS5jbGFzc05hbWU9InNlY3QiOyBoMS50ZXh0Q29udGVudD0i8J+noCBXYXMgRGlubyDDvGJlciBkaWNoIHdlacOfIjsKICBib2R5LmFwcGVuZENoaWxkKGgxKTsKICBpZiAoZmFjdHMubGVuZ3RoKXsKICAgIGNvbnN0IHVsID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgidWwiKTsgdWwuY2xhc3NOYW1lPSJmYWN0bGlzdCI7CiAgICBmYWN0cy5mb3JFYWNoKGYgPT4geyBjb25zdCBsaT1kb2N1bWVudC5jcmVhdGVFbGVtZW50KCJsaSIpOyBsaS50ZXh0Q29udGVudD1mOyB1bC5hcHBlbmRDaGlsZChsaSk7IH0pOwogICAgYm9keS5hcHBlbmRDaGlsZCh1bCk7CiAgfSBlbHNlIHsKICAgIGNvbnN0IGU9ZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IGUuY2xhc3NOYW1lPSJlbXB0eSI7IGUudGV4dENvbnRlbnQ9Ik5vY2ggbGVlciDigJQga2xpY2sgaW0gQ2hhdCBhdWYgwrvwn6egIExlcm5lbsKrLiI7CiAgICBib2R5LmFwcGVuZENoaWxkKGUpOwogIH0KCiAgY29uc3QgaDIgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgaDIuY2xhc3NOYW1lPSJzZWN0IjsgaDIudGV4dENvbnRlbnQ9IvCfk5MgTGV0enRlIE5vdGl6ZW4gKFRhZ2VidWNoKSI7CiAgYm9keS5hcHBlbmRDaGlsZChoMik7CiAgY29uc3QgaldyYXAgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgaldyYXAuY2xhc3NOYW1lPSJqb3VybmFsIjsKICBjb25zdCBsYXN0ID0gam91cm5hbC5zbGljZSgtMTUpLnJldmVyc2UoKTsKICBpZiAobGFzdC5sZW5ndGgpewogICAgbGFzdC5mb3JFYWNoKGo9PnsKICAgICAgY29uc3QgbGluZSA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOwogICAgICBjb25zdCBkMiA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoInNwYW4iKTsgZDIuY2xhc3NOYW1lPSJkIjsgZDIudGV4dENvbnRlbnQgPSAiWyIrKGouZGF0ZXx8IiIpKyJdICI7CiAgICAgIGxpbmUuYXBwZW5kQ2hpbGQoZDIpOwogICAgICBsaW5lLmFwcGVuZENoaWxkKGRvY3VtZW50LmNyZWF0ZVRleHROb2RlKGoubm90ZXx8IiIpKTsKICAgICAgaldyYXAuYXBwZW5kQ2hpbGQobGluZSk7CiAgICB9KTsKICB9IGVsc2UgewogICAgaldyYXAuaW5uZXJIVE1MID0gJzxkaXYgY2xhc3M9ImVtcHR5Ij4obGVlcik8L2Rpdj4nOwogIH0KICBib2R5LmFwcGVuZENoaWxkKGpXcmFwKTsKfQoKLy8ga2xlaW5lIHJvdGUgRmVobGVyYm94IGbDvHIgUGFuZWxzCmZ1bmN0aW9uIGVyckJveCh0ZXh0KXsKICBjb25zdCBlID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7CiAgZS5jbGFzc05hbWUgPSAibXNnIGVycm9yIjsgZS5zdHlsZS5tYXhXaWR0aD0iMTAwJSI7CiAgY29uc3QgYiA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBiLmNsYXNzTmFtZT0iYnViYmxlIjsgYi50ZXh0Q29udGVudCA9IHRleHQ7CiAgZS5hcHBlbmRDaGlsZChiKTsKICByZXR1cm4gZTsKfQoKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09Ci8vICBTdGFydAovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KbG9hZFN0YXR1cygpOwppbnB1dEVsLmZvY3VzKCk7Cjwvc2NyaXB0Pgo8L2JvZHk+CjwvaHRtbD4K").decode("utf-8")

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
