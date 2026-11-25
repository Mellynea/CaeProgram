# Changelog

## v1.3fix

- Fix repeated native allocations in the Minecraft 1.20.x HUD renderer and missing cleanup of legacy preview buffers (issue #2).
- Release preview meshes, GPU buffers and shader resources on failure.
- Reject overflowed dimensions in damaged building files.
- See [v1.3fix release notes](docs/releases/v1.3fix.md) for scope and validation.

## v1.2_fix

Separate corrective release containing the scrolling/native-font clipping and font-state recovery fixes described below, plus source-quality default and 1080p120 projection sharing. Every supported target is packaged independently with project version **1.2_fix**. See the [fix release notes](docs/releases/v1.2_fix.md) for downloads and validation. Existing releases and tags are retained.

## v1.2 local update — source-quality default and 1080p120 sharing

- Default new/reset projection-sharing settings to source quality and capture cadence. Preserve saved mode IDs and offer source, 1080p60 and 1080p120 in one cycle.
- Apply the 120 FPS choice to capture requests, publication pacing and encoder input metadata; preserve aspect ratio in both 1080p modes.
- Retain fractional frame timing when capping publication so small capture jitter does not repeatedly halve the selected frame rate. Native shared captions still have no video-quality controls.

## v1.2 local hotfix — scrolling and native font clipping

- Restore native-font matrices in a finally block if glyph rendering fails, across all seven canvas adapters. Preserve text advance and normal rendering behavior.
- Reuse the already captured scissor rectangle in native-font submission instead of querying the same OpenGL state twice per call.
- Skip invisible native text and material draws when a nested scrolling clip becomes empty. Keep clipping active so off-list content never leaks outside the panel.
- Bound canvas and native-material scissors to the actual destination dimensions. Handle fractional scales, fully offscreen widgets, invalid dimensions and arithmetic overflow.
- Apply the shared canvas protection to every Fabric and Forge build, and add native draw guards to the 1.21.10+ adapters.
- Reproduce the old 26.3 exception with native-font fallback and verify the patched UI across window sizes, font modes and all module settings. The reporter's exact environment remains untested.

## v1.2

Project version is now **v1.2** across ten exact-version Fabric builds and two Forge builds. Filenames, embedded loader metadata, resource-pack descriptions and release manifests identify the same version. See the [v1.2 release notes](docs/releases/v1.2.md) for the complete artifact table, current highlights, setup requirements and verification limits.

This release consolidates the local updates below, including shared application projections, native shared lyrics, invitation privacy controls, AutoParkour prediction and route visualization, music-library interaction and compatibility work. Previous local-update entries and historical release notes retain their original version labels.

## v1.1 local update — private invitation display

- Mask generated and pasted shared-viewing invitations by default, with a separate eye icon to reveal or hide each value.
- Keep one-click copying available while the generated invitation remains hidden. Re-mask invitations on page exit, joining, regeneration and replacement.
- Apply the same behavior to projection and native floating lyrics across all GUI adapters, with localized reveal/hide hints.

## v1.1 local update — shared projections and native lyrics

- Share the selected application screen using revocable invitations, with 1080p/60 FPS and source-resolution/source-cadence modes. Preserve the source aspect ratio and use bounded latest-frame queues to avoid accumulated playback delay.
- Share floating lyrics as native text and 3D scene data, preserving placement, sung text, translations, colors and animation without a video-quality selector.
- Leave the server address blank for direct LAN sharing. Direct invitations authenticate an ephemeral host public key; an optional open-source TLS relay supports reachable internet deployments.
- Encrypt video and caption payloads end to end. Regenerating or revoking an invitation disconnects its viewers; music credentials and API keys are never included in shared payloads.
- Add shared-viewing pages to projection and floating-lyric settings across all supported Fabric and Forge targets. Video requires FFmpeg on both peers; audio sharing is not included.
- Document setup, network requirements and validation in [the shared-projection guide](docs/shared-projections.md).

## v1.1 local update — Forge 1.20.1 panel compositing

- Restore the legacy shader blend-mode cache after offscreen/interface drawing, so vanilla vignette rendering keeps its multiplicative blend instead of covering the world in black.
- Use alpha blending for the full-screen backdrop, so its opening opacity composites over the world instead of overwriting the scene and its alpha.
- Synchronize separate alpha factors with the legacy OpenGL state cache after shader draws and when restoring render state.
- Flush queued vanilla GUI batches before taking the panel's render-state snapshot.
- Show the running Minecraft version in the panel header.

## v1.1 local update — Windows physical panel modifiers

- Read the configured modifier key through Windows physical key state when Minecraft owns the foreground window, after live sampling confirmed Right Shift reaches Windows but not the existing game route.
- Poll the panel binding at render-frame start as well as client-tick start, sharing the same latch and focus/GUI ownership checks.
- Log the loaded binding and first observed panel-key context without recording typed text.

## v1.1 local update — Forge panel-key fallback

- Detect fresh presses of the configured panel key from Minecraft's own GLFW window, including modifier-only bindings whose raw callback never reaches Forge's post-input event.
- Share the key latch with native events to avoid duplicate opens, held-key repeats or reactivation after a binding/focus change. Retain screen and overlay input ownership.

## v1.1 local update — Forge 1.20.1 native client events

- Register native Forge key, extra mouse-button, client tick and GUI post-render handlers after client setup. ForgeGui replaces the vanilla GUI render method.
- Keep custom screen/projection input interception while disabling duplicate shared dispatch in the generated Forge mixins.
- Isolate an IME update failure from feature ticks, and record one-time native hook activation diagnostics without recording typed text.

## v1.1 local update — Forge resource-pack metadata

- Include the root pack.mcmeta required by Forge: format 15 for Minecraft 1.20.1 and the native 69–88 resource/data range for 1.21.10.
- Reject Forge artifacts with missing or incorrect pack metadata during packaging.

## v1.1 local update — Forge bootstrap order

- Keep native render targets and input handling unchanged until client settings, modules and configuration have finished initialization.
- Load world-panel preferences lazily, validate interaction-key conflicts against the loaded GUI binding, and avoid saving absent settings during a failed early startup.

## v1.1 local update — parkour ribbons and Forge screen rendering

- Add an optional broad, joined, shaded world-space ribbon with adjustable width and smooth rainbow or transgender palettes.
- Retain replaced/passed route lines, glow and landing/waypoint marks for a configurable duration, including waypoint-editor visuals. Deduplicate recolored geometry, bound retained storage, fade the final quarter and clear it across worlds or module disable.
- Adapt the Forge 1.20.1 fullscreen-pointer wrapper to ForgeHooksClient.drawScreen, preserving Forge screen events instead of targeting the vanilla call removed by Forge.

## v1.1 local update — GitHub Star shortcut

- Add a separate Star button immediately to the left of the control-panel project link, with a gentle hover animation and explanatory tooltip.
- Open the project page for the user to star on GitHub, with a thank-you message and instructions. The client does not request account access or assume the repository has been starred.
- Translate the tooltip and thank-you messages into all eight interface languages, with the requested gentle cat-style phrasing.

## v1.1 local update — returned progress and unrestricted falls

- Reconcile earlier waypoint/segment returns on resume and large grounded position corrections; cancel stale predictions before replanning from the returned progress.
- Keep unchanged pauses, normal runups and ambiguous crossing segments from rewinding the course. Position matching includes elevation and supports routes with 10,000 checkpoints.
- Allow damaging falls in the live AutoParkour physics policy. Direct downward routes need no intermediate support; upward reach is still calculated from real gravity/jump motion.
- Extend initial and predicted captures to the next checkpoint's actual elevation within the dimension. Remove fixed six-block guide-height bands and fixed downward transition cutoffs under the unrestricted-fall policy.

## v1.1 local update — ordinary-jump to multi-wall transitions

- Prepare neo runups on actual support and search bounded preparation-hop phases when the entry platform is shorter than the normal runway.
- Feed predicted landing and approach states into the compound solver during ordinary motion search, sharing the original node/time budget. Preserve complete existing compound plans.
- Retain native rolling takeoff momentum at entry; do not shorten/restart an already prepared contact jump.
- Add gap-to-three-wall regression courses with sole-final and ordered checkpoints across four rotations and both movement families.

## v1.1 local update — early prediction and faster continuation

- Preserve compatible in-flight predictions through small movement corrections, and catch up late results only after checking the prefix actually followed.
- Prefer rolling jump contacts before terminal braking, leaving verified movement after the handoff while a worker finishes.
- Reuse captured forward terrain for distant-target local windows. Refresh an empty cached prediction before its handoff rather than discovering the failure on arrival.
- Publish long validated compound prefixes without redundant coarse-guide/beam expansion. Reuse unchanged dry cells and immutable air cells during overlapping captures; increase the cell cap while retaining the 1.5 ms scan-slice time budget.

## v1.1 local update — mixed-height wall routes and native IME presentation

- Stop same-level contact lookahead before raised waypoints. Infer a supported flat exit from actual wall geometry when only a distant high final checkpoint is set.
- Preserve rolling prediction through the wall compound before planning raised, turning platforms. Clear stale wall-contact sprint state through a simulated native neutral tick at a stationary start.
- Keep Chinese inventory commits and composition-key isolation while removing IME context reassociation, forced candidate/composition positions and synthetic system carets. The selected input method controls its own presentation.

## v1.1 local update — close-start parkour and Chinese input

- Account for actual retreat/alignment time before selecting the number of consecutive wall jumps in a prediction window. Keep verified rolling continuations when starting directly against the first wall.
- Add nine-wall, unit-voxel regression courses using native player dimensions, center/edge starts, and final-only/ordered checkpoints in both movement families.
- Prevent stale creative-search shortcut suppression from dropping non-ASCII IME commits without matching raw key events.
- Position native Windows composition/candidate windows at focused inventory and custom text fields. Preserve the selected input method and its Unicode delivery; isolate composition navigation from inventory shortcuts.

## v1.1 local update — continuous multi-wall regression

- Prepare momentum-sensitive multi-wall jumps before walking/maze guidance and bypass redundant guide work after finding a complete validated compound.
- Restrict the direct-clearance shortcut to same-height travel so raised support chains are not skipped.
- Add bounded, dense support-top fallback guidance for local raised courses, retaining per-tick collision validation.
- Record bounded route-failure diagnostics without player/world coordinates.

## v1.1 local update — water-aware detours and maze navigation

- Strengthen single-final-waypoint maze guidance and preserve retreat space when progressively widening failed scans, up to 40 blocks.
- Remove the additional 36-block coarse-route cutoff, add a one-cell collision halo and detect repeated completed-prefix regions.
- Compare actual fluid heights with the player's body so dry banks, waterlogged upper surfaces and thin crossings are not rejected as whole wet cells; revalidate fluid changes along the route.
- Keep hazardous terrain and actual fluid entry excluded. This update does not implement swimming or diving.

## v1.1 local update — application projection

- Rotate projection uploads across three fenced textures without waiting on busy surfaces; retain the latest incoming frame and publish only complete pictures.
- Preserve lossless BGRA input with GPU texture channel mapping instead of a full-frame CPU channel-swap loop.
- Use bounded nonblocking WGC readback, copy packed rows in bulk and retain the compositor's original capture timestamps through texture publication.
- Keep ordinary all-key projection controls, physical printable-key forwarding, shortcuts, Unicode text, mouse dragging and scrolling.
- Validate saved settings through each setting's serialized schema, including waypoint arrays and selected support regions.

## v1.1 local update — AutoParkour

- Added independent Forge 1.20.1 and 1.21.10 client builds, versioned JARs, loader path/metadata adapters and explicit Java 21 requirements. Legacy Forge packaging includes SRG remapping, a generated mixin reference map, Java 17 hook bytecode and the required MixinExtras runtime. Both targets pass compilation, artifact checks and offline target/member validation; Forge gameplay testing remains pending.
- Fixed compact consecutive three-block-long neos separated by a single landing block. The planner searches the full visible compound before moving, preserves real transient ground contact and chooses landing states together with the following native takeoff. The new 64-case suite covers two/five walls, two/three-block heights, four rotations, two approach headings and both movement families; every transition retains a twelve-tick jump cadence without an inserted wait.
- Distant targets bias the existing snapshot cube forward while retaining retreat room; the scan size and per-tick work limits are unchanged. This captures later obstacles before entering a compact chain.
- Enabled grounded Creative-mode parkour. Actual flight and Spectator mode remain outside the movement model; starting or switching into flight releases automatic control.
- Added a parkour information master switch and separate controls for the bottom status, detailed metrics, feature-list entry and feature-list status. Route and landing-marker visibility remain independently configurable.
- Completed courses restart at the first waypoint when enabled again; interrupted unchanged courses retain their next checkpoint. The explicit restart control remains available.
- Added early bounded airborne tracking: small live deviations adjust only remaining native yaw inputs, replay the entire suffix and retain safe release and ordered goal coverage. Input and heading are finalized at `serverAiStep` on older clients and `applyInput` on 1.21.10+.
- Reduced unnecessary braking at wide wall exits and retained incoming momentum when a validated takeoff is available. Early handoffs retain an existing verified suffix when a replacement loses checkpoint coverage or takes longer to complete the same goals. Smooth camera mode follows a short trajectory chord to reduce visible steering jitter. These changes passed standalone regressions and all nine artifact builds; user gameplay confirmation remains pending.
- Fixed input/physics parity at the native movement boundary. Vanilla's double-tap or held sprint key can no longer turn planned walking hops into sprint jumps; minor wall grazes retain sprint eligibility while major collisions disable it in both prediction and execution. Collision-dependent sprint state is captured and included in exact-route adoption and beam keys.
- Fixed inferred exits for closely spaced walls landing inside the next wall. The solver selects the actual gap, allows walking takeoffs and prepares its heading/collision state before jumping. Added 80 narrow-gap replays across four rotations, incoming speeds, collision states, ordered/final-only checkpoints and early handoffs; earlier 92 ordinary-ground triple-neo replays remain passing.
- Grounded strides record checkpoint regions crossed between tick samples; airborne/height-changing/long-correction crossings remain excluded. Actual progress is recorded immediately after movement and preserved when resuming an unchanged course. An explicit localized restart control starts again from the first waypoint.
- Added ordinary-ground, same-height triple-neo preparation: momentum-building hops, native delayed edge takeoff and controlled inward landing. Sub-threshold lateral velocity follows each movement family's reset rule. No extra jump height, forced ground flag or direct velocity changes are used.
- Chained obstacle transitions are inferred from collision geometry with only the final user waypoint. Preparation retains clearance from the preceding wall and can retreat for a run-up; long courses continue through safe rolling plans when the final target is outside the current terrain snapshot. Added 92 exact replays covering single/short-approach, consecutive two/three triple-neos in four rotations with 4/5/6-block clear gaps, and eight consecutive triple-neos with full/local-only snapshots, in both movement families.
- Added independent native-input candidates for edge preparation and side wraps, with collision-verified takeoff, controlled air steering and landing/braking. They use actual incoming momentum and surface friction; normal jump height is unchanged. Fine heading alternatives near walls and one/two/four-tick takeoff probes widen search coverage within the existing budgets.
- Corrected ground friction at supported overhangs: the actual supporting block supplies the horizontal sample rather than an off-platform body centre. This affects ice approaches and narrow special-block edges.
- Expanded compound checks to 16 geometries in both movement families (32 replays): one/two-wall neo, three-wall ice approach in four rotations, alternating neos, zigzag islands, head-hitter gap, stairs, fence posts, trapdoors, lily pads, ice turns, ladder-to-gap and slime-to-exit. Three-wall results remain conditional on actual incoming speed/support/landing; no universal same-height completion claim is made.
- Early handoffs wait for a stable grounded span instead of splitting a prepared hop/edge jump. Distant destinations trigger a refreshed future-centred snapshot, rather than repeatedly planning against an old scan boundary. Twenty-four eight-neo replays cover overlapping local prediction in four rotations and both movement families, with no inserted idle inputs. Local obstacle queries stay bounded even for arbitrarily distant target coordinates.
- Prediction now overlaps the running trajectory instead of waiting for its endpoint. Up to eight ordered points inform each window; the next start is selected ahead of time using scan/search latency and observed preparation time. Short initial routes buffer once before movement when needed. Ordinary exact-start adoption reuses worker-validated trajectories without replaying every tick on the render/client thread.
- Added bounded checks of upcoming path corridors and early refreshed snapshots for detected changes, while retaining the live check before every native movement input. Preserved position, momentum and jump cooldown across handoffs; late/invalid results still require safe fallback.
- Added finer airborne-side detour hints and first-jump collision checks for narrow neo routes. Guided and free-heading beam lanes coexist, covering alternative takeoffs instead of forcing an optimistic guide. Added two/three-high wall, double-width neo, triple-width neo with a lower landing, consecutive offset walls and ceiling/narrow-landing checks.
- Added native slime landing/rebound prediction, low-speed slowdown and support-edge selection. Version adapters distinguish 1.20.x block-effect order, newer block-effect order and 26.2 collision-time restitution. High-drop admission requires known unobstructed slime below; unknown/hazardous/ordinary damaging falls remain rejected.
- Fixed shortcut binding being intercepted by other world interfaces. Module and waypoint bindings capture presses, text, repeats and releases; waypoint rebinding works directly in the panel, including outside a world. Esc cancels and Delete/Backspace unbinds; default placement remains F5.
- Added collision-shape A* guidance for wall bypasses, corners, U-shaped exits that initially move away from the target, and offset doorways. The bounded tick search follows guide headings/distances while still validating every native movement tick; ordinary gap/jump search stays available when no complete walking guide is found.
- Missing routes and delayed/stale prefetch results no longer consume the execution-deviation retry allowance. Recoverable drift can replay only the unexecuted inputs against the actual state, including in midair, with goal and safe-release checks before adoption.
- Added saved sequential waypoints with no artificial count/text limit. A detached-camera editor marks aimed block-component tops with a configurable key (F5 by default), supports undo/clear, and returns with Esc. Existing coordinate courses migrate automatically.
- Rolling lookahead plans up to three ordered waypoints and precomputes the following route. Intermediate points retain native movement and velocity; validated continuation applies its first input in the same tick. Late/invalid plans can still trigger a safe wait or replan. Later points cannot skip the active destination. AutoParkour appears near the bottom of the feature list.
- Fixed false stops caused by dropped items, XP and unrelated block-state changes. Only movement-relevant changes along the path invalidate it; real grounded obstructions trigger bounded automatic replanning. Corrected the HUD's per-route tick counter.
- Smooth turning now uses damped render-camera yaw with frame interpolation, shortest-angle wrap and smooth release, while retaining the planner's actual native movement yaw.
- Added native movement inputs and velocity-aware tick simulation against captured block collision shapes. Thin supports over water and vanilla ladder/climbable motion receive dedicated simulation checks; selecting a shape does not guarantee reachability.
- Added bounded asynchronous trajectory search, grounded replanning, local input correction, live terrain validation and safe endpoint checks. Unsupported special physics and unknown terrain are rejected.
- Added world-space predicted routes, takeoff/landing markers, configurable white or OKLab transgender-pride gradients, width, glow, opacity and depth testing.
- Added version-specific input/physics/rendering adapters, repeatable simulation comparisons and isolated Minecraft gameplay checks. Details, measured results and current limitations are in [AutoParkour](docs/AUTO_PARKOUR.md).
- Active parkour inputs update the native input-activity tracker so newer clients do not enter the idle 30 FPS cap during automatic movement; the user's configured frame limit is retained.
- This is a local development update, not a claim of globally optimal routes or world-record performance.

## v1.1 local update — liquid materials and in-world music

- Fixed in-world album-wall and album-floor overlap after enlarging covers. Mosaic positions scale with their covers, animated wall tiles use stable depth layers, and the floor reserves enlarged tile spacing without collapsing nearby rows to one plane.
- Gallery refraction now captures the clean world before drawing any artwork, preventing covers from appearing in other glass surfaces. Both ordinary and through-wall album views use a private depth layer; ordinary mode inherits world occlusion without changing the game's depth contents.
- In-world dragging now consumes native pointer motion at the music page's logical scale. Wall panning and wheel zoom use ray intersections with the actual wall, so the point under the cursor stays anchored. Horizontal wall scrolling pans the wall, hover respects tile seams, and unchanged samples no longer erase coverflow/ring inertia.

- Liquid toggle notifications now use a default blue, pink and white material. Moving pigment volumes share convex lighting, refraction and an advancing meniscus. An adjustable concentration and clear-glass option remain available. Existing profiles are migrated to enable this appearance once; later user choices are retained.
- The feature list's transgender palette colors its liquid-glass surface and glow, keeping the original text colors. Its motion loops continuously.
- Added a real world-space music browser for all eight album layouts, using the current platform library, cached artwork and playback. Tap **F9** to open it with the player's selected layout; tap again to cycle layouts. Hold F9 to browse with the mouse, click a cover to play, and use the wheel according to the layout. Release the key to resume camera control; Esc closes the browser. The key can be rebound in subtitle settings.
- In-world covers now default to **145%** size at **4.5 blocks** from the player. Cover size is independent of scene spacing; older profiles using the former 7-block default are moved closer once while custom distances are retained.
- Fixed gallery glass planes using inconsistent centre/basis transforms, which could shift the corridor across the camera and obscure covers. The room now uses one affine map, aligned square artwork/backing lenses and a near-camera glass cutoff.
- Scene distance, width, height, depth, vertical offset, follow behavior, hold delay and visibility through walls can be customized. Album proportions are preserved, and artwork preloading follows the visible scene.
- These controls and descriptions are translated into all eight interface languages and shared by all nine Fabric builds.

## v1.1 distribution update — project link and licensing

Project version remains **v1.1**. Downloads on both existing **v1.0** and **v1.1** release pages are replaced with the latest nine-version distribution. Every JAR filename and its embedded metadata identify the actual project version as **v1.1**, regardless of the release page label.

### Added

- A fixed, clickable link to the official project repository at the far right of the control-panel row containing the AI Players tab, shared by every supported Minecraft build.

### Licensing

- New original changes in this revision use **PolyForm Noncommercial 1.0.0**, with a required project attribution notice. Redistribution must retain the project attribution and applicable copyright and license notices, including the Required Notice for this revision. This is a source-available, noncommercial revision; commercial permission is not granted by this license.
- The historic MIT grant already requires retaining its copyright and full permission notices in copies or substantial portions. Its original terms and attribution condition are preserved in `LICENSE-LEGACY-MIT`; the updated distribution does not change that historic grant. Third-party licenses are unchanged. See [LICENSING.md](LICENSING.md) for the exact boundary and required notice.
- All nine matching JARs, the source archive and checksums are rebuilt for this update and replace the attachments on both existing release pages. Earlier MIT grants remain identifiable by the original immutable commit in Git history.

## v1.1

v1.1 expands building and particle creation, adds five music-library layouts, and updates all nine supported Fabric builds. Minecraft **1.20.1** and **1.20.4** are newly supported.

### Added

- **Building analysis:** native 3D block icons with names and quantities, maximum length/width/height, and horizontal-layer inspection with separate material totals for each layer.
- **First-person building visits:** enter an independent preview, move with WASD, fly with Space/Shift, and look around without moving your player in the live world.
- **AI building designer:** connect your own API key and model endpoint, describe a building or attach reference images, preview the generated blocks, and request further revisions. Generated buildings use the same materials, layer analysis and visit controls.
- **AI particle designer:** turn text and reference images into native particle compositions and motion paths, preview and revise the result, and export its independent CPS1 configuration code.
- **AI image attachments** in AI Control, AI Players and both designers, with preview/removal before sending. The two new designers have independent refreshable/searchable model catalogues and OpenAI, DeepSeek or custom endpoint controls. Credentials and image attachments stay out of shared configuration codes.
- **Five additional album layouts:** album floor, floating constellation, spiral staircase, music planet and immersive music gallery. There are eight layouts in total; coverflow remains the default. The gallery combines two-sided artwork and camera navigation with liquid glass that matches the surrounding interface.
- **Progressive artwork preloading for every layout:** visible covers are prioritized, and background disk preloading continues through the library without uploading distant covers into the GPU cache. Visible texture protection and bounded caching reduce unnecessary reloads.

### Fixed

- Modern GUI submission and render-state restoration that could clip or hide inventory icons, held items and other native models.
- World-overlay render-target handling that could cause building selection boxes and placement previews to be overwritten.
- Building tasks staying blocked after switching worlds or servers, and library file operations being cancelled when no world was open.
- Missed short **F6/F7/F8** selection taps; marking now reports the selected coordinates or a useful aim hint.
- Chinese input in custom **26.x AI building/particle fields**, including native IME composition/candidate display, caret positioning and focus cleanup.
- Gallery browsing direction and access to later songs; preloading now follows the viewed area independently of the playing track. Aligned renderer and screen prefetch ranges prevent them from cancelling each other's requests.
- Ore-backfill direction tracking during slow or crouched movement.
- Desktop-audio process-tree resolution, inactive-session routing, stalled-helper recovery and route-status reporting.

### Downloads

Project version: **v1.1**. Loader: **Fabric**. Download the JAR matching your exact Minecraft version and install only one CaeDuex JAR in that instance.

| Minecraft | Project version | Java | JAR |
| --- | --- | --- | --- |
| 1.20.1 | v1.1 | 21+ | `caeduex-v1.1-fabric-mc1.20.1.jar` |
| 1.20.4 | v1.1 | 21+ | `caeduex-v1.1-fabric-mc1.20.4.jar` |
| 1.21.4 | v1.1 | 21+ | `caeduex-v1.1-fabric-mc1.21.4.jar` |
| 1.21.10 | v1.1 | 21+ | `caeduex-v1.1-fabric-mc1.21.10.jar` |
| 1.21.11 | v1.1 | 21+ | `caeduex-v1.1-fabric-mc1.21.11.jar` |
| 26.1 | v1.1 | 25+ | `caeduex-v1.1-fabric-mc26.1.jar` |
| 26.1.1 | v1.1 | 25+ | `caeduex-v1.1-fabric-mc26.1.1.jar` |
| 26.1.2 | v1.1 | 25+ | `caeduex-v1.1-fabric-mc26.1.2.jar` |
| 26.2 | v1.1 | 25+ | `caeduex-v1.1-fabric-mc26.2.jar` |

**The 1.20.1 and 1.20.4 builds also require Java 21 or newer.** Source code and `SHA256SUMS.txt` are attached alongside the nine JARs.

### Verification and known limits

All nine targets passed separate builds, exact Minecraft/Java metadata checks, mixin-content checks and feature-scope checks. Isolated in-game workflows were checked on 1.20.1, 1.20.4 and 1.21.4. Additional CPU tests cover building jobs, Unicode editing, album geometry/picking and artwork preloading, and the gallery material was rendered in a separate hidden OpenGL context.

The latest modern rendering, IME, building-marker and music-page integration changes still need broader gameplay feedback. Paid-provider generation, every external application, Vulkan and exhaustive multiplayer behavior have not been tested. Some applications cannot migrate an already-open audio stream: restart playback or select **CABLE Input** in that application when the interface reports that a restart is needed.

CaeDuex is actively maintained. If you try v1.1, reports of what works and what still needs attention are welcome. If the project interests you, consider giving it a Star to follow its progress. Thank you for trying it.
