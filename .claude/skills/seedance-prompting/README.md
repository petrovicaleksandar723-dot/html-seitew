# Seedance 2.0 Skill for Claude Code

A Claude Code skill that turns any creative brief into a perfect Seedance 2.0 prompt — every single time.

Built by [@timkoda_](https://instagram.com/timkoda_) for creators who want to stop prompting AI video like a chatbot and start directing it like a filmmaker.

---

## What it does

When installed, this skill teaches Claude Code the full Seedance 2.0 prompting system:

- **The 6-Layer Architecture** (Subject → Action → Environment → Camera → Style → Constraints)
- **Multi-shot bracket syntax** for generating cinematic multi-shot scenes in one prompt
- **Native audio prompting** dictionary (voice emotion, sound effects, music mood, acoustics)
- **Camera movement encyclopedia** (dolly, tracking, orbit, aerial, handheld, locked-off)
- **Positive constraints library** (Seedance doesn't support negative prompts — use these instead)
- **Killer words to avoid** ("fast", "cinematic" alone, "epic", "lots of movement"...)
- **Tested examples** verified working on OpenArt Seedance 2.0

Once loaded, you just describe what you want in plain English, and Claude writes a production-grade Seedance 2.0 prompt following the official ByteDance specification.

---

## Installation

### Option 1 — User-scope (available in every project)

```bash
mkdir -p ~/.claude/skills/seedance-prompting
curl -fsSL https://raw.githubusercontent.com/timkoda/seedance-skill/main/SKILL.md -o ~/.claude/skills/seedance-prompting/SKILL.md
mkdir -p ~/.claude/skills/seedance-prompting/references
curl -fsSL https://raw.githubusercontent.com/timkoda/seedance-skill/main/references/seedance-rules.md -o ~/.claude/skills/seedance-prompting/references/seedance-rules.md
```

Restart Claude Code. The skill loads automatically whenever you mention Seedance, video prompts, or cinematic AI video.

### Option 2 — Clone the repo

```bash
git clone https://github.com/timkoda/seedance-skill.git ~/.claude/skills/seedance-prompting
```

---

## Usage

Once installed, just talk to Claude Code naturally:

> *"Write me a Seedance prompt for a young surfer riding a wave at sunset, tight close-up, with explosive energy"*

> *"Multi-shot scene: traceur running across Parisian rooftops, then jumping between buildings, then landing and looking at camera"*

> *"Cinematic Seedance prompt for a woman walking through a neon Tokyo street, with ambient rain audio"*

Claude will use the skill to output a perfect Seedance 2.0 prompt with the right camera instruction, physics-aware action verbs, positive constraints, and audio cues — ready to paste into OpenArt.

---

## The 6-Layer Architecture (core of the skill)

```
1. SUBJECT       — specific visual features
2. ACTION        — concrete verbs + physics awareness
3. ENVIRONMENT   — location + lighting mood
4. CAMERA        — ONE primary instruction
5. STYLE         — visual references + film vocabulary
6. CONSTRAINTS   — positive statements only
```

Every prompt the skill generates follows this order. Skip a layer and Seedance fills the gap with chaos.

---

## Where Seedance 2.0 runs

Seedance 2.0 is available on:
- **[OpenArt](https://openart.ai/home?utm_source=tolt&utm_medium=affiliate&ref=timkoda)** — most accessible, multimodal inputs (9 images + 3 videos + 3 audio)
- CapCut
- Higgsfield
- Picsart Flow

If you don't have access yet, **[sign up to OpenArt here](https://openart.ai/home?utm_source=tolt&utm_medium=affiliate&ref=timkoda)** — it's where I tested and validated every prompt in this skill.

---

## Credits

Built and tested by [Tim Koda](https://instagram.com/timkoda_) — French AI creative director, @timkoda_ on Instagram.

If this skill saves you time, [leave a tip](https://timkoda.com/tip) or follow for more creator AI tools.

---

## License

MIT — use it, fork it, remix it. Just keep the credit.
