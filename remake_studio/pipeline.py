"""Real, cached production stages for one local remake job."""
import asyncio
import hashlib
import json
import os
import math
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from pathlib import Path

from .agents import invoke, RESEARCH, SCRIPT, VISUALS, QA
from .common import read_json, write_json, update, probe
from .source import acquire
from .production import validate_visuals, synthesize, build_project, sound, render


class JobAlreadyRunning(RuntimeError):
    """Another process owns this job; callers must not overwrite its status."""


@contextmanager
def job_lock(job):
    # Keep the file: deleting it creates a race with processes holding its inode.
    handle = (Path(job) / '.execution.lock').open('a+b')
    locked = False
    try:
        handle.seek(0, 2)
        if handle.tell() == 0:
            handle.write(b'0')
            handle.flush()
        handle.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            locked = True
        except OSError as exc:
            raise JobAlreadyRunning('Job is already executing in another process') from exc
        yield
    finally:
        if locked:
            handle.seek(0)
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def render_signature(job, manifest, mix):
    digest = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode())
    digest.update(Path(mix).read_bytes())
    project = Path(job) / 'project'
    files = sorted(p for p in (project / 'src').rglob('*') if p.is_file())
    files += [project / name for name in ('package.json', 'tsconfig.json') if (project / name).is_file()]
    files += sorted({project/'public'/b['art']['file'] for s in manifest.get('scenes',[]) for b in s.get('beats',[]) if b.get('art')})
    files += sorted({project/'public'/m['file'] for s in manifest.get('scenes',[]) for m in s.get('media',[])})
    for path in files:
        digest.update(str(path.relative_to(project)).replace('\\', '/').encode())
        digest.update(b'\0')
        digest.update(path.read_bytes())
    return digest.hexdigest()


def is_job_running(job):
    try:
        with job_lock(job):
            return False
    except JobAlreadyRunning:
        return True


def validate_export(metadata, manifest):
    streams = metadata.get('streams', [])
    if not all(any(s.get('codec_type') == kind for s in streams) for kind in ('audio', 'video')):
        raise RuntimeError('Export must contain both video and audio')
    expected = manifest['frames'] / manifest['fps']
    duration = float(metadata.get('format', {}).get('duration', 0))
    if not math.isfinite(duration) or abs(duration - expected) > max(.25, 2 / manifest['fps']):
        raise RuntimeError(f'Export duration mismatch: expected {expected:.3f}s, got {duration:.3f}s')


def visual_batch(job, title, batch, index):
    role = f'visuals-{index + 1:02d}'
    payload = {
        'title': title, 'scenes': batch,
        'direction': 'For each beat, cue_word must be an exact spoken word at its intended transition. Draw concrete layered pictorial illustrations: 3–7 detailed layers, no lettering inside SVG; short identifying labels belong in the separate labels array. Select enough beats to change composition every 3–6 seconds of narration; use 3–5 beats for longer scenes.',
    }
    result = invoke(job, role, payload, VISUALS)
    try:
        validate_visuals(result, {'scenes': batch})
    except Exception as exc:
        # Includes XML ParseError. One independent repair, then fail honestly.
        result = invoke(job, role + '-repair', {
            **payload, 'invalid_result': result, 'validation_error': str(exc),
            'repair_instructions': 'Repair the supplied result to satisfy the schema and validation error. Preserve scene IDs and useful detailed illustrations. Return the entire corrected batch with valid XML SVG, no words, scripts, external resources or text elements.',
        }, VISUALS)
        validate_visuals(result, {'scenes': batch})
    return result


def generate_visuals(job, script):
    batches = [script['scenes'][i:i + 3] for i in range(0, len(script['scenes']), 3)]
    results = {}
    # Only two in-flight batches, rather than ten queued tasks that continue
    # spending tokens after an early failure. Drain the other active batch so
    # the job lock remains held until all writes from this execution finish.
    with ThreadPoolExecutor(max_workers=2) as workers:
        next_index = 0
        futures = {}
        while next_index < min(2, len(batches)):
            futures[workers.submit(visual_batch, job, script['title'], batches[next_index], next_index)] = next_index
            next_index += 1
        while futures:
            done, _ = wait(futures, return_when=FIRST_COMPLETED)
            for future in done:
                index = futures.pop(future)
                results[index] = future.result()
            update(job, 'visuals', detail=f'Đã vẽ {len(results)}/{len(batches)} nhóm cảnh')
            while len(futures) < 2 and next_index < len(batches):
                futures[workers.submit(visual_batch, job, script['title'], batches[next_index], next_index)] = next_index
                next_index += 1
    return {'scenes': [scene for i in range(len(batches)) for scene in results[i]['scenes']]}


