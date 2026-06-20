#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦖 Dino KI — Fenster-Version (Klick-Oberfläche).

Kein Tippen von Befehlen nötig — alles per Klick:
  • Chat mit Dino
  • Kunden & Aufträge verwalten
  • Wochen-Geldplan & Tages-Check-in
  • Gedächtnis ansehen
  • Einstellungen (Schlüssel, Gehirn, Humor, Ziel)

Nutzt tkinter (in Python eingebaut). Starten:  python dino_app.py
"""

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

import dino_core as core

# ── Farben (dunkles Theme, passend zu CleanLines) ──────────────────────
BG = "#0c0f1c"; CARD = "#141a2e"; FG = "#f4f6fb"; MUT = "#98a2b8"
ACCENT = "#60a5fa"; PURPLE = "#a78bfa"; GREEN = "#34d399"; AMBER = "#fbbf24"; ROSE = "#fb7185"
FONT = ("Segoe UI", 10); FONT_B = ("Segoe UI", 10, "bold"); FONT_H = ("Segoe UI", 15, "bold")


class DinoApp:
    def __init__(self, root):
        self.d = core.Dino()
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

        if not self.d.has_any_key():
            self.append_chat("info", "Willkommen! 🦖 Trage zuerst deinen API-Schlüssel unter "
                                     "»⚙ Einstellungen« ein (Claude empfohlen), dann können wir loslegen.")
        else:
            p = self.d.config["persona"]
            self.append_chat("dino", f"Bin bereit, {p['user_name']}! Frag mich was, oder klick auf "
                                     f"»📅 Wochenplan« bzw. »☀️ Heute«. 🦖")

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
        if not self.d.has_any_key():
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
                core.euro(c.get("preis", 0)), c.get("status", ""), c.get("naechster_schritt", "")))
        r = self.d.revenue()
        self.rev_lbl.config(text=f"💰 Monatsumsatz: {core.euro(r['monthly'])}  "
                                 f"(~{core.euro(r['weekly'])}/Woche)  ·  "
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
        if not self.d.has_any_key():
            messagebox.showinfo("Plan", "Trag zuerst einen Schlüssel unter Einstellungen ein.")
            return
        self._plan_out("🦖 Dino baut deinen Wochenplan…")
        self.run_bg(self.d.plan, lambda r: self._plan_done(r))

    def on_today(self):
        if self.busy:
            return
        if not self.d.has_any_key():
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
                                values=["claude", "openai", "gemini"], width=14)
        prov_box.pack(side="left")
        mrow = tk.Frame(wrap, bg=BG); mrow.pack(fill="x", pady=2)
        tk.Label(mrow, text="Claude-Modell", bg=BG, fg=MUT, font=FONT, width=22, anchor="w").pack(side="left")
        self.cmodel_var = tk.StringVar()
        ttk.Combobox(mrow, textvariable=self.cmodel_var, state="readonly", width=22,
                     values=[m[0] for m in core.CLAUDE_MODELS.values()]).pack(side="left")
        field("OpenAI-Modell (z.B. gpt-5.1)", "openai_model", width=30)
        field("Gemini-Modell", "gemini_model", width=30)

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
                     values=core.CUSTOMER_STATUS).pack(fill="x", padx=18)

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
