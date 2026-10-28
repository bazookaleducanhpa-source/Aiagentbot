@C:\Users\Tonny\.codex\RTK.md

# Project guidance

Read the referenced RTK instructions and prefix shell commands with `rtk`. The latest user request takes precedence over the creative defaults below.

## Video defaults

- Latest pacing preference: more distinct activities and shots, with meaningful development roughly every 1.5–3 seconds where narration allows. Plan wide context, physical-process close-ups and consequence/measurement views in each scene's action/shot inventory. Typical actions may resolve around 2.6–3.2 seconds, but avoid rigid cut spam; preserve spoken cues, object continuity and comprehension. Labels remain readable for 2–4 seconds or longer for comparisons. Added shots must explain, not recycle filler or substitute zoom/wobble; art detail should improve clarity. Do not claim unseen scenes verified or new artwork approved.

- Further art improvements should produce soft illustrated 2.5D subjects with meaningful silhouettes, refined organic curves, distinct materials, consistent key/rim lighting and controlled value/depth hierarchy. Avoid flat circles/ring piles and background texture used as a substitute for subject quality. Preserve Cappy's identity. Follow `skills/cappy-video-remake/references/art-direction.md`, compare matching actual renders at full/small sizes, and report only verified current-revision results; a new design is not approved merely because it was generated. Prefer existing tools over unnecessary expensive libraries.

- Background floating must now be clearly visible at normal playback. Start around 60–110 px per five seconds for the nearest background layer at 1080p, then adjust by reviewing the actual clip; this is not a rigid rule. Overscan layers and protect foreground readability. Make causal animation faster and clearer without shifting spoken cues or speeding the voice, and continue meaningful processes instead of freezing after a reveal. Improve rounded artwork and lighting as part of the revision.
- Preferred music is all four existing tracks from `output/tesla-cappy-vfacts/public/music`: Cosmic Star Candy, Monkeys Spinning Monkeys, SOSO and Sugar Cookie. Trim the first four seconds of EACH non-destructively, sequence all four with crossfades and voice ducking, retain SFX and provenance, and preserve original music files.

- Every video requires clearly perceptible moving layered backgrounds: deterministic frame-based visible ambient motion or parallax, overscanned edges and no hard reset seams. Keep background contrast/movement subordinate to narrated subject actions. Section headings stay in their intended layout; object labels follow actual targets, never decorative background drift. QA inspects motion clips, boundaries, visual hierarchy and readability.
- Improve video art/layout in each requested revision and persist specific user-approved lessons in the reusable skill. The user's “UI” request here concerns video presentation, not unrelated website redesign. Do not imply scheduled or unattended continuous work.

- Give narration purposeful emphasis and pauses while retaining the established English GuyNeural identity. Use measured phrase-level rate/pitch changes and explicit pauses; do not claim unsupported emotion SSML or guarantee human acting. Preserve all narration words and cache by every voice/prosody setting.
- Deliver each video as its own folder with `video.mp4`, `thumbnail.jpg` or `.png`, `title.txt` and title alternatives. Thumbnail quality is a primary packaging priority: original cinematic composition, a clear small-size focal subject and attractive truthful framing. Study reference context without copying logos or exact designs. Verify all package files exist before declaring the package complete.

- Highest creative priority: synchronize each spoken idea with the corresponding visible action using measured voice/word timing, keeping meaningful motion continuous into the next idea. Check semantic synchronization and repeated scene choreography before decorative polish. Equal-duration beats, unrelated motion or static-image wobble do not satisfy this requirement. Preserve the other approved defaults.

- Keep a scene-action inventory and match each scene's action and result to its spoken meaning. Reuse art, characters and settings where helpful, but never reuse an entire choreography under different narration as filler. Scanning, surgery and medication must depict distinct supported actions, not the same repeated scan/extract sequence. QA compares scenes for repeated animation/footage; repeat only for an explicit relevant recap.

