# Seedance 2.0 — Full ByteDance Prompting Specification

## Model Identity
- **Vendor**: ByteDance
- **Model**: Seedance 2.0
- **Available on**: OpenArt, CapCut, Higgsfield, Picsart Flow
- **Killer features**: Multi-shot generation in one prompt, character consistency across cuts, multimodal references (9 images + 3 videos + 3 audio), native audio engine, 9/10 camera control score

## Optimal Prompt Length
- **Single shot**: 60-100 words (sweet spot)
- **Multi-shot 3 shots**: 150-200 words total
- **Hard maximum**: 200 words per generation
- Too short → model fills the gaps badly
- Too long → model ignores layers

## The 6-Layer Architecture
```
1. SUBJECT — specific visual features
2. ACTION — concrete verbs + physics awareness
3. ENVIRONMENT — location + lighting mood
4. CAMERA — ONE primary instruction
5. STYLE — visual references + film vocabulary
6. CONSTRAINTS — positive statements only
```

## Camera Movements (Seedance-Optimized)
| Movement | Term | Effect | Best Use |
|---|---|---|---|
| Push-in | `dolly in` | Moves toward subject | Emotional close-ups, reveals |
| Pull-out | `dolly out` | Moves away to reveal | Environmental context, wide reveals |
| Pan | `pan left` / `pan right` | Horizontal sweep | Tracking subjects laterally |
| Tracking | `tracking shot` | Follows subject in motion | Action sequences, movement |
| Orbit | `orbit` / `arc motion` | Rotates around subject | Product shots, portraits |
| Aerial | `aerial drone shot` | Bird's-eye view | Landscapes, scale, geography |
| Handheld | `handheld at chest level` | Documentary feel with shake | Realism, urgency |
| Fixed | `locked-off` / `static camera` | Completely still | Subject-action focus |

**Always specify the level/height**: "at chest level", "at waist level", "low angle from below", "high angle from above", "bird's eye top-down".

## Physics Awareness (Critical)
Seedance responds to physics descriptions, not just verbs.

| ❌ Vague | ✅ Physics-aware |
|---|---|
| "car turns" | "the tires smoke as the car drifts 90 degrees, weight transferring to the outside wheels" |
| "she jumps" | "she launches off the edge with explosive force, body fully extended in mid-air, arms stretched forward, legs trailing behind" |
| "dust falls" | "dust and loose mortar scatter in the air, particles catching golden hour light" |
| "wind blows" | "wind whips her dress and hair wildly to the right" |

## Lighting (#1 Quality Lever)
If you must add ONE thing to a prompt, make it lighting. Be specific:
- "golden hour late afternoon sun creating sharp rim light through his silhouette"
- "single hard key light from the right carving his profile out of deep blue shadow"
- "soft diffused window light wrapping around her face, warm tones"
- "neon teal and pink reflections from the wet street below"
- "dramatic chiaroscuro with harsh shadows and one bright source"

## Audio Prompting Dictionary

### Voice emotion
- "speaks with explosive enthusiastic attitude"
- "voice is loud, charged, electric, like she just discovered something insane"
- "calm grounded voice, almost a whisper"
- "speaks with intense focused conviction, low and steady"
- "excited rapid delivery, breathless from the action"
- "confident smirk in his voice, like dropping a final truth"

### Sound effects
- "wind whistling loudly past the camera"
- "footsteps echoing on metal rooftops"
- "waves crashing violently against the rocks"
- "rain pattering on the glass"
- "engine roaring, tires screeching"
- "fabric rustling, breath catching"
- "metallic scrape of shoes on the surface"
- "distant city ambience"

### Music mood
- "tense orchestral score building"
- "upbeat electronic beat with synths"
- "somber piano notes drifting"
- "epic cinematic strings"
- "lo-fi hip hop chill"

### Acoustics
- "reverb in large empty space"
- "muffled underwater quality"
- "crisp close-mic vocal"
- "echo bouncing off cathedral walls"
- "tight indoor room tone"

## Constraints — Positive Statements Library

Seedance does NOT support negative prompts. Use these positive equivalents:

| ❌ Negative | ✅ Positive |
|---|---|
| "no blur" | "sharp focus throughout" |
| "no morphing" | "identity stays locked across the entire shot" |
| "no distortion" | "natural anatomy with properly formed limbs" |
| "no jitter" | "smooth controlled motion" |
| "no character drift" | "character consistency maintained on the reference face" |
| "no inconsistency" | "temporal consistency across all frames" |
| "no fragmentation" | "the subject stays perfectly intact as one solid body" |
| "no slow motion" | "natural realtime speed" |
| "no fast cuts" | "single continuous take" |
| "no extra limbs" | "two arms two legs anatomy" |

## Pitfalls — Words That Cause Chaos

