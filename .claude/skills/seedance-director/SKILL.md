---
name: seedance-director
description: Write and direct high-quality Seedance 2.0 video prompts (Higgsfield, fal, or any Seedance surface) — text-to-video, image-to-video, multi-shot sequences, dialogue/lip-sync with voice direction, multilingual lines, and IP-safe character design. Use whenever the user asks for a Seedance/video-generation prompt, a multi-part video story, camera direction, or wants copyrighted characters swapped for original ones.
license: MIT
tags: [seedance, video, prompt-engineering]
---

# Seedance Director

A self-contained prompt-engineering skill for ByteDance Seedance 2.0 (and compatible surfaces: Higgsfield Cinema Studio, fal, Dreamina, Jimeng, CapCut, etc). Core stance: **direct the model, don't micromanage the frame** — give physical, concrete choices instead of vague hype-words.

## Core principles

1. **Be a director, not a hype-writer.** Avoid vague words like "cinematic," "epic," "dynamic." Instead specify physical choices: shot size, camera support, movement, light direction, a clear start and end composition.
2. **One beat, one idea.** A single unbroken shot should carry one clear action/reveal. For a ~15s clip, split into 3 beats (0–5s / 5–10s / 10–15s) rather than cramming five ideas into one paragraph.
3. **Preserve fragile anchors.** Name the 2–3 things that must NOT drift shot-to-shot (face/hair, outfit color, a signature prop, a logo) — models drift on everything you don't pin down.
4. **IP-safe by default.** Never generate named franchise characters, celebrity likenesses, or trademarked logos unless the user explicitly owns the rights. Always offer an original-character rewrite instead (see IP-Safety Checklist below).

## The Shot Contract

Every shot should specify these components — this is the actual lever that makes a prompt read as "directed" instead of "generated":

| Component | Options |
|---|---|
| **Size** | extreme-wide → wide → medium-wide → medium → medium-close → close-up → extreme-close-up → macro |
| **Angle** | eye-level, low, high, overhead, profile, over-the-shoulder, insert |
| **Lens character** | wide spatial energy (24-28mm), natural (35-50mm), portrait compression (85mm+), macro detail |
| **Camera support** | locked-off, handheld, slider, dolly, crane, drone, gimbal |
| **Movement** | push-in, pull-back, lateral track, orbit, pan, tilt, pedestal, crane-up, rack-focus |
| **Subject relation** | camera follows / leads / discovers / holds / observes / blocks the subject |
| **Start & end frame** | a specific composition at t=0 and a specific composition at the cut — not a vague state |

### Movement grammar — when to use what

| Movement | Use for | Avoid when |
|---|---|---|
| Locked-off | lip-sync, on-screen text, logos, VFX precision | you actually want energy |
| Push-in / dolly-in | discovery, reveal, intimacy | subject is unstable/morphing |
| Lateral track | travel, choreography, foreground layering | — |
| Orbit | hero/product shots, statuesque subjects | angle stability matters more than drama |
| Crane / drone | scale, geography, arrival | dialogue or small text needs to read |
| Handheld | realism, tension | identity/face must stay perfectly stable |
| Rack focus | attention shift between two points | already combining a complex move |

### Shot-size rules of thumb
- **Extreme wide** — sells scale/environment; do not demand facial acting, small faces/logos will drift.
- **Wide** — good for movement/dance/blocking; keep the action simple, one clear silhouette read.
- **Medium** — the safe default for dialogue and product-in-use.
- **Close-up** — for emotion, texture, lip-sync; needs a stable (often locked-off) camera.
- **Macro** — fine detail only; avoid combining with large subject motion.

### Prompt pattern (one shot)
```
Shot: [size] [angle], [lens character]. Camera [support] starts on [composition A],
[one movement] at [speed] while [subject does ONE action], ending on [composition B].
Preserve: [fragile anchor 1], [fragile anchor 2].
```

## Multi-beat structure (10–15s clips)

Split into 3 beats instead of one wall of text — this is what makes AI video feel directed instead of generated:
```
0-5s: [establish / hook — one clear image or action]
5-10s: [escalate / complicate — the turn]
10-15s: [payoff — the reveal, impact, or button]
```
Each beat = one camera move + one subject action. Don't restate the whole scene in every beat — build on the previous one.

## Dialogue & voice direction

Seedance renders spoken lines most reliably when you give a **short quoted line + explicit voice direction** right next to it, not just "they say something":
```
DIALOGUE ([language], spoken naturally, no on-screen subtitles): [Character], [voice quality:
age/register/emotion/delivery], says: "[short line in the target language]" ([literal translation]).
```
- Keep lines **short** (one clause) — long lines increase lip-sync drift.
- Always give **voice direction** (e.g. "deep gravelly badass young-male shonen protagonist voice, no falsetto, aggressive delivery" vs "cold commanding villain baritone, contemptuous").
- For non-English lines, write the line in-language AND give a literal translation in parentheses — this measurably improves pronunciation accuracy.
- If a rendered voice comes out too soft/flat, append explicit vocal-quality tags: `"deep gravelly masculine voice, no falsetto, aggressive delivery"` or `"breathy, hushed, trembling"` etc.
- Native ambient/SFX audio goes in a separate `NATIVE AUDIO:` line — don't mix dialogue and ambience in the same sentence.

## IP-Safety Checklist (apply before generating)

Run every prompt through this before submitting:
- [ ] No named characters/franchises/studios (e.g. write "an original masked rooftop courier in a red jacket," not a named superhero)
- [ ] No celebrity or real-person likeness without explicit authorization
- [ ] No brand logos or trademarked marks — use generic/blank labels
- [ ] No copyrighted songs/voices/performances — direct tempo/instrumentation/mood instead
- [ ] Not an exact scene recreation from a protected work — same *function* (genre, mood, camera logic, emotional beat), different concrete details
- [ ] If unclear whether the user owns the IP, default to the original-character rewrite and say so

**Rewrite pattern:** preserve the scene's function (genre / mood / camera logic / emotional beat), replace every identifiable IP element with an original equivalent, and briefly note what changed and why.

## Multilingual note

When writing non-English dialogue, prefer natural short spoken lines over literal word-for-word translation, and always pair the in-language line with a parenthetical translation so the intent is auditable. This applies equally to Japanese, Korean, Chinese, Spanish, and Russian lines.

## Quick templates

**Single establishing shot:**
```
Shot: wide, eye-level, natural 35mm. Camera on a slow crane-up starts on [character] small
against [environment], rising to reveal [scale reveal], ending locked on [final composition].
Preserve: [outfit color], [signature prop]. NATIVE AUDIO: [ambience], no dialogue.
```

**Action beat (3-part, 15s):**
```
0-5s: [size/angle] — [character] does [action A], camera [movement].
5-10s: [size/angle] — [complication/turn], camera [movement].
10-15s: [size/angle] — [payoff], camera [movement] ending on [final composition].
Style: [art direction in one clause]. NATIVE AUDIO: [sfx/ambience], [voice line if any].
```

**Dialogue beat:**
```
[size/angle], locked-off or minimal movement for lip-sync stability.
[Character], [voice direction], says: "[line]" ([translation]).
NATIVE AUDIO: [ambience under the line].
```
