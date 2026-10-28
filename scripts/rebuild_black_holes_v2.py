"""Isolated, resumable rebuild using measured connected narration and current art."""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ['PATH'] = str(ROOT / '.tools/ffmpeg/ffmpeg-9.0.2-full_build/bin') + os.pathsep + os.environ.get('PATH', '')
from remake_studio.common import read_json, write_json, run
from remake_studio.production import build_project, sound, mux_audio
from remake_studio.delivery import package_delivery

SOURCE = ROOT / 'data/remake-jobs/b12026102601'
VOICE = ROOT / 'output/black-holes-point-of-no-return/voice-natural-v2'
JOB = ROOT / 'data/remake-jobs/b12026102702'
DEST = ROOT / 'output/black-holes-point-of-no-return-v2'


def phrase_time(words, phrase):
    clean = lambda s: re.sub('[^a-z0-9]', '', s.lower())
    tokens = [(clean(t), w['start']) for w in words for t in w['text'].split() if clean(t)]
    wanted = [clean(t) for t in phrase.split()]
    hits = [tokens[i][1] + .15 for i in range(len(tokens)) if [t[0] for t in tokens[i:i+len(wanted)]] == wanted]
    if len(hits) != 1:
        raise ValueError(f'Expected one semantic anchor: {phrase}: {hits}')
    return hits[0]


def prepare():
    JOB.mkdir(parents=True, exist_ok=True)
    for name in ('visuals.json', 'research.json', 'qa-editorial.json'):
        shutil.copy2(SOURCE / name, JOB / name)
    script = read_json(VOICE / 'script.json')
    original = read_json(SOURCE / 'script.json')
    assert [s['narration'] for s in script['scenes']] == [s['narration'] for s in original['scenes']]
    write_json(JOB / 'script.json', script)
    voices = read_json(VOICE / 'voice-results.json')
    write_json(JOB / 'voice-results.json', voices)
    public = JOB / 'project/public'
    # Copy only named asset directories, never the old project's node_modules junction.
    for name in ('art', 'real-media'):
        shutil.copytree(SOURCE / 'project/public' / name, public / name, dirs_exist_ok=True)
    shutil.copytree(VOICE / 'project/public/voice', public / 'voice', dirs_exist_ok=True)
    plan = read_json(SOURCE / 'motion-plan.json')
    anchors = {'space-08': 'where interactions and friction', 'space-10': 'reveal bright emission', 'space-19': 'Near the heart of our own galaxy'}
    changes = []
    for scene, voice in zip(script['scenes'], voices):
        for media in plan['scenes'][scene['id']].get('media', []):
            before = media['from']
            start = phrase_time(voice['words'], anchors[scene['id']])
            end = voice['seconds'] + .15
            media['from'] = start
            media['duration'] = min(media['duration'], end - start)
            if scene['id'] == 'space-10':
                # Leave the later model-comparison insert completely unobstructed.
                media['duration'] = min(media['duration'], phrase_time(voice['words'], 'These observations test our models') - start - .15)
            assert media['duration'] > 1
            changes.append(dict(scene=scene['id'], phrase=anchors[scene['id']], previous_start=before, start=start, duration=media['duration']))
    write_json(JOB / 'motion-plan.json', plan)
    write_json(JOB / 'retiming.json', dict(media=changes, narration_words_preserved=True, source_job=SOURCE.name, voice_source=str(VOICE), narration_seconds=sum(v['seconds'] for v in voices)))
    write_json(JOB / 'job.json', dict(id=JOB.name, title=script['title'], status='running', stage='visuals', progress=50, source_job=SOURCE.name, delivery_folder=str(DEST)))
    print(json.dumps(dict(job=str(JOB), media_retimed=changes)))


def build():
    manifest = build_project(JOB, read_json(JOB / 'script.json'), read_json(JOB / 'visuals.json'), read_json(JOB / 'voice-results.json'))
    inventory = []
    for s in manifest['scenes']:
        inventory.append(dict(scene=s['id'], start=s['from']/30, seconds=s['frames']/30, section=s['section_title'], action=s['visual_brief'], voice_words=len(s['words']), cue_source='measured scene word boundaries; contextual phrase matching in continuous components', component='ContinuousSpace + SpaceDetailShots + SpaceHost where applicable'))
    write_json(JOB / 'scene-action-inventory.json', inventory)
    run(['node', ROOT / 'tools/motion-studio/node_modules/typescript/bin/tsc', '--noEmit'], cwd=JOB / 'project', log=JOB / 'typecheck.log')
    sound(JOB, manifest)
    print(json.dumps(dict(frames=manifest['frames'], seconds=manifest['frames']/30, scenes=len(manifest['scenes']), stage='ready-for-preview')))


def deliver():
    old = ROOT / 'output/black-holes-point-of-no-return'
    alternatives = (old / 'title-alternatives.txt').read_text(encoding='utf-8').splitlines()
    for name in ('credits.txt',):
        shutil.copy2(old / name, JOB / 'deliverables' / name)
    result = package_delivery(JOB, DEST, old / 'thumbnail.jpg', alternatives=alternatives)
    for name in ('audio-qa.json', 'export-verification.json', 'contact-sheet.jpg', 'ending.png', 'revision-qa.json'):
        src = JOB / 'deliverables' / name
        if src.exists():
            shutil.copy2(src, DEST / name)
    state = read_json(JOB / 'job.json')
    state.update(status='complete', stage='export', progress=100)
    write_json(JOB / 'job.json', state)
    print(json.dumps(result))


def render():
    pending = JOB / 'deliverables/final.pending.mp4'
    command = ['node', str(ROOT/'tools/motion-studio/node_modules/@remotion/cli/remotion-cli.js'),
               'render', 'src/index.tsx', 'Remake', str(pending), '--codec=h264', '--crf=20',
               '--concurrency=4', '--log=info']
    with (JOB / 'render.log').open('w', encoding='utf-8') as log:
        process = subprocess.Popen(command, cwd=JOB/'project', stdout=log, stderr=subprocess.STDOUT,
                                   creationflags=0x08000000 if os.name == 'nt' else 0)
        code = process.wait(timeout=7200)
    if code:
        raise RuntimeError(f'Render failed ({code}); see {JOB / "render.log"}')
    mux_audio(JOB, pending)
    # Preserve intermediate silent output for bounded recovery until QA is done.
    run([ROOT/'.tools/omnivoice-env/Scripts/python.exe', ROOT/'remake_studio/verify_render.py', JOB], timeout=300, log=JOB/'export-check.log')
    print('Rendered, muxed and verified', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['prepare', 'build', 'render', 'deliver'])
    args = parser.parse_args()
    {'prepare': prepare, 'build': build, 'render': render, 'deliver': deliver}[args.stage]()