def approved(job, kind):
    path = job / ('approved-' + kind + '.json')
    if not path.exists():
        return None
    raw = read_json(path)
    artifact = raw.get('artifact', raw)
    write_json(job / 'agents' / (kind + '.provenance.json'), {
        'mode': 'supplied-approved-artifact', 'path': str(path),
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'provenance': raw.get('provenance', 'Approved bootstrap artifact supplied to this job'),
    })
    return artifact


def execute(job):
    job = Path(job).resolve()
    with job_lock(job):
        return _execute(job)


def _execute(job):
    data = read_json(job / 'job.json')
    (job / 'deliverables').mkdir(exist_ok=True)
    update(job, 'source', detail='Đọc nội dung và phụ đề video nguồn', error=None)
    source = acquire(job, data['url'])
    update(job, 'source', 'complete', 'Đã đọc nội dung nguồn', title=source['title'])

    update(job, 'research', detail='Kiểm chứng nội dung và lập hướng giải thích')
    research = approved(job, 'research')
    supplied_research = research is not None
    if research is None:
        sheet = job / 'source/contact-sheet.jpg'
        research = invoke(job, 'research', {'source': source, 'notes': data.get('notes', '')}, RESEARCH,
                          images=[sheet] if sheet.is_file() else None)
    write_json(job / 'research.json', research)
    update(job, 'research', 'complete', 'Dùng nghiên cứu đã duyệt, có provenance' if supplied_research else 'Đã hoàn thành nghiên cứu')

    update(job, 'script', detail='Viết lời dẫn tiếng Anh nguyên bản')
    script = approved(job, 'script')
    supplied_script = script is not None
    if script is None:
        script = invoke(job, 'script', {'source': source, 'research': research, 'notes': data.get('notes', '')}, SCRIPT)
    if not script.get('scenes') or len({s['id'] for s in script['scenes']}) != len(script['scenes']):
        raise ValueError('Script needs unique, nonempty scenes')
    if any(not s.get('narration', '').strip() for s in script['scenes']):
        raise ValueError('Every scene must have spoken narration')
    write_json(job / 'script.json', script)
    update(job, 'script', 'complete', f'{len(script["scenes"])} cảnh; ' + ('kịch bản đã duyệt' if supplied_script else 'kịch bản nguyên bản'), title=script['title'])

    script, manifest, mix = editorial_production(job, script, research)

    update(job, 'export', detail='Render MP4 1080p với audio hoàn chỉnh')
    signature = render_signature(job, manifest, mix)
    cache = job / 'deliverables/render-cache.json'
    output = job / 'deliverables/final.mp4'
    if output.exists() and cache.exists() and read_json(cache).get('key') == signature:
        metadata = probe(output)
    else:
        metadata = render(job)
    validate_export(metadata, manifest)
    write_json(cache, {'key': signature})
    update(job, 'export', 'complete', 'MP4 hoàn tất, đã kiểm tra audio/video')
    data = read_json(job / 'job.json')
    data.update(status='complete', progress=100, error=None)
    write_json(job / 'job.json', data)
    return data


