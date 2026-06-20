#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DINO KI - EINE Datei. Doppelklick (oder: python Dino-KI.py) und es
oeffnet sich dein Jarvis-Chatfenster im Browser.

Dino laeuft ab Werk GRATIS & lokal ueber Ollama (kein Schluessel) und
richtet sich beim Start selbst ein (Ollama starten + Modell laden).
Reine Standardbibliothek. Voraussetzung: Python + Ollama (ollama.com).
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
    try:
        body = e.read().decode("utf-8")
        info = json.loads(body)
        msg = info.get("error", {}).get("message") or info.get("error", {}).get("type") or body
    except Exception:
        msg = str(e)
    if e.code == 401:
        return f"Schlüssel ungültig (401). Prüf ihn in den Einstellungen.  [{msg}]"
    if e.code == 429:
        return f"Zu viele Anfragen / Guthaben leer (429).  [{msg}]"
    return f"Fehler {e.code}: {msg}"


def euro(x):
    try:
        return f"{float(x):,.0f} €".replace(",", ".")
    except (ValueError, TypeError):
        return "0 €"


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
        Läuft beim Start der App, damit der Nutzer nichts von Hand tippen muss."""
        if self.config["provider"] != "ollama":
            return
        exe = shutil.which("ollama")
        if not exe:
            log("  ⚠ Ollama ist noch nicht installiert (gratis: https://ollama.com/download).")
            log("    Dino startet trotzdem — installier Ollama und starte Dino neu.")
            return
        # Server erreichbar? Sonst im Hintergrund starten.
        if not self.ollama_status()["running"]:
            log("  🦖 Starte das lokale Gehirn (Ollama)…")
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
            log("  ⚠ Ollama startet nicht automatisch — öffne die Ollama-App einmal manuell.")
            return
        # Modell vorhanden? Sonst automatisch herunterladen.
        model = self.config.get("ollama_model", "llama3.2")
        if ":" in model:
            have = model in st["models"]
        else:
            have = any(m == model or m.split(":")[0] == model for m in st["models"])
        if have:
            log(f"  ✓ Dinos Gehirn ist bereit: {model}")
            return
        log(f"  🦖 Lade Dinos Gehirn herunter: {model}  (einmalig — kann ein paar Minuten dauern)…")
        try:
            subprocess.run([exe, "pull", model])
            log("  ✓ Modell geladen. Los geht's!")
        except Exception as e:
            log(f"  ⚠ Konnte das Modell nicht automatisch laden: {e}")
            log(f"    Tipp: im Terminal  ollama pull {model}")

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
        """Gratis-Gehirn: ein KI-Modell, das lokal über Ollama läuft (kein Schlüssel)."""
        url = self.config.get("ollama_url", "http://127.0.0.1:11434").rstrip("/") + "/api/chat"
        model = self.config.get("ollama_model", "llama3.2")
        msgs = [{"role": "system", "content": system}] + messages
        body = {"model": model, "messages": msgs, "stream": False,
                "options": {"num_predict": max_tokens}}
        try:
            data = self._post(url, {"content-type": "application/json"}, body, timeout=600)
            return (data.get("message", {}).get("content", "") or "").strip(), None
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None, (f"Modell »{model}« ist noch nicht da. Lade es im Terminal: "
                              f"ollama pull {model}")
            return None, _http_msg(e)
        except urllib.error.URLError:
            return None, ("Ollama läuft nicht. Installiere es gratis von ollama.com und starte "
                          "im Terminal ein Modell, z.B.:  ollama run llama3.2")
        except Exception as e:
            return None, f"Verbindungsfehler zu Ollama: {e}"

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
        return self.ask_provider(self.build_system(), history, max_tokens, effort)

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
DINO_HTML = _b64.b64decode("PCFET0NUWVBFIGh0bWw+CjxodG1sIGxhbmc9ImRlIj4KPGhlYWQ+CjxtZXRhIGNoYXJzZXQ9IlVURi04Ij4KPG1ldGEgbmFtZT0idmlld3BvcnQiIGNvbnRlbnQ9IndpZHRoPWRldmljZS13aWR0aCwgaW5pdGlhbC1zY2FsZT0xLjAiPgo8dGl0bGU+8J+mliBEaW5vIEtJPC90aXRsZT4KPHN0eWxlPgovKiA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KICAgRElOTyBLSSDigJQgSmFydmlzL1NjaS1GaSBGcm9udGVuZCAoZWluZSBlaWdlbnN0w6RuZGlnZSBEYXRlaSkKICAgUmVpbmVzIEhUTUwvQ1NTL0pTLCBrZWluZSBleHRlcm5lbiBCaWJsaW90aGVrZW4uCiAgID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PSAqLwoKLyogLS0tLSBEZXNpZ24tVmFyaWFibGVuIC0tLS0gKi8KOnJvb3R7CiAgLS1iZzojMDQwNjBkOyAgICAgICAgICAgIC8qIGZhc3Qgc2Nod2FyeiAqLwogIC0tYmcyOiMwNjBhMTY7CiAgLS1wYW5lbDpyZ2JhKDE0LDIyLDQyLC42Mik7ICAgLyogR2xhc21vcnBoaXNtdXMtUGFuZWwgKi8KICAtLXBhbmVsLXNvbGlkOiMwYTExMjQ7CiAgLS1saW5lOnJnYmEoNTYsMTg5LDI0OCwuMjIpOyAgLyogbGV1Y2h0ZW5kZXIgZMO8bm5lciBSYW5kICovCiAgLS1jeWFuOiMyMmQzZWU7CiAgLS1ibHVlOiMzOGJkZjg7CiAgLS1ibHVlMjojNjBhNWZhOwogIC0tdHh0OiNlOGYxZmY7CiAgLS1tdXQ6IzdjOGRiNTsKICAtLWdyZWVuOiMzNGQzOTk7CiAgLS1yb3NlOiNmYjcxODU7CiAgLS1hbWJlcjojZmJiZjI0OwogIC0tZ2xvdzowIDAgMThweCByZ2JhKDM0LDIxMSwyMzgsLjU1KTsKfQoKKntib3gtc2l6aW5nOmJvcmRlci1ib3h9Cmh0bWwsYm9keXtoZWlnaHQ6MTAwJX0KYm9keXsKICBtYXJnaW46MDsKICBmb250LWZhbWlseToiU2Vnb2UgVUkiLHN5c3RlbS11aSwtYXBwbGUtc3lzdGVtLCJIZWx2ZXRpY2EgTmV1ZSIsQXJpYWwsc2Fucy1zZXJpZjsKICBjb2xvcjp2YXIoLS10eHQpOwogIGJhY2tncm91bmQ6CiAgICByYWRpYWwtZ3JhZGllbnQoMTIwMHB4IDYwMHB4IGF0IDUwJSAtMTAlLCByZ2JhKDM0LDIxMSwyMzgsLjEwKSwgdHJhbnNwYXJlbnQgNjAlKSwKICAgIHJhZGlhbC1ncmFkaWVudCg5MDBweCA1MDBweCBhdCA5MCUgMTEwJSwgcmdiYSg5NiwxNjUsMjUwLC4wOCksIHRyYW5zcGFyZW50IDYwJSksCiAgICB2YXIoLS1iZyk7CiAgb3ZlcmZsb3c6aGlkZGVuOwp9Ci8qIGRlemVudGVzIEdyaWQgaW0gSGludGVyZ3J1bmQgKi8KYm9keTo6YmVmb3JlewogIGNvbnRlbnQ6IiI7cG9zaXRpb246Zml4ZWQ7aW5zZXQ6MDt6LWluZGV4OjA7cG9pbnRlci1ldmVudHM6bm9uZTtvcGFjaXR5Oi4zNTsKICBiYWNrZ3JvdW5kLWltYWdlOgogICAgbGluZWFyLWdyYWRpZW50KHJnYmEoNTYsMTg5LDI0OCwuMDYpIDFweCx0cmFuc3BhcmVudCAxcHgpLAogICAgbGluZWFyLWdyYWRpZW50KDkwZGVnLHJnYmEoNTYsMTg5LDI0OCwuMDYpIDFweCx0cmFuc3BhcmVudCAxcHgpOwogIGJhY2tncm91bmQtc2l6ZTo0NHB4IDQ0cHg7CiAgbWFzay1pbWFnZTpyYWRpYWwtZ3JhZGllbnQoY2lyY2xlIGF0IDUwJSAzMCUsIzAwMCAwJSx0cmFuc3BhcmVudCA4MCUpOwp9CgouYXBwe3Bvc2l0aW9uOnJlbGF0aXZlO3otaW5kZXg6MTtkaXNwbGF5OmZsZXg7ZmxleC1kaXJlY3Rpb246Y29sdW1uO2hlaWdodDoxMDB2aDttYXgtd2lkdGg6MTE4MHB4O21hcmdpbjowIGF1dG87cGFkZGluZzoxNHB4IDE4cHggMTZweH0KCi8qID09PT09PT09PT09PT09PT09IEtvcGZ6ZWlsZSA9PT09PT09PT09PT09PT09PSAqLwouaGVhZGVye2Rpc3BsYXk6ZmxleDthbGlnbi1pdGVtczpjZW50ZXI7Z2FwOjE4cHg7cGFkZGluZzo2cHggNHB4IDEycHh9Ci5icmFuZHtkaXNwbGF5OmZsZXg7YWxpZ24taXRlbXM6Y2VudGVyO2dhcDoxNHB4O21pbi13aWR0aDowfQoud29yZG1hcmt7CiAgZm9udC1zaXplOjI2cHg7Zm9udC13ZWlnaHQ6ODAwO2xldHRlci1zcGFjaW5nOjVweDsKICBiYWNrZ3JvdW5kOmxpbmVhci1ncmFkaWVudCg5MGRlZywjNjdlOGY5LCMzOGJkZjgsIzgxOGNmOCk7CiAgLXdlYmtpdC1iYWNrZ3JvdW5kLWNsaXA6dGV4dDtiYWNrZ3JvdW5kLWNsaXA6dGV4dDtjb2xvcjp0cmFuc3BhcmVudDsKICB0ZXh0LXNoYWRvdzowIDAgMjRweCByZ2JhKDU2LDE4OSwyNDgsLjM1KTsKICBmaWx0ZXI6ZHJvcC1zaGFkb3coMCAwIDEwcHggcmdiYSgzNCwyMTEsMjM4LC40KSk7Cn0KLnRhZ2xpbmV7CiAgZm9udC1zaXplOjExcHg7bGV0dGVyLXNwYWNpbmc6MS41cHg7bWFyZ2luLXRvcDoxcHg7Zm9udC13ZWlnaHQ6NjAwOwogIGJhY2tncm91bmQ6bGluZWFyLWdyYWRpZW50KDkwZGVnLCM2N2U4ZjksIzYwYTVmYSk7CiAgLXdlYmtpdC1iYWNrZ3JvdW5kLWNsaXA6dGV4dDtiYWNrZ3JvdW5kLWNsaXA6dGV4dDtjb2xvcjp0cmFuc3BhcmVudDsKICB0ZXh0LXNoYWRvdzowIDAgMTJweCByZ2JhKDU2LDE4OSwyNDgsLjI1KTtvcGFjaXR5Oi45MjsKfQouc3RhdHVzbGluZXtkaXNwbGF5OmZsZXg7YWxpZ24taXRlbXM6Y2VudGVyO2dhcDo4cHg7Zm9udC1zaXplOjEyLjVweDtjb2xvcjp2YXIoLS1tdXQpO21hcmdpbi10b3A6M3B4O2ZsZXgtd3JhcDp3cmFwfQouZG90e3dpZHRoOjlweDtoZWlnaHQ6OXB4O2JvcmRlci1yYWRpdXM6NTAlO2JhY2tncm91bmQ6dmFyKC0tbXV0KTtib3gtc2hhZG93OjAgMCA4cHggY3VycmVudENvbG9yO3RyYW5zaXRpb246LjNzfQouZG90Lm9re2JhY2tncm91bmQ6dmFyKC0tZ3JlZW4pO2NvbG9yOnZhcigtLWdyZWVuKX0KLmRvdC5iYWR7YmFja2dyb3VuZDp2YXIoLS1yb3NlKTtjb2xvcjp2YXIoLS1yb3NlKX0KLyoga2xlaW5lciBPbGxhbWEtSW5kaWthdG9yIG9iZW4gKi8KLm9sbGFtYS1waWxse2Rpc3BsYXk6aW5saW5lLWZsZXg7YWxpZ24taXRlbXM6Y2VudGVyO2dhcDo2cHg7Zm9udC1zaXplOjExcHg7cGFkZGluZzoycHggOXB4O2JvcmRlci1yYWRpdXM6OTk5cHg7CiAgYm9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtiYWNrZ3JvdW5kOnZhcigtLXBhbmVsKTtiYWNrZHJvcC1maWx0ZXI6Ymx1cig4cHgpO2NvbG9yOnZhcigtLW11dCl9Ci5vbGxhbWEtcGlsbCAub3Bkb3R7d2lkdGg6N3B4O2hlaWdodDo3cHg7Ym9yZGVyLXJhZGl1czo1MCU7YmFja2dyb3VuZDp2YXIoLS1tdXQpO2JveC1zaGFkb3c6MCAwIDdweCBjdXJyZW50Q29sb3I7dHJhbnNpdGlvbjouM3N9Ci5vbGxhbWEtcGlsbC5va3tjb2xvcjojYmZmNGZmO2JvcmRlci1jb2xvcjpyZ2JhKDUyLDIxMSwxNTMsLjUpfQoub2xsYW1hLXBpbGwub2sgLm9wZG90e2JhY2tncm91bmQ6dmFyKC0tZ3JlZW4pO2NvbG9yOnZhcigtLWdyZWVuKX0KLm9sbGFtYS1waWxsLndhcm57Y29sb3I6I2ZmZTliODtib3JkZXItY29sb3I6cmdiYSgyNTEsMTkxLDM2LC41KX0KLm9sbGFtYS1waWxsLndhcm4gLm9wZG90e2JhY2tncm91bmQ6dmFyKC0tYW1iZXIpO2NvbG9yOnZhcigtLWFtYmVyKX0KLm9sbGFtYS1waWxsLmJhZHtjb2xvcjojZmZkOWRmO2JvcmRlci1jb2xvcjpyZ2JhKDI1MSwxMTMsMTMzLC41KX0KLm9sbGFtYS1waWxsLmJhZCAub3Bkb3R7YmFja2dyb3VuZDp2YXIoLS1yb3NlKTtjb2xvcjp2YXIoLS1yb3NlKX0KLmhlYWRlciAuc3BhY2Vye2ZsZXg6MX0KLmljb25idG5ze2Rpc3BsYXk6ZmxleDtnYXA6OHB4fQouaWNvbmJ0bnsKICB3aWR0aDo0MnB4O2hlaWdodDo0MnB4O2JvcmRlci1yYWRpdXM6MTJweDtib3JkZXI6MXB4IHNvbGlkIHZhcigtLWxpbmUpOwogIGJhY2tncm91bmQ6dmFyKC0tcGFuZWwpO2JhY2tkcm9wLWZpbHRlcjpibHVyKDhweCk7CiAgY29sb3I6dmFyKC0tdHh0KTtmb250LXNpemU6MThweDtjdXJzb3I6cG9pbnRlcjtkaXNwbGF5OmdyaWQ7cGxhY2UtaXRlbXM6Y2VudGVyOwogIHRyYW5zaXRpb246LjE4czsKfQouaWNvbmJ0bjpob3Zlcntib3JkZXItY29sb3I6dmFyKC0tY3lhbik7Ym94LXNoYWRvdzp2YXIoLS1nbG93KTt0cmFuc2Zvcm06dHJhbnNsYXRlWSgtMXB4KX0KCi8qID09PT09PT09PT09PT09PT09IENvcmUgLyBPcmIgPT09PT09PT09PT09PT09PT0gKi8KLmNvcmUtd3JhcHtkaXNwbGF5OmZsZXg7anVzdGlmeS1jb250ZW50OmNlbnRlcjthbGlnbi1pdGVtczpjZW50ZXI7aGVpZ2h0OjExOHB4O21hcmdpbjotNHB4IDAgNnB4O3Bvc2l0aW9uOnJlbGF0aXZlfQouY29yZXtwb3NpdGlvbjpyZWxhdGl2ZTt3aWR0aDo5NnB4O2hlaWdodDo5NnB4O2Rpc3BsYXk6Z3JpZDtwbGFjZS1pdGVtczpjZW50ZXJ9Ci5jb3JlIC5yaW5newogIHBvc2l0aW9uOmFic29sdXRlO2JvcmRlci1yYWRpdXM6NTAlO2JvcmRlcjoycHggc29saWQgcmdiYSg1NiwxODksMjQ4LC4zNSk7CiAgYW5pbWF0aW9uOnNwaW4gNnMgbGluZWFyIGluZmluaXRlOwp9Ci5jb3JlIC5yMXtpbnNldDowO2JvcmRlci10b3AtY29sb3I6dmFyKC0tY3lhbik7Ym9yZGVyLXJpZ2h0LWNvbG9yOnRyYW5zcGFyZW50fQouY29yZSAucjJ7aW5zZXQ6MTJweDtib3JkZXItYm90dG9tLWNvbG9yOnZhcigtLWJsdWUyKTtib3JkZXItbGVmdC1jb2xvcjp0cmFuc3BhcmVudDthbmltYXRpb24tZHVyYXRpb246NHM7YW5pbWF0aW9uLWRpcmVjdGlvbjpyZXZlcnNlfQouY29yZSAucjN7aW5zZXQ6MjRweDtib3JkZXItdG9wLWNvbG9yOnZhcigtLWJsdWUpO2JvcmRlci1sZWZ0LWNvbG9yOnRyYW5zcGFyZW50O2FuaW1hdGlvbi1kdXJhdGlvbjo4c30KLmNvcmUgLm51Y2xldXN7CiAgd2lkdGg6MzhweDtoZWlnaHQ6MzhweDtib3JkZXItcmFkaXVzOjUwJTsKICBiYWNrZ3JvdW5kOnJhZGlhbC1ncmFkaWVudChjaXJjbGUgYXQgMzUlIDMwJSwjYmZmNGZmLCMyMmQzZWUgNDUlLCMxZDRlZDggMTAwJSk7CiAgYm94LXNoYWRvdzowIDAgMjZweCA2cHggcmdiYSgzNCwyMTEsMjM4LC42NSksMCAwIDYwcHggMTJweCByZ2JhKDU2LDE4OSwyNDgsLjI1KTsKICBhbmltYXRpb246cHVsc2UgMi42cyBlYXNlLWluLW91dCBpbmZpbml0ZTsKfQpAa2V5ZnJhbWVzIHNwaW57dG97dHJhbnNmb3JtOnJvdGF0ZSgzNjBkZWcpfX0KQGtleWZyYW1lcyBwdWxzZXswJSwxMDAle3RyYW5zZm9ybTpzY2FsZSgxKTtvcGFjaXR5Oi45Mn01MCV7dHJhbnNmb3JtOnNjYWxlKDEuMTYpO29wYWNpdHk6MX19Ci8qIFp1c3TDpG5kZTogbmFjaGRlbmtlbiAoc2NobmVsbGVyKSAvIHNwcmVjaGVuICovCi5jb3JlLnRoaW5raW5nIC5yaW5ne2FuaW1hdGlvbi1kdXJhdGlvbjoxLjRzIWltcG9ydGFudH0KLmNvcmUudGhpbmtpbmcgLnIye2FuaW1hdGlvbi1kdXJhdGlvbjoxcyFpbXBvcnRhbnR9Ci5jb3JlLnRoaW5raW5nIC5udWNsZXVze2FuaW1hdGlvbi1kdXJhdGlvbjouOHN9Ci5jb3JlLnNwZWFraW5nIC5udWNsZXVze2FuaW1hdGlvbjpzcGVhayAuNXMgZWFzZS1pbi1vdXQgaW5maW5pdGV9CkBrZXlmcmFtZXMgc3BlYWt7MCUsMTAwJXt0cmFuc2Zvcm06c2NhbGUoMSl9NTAle3RyYW5zZm9ybTpzY2FsZSgxLjI4KTtib3gtc2hhZG93OjAgMCAzNHB4IDEwcHggcmdiYSgzNCwyMTEsMjM4LC44NSl9fQoKLyogPT09PT09PT09PT09PT09PT0gQ2hhdCA9PT09PT09PT09PT09PT09PSAqLwouY2hhdHsKICBmbGV4OjE7b3ZlcmZsb3cteTphdXRvO3BhZGRpbmc6MTBweCA2cHggNHB4O2Rpc3BsYXk6ZmxleDtmbGV4LWRpcmVjdGlvbjpjb2x1bW47Z2FwOjE0cHg7CiAgc2Nyb2xsYmFyLXdpZHRoOnRoaW47c2Nyb2xsYmFyLWNvbG9yOnJnYmEoNTYsMTg5LDI0OCwuNCkgdHJhbnNwYXJlbnQ7Cn0KLmNoYXQ6Oi13ZWJraXQtc2Nyb2xsYmFye3dpZHRoOjhweH0KLmNoYXQ6Oi13ZWJraXQtc2Nyb2xsYmFyLXRodW1ie2JhY2tncm91bmQ6cmdiYSg1NiwxODksMjQ4LC4zNSk7Ym9yZGVyLXJhZGl1czo4cHh9CgoubXNne2Rpc3BsYXk6ZmxleDtnYXA6MTBweDttYXgtd2lkdGg6ODIlO2FuaW1hdGlvbjpmYWRlaW4gLjM1cyBlYXNlIGJvdGh9CkBrZXlmcmFtZXMgZmFkZWlue2Zyb217b3BhY2l0eTowO3RyYW5zZm9ybTp0cmFuc2xhdGVZKDEwcHgpfXRve29wYWNpdHk6MTt0cmFuc2Zvcm06bm9uZX19Ci5tc2cudXNlcnthbGlnbi1zZWxmOmZsZXgtZW5kO2ZsZXgtZGlyZWN0aW9uOnJvdy1yZXZlcnNlfQouYXZhdGFye2ZsZXg6bm9uZTt3aWR0aDozMHB4O2hlaWdodDozMHB4O2JvcmRlci1yYWRpdXM6OXB4O2Rpc3BsYXk6Z3JpZDtwbGFjZS1pdGVtczpjZW50ZXI7Zm9udC1zaXplOjE1cHg7CiAgYmFja2dyb3VuZDp2YXIoLS1wYW5lbCk7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKX0KLmJ1YmJsZXsKICBwYWRkaW5nOjExcHggMTRweDtib3JkZXItcmFkaXVzOjE0cHg7Zm9udC1zaXplOjE0LjVweDtsaW5lLWhlaWdodDoxLjU7CiAgd2hpdGUtc3BhY2U6cHJlLXdyYXA7d29yZC1icmVhazpicmVhay13b3JkOwp9Ci8qIERpbm86IEdsYXMtQnViYmxlICovCi5tc2cuZGlubyAuYnViYmxlewogIGJhY2tncm91bmQ6dmFyKC0tcGFuZWwpO2JhY2tkcm9wLWZpbHRlcjpibHVyKDEwcHgpOwogIGJvcmRlcjoxcHggc29saWQgdmFyKC0tbGluZSk7Ym9yZGVyLXRvcC1sZWZ0LXJhZGl1czo0cHg7CiAgYm94LXNoYWRvdzowIDRweCAyMnB4IHJnYmEoMCwwLDAsLjM1KTsKfQovKiBOdXR6ZXI6IEFremVudC1CdWJibGUgKi8KLm1zZy51c2VyIC5idWJibGV7CiAgYmFja2dyb3VuZDpsaW5lYXItZ3JhZGllbnQoMTM1ZGVnLHJnYmEoMzQsMjExLDIzOCwuMjIpLHJnYmEoOTYsMTY1LDI1MCwuMjApKTsKICBib3JkZXI6MXB4IHNvbGlkIHJnYmEoMzQsMjExLDIzOCwuNDUpO2JvcmRlci10b3AtcmlnaHQtcmFkaXVzOjRweDsKICBib3gtc2hhZG93OjAgMCAxOHB4IHJnYmEoMzQsMjExLDIzOCwuMTgpOwp9Ci8qIEluZm8gLyBGZWhsZXIgLyBMYWJlbCAvIFN5bnRoZXNlICovCi5tc2cuaW5mbyAuYnViYmxle2JhY2tncm91bmQ6dHJhbnNwYXJlbnQ7Ym9yZGVyOjFweCBkYXNoZWQgcmdiYSgxMjQsMTQxLDE4MSwuNCk7Y29sb3I6dmFyKC0tbXV0KTtmb250LXN0eWxlOml0YWxpYztmb250LXNpemU6MTNweH0KLm1zZy5lcnJvciAuYnViYmxle2JhY2tncm91bmQ6cmdiYSgyNTEsMTEzLDEzMywuMTIpO2JvcmRlcjoxcHggc29saWQgdmFyKC0tcm9zZSk7Y29sb3I6I2ZmZDlkZn0KLm1zZy5lcnJvciAuYXZhdGFye2JvcmRlci1jb2xvcjp2YXIoLS1yb3NlKX0KLmxhYmVse2ZvbnQtc2l6ZToxMXB4O2xldHRlci1zcGFjaW5nOi41cHg7dGV4dC10cmFuc2Zvcm06dXBwZXJjYXNlO2NvbG9yOnZhcigtLWN5YW4pO21hcmdpbi1ib3R0b206M3B4O2ZvbnQtd2VpZ2h0OjcwMDtvcGFjaXR5Oi45fQoubXNnLnN5bnRoIC5idWJibGV7CiAgYmFja2dyb3VuZDpsaW5lYXItZ3JhZGllbnQoMTM1ZGVnLHJnYmEoMzQsMjExLDIzOCwuMTYpLHJnYmEoMTI5LDE0MCwyNDgsLjE0KSk7CiAgYm9yZGVyOjFweCBzb2xpZCB2YXIoLS1jeWFuKTtib3gtc2hhZG93OnZhcigtLWdsb3cpOwp9CgovKiBUaXBwLUluZGlrYXRvciAqLwoudHlwaW5ne2Rpc3BsYXk6ZmxleDtnYXA6NXB4O2FsaWduLWl0ZW1zOmNlbnRlcjtwYWRkaW5nOjEzcHggMTZweH0KLnR5cGluZyBzcGFue3dpZHRoOjhweDtoZWlnaHQ6OHB4O2JvcmRlci1yYWRpdXM6NTAlO2JhY2tncm91bmQ6dmFyKC0tY3lhbik7b3BhY2l0eTouNTthbmltYXRpb246Ym91bmNlIDEuMnMgaW5maW5pdGV9Ci50eXBpbmcgc3BhbjpudGgtY2hpbGQoMil7YW5pbWF0aW9uLWRlbGF5Oi4xOHN9Ci50eXBpbmcgc3BhbjpudGgtY2hpbGQoMyl7YW5pbWF0aW9uLWRlbGF5Oi4zNnN9CkBrZXlmcmFtZXMgYm91bmNlezAlLDYwJSwxMDAle3RyYW5zZm9ybTp0cmFuc2xhdGVZKDApO29wYWNpdHk6LjR9MzAle3RyYW5zZm9ybTp0cmFuc2xhdGVZKC02cHgpO29wYWNpdHk6MX19CgovKiA9PT09PT09PT09PT09PT09PSBEaW5vLVNldHVwLUthcnRlID09PT09PT09PT09PT09PT09ICovCi5zZXR1cC1jYXJkewogIGFsaWduLXNlbGY6c3RyZXRjaDttYXgtd2lkdGg6MTAwJTsKICBib3JkZXI6MXB4IHNvbGlkIHZhcigtLWN5YW4pO2JvcmRlci1yYWRpdXM6MTZweDtwYWRkaW5nOjE4cHggMjBweDsKICBiYWNrZ3JvdW5kOmxpbmVhci1ncmFkaWVudCgxNTBkZWcscmdiYSgzNCwyMTEsMjM4LC4xMCkscmdiYSgxMjksMTQwLDI0OCwuMDgpKTsKICBiYWNrZHJvcC1maWx0ZXI6Ymx1cigxMnB4KTtib3gtc2hhZG93OjAgMCAzMHB4IHJnYmEoMzQsMjExLDIzOCwuMTgpLDAgNnB4IDI4cHggcmdiYSgwLDAsMCwuNCk7CiAgYW5pbWF0aW9uOmZhZGVpbiAuNHMgZWFzZSBib3RoOwp9Ci5zZXR1cC1jYXJkIC5zYy10aXRsZXtmb250LXNpemU6MTdweDtmb250LXdlaWdodDo4MDA7bGV0dGVyLXNwYWNpbmc6LjRweDsKICBiYWNrZ3JvdW5kOmxpbmVhci1ncmFkaWVudCg5MGRlZywjYmZmNGZmLCM2MGE1ZmEpOy13ZWJraXQtYmFja2dyb3VuZC1jbGlwOnRleHQ7YmFja2dyb3VuZC1jbGlwOnRleHQ7Y29sb3I6dHJhbnNwYXJlbnQ7CiAgdGV4dC1zaGFkb3c6MCAwIDE4cHggcmdiYSg1NiwxODksMjQ4LC4zKTttYXJnaW4tYm90dG9tOjZweH0KLnNldHVwLWNhcmQgLnNjLXN1Yntmb250LXNpemU6MTNweDtjb2xvcjp2YXIoLS1tdXQpO2xpbmUtaGVpZ2h0OjEuNjttYXJnaW4tYm90dG9tOjE0cHh9Ci5zZXR1cC1jYXJkIC5zYy1zdGVwe21hcmdpbjoxMnB4IDB9Ci5zZXR1cC1jYXJkIC5zYy1zdGVwLWh7Zm9udC1zaXplOjEzLjVweDtmb250LXdlaWdodDo3MDA7Y29sb3I6dmFyKC0tdHh0KTttYXJnaW4tYm90dG9tOjZweDtkaXNwbGF5OmZsZXg7YWxpZ24taXRlbXM6Y2VudGVyO2dhcDo3cHh9Ci5zZXR1cC1jYXJkIC5zYy1zdGVwLWggLm51bXtmbGV4Om5vbmU7d2lkdGg6MjJweDtoZWlnaHQ6MjJweDtib3JkZXItcmFkaXVzOjUwJTtkaXNwbGF5OmdyaWQ7cGxhY2UtaXRlbXM6Y2VudGVyOwogIGZvbnQtc2l6ZToxMnB4O2JhY2tncm91bmQ6cmdiYSgzNCwyMTEsMjM4LC4xNik7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtjb2xvcjp2YXIoLS1jeWFuKX0KLnNldHVwLWNhcmQgYS5zYy1saW5re2NvbG9yOnZhcigtLWJsdWUyKTt0ZXh0LWRlY29yYXRpb246bm9uZTtib3JkZXItYm90dG9tOjFweCBkb3R0ZWQgcmdiYSg5NiwxNjUsMjUwLC41KX0KLnNldHVwLWNhcmQgYS5zYy1saW5rOmhvdmVye2NvbG9yOiNiZmY0ZmY7Ym9yZGVyLWJvdHRvbS1jb2xvcjp2YXIoLS1jeWFuKX0KLnNldHVwLWNhcmQgLnNjLWNvZGVib3h7ZGlzcGxheTpmbGV4O2FsaWduLWl0ZW1zOmNlbnRlcjtnYXA6OHB4O21hcmdpbi10b3A6NnB4fQouc2V0dXAtY2FyZCAuc2MtY29kZXsKICBmbGV4OjE7Zm9udC1mYW1pbHk6IkNvbnNvbGFzIiwiU0YgTW9ubyIsdWktbW9ub3NwYWNlLG1vbm9zcGFjZTtmb250LXNpemU6MTMuNXB4O2NvbG9yOiNiZmY0ZmY7CiAgYmFja2dyb3VuZDpyZ2JhKDIsOCwyMCwuNyk7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtib3JkZXItcmFkaXVzOjEwcHg7cGFkZGluZzo5cHggMTJweDsKICB3aGl0ZS1zcGFjZTpub3dyYXA7b3ZlcmZsb3cteDphdXRvO2JveC1zaGFkb3c6aW5zZXQgMCAwIDE0cHggcmdiYSgzNCwyMTEsMjM4LC4wOCk7Cn0KLnNldHVwLWNhcmQgLnNjLWNvcHl7ZmxleDpub25lO3BhZGRpbmc6OXB4IDExcHg7Ym9yZGVyLXJhZGl1czoxMHB4O2JvcmRlcjoxcHggc29saWQgdmFyKC0tbGluZSk7CiAgYmFja2dyb3VuZDp2YXIoLS1wYW5lbCk7Y29sb3I6dmFyKC0tdHh0KTtmb250OmluaGVyaXQ7Zm9udC1zaXplOjEzcHg7Y3Vyc29yOnBvaW50ZXI7dHJhbnNpdGlvbjouMTZzfQouc2V0dXAtY2FyZCAuc2MtY29weTpob3Zlcntib3JkZXItY29sb3I6dmFyKC0tY3lhbik7Ym94LXNoYWRvdzp2YXIoLS1nbG93KX0KLnNldHVwLWNhcmQgLnNjLW1vZGVsc3tkaXNwbGF5OmZsZXg7ZmxleC13cmFwOndyYXA7Z2FwOjhweDttYXJnaW4tdG9wOjhweH0KLnNldHVwLWNhcmQgLnNjLW1vZGVse3BhZGRpbmc6NnB4IDEycHg7Ym9yZGVyLXJhZGl1czo5OTlweDtib3JkZXI6MXB4IHNvbGlkIHZhcigtLWxpbmUpOwogIGJhY2tncm91bmQ6dmFyKC0tcGFuZWwpO2NvbG9yOnZhcigtLXR4dCk7Zm9udDppbmhlcml0O2ZvbnQtc2l6ZToxMi41cHg7Y3Vyc29yOnBvaW50ZXI7dHJhbnNpdGlvbjouMTZzfQouc2V0dXAtY2FyZCAuc2MtbW9kZWw6aG92ZXJ7Ym9yZGVyLWNvbG9yOnZhcigtLWN5YW4pO2JveC1zaGFkb3c6dmFyKC0tZ2xvdyk7Y29sb3I6I2JmZjRmZn0KLnNldHVwLWNhcmQgLnNjLWFjdGlvbnN7ZGlzcGxheTpmbGV4O2FsaWduLWl0ZW1zOmNlbnRlcjtnYXA6MTBweDtmbGV4LXdyYXA6d3JhcDttYXJnaW4tdG9wOjE2cHh9Ci5zZXR1cC1jYXJkIC5zYy1yZWNoZWNre3BhZGRpbmc6OXB4IDE2cHg7Ym9yZGVyLXJhZGl1czoxMHB4O2JvcmRlcjpub25lO2N1cnNvcjpwb2ludGVyO2ZvbnQ6aW5oZXJpdDtmb250LXNpemU6MTMuNXB4O2ZvbnQtd2VpZ2h0OjYwMDsKICBiYWNrZ3JvdW5kOmxpbmVhci1ncmFkaWVudCgxMzVkZWcsdmFyKC0tY3lhbiksdmFyKC0tYmx1ZTIpKTtjb2xvcjojMDQxMDFmO2JveC1zaGFkb3c6MCAwIDE4cHggcmdiYSgzNCwyMTEsMjM4LC40KTt0cmFuc2l0aW9uOi4xNnN9Ci5zZXR1cC1jYXJkIC5zYy1yZWNoZWNrOmhvdmVye2ZpbHRlcjpicmlnaHRuZXNzKDEuMSl9Ci5zZXR1cC1jYXJkIC5zYy1yZWNoZWNrOmRpc2FibGVke29wYWNpdHk6LjU1O2N1cnNvcjp3YWl0O2JveC1zaGFkb3c6bm9uZX0KLnNldHVwLWNhcmQgLnNjLXNldHRpbmdze2ZvbnQtc2l6ZToxMi41cHg7Y29sb3I6dmFyKC0tbXV0KTtiYWNrZ3JvdW5kOm5vbmU7Ym9yZGVyOm5vbmU7Y3Vyc29yOnBvaW50ZXI7Zm9udDppbmhlcml0OwogIHRleHQtZGVjb3JhdGlvbjp1bmRlcmxpbmU7dGV4dC1kZWNvcmF0aW9uLXN0eWxlOmRvdHRlZDtwYWRkaW5nOjB9Ci5zZXR1cC1jYXJkIC5zYy1zZXR0aW5nczpob3Zlcntjb2xvcjp2YXIoLS1ibHVlMil9Ci5zZXR1cC1jYXJkIC5zYy1zdGF0ZXtmb250LXNpemU6MTIuNXB4O2NvbG9yOnZhcigtLWN5YW4pO21pbi1oZWlnaHQ6MWVtfQoKLyogPT09PT09PT09PT09PT09PT0gUXVpY2stQ2hpcHMgPT09PT09PT09PT09PT09PT0gKi8KLmNoaXBze2Rpc3BsYXk6ZmxleDtmbGV4LXdyYXA6d3JhcDtnYXA6OHB4O3BhZGRpbmc6MTBweCA0cHggOHB4fQouY2hpcHsKICBwYWRkaW5nOjdweCAxM3B4O2JvcmRlci1yYWRpdXM6OTk5cHg7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTsKICBiYWNrZ3JvdW5kOnZhcigtLXBhbmVsKTtjb2xvcjp2YXIoLS10eHQpO2ZvbnQtc2l6ZToxM3B4O2N1cnNvcjpwb2ludGVyO3RyYW5zaXRpb246LjE2czsKICBiYWNrZHJvcC1maWx0ZXI6Ymx1cig4cHgpOwp9Ci5jaGlwOmhvdmVye2JvcmRlci1jb2xvcjp2YXIoLS1jeWFuKTtib3gtc2hhZG93OnZhcigtLWdsb3cpO2NvbG9yOiNiZmY0ZmZ9Ci5jaGlwOmRpc2FibGVke29wYWNpdHk6LjQ7Y3Vyc29yOm5vdC1hbGxvd2VkO2JveC1zaGFkb3c6bm9uZX0KCi8qID09PT09PT09PT09PT09PT09IEVpbmdhYmVsZWlzdGUgPT09PT09PT09PT09PT09PT0gKi8KLmlucHV0YmFyewogIGRpc3BsYXk6ZmxleDthbGlnbi1pdGVtczpmbGV4LWVuZDtnYXA6OXB4O3BhZGRpbmc6MTBweDtib3JkZXItcmFkaXVzOjE2cHg7CiAgYm9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtiYWNrZ3JvdW5kOnZhcigtLXBhbmVsKTtiYWNrZHJvcC1maWx0ZXI6Ymx1cigxMnB4KTsKICBib3gtc2hhZG93OjAgMCAyNnB4IHJnYmEoMzQsMjExLDIzOCwuMTApOwp9CiNpbnB1dHsKICBmbGV4OjE7cmVzaXplOm5vbmU7bWF4LWhlaWdodDoxNDBweDttaW4taGVpZ2h0OjI0cHg7Ym9yZGVyOm5vbmU7b3V0bGluZTpub25lOwogIGJhY2tncm91bmQ6dHJhbnNwYXJlbnQ7Y29sb3I6dmFyKC0tdHh0KTtmb250OmluaGVyaXQ7Zm9udC1zaXplOjE0LjVweDtsaW5lLWhlaWdodDoxLjQ1OwogIHBhZGRpbmc6NnB4IDRweDsKfQojaW5wdXQ6OnBsYWNlaG9sZGVye2NvbG9yOnZhcigtLW11dCl9Ci5pYnRuewogIGZsZXg6bm9uZTt3aWR0aDo0MnB4O2hlaWdodDo0MnB4O2JvcmRlci1yYWRpdXM6MTFweDtib3JkZXI6MXB4IHNvbGlkIHZhcigtLWxpbmUpOwogIGJhY2tncm91bmQ6cmdiYSgyNTUsMjU1LDI1NSwuMDMpO2NvbG9yOnZhcigtLXR4dCk7Zm9udC1zaXplOjE4cHg7Y3Vyc29yOnBvaW50ZXI7CiAgZGlzcGxheTpncmlkO3BsYWNlLWl0ZW1zOmNlbnRlcjt0cmFuc2l0aW9uOi4xNnM7Cn0KLmlidG46aG92ZXJ7Ym9yZGVyLWNvbG9yOnZhcigtLWN5YW4pO2JveC1zaGFkb3c6dmFyKC0tZ2xvdyl9Ci5pYnRuLmFjdGl2ZXtib3JkZXItY29sb3I6dmFyKC0tY3lhbik7Y29sb3I6dmFyKC0tY3lhbik7YmFja2dyb3VuZDpyZ2JhKDM0LDIxMSwyMzgsLjEyKTtib3gtc2hhZG93OnZhcigtLWdsb3cpfQouaWJ0bi5taWMubGlzdGVuaW5ne2NvbG9yOnZhcigtLXJvc2UpO2JvcmRlci1jb2xvcjp2YXIoLS1yb3NlKTtib3gtc2hhZG93OjAgMCAxNnB4IHJnYmEoMjUxLDExMywxMzMsLjYpO2FuaW1hdGlvbjptaWNwdWxzZSAxcyBpbmZpbml0ZX0KQGtleWZyYW1lcyBtaWNwdWxzZXs1MCV7YmFja2dyb3VuZDpyZ2JhKDI1MSwxMTMsMTMzLC4xOCl9fQouaWJ0bi5zZW5kewogIGJhY2tncm91bmQ6bGluZWFyLWdyYWRpZW50KDEzNWRlZyx2YXIoLS1jeWFuKSx2YXIoLS1ibHVlMikpO2NvbG9yOiMwNDEwMWY7Ym9yZGVyOm5vbmU7CiAgYm94LXNoYWRvdzowIDAgMThweCByZ2JhKDM0LDIxMSwyMzgsLjUpOwp9Ci5pYnRuLnNlbmQ6aG92ZXJ7ZmlsdGVyOmJyaWdodG5lc3MoMS4xKX0KLmlidG46ZGlzYWJsZWR7b3BhY2l0eTouNDtjdXJzb3I6bm90LWFsbG93ZWQ7Ym94LXNoYWRvdzpub25lfQoKLyogPT09PT09PT09PT09PT09PT0gUGFuZWxzIChTbGlkZS1PdmVyKSA9PT09PT09PT09PT09PT09PSAqLwoub3ZlcmxheXtwb3NpdGlvbjpmaXhlZDtpbnNldDowO3otaW5kZXg6NDA7YmFja2dyb3VuZDpyZ2JhKDIsNCwxMCwuNik7YmFja2Ryb3AtZmlsdGVyOmJsdXIoM3B4KTsKICBvcGFjaXR5OjA7cG9pbnRlci1ldmVudHM6bm9uZTt0cmFuc2l0aW9uOi4yNXN9Ci5vdmVybGF5Lm9wZW57b3BhY2l0eToxO3BvaW50ZXItZXZlbnRzOmF1dG99Ci5wYW5lbHsKICBwb3NpdGlvbjpmaXhlZDt0b3A6MDtyaWdodDowO2hlaWdodDoxMDAlO3dpZHRoOm1pbig0NjBweCw5NHZ3KTt6LWluZGV4OjQxOwogIGJhY2tncm91bmQ6bGluZWFyLWdyYWRpZW50KDE4MGRlZyx2YXIoLS1iZzIpLHZhcigtLWJnKSk7CiAgYm9yZGVyLWxlZnQ6MXB4IHNvbGlkIHZhcigtLWxpbmUpO2JveC1zaGFkb3c6LTIwcHggMCA2MHB4IHJnYmEoMCwwLDAsLjU1KTsKICB0cmFuc2Zvcm06dHJhbnNsYXRlWCgxMDAlKTt0cmFuc2l0aW9uOnRyYW5zZm9ybSAuMjhzIGN1YmljLWJlemllciguNCwuMCwuMiwxKTsKICBkaXNwbGF5OmZsZXg7ZmxleC1kaXJlY3Rpb246Y29sdW1uOwp9Ci5wYW5lbC5vcGVue3RyYW5zZm9ybTpub25lfQoucGFuZWwtaGVhZHtkaXNwbGF5OmZsZXg7YWxpZ24taXRlbXM6Y2VudGVyO2dhcDoxMHB4O3BhZGRpbmc6MThweCAyMHB4IDEycHg7Ym9yZGVyLWJvdHRvbToxcHggc29saWQgdmFyKC0tbGluZSl9Ci5wYW5lbC1oZWFkIGgye21hcmdpbjowO2ZvbnQtc2l6ZToxN3B4O2ZvbnQtd2VpZ2h0OjcwMDtsZXR0ZXItc3BhY2luZzouNXB4fQoucGFuZWwtaGVhZCAuY2xvc2V7bWFyZ2luLWxlZnQ6YXV0bzt3aWR0aDozNHB4O2hlaWdodDozNHB4O2JvcmRlci1yYWRpdXM6OXB4O2JvcmRlcjoxcHggc29saWQgdmFyKC0tbGluZSk7CiAgYmFja2dyb3VuZDp0cmFuc3BhcmVudDtjb2xvcjp2YXIoLS10eHQpO2ZvbnQtc2l6ZToxOHB4O2N1cnNvcjpwb2ludGVyfQoucGFuZWwtaGVhZCAuY2xvc2U6aG92ZXJ7Ym9yZGVyLWNvbG9yOnZhcigtLXJvc2UpO2NvbG9yOnZhcigtLXJvc2UpfQoucGFuZWwtYm9keXtmbGV4OjE7b3ZlcmZsb3cteTphdXRvO3BhZGRpbmc6MTZweCAyMHB4IDI4cHg7c2Nyb2xsYmFyLXdpZHRoOnRoaW47c2Nyb2xsYmFyLWNvbG9yOnJnYmEoNTYsMTg5LDI0OCwuNCkgdHJhbnNwYXJlbnR9Ci5wYW5lbC1ib2R5Ojotd2Via2l0LXNjcm9sbGJhcnt3aWR0aDo4cHh9Ci5wYW5lbC1ib2R5Ojotd2Via2l0LXNjcm9sbGJhci10aHVtYntiYWNrZ3JvdW5kOnJnYmEoNTYsMTg5LDI0OCwuMzUpO2JvcmRlci1yYWRpdXM6OHB4fQoKLnNlY3R7Y29sb3I6dmFyKC0tY3lhbik7Zm9udC1zaXplOjEycHg7bGV0dGVyLXNwYWNpbmc6LjZweDt0ZXh0LXRyYW5zZm9ybTp1cHBlcmNhc2U7Zm9udC13ZWlnaHQ6NzAwO21hcmdpbjoxOHB4IDAgOHB4fQouc2VjdDpmaXJzdC1jaGlsZHttYXJnaW4tdG9wOjB9Ci5maWVsZHttYXJnaW4tYm90dG9tOjExcHh9Ci5maWVsZCBsYWJlbHtkaXNwbGF5OmJsb2NrO2ZvbnQtc2l6ZToxMnB4O2NvbG9yOnZhcigtLW11dCk7bWFyZ2luLWJvdHRvbTo0cHh9Ci5maWVsZCBpbnB1dCwuZmllbGQgc2VsZWN0LC5maWVsZCB0ZXh0YXJlYXsKICB3aWR0aDoxMDAlO3BhZGRpbmc6OXB4IDExcHg7Ym9yZGVyLXJhZGl1czo5cHg7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTsKICBiYWNrZ3JvdW5kOnJnYmEoMjU1LDI1NSwyNTUsLjAzKTtjb2xvcjp2YXIoLS10eHQpO2ZvbnQ6aW5oZXJpdDtmb250LXNpemU6MTMuNXB4O291dGxpbmU6bm9uZTsKfQouZmllbGQgaW5wdXQ6Zm9jdXMsLmZpZWxkIHNlbGVjdDpmb2N1cywuZmllbGQgdGV4dGFyZWE6Zm9jdXN7Ym9yZGVyLWNvbG9yOnZhcigtLWN5YW4pO2JveC1zaGFkb3c6MCAwIDAgMnB4IHJnYmEoMzQsMjExLDIzOCwuMTgpfQouZmllbGQgc2VsZWN0IG9wdGlvbntiYWNrZ3JvdW5kOnZhcigtLXBhbmVsLXNvbGlkKX0KLmZpZWxkIHRleHRhcmVhe3Jlc2l6ZTp2ZXJ0aWNhbDttaW4taGVpZ2h0OjU0cHh9Ci5oaW50e2ZvbnQtc2l6ZToxMS41cHg7Y29sb3I6dmFyKC0tbXV0KTtsaW5lLWhlaWdodDoxLjY7bWFyZ2luLXRvcDo2cHh9Ci5oaW50IGNvZGV7Y29sb3I6dmFyKC0tYmx1ZTIpO2JhY2tncm91bmQ6cmdiYSg1NiwxODksMjQ4LC4wOCk7cGFkZGluZzoxcHggNXB4O2JvcmRlci1yYWRpdXM6NXB4fQoKLmJ0bnsKICBwYWRkaW5nOjEwcHggMTZweDtib3JkZXItcmFkaXVzOjEwcHg7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTsKICBiYWNrZ3JvdW5kOnZhcigtLXBhbmVsKTtjb2xvcjp2YXIoLS10eHQpO2ZvbnQ6aW5oZXJpdDtmb250LXNpemU6MTMuNXB4O2ZvbnQtd2VpZ2h0OjYwMDtjdXJzb3I6cG9pbnRlcjt0cmFuc2l0aW9uOi4xNnM7Cn0KLmJ0bjpob3Zlcntib3JkZXItY29sb3I6dmFyKC0tY3lhbik7Ym94LXNoYWRvdzp2YXIoLS1nbG93KX0KLmJ0bi5wcmltYXJ5e2JhY2tncm91bmQ6bGluZWFyLWdyYWRpZW50KDEzNWRlZyx2YXIoLS1jeWFuKSx2YXIoLS1ibHVlMikpO2NvbG9yOiMwNDEwMWY7Ym9yZGVyOm5vbmU7Ym94LXNoYWRvdzowIDAgMThweCByZ2JhKDM0LDIxMSwyMzgsLjQpfQouYnRuLmRhbmdlcntib3JkZXItY29sb3I6cmdiYSgyNTEsMTEzLDEzMywuNSk7Y29sb3I6I2ZmZDlkZn0KLmJ0bi5kYW5nZXI6aG92ZXJ7Ym9yZGVyLWNvbG9yOnZhcigtLXJvc2UpO2JveC1zaGFkb3c6MCAwIDE0cHggcmdiYSgyNTEsMTEzLDEzMywuNCl9Ci5idG4uc217cGFkZGluZzo2cHggMTFweDtmb250LXNpemU6MTJweH0KLmJ0bnJvd3tkaXNwbGF5OmZsZXg7Z2FwOjlweDtmbGV4LXdyYXA6d3JhcDttYXJnaW4tdG9wOjE0cHh9CgovKiBVbXNhdHotQmFubmVyIChLdW5kZW4pICovCi5yZXZlbnVlewogIGJvcmRlcjoxcHggc29saWQgdmFyKC0tbGluZSk7Ym9yZGVyLXJhZGl1czoxM3B4O3BhZGRpbmc6MTRweCAxNnB4O21hcmdpbi1ib3R0b206MTRweDsKICBiYWNrZ3JvdW5kOmxpbmVhci1ncmFkaWVudCgxMzVkZWcscmdiYSg1MiwyMTEsMTUzLC4xMCkscmdiYSgzNCwyMTEsMjM4LC4wNikpOwp9Ci5yZXZlbnVlIC5iaWd7Zm9udC1zaXplOjI0cHg7Zm9udC13ZWlnaHQ6ODAwO2NvbG9yOnZhcigtLWdyZWVuKTt0ZXh0LXNoYWRvdzowIDAgMTZweCByZ2JhKDUyLDIxMSwxNTMsLjM1KX0KLnJldmVudWUgLnN1Yntmb250LXNpemU6MTJweDtjb2xvcjp2YXIoLS1tdXQpO21hcmdpbi10b3A6M3B4fQoKLyogS3VuZGVuLUthcnRlbiAqLwouY3VzdHtib3JkZXI6MXB4IHNvbGlkIHZhcigtLWxpbmUpO2JvcmRlci1yYWRpdXM6MTJweDtwYWRkaW5nOjEycHggMTRweDttYXJnaW4tYm90dG9tOjEwcHg7YmFja2dyb3VuZDp2YXIoLS1wYW5lbCl9Ci5jdXN0IC50b3B7ZGlzcGxheTpmbGV4O2FsaWduLWl0ZW1zOmNlbnRlcjtnYXA6OHB4O2ZsZXgtd3JhcDp3cmFwfQouY3VzdCAubmFtZXtmb250LXdlaWdodDo3MDA7Zm9udC1zaXplOjE0LjVweH0KLmN1c3QgLmJhZGdle2ZvbnQtc2l6ZToxMC41cHg7cGFkZGluZzoycHggOHB4O2JvcmRlci1yYWRpdXM6OTk5cHg7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtjb2xvcjp2YXIoLS1jeWFuKX0KLmN1c3QgLm1ldGF7Zm9udC1zaXplOjEyLjVweDtjb2xvcjp2YXIoLS1tdXQpO21hcmdpbi10b3A6NHB4O2xpbmUtaGVpZ2h0OjEuNX0KLmN1c3QgLnByaWNle2NvbG9yOnZhcigtLWdyZWVuKTtmb250LXdlaWdodDo2MDB9Ci5jdXN0IC5hY3Rpb25ze2Rpc3BsYXk6ZmxleDtnYXA6N3B4O21hcmdpbi10b3A6OXB4fQoKLyogR2Vkw6RjaHRuaXMgKi8KLmZhY3RsaXN0e2xpc3Qtc3R5bGU6bm9uZTttYXJnaW46MDtwYWRkaW5nOjB9Ci5mYWN0bGlzdCBsaXtwYWRkaW5nOjhweCAxMXB4O2JvcmRlcjoxcHggc29saWQgdmFyKC0tbGluZSk7Ym9yZGVyLXJhZGl1czo5cHg7bWFyZ2luLWJvdHRvbTo3cHg7Zm9udC1zaXplOjEzLjVweDtiYWNrZ3JvdW5kOnZhcigtLXBhbmVsKX0KLmZhY3RsaXN0IGxpOjpiZWZvcmV7Y29udGVudDoi4oCiICI7Y29sb3I6dmFyKC0tY3lhbil9Ci5qb3VybmFse2ZvbnQtc2l6ZToxMi41cHg7Y29sb3I6dmFyKC0tbXV0KTtsaW5lLWhlaWdodDoxLjd9Ci5qb3VybmFsIC5ke2NvbG9yOnZhcigtLWJsdWUyKX0KLmVtcHR5e2NvbG9yOnZhcigtLW11dCk7Zm9udC1zdHlsZTppdGFsaWM7Zm9udC1zaXplOjEzcHg7cGFkZGluZzo2cHggMH0KCkBtZWRpYShtYXgtd2lkdGg6NTYwcHgpewogIC53b3JkbWFya3tmb250LXNpemU6MjJweDtsZXR0ZXItc3BhY2luZzozcHh9CiAgLm1zZ3ttYXgtd2lkdGg6OTIlfQogIC5jb3JlLXdyYXB7aGVpZ2h0Ojk2cHh9CiAgLmNvcmV7d2lkdGg6NzhweDtoZWlnaHQ6NzhweH0KfQo8L3N0eWxlPgo8L2hlYWQ+Cjxib2R5Pgo8ZGl2IGNsYXNzPSJhcHAiPgoKICA8IS0tIEtvcGZ6ZWlsZSAtLT4KICA8ZGl2IGNsYXNzPSJoZWFkZXIiPgogICAgPGRpdiBjbGFzcz0iYnJhbmQiPgogICAgICA8ZGl2PgogICAgICAgIDxkaXYgY2xhc3M9IndvcmRtYXJrIj5ESU5PPC9kaXY+CiAgICAgICAgPGRpdiBjbGFzcz0idGFnbGluZSI+ZGVpbiBlaWdlbmVyIEphcnZpcyDCtyBsw6R1ZnQgbG9rYWw8L2Rpdj4KICAgICAgICA8ZGl2IGNsYXNzPSJzdGF0dXNsaW5lIj4KICAgICAgICAgIDxzcGFuIGlkPSJzdGF0dXNEb3QiIGNsYXNzPSJkb3QiPjwvc3Bhbj4KICAgICAgICAgIDxzcGFuIGlkPSJicmFpblRleHQiPnZlcmJpbmRl4oCmPC9zcGFuPgogICAgICAgICAgPHNwYW4gaWQ9Im9sbGFtYVBpbGwiIGNsYXNzPSJvbGxhbWEtcGlsbCIgc3R5bGU9ImRpc3BsYXk6bm9uZSI+PHNwYW4gY2xhc3M9Im9wZG90Ij48L3NwYW4+PHNwYW4gaWQ9Im9sbGFtYVBpbGxUZXh0Ij5sb2thbDwvc3Bhbj48L3NwYW4+CiAgICAgICAgPC9kaXY+CiAgICAgIDwvZGl2PgogICAgPC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJzcGFjZXIiPjwvZGl2PgogICAgPGRpdiBjbGFzcz0iaWNvbmJ0bnMiPgogICAgICA8YnV0dG9uIGNsYXNzPSJpY29uYnRuIiB0aXRsZT0iS3VuZGVuIiBvbmNsaWNrPSJvcGVuUGFuZWwoJ2N1c3RvbWVycycpIj7wn5GlPC9idXR0b24+CiAgICAgIDxidXR0b24gY2xhc3M9Imljb25idG4iIHRpdGxlPSJHZWTDpGNodG5pcyIgb25jbGljaz0ib3BlblBhbmVsKCdtZW1vcnknKSI+8J+noDwvYnV0dG9uPgogICAgICA8YnV0dG9uIGNsYXNzPSJpY29uYnRuIiB0aXRsZT0iRWluc3RlbGx1bmdlbiIgb25jbGljaz0ib3BlblBhbmVsKCdzZXR0aW5ncycpIj7impk8L2J1dHRvbj4KICAgIDwvZGl2PgogIDwvZGl2PgoKICA8IS0tIENvcmUgLyBPcmIgLS0+CiAgPGRpdiBjbGFzcz0iY29yZS13cmFwIj4KICAgIDxkaXYgY2xhc3M9ImNvcmUiIGlkPSJjb3JlIj4KICAgICAgPGRpdiBjbGFzcz0icmluZyByMSI+PC9kaXY+CiAgICAgIDxkaXYgY2xhc3M9InJpbmcgcjIiPjwvZGl2PgogICAgICA8ZGl2IGNsYXNzPSJyaW5nIHIzIj48L2Rpdj4KICAgICAgPGRpdiBjbGFzcz0ibnVjbGV1cyI+PC9kaXY+CiAgICA8L2Rpdj4KICA8L2Rpdj4KCiAgPCEtLSBDaGF0IC0tPgogIDxkaXYgY2xhc3M9ImNoYXQiIGlkPSJjaGF0Ij48L2Rpdj4KCiAgPCEtLSBRdWljay1DaGlwcyAtLT4KICA8ZGl2IGNsYXNzPSJjaGlwcyI+CiAgICA8YnV0dG9uIGNsYXNzPSJjaGlwIiBvbmNsaWNrPSJxdWlja1BsYW4oKSI+8J+ThSBXb2NoZW5wbGFuPC9idXR0b24+CiAgICA8YnV0dG9uIGNsYXNzPSJjaGlwIiBvbmNsaWNrPSJxdWlja1RvZGF5KCkiPuKYgO+4jyBIZXV0ZTwvYnV0dG9uPgogICAgPGJ1dHRvbiBjbGFzcz0iY2hpcCIgb25jbGljaz0icXVpY2tMZWFybigpIj7wn6egIExlcm5lbjwvYnV0dG9uPgogICAgPGJ1dHRvbiBjbGFzcz0iY2hpcCIgb25jbGljaz0icXVpY2tDb3VuY2lsKCkiPvCfp6Dwn6eg8J+noCBSYXQgZGVyIEtJczwvYnV0dG9uPgogIDwvZGl2PgoKICA8IS0tIEVpbmdhYmVsZWlzdGUgLS0+CiAgPGRpdiBjbGFzcz0iaW5wdXRiYXIiPgogICAgPHRleHRhcmVhIGlkPSJpbnB1dCIgcm93cz0iMSIgcGxhY2Vob2xkZXI9IlNjaHJlaWIgRGlubyB3YXPigKYgKEVudGVyIHNlbmRlbiDCtyBTaGlmdCtFbnRlciBuZXVlIFplaWxlKSI+PC90ZXh0YXJlYT4KICAgIDxidXR0b24gY2xhc3M9ImlidG4gbWljIiBpZD0ibWljQnRuIiB0aXRsZT0iU3ByZWNoZW4iIG9uY2xpY2s9InRvZ2dsZU1pYygpIj7wn46kPC9idXR0b24+CiAgICA8YnV0dG9uIGNsYXNzPSJpYnRuIiBpZD0idm9pY2VCdG4iIHRpdGxlPSJTcHJhY2hhdXNnYWJlIiBvbmNsaWNrPSJ0b2dnbGVWb2ljZSgpIj7wn5SKPC9idXR0b24+CiAgICA8YnV0dG9uIGNsYXNzPSJpYnRuIHNlbmQiIGlkPSJzZW5kQnRuIiB0aXRsZT0iU2VuZGVuIiBvbmNsaWNrPSJzZW5kKCkiPuKepDwvYnV0dG9uPgogIDwvZGl2Pgo8L2Rpdj4KCjwhLS0gPT09PT09PT09PT09PT09PT09PT09IFBhbmVscyA9PT09PT09PT09PT09PT09PT09PT0gLS0+CjxkaXYgY2xhc3M9Im92ZXJsYXkiIGlkPSJvdmVybGF5IiBvbmNsaWNrPSJjbG9zZVBhbmVscygpIj48L2Rpdj4KCjwhLS0gRWluc3RlbGx1bmdlbiAtLT4KPGFzaWRlIGNsYXNzPSJwYW5lbCIgaWQ9InBhbmVsLXNldHRpbmdzIj4KICA8ZGl2IGNsYXNzPSJwYW5lbC1oZWFkIj48c3Bhbj7impk8L3NwYW4+PGgyPkVpbnN0ZWxsdW5nZW48L2gyPjxidXR0b24gY2xhc3M9ImNsb3NlIiBvbmNsaWNrPSJjbG9zZVBhbmVscygpIj7inJU8L2J1dHRvbj48L2Rpdj4KICA8ZGl2IGNsYXNzPSJwYW5lbC1ib2R5IiBpZD0ic2V0dGluZ3NCb2R5Ij48ZGl2IGNsYXNzPSJlbXB0eSI+bMOkZHTigKY8L2Rpdj48L2Rpdj4KPC9hc2lkZT4KCjwhLS0gS3VuZGVuIC0tPgo8YXNpZGUgY2xhc3M9InBhbmVsIiBpZD0icGFuZWwtY3VzdG9tZXJzIj4KICA8ZGl2IGNsYXNzPSJwYW5lbC1oZWFkIj48c3Bhbj7wn5GlPC9zcGFuPjxoMj5LdW5kZW48L2gyPjxidXR0b24gY2xhc3M9ImNsb3NlIiBvbmNsaWNrPSJjbG9zZVBhbmVscygpIj7inJU8L2J1dHRvbj48L2Rpdj4KICA8ZGl2IGNsYXNzPSJwYW5lbC1ib2R5IiBpZD0iY3VzdG9tZXJzQm9keSI+PGRpdiBjbGFzcz0iZW1wdHkiPmzDpGR04oCmPC9kaXY+PC9kaXY+CjwvYXNpZGU+Cgo8IS0tIEdlZMOkY2h0bmlzIC0tPgo8YXNpZGUgY2xhc3M9InBhbmVsIiBpZD0icGFuZWwtbWVtb3J5Ij4KICA8ZGl2IGNsYXNzPSJwYW5lbC1oZWFkIj48c3Bhbj7wn6egPC9zcGFuPjxoMj5HZWTDpGNodG5pczwvaDI+PGJ1dHRvbiBjbGFzcz0iY2xvc2UiIG9uY2xpY2s9ImNsb3NlUGFuZWxzKCkiPuKclTwvYnV0dG9uPjwvZGl2PgogIDxkaXYgY2xhc3M9InBhbmVsLWJvZHkiIGlkPSJtZW1vcnlCb2R5Ij48ZGl2IGNsYXNzPSJlbXB0eSI+bMOkZHTigKY8L2Rpdj48L2Rpdj4KPC9hc2lkZT4KCjxzY3JpcHQ+CiJ1c2Ugc3RyaWN0IjsKLyogPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09CiAgIERJTk8gS0kg4oCUIEZyb250ZW5kLUxvZ2lrCiAgIFNwcmljaHQgcGVyIGZldGNoKCkgbWl0IGRlbSBsb2thbGVuIFNlcnZlciAoZ2xlaWNoZXIgT3JpZ2luKS4KICAgPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09ICovCgovLyAtLS0tIFp1c3RhbmQgLS0tLQpjb25zdCBzdGF0ZSA9IHsKICBtZXNzYWdlczogW10sICAgICAgICAgIC8vIENoYXQtSGlzdG9yaWUge3JvbGUsIGNvbnRlbnR9CiAgcmVhZHk6IGZhbHNlLAogIGFzc2lzdGFudE5hbWU6ICJEaW5vIiwKICB1c2VyTmFtZTogIkJvc3MiLAogIGJ1c3k6IGZhbHNlLAogIHZvaWNlT246IGZhbHNlLCAgICAgICAgLy8gU3ByYWNoYXVzZ2FiZSBhbi9hdXMKICBzdGF0dXNWYWx1ZXM6IFsiTGVhZCIsIkFuZ2Vib3QiLCJBa3RpdiIsIkJlemFobHQiLCJQYXVzaWVydCIsIkJlZW5kZXQiXSwKICBwcm92aWRlcjogbnVsbCwgICAgICAgIC8vICJvbGxhbWEiIHwgImNsYXVkZSIgfCAib3BlbmFpIiB8ICJnZW1pbmkiCiAgYXV0b1JlY2hlY2tEb25lOiBmYWxzZSwvLyBlaW5tYWxpZ2VzIEF1dG8tUmVjaGVjayBiZWltIGVyc3RlbiBMYWRlbgp9OwoKLy8gLS0tLSBET00tS3VyemhlbGZlciAtLS0tCmNvbnN0ICQgPSAoaWQpID0+IGRvY3VtZW50LmdldEVsZW1lbnRCeUlkKGlkKTsKY29uc3QgY2hhdEVsID0gJCgiY2hhdCIpOwpjb25zdCBjb3JlRWwgPSAkKCJjb3JlIik7CmNvbnN0IGlucHV0RWwgPSAkKCJpbnB1dCIpOwoKLy8gLS0tLSBIaWxmc2Z1bmt0aW9uZW4gLS0tLQpmdW5jdGlvbiBldXJvKHgpewogIGNvbnN0IG4gPSBOdW1iZXIoeCkgfHwgMDsKICByZXR1cm4gbi50b0xvY2FsZVN0cmluZygiZGUtREUiLHttYXhpbXVtRnJhY3Rpb25EaWdpdHM6MH0pICsgIiDigqwiOwp9CmZ1bmN0aW9uIGVzYyhzKXsgLy8gd2lyIG51dHplbiBvaG5laGluIHRleHRDb250ZW50LCBkaWVzIG51ciBmw7xyIHNpY2hlcmUgQXR0cmlidXQtZnJlaWUgQW56ZWlnZQogIHJldHVybiBTdHJpbmcocyA9PSBudWxsID8gIiIgOiBzKTsKfQoKLy8gLS0tLSBDb3JlLUFuaW1hdGlvbmVuIC0tLS0KZnVuY3Rpb24gc2V0VGhpbmtpbmcob24peyBjb3JlRWwuY2xhc3NMaXN0LnRvZ2dsZSgidGhpbmtpbmciLCBvbik7IH0KZnVuY3Rpb24gc2V0U3BlYWtpbmcob24peyBjb3JlRWwuY2xhc3NMaXN0LnRvZ2dsZSgic3BlYWtpbmciLCBvbik7IH0KCi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQovLyAgQ2hhdC1BbnplaWdlCi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQovKioKICogRsO8Z3QgZWluZSBCdWJibGUgaGluenUuIEluaGFsdCB3aXJkIHZpYSB0ZXh0Q29udGVudCBnZXNldHp0IChrZWluIFhTUykuCiAqIGtpbmQ6ICJkaW5vIiB8ICJ1c2VyIiB8ICJpbmZvIiB8ICJlcnJvciIgfCAic3ludGgiIHwgImNvdW5jaWwiCiAqIGxhYmVsOiBvcHRpb25hbGVzIExhYmVsICh6LkIuIEtJLU5hbWUpCiAqLwpmdW5jdGlvbiBhZGRCdWJibGUoa2luZCwgdGV4dCwgbGFiZWwpewogIGNvbnN0IHdyYXAgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsKICBjb25zdCBjbHMgPSAoa2luZCA9PT0gInN5bnRoIiB8fCBraW5kID09PSAiY291bmNpbCIpID8gImRpbm8iIDoga2luZDsKICB3cmFwLmNsYXNzTmFtZSA9ICJtc2cgIiArIChraW5kID09PSAic3ludGgiID8gImRpbm8gc3ludGgiIDogY2xzKTsKCiAgLy8gQXZhdGFyIG51ciBmw7xyIERpbm8tL051dHplci0vRmVobGVyLUJ1YmJsZXMKICBpZiAoa2luZCA9PT0gImRpbm8iIHx8IGtpbmQgPT09ICJzeW50aCIgfHwga2luZCA9PT0gImNvdW5jaWwiKXsKICAgIGNvbnN0IGEgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgYS5jbGFzc05hbWU9ImF2YXRhciI7IGEudGV4dENvbnRlbnQ9IvCfppYiOyB3cmFwLmFwcGVuZENoaWxkKGEpOwogIH0gZWxzZSBpZiAoa2luZCA9PT0gInVzZXIiKXsKICAgIGNvbnN0IGEgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgYS5jbGFzc05hbWU9ImF2YXRhciI7IGEudGV4dENvbnRlbnQ9IvCfp5EiOyB3cmFwLmFwcGVuZENoaWxkKGEpOwogIH0gZWxzZSBpZiAoa2luZCA9PT0gImVycm9yIil7CiAgICBjb25zdCBhID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IGEuY2xhc3NOYW1lPSJhdmF0YXIiOyBhLnRleHRDb250ZW50PSLimqDvuI8iOyB3cmFwLmFwcGVuZENoaWxkKGEpOwogIH0KCiAgY29uc3QgYiA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBiLmNsYXNzTmFtZT0iYnViYmxlIjsKICBpZiAobGFiZWwpewogICAgY29uc3QgbCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBsLmNsYXNzTmFtZT0ibGFiZWwiOyBsLnRleHRDb250ZW50ID0gbGFiZWw7CiAgICBiLmFwcGVuZENoaWxkKGwpOwogICAgY29uc3QgdCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyB0LnRleHRDb250ZW50ID0gdGV4dDsgYi5hcHBlbmRDaGlsZCh0KTsKICB9IGVsc2UgewogICAgYi50ZXh0Q29udGVudCA9IHRleHQ7CiAgfQogIHdyYXAuYXBwZW5kQ2hpbGQoYik7CiAgY2hhdEVsLmFwcGVuZENoaWxkKHdyYXApOwogIHNjcm9sbERvd24oKTsKICByZXR1cm4gd3JhcDsKfQoKZnVuY3Rpb24gc2Nyb2xsRG93bigpeyByZXF1ZXN0QW5pbWF0aW9uRnJhbWUoKCk9PnsgY2hhdEVsLnNjcm9sbFRvcCA9IGNoYXRFbC5zY3JvbGxIZWlnaHQ7IH0pOyB9CgovLyBUaXBwLUluZGlrYXRvcgpsZXQgdHlwaW5nRWwgPSBudWxsOwpmdW5jdGlvbiBzaG93VHlwaW5nKCl7CiAgaWYgKHR5cGluZ0VsKSByZXR1cm47CiAgdHlwaW5nRWwgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsKICB0eXBpbmdFbC5jbGFzc05hbWUgPSAibXNnIGRpbm8iOwogIHR5cGluZ0VsLmlubmVySFRNTCA9ICc8ZGl2IGNsYXNzPSJhdmF0YXIiPvCfppY8L2Rpdj48ZGl2IGNsYXNzPSJidWJibGUiPjxkaXYgY2xhc3M9InR5cGluZyI+PHNwYW4+PC9zcGFuPjxzcGFuPjwvc3Bhbj48c3Bhbj48L3NwYW4+PC9kaXY+PC9kaXY+JzsKICBjaGF0RWwuYXBwZW5kQ2hpbGQodHlwaW5nRWwpOwogIHNjcm9sbERvd24oKTsKfQpmdW5jdGlvbiBoaWRlVHlwaW5nKCl7IGlmICh0eXBpbmdFbCl7IHR5cGluZ0VsLnJlbW92ZSgpOyB0eXBpbmdFbCA9IG51bGw7IH0gfQoKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09Ci8vICBOZXR6d2VyawovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KYXN5bmMgZnVuY3Rpb24gYXBpKHBhdGgsIG1ldGhvZCwgYm9keSl7CiAgY29uc3Qgb3B0ID0geyBtZXRob2Q6IG1ldGhvZCB8fCAiR0VUIiwgaGVhZGVyczp7fSB9OwogIGlmIChib2R5ICE9PSB1bmRlZmluZWQpeyBvcHQuaGVhZGVyc1siQ29udGVudC1UeXBlIl09ImFwcGxpY2F0aW9uL2pzb24iOyBvcHQuYm9keSA9IEpTT04uc3RyaW5naWZ5KGJvZHkpOyB9CiAgY29uc3QgcmVzID0gYXdhaXQgZmV0Y2gocGF0aCwgb3B0KTsKICAvLyBWZXJzdWNoZSBKU09OIHp1IGxlc2VuIOKAkyBhdWNoIGJlaSA0eHgvNXh4IGthbm4gZWluIHtlcnJvcn0ga29tbWVuCiAgbGV0IGRhdGE7CiAgdHJ5IHsgZGF0YSA9IGF3YWl0IHJlcy5qc29uKCk7IH0KICBjYXRjaChlKXsgdGhyb3cgbmV3IEVycm9yKCJVbmfDvGx0aWdlIEFudHdvcnQgdm9tIFNlcnZlciAoa2VpbiBKU09OKS4iKTsgfQogIHJldHVybiBkYXRhOwp9CgovLyBCdXN5LVp1c3RhbmQgKHNwZXJydCBTZW5kZW4gKyBDaGlwcyB3w6RocmVuZCBlaW5lciBBbmZyYWdlKQpmdW5jdGlvbiBzZXRCdXN5KG9uKXsKICBzdGF0ZS5idXN5ID0gb247CiAgc2V0VGhpbmtpbmcob24pOwogICQoInNlbmRCdG4iKS5kaXNhYmxlZCA9IG9uOwogIGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3JBbGwoIi5jaGlwIikuZm9yRWFjaChjID0+IGMuZGlzYWJsZWQgPSBvbik7CiAgaWYgKG9uKSBzaG93VHlwaW5nKCk7IGVsc2UgaGlkZVR5cGluZygpOwp9CgovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KLy8gIFN0YXJ0OiBTdGF0dXMgbGFkZW4KLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09CmFzeW5jIGZ1bmN0aW9uIGxvYWRTdGF0dXMoKXsKICB0cnl7CiAgICBjb25zdCBzID0gYXdhaXQgYXBpKCIvYXBpL3N0YXR1cyIpOwogICAgaWYgKHMuZXJyb3IpeyBtYXJrU3RhdHVzKGZhbHNlLCAiRmVobGVyOiAiK3MuZXJyb3IpOyByZXR1cm47IH0KICAgIHN0YXRlLnJlYWR5ID0gISFzLnJlYWR5OwogICAgc3RhdGUuYXNzaXN0YW50TmFtZSA9IHMuYXNzaXN0YW50X25hbWUgfHwgIkRpbm8iOwogICAgc3RhdGUudXNlck5hbWUgPSBzLnVzZXJfbmFtZSB8fCAiQm9zcyI7CiAgICBzdGF0ZS5wcm92aWRlciA9IHMucHJvdmlkZXIgfHwgbnVsbDsKICAgIG1hcmtTdGF0dXMocy5yZWFkeSwgcy5icmFpbiB8fCAi4oCUIik7CgogICAgaWYgKHN0YXRlLnByb3ZpZGVyID09PSAib2xsYW1hIil7CiAgICAgIC8vIExva2FsZXMgR2VoaXJuIC0+IGVpZ2VuZSBPbmJvYXJkaW5nLS9TZXR1cC1Mb2dpayAoa8O8bW1lcnQgc2ljaCB1bSBCZWdyw7zDn3VuZy9LYXJ0ZSkKICAgICAgYXdhaXQgY2hlY2tPbGxhbWEoKTsKICAgICAgcmV0dXJuOwogICAgfQoKICAgIC8vIEFuZGVyZSBBbmJpZXRlciAoQ2xhdWRlIGV0Yy4pOiBWZXJoYWx0ZW4gd2llIGJpc2hlcgogICAgaGlkZU9sbGFtYVBpbGwoKTsKICAgIGlmICghc3RhdGUucmVhZHkpewogICAgICAvLyBOaWNodCBiZXJlaXQgLT4gZnJldW5kbGljaGUgU3RhcnRuYWNocmljaHQgKyBFaW5zdGVsbHVuZ2VuIMO2ZmZuZW4KICAgICAgaWYgKGNoYXRFbC5jaGlsZHJlbi5sZW5ndGggPT09IDApCiAgICAgICAgYWRkQnViYmxlKCJkaW5vIiwgIlRyYWcgenVlcnN0IGRlaW5lbiBBUEktU2NobMO8c3NlbCB1bnRlciDimpkgZWluLCBkYW5uIGxlZ2UgaWNoIGxvcy4g8J+mliIpOwogICAgICBvcGVuUGFuZWwoInNldHRpbmdzIik7CiAgICB9IGVsc2UgaWYgKGNoYXRFbC5jaGlsZHJlbi5sZW5ndGggPT09IDApewogICAgICAvLyBCZXJlaXQgLT4gQmVncsO8w591bmcKICAgICAgZ3JlZXQoKTsKICAgIH0KICB9Y2F0Y2goZSl7CiAgICBtYXJrU3RhdHVzKGZhbHNlLCAib2ZmbGluZSIpOwogICAgYWRkQnViYmxlKCJlcnJvciIsICJLb21tZSBuaWNodCBhbiBkZW4gRGluby1TZXJ2ZXIgcmFuICgiK2UubWVzc2FnZSsiKS4gTMOkdWZ0IGRlciBsb2thbGUgU2VydmVyPyIpOwogIH0KfQoKZnVuY3Rpb24gbWFya1N0YXR1cyhyZWFkeSwgYnJhaW4pewogIGNvbnN0IGRvdCA9ICQoInN0YXR1c0RvdCIpOwogIGRvdC5jbGFzc05hbWUgPSAiZG90ICIgKyAocmVhZHkgPyAib2siIDogImJhZCIpOwogICQoImJyYWluVGV4dCIpLnRleHRDb250ZW50ID0gYnJhaW4gKyAocmVhZHkgPyAiICDCtyAgb25saW5lIiA6ICIgIMK3ICBvZmZsaW5lIik7Cn0KCi8vIEJlZ3LDvMOfdW5nIChudXIgZmFsbHMgQ2hhdCBub2NoIGxlZXIpIOKAlCB6ZW50cmFsLCBkYW1pdCDDvGJlcmFsbCB3aWVkZXJ2ZXJ3ZW5kYmFyCmZ1bmN0aW9uIGdyZWV0KCl7CiAgaWYgKGNoYXRFbC5jaGlsZHJlbi5sZW5ndGggPT09IDApCiAgICBhZGRCdWJibGUoImRpbm8iLCBgRGlubyBpc3Qgb25saW5lLCAke3N0YXRlLnVzZXJOYW1lfSEgV29yYXVmIGhhc3QgZHUgQm9jaz8g4pqhYCk7Cn0KCi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQovLyAgT2xsYW1hLU9uYm9hcmRpbmcgKGxva2FsZXMgR2VoaXJuKQovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KY29uc3QgT0xMQU1BX0RFRkFVTFRfTU9ERUwgPSAibGxhbWEzLjIiOwpsZXQgc2V0dXBDYXJkRWwgPSBudWxsOwoKLy8gVG9sZXJhbnQ6IGdpbHQgY3VycmVudF9tb2RlbCBhbHMgaW5zdGFsbGllcnQ/ICh6LkIuICJsbGFtYTMuMiIgbWF0Y2h0ICJsbGFtYTMuMjpsYXRlc3QiKQpmdW5jdGlvbiBtb2RlbEluc3RhbGxlZChtb2RlbHMsIGN1cnJlbnQpewogIGlmICghQXJyYXkuaXNBcnJheShtb2RlbHMpIHx8ICFtb2RlbHMubGVuZ3RoKSByZXR1cm4gZmFsc2U7CiAgaWYgKCFjdXJyZW50KSByZXR1cm4gZmFsc2U7CiAgcmV0dXJuIG1vZGVscy5zb21lKG0gPT4gewogICAgY29uc3QgYSA9IFN0cmluZyhtKSwgYiA9IFN0cmluZyhjdXJyZW50KTsKICAgIHJldHVybiBhID09PSBiIHx8IGEuc3RhcnRzV2l0aChiKSB8fCBiLnN0YXJ0c1dpdGgoYSk7CiAgfSk7Cn0KCi8vIGtsZWluZXIgU3RhdHVzLUluZGlrYXRvciBvYmVuCmZ1bmN0aW9uIHNldE9sbGFtYVBpbGwoa2luZCwgbGFiZWwpewogIGNvbnN0IHBpbGwgPSAkKCJvbGxhbWFQaWxsIik7CiAgaWYgKCFwaWxsKSByZXR1cm47CiAgcGlsbC5zdHlsZS5kaXNwbGF5ID0gImlubGluZS1mbGV4IjsKICBwaWxsLmNsYXNzTmFtZSA9ICJvbGxhbWEtcGlsbCAiICsgKGtpbmQgfHwgIiIpOwogICQoIm9sbGFtYVBpbGxUZXh0IikudGV4dENvbnRlbnQgPSBsYWJlbDsKfQpmdW5jdGlvbiBoaWRlT2xsYW1hUGlsbCgpewogIGNvbnN0IHBpbGwgPSAkKCJvbGxhbWFQaWxsIik7CiAgaWYgKHBpbGwpIHBpbGwuc3R5bGUuZGlzcGxheSA9ICJub25lIjsKfQoKLy8gRW50ZmVybnQgZWluZSBnZ2YuIHZvcmhhbmRlbmUgU2V0dXAtS2FydGUKZnVuY3Rpb24gcmVtb3ZlU2V0dXBDYXJkKCl7CiAgaWYgKHNldHVwQ2FyZEVsKXsgc2V0dXBDYXJkRWwucmVtb3ZlKCk7IHNldHVwQ2FyZEVsID0gbnVsbDsgfQp9CgovLyBQcsO8ZnQgL2FwaS9vbGxhbWEgdW5kIGVudHNjaGVpZGV0IMO8YmVyIEthcnRlL0JlZ3LDvMOfdW5nCmFzeW5jIGZ1bmN0aW9uIGNoZWNrT2xsYW1hKCl7CiAgbGV0IG87CiAgdHJ5ewogICAgbyA9IGF3YWl0IGFwaSgiL2FwaS9vbGxhbWEiKTsKICB9Y2F0Y2goZSl7CiAgICAvLyBLb25udGUgT2xsYW1hLUluZm8gbmljaHQgbGFkZW4gLT4gYmVoYW5kZWxuIHdpZSAibMOkdWZ0IG5pY2h0IgogICAgbyA9IHsgcnVubmluZzpmYWxzZSwgbW9kZWxzOltdLCBjdXJyZW50X21vZGVsOk9MTEFNQV9ERUZBVUxUX01PREVMIH07CiAgfQogIGlmIChvICYmIG8uZXJyb3IpeyBvID0geyBydW5uaW5nOmZhbHNlLCBtb2RlbHM6W10sIGN1cnJlbnRfbW9kZWw6T0xMQU1BX0RFRkFVTFRfTU9ERUwgfTsgfQoKICBjb25zdCBydW5uaW5nID0gISEobyAmJiBvLnJ1bm5pbmcpOwogIGNvbnN0IG1vZGVscyA9IChvICYmIEFycmF5LmlzQXJyYXkoby5tb2RlbHMpKSA/IG8ubW9kZWxzIDogW107CiAgY29uc3QgY3VycmVudCA9IChvICYmIG8uY3VycmVudF9tb2RlbCkgfHwgT0xMQU1BX0RFRkFVTFRfTU9ERUw7CiAgY29uc3QgaGFzTW9kZWwgPSBtb2RlbEluc3RhbGxlZChtb2RlbHMsIGN1cnJlbnQpOwoKICBpZiAocnVubmluZyAmJiBoYXNNb2RlbCl7CiAgICAvLyBBbGxlcyBiZXJlaXQgLT4ga2VpbmUgS2FydGUsIG5vcm1hbGUgQmVncsO8w591bmcKICAgIHNldE9sbGFtYVBpbGwoIm9rIiwgImxva2FsIGFrdGl2Iik7CiAgICByZW1vdmVTZXR1cENhcmQoKTsKICAgIGdyZWV0KCk7CiAgICByZXR1cm4gdHJ1ZTsKICB9CgogIGlmICghcnVubmluZyl7CiAgICBzZXRPbGxhbWFQaWxsKCJiYWQiLCAiU2V0dXAgbsO2dGlnIik7CiAgICBzaG93U2V0dXBDYXJkKCJub3QtcnVubmluZyIsIHsgbW9kZWxzLCBjdXJyZW50IH0pOwogIH0gZWxzZSB7CiAgICAvLyBsw6R1ZnQsIGFiZXIga2VpbiBwYXNzZW5kZXMgTW9kZWxsCiAgICBzZXRPbGxhbWFQaWxsKCJ3YXJuIiwgIk1vZGVsbCBmZWhsdCIpOwogICAgc2hvd1NldHVwQ2FyZCgibm8tbW9kZWwiLCB7IG1vZGVscywgY3VycmVudCB9KTsKICB9CgogIC8vIEVpbm1hbGlnZXMgQXV0by1SZWNoZWNrIG5hY2ggfjJzIGJlaW0gZXJzdGVuIExhZGVuIChrZWluIERhdWVyLVBvbGxpbmcpCiAgaWYgKCFzdGF0ZS5hdXRvUmVjaGVja0RvbmUpewogICAgc3RhdGUuYXV0b1JlY2hlY2tEb25lID0gdHJ1ZTsKICAgIHNldFRpbWVvdXQoKCk9PnsgaWYgKHNldHVwQ2FyZEVsKSByZWNoZWNrT2xsYW1hKCk7IH0sIDIwMDApOwogIH0KICByZXR1cm4gZmFsc2U7Cn0KCi8vIEJhdXQvYWt0dWFsaXNpZXJ0IGRpZSBTZXR1cC1LYXJ0ZSAoc3RhdGlzY2hlcyBNYXJrdXAgPSBpbm5lckhUTUw7IGR5bmFtaXNjaGUgVGV4dGUgdmlhIHRleHRDb250ZW50KQpmdW5jdGlvbiBzaG93U2V0dXBDYXJkKG1vZGUsIGluZm8pewogIHJlbW92ZVNldHVwQ2FyZCgpOwogIGNvbnN0IGNhcmQgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsKICBjYXJkLmNsYXNzTmFtZSA9ICJzZXR1cC1jYXJkIjsKCiAgaWYgKG1vZGUgPT09ICJuby1tb2RlbCIpewogICAgY2FyZC5pbm5lckhUTUwgPSBgCiAgICAgIDxkaXYgY2xhc3M9InNjLXRpdGxlIj7wn6egIERpbm8gZmVobHQgbm9jaCBlaW4gTW9kZWxsPC9kaXY+CiAgICAgIDxkaXYgY2xhc3M9InNjLXN1YiI+T2xsYW1hIGzDpHVmdCBzY2hvbiDigJQgRGlubyBicmF1Y2h0IG51ciBub2NoIGVpbiBTcHJhY2htb2RlbGwuIEhvbCBkaXIgZGFzIFN0YW5kYXJkbW9kZWxsIG9kZXIgd8OkaGwgZWlucyBkZXIgaW5zdGFsbGllcnRlbi48L2Rpdj4KICAgICAgPGRpdiBjbGFzcz0ic2Mtc3RlcCI+CiAgICAgICAgPGRpdiBjbGFzcz0ic2Mtc3RlcC1oIj48c3BhbiBjbGFzcz0ibnVtIj7ihpM8L3NwYW4+PHNwYW4+TW9kZWxsIGxhZGVuIChncmF0aXMpPC9zcGFuPjwvZGl2PgogICAgICAgIDxkaXYgY2xhc3M9InNjLWNvZGVib3giPgogICAgICAgICAgPGNvZGUgY2xhc3M9InNjLWNvZGUiIGlkPSJzYy1jbWQiPjwvY29kZT4KICAgICAgICAgIDxidXR0b24gY2xhc3M9InNjLWNvcHkiIGlkPSJzYy1jb3B5Ij7wn5OLIEtvcGllcmVuPC9idXR0b24+CiAgICAgICAgPC9kaXY+CiAgICAgICAgPGRpdiBjbGFzcz0ic2MtbW9kZWxzIiBpZD0ic2MtbW9kZWxzIj48L2Rpdj4KICAgICAgPC9kaXY+CiAgICAgIDxkaXYgY2xhc3M9InNjLWFjdGlvbnMiPgogICAgICAgIDxidXR0b24gY2xhc3M9InNjLXJlY2hlY2siIGlkPSJzYy1yZWNoZWNrIj7wn5SEIE5vY2htYWwgcHLDvGZlbjwvYnV0dG9uPgogICAgICAgIDxzcGFuIGNsYXNzPSJzYy1zdGF0ZSIgaWQ9InNjLXN0YXRlIj48L3NwYW4+CiAgICAgIDwvZGl2PgogICAgYDsKICB9IGVsc2UgewogICAgY2FyZC5pbm5lckhUTUwgPSBgCiAgICAgIDxkaXYgY2xhc3M9InNjLXRpdGxlIj7wn6aWIEZhc3QgZmVydGlnIOKAlCBEaW5vIGJyYXVjaHQgbm9jaCBzZWluIEdlaGlybjwvZGl2PgogICAgICA8ZGl2IGNsYXNzPSJzYy1zdWIiPkRpbm8gbMOkdWZ0IHN0YW5kYXJkbcOkw59pZyBncmF0aXMgdW5kIGxva2FsIMO8YmVyIE9sbGFtYS4gWndlaSBrdXJ6ZSBTY2hyaXR0ZSwgZGFubiBnZWh0J3MgbG9zLjwvZGl2PgogICAgICA8ZGl2IGNsYXNzPSJzYy1zdGVwIj4KICAgICAgICA8ZGl2IGNsYXNzPSJzYy1zdGVwLWgiPjxzcGFuIGNsYXNzPSJudW0iPjE8L3NwYW4+PHNwYW4+T2xsYW1hIGluc3RhbGxpZXJlbiAoZ3JhdGlzKTwvc3Bhbj48L2Rpdj4KICAgICAgICA8ZGl2IGNsYXNzPSJzYy1zdWIiIHN0eWxlPSJtYXJnaW46MCI+CiAgICAgICAgICBMYWRlIGVzIGhpZXIgaGVydW50ZXI6IDxhIGNsYXNzPSJzYy1saW5rIiBpZD0ic2MtZGwiIGhyZWY9Imh0dHBzOi8vb2xsYW1hLmNvbS9kb3dubG9hZCIgdGFyZ2V0PSJfYmxhbmsiIHJlbD0ibm9vcGVuZXIgbm9yZWZlcnJlciI+b2xsYW1hLmNvbS9kb3dubG9hZDwvYT4KICAgICAgICA8L2Rpdj4KICAgICAgPC9kaXY+CiAgICAgIDxkaXYgY2xhc3M9InNjLXN0ZXAiPgogICAgICAgIDxkaXYgY2xhc3M9InNjLXN0ZXAtaCI+PHNwYW4gY2xhc3M9Im51bSI+Mjwvc3Bhbj48c3Bhbj5EaWVzZXMgS29tbWFuZG8gaW0gVGVybWluYWwgLyBpbiBkZXIgRWluZ2FiZWF1ZmZvcmRlcnVuZyBhdXNmw7xocmVuOjwvc3Bhbj48L2Rpdj4KICAgICAgICA8ZGl2IGNsYXNzPSJzYy1jb2RlYm94Ij4KICAgICAgICAgIDxjb2RlIGNsYXNzPSJzYy1jb2RlIiBpZD0ic2MtY21kIj48L2NvZGU+CiAgICAgICAgICA8YnV0dG9uIGNsYXNzPSJzYy1jb3B5IiBpZD0ic2MtY29weSI+8J+TiyBLb3BpZXJlbjwvYnV0dG9uPgogICAgICAgIDwvZGl2PgogICAgICA8L2Rpdj4KICAgICAgPGRpdiBjbGFzcz0ic2MtYWN0aW9ucyI+CiAgICAgICAgPGJ1dHRvbiBjbGFzcz0ic2MtcmVjaGVjayIgaWQ9InNjLXJlY2hlY2siPvCflIQgTm9jaG1hbCBwcsO8ZmVuPC9idXR0b24+CiAgICAgICAgPGJ1dHRvbiBjbGFzcz0ic2Mtc2V0dGluZ3MiIGlkPSJzYy1zZXR0aW5ncyI+TGllYmVyIGRlbiBzdGFya2VuIENsYXVkZSBudXR6ZW4/IOKGkiDimpkgRWluc3RlbGx1bmdlbjwvYnV0dG9uPgogICAgICAgIDxzcGFuIGNsYXNzPSJzYy1zdGF0ZSIgaWQ9InNjLXN0YXRlIj48L3NwYW4+CiAgICAgIDwvZGl2PgogICAgYDsKICB9CgogIC8vIEthcnRlIG9iZW4gaW0gQ2hhdCBwbGF0emllcmVuLCBkYW1pdCBzaWUgZ3V0IHNpY2h0YmFyIGlzdAogIGNoYXRFbC5wcmVwZW5kKGNhcmQpOwogIHNldHVwQ2FyZEVsID0gY2FyZDsKICBzY3JvbGxEb3duKCk7CgogIC8vIEtvbW1hbmRvLVRleHQgKGR5bmFtaXNjaCAtPiB0ZXh0Q29udGVudCwga2VpbiBpbm5lckhUTUwpCiAgY29uc3QgY21kID0gKG1vZGUgPT09ICJuby1tb2RlbCIpCiAgICA/ICgib2xsYW1hIHB1bGwgIiArIChpbmZvICYmIGluZm8uY3VycmVudCA/IGluZm8uY3VycmVudCA6IE9MTEFNQV9ERUZBVUxUX01PREVMKSkKICAgIDogKCJvbGxhbWEgcnVuICIgKyBPTExBTUFfREVGQVVMVF9NT0RFTCk7CiAgY29uc3QgY21kRWwgPSBjYXJkLnF1ZXJ5U2VsZWN0b3IoIiNzYy1jbWQiKTsKICBpZiAoY21kRWwpIGNtZEVsLnRleHRDb250ZW50ID0gY21kOwoKICAvLyBLb3BpZXJlbi1CdXR0b24KICBjb25zdCBjb3B5QnRuID0gY2FyZC5xdWVyeVNlbGVjdG9yKCIjc2MtY29weSIpOwogIGlmIChjb3B5QnRuKSBjb3B5QnRuLm9uY2xpY2sgPSAoKT0+IGNvcHlUb0NsaXBib2FyZChjbWQsIGNvcHlCdG4pOwoKICAvLyBSZWNoZWNrLUJ1dHRvbgogIGNvbnN0IHJlY2hlY2tCdG4gPSBjYXJkLnF1ZXJ5U2VsZWN0b3IoIiNzYy1yZWNoZWNrIik7CiAgaWYgKHJlY2hlY2tCdG4pIHJlY2hlY2tCdG4ub25jbGljayA9IHJlY2hlY2tPbGxhbWE7CgogIC8vIEVpbnN0ZWxsdW5nZW4tTGluawogIGNvbnN0IHNldEJ0biA9IGNhcmQucXVlcnlTZWxlY3RvcigiI3NjLXNldHRpbmdzIik7CiAgaWYgKHNldEJ0bikgc2V0QnRuLm9uY2xpY2sgPSAoKT0+IG9wZW5QYW5lbCgic2V0dGluZ3MiKTsKCiAgLy8gSW5zdGFsbGllcnRlIE1vZGVsbGUgYWxzIEJ1dHRvbnMgKG51ciBpbSBuby1tb2RlbC1GYWxsIHVuZCB3ZW5uIHZvcmhhbmRlbikKICBpZiAobW9kZSA9PT0gIm5vLW1vZGVsIil7CiAgICBjb25zdCB3cmFwID0gY2FyZC5xdWVyeVNlbGVjdG9yKCIjc2MtbW9kZWxzIik7CiAgICBjb25zdCBtb2RlbHMgPSAoaW5mbyAmJiBBcnJheS5pc0FycmF5KGluZm8ubW9kZWxzKSkgPyBpbmZvLm1vZGVscyA6IFtdOwogICAgaWYgKHdyYXAgJiYgbW9kZWxzLmxlbmd0aCl7CiAgICAgIGNvbnN0IGxibCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoInNwYW4iKTsKICAgICAgbGJsLnN0eWxlLmNzc1RleHQgPSAiZm9udC1zaXplOjEycHg7Y29sb3I6dmFyKC0tbXV0KTthbGlnbi1zZWxmOmNlbnRlcjttYXJnaW4tcmlnaHQ6MnB4IjsKICAgICAgbGJsLnRleHRDb250ZW50ID0gIlNjaG9uIGluc3RhbGxpZXJ0OiI7CiAgICAgIHdyYXAuYXBwZW5kQ2hpbGQobGJsKTsKICAgICAgbW9kZWxzLmZvckVhY2gobT0+ewogICAgICAgIGNvbnN0IGIgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJidXR0b24iKTsKICAgICAgICBiLmNsYXNzTmFtZSA9ICJzYy1tb2RlbCI7CiAgICAgICAgYi50ZXh0Q29udGVudCA9IG07ICAgICAgICAgICAgICAgICAvLyBkeW5hbWlzY2ggLT4gdGV4dENvbnRlbnQKICAgICAgICBiLm9uY2xpY2sgPSAoKT0+IHBpY2tPbGxhbWFNb2RlbChtLCBiKTsKICAgICAgICB3cmFwLmFwcGVuZENoaWxkKGIpOwogICAgICB9KTsKICAgIH0KICB9Cn0KCi8vIEluIFp3aXNjaGVuYWJsYWdlIGtvcGllcmVuIChtaXQgRmFsbGJhY2spCmZ1bmN0aW9uIGNvcHlUb0NsaXBib2FyZCh0ZXh0LCBidG4pewogIGNvbnN0IGRvbmUgPSAoKT0+ewogICAgaWYgKCFidG4pIHJldHVybjsKICAgIGNvbnN0IG9sZCA9IGJ0bi50ZXh0Q29udGVudDsKICAgIGJ0bi50ZXh0Q29udGVudCA9ICLinJMgS29waWVydCI7CiAgICBzZXRUaW1lb3V0KCgpPT57IGJ0bi50ZXh0Q29udGVudCA9IG9sZDsgfSwgMTUwMCk7CiAgfTsKICB0cnl7CiAgICBpZiAobmF2aWdhdG9yLmNsaXBib2FyZCAmJiBuYXZpZ2F0b3IuY2xpcGJvYXJkLndyaXRlVGV4dCl7CiAgICAgIG5hdmlnYXRvci5jbGlwYm9hcmQud3JpdGVUZXh0KHRleHQpLnRoZW4oZG9uZSwgKCk9PmZhbGxiYWNrQ29weSh0ZXh0LCBkb25lKSk7CiAgICB9IGVsc2UgewogICAgICBmYWxsYmFja0NvcHkodGV4dCwgZG9uZSk7CiAgICB9CiAgfWNhdGNoKGUpeyBmYWxsYmFja0NvcHkodGV4dCwgZG9uZSk7IH0KfQpmdW5jdGlvbiBmYWxsYmFja0NvcHkodGV4dCwgZG9uZSl7CiAgdHJ5ewogICAgY29uc3QgdGEgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJ0ZXh0YXJlYSIpOwogICAgdGEudmFsdWUgPSB0ZXh0OyB0YS5zdHlsZS5wb3NpdGlvbj0iZml4ZWQiOyB0YS5zdHlsZS5vcGFjaXR5PSIwIjsKICAgIGRvY3VtZW50LmJvZHkuYXBwZW5kQ2hpbGQodGEpOyB0YS5mb2N1cygpOyB0YS5zZWxlY3QoKTsKICAgIGRvY3VtZW50LmV4ZWNDb21tYW5kKCJjb3B5Iik7CiAgICBkb2N1bWVudC5ib2R5LnJlbW92ZUNoaWxkKHRhKTsKICAgIGRvbmUgJiYgZG9uZSgpOwogIH1jYXRjaChlKXsgLyogc3RpbGwgKi8gfQp9CgovLyBJbnN0YWxsaWVydGVzIE1vZGVsbCB3w6RobGVuIC0+IHNldHplbiwgU3RhdHVzIG5ldSBsYWRlbiwgS2FydGUgYXVzYmxlbmRlbgphc3luYyBmdW5jdGlvbiBwaWNrT2xsYW1hTW9kZWwobmFtZSwgYnRuKXsKICBjb25zdCBzdGF0ZUVsID0gc2V0dXBDYXJkRWwgPyBzZXR1cENhcmRFbC5xdWVyeVNlbGVjdG9yKCIjc2Mtc3RhdGUiKSA6IG51bGw7CiAgaWYgKGJ0bikgYnRuLmRpc2FibGVkID0gdHJ1ZTsKICBpZiAoc3RhdGVFbCkgc3RhdGVFbC50ZXh0Q29udGVudCA9ICJzZXR6ZSBNb2RlbGwg4oCmIjsKICB0cnl7CiAgICBjb25zdCByID0gYXdhaXQgYXBpKCIvYXBpL3NldHRpbmdzIiwgIlBPU1QiLCB7IG9sbGFtYV9tb2RlbDogbmFtZSB9KTsKICAgIGlmIChyICYmIHIuZXJyb3IpewogICAgICBpZiAoc3RhdGVFbCkgc3RhdGVFbC50ZXh0Q29udGVudCA9ICLimqAgIiArIHIuZXJyb3I7CiAgICAgIGlmIChidG4pIGJ0bi5kaXNhYmxlZCA9IGZhbHNlOwogICAgICByZXR1cm47CiAgICB9CiAgICByZW1vdmVTZXR1cENhcmQoKTsKICAgIGF3YWl0IGxvYWRTdGF0dXMoKTsgICAgICAgICAgLy8gbMOkZHQgU3RhdHVzICsgT2xsYW1hIG5ldSwgYmVncsO8w590IGJlaSBFcmZvbGcKICB9Y2F0Y2goZSl7CiAgICBpZiAoc3RhdGVFbCkgc3RhdGVFbC50ZXh0Q29udGVudCA9ICLimqAgIiArIGUubWVzc2FnZTsKICAgIGlmIChidG4pIGJ0bi5kaXNhYmxlZCA9IGZhbHNlOwogIH0KfQoKLy8gIk5vY2htYWwgcHLDvGZlbiIg4oCUIHJvYnVzdCwga2VpbiBEYXVlci1Qb2xsaW5nCmFzeW5jIGZ1bmN0aW9uIHJlY2hlY2tPbGxhbWEoKXsKICBpZiAoIXNldHVwQ2FyZEVsKSByZXR1cm47CiAgY29uc3QgcmVjaGVja0J0biA9IHNldHVwQ2FyZEVsLnF1ZXJ5U2VsZWN0b3IoIiNzYy1yZWNoZWNrIik7CiAgY29uc3Qgc3RhdGVFbCA9IHNldHVwQ2FyZEVsLnF1ZXJ5U2VsZWN0b3IoIiNzYy1zdGF0ZSIpOwogIGlmIChyZWNoZWNrQnRuKSByZWNoZWNrQnRuLmRpc2FibGVkID0gdHJ1ZTsKICBpZiAoc3RhdGVFbCkgc3RhdGVFbC50ZXh0Q29udGVudCA9ICJwcsO8ZmUg4oCmIjsKICBsZXQgbzsKICB0cnl7CiAgICBvID0gYXdhaXQgYXBpKCIvYXBpL29sbGFtYSIpOwogIH1jYXRjaChlKXsKICAgIGlmIChzdGF0ZUVsKSBzdGF0ZUVsLnRleHRDb250ZW50ID0gIk5vY2ggbmljaHQgZXJyZWljaGJhciDigJQgc3RhcnRlIE9sbGFtYSB1bmQgdmVyc3VjaCdzIGdsZWljaCBub2NobWFsLiI7CiAgICBpZiAocmVjaGVja0J0bikgcmVjaGVja0J0bi5kaXNhYmxlZCA9IGZhbHNlOwogICAgc2V0T2xsYW1hUGlsbCgiYmFkIiwgIlNldHVwIG7DtnRpZyIpOwogICAgcmV0dXJuOwogIH0KICBpZiAobyAmJiBvLmVycm9yKXsKICAgIGlmIChzdGF0ZUVsKSBzdGF0ZUVsLnRleHRDb250ZW50ID0gIuKaoCAiICsgby5lcnJvcjsKICAgIGlmIChyZWNoZWNrQnRuKSByZWNoZWNrQnRuLmRpc2FibGVkID0gZmFsc2U7CiAgICByZXR1cm47CiAgfQoKICBjb25zdCBydW5uaW5nID0gISEobyAmJiBvLnJ1bm5pbmcpOwogIGNvbnN0IG1vZGVscyA9IChvICYmIEFycmF5LmlzQXJyYXkoby5tb2RlbHMpKSA/IG8ubW9kZWxzIDogW107CiAgY29uc3QgY3VycmVudCA9IChvICYmIG8uY3VycmVudF9tb2RlbCkgfHwgT0xMQU1BX0RFRkFVTFRfTU9ERUw7CiAgY29uc3QgaGFzTW9kZWwgPSBtb2RlbEluc3RhbGxlZChtb2RlbHMsIGN1cnJlbnQpOwoKICBpZiAocnVubmluZyAmJiBoYXNNb2RlbCl7CiAgICBzZXRPbGxhbWFQaWxsKCJvayIsICJsb2thbCBha3RpdiIpOwogICAgcmVtb3ZlU2V0dXBDYXJkKCk7CiAgICBzdGF0ZS5yZWFkeSA9IHRydWU7CiAgICBhZGRCdWJibGUoImRpbm8iLCBgRGlubyBpc3Qgb25saW5lLCAke3N0YXRlLnVzZXJOYW1lfSEgV29yYXVmIGhhc3QgZHUgQm9jaz8g4pqhYCk7CiAgICByZXR1cm47CiAgfQoKICAvLyBOb2NoIG5pY2h0IGZlcnRpZyAtPiBLYXJ0ZSBwYXNzZW5kIGFrdHVhbGlzaWVyZW4KICBpZiAoIXJ1bm5pbmcpewogICAgc2V0T2xsYW1hUGlsbCgiYmFkIiwgIlNldHVwIG7DtnRpZyIpOwogICAgc2hvd1NldHVwQ2FyZCgibm90LXJ1bm5pbmciLCB7IG1vZGVscywgY3VycmVudCB9KTsKICB9IGVsc2UgewogICAgc2V0T2xsYW1hUGlsbCgid2FybiIsICJNb2RlbGwgZmVobHQiKTsKICAgIHNob3dTZXR1cENhcmQoIm5vLW1vZGVsIiwgeyBtb2RlbHMsIGN1cnJlbnQgfSk7CiAgfQogIGNvbnN0IG5zID0gc2V0dXBDYXJkRWwgPyBzZXR1cENhcmRFbC5xdWVyeVNlbGVjdG9yKCIjc2Mtc3RhdGUiKSA6IG51bGw7CiAgaWYgKG5zKSBucy50ZXh0Q29udGVudCA9IHJ1bm5pbmcgPyAiTMOkdWZ0IOKAlCBhYmVyIGVzIGZlaGx0IG5vY2ggZGFzIE1vZGVsbC4iIDogIk9sbGFtYSBsw6R1ZnQgbm9jaCBuaWNodC4iOwp9CgovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KLy8gIENoYXQgc2VuZGVuCi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQphc3luYyBmdW5jdGlvbiBzZW5kKCl7CiAgaWYgKHN0YXRlLmJ1c3kpIHJldHVybjsKICBjb25zdCB0ZXh0ID0gaW5wdXRFbC52YWx1ZS50cmltKCk7CiAgaWYgKCF0ZXh0KSByZXR1cm47CiAgaW5wdXRFbC52YWx1ZSA9ICIiOyBhdXRvR3JvdygpOwoKICBhZGRCdWJibGUoInVzZXIiLCB0ZXh0KTsKICBzdGF0ZS5tZXNzYWdlcy5wdXNoKHsgcm9sZToidXNlciIsIGNvbnRlbnQ6dGV4dCB9KTsKCiAgc2V0QnVzeSh0cnVlKTsKICB0cnl7CiAgICBjb25zdCBkYXRhID0gYXdhaXQgYXBpKCIvYXBpL2NoYXQiLCAiUE9TVCIsIHsgbWVzc2FnZXM6IHN0YXRlLm1lc3NhZ2VzIH0pOwogICAgaGlkZVR5cGluZygpOwogICAgaWYgKGRhdGEuZXJyb3IpewogICAgICBhZGRCdWJibGUoImVycm9yIiwgZGF0YS5lcnJvcik7CiAgICAgIC8vIGxldHp0ZSBOdXR6ZXItTmFjaHJpY2h0IG5pY2h0IGRhdWVyaGFmdCBiZWhhbHRlbgogICAgICBzdGF0ZS5tZXNzYWdlcy5wb3AoKTsKICAgIH0gZWxzZSB7CiAgICAgIGNvbnN0IHJlcGx5ID0gZGF0YS5yZXBseSB8fCAiIjsKICAgICAgYWRkQnViYmxlKCJkaW5vIiwgcmVwbHkpOwogICAgICBzdGF0ZS5tZXNzYWdlcy5wdXNoKHsgcm9sZToiYXNzaXN0YW50IiwgY29udGVudDpyZXBseSB9KTsKICAgICAgc3BlYWsocmVwbHkpOwogICAgfQogIH1jYXRjaChlKXsKICAgIGhpZGVUeXBpbmcoKTsKICAgIGFkZEJ1YmJsZSgiZXJyb3IiLCAiTmV0endlcmtmZWhsZXI6ICIrZS5tZXNzYWdlKTsKICAgIHN0YXRlLm1lc3NhZ2VzLnBvcCgpOwogIH1maW5hbGx5ewogICAgc2V0QnVzeShmYWxzZSk7CiAgICBpbnB1dEVsLmZvY3VzKCk7CiAgfQp9CgovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KLy8gIFF1aWNrLUFjdGlvbnMKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09Ci8vIEdlbmVyaXNjaGVyIEhlbGZlciBmw7xyIC9wbGFuIHVuZCAvdGFnIChCb2R5IHt9IC0+IHt0ZXh0fSkKYXN5bmMgZnVuY3Rpb24gc2ltcGxlQWN0aW9uKHBhdGgpewogIGlmIChzdGF0ZS5idXN5KSByZXR1cm47CiAgc2V0QnVzeSh0cnVlKTsKICB0cnl7CiAgICBjb25zdCBkYXRhID0gYXdhaXQgYXBpKHBhdGgsICJQT1NUIiwge30pOwogICAgaGlkZVR5cGluZygpOwogICAgaWYgKGRhdGEuZXJyb3IpIGFkZEJ1YmJsZSgiZXJyb3IiLCBkYXRhLmVycm9yKTsKICAgIGVsc2V7CiAgICAgIGNvbnN0IHR4dCA9IGRhdGEudGV4dCB8fCAiIjsKICAgICAgYWRkQnViYmxlKCJkaW5vIiwgdHh0KTsKICAgICAgc3RhdGUubWVzc2FnZXMucHVzaCh7IHJvbGU6ImFzc2lzdGFudCIsIGNvbnRlbnQ6dHh0IH0pOwogICAgICBzcGVhayh0eHQpOwogICAgfQogIH1jYXRjaChlKXsgaGlkZVR5cGluZygpOyBhZGRCdWJibGUoImVycm9yIiwiTmV0endlcmtmZWhsZXI6ICIrZS5tZXNzYWdlKTsgfQogIGZpbmFsbHl7IHNldEJ1c3koZmFsc2UpOyB9Cn0KZnVuY3Rpb24gcXVpY2tQbGFuKCl7IHNpbXBsZUFjdGlvbigiL2FwaS9wbGFuIik7IH0KZnVuY3Rpb24gcXVpY2tUb2RheSgpeyBzaW1wbGVBY3Rpb24oIi9hcGkvdGFnIik7IH0KCi8vIExlcm5lbiAtPiB2ZXJkaWNodGV0IEdlc3Byw6RjaCB6dSBGYWt0ZW4KYXN5bmMgZnVuY3Rpb24gcXVpY2tMZWFybigpewogIGlmIChzdGF0ZS5idXN5KSByZXR1cm47CiAgaWYgKCFzdGF0ZS5tZXNzYWdlcy5sZW5ndGgpeyBhZGRCdWJibGUoImluZm8iLCJXaXIgaGFiZW4gbm9jaCBuaWNodCBnZXJlZGV0IOKAlCBuaWNodHMgenUgbGVybmVuLiDwn5iJIik7IHJldHVybjsgfQogIHNldEJ1c3kodHJ1ZSk7CiAgdHJ5ewogICAgY29uc3QgZGF0YSA9IGF3YWl0IGFwaSgiL2FwaS9sZWFybiIsICJQT1NUIiwgeyBtZXNzYWdlczogc3RhdGUubWVzc2FnZXMgfSk7CiAgICBoaWRlVHlwaW5nKCk7CiAgICBpZiAoZGF0YS5lcnJvcikgYWRkQnViYmxlKCJlcnJvciIsIGRhdGEuZXJyb3IpOwogICAgZWxzZSBhZGRCdWJibGUoImluZm8iLCBgR2VtZXJrdCEgRGlubyBrZW5udCBqZXR6dCAke2RhdGEuY291bnQgPz8gMH0gRmFrdGVuLiDwn6egYCk7CiAgfWNhdGNoKGUpeyBoaWRlVHlwaW5nKCk7IGFkZEJ1YmJsZSgiZXJyb3IiLCJOZXR6d2Vya2ZlaGxlcjogIitlLm1lc3NhZ2UpOyB9CiAgZmluYWxseXsgc2V0QnVzeShmYWxzZSk7IH0KfQoKLy8gUmF0IGRlciBLSXMgLT4gbmltbXQgYWt0dWVsbGVuIEVpbmdhYmV0ZXh0IGFscyBGcmFnZQphc3luYyBmdW5jdGlvbiBxdWlja0NvdW5jaWwoKXsKICBpZiAoc3RhdGUuYnVzeSkgcmV0dXJuOwogIGNvbnN0IGZyYWdlID0gaW5wdXRFbC52YWx1ZS50cmltKCk7CiAgaWYgKCFmcmFnZSl7IGFkZEJ1YmJsZSgiaW5mbyIsIlNjaHJlaWIgenVlcnN0IGRlaW5lIEZyYWdlIGlucyBGZWxkLCBkYW5uIMK7UmF0IGRlciBLSXPCqy4g8J+noCIpOyByZXR1cm47IH0KICBpbnB1dEVsLnZhbHVlPSIiOyBhdXRvR3JvdygpOwogIGFkZEJ1YmJsZSgidXNlciIsIGZyYWdlKTsKCiAgc2V0QnVzeSh0cnVlKTsKICB0cnl7CiAgICBjb25zdCBkYXRhID0gYXdhaXQgYXBpKCIvYXBpL2NvdW5jaWwiLCAiUE9TVCIsIHsgbWVzc2FnZXM6IHN0YXRlLm1lc3NhZ2VzLCBmcmFnZSB9KTsKICAgIGhpZGVUeXBpbmcoKTsKICAgIGlmIChkYXRhLmVycm9yKXsgYWRkQnViYmxlKCJlcnJvciIsIGRhdGEuZXJyb3IpOyBzZXRCdXN5KGZhbHNlKTsgcmV0dXJuOyB9CiAgICBjb25zdCBhbnN3ZXJzID0gZGF0YS5hbnN3ZXJzIHx8IHt9OwogICAgLy8gUmVpaGVuZm9sZ2U6IENsYXVkZSwgQ2hhdEdQVCwgR2VtaW5pIChmYWxscyB2b3JoYW5kZW4pCiAgICBbIkNsYXVkZSIsIkNoYXRHUFQiLCJHZW1pbmkiXS5mb3JFYWNoKG5hbWU9PnsKICAgICAgaWYgKGFuc3dlcnNbbmFtZV0gIT0gbnVsbCkgYWRkQnViYmxlKCJjb3VuY2lsIiwgYW5zd2Vyc1tuYW1lXSwgIuKWuCAiK25hbWUpOwogICAgfSk7CiAgICAvLyBldnRsLiB3ZWl0ZXJlIHVuYmVrYW5udGUgU2NobMO8c3NlbAogICAgT2JqZWN0LmtleXMoYW5zd2VycykuZm9yRWFjaChuYW1lPT57CiAgICAgIGlmICghWyJDbGF1ZGUiLCJDaGF0R1BUIiwiR2VtaW5pIl0uaW5jbHVkZXMobmFtZSkpIGFkZEJ1YmJsZSgiY291bmNpbCIsIGFuc3dlcnNbbmFtZV0sICLilrggIituYW1lKTsKICAgIH0pOwogICAgaWYgKGRhdGEuc3ludGhlc2UpewogICAgICBhZGRCdWJibGUoInN5bnRoIiwgZGF0YS5zeW50aGVzZSwgIuKcpiBEaW5vcyBGYXppdCIpOwogICAgICBzdGF0ZS5tZXNzYWdlcy5wdXNoKHsgcm9sZToiYXNzaXN0YW50IiwgY29udGVudDpkYXRhLnN5bnRoZXNlIH0pOwogICAgICBzcGVhayhkYXRhLnN5bnRoZXNlKTsKICAgIH0KICB9Y2F0Y2goZSl7IGhpZGVUeXBpbmcoKTsgYWRkQnViYmxlKCJlcnJvciIsIk5ldHp3ZXJrZmVobGVyOiAiK2UubWVzc2FnZSk7IH0KICBmaW5hbGx5eyBzZXRCdXN5KGZhbHNlKTsgfQp9CgovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KLy8gIEVpbmdhYmVmZWxkOiBBdXRvLUdyb3cgKyBUYXN0YXR1cgovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KZnVuY3Rpb24gYXV0b0dyb3coKXsKICBpbnB1dEVsLnN0eWxlLmhlaWdodCA9ICJhdXRvIjsKICBpbnB1dEVsLnN0eWxlLmhlaWdodCA9IE1hdGgubWluKGlucHV0RWwuc2Nyb2xsSGVpZ2h0LCAxNDApICsgInB4IjsKfQppbnB1dEVsLmFkZEV2ZW50TGlzdGVuZXIoImlucHV0IiwgYXV0b0dyb3cpOwppbnB1dEVsLmFkZEV2ZW50TGlzdGVuZXIoImtleWRvd24iLCAoZSk9PnsKICBpZiAoZS5rZXkgPT09ICJFbnRlciIgJiYgIWUuc2hpZnRLZXkpeyBlLnByZXZlbnREZWZhdWx0KCk7IHNlbmQoKTsgfQp9KTsKCi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQovLyAgU3ByYWNoYXVzZ2FiZSAoc3BlZWNoU3ludGhlc2lzKQovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KbGV0IGRlVm9pY2UgPSBudWxsOwpmdW5jdGlvbiBwaWNrVm9pY2UoKXsKICBpZiAoISgic3BlZWNoU3ludGhlc2lzIiBpbiB3aW5kb3cpKSByZXR1cm47CiAgY29uc3QgdnMgPSBzcGVlY2hTeW50aGVzaXMuZ2V0Vm9pY2VzKCk7CiAgZGVWb2ljZSA9IHZzLmZpbmQodiA9PiB2LmxhbmcgPT09ICJkZS1ERSIpIHx8IHZzLmZpbmQodiA9PiAvXmRlL2kudGVzdCh2LmxhbmcpKSB8fCBudWxsOwp9CmlmICgic3BlZWNoU3ludGhlc2lzIiBpbiB3aW5kb3cpewogIHBpY2tWb2ljZSgpOwogIHNwZWVjaFN5bnRoZXNpcy5vbnZvaWNlc2NoYW5nZWQgPSBwaWNrVm9pY2U7Cn0gZWxzZSB7CiAgJCgidm9pY2VCdG4iKS5zdHlsZS5kaXNwbGF5ID0gIm5vbmUiOyAvLyBrZWluIFRUUyAtPiBCdXR0b24gYXVzYmxlbmRlbgp9CmZ1bmN0aW9uIHRvZ2dsZVZvaWNlKCl7CiAgc3RhdGUudm9pY2VPbiA9ICFzdGF0ZS52b2ljZU9uOwogICQoInZvaWNlQnRuIikuY2xhc3NMaXN0LnRvZ2dsZSgiYWN0aXZlIiwgc3RhdGUudm9pY2VPbik7CiAgaWYgKCFzdGF0ZS52b2ljZU9uICYmICJzcGVlY2hTeW50aGVzaXMiIGluIHdpbmRvdykgc3BlZWNoU3ludGhlc2lzLmNhbmNlbCgpOwp9CmZ1bmN0aW9uIHNwZWFrKHRleHQpewogIGlmICghc3RhdGUudm9pY2VPbiB8fCAhdGV4dCB8fCAhKCJzcGVlY2hTeW50aGVzaXMiIGluIHdpbmRvdykpIHJldHVybjsKICB0cnl7CiAgICBzcGVlY2hTeW50aGVzaXMuY2FuY2VsKCk7CiAgICBjb25zdCB1ID0gbmV3IFNwZWVjaFN5bnRoZXNpc1V0dGVyYW5jZSh0ZXh0KTsKICAgIHUubGFuZyA9ICJkZS1ERSI7CiAgICBpZiAoZGVWb2ljZSkgdS52b2ljZSA9IGRlVm9pY2U7CiAgICB1Lm9uc3RhcnQgPSAoKT0+IHNldFNwZWFraW5nKHRydWUpOwogICAgdS5vbmVuZCAgID0gKCk9PiBzZXRTcGVha2luZyhmYWxzZSk7CiAgICB1Lm9uZXJyb3IgPSAoKT0+IHNldFNwZWFraW5nKGZhbHNlKTsKICAgIHNwZWVjaFN5bnRoZXNpcy5zcGVhayh1KTsKICB9Y2F0Y2goZSl7IC8qIHN0aWxsICovIH0KfQoKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09Ci8vICBTcHJhY2hlcmtlbm51bmcgKFNwZWVjaFJlY29nbml0aW9uKQovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KbGV0IHJlY29nID0gbnVsbCwgbGlzdGVuaW5nID0gZmFsc2U7CihmdW5jdGlvbiBpbml0TWljKCl7CiAgY29uc3QgU1IgPSB3aW5kb3cuU3BlZWNoUmVjb2duaXRpb24gfHwgd2luZG93LndlYmtpdFNwZWVjaFJlY29nbml0aW9uOwogIGlmICghU1IpeyAkKCJtaWNCdG4iKS5zdHlsZS5kaXNwbGF5ID0gIm5vbmUiOyByZXR1cm47IH0gLy8gbmljaHQgdW50ZXJzdMO8dHp0IC0+IGVsZWdhbnQgYXVzYmxlbmRlbgogIHJlY29nID0gbmV3IFNSKCk7CiAgcmVjb2cubGFuZyA9ICJkZS1ERSI7CiAgcmVjb2cuaW50ZXJpbVJlc3VsdHMgPSBmYWxzZTsKICByZWNvZy5tYXhBbHRlcm5hdGl2ZXMgPSAxOwogIHJlY29nLm9ucmVzdWx0ID0gKGUpPT57CiAgICBjb25zdCB0ID0gZS5yZXN1bHRzWzBdWzBdLnRyYW5zY3JpcHQ7CiAgICBpbnB1dEVsLnZhbHVlID0gKGlucHV0RWwudmFsdWUgPyBpbnB1dEVsLnZhbHVlKyIgIiA6ICIiKSArIHQ7CiAgICBhdXRvR3JvdygpOyBpbnB1dEVsLmZvY3VzKCk7CiAgfTsKICByZWNvZy5vbmVycm9yID0gKCk9PiBzdG9wTWljKCk7CiAgcmVjb2cub25lbmQgPSAoKT0+IHN0b3BNaWMoKTsKfSkoKTsKZnVuY3Rpb24gdG9nZ2xlTWljKCl7CiAgaWYgKCFyZWNvZykgcmV0dXJuOwogIGlmIChsaXN0ZW5pbmcpeyByZWNvZy5zdG9wKCk7IHN0b3BNaWMoKTsgfQogIGVsc2UgeyB0cnl7IHJlY29nLnN0YXJ0KCk7IGxpc3RlbmluZyA9IHRydWU7ICQoIm1pY0J0biIpLmNsYXNzTGlzdC5hZGQoImxpc3RlbmluZyIpOyB9Y2F0Y2goZSl7IHN0b3BNaWMoKTsgfSB9Cn0KZnVuY3Rpb24gc3RvcE1pYygpeyBsaXN0ZW5pbmcgPSBmYWxzZTsgJCgibWljQnRuIikuY2xhc3NMaXN0LnJlbW92ZSgibGlzdGVuaW5nIik7IH0KCi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQovLyAgUGFuZWxzIChTbGlkZS1PdmVyKQovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KZnVuY3Rpb24gb3BlblBhbmVsKG5hbWUpewogIGNsb3NlUGFuZWxzKCk7CiAgJCgib3ZlcmxheSIpLmNsYXNzTGlzdC5hZGQoIm9wZW4iKTsKICBjb25zdCBwID0gJCgicGFuZWwtIituYW1lKTsKICBpZiAocCkgcC5jbGFzc0xpc3QuYWRkKCJvcGVuIik7CiAgaWYgKG5hbWUgPT09ICJzZXR0aW5ncyIpIGxvYWRTZXR0aW5ncygpOwogIGlmIChuYW1lID09PSAiY3VzdG9tZXJzIikgbG9hZEN1c3RvbWVycygpOwogIGlmIChuYW1lID09PSAibWVtb3J5IikgbG9hZE1lbW9yeSgpOwp9CmZ1bmN0aW9uIGNsb3NlUGFuZWxzKCl7CiAgJCgib3ZlcmxheSIpLmNsYXNzTGlzdC5yZW1vdmUoIm9wZW4iKTsKICBkb2N1bWVudC5xdWVyeVNlbGVjdG9yQWxsKCIucGFuZWwiKS5mb3JFYWNoKHAgPT4gcC5jbGFzc0xpc3QucmVtb3ZlKCJvcGVuIikpOwp9CmRvY3VtZW50LmFkZEV2ZW50TGlzdGVuZXIoImtleWRvd24iLCBlID0+IHsgaWYgKGUua2V5ID09PSAiRXNjYXBlIikgY2xvc2VQYW5lbHMoKTsgfSk7CgovLyAtLS0tLS0tLS0tIEVpbnN0ZWxsdW5nZW4gLS0tLS0tLS0tLQphc3luYyBmdW5jdGlvbiBsb2FkU2V0dGluZ3MoKXsKICBjb25zdCBib2R5ID0gJCgic2V0dGluZ3NCb2R5Iik7CiAgYm9keS5pbm5lckhUTUwgPSAnPGRpdiBjbGFzcz0iZW1wdHkiPmzDpGR04oCmPC9kaXY+JzsKICBsZXQgczsKICB0cnkgeyBzID0gYXdhaXQgYXBpKCIvYXBpL3NldHRpbmdzIik7IH0KICBjYXRjaChlKXsgYm9keS5pbm5lckhUTUwgPSAiIjsgYm9keS5hcHBlbmRDaGlsZChlcnJCb3goIktvbm50ZSBFaW5zdGVsbHVuZ2VuIG5pY2h0IGxhZGVuOiAiK2UubWVzc2FnZSkpOyByZXR1cm47IH0KICBpZiAocy5lcnJvcil7IGJvZHkuaW5uZXJIVE1MPSIiOyBib2R5LmFwcGVuZENoaWxkKGVyckJveChzLmVycm9yKSk7IHJldHVybjsgfQoKICBjb25zdCBrZXlzID0gcy5rZXlzIHx8IHt9OwogIGNvbnN0IHBlcnNvbmEgPSBzLnBlcnNvbmEgfHwge307CiAgY29uc3QgY2xhdWRlTW9kZWxzID0gcy5jbGF1ZGVfbW9kZWxzIHx8IFtdOwoKICAvLyBDbGF1ZGUtTW9kZWxsLU9wdGlvbmVuCiAgY29uc3QgY21PcHRzID0gY2xhdWRlTW9kZWxzLm1hcChtID0+CiAgICBgPG9wdGlvbiB2YWx1ZT0iJHtlc2MobVswXSl9IiAke21bMF09PT1zLmNsYXVkZV9tb2RlbD8ic2VsZWN0ZWQiOiIifT4ke2VzYyhtWzFdKX08L29wdGlvbj5gKS5qb2luKCIiKTsKCiAgY29uc3QgcHJvdlNlbCA9IChwKT0+IGA8b3B0aW9uIHZhbHVlPSIke3B9IiAke3MucHJvdmlkZXI9PT1wPyJzZWxlY3RlZCI6IiJ9PmA7CgogIGJvZHkuaW5uZXJIVE1MID0gYAogICAgPGRpdiBjbGFzcz0ic2VjdCI+8J+UkSBBUEktU2NobMO8c3NlbDwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5DbGF1ZGUgKGVtcGZvaGxlbik8L2xhYmVsPjxpbnB1dCBpZD0ic3Qta2V5LWNsYXVkZSIgdHlwZT0icGFzc3dvcmQiIHBsYWNlaG9sZGVyPSJzay1hbnQt4oCmIj48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+Q2hhdEdQVCAvIE9wZW5BSTwvbGFiZWw+PGlucHV0IGlkPSJzdC1rZXktb3BlbmFpIiB0eXBlPSJwYXNzd29yZCIgcGxhY2Vob2xkZXI9InNrLeKApiI+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPkdvb2dsZSBHZW1pbmk8L2xhYmVsPjxpbnB1dCBpZD0ic3Qta2V5LWdlbWluaSIgdHlwZT0icGFzc3dvcmQiIHBsYWNlaG9sZGVyPSJBSXph4oCmIj48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImhpbnQiPlNjaGzDvHNzZWwgaG9sZW46IDxjb2RlPmNvbnNvbGUuYW50aHJvcGljLmNvbTwvY29kZT4gwrcgPGNvZGU+cGxhdGZvcm0ub3BlbmFpLmNvbS9hcGkta2V5czwvY29kZT4gwrcgPGNvZGU+YWlzdHVkaW8uZ29vZ2xlLmNvbS9hcGlrZXk8L2NvZGU+PGJyPlNpZSBibGVpYmVuIGxva2FsIGF1ZiBkZWluZW0gUEMuPC9kaXY+CgogICAgPGRpdiBjbGFzcz0ic2VjdCI+8J+noCBXZWxjaGVzIEdlaGlybj88L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+QW5iaWV0ZXI8L2xhYmVsPjxzZWxlY3QgaWQ9InN0LXByb3ZpZGVyIj4KICAgICAgJHtwcm92U2VsKCJjbGF1ZGUiKX1DbGF1ZGU8L29wdGlvbj4ke3Byb3ZTZWwoIm9sbGFtYSIpffCfhpMgR3JhdGlzIGxva2FsIChPbGxhbWEpPC9vcHRpb24+JHtwcm92U2VsKCJvcGVuYWkiKX1DaGF0R1BUIC8gT3BlbkFJPC9vcHRpb24+JHtwcm92U2VsKCJnZW1pbmkiKX1HZW1pbmk8L29wdGlvbj4KICAgIDwvc2VsZWN0PjwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5DbGF1ZGUtTW9kZWxsPC9sYWJlbD48c2VsZWN0IGlkPSJzdC1jbGF1ZGUtbW9kZWwiPiR7Y21PcHRzfTwvc2VsZWN0PjwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5PcGVuQUktTW9kZWxsPC9sYWJlbD48aW5wdXQgaWQ9InN0LW9wZW5haS1tb2RlbCIgcGxhY2Vob2xkZXI9InouQi4gZ3B0LTUuMSI+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPkdlbWluaS1Nb2RlbGw8L2xhYmVsPjxpbnB1dCBpZD0ic3QtZ2VtaW5pLW1vZGVsIiBwbGFjZWhvbGRlcj0iei5CLiBnZW1pbmktMi41LXBybyI+PC9kaXY+CgogICAgPGRpdiBjbGFzcz0ic2VjdCI+8J+GkyBHcmF0aXMgbG9rYWwgKE9sbGFtYSkg4oCUIG9obmUgU2NobMO8c3NlbDwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5HcmF0aXMtTW9kZWxsPC9sYWJlbD48aW5wdXQgaWQ9InN0LW9sbGFtYS1tb2RlbCIgcGxhY2Vob2xkZXI9InouQi4gbGxhbWEzLjIiPjwvZGl2PgogICAgPGRpdiBjbGFzcz0iaGludCI+S29tcGxldHQgZ3JhdGlzLCBvaG5lIFNjaGzDvHNzZWw6IGluc3RhbGxpZXJlIDxjb2RlPk9sbGFtYTwvY29kZT4gdm9uIDxjb2RlPm9sbGFtYS5jb208L2NvZGU+LCBkYW5uIGltIFRlcm1pbmFsIDxjb2RlPm9sbGFtYSBydW4gbGxhbWEzLjI8L2NvZGU+IGF1c2bDvGhyZW4gdW5kIG9iZW4gQW5iaWV0ZXIgPGI+8J+GkyBHcmF0aXMgbG9rYWw8L2I+IHfDpGhsZW4uIChTY2h3w6RjaGVyIGFscyBDbGF1ZGUsIGzDpHVmdCBkYWbDvHIgb2ZmbGluZSBhdWYgZGVpbmVtIFBDLik8L2Rpdj4KCiAgICA8ZGl2IGNsYXNzPSJzZWN0Ij7wn46tIFBlcnNvbmE8L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+TmFtZSBkZXIgS0k8L2xhYmVsPjxpbnB1dCBpZD0ic3QtYXNzaXN0YW50Ij48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+V2llIERpbm8gZGljaCBuZW5udDwvbGFiZWw+PGlucHV0IGlkPSJzdC11c2VyIj48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+RGVpbiBCdXNpbmVzczwvbGFiZWw+PHRleHRhcmVhIGlkPSJzdC1idXNpbmVzcyI+PC90ZXh0YXJlYT48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+U3RpbCAvIEh1bW9yPC9sYWJlbD48dGV4dGFyZWEgaWQ9InN0LWh1bW9yIj48L3RleHRhcmVhPjwvZGl2PgoKICAgIDxkaXYgY2xhc3M9InNlY3QiPvCfjq8gWmllbDwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjx0ZXh0YXJlYSBpZD0ic3QtZ29hbCI+PC90ZXh0YXJlYT48L2Rpdj4KCiAgICA8ZGl2IGNsYXNzPSJidG5yb3ciPgogICAgICA8YnV0dG9uIGNsYXNzPSJidG4gcHJpbWFyeSIgaWQ9InN0LXNhdmUiPvCfkr4gU3BlaWNoZXJuPC9idXR0b24+CiAgICAgIDxzcGFuIGlkPSJzdC1tc2ciIGNsYXNzPSJoaW50IiBzdHlsZT0iYWxpZ24tc2VsZjpjZW50ZXIiPjwvc3Bhbj4KICAgIDwvZGl2PgogIGA7CiAgLy8gV2VydGUgZWluc2V0emVuIChwZXIgLnZhbHVlLCBuaWNodCBpbiBpbm5lckhUTUwgLT4gc2ljaGVyKQogICQoInN0LWtleS1jbGF1ZGUiKS52YWx1ZSA9IGtleXMuY2xhdWRlIHx8ICIiOwogICQoInN0LWtleS1vcGVuYWkiKS52YWx1ZSA9IGtleXMub3BlbmFpIHx8ICIiOwogICQoInN0LWtleS1nZW1pbmkiKS52YWx1ZSA9IGtleXMuZ2VtaW5pIHx8ICIiOwogICQoInN0LW9wZW5haS1tb2RlbCIpLnZhbHVlID0gcy5vcGVuYWlfbW9kZWwgfHwgIiI7CiAgJCgic3QtZ2VtaW5pLW1vZGVsIikudmFsdWUgPSBzLmdlbWluaV9tb2RlbCB8fCAiIjsKICAkKCJzdC1vbGxhbWEtbW9kZWwiKS52YWx1ZSA9IHMub2xsYW1hX21vZGVsIHx8ICIiOwogICQoInN0LWFzc2lzdGFudCIpLnZhbHVlID0gcGVyc29uYS5hc3Npc3RhbnRfbmFtZSB8fCAiIjsKICAkKCJzdC11c2VyIikudmFsdWUgPSBwZXJzb25hLnVzZXJfbmFtZSB8fCAiIjsKICAkKCJzdC1idXNpbmVzcyIpLnZhbHVlID0gcGVyc29uYS5idXNpbmVzcyB8fCAiIjsKICAkKCJzdC1odW1vciIpLnZhbHVlID0gcGVyc29uYS5odW1vciB8fCAiIjsKICAkKCJzdC1nb2FsIikudmFsdWUgPSBzLmdvYWwgfHwgIiI7CgogICQoInN0LXNhdmUiKS5vbmNsaWNrID0gc2F2ZVNldHRpbmdzOwp9Cgphc3luYyBmdW5jdGlvbiBzYXZlU2V0dGluZ3MoKXsKICBjb25zdCBidG4gPSAkKCJzdC1zYXZlIik7IGJ0bi5kaXNhYmxlZCA9IHRydWU7CiAgY29uc3QgcGF5bG9hZCA9IHsKICAgIHByb3ZpZGVyOiAkKCJzdC1wcm92aWRlciIpLnZhbHVlLAogICAgY2xhdWRlX21vZGVsOiAkKCJzdC1jbGF1ZGUtbW9kZWwiKS52YWx1ZSwKICAgIG9wZW5haV9tb2RlbDogJCgic3Qtb3BlbmFpLW1vZGVsIikudmFsdWUudHJpbSgpLAogICAgZ2VtaW5pX21vZGVsOiAkKCJzdC1nZW1pbmktbW9kZWwiKS52YWx1ZS50cmltKCksCiAgICBvbGxhbWFfbW9kZWw6ICQoInN0LW9sbGFtYS1tb2RlbCIpLnZhbHVlLnRyaW0oKSwKICAgIGtleXM6IHsKICAgICAgY2xhdWRlOiAkKCJzdC1rZXktY2xhdWRlIikudmFsdWUudHJpbSgpLAogICAgICBvcGVuYWk6ICQoInN0LWtleS1vcGVuYWkiKS52YWx1ZS50cmltKCksCiAgICAgIGdlbWluaTogJCgic3Qta2V5LWdlbWluaSIpLnZhbHVlLnRyaW0oKSwKICAgIH0sCiAgICBwZXJzb25hOiB7CiAgICAgIGFzc2lzdGFudF9uYW1lOiAkKCJzdC1hc3Npc3RhbnQiKS52YWx1ZS50cmltKCksCiAgICAgIHVzZXJfbmFtZTogJCgic3QtdXNlciIpLnZhbHVlLnRyaW0oKSwKICAgICAgYnVzaW5lc3M6ICQoInN0LWJ1c2luZXNzIikudmFsdWUudHJpbSgpLAogICAgICBodW1vcjogJCgic3QtaHVtb3IiKS52YWx1ZS50cmltKCksCiAgICB9LAogICAgZ29hbDogJCgic3QtZ29hbCIpLnZhbHVlLnRyaW0oKSwKICB9OwogIGNvbnN0IG1zZyA9ICQoInN0LW1zZyIpOwogIHRyeXsKICAgIGNvbnN0IHIgPSBhd2FpdCBhcGkoIi9hcGkvc2V0dGluZ3MiLCAiUE9TVCIsIHBheWxvYWQpOwogICAgaWYgKHIuZXJyb3IpeyBtc2cudGV4dENvbnRlbnQgPSAi4pqgICIrci5lcnJvcjsgbXNnLnN0eWxlLmNvbG9yPSJ2YXIoLS1yb3NlKSI7IH0KICAgIGVsc2V7CiAgICAgIG1zZy50ZXh0Q29udGVudCA9ICJHZXNwZWljaGVydCDinJMiOyBtc2cuc3R5bGUuY29sb3I9InZhcigtLWdyZWVuKSI7CiAgICAgIGF3YWl0IGxvYWRTdGF0dXMoKTsgICAgICAgICAgICAvLyBTdGF0dXMgb2JlbiBuZXUgbGFkZW4gKGvDvG1tZXJ0IHNpY2ggdW0gQmVncsO8w591bmcvU2V0dXAtS2FydGUpCiAgICB9CiAgfWNhdGNoKGUpeyBtc2cudGV4dENvbnRlbnQgPSAi4pqgICIrZS5tZXNzYWdlOyBtc2cuc3R5bGUuY29sb3I9InZhcigtLXJvc2UpIjsgfQogIGZpbmFsbHl7IGJ0bi5kaXNhYmxlZCA9IGZhbHNlOyB9Cn0KCi8vIC0tLS0tLS0tLS0gS3VuZGVuIC0tLS0tLS0tLS0KYXN5bmMgZnVuY3Rpb24gbG9hZEN1c3RvbWVycygpewogIGNvbnN0IGJvZHkgPSAkKCJjdXN0b21lcnNCb2R5Iik7CiAgYm9keS5pbm5lckhUTUwgPSAnPGRpdiBjbGFzcz0iZW1wdHkiPmzDpGR04oCmPC9kaXY+JzsKICBsZXQgZDsKICB0cnkgeyBkID0gYXdhaXQgYXBpKCIvYXBpL2N1c3RvbWVycyIpOyB9CiAgY2F0Y2goZSl7IGJvZHkuaW5uZXJIVE1MPSIiOyBib2R5LmFwcGVuZENoaWxkKGVyckJveCgiS29ubnRlIEt1bmRlbiBuaWNodCBsYWRlbjogIitlLm1lc3NhZ2UpKTsgcmV0dXJuOyB9CiAgaWYgKGQuZXJyb3IpeyBib2R5LmlubmVySFRNTD0iIjsgYm9keS5hcHBlbmRDaGlsZChlcnJCb3goZC5lcnJvcikpOyByZXR1cm47IH0KICByZW5kZXJDdXN0b21lcnMoZCk7Cn0KCmZ1bmN0aW9uIHJlbmRlckN1c3RvbWVycyhkKXsKICBjb25zdCBib2R5ID0gJCgiY3VzdG9tZXJzQm9keSIpOwogIGJvZHkuaW5uZXJIVE1MID0gIiI7CiAgY29uc3QgciA9IGQucmV2ZW51ZSB8fCB7fTsKICBjb25zdCBjdXN0cyA9IGQuY3VzdG9tZXJzIHx8IFtdOwoKICAvLyBVbXNhdHotQmFubmVyCiAgY29uc3QgcmV2ID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7CiAgcmV2LmNsYXNzTmFtZSA9ICJyZXZlbnVlIjsKICByZXYuaW5uZXJIVE1MID0KICAgIGA8ZGl2IGNsYXNzPSJiaWciPiR7ZXVybyhyLm1vbnRobHkpfTwvZGl2PmArCiAgICBgPGRpdiBjbGFzcz0ic3ViIj5Nb25hdHN1bXNhdHogwrcgfiR7ZXVybyhyLndlZWtseSl9L1dvY2hlIMK3ICR7ci5hY3RpdmV8fDB9IGFrdGl2IMK3ICR7ci5sZWFkc3x8MH0gTGVhZHMgwrcgJHtyLnRvdGFsfHwwfSBnZXNhbXQ8L2Rpdj5gOwogIGJvZHkuYXBwZW5kQ2hpbGQocmV2KTsKCiAgLy8gIk5ldWVyIEt1bmRlIgogIGNvbnN0IG5ld0J0biA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImJ1dHRvbiIpOwogIG5ld0J0bi5jbGFzc05hbWUgPSAiYnRuIHByaW1hcnkiOyBuZXdCdG4uc3R5bGUubWFyZ2luQm90dG9tPSIxNHB4IjsgbmV3QnRuLnRleHRDb250ZW50ID0gIuKelSBOZXVlciBLdW5kZSI7CiAgbmV3QnRuLm9uY2xpY2sgPSAoKT0+IHNob3dDdXN0b21lckZvcm0obnVsbCk7CiAgYm9keS5hcHBlbmRDaGlsZChuZXdCdG4pOwoKICBpZiAoIWN1c3RzLmxlbmd0aCl7CiAgICBjb25zdCBlID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IGUuY2xhc3NOYW1lPSJlbXB0eSI7IGUudGV4dENvbnRlbnQ9Ik5vY2gga2VpbmUgS3VuZGVuLiBMZWcgZWluZW4gYW4uIPCfkaUiOwogICAgYm9keS5hcHBlbmRDaGlsZChlKTsKICAgIHJldHVybjsKICB9CiAgY3VzdHMuZm9yRWFjaChjID0+IGJvZHkuYXBwZW5kQ2hpbGQoY3VzdENhcmQoYykpKTsKfQoKZnVuY3Rpb24gY3VzdENhcmQoYyl7CiAgY29uc3QgY2FyZCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBjYXJkLmNsYXNzTmFtZSA9ICJjdXN0IjsKICBjb25zdCB0b3AgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgdG9wLmNsYXNzTmFtZT0idG9wIjsKICBjb25zdCBubSA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoInNwYW4iKTsgbm0uY2xhc3NOYW1lPSJuYW1lIjsgbm0udGV4dENvbnRlbnQgPSBjLm5hbWUgfHwgIuKAlCI7CiAgY29uc3QgYmQgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJzcGFuIik7IGJkLmNsYXNzTmFtZT0iYmFkZ2UiOyBiZC50ZXh0Q29udGVudCA9IGMuc3RhdHVzIHx8ICLigJQiOwogIHRvcC5hcHBlbmRDaGlsZChubSk7IHRvcC5hcHBlbmRDaGlsZChiZCk7IGNhcmQuYXBwZW5kQ2hpbGQodG9wKTsKCiAgY29uc3QgbWV0YSA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBtZXRhLmNsYXNzTmFtZT0ibWV0YSI7CiAgY29uc3QgcGFydHMgPSBbXTsKICBpZiAoYy5icmFuY2hlKSBwYXJ0cy5wdXNoKGMuYnJhbmNoZSk7CiAgaWYgKGMucGFrZXQpIHBhcnRzLnB1c2goYy5wYWtldCk7CiAgbWV0YS50ZXh0Q29udGVudCA9IHBhcnRzLmpvaW4oIiDCtyAiKTsKICBpZiAoYy5wcmVpcyl7CiAgICBjb25zdCBwID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgic3BhbiIpOyBwLmNsYXNzTmFtZT0icHJpY2UiOyBwLnRleHRDb250ZW50ID0gKHBhcnRzLmxlbmd0aD8iIMK3ICI6IiIpICsgZXVybyhjLnByZWlzKSsiL01vbmF0IjsKICAgIG1ldGEuYXBwZW5kQ2hpbGQocCk7CiAgfQogIGNhcmQuYXBwZW5kQ2hpbGQobWV0YSk7CgogIGlmIChjLm5hZWNoc3Rlcl9zY2hyaXR0KXsKICAgIGNvbnN0IG5zID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IG5zLmNsYXNzTmFtZT0ibWV0YSI7IG5zLnRleHRDb250ZW50ID0gIuKGkiAiICsgYy5uYWVjaHN0ZXJfc2Nocml0dDsKICAgIGNhcmQuYXBwZW5kQ2hpbGQobnMpOwogIH0KICBpZiAoYy5rb250YWt0KXsKICAgIGNvbnN0IGsgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgay5jbGFzc05hbWU9Im1ldGEiOyBrLnRleHRDb250ZW50ID0gIuKciSAiICsgYy5rb250YWt0OwogICAgY2FyZC5hcHBlbmRDaGlsZChrKTsKICB9CgogIGNvbnN0IGFjdCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBhY3QuY2xhc3NOYW1lPSJhY3Rpb25zIjsKICBjb25zdCBlZGl0ID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiYnV0dG9uIik7IGVkaXQuY2xhc3NOYW1lPSJidG4gc20iOyBlZGl0LnRleHRDb250ZW50PSLinI/vuI8gQmVhcmJlaXRlbiI7CiAgZWRpdC5vbmNsaWNrID0gKCk9PiBzaG93Q3VzdG9tZXJGb3JtKGMpOwogIGNvbnN0IGRlbCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImJ1dHRvbiIpOyBkZWwuY2xhc3NOYW1lPSJidG4gc20gZGFuZ2VyIjsgZGVsLnRleHRDb250ZW50PSLwn5eRIEzDtnNjaGVuIjsKICBkZWwub25jbGljayA9ICgpPT4gZGVsZXRlQ3VzdG9tZXIoYyk7CiAgYWN0LmFwcGVuZENoaWxkKGVkaXQpOyBhY3QuYXBwZW5kQ2hpbGQoZGVsKTsKICBjYXJkLmFwcGVuZENoaWxkKGFjdCk7CiAgcmV0dXJuIGNhcmQ7Cn0KCi8vIElubGluZS1Gb3JtdWxhciAobmV1L2JlYXJiZWl0ZW4pIGFscyBLYXJ0ZQpmdW5jdGlvbiBzaG93Q3VzdG9tZXJGb3JtKGMpewogIGNvbnN0IGlzRWRpdCA9ICEhYzsKICBjID0gYyB8fCB7fTsKICBjb25zdCBib2R5ID0gJCgiY3VzdG9tZXJzQm9keSIpOwogIGNvbnN0IGZvcm0gPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgZm9ybS5jbGFzc05hbWU9ImN1c3QiOwogIGNvbnN0IHN0YXR1c09wdHMgPSBzdGF0ZS5zdGF0dXNWYWx1ZXMubWFwKHMgPT4KICAgIGA8b3B0aW9uIHZhbHVlPSIke3N9IiAkeyAoYy5zdGF0dXN8fCJMZWFkIik9PT1zID8gInNlbGVjdGVkIjoiIiB9PiR7c308L29wdGlvbj5gKS5qb2luKCIiKTsKICBmb3JtLmlubmVySFRNTCA9IGAKICAgIDxkaXYgY2xhc3M9InNlY3QiIHN0eWxlPSJtYXJnaW4tdG9wOjAiPiR7aXNFZGl0ID8gIuKcj++4jyBLdW5kZSBiZWFyYmVpdGVuIiA6ICLinpUgTmV1ZXIgS3VuZGUifTwvZGl2PgogICAgPGRpdiBjbGFzcz0iZmllbGQiPjxsYWJlbD5OYW1lICo8L2xhYmVsPjxpbnB1dCBpZD0iY2YtbmFtZSI+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPkJyYW5jaGU8L2xhYmVsPjxpbnB1dCBpZD0iY2YtYnJhbmNoZSI+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPktvbnRha3Q8L2xhYmVsPjxpbnB1dCBpZD0iY2Yta29udGFrdCI+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPlBha2V0PC9sYWJlbD48aW5wdXQgaWQ9ImNmLXBha2V0Ij48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+UHJlaXMg4oKsIC8gTW9uYXQ8L2xhYmVsPjxpbnB1dCBpZD0iY2YtcHJlaXMiIHR5cGU9Im51bWJlciIgc3RlcD0iYW55Ij48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+U3RhdHVzPC9sYWJlbD48c2VsZWN0IGlkPSJjZi1zdGF0dXMiPiR7c3RhdHVzT3B0c308L3NlbGVjdD48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImZpZWxkIj48bGFiZWw+TsOkY2hzdGVyIFNjaHJpdHQ8L2xhYmVsPjxpbnB1dCBpZD0iY2Ytc2Nocml0dCI+PC9kaXY+CiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+PGxhYmVsPk5vdGl6ZW48L2xhYmVsPjx0ZXh0YXJlYSBpZD0iY2Ytbm90aXplbiI+PC90ZXh0YXJlYT48L2Rpdj4KICAgIDxkaXYgY2xhc3M9ImJ0bnJvdyI+CiAgICAgIDxidXR0b24gY2xhc3M9ImJ0biBwcmltYXJ5IiBpZD0iY2Ytc2F2ZSI+4pyTIFNwZWljaGVybjwvYnV0dG9uPgogICAgICA8YnV0dG9uIGNsYXNzPSJidG4iIGlkPSJjZi1jYW5jZWwiPkFiYnJlY2hlbjwvYnV0dG9uPgogICAgICA8c3BhbiBpZD0iY2YtbXNnIiBjbGFzcz0iaGludCIgc3R5bGU9ImFsaWduLXNlbGY6Y2VudGVyIj48L3NwYW4+CiAgICA8L2Rpdj4KICBgOwogIGJvZHkucHJlcGVuZChmb3JtKTsKICAvLyBXZXJ0ZSBlaW5zZXR6ZW4gKHNpY2hlciwgdmlhIC52YWx1ZSkKICAkKCJjZi1uYW1lIikudmFsdWUgPSBjLm5hbWUgfHwgIiI7CiAgJCgiY2YtYnJhbmNoZSIpLnZhbHVlID0gYy5icmFuY2hlIHx8ICIiOwogICQoImNmLWtvbnRha3QiKS52YWx1ZSA9IGMua29udGFrdCB8fCAiIjsKICAkKCJjZi1wYWtldCIpLnZhbHVlID0gYy5wYWtldCB8fCAiIjsKICAkKCJjZi1wcmVpcyIpLnZhbHVlID0gYy5wcmVpcyAhPSBudWxsID8gYy5wcmVpcyA6ICIiOwogICQoImNmLXNjaHJpdHQiKS52YWx1ZSA9IGMubmFlY2hzdGVyX3NjaHJpdHQgfHwgIiI7CiAgJCgiY2Ytbm90aXplbiIpLnZhbHVlID0gYy5ub3RpemVuIHx8ICIiOwogIGZvcm0uc2Nyb2xsSW50b1ZpZXcoe2JlaGF2aW9yOiJzbW9vdGgiLCBibG9jazoic3RhcnQifSk7CgogICQoImNmLWNhbmNlbCIpLm9uY2xpY2sgPSAoKT0+IGxvYWRDdXN0b21lcnMoKTsKICAkKCJjZi1zYXZlIikub25jbGljayA9IGFzeW5jICgpPT57CiAgICBjb25zdCBuYW1lID0gJCgiY2YtbmFtZSIpLnZhbHVlLnRyaW0oKTsKICAgIGNvbnN0IG1zZyA9ICQoImNmLW1zZyIpOwogICAgaWYgKCFuYW1lKXsgbXNnLnRleHRDb250ZW50PSJOYW1lIGZlaGx0LiI7IG1zZy5zdHlsZS5jb2xvcj0idmFyKC0tcm9zZSkiOyByZXR1cm47IH0KICAgIGNvbnN0IGZpZWxkcyA9IHsKICAgICAgbmFtZSwKICAgICAgYnJhbmNoZTogJCgiY2YtYnJhbmNoZSIpLnZhbHVlLnRyaW0oKSwKICAgICAga29udGFrdDogJCgiY2Yta29udGFrdCIpLnZhbHVlLnRyaW0oKSwKICAgICAgcGFrZXQ6ICQoImNmLXBha2V0IikudmFsdWUudHJpbSgpLAogICAgICBwcmVpczogJCgiY2YtcHJlaXMiKS52YWx1ZS50cmltKCksCiAgICAgIHN0YXR1czogJCgiY2Ytc3RhdHVzIikudmFsdWUsCiAgICAgIG5hZWNoc3Rlcl9zY2hyaXR0OiAkKCJjZi1zY2hyaXR0IikudmFsdWUudHJpbSgpLAogICAgICBub3RpemVuOiAkKCJjZi1ub3RpemVuIikudmFsdWUudHJpbSgpLAogICAgfTsKICAgIGNvbnN0IHBheWxvYWQgPSBpc0VkaXQgPyBPYmplY3QuYXNzaWduKHsgb3A6InVwZGF0ZSIsIGlkOmMuaWQgfSwgZmllbGRzKSA6IE9iamVjdC5hc3NpZ24oeyBvcDoiYWRkIiB9LCBmaWVsZHMpOwogICAgJCgiY2Ytc2F2ZSIpLmRpc2FibGVkID0gdHJ1ZTsKICAgIHRyeXsKICAgICAgY29uc3QgciA9IGF3YWl0IGFwaSgiL2FwaS9jdXN0b21lcnMiLCAiUE9TVCIsIHBheWxvYWQpOwogICAgICBpZiAoci5lcnJvcil7IG1zZy50ZXh0Q29udGVudD0i4pqgICIrci5lcnJvcjsgbXNnLnN0eWxlLmNvbG9yPSJ2YXIoLS1yb3NlKSI7ICQoImNmLXNhdmUiKS5kaXNhYmxlZD1mYWxzZTsgfQogICAgICBlbHNlIHJlbmRlckN1c3RvbWVycyhyKTsgICAgIC8vIEFudHdvcnQgZW50aMOkbHQgY3VzdG9tZXJzICsgcmV2ZW51ZQogICAgfWNhdGNoKGUpeyBtc2cudGV4dENvbnRlbnQ9IuKaoCAiK2UubWVzc2FnZTsgbXNnLnN0eWxlLmNvbG9yPSJ2YXIoLS1yb3NlKSI7ICQoImNmLXNhdmUiKS5kaXNhYmxlZD1mYWxzZTsgfQogIH07Cn0KCmFzeW5jIGZ1bmN0aW9uIGRlbGV0ZUN1c3RvbWVyKGMpewogIGlmICghY29uZmlybShgS3VuZGUgwrske2MubmFtZX3CqyB3aXJrbGljaCBsw7ZzY2hlbj9gKSkgcmV0dXJuOwogIHRyeXsKICAgIGNvbnN0IHIgPSBhd2FpdCBhcGkoIi9hcGkvY3VzdG9tZXJzIiwgIlBPU1QiLCB7IG9wOiJkZWxldGUiLCBpZDpjLmlkIH0pOwogICAgaWYgKHIuZXJyb3IpeyBjb25zdCBiPSQoImN1c3RvbWVyc0JvZHkiKTsgYi5wcmVwZW5kKGVyckJveChyLmVycm9yKSk7IH0KICAgIGVsc2UgcmVuZGVyQ3VzdG9tZXJzKHIpOwogIH1jYXRjaChlKXsgJCgiY3VzdG9tZXJzQm9keSIpLnByZXBlbmQoZXJyQm94KCJOZXR6d2Vya2ZlaGxlcjogIitlLm1lc3NhZ2UpKTsgfQp9CgovLyAtLS0tLS0tLS0tIEdlZMOkY2h0bmlzIC0tLS0tLS0tLS0KYXN5bmMgZnVuY3Rpb24gbG9hZE1lbW9yeSgpewogIGNvbnN0IGJvZHkgPSAkKCJtZW1vcnlCb2R5Iik7CiAgYm9keS5pbm5lckhUTUwgPSAnPGRpdiBjbGFzcz0iZW1wdHkiPmzDpGR04oCmPC9kaXY+JzsKICBsZXQgZDsKICB0cnkgeyBkID0gYXdhaXQgYXBpKCIvYXBpL21lbW9yeSIpOyB9CiAgY2F0Y2goZSl7IGJvZHkuaW5uZXJIVE1MPSIiOyBib2R5LmFwcGVuZENoaWxkKGVyckJveCgiS29ubnRlIEdlZMOkY2h0bmlzIG5pY2h0IGxhZGVuOiAiK2UubWVzc2FnZSkpOyByZXR1cm47IH0KICBpZiAoZC5lcnJvcil7IGJvZHkuaW5uZXJIVE1MPSIiOyBib2R5LmFwcGVuZENoaWxkKGVyckJveChkLmVycm9yKSk7IHJldHVybjsgfQoKICBib2R5LmlubmVySFRNTCA9ICIiOwogIGNvbnN0IGZhY3RzID0gZC5mYWN0cyB8fCBbXTsKICBjb25zdCBqb3VybmFsID0gZC5qb3VybmFsIHx8IFtdOwoKICBjb25zdCBoMSA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBoMS5jbGFzc05hbWU9InNlY3QiOyBoMS50ZXh0Q29udGVudD0i8J+noCBXYXMgRGlubyDDvGJlciBkaWNoIHdlacOfIjsKICBib2R5LmFwcGVuZENoaWxkKGgxKTsKICBpZiAoZmFjdHMubGVuZ3RoKXsKICAgIGNvbnN0IHVsID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgidWwiKTsgdWwuY2xhc3NOYW1lPSJmYWN0bGlzdCI7CiAgICBmYWN0cy5mb3JFYWNoKGYgPT4geyBjb25zdCBsaT1kb2N1bWVudC5jcmVhdGVFbGVtZW50KCJsaSIpOyBsaS50ZXh0Q29udGVudD1mOyB1bC5hcHBlbmRDaGlsZChsaSk7IH0pOwogICAgYm9keS5hcHBlbmRDaGlsZCh1bCk7CiAgfSBlbHNlIHsKICAgIGNvbnN0IGU9ZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7IGUuY2xhc3NOYW1lPSJlbXB0eSI7IGUudGV4dENvbnRlbnQ9Ik5vY2ggbGVlciDigJQga2xpY2sgaW0gQ2hhdCBhdWYgwrvwn6egIExlcm5lbsKrLiI7CiAgICBib2R5LmFwcGVuZENoaWxkKGUpOwogIH0KCiAgY29uc3QgaDIgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgaDIuY2xhc3NOYW1lPSJzZWN0IjsgaDIudGV4dENvbnRlbnQ9IvCfk5MgTGV0enRlIE5vdGl6ZW4gKFRhZ2VidWNoKSI7CiAgYm9keS5hcHBlbmRDaGlsZChoMik7CiAgY29uc3QgaldyYXAgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsgaldyYXAuY2xhc3NOYW1lPSJqb3VybmFsIjsKICBjb25zdCBsYXN0ID0gam91cm5hbC5zbGljZSgtMTUpLnJldmVyc2UoKTsKICBpZiAobGFzdC5sZW5ndGgpewogICAgbGFzdC5mb3JFYWNoKGo9PnsKICAgICAgY29uc3QgbGluZSA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOwogICAgICBjb25zdCBkMiA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoInNwYW4iKTsgZDIuY2xhc3NOYW1lPSJkIjsgZDIudGV4dENvbnRlbnQgPSAiWyIrKGouZGF0ZXx8IiIpKyJdICI7CiAgICAgIGxpbmUuYXBwZW5kQ2hpbGQoZDIpOwogICAgICBsaW5lLmFwcGVuZENoaWxkKGRvY3VtZW50LmNyZWF0ZVRleHROb2RlKGoubm90ZXx8IiIpKTsKICAgICAgaldyYXAuYXBwZW5kQ2hpbGQobGluZSk7CiAgICB9KTsKICB9IGVsc2UgewogICAgaldyYXAuaW5uZXJIVE1MID0gJzxkaXYgY2xhc3M9ImVtcHR5Ij4obGVlcik8L2Rpdj4nOwogIH0KICBib2R5LmFwcGVuZENoaWxkKGpXcmFwKTsKfQoKLy8ga2xlaW5lIHJvdGUgRmVobGVyYm94IGbDvHIgUGFuZWxzCmZ1bmN0aW9uIGVyckJveCh0ZXh0KXsKICBjb25zdCBlID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgiZGl2Iik7CiAgZS5jbGFzc05hbWUgPSAibXNnIGVycm9yIjsgZS5zdHlsZS5tYXhXaWR0aD0iMTAwJSI7CiAgY29uc3QgYiA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOyBiLmNsYXNzTmFtZT0iYnViYmxlIjsgYi50ZXh0Q29udGVudCA9IHRleHQ7CiAgZS5hcHBlbmRDaGlsZChiKTsKICByZXR1cm4gZTsKfQoKLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09Ci8vICBTdGFydAovLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KbG9hZFN0YXR1cygpOwppbnB1dEVsLmZvY3VzKCk7Cjwvc2NyaXB0Pgo8L2JvZHk+CjwvaHRtbD4K").decode("utf-8")

import json
import sys
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


def main():
    httpd = None
    for port in PORT_RANGE:
        try:
            httpd = ThreadingHTTPServer((HOST, port), Handler)
            break
        except OSError:
            continue
    if httpd is None:
        print("Konnte keinen freien Port finden (8765–8799)."); sys.exit(1)

    print("\n  🦖  DINO wird gestartet — richte mich kurz selbst ein…\n")
    try:
        d.ensure_ollama()
    except Exception as e:
        print(f"  (Auto-Setup übersprungen: {e})")

    url = f"http://{HOST}:{httpd.server_address[1]}/"
    print("\n  🦖  DINO KI läuft!")
    print(f"  ➜  Dein Chat-Fenster öffnet sich jetzt:  {url}")
    print("  (Dieses Fenster offen lassen — schließen beendet Dino. Stoppen: Strg+C)\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  🦖  Dino macht Feierabend. Bis später!")
        httpd.shutdown()


if __name__ == "__main__":
    main()
