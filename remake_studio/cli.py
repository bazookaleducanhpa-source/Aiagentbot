"""python -m remake_studio.cli URL, --job ID, or --serve."""
import argparse
import uuid
from datetime import datetime, timezone
from .common import JOBS, STAGES, read_json, write_json
from .source import video_id


def main():
    parser = argparse.ArgumentParser(description='Cappy local video remake')
    parser.add_argument('url', nargs='?')
    parser.add_argument('--job', help='Resume an existing 12-character job ID')
    parser.add_argument('--notes', default='')
    parser.add_argument('--serve', action='store_true')
    args = parser.parse_args()
    if args.serve:
        import uvicorn
        uvicorn.run('remake_studio.server:app', host='127.0.0.1', port=8010)
        return
    if args.job:
        import re
        if not re.fullmatch(r'[a-f0-9]{12}', args.job):
            parser.error('Invalid job ID')
        job = JOBS / args.job
        if not (job / 'job.json').is_file():
            parser.error('Job does not exist')
    else:
        if not args.url:
            parser.error('Supply a YouTube URL, --job ID, or --serve')
        vid = video_id(args.url)
        jid = uuid.uuid4().hex[:12]
        job = JOBS / jid
        write_json(job / 'job.json', {
            'id': jid, 'url': 'https://www.youtube.com/watch?v=' + vid,
            'title': vid, 'status': 'queued', 'stage': 'source', 'progress': 0,
            'created_at': datetime.now(timezone.utc).isoformat(), 'error': None,
            'notes': args.notes, 'language': 'en',
            'stages': [{'id': k, 'label': label, 'status': 'pending', 'detail': ''} for k, label in STAGES],
        })
    print('Job:', job.name, flush=True)
    from .pipeline import execute, JobAlreadyRunning
    try:
        execute(job)
    except JobAlreadyRunning as exc:
        parser.exit(2, str(exc) + '\n')
    except Exception as exc:
        data = read_json(job / 'job.json')
        data.update(status='failed', error=str(exc)[:2000])
        for stage in data['stages']:
            if stage['status'] == 'running':
                stage.update(status='failed', detail=str(exc)[:400])
        write_json(job / 'job.json', data)
        raise
    print('Video:', job / 'deliverables/final.mp4', flush=True)


if __name__ == '__main__':
    main()
