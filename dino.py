#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦖 DINO KI — deine eigene KI.

Ein echtes Programm, das auf deinem PC läuft. Dino KI ist KEIN eigenes
Modell (das kann niemand auf einem PC bauen) — Dino KI ist DEIN eigener
KI-Assistent, der das Wissen der stärksten KIs der Welt benutzt:

    • Claude  (Anthropic)  — das stärkste Standard-Gehirn
    • ChatGPT (OpenAI)     — optional als zweites Gehirn
    • Gemini  (Google)     — optional als drittes Gehirn

Dino lernt jeden Tag dazu, weil er sich alles über dich und dein Business
in einem Gedächtnis merkt. Er übernimmt deinen Humor, baut dir realistische
Geld-Pläne und macht nur etwas, wenn du OK sagst.

Reines Python (Standardbibliothek) — keine Extra-Pakete nötig.
Starten:  python dino.py     (oder: python3 dino.py)
"""

import json
import os
import sys
import datetime
import urllib.request
import urllib.error

# ── Dateien (liegen neben diesem Programm) ─────────────────────────────
HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(HERE, "dino_config.json")
MEMORY_FILE = os.path.join(HERE, "dino_memory.json")

# ── Farben fürs Terminal ───────────────────────────────────────────────
if sys.platform == "win32":
    os.system("")  # aktiviert Farben in modernen Windows-Terminals

class C:
    R = "\033[0m"; B = "\033[1m"; DIM = "\033[2m"
    BLUE = "\033[38;5;75m"; PURPLE = "\033[38;5;141m"
    GREEN = "\033[38;5;79m"; AMBER = "\033[38;5;221m"
    ROSE = "\033[38;5;210m"; GREY = "\033[38;5;245m"

def c(text, col): return f"{col}{text}{C.R}"

# ── Modelle (Stand: aktuell) ───────────────────────────────────────────
# Standard ist Claude Opus 4.8 — bester Allrounder. Fable 5 ist das
# absolut stärkste Modell (langsamer, teurer).
CLAUDE_MODELS = {
    "1": ("claude-opus-4-8", "Claude Opus 4.8 — stark & schnell (empfohlen)"),
    "2": ("claude-fable-5",  "Claude Fable 5 — das STÄRKSTE Modell der Welt (langsamer)"),
    "3": ("claude-sonnet-4-6", "Claude Sonnet 4.6 — schnell & günstig"),
}

DEFAULT_CONFIG = {
    "provider": "claude",          # claude | openai | gemini
    "claude_model": "claude-opus-4-8",
    "openai_model": "",            # z.B. dein OpenAI-Modellname
    "gemini_model": "gemini-2.5-pro",
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
    "facts": [],     # dauerhaftes Wissen über dich & dein Business
    "journal": [],   # automatische Tages-Notizen (wächst jeden Tag)
}

# ── Laden / Speichern ──────────────────────────────────────────────────
def load(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # fehlende Schlüssel ergänzen (sanfte Migration)
        if isinstance(default, dict):
            for k, v in default.items():
                data.setdefault(k, v)
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return json.loads(json.dumps(default))

def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

config = load(CONFIG_FILE, DEFAULT_CONFIG)
memory = load(MEMORY_FILE, DEFAULT_MEMORY)

def today():
    return datetime.date.today().isoformat()

# ── System-Prompt: hier wird Dino "schlau" über dich ───────────────────
def build_system():
    p = config["persona"]
    facts = memory.get("facts", [])
    journal = memory.get("journal", [])[-25:]
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
{config['goal']}

WAS DU ÜBER {p['user_name'].upper()} & DAS BUSINESS GELERNT HAST (dein Gedächtnis):
{facts_txt}

LETZTE TAGES-NOTIZEN:
{journal_txt}

Wichtig: Du handelst nie eigenmächtig nach außen (keine Mails/Posts ohne Freigabe).
Du machst Vorschläge und {p['user_name']} entscheidet."""

# ── Netzwerk-Helfer ────────────────────────────────────────────────────
def _post(url, headers, body, timeout=300):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

