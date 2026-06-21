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

import dino_core as core

HOST = "127.0.0.1"
PORT_RANGE = range(8765, 8800)

d = core.Dino()
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
        "claude_models": [[mid, desc] for mid, desc in core.CLAUDE_MODELS.values()],
        "ollama_models": [[mid, desc] for mid, desc in core.OLLAMA_MODELS.values()],
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
            self._send_file(core.os.path.join(core.HERE, "dino_chat.html"))
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
        with open(os.path.join(core.HERE, "Dino-Log.txt"), "w", encoding="utf-8") as lf:
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