def editorial_production(job, original_script, research):
    """Resume bounded revisions without mutating manually approved artifacts."""
    base_key = hashlib.sha256(json.dumps({'script': original_script, 'research': research},
                                        sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    revision_path = job / 'script-revision.json'
    script, attempt = original_script, 0
    if revision_path.exists():
        cached = read_json(revision_path)
        if cached.get('base_key') == base_key:
            script, attempt = cached['script'], cached['attempt']
            if attempt not in (1, 2):
                raise ValueError('Invalid cached editorial repair attempt')
    while True:
        write_json(job / 'script.json', script)
        manifest, mix, qa, visuals = production_round(job, script, research, allow_approved=attempt == 0)
        write_json(job / 'deliverables' / f'qa-attempt-{attempt:02d}.json', qa)
        if qa.get('pass'):
            update(job, 'qa', 'complete', 'Đã qua kiểm tra nội dung và cấu trúc')
            return script, manifest, mix
        issues = qa.get('issues', [])
        if attempt >= 2:
            raise RuntimeError('Editorial QA failed after 2 automatic repairs: ' + '; '.join(issues))
        attempt += 1
        update(job, 'script', detail=f'Tự sửa lỗi biên tập {attempt}/2: ' + '; '.join(issues)[:300])
        repaired = invoke(job, f'script-repair-{attempt:02d}', {
            'original_script': original_script, 'script': script, 'research': research,
            'issues': issues, 'qa_summary': qa.get('summary', ''),
            'visuals': [{'id': s['id'], 'beats': [{'description': b['description'], 'cue_word': b.get('cue_word', '')}
                                                for b in s['beats']]} for s in visuals['scenes']],
        }, SCRIPT)
        if [s['id'] for s in repaired.get('scenes', [])] != [s['id'] for s in script['scenes']]:
            raise RuntimeError('Editorial repair changed scene IDs or order')
        if any(not s.get('narration', '').strip() or not s.get('visual_brief', '').strip() for s in repaired['scenes']):
            raise RuntimeError('Editorial repair produced an empty narration or visual brief')
        meaningful = any(old['narration'] != new['narration'] or old['visual_brief'] != new['visual_brief']
                         for old, new in zip(script['scenes'], repaired['scenes']))
        if not meaningful:
            raise RuntimeError('Editorial repair made no meaningful narration or visual change: ' + '; '.join(issues))
        # Preserve metadata to avoid invalidating every visual batch for a title edit.
        repaired['title'] = script['title']
        script = repaired
        write_json(revision_path, {'base_key': base_key, 'attempt': attempt, 'script': script,
                                   'issues_addressed': issues, 'mode': 'automatic-editorial-repair'})
        update(job, 'script', 'complete', f'Đã sửa lỗi biên tập lần {attempt}; kiểm tra lại')


def production_round(job, script, research, allow_approved):
    update(job, 'visuals', detail='Vẽ nhiều lớp minh họa và dựng nhịp chuyển cảnh')
    visuals = approved(job, 'visuals') if allow_approved else None
    if visuals is None:
        visuals = generate_visuals(job, script)
    beat_count = validate_visuals(visuals, script)
    write_json(job / 'visuals.json', visuals)
    update(job, 'visuals', 'complete', f'{beat_count} bố cục minh họa nhiều lớp')

    update(job, 'voice', detail='Tạo giọng tiếng Anh và lấy thời điểm từng từ')
    voices = asyncio.run(synthesize(job, script))
    manifest = build_project(job, script, visuals, voices)
    update(job, 'voice', 'complete', f'{manifest["frames"] / manifest["fps"]:.1f} giây, chuyển cảnh khớp lời')

    update(job, 'sound', detail='Phối nhạc vui từ thư viện và hiệu ứng theo nhịp')
    sound(job, manifest)
    mix = job / 'deliverables/full-mix.mp3'
    if not mix.is_file() or mix.stat().st_size == 0:
        raise RuntimeError('Sound stage produced no full mix')
    update(job, 'sound', 'complete', 'Đã phối giọng, nhạc nền và hiệu ứng')

    update(job, 'qa', detail='Kiểm tra độc lập nội dung, hình ảnh và đồng bộ')
    qa = invoke(job, 'qa', {
        'research': research, 'script': script,
        'visuals': [{'id': s['id'], 'beats': [{'description': b['description'], 'cue_word': b.get('cue_word', '')} for b in s['beats']]} for s in visuals['scenes']],
    }, QA)
    validate_visuals(visuals, script)
    durations = [b['frames'] / manifest['fps'] for s in manifest['scenes'] for b in s['beats']]
    qa['deterministic'] = {'visual_beats': beat_count, 'no_subtitles': manifest['subtitles'] is False,
                           'no_text_cards': manifest.get('textCards',False) is False,
                           'longest_visual_seconds': round(max(durations), 2),
                           'audio_present': mix.exists()}
    if max(durations) > 9:
        long_scenes=[s['id'] for s in manifest['scenes'] if any(b['frames']/manifest['fps']>9 for b in s['beats'])]
        qa['pass']=False
        qa.setdefault('issues',[]).append('Visual pacing: '+', '.join(long_scenes)+' holds a composition over 9 seconds. Revise their visual briefs to require more distinct beats, or split/shorten the narration without changing facts.')
    write_json(job / 'deliverables/qa.json', qa)
    return manifest, mix, qa, visuals