# ── Die drei Gehirne ───────────────────────────────────────────────────
def ask_claude(system, messages, max_tokens=4096, effort="medium"):
    key = config["keys"]["claude"]
    if not key:
        return None, "Kein Claude-Schlüssel. Tippe /key um ihn einzutragen."
    body = {
        "model": config["claude_model"],
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
        data = _post("https://api.anthropic.com/v1/messages", headers, body)
        parts = [b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"]
        text = "".join(parts).strip()
        if data.get("stop_reason") == "refusal":
            return None, "Claude hat aus Sicherheitsgründen abgelehnt. Formulier es anders."
        return text, None
    except urllib.error.HTTPError as e:
        return None, _http_msg(e)
    except Exception as e:
        return None, f"Verbindungsfehler: {e}"

def ask_openai(system, messages, max_tokens=4096):
    key = config["keys"]["openai"]
    if not key:
        return None, "Kein OpenAI-Schlüssel. Tippe /key."
    if not config["openai_model"]:
        return None, "Kein OpenAI-Modell gesetzt. Tippe /modell."
    msgs = [{"role": "system", "content": system}] + messages
    body = {"model": config["openai_model"], "messages": msgs, "max_tokens": max_tokens}
    headers = {"content-type": "application/json", "authorization": f"Bearer {key}"}
    try:
        data = _post("https://api.openai.com/v1/chat/completions", headers, body)
        return data["choices"][0]["message"]["content"].strip(), None
    except urllib.error.HTTPError as e:
        return None, _http_msg(e)
    except Exception as e:
        return None, f"Verbindungsfehler: {e}"

def ask_gemini(system, messages, max_tokens=4096):
    key = config["keys"]["gemini"]
    if not key:
        return None, "Kein Gemini-Schlüssel. Tippe /key."
    contents = []
    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})
    body = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": contents,
        "generationConfig": {"maxOutputTokens": max_tokens},
    }
    model = config["gemini_model"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    headers = {"content-type": "application/json"}
    try:
        data = _post(url, headers, body)
        parts = data["candidates"][0]["content"]["parts"]
        return "".join(p.get("text", "") for p in parts).strip(), None
    except urllib.error.HTTPError as e:
        return None, _http_msg(e)
    except Exception as e:
        return None, f"Verbindungsfehler: {e}"

def _http_msg(e):
    try:
        body = e.read().decode("utf-8")
        info = json.loads(body)
        msg = info.get("error", {}).get("message") or info.get("error", {}).get("type") or body
    except Exception:
        msg = str(e)
    if e.code == 401:
        return f"Schlüssel ungültig (401). Prüf ihn mit /key.  [{msg}]"
    if e.code == 429:
        return f"Zu viele Anfragen / Guthaben leer (429).  [{msg}]"
    return f"Fehler {e.code}: {msg}"

def ask(system, messages, **kw):
    prov = config["provider"]
    if prov == "openai":
        return ask_openai(system, messages, **{k: v for k, v in kw.items() if k == "max_tokens"})
    if prov == "gemini":
        return ask_gemini(system, messages, **{k: v for k, v in kw.items() if k == "max_tokens"})
    return ask_claude(system, messages, **kw)

def provider_label():
    prov = config["provider"]
    if prov == "claude":
        return f"Claude · {config['claude_model']}"
    if prov == "openai":
        return f"ChatGPT · {config['openai_model'] or '(kein Modell)'}"
    return f"Gemini · {config['gemini_model']}"

# ── Anzeige-Helfer ─────────────────────────────────────────────────────
def banner():
    art = r"""
        __
       / _)      🦖  D I N O   K I
  .-^^^-/ /          deine eigene KI
__/       /          nutzt das Wissen aller großen KIs
<__.|_|-|_|          und wird jeden Tag schlauer
"""
    print(c(art, C.GREEN))

def line():
    print(c("─" * 64, C.DIM))

def dino_say(text):
    name = config["persona"]["assistant_name"]
    print(f"\n{c('🦖 ' + name, C.GREEN + C.B)} {c('›', C.DIM)} {text}\n")

def spinner_note():
    print(c(f"   🦖 {config['persona']['assistant_name']} denkt nach…", C.DIM), end="\r")

# ── Gedächtnis-Funktionen ──────────────────────────────────────────────
def add_journal(note):
    memory["journal"].append({"date": today(), "note": note[:280]})
    memory["journal"] = memory["journal"][-200:]  # nicht endlos wachsen
    save(MEMORY_FILE, memory)

def cmd_lernen(history):
    """Dino fasst das Gespräch + Journal zu dauerhaftem Wissen zusammen."""
    if not history:
        dino_say("Wir haben noch nicht geredet — nichts zu lernen. 😉")
        return
    convo = "\n".join(f"{m['role']}: {m['content']}" for m in history[-20:])
    facts_now = "\n".join(f"- {x}" for x in memory["facts"]) or "(noch nichts)"
    sys_p = ("Du bist ein Gedächtnis-Helfer. Lies das Gespräch und das bisherige Wissen. "
             "Gib AUSSCHLIESSLICH eine kurze Liste der wichtigsten DAUERHAFTEN Fakten über "
             "den Nutzer und sein Business zurück (Vorlieben, Ziele, Stil, Business-Details, "
             "Entscheidungen). Eine Zeile pro Fakt, beginnend mit '- '. Keine Erklärung, "
             "keine Wiederholungen, max. 40 Zeilen.")
    user_p = f"BISHERIGES WISSEN:\n{facts_now}\n\nNEUES GESPRÄCH:\n{convo}\n\nAktualisierte Faktenliste:"
    print(); spinner_note()
    text, err = ask_claude(sys_p, [{"role": "user", "content": user_p}], max_tokens=1500, effort="high") \
        if config["keys"]["claude"] else ask(sys_p, [{"role": "user", "content": user_p}])
    print(" " * 50, end="\r")
    if err:
        dino_say(c("Konnte nicht lernen: " + err, C.ROSE)); return
    facts = [ln.strip()[2:].strip() for ln in text.splitlines() if ln.strip().startswith("- ")]
    if facts:
        memory["facts"] = facts[:60]
        save(MEMORY_FILE, memory)
        dino_say(c(f"Gemerkt! Mein Gedächtnis hat jetzt {len(memory['facts'])} Fakten über dich. 🧠", C.GREEN))
    else:
        dino_say("Nichts Neues zum Merken gefunden.")

def cmd_gedaechtnis():
    facts = memory.get("facts", [])
    journal = memory.get("journal", [])
    line()
    print(c("  🧠  DINOS GEDÄCHTNIS", C.PURPLE + C.B))
    line()
    print(c("  Dauerhaftes Wissen:", C.B))
    if facts:
        for x in facts:
            print(f"   • {x}")
    else:
        print(c("   (noch leer — nutze /lernen nach einem Gespräch)", C.DIM))
    print(c(f"\n  Tages-Notizen (letzte 10 von {len(journal)}):", C.B))
    if journal:
        for j in journal[-10:]:
            print(c(f"   [{j['date']}] ", C.DIM) + j["note"])
    else:
        print(c("   (noch leer)", C.DIM))
    line()

def cmd_tag(history):
    """Tages-Check-in: Dino schlägt die 3 wichtigsten Geld-Aktionen für heute vor."""
    sys_p = build_system()
    user_p = ("Mach jetzt meinen Tages-Check-in. Schau auf mein Ziel und dein Gedächtnis. "
              "Gib mir die 3 wichtigsten, realistischen Aktionen für HEUTE, die mich dem "
              "Geld-Ziel näher bringen. Kurz, konkret, machbar in ein paar Stunden. "
              "Danach eine Zeile Motivation in meinem Humor.")
    print(); spinner_note()
    text, err = ask(sys_p, [{"role": "user", "content": user_p}], max_tokens=1200, effort="high")
    print(" " * 50, end="\r")
    if err:
        dino_say(c(err, C.ROSE)); return
    dino_say(text)
    add_journal("Tages-Check-in gemacht.")

def cmd_plan():
    """Realistischer Wochen-Geldplan zum Ziel."""
    sys_p = build_system()
    user_p = (f"Bau mir einen konkreten, REALISTISCHEN Wochenplan, um meinem Ziel näher zu "
              f"kommen: {config['goal']}. "
              "Gib: 1) eine ehrliche Einschätzung was diese Woche realistisch drin ist, "
              "2) Tag-für-Tag Aufgaben (Mo–So), 3) genau, WAS ich verkaufe und an WEN "
              "(passend zu CleanLines), 4) welche Texte/Inhalte Dino dir dafür sofort schreiben kann. "
              "Keine Garantien, keine Abzock-Versprechen — echte Schritte.")
    print(); spinner_note()
    text, err = ask(sys_p, [{"role": "user", "content": user_p}], max_tokens=4096, effort="high")
    print(" " * 50, end="\r")
    if err:
        dino_say(c(err, C.ROSE)); return
    dino_say(text)
    add_journal("Wochen-Geldplan erstellt.")

def cmd_rat(history, frage):
    """Rat der KIs: fragt ALLE eingerichteten Gehirne und lässt Claude zusammenfassen."""
    if not frage:
        frage = input(c("   Deine Frage an den Rat aller KIs: ", C.AMBER)).strip()
    if not frage:
        return
    sys_p = build_system()
    msgs = history + [{"role": "user", "content": frage}]
    answers = {}
    available = []
    if config["keys"]["claude"]: available.append(("Claude", ask_claude))
    if config["keys"]["openai"] and config["openai_model"]: available.append(("ChatGPT", ask_openai))
    if config["keys"]["gemini"]: available.append(("Gemini", ask_gemini))
    if not available:
        dino_say("Kein KI-Gehirn eingerichtet. Tippe /key."); return
    line()
    print(c("  🧠🧠🧠  RAT DER KIS — alle antworten", C.PURPLE + C.B))
    line()
    for name, fn in available:
        print(c(f"   frage {name}…", C.DIM), end="\r")
        text, err = fn(sys_p, msgs, max_tokens=1500) if name != "Claude" else fn(sys_p, msgs, max_tokens=1500, effort="medium")
        print(" " * 40, end="\r")
        answers[name] = text if text else f"(Fehler: {err})"
        print(f"\n{c('▸ ' + name, C.BLUE + C.B)}\n{answers[name]}\n")
    # Synthese durch das beste verfügbare Gehirn
    if len(answers) > 1 and config["keys"]["claude"]:
        joined = "\n\n".join(f"### {k}\n{v}" for k, v in answers.items())
        syn_p = ("Hier sind Antworten mehrerer KIs auf dieselbe Frage. Fasse das BESTE aus allen "
                 "zu einer einzigen, klaren Empfehlung zusammen. Sag, worin sie sich einig sind und "
                 "was die stärkste Idee ist. Im Stil des Nutzers.")
        text, err = ask_claude(sys_p, [{"role": "user", "content": f"FRAGE: {frage}\n\n{joined}\n\n{syn_p}"}],
                               max_tokens=1500, effort="high")
        if text:
            print(c("  ✦ DINOS FAZIT (aus allen KIs):", C.GREEN + C.B))
            print(text + "\n")
    line()

# ── Einstellungs-Befehle ───────────────────────────────────────────────
def cmd_key():
    line()
    print(c("  🔑  API-SCHLÜSSEL (werden lokal in dino_config.json gespeichert)", C.AMBER + C.B))
    print(c("  Leer lassen = unverändert. Schlüssel bekommst du hier:", C.DIM))
    print(c("   Claude : https://console.anthropic.com/  → API Keys", C.DIM))
    print(c("   OpenAI : https://platform.openai.com/api-keys", C.DIM))
    print(c("   Gemini : https://aistudio.google.com/apikey", C.DIM))
    line()
    for prov, label in (("claude", "Claude (empfohlen)"), ("openai", "OpenAI/ChatGPT"), ("gemini", "Google Gemini")):
        cur = config["keys"][prov]
        shown = (cur[:6] + "…" + cur[-4:]) if cur else "—"
        val = input(f"   {label} [{shown}]: ").strip()
        if val:
            config["keys"][prov] = val
    save(CONFIG_FILE, config)
    dino_say(c("Schlüssel gespeichert. 🔒", C.GREEN))

def cmd_modell():
    line()
    print(c("  🧠  WELCHES GEHIRN SOLL DINO BENUTZEN?", C.BLUE + C.B))
    line()
    print(c("   [c] Claude  (empfohlen, stärkstes Standard-Gehirn)", C.B))
    for k, (mid, desc) in CLAUDE_MODELS.items():
        mark = "✓" if mid == config["claude_model"] else " "
        print(f"       {k}) {mark} {desc}")
    print(c("   [o] ChatGPT (OpenAI)", C.B))
    print(c("   [g] Gemini  (Google)", C.B))
    print()
    choice = input("   Wähle (c/o/g) oder Claude-Modell-Nummer 1-3: ").strip().lower()
    if choice in CLAUDE_MODELS:
        config["claude_model"] = CLAUDE_MODELS[choice][0]; config["provider"] = "claude"
    elif choice in ("c", "claude"):
        config["provider"] = "claude"
    elif choice in ("o", "openai", "chatgpt"):
        config["provider"] = "openai"
        m = input(f"   OpenAI-Modellname [{config['openai_model'] or 'z.B. gpt-5.1'}]: ").strip()
        if m: config["openai_model"] = m
    elif choice in ("g", "gemini"):
        config["provider"] = "gemini"
        m = input(f"   Gemini-Modellname [{config['gemini_model']}]: ").strip()
        if m: config["gemini_model"] = m
    save(CONFIG_FILE, config)
    dino_say(c(f"Aktiv: {provider_label()}", C.GREEN))

def cmd_persona():
    p = config["persona"]
    line()
    print(c("  🎭  DINOS PERSÖNLICHKEIT & DEIN HUMOR", C.PURPLE + C.B))
    print(c("  (Enter = unverändert lassen)", C.DIM))
    line()
    for key, label in (("assistant_name", "Name der KI"), ("user_name", "Wie Dino DICH nennt"),
                       ("business", "Dein Business"), ("humor", "Stil/Humor")):
        val = input(f"   {label} [{p[key]}]: ").strip()
        if val:
            p[key] = val
    save(CONFIG_FILE, config)
    dino_say(c("Persönlichkeit gespeichert. 🎭", C.GREEN))

def cmd_ziel():
    line()
    print(c("  🎯  DEIN ZIEL", C.AMBER + C.B))
    print(c(f"   Aktuell: {config['goal']}", C.DIM))
    val = input("   Neues Ziel (Enter = behalten): ").strip()
    if val:
        config["goal"] = val
        save(CONFIG_FILE, config)
        dino_say(c("Ziel gespeichert. 🎯", C.GREEN))

def cmd_vergessen():
    sure = input(c("   Wirklich das ganze Gedächtnis löschen? (ja/nein): ", C.ROSE)).strip().lower()
    if sure == "ja":
        memory["facts"] = []; memory["journal"] = []
        save(MEMORY_FILE, memory)
        dino_say("Gedächtnis geleert. Ich fange bei null an.")
    else:
        dino_say("Abgebrochen — dein Gedächtnis bleibt.")

def cmd_hilfe():
    name = config["persona"]["assistant_name"]
    line()
    print(c(f"  🦖  {name} KI — BEFEHLE", C.GREEN + C.B))
    line()
    cmds = [
        ("einfach schreiben", "ganz normal mit Dino reden"),
        ("/plan", "realistischen Wochen-Geldplan zum Ziel erstellen"),
        ("/tag", "Tages-Check-in: die 3 wichtigsten Geld-Aktionen für heute"),
        ("/rat <frage>", "alle KIs (Claude+ChatGPT+Gemini) fragen + Fazit"),
        ("/lernen", "Dino merkt sich dauerhaft, was er gerade gelernt hat 🧠"),
        ("/gedächtnis", "zeigen, was Dino über dich weiß"),
        ("/persona", "Name, Humor & Business von Dino einstellen"),
        ("/ziel", "dein Geld-Ziel festlegen"),
        ("/modell", "Gehirn wählen (Claude / ChatGPT / Gemini)"),
        ("/key", "API-Schlüssel eintragen"),
        ("/neu", "neues Gespräch starten (Gedächtnis bleibt)"),
        ("/vergessen", "Gedächtnis löschen"),
        ("/hilfe", "diese Hilfe"),
        ("/ende", "Dino beenden"),
    ]
    for cmd, desc in cmds:
        print(f"   {c(cmd.ljust(16), C.AMBER)} {desc}")
    line()

# ── Hauptschleife ──────────────────────────────────────────────────────
def first_run_setup():
    if config["keys"]["claude"] or config["keys"]["openai"] or config["keys"]["gemini"]:
        return
    dino_say("Hi! Ich bin Dino, deine eigene KI. 🦖 Damit ich denken kann, brauche ich "
             "EINEN API-Schlüssel (am besten Claude). Ohne Schlüssel kann ich nicht reden — "
             "der ist gratis erstellbar, du zahlst nur deine Nutzung.")
    go = input(c("   Jetzt Schlüssel eintragen? (j/n): ", C.AMBER)).strip().lower()
    if go in ("j", "ja", "y", "yes", ""):
        cmd_key()

def main():
    banner()
    print(c(f"  Gehirn: {provider_label()}", C.DIM) +
          c(f"   |   Gedächtnis: {len(memory['facts'])} Fakten", C.DIM))
    print(c("  Tippe /hilfe für alle Befehle  ·  /ende zum Beenden", C.DIM))
    line()

    first_run_setup()
    if config["keys"]["claude"] or config["keys"]["openai"] or config["keys"]["gemini"]:
        dino_say(f"Bin bereit, {config['persona']['user_name']}. Worauf hast du Bock? "
                 f"(/plan für deinen Geld-Wochenplan, /tag für heute)")

    history = []  # aktuelles Gespräch (role/content)

    while True:
        try:
            user = input(c("Du › ", C.BLUE + C.B)).strip()
        except (EOFError, KeyboardInterrupt):
            print(); break
        if not user:
            continue

        low = user.lower()
        # ── Befehle ──
        if low in ("/ende", "/exit", "/quit", "/q"):
            break
        if low in ("/hilfe", "/help", "/h", "?"):
            cmd_hilfe(); continue
        if low == "/key":
            cmd_key(); continue
        if low in ("/modell", "/model"):
            cmd_modell(); continue
        if low == "/persona":
            cmd_persona(); continue
        if low == "/ziel":
            cmd_ziel(); continue
        if low in ("/gedächtnis", "/gedaechtnis", "/memory"):
            cmd_gedaechtnis(); continue
        if low == "/lernen":
            cmd_lernen(history); continue
        if low == "/vergessen":
            cmd_vergessen(); continue
        if low == "/plan":
            cmd_plan(); continue
        if low == "/tag":
            cmd_tag(history); continue
        if low.startswith("/rat"):
            cmd_rat(history, user[4:].strip()); continue
        if low == "/neu":
            history = []
            dino_say("Neues Gespräch. Mein Gedächtnis bleibt natürlich. 🦖"); continue
        if low.startswith("/"):
            dino_say("Den Befehl kenne ich nicht — /hilfe zeigt alle."); continue

        # ── Normales Reden ──
        history.append({"role": "user", "content": user})
        add_journal(f"hat geschrieben: {user}")
        print(); spinner_note()
        text, err = ask(build_system(), history, max_tokens=4096, effort="medium")
        print(" " * 50, end="\r")
        if err:
            dino_say(c(err, C.ROSE))
            history.pop()  # fehlgeschlagene Runde nicht behalten
            continue
        dino_say(text)
        history.append({"role": "assistant", "content": text})

    # ── beim Beenden automatisch dazulernen ──
    if history and config["keys"]["claude"]:
        try:
            print(c("   🦖 Dino merkt sich kurz, was er heute gelernt hat…", C.DIM))
            cmd_lernen(history)
        except Exception:
            pass
    dino_say("Bis später! Ich werde jeden Tag ein Stück schlauer. 🦖💪")

if __name__ == "__main__":
    main()