- Divide content into clear substantive sections with short English 2–5 word headings at the top-left over ongoing visuals. Every script scene includes `section_title`, repeated exactly across contiguous scenes belonging to that section; intro/outro may be empty. Keep the title persistent within its section or subtly reintroduce it on reentry. Do not rename every shot. Section headings and identifying entity labels are permitted clean renderer overlays; text-only title cards, paragraphs and subtitles remain prohibited.

- Write original English narration with restrained jokes. A source link is research for a new explanation, not a script to paraphrase line by line.
- Include a concise topic hook followed by a brief spoken English Cappy welcome/introduction. After the substantive conclusion, speak a concrete topic-specific comment question and a brief explicit like-and-subscribe invitation. Show animated Cappy gestures and non-text icons/props; do not turn this into a text card, subtitle or long channel bumper. Preserve these defaults unless the latest user request overrides them.
- Preserve the approved white doodle capybara mascot and expressive poses. Reference `output/mascot-capybara` and the Tesla V5 artwork for established appearance.
- Viewers should understand through pictures and motion: no burnt-in subtitles, paragraph cards, text-only explanations or endings. Inventory explanatory foreground objects in every scene, including stars, planets, black holes, tools, clocks, vehicles, organisms and cells. Require accurate short English names at introduction/reentry/ambiguity: 1–4 words, generally 2–4 seconds or longer for relationship comparisons, at most 2–3 labels simultaneously. Follow the actual object through motion and transitions; never call a generic planet Earth or generic star the Sun without identification. Decorative background stars need no labels. Render clean overlay labels rather than generated lettering or SVG text. Beat `labels` entries use `{text,x,y,target_entity_id,from,duration}`; x/y are offsets relative to the moving target entity, and from/duration are seconds relative to the beat start. QA checks coverage across every scene, including nonbiological objects. Use an empty labels array when none is needed.
- Match spoken ideas with frequent meaningful visual changes, generally every about 1.5–3 seconds where narration allows. Use multiple detailed illustrations, relevant footage, close-ups and animation rather than long static shots or repetitive generic icons.
- The user rejects image wobble/pan as animation. Show large, smooth continuous causal object actions with preparation, interaction and consequence; carry object identity and matching poses across adjacent beats. Use softer rounded organic art and round stroke caps/joins, not angular stiff shapes or decorative oscillation.
- Use relevant online footage/photos where helpful, researched and attached through curated media manifests with provenance and permission status. Do not claim automatic sourcing or automatically reuse the source video's footage.
- Use cheerful music from the existing library and relevant sound effects, mixed beneath clear narration. Verify sound in the exported file.
- Present predictions as predictions, illustrated with scenarios. Verify factual claims, especially medical claims, against appropriate primary evidence.
- Measure generated voice duration before final animation timing. Reuse scene voice caches and preserve editable project files.

## Agent and file ownership

This remake workflow uses separate research, writing, direction/assets, voice, sound and QA responsibilities. When delegating, assign disjoint output paths and identify one integrator for shared manifests, schema and package files. Do not overwrite another agent's work; coordinate interface changes and record actual agent execution instead of treating role names as proof of delegation.

The local remake app is `remake_studio` with `remake_web`, `remake_engine` and `data/remake-jobs`. The existing `app`, `web`, studio database and publishing workflow remain separate. Do not change unrelated user projects as part of a video job.

The automated pipeline defaults to layered SVG. Host-agent ImageGen artwork can be attached through job `artwork.json`; do not claim the web interface automatically generates raster images. Keep prompts, provenance and media permission status with job artifacts.

## Completion and cleanup

Inspect actual frames and audio and verify the export before declaring completion. Preserve errors and partial artifacts when a stage fails. A running server or valid manifest alone is not a completed video. Do not publish externally without explicit user authorization.

Cleanup must be dependency-aware and limited to proven disposable items in the requested scope. Preserve secrets, user data, installed tool/model environments, reusable music/mascot assets and projects still referenced by live compositions. Verify absolute path containment before removal and never traverse junction targets. Record removed paths and reasons.
