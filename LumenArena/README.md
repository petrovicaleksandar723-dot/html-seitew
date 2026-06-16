# LumenArena — Cinematic Triple-A Mini-Game (Unreal Engine 5, C++)

A small, fully **C++** Unreal Engine 5 game built to look cinematic out of the box:
**Lumen** global illumination + reflections, **Nanite**, **Virtual Shadow Maps**,
**TSR**, and cinematic post-processing. You play a third-person character in a dark
arena and collect glowing orbs — each orb is a colored light source, so Lumen bounces
rich colored GI across the floor for that "rendered" look.

> ⚠️ This is source + config only. Unreal Engine can't run in the cloud sandbox where
> it was generated. Open it on your own machine (with UE5 installed) to build and play.

---

## Requirements
- **Unreal Engine 5.3** (5.2–5.5 will work; adjust `EngineAssociation` in `LumenArena.uproject`)
- Visual Studio 2022 (Windows) with "Game development with C++", **or** Rider / Xcode (macOS)
- A GPU that supports **DX12** (Windows) — required for Lumen / Nanite / VSM

## How to open & play
1. **Right-click `LumenArena.uproject` → "Generate Visual Studio project files"**
   (or open the `.uproject` directly — UE will offer to rebuild the C++ module; click **Yes**).
2. Open the generated solution and **Build** (Development Editor), or just let the editor compile.
3. In the editor, open **any** level — the easiest is `File → New Level → Empty Level`
   (the GameMode builds the floor, lighting and orbs for you).
4. Press **Play (Alt+P)**. Done.

Because `Config/DefaultEngine.ini` sets `GlobalDefaultGameMode`, **every** level
automatically uses `ALumenArenaGameMode`, which spawns the whole playable arena at
`BeginPlay`. No Blueprint wiring, no asset authoring.

## Controls
| Action | Key |
|---|---|
| Move | **WASD** |
| Look | **Mouse** |
| Jump | **Space** |
| Dash | **Left Shift** |

Collect all orbs — the HUD shows your count and time; a banner appears when you finish.

---

## What's inside (and which UE skills it uses)

| File | Role | UE skill |
|---|---|---|
| `LumenArenaCharacter.*` | Third-person `ACharacter`; **Enhanced Input built entirely in C++ at runtime** (WASD→2D axis via Swizzle/Negate modifiers, mouse look, jump, dash via `LaunchCharacter`) | `ue-character-movement`, `ue-input-system` |
| `LumenArenaGameMode.*` | Procedurally spawns floor, cinematic key light and a ring of orbs; places the player; starts the timer | `ue-gameplay-framework`, `ue-procedural-generation` |
| `ArenaGameState.*` | Score / total / timer / finished state | `ue-gameplay-framework` |
| `OrbPickup.*` | Collectible actor: `USphereComponent` overlap, spinning/bobbing `UStaticMeshComponent` (engine sphere), bright `UPointLightComponent` for Lumen GI, dynamic material tint, collect flourish | `ue-actor-component-architecture`, `ue-physics-collision`, `ue-materials-rendering` |
| `ArenaHUD.*` | Code-only Canvas HUD (no UMG assets) | `ue-ui-umg-slate` |
| `*.Build.cs`, `*.Target.cs` | Module + build configuration (`EnhancedInput` dependency) | `ue-module-build-system` |
| `Config/DefaultEngine.ini` | The cinematic render stack: Lumen, Nanite, VSM, TSR, bloom, exposure, motion blur, DX12 | `ue-materials-rendering` |

### Make it even prettier (optional, 30 seconds)
For a full sky instead of the moody void:
- Add **Sky Atmosphere**, a **Directional Light** (Atmosphere Sun Light), **Sky Light**
  (Real-Time Capture) and **Exponential Height Fog** to your level, or just start from
  the **"Basic"** template level.
- Drop a **Post Process Volume** (Unbound), enable **Lumen** in GI/Reflections, crank
  Bloom, add a touch of film grain + vignette + chromatic aberration for that AAA grade.
- Replace the engine sphere with a **Nanite** mesh and a custom **emissive material**
  for glowing orbs with surface detail.

Have fun, Bro. 🎮
