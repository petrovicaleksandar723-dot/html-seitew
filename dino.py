#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦖 DINO KI — Terminal-Version.

Deine eigene KI im Terminal. Nutzt dasselbe Gehirn wie die Fenster-Version
(dino_app.py) über das gemeinsame Modul dino_core.

Tipp: Wenn dir Tippen zu technisch ist, nutze lieber die Klick-Oberfläche:
      python dino_app.py     (oder Doppelklick auf Dino-KI-Start.bat)

Starten:  python dino.py
"""

import sys
import dino_core as core

# ── Farben fürs Terminal ───────────────────────────────────────────────
if sys.platform == "win32":
    import os
    os.system("")

class C:
    R = "\033[0m"; B = "\033[1m"; DIM = "\033[2m"
    BLUE = "\033[38;5;75m"; PURPLE = "\033[38;5;141m"
    GREEN = "\033[38;5;79m"; AMBER = "\033[38;5;221m"; ROSE = "\033[38;5;210m"

def col(t, c): return f"{c}{t}{C.R}"

d = core.Dino()

# ── Anzeige-Helfer ─────────────────────────────────────────────────────
def banner():
    art = r"""
        __
       / _)      🦖  D I N O   K I
  .-^^^-/ /          deine eigene KI
__/       /          nutzt das Wissen aller großen KIs
<__.|_|-|_|          und wird jeden Tag schlauer
"""
    print(col(art, C.GREEN))

def line():
    print(col("─" * 64, C.DIM))

def dino_say(t):
    name = d.config["persona"]["assistant_name"]
    print(f"\n{col('🦖 ' + name, C.GREEN + C.B)} {col('›', C.DIM)} {t}\n")

def thinking():
    print(col(f"   🦖 {d.config['persona']['assistant_name']} denkt nach…", C.DIM), end="\r")

def clear_line():
    print(" " * 52, end="\r")

# ── Einstellungs-Befehle ───────────────────────────────────────────────
def cmd_key():
    line()
    print(col("  🔑  API-SCHLÜSSEL (lokal in dino_config.json gespeichert)", C.AMBER + C.B))
    print(col("   Claude : https://console.anthropic.com/  → API Keys", C.DIM))
    print(col("   OpenAI : https://platform.openai.com/api-keys", C.DIM))
    print(col("   Gemini : https://aistudio.google.com/apikey", C.DIM))
    line()
    for prov, label in (("claude", "Claude (empfohlen)"), ("openai", "OpenAI/ChatGPT"), ("gemini", "Gemini")):
        cur = d.config["keys"][prov]
        shown = (cur[:6] + "…" + cur[-4:]) if cur else "—"
        val = input(f"   {label} [{shown}]: ").strip()
        if val:
            d.config["keys"][prov] = val
    d.save_config()
    dino_say(col("Schlüssel gespeichert. 🔒", C.GREEN))

def cmd_modell():
    line()
    print(col("  🧠  WELCHES GEHIRN SOLL DINO BENUTZEN?", C.BLUE + C.B))
    print(col("   [c] Claude  (empfohlen)", C.B))
    for k, (mid, desc) in core.CLAUDE_MODELS.items():
        mark = "✓" if mid == d.config["claude_model"] else " "
        print(f"       {k}) {mark} {desc}")
    print(col("   [o] ChatGPT     [g] Gemini", C.B))
    choice = input("   Wähle (c/o/g) oder Claude-Nummer 1-3: ").strip().lower()
    if choice in core.CLAUDE_MODELS:
        d.config["claude_model"] = core.CLAUDE_MODELS[choice][0]; d.config["provider"] = "claude"
    elif choice in ("c", "claude"):
        d.config["provider"] = "claude"
    elif choice in ("o", "openai", "chatgpt"):
        d.config["provider"] = "openai"
        m = input(f"   OpenAI-Modell [{d.config['openai_model'] or 'z.B. gpt-5.1'}]: ").strip()
        if m: d.config["openai_model"] = m
    elif choice in ("g", "gemini"):
        d.config["provider"] = "gemini"
        m = input(f"   Gemini-Modell [{d.config['gemini_model']}]: ").strip()
        if m: d.config["gemini_model"] = m
    d.save_config()
    dino_say(col(f"Aktiv: {d.provider_label()}", C.GREEN))

def cmd_persona():
    p = d.config["persona"]
    line()
    print(col("  🎭  DINOS PERSÖNLICHKEIT & DEIN HUMOR (Enter = behalten)", C.PURPLE + C.B))
    for key, label in (("assistant_name", "Name der KI"), ("user_name", "Wie Dino dich nennt"),
                       ("business", "Dein Business"), ("humor", "Stil/Humor")):
        val = input(f"   {label} [{p[key]}]: ").strip()
        if val: p[key] = val
    d.save_config()
    dino_say(col("Gespeichert. 🎭", C.GREEN))

def cmd_ziel():
    print(col(f"   Aktuelles Ziel: {d.config['goal']}", C.DIM))
    val = input("   Neues Ziel (Enter = behalten): ").strip()
    if val:
        d.config["goal"] = val; d.save_config()
        dino_say(col("Ziel gespeichert. 🎯", C.GREEN))

# ── Kunden ─────────────────────────────────────────────────────────────
def cmd_kunden():
    while True:
        custs = d.customers()
        line()
        print(col("  👥  KUNDEN & AUFTRÄGE", C.BLUE + C.B))
        line()
        if custs:
            for c in custs:
                preis = core.euro(c["preis"]) + "/Mon" if c.get("preis") else "—"
                print(f"   {col('#'+str(c['id']), C.DIM)} [{col(c['status'], C.AMBER)}] "
                      f"{col(c['name'], C.B)}  {col(c.get('branche',''), C.DIM)}  "
                      f"{c.get('paket','')}  {col(preis, C.GREEN)}")
                if c.get("naechster_schritt"):
                    print(col(f"        → {c['naechster_schritt']}", C.DIM))
        else:
            print(col("   (noch keine Kunden)", C.DIM))
        r = d.revenue()
        print(col(f"\n   💰 Monatsumsatz: {core.euro(r['monthly'])} (~{core.euro(r['weekly'])}/Woche) · "
                  f"{r['active']} aktiv, {r['leads']} Leads", C.GREEN))
        line()
        print(col("   [n] neu   [b] bearbeiten   [l] löschen   [z] zurück", C.DIM))
        ch = input("   > ").strip().lower()
        if ch in ("z", "", "q", "zurück"):
            return
        elif ch == "n":
            _kunde_neu()
        elif ch == "b":
            _kunde_bearbeiten()
        elif ch == "l":
            _kunde_loeschen()

def _kunde_neu():
    print(col("   Neuer Kunde:", C.B))
    name = input("    Name: ").strip()
    if not name:
        return
    branche = input("    Branche: ").strip()
    kontakt = input("    Kontakt: ").strip()
    paket = input("    Paket: ").strip()
    preis = input("    Preis €/Monat: ").strip()
    print(col(f"    Status {core.CUSTOMER_STATUS}", C.DIM))
    status = input("    Status [Lead]: ").strip() or "Lead"
    schritt = input("    Nächster Schritt: ").strip()
    d.add_customer(name=name, branche=branche, kontakt=kontakt, paket=paket,
                   preis=preis, status=status, naechster_schritt=schritt)
    dino_say(col(f"Kunde »{name}« angelegt. 👍", C.GREEN))

def _kunde_bearbeiten():
    cid = input("    Kunden-Nummer (#): ").strip().lstrip("#")
    if not cid.isdigit():
        return
    c = d.get_customer(int(cid))
    if not c:
        dino_say("Kunde nicht gefunden."); return
    print(col(f"   Bearbeite {c['name']} (Enter = behalten):", C.B))
    fields = {}
    for key, label in (("name", "Name"), ("branche", "Branche"), ("kontakt", "Kontakt"),
                       ("paket", "Paket"), ("preis", "Preis €/Monat"),
                       ("status", f"Status {core.CUSTOMER_STATUS}"), ("naechster_schritt", "Nächster Schritt")):
        val = input(f"    {label} [{c.get(key,'')}]: ").strip()
        if val:
            fields[key] = val
    if fields:
        d.update_customer(int(cid), **fields)
        dino_say(col("Aktualisiert. 👍", C.GREEN))

def _kunde_loeschen():
    cid = input("    Kunden-Nummer zum Löschen (#): ").strip().lstrip("#")
    if cid.isdigit() and input("    Wirklich löschen? (ja/nein): ").strip().lower() == "ja":
        d.delete_customer(int(cid))
        dino_say("Gelöscht.")

# ── Gedächtnis / Aktionen ──────────────────────────────────────────────
def cmd_gedaechtnis():
    line()
    print(col("  🧠  DINOS GEDÄCHTNIS", C.PURPLE + C.B))
    line()
    print(col("  Dauerhaftes Wissen:", C.B))
    facts = d.memory.get("facts", [])
    for x in facts:
        print(f"   • {x}")
    if not facts:
        print(col("   (leer — nutze /lernen)", C.DIM))
    journal = d.memory.get("journal", [])
    print(col(f"\n  Notizen (letzte 10 von {len(journal)}):", C.B))
    for j in journal[-10:]:
        print(col(f"   [{j['date']}] ", C.DIM) + j["note"])
    line()

def run(fn, *args):
    print(); thinking()
    text, err = fn(*args)
    clear_line()
    dino_say(col(err, C.ROSE) if err else text)

def cmd_lernen(history):
    if not history:
        dino_say("Wir haben noch nicht geredet — nichts zu lernen. 😉"); return
    print(); thinking()
    count, err = d.learn(history)
    clear_line()
    if err:
        dino_say(col(err, C.ROSE))
    elif count:
        dino_say(col(f"Gemerkt! Mein Gedächtnis hat jetzt {count} Fakten über dich. 🧠", C.GREEN))
    else:
        dino_say("Nichts Neues zum Merken gefunden.")

def cmd_rat(history, frage):
    if not frage:
        frage = input(col("   Frage an alle KIs: ", C.AMBER)).strip()
    if not frage:
        return
    print(); thinking()
    answers, synthese, err = d.rat(history, frage)
    clear_line()
    if err:
        dino_say(col(err, C.ROSE)); return
    line()
    for name, ans in answers.items():
        print(f"\n{col('▸ ' + name, C.BLUE + C.B)}\n{ans}\n")
    if synthese:
        print(col("  ✦ DINOS FAZIT (aus allen KIs):", C.GREEN + C.B))
        print(synthese + "\n")
    line()

def cmd_hilfe():
    name = d.config["persona"]["assistant_name"]
    line()
    print(col(f"  🦖  {name} KI — BEFEHLE", C.GREEN + C.B))
    line()
    for cmd, desc in [
        ("einfach schreiben", "ganz normal mit Dino reden"),
        ("/plan", "realistischen Wochen-Geldplan erstellen"),
        ("/tag", "Tages-Check-in: 3 wichtigste Geld-Aktionen für heute"),
        ("/kunden", "Kunden & Aufträge verwalten"),
        ("/rat <frage>", "alle KIs fragen + Fazit"),
        ("/lernen", "Dino merkt sich dauerhaft, was er gelernt hat 🧠"),
        ("/gedächtnis", "zeigen, was Dino weiß"),
        ("/persona", "Name, Humor & Business einstellen"),
        ("/ziel", "Geld-Ziel festlegen"),
        ("/modell", "Gehirn wählen (Claude/ChatGPT/Gemini)"),
        ("/key", "API-Schlüssel eintragen"),
        ("/neu", "neues Gespräch (Gedächtnis bleibt)"),
        ("/ende", "Dino beenden"),
    ]:
        print(f"   {col(cmd.ljust(18), C.AMBER)} {desc}")
    line()

# ── Hauptschleife ──────────────────────────────────────────────────────
def main():
    banner()
    print(col(f"  Gehirn: {d.provider_label()}", C.DIM) +
          col(f"   |   {len(d.memory.get('facts', []))} Fakten   |   {len(d.customers())} Kunden", C.DIM))
    print(col("  /hilfe für alle Befehle  ·  Tipp: Fenster-Version → python dino_app.py", C.DIM))
    line()

    if not d.has_any_key():
        dino_say("Hi! Ich bin Dino, deine eigene KI. 🦖 Ich brauche EINEN API-Schlüssel (am besten "
                 "Claude), sonst kann ich nicht denken.")
        if input(col("   Jetzt eintragen? (j/n): ", C.AMBER)).strip().lower() in ("j", "ja", "y", ""):
            cmd_key()
    if d.has_any_key():
        dino_say(f"Bin bereit, {d.config['persona']['user_name']}. (/plan, /tag, /kunden …)")

    history = []
    while True:
        try:
            user = input(col("Du › ", C.BLUE + C.B)).strip()
        except (EOFError, KeyboardInterrupt):
            print(); break
        if not user:
            continue
        low = user.lower()

        if low in ("/ende", "/exit", "/quit", "/q"):
            break
        elif low in ("/hilfe", "/help", "/h", "?"):
            cmd_hilfe()
        elif low == "/key":
            cmd_key()
        elif low in ("/modell", "/model"):
            cmd_modell()
        elif low == "/persona":
            cmd_persona()
        elif low == "/ziel":
            cmd_ziel()
        elif low in ("/kunden", "/kunde"):
            cmd_kunden()
        elif low in ("/gedächtnis", "/gedaechtnis", "/memory"):
            cmd_gedaechtnis()
        elif low == "/lernen":
            cmd_lernen(history)
        elif low == "/plan":
            run(d.plan)
        elif low == "/tag":
            run(d.tagescheckin)
        elif low.startswith("/rat"):
            cmd_rat(history, user[4:].strip())
        elif low == "/neu":
            history = []
            dino_say("Neues Gespräch. Gedächtnis bleibt. 🦖")
        elif low.startswith("/"):
            dino_say("Den Befehl kenne ich nicht — /hilfe zeigt alle.")
        else:
            history.append({"role": "user", "content": user})
            d.add_journal(f"hat geschrieben: {user}")
            print(); thinking()
            text, err = d.chat(history)
            clear_line()
            if err:
                dino_say(col(err, C.ROSE)); history.pop()
            else:
                dino_say(text)
                history.append({"role": "assistant", "content": text})

    if history and d.config["keys"]["claude"]:
        try:
            print(col("   🦖 Dino merkt sich kurz, was er heute gelernt hat…", C.DIM))
            cmd_lernen(history)
        except Exception:
            pass
    dino_say("Bis später! Ich werde jeden Tag schlauer. 🦖💪")


if __name__ == "__main__":
    main()