| Killer word | Why it fails | Fix |
|---|---|---|
| "fast" alone | Causes uncontrolled chaos | "fast but controlled with smooth easing" |
| "cinematic" alone | Too vague | "cinematic 35mm film look with warm golden grading" |
| "epic" / "amazing" / "beautiful" | Zero practical guidance | Concrete visual descriptors |
| "lots of movement" | Jitter guaranteed | One specific motion described |
| "dynamic" alone | Means nothing to the model | "tracking shot following his movement" |
| "stylized" alone | Too vague | Reference a specific film/artist |

## Multi-Shot Bracket Syntax

Format:
```
[Shot N, X seconds: SHOT DESCRIPTION INCLUDING SUBJECT + ACTION + CAMERA]

[Shot N+1, X seconds: SHOT DESCRIPTION...]

[Shot N+2, X seconds: SHOT DESCRIPTION...]

GLOBAL STYLE LINE outside brackets
GLOBAL CONSTRAINTS LINE outside brackets
```

Rules:
- Each bracket = ONE shot with ONE camera
- Reference the same character across shots: "the same male traceur", "Same dancer"
- Total length: 6-15 seconds across all shots
- Maximum 5 shots per generation (3 is the sweet spot)
- ALWAYS end with global style + constraints OUTSIDE the brackets

## Reference System (Multimodal Inputs)

OpenArt's Seedance 2 implementation accepts:
- **9 images max** — character refs, mood refs, environment refs, palette refs
- **3 videos max** — camera movement refs, energy refs, pacing refs
- **3 audio files max** — voice tone refs, music refs, sound design refs

Best practice for character consistency:
1. Upload ONE clean front-facing portrait of the character (neutral background, good lighting)
2. Always add to the prompt: "identity stays locked on reference face"
3. In multi-shot prompts, refer to "the same [subject]" in shot 2+
4. Don't upload multiple face refs of the same character — splits the identity

## Tested Examples (verified working)

### Hook with voice line + dolly in (validated by Tim Apr 2026)
```
A young athletic male traceur in beige cargo pants and white oversized t-shirt lands hard on a Parisian zinc rooftop, hands violently gripping the edge, dust scattering, looks straight into the camera with intense determined eyes and says "And here's everything you need to master it" with an explosive charged voice like he just discovered something insane. Golden hour sun creates a sharp rim light on his face. Distant Eiffel Tower silhouette glows in golden hour haze. Intense fast dolly in pushing aggressively toward his face during the line, ending on a tight close-up of his eyes. Wind whistles loudly past the camera. Editorial action sport, cinematic 35mm film, warm golden grading. Sharp focus throughout, identity stays locked on reference face.
```

### Surf hook (validated, Blink reel)
```
The woman rides the surfboard towards camera at high speed, crouched low, intense focused expression behind her sunglasses. She suddenly looks up directly into camera lens with a huge excited grin, pure hype energy, and speaks with explosive enthusiastic attitude saying "Steal these 3 Claude creative agents and your workflow will change forever." Her voice is loud, charged, electric, like she just discovered something insane and can't hold it in. Water sprays violently from the board cutting through the ocean. Wind whips her dress and hair wildly. Handheld camera following her closely at water level. Raw action sports energy mixed with fashion editorial confidence. Sharp focus throughout, natural anatomy, identity stays locked.
```

### Multi-shot rooftop scene
```
[Shot 1, 3 seconds: A young male traceur in cargo pants and white tee sprints across a Parisian zinc rooftop directly toward the camera with intense focused expression, golden hour rim light. Handheld camera tracking him at chest level. Wind whistles past.]

[Shot 2, 3 seconds: Same traceur leaps over a gap between two Haussmann buildings in dramatic slow motion, body fully extended, sun behind him creating sharp silhouette. Locked-off side angle camera at the same height.]

[Shot 3, 2 seconds: Tight close-up, he lands and grips the zinc edge of the opposite rooftop, looks into the camera and says "And here's everything you need to master it" with explosive charged voice. Intense fast dolly in pushing toward his determined eyes.]

Editorial fashion action sport, cinematic 35mm film, warm golden grading. Distant Eiffel Tower visible in the haze. Identity stays locked on reference face across all three shots, character consistency maintained, sharp focus throughout, natural anatomy.
```

## Quick Sanity Check Before Generating

Before sending any prompt to Seedance, verify:
- [ ] Subject is specific (outfit, age, distinguishing features)
- [ ] Action has physics description, not just verbs
- [ ] Lighting is described (direction, quality, mood)
- [ ] ONE camera instruction with level/height
- [ ] Style line with film vocabulary (not just "cinematic")
- [ ] Constraints are POSITIVE (no "no/avoid/without")
- [ ] If speaking, voice emotion + audio cue included
- [ ] If multi-shot, brackets used + global style/constraints OUTSIDE
- [ ] Reference face mentioned if character lock needed
- [ ] Word count between 60-200
- [ ] No killer words ("fast", "epic", "amazing", "cinematic" alone)
