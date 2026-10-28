# Art and animation techniques adapted for Cappy

Read for character acting, staging or animation-quality revisions. This is a selective adaptation of the user-supplied `D:/thanh-hai-learn-ai-2d-studio.plugin`, not installation of that plugin or proof of its render quality. Inspected: `make-2d-video` style-bible, story-breakdown, engine-api, render-qc; `rig2d.js` pose helpers and reaction-time cafe examples. No bundled executable was run during review. The original archive remains unchanged.

## Transfer the craft, preserve the film

Keep white doodle Cappy, rounded illustrated 2.5D subjects, existing Remotion workflow, English headings/entity labels, measured narration cues, visible layered backgrounds and the four preferred music tracks. Borrow techniques rather than the plugin's black stick figures or fixed dramatic grade. Do not inherit its compulsory camera drift, freeze quotas, 3D quotas, generated music, subtitles, data/title/end cards or language/setup questions. A new renderer is optional only when a concrete shot needs it; do not install Three.js or replace the production timeline just to adopt the guidance.

## Plan a specific performance

Extend the scene-action inventory with shot framing, spoken cue/word occurrence, subject intent, preparation, contact/interaction, consequence, next state, expression/gaze and light direction. These are planning fields, not automatically supported manifest fields. Reuse a location and character design; write fresh action for each spoken idea.

- Establish spatial context, then show the relevant physical mechanism in an insert/cutaway and its result. A Cappy reaction close-up earns its place when it helps communicate a discovery or consequence; it cannot replace the mechanism.
- Keep screen direction, object scale, set geometry and the same hand holding the same prop consistent across cuts. Use a different framing after several similar shots when it improves explanation, without forcing a camera change at every beat.
- Allow a short visual lead-in for preparation when useful (roughly 0.1–0.2 seconds), but land the actual event on the measured spoken cue. Resolve repeated words by occurrence/context, not the first matching word in the scene.

## Pose and contact

Use readable key poses with head, torso, near/far limbs and props as separate controllable parts. Adapt this rigging idea to Cappy's existing proportions and silhouette; do not import the plugin's human skeleton coordinates.

- Gaze toward the target, prepare the body, reach/interact, then react to the result. Blend intentional pose changes over about 0.2–0.35 seconds as a starting point; use the actual action speed to decide.
- Plant feet during weight-bearing phases. Lock a gripping hand to the prop's attachment point while carrying it; release only at the release cue. Derive a held prop's world transform from the hand instead of independently animating two approximations. Grounded subjects need a contact shadow; free-floating space objects do not need a floor.
- For walking, match traveled distance to stride and plant the supporting foot; sliding a static figure is not a walk. Keep limb lengths stable, using local joint rotations or a suitable IK solution where needed.
- Expressions change on the meaning of the words. Eye direction and a brief head turn may precede a gesture. Breathing and blinks are subordinate life detail, never the main animation. Do not introduce compulsory narrator mouth motion or lip-sync across every explanatory object.

## Movement curves describe forces

Use preparation → acceleration → interaction → consequence → settling. Ease a voluntary reach; continue inertia after release; use acceleration for falling where appropriate. Reserve overshoot for flexible subjects or brief contact response, not rigid scientific trajectories. Do not apply a fresh full ease-in/ease-out at every intermediate point of a continuous orbit or stream, since that creates unwanted stopping. Use paths and matching velocities across segment boundaries, or analytic frame-time motion in a dedicated component.

Particles, trails and impact accents must originate from an actual event, inherit its direction and end naturally. Avoid universal ring bursts, shake, sparkles or flashes on every reveal. Continue a useful process (flow, contraction, circulation, measurement) while its result is explained, rather than holding a completed reveal with decorative wobble.

## Light, depth and framing

For each reusable set, record palette roles, key-light source/direction, subject material, contact/occlusion shadows, and far/mid/near layers. Separate near and far limbs with controlled values, not a new identity colour. Match the rim to the key source and use it only where it helps separation; keep white Cappy's form and black facial features readable without blowing out the silhouette.

Use a small number of bright accents and a clear subject/background value hierarchy. Adapt the plugin's coherent lighting, not its mostly dark frame ratio. Soft foreground occluders and atmospheric depth are optional; they must not cover the mechanism, headings or target labels. Limit blur/glow so the explanatory shape stays clear at phone size.

Layer motion stays deterministic, visibly perceptible and overscanned per the existing background guidance. Camera movement may reveal space or follow action; it does not count as subject action. Preserve stable screen-space headings and derive identifying labels from actual target transforms. Hard cuts and continuity edits are usually enough; avoid mandatory bars, freeze frames, whip transitions or changing grades that disrupt comprehension.

## Fit the current renderer honestly

`remake_engine/src/index.tsx` generic `Tracks` interpolates entity translation, uniform scale, rotation and opacity; it does not consume joint poses, IK, path curves, per-key easing, camera-depth or expression fields. It retains the first SVG geometry for a reused entity, so swapping the SVG under that ID does not implement a pose morph. Do not write unsupported fields and claim they animate.

For articulated acting, implement local part transforms or compatible path morphs in a dedicated frame-driven component, following existing Cappy/continuous-scene integration. For arcs under generic tracks, use adequate measured intermediate positions while checking unwanted easing stops. Preserve the documented entity IDs, normalized keyframes and target-relative label contract; extend schema, renderer and validation together if adding real capabilities. Determine prop/label world positions from the same transforms that draw them.

## Verify the transfer

For an actual art/animation revision, render representative wide, interaction close-up and result shots before a long export. Compare matching before/after frames at full and small size; inspect short clips at normal speed, including a transition. Check silhouette, lighting, contact, limb stability, acceleration, label tracking, occlusion and overscanned edges. Verify each cue and compare choreography across scenes. Still/contact-sheet inspection does not establish motion quality. Report inspected shot IDs/time ranges and unresolved faults. These techniques are adopted guidance; no new artwork or animation is user-approved until reviewed.
