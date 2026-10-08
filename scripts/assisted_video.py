"""Render chat-authored content and local images; publishing is an explicit command."""
import argparse
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import media, pipeline, store
from app.config import ARTIFACTS
from app.models import Campaign, Script, Publication


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='action', required=True)
    build = sub.add_parser('build')
    build.add_argument('--brief', type=Path, required=True)
    build.add_argument('--research', type=Path, required=True)
    build.add_argument('--images', type=Path, nargs='+', required=True)
    publish = sub.add_parser('publish')
    publish.add_argument('--job', required=True)
    args = parser.parse_args()
    if args.action == 'build':
        payload = json.loads(args.brief.read_text(encoding='utf-8-sig'))
        spec = Campaign.model_validate(payload['campaign'])
        script = Script.model_validate(payload['script'])
        research = json.loads(args.research.read_text(encoding='utf-8-sig'))
        research.update(payload.get('research_notes', {}))
        job_id = uuid.uuid4().hex
        with store.db() as c:
            c.execute('INSERT INTO jobs(id,topic,spec,mode,status,created_at) VALUES(?,?,?,?,?,?)',
                      (job_id, spec.topic, spec.model_dump_json(), 'live', 'producing', store.now()))
        store.update(job_id, research=research, script=script.model_dump())
        store.event(job_id, 'research', 'Collected live platform metadata; analysis and script authored in the chat session.')
        print('JOB_ID=' + job_id, flush=True)
        try:
            artifacts = media.render(store.job(job_id),
                lambda message: (print(message, flush=True), store.event(job_id, 'production', message)),
                local_images=args.images)
            store.update(job_id, artifacts=artifacts, status='review')
            store.event(job_id, 'review', 'Video rendered from chat-generated images and Groq narration; ready for inspection.')
            print(json.dumps(artifacts), flush=True)
            print('VIDEO=' + str(ARTIFACTS / job_id / 'video.mp4'), flush=True)
        except Exception:
            store.update(job_id, status='failed', error='Assisted render failed; inspect local execution output.')
            raise
    else:
        from app.main import approve, publish as queue_publication
        job = store.job(args.job)
        if not job or job['status'] not in ('review', 'approved'):
            raise ValueError('A finished video must be inspected before publishing.')
        approve(args.job)
        for platform in job['spec']['platforms']:
            if any(p['platform'] == platform and p['status'] != 'cancelled' for p in job['publications']):
                continue
            queue_publication(args.job, Publication(platform=platform, privacy='public',
                tiktok_mode='buffer' if platform == 'tiktok' else None))
        pipeline.dispatch_publications()
        print(json.dumps(store.job(args.job)['publications']), flush=True)


if __name__ == '__main__':
    main()
