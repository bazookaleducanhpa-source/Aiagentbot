# Connected English narration

The user requested on 2026-10-27 that the new connected delivery be retained in the reusable skill. Keep `en-US-GuyNeural`. Reference for delivery direction: https://www.youtube.com/watch?v=5_Fayfx2NUM&t=54s (from 0:54). Borrow narrative rhythm, selective emphasis and pauses before turns. The local reference review used word-timed automatic captions and a downloaded 0:54–1:34 excerpt; do not claim a verified listening assessment or reproduce the speaker's identity/audio.

## Default production choice

Explicitly set `voice_direction: "conversational"` in newly directed scenes. In `remake_studio/voice.py` this is implemented as whole-scene synthesis at `+1%` rate, `+0Hz` pitch and no extra inserted silence. Connected text lets the engine carry intonation across sentences instead of restarting for every sentence. The code's absent-direction fallback remains `neutral`; writing this guide does not change that fallback or automatically migrate existing jobs.

Prefer connected thought groups. Use explicit `voice_segments` only at a meaningful turn, contrast, suspense point or distinct speaker intention; several connected sentences can form one segment. Preserve every narration word and order. Do not split every keyword to make it louder or higher. Start with subtle adjustments around rate `-2%` to `+1%` and pitch `-1Hz` to `+2Hz`; these are examples, not a fixed alternating pattern. Keep extra pauses sparse, often around 0.08–0.16 seconds where needed. Listen to the engine's existing sentence-tail silence before adding more. Avoid slowing an entire emphasis scene or repeating identical pauses at every sentence.

Example preserving whole thoughts:

```json
{
  "voice_segments": [
    {"text": "Imagine sending a beam of light past a dark object. One beam bends and escapes.", "rate": "+1%", "pitch": "+0Hz", "pause_after": 0.08},
    {"text": "Another crosses a boundary, and never comes back. That boundary belongs to a black hole.", "rate": "-2%", "pitch": "-1Hz", "pause_after": 0.16},
    {"text": "How does the universe build something like this?", "rate": "+0%", "pitch": "+2Hz", "pause_after": 0}
  ]
}
```

Rate/pitch controls and punctuation offer limited performance direction; do not promise human acting or unsupported emotion SSML. Keep words intact and avoid fake breaths, random pitch jitter or post-processing that simply stretches the old narration.

## Measure, compare, then integrate

Use `synthesize_directed(job, script)` in an isolated revision directory, preserving old audio and all caches. Cache by text, voice, all prosody/pause settings and synthesis version. Measure sample durations and word boundaries anew. A voice revision changes shot timing and requires retiming semantic cues, scene durations, music/SFX and mix before replacing a film; never drop shorter audio under the old timeline and call it synchronized.

Listen to connected delivery against the previous version: opening, explanatory passage, contrast/question and ending. Check joins, choppy sentence endings, misplaced stress, intelligibility and excessive pauses. Decode/check output for truncation, clipping and timing bounds; leave mixing headroom. Automated metrics do not establish naturalness. If listening is unavailable, mark it pending and present the audio as a candidate.

Current implementation example: `output/black-holes-point-of-no-return/voice-natural-v2/` has `preview.mp3`, full narration, directed script and measured metadata. `scripts/preview_cappy_conversational.py` is a job-specific reproduction helper, not a generic production CLI. The candidate retained 24 scenes with valid word bounds; listening review is pending and `video_updated` is false. The user's request adopts the delivery approach without asserting that the audio or a retimed video has passed listening QA.
