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
