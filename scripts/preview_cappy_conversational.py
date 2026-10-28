"""Create an isolated narration revision; never overwrite the current film timing."""
import asyncio
import copy
import json
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from remake_studio.common import run, write_json
from remake_studio.voice import synthesize_directed, SR


async def main():
    source = ROOT / 'data/remake-jobs/b12026102601'
    out = ROOT / 'output/black-holes-point-of-no-return/voice-natural-v2'
    script = copy.deepcopy(json.loads((source / 'script.json').read_text(encoding='utf-8')))
    for scene in script['scenes']:
        scene.pop('voice_segments', None)
        scene['voice_direction'] = 'conversational'
    # Direct complete thoughts, rather than restarting the voice for each word
    # or adding identical pauses to every sentence. Narration words stay intact.
    script['scenes'][0]['voice_segments'] = [
        dict(text='Imagine sending a beam of light past a dark object. One beam bends and escapes.', rate='+1%', pitch='+0Hz', pause_after=.08),
        dict(text='Another crosses a boundary, and never comes back. That boundary belongs to a black hole.', rate='-2%', pitch='-1Hz', pause_after=.16),
        dict(text='How does the universe build something like this?', rate='+0%', pitch='+2Hz', pause_after=0),
    ]
    write_json(out / 'script.json', script)
    voices = await synthesize_directed(out, script)
    write_json(out / 'voice-results.json', voices)
    for name, count in [('preview', 3), ('narration', len(voices))]:
        wav = out / (name + '.wav')
        with wave.open(str(wav), 'wb') as target:
            target.setnchannels(1)
            target.setsampwidth(2)
            target.setframerate(SR)
            for i, scene in enumerate(script['scenes'][:count]):
                with wave.open(str(out / 'project/public/voice' / (scene['id'] + '.wav')), 'rb') as src:
                    target.writeframes(src.readframes(src.getnframes()))
                if i < count - 1:
                    target.writeframes(b'\0' * (round(.22 * SR) * 2))
        run(['ffmpeg', '-y', '-v', 'error', '-i', wav, '-c:a', 'libmp3lame', '-b:a', '160k', out / (name + '.mp3')])
    invalid = [s['id'] for s, v in zip(script['scenes'], voices) if any(w['start'] < 0 or w['end'] > v['seconds'] + .05 for w in v['words'])]
    report = dict(voice='en-US-GuyNeural', scenes=len(voices), seconds=sum(v['seconds'] for v in voices),
                  reference='https://www.youtube.com/watch?v=5_Fayfx2NUM&t=54s',
                  approach='Connected thought groups; minimal pitch shifts; varied pauses only at narrative turns.',
                  invalid_word_timings=invalid, listening_review='pending',
                  video_updated=False, original_preserved=True)
    write_json(out / 'qa.json', report)
    print(json.dumps(report))


if __name__ == '__main__':
    asyncio.run(main())
