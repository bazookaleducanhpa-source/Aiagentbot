"""Deterministic frame-aligned voice, cheerful library music and restrained SFX mix."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SR = 24000
MUSIC_START_SECONDS = 4
FFMPEG = str(next(iter((ROOT / '.tools/ffmpeg').glob('**/bin/ffmpeg.exe')), 'ffmpeg'))


def decode(path):
    p = subprocess.run([FFMPEG, '-v', 'error', '-i', str(path), '-f', 'f32le', '-ar', str(SR), '-ac', '2', 'pipe:1'], capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode(errors='replace'))
    return np.frombuffer(p.stdout, dtype='<f4').reshape(-1, 2).copy()


def encode(path, samples):
    path.parent.mkdir(parents=True, exist_ok=True)
    p = subprocess.run([FFMPEG, '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', 'pipe:0', '-c:a', 'libmp3lame', '-b:a', '192k', str(path)], input=samples.astype('<f4').tobytes(), capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode(errors='replace'))


def rms(x):
    return float(np.sqrt(np.mean(np.square(x, dtype=np.float64)))) if x.size else 0.


def library():
    target = ROOT / 'assets/music'
    target.mkdir(parents=True, exist_ok=True)
    original = ROOT / 'output/tesla-cappy-vfacts/public/music'
    records = []
    for src in sorted(original.glob('*.mp3')):
        dst = target / src.name
        if not dst.exists() or hashlib.sha256(src.read_bytes()).digest() != hashlib.sha256(dst.read_bytes()).digest():
            shutil.copy2(src, dst)
        records.append({'file': dst.name, 'source': str(src), 'sha256': hashlib.sha256(dst.read_bytes()).hexdigest(), 'rights': 'Existing user project library; no new license or public-domain claim.'})
    if records:
        (target / 'provenance.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
    paths = sorted(target.glob('*.mp3'))
    # These were selected for the earlier user-approved cheerful Tesla sound bed.
    preferred = ['Sugar Cookie.mp3', 'Cosmic Star Candy.mp3', 'SOSO.mp3', 'Monkeys Spinning Monkeys.mp3']
    paths.sort(key=lambda p: preferred.index(p.name) if p.name in preferred else len(preferred))
    if not paths:
        raise FileNotFoundError('No existing music in assets/music or Tesla vfacts library')
    return paths


def make(job):
    job = Path(job).resolve()
    manifest = json.loads((job / 'deliverables/manifest.json').read_text(encoding='utf-8'))
    fps = float(manifest['fps'])
    count = round(manifest['frames'] / fps * SR)
    if count < SR or fps <= 0:
        raise ValueError('Invalid manifest duration')
    voice = decode(job / 'narration.wav')
    if abs(len(voice) - count) > SR / fps + 2:
        raise ValueError('Narration duration does not match manifest frame grid')
    voice = np.pad(voice[:count], ((0, max(0, count-len(voice))), (0, 0)))
    peak = np.max(np.abs(voice), axis=1)
    active = peak > .012
    voice_rms = rms(voice[active])
    if voice_rms < .002:
        raise ValueError('Narration is silent or too quiet')
    music = np.zeros_like(voice)
    playlist = library()
    cursor = 0
    track_index = 0
    tracks = []
    crossfade = SR * 3
    while cursor < count:
        path = playlist[track_index % len(playlist)]
        # User preference: remove the first four seconds of EVERY source track,
        # including its later reappearances; leave the original files intact.
        chunk = decode(path)[SR*MUSIC_START_SECONDS:SR*(MUSIC_START_SECONDS+95)]
        if len(chunk) < SR or rms(chunk) < .0001:
            raise ValueError(f'Music track is too short or silent: {path}')
        chunk *= .1 / rms(chunk)
        fade = min(crossfade, len(chunk)//3)
        chunk[:fade] *= np.linspace(0, 1, fade, dtype=np.float32)[:, None]
        chunk[-fade:] *= np.linspace(1, 0, fade, dtype=np.float32)[:, None]
        end = min(count, cursor + len(chunk))
        music[cursor:end] += chunk[:end-cursor]
        tracks.append({'file': path.name, 'startSeconds': cursor/SR, 'endSeconds': end/SR,
                       'sourceStartSeconds': MUSIC_START_SECONDS,
                       'sourceEndSeconds': MUSIC_START_SECONDS+(end-cursor)/SR,
                       'crossfadeSeconds': fade/SR})
        if end == count:
            break
        cursor += len(chunk)-fade
        track_index += 1
    # Smooth speech detector at 50 Hz: fast attack, slow release; lift gaps gently.
    hop = SR//50
    positions = np.arange(0, count, hop)
    envelope = []
    level = 0.
    for p in positions:
        target = min(1., rms(voice[p:p+hop]) / max(.008, voice_rms*.35))
        level += (target-level) * (.55 if target > level else .06)
        envelope.append(level)
    duck = np.interp(np.arange(count), positions, envelope).astype(np.float32)
    music *= (1.35 - .35*duck)[:, None]
    music *= (voice_rms * 10**(-12/20)) / max(rms(music[active]), 1e-9)
    fade = min(SR*2, count//4)
    music[:fade] *= np.linspace(0, 1, fade, dtype=np.float32)[:, None]
    music[-fade:] *= np.linspace(1, 0, fade, dtype=np.float32)[:, None]
    effects = np.zeros_like(voice)
    rng = np.random.default_rng(137)
    cues = []
    last = -10.
    for scene in manifest.get('scenes', []):
        for index, beat in enumerate(scene.get('beats', [])):
            seconds = (scene.get('from', 0) + beat.get('from', 0))/fps
            requested=beat.get('sfx','none')
            if requested=='none' or seconds-last < 5:
                continue
            # Brief original soft tonal pluck / airy transition. No comic alarms.
            length = round(SR*.34)
            t = np.arange(length, dtype=np.float32)/SR
            if requested in ('soft-pop','chime'):
                phase=2*np.pi*(420*t-280*t*t) if requested=='soft-pop' else 2*np.pi*880*t
                signal = (np.sin(phase) + .25*np.sin(phase*1.5))*np.exp(-18*t)
                kind = requested
            else:
                noise = rng.normal(0, 1, length).astype(np.float32)
                signal = np.convolve(noise, np.ones(17, dtype=np.float32)/17, mode='same')*np.sin(np.pi*t/.34)**2
                kind = requested
            signal *= voice_rms * .32 / max(rms(signal), 1e-9)
            signal[:240] *= np.linspace(0, 1, 240)
            start = round(seconds*SR)
            end = min(count, start+length)
            if start < 0 or start >= count:
                continue
            effects[start:end] += signal[:end-start, None]
            cues.append({'seconds': seconds, 'kind': kind})
            last = seconds
    mix = voice + music + effects
    # Transparent peak ceiling; one shared gain retains balance, no clipping.
    gain = min(1., .89 / max(float(np.max(np.abs(mix))), 1e-9))
    mix *= gain
    public = job/'project/public/sound'
    encode(public/'music.mp3', music)
    encode(public/'effects.mp3', effects)
    encode(job/'deliverables/full-mix.mp3', mix)
    # Full mix is the canonical soundtrack; save it beside stems for Remotion.
    shutil.copy2(job/'deliverables/full-mix.mp3', public/'full-mix.mp3')
    decoded = decode(job/'deliverables/full-mix.mp3')
    qa = {'sampleRate': SR, 'samples': count, 'durationSeconds': count/SR,
          'decodedSamples': len(decoded), 'durationErrorSeconds': abs(len(decoded)-count)/SR,
          'speechRmsDbfs': 20*np.log10(voice_rms),
          'musicBelowSpeechDb': 20*np.log10(voice_rms/max(rms(music[active]), 1e-9)),
          'preLimitPeak': float(np.max(np.abs(voice+music+effects))),
          'limiterGain': gain, 'decodedPeak': float(np.max(np.abs(decoded))),
          'musicTracks': tracks, 'effects': cues,
          'canonicalAudio': 'sound/full-mix.mp3',
          'notes': 'Canonical mix includes narration, music and effects. Do not add separate voice or stems when using it. Exact PCM frame grid; decoded MP3 codec-tail tolerance is 1 ms.'}
    qa['passed'] = bool(qa['durationErrorSeconds'] <= .001 and qa['decodedPeak'] < 1 and 10 <= qa['musicBelowSpeechDb'] <= 15)
    (job/'deliverables/audio-qa.json').write_text(json.dumps(qa, indent=2), encoding='utf-8')
    if not qa['passed']:
        raise RuntimeError('Audio QA failed; inspect deliverables/audio-qa.json')
    print(json.dumps({'durationSeconds': count/SR, 'musicTracks': len(tracks), 'effectCues': len(cues), 'passed': True}))


if __name__ == '__main__':
    make(sys.argv[1])
