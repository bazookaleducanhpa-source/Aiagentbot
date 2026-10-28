"""Offline API contracts. Never submit a real remake or modify live jobs."""
import sys
import copy
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from remake_studio import common, server
from remake_studio.source import video_id
from remake_studio import pipeline


class SourceURLTests(unittest.TestCase):
    def test_supported_youtube_links(self):
        for url in (
            'https://www.youtube.com/watch?v=0NY2gAftzJE&t=12',
            'https://youtube.com/watch?v=0NY2gAftzJE',
            'https://m.youtube.com/watch?v=0NY2gAftzJE',
            'https://youtu.be/0NY2gAftzJE?si=abc',
            'https://www.youtube.com/shorts/0NY2gAftzJE',
            'https://www.youtube.com/embed/0NY2gAftzJE',
        ):
            with self.subTest(url=url):
                self.assertEqual(video_id(url), '0NY2gAftzJE')

    def test_rejects_untrusted_or_invalid_links(self):
        for url in (
            'https://user:password@youtube.com/watch?v=0NY2gAftzJE',
            'https://user@youtu.be/0NY2gAftzJE',
            'https://youtube.com.evil.example/watch?v=0NY2gAftzJE',
            'https://evil.example/youtube.com/watch?v=0NY2gAftzJE',
            'http://127.0.0.1/watch?v=0NY2gAftzJE',
            'file:///etc/passwd',
            'javascript:alert(1)',
            'https://youtube.com/watch?v=short',
            'https://youtube.com/watch?v=0NY2gAftzJEextra',
            'https://youtube.com/watch?v=0NY2gAftzJ!',
            'https://youtube.com/watch',
            'https://youtu.be/',
            'https://youtube.com/shorts/',
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                video_id(url)


class StudioAPITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.jobs = Path(self.temp.name)
        for target in (server, common):
            p = patch.object(target, 'JOBS', self.jobs)
            p.start()
            self.addCleanup(p.stop)
        p = patch.object(server, 'pending', set())
        p.start()
        self.addCleanup(p.stop)
        p = patch.object(server, 'submit')
        self.submit = p.start()
        self.addCleanup(p.stop)
        # Explicit recover test controls startup; ordinary tests isolate each request.
        self.client = TestClient(server.app)
        self.addCleanup(self.client.close)

    def seed(self, status='failed', jid='abcdef123456'):
        folder = self.jobs / jid
        common.write_json(folder / 'job.json', {
            'id': jid, 'url': 'https://www.youtube.com/watch?v=0NY2gAftzJE',
            'title': 'Test source', 'status': status, 'stage': 'source',
            'progress': 0, 'created_at': '2026-10-25T00:00:00Z',
            'error': 'Previous failure' if status == 'failed' else None,
            'stages': [{'id': k, 'label': label, 'status': 'pending', 'detail': ''}
                       for k, label in common.STAGES],
        })
        return folder

    def test_create_is_queued_and_has_no_fabricated_output(self):
        response = self.client.post('/api/jobs', json={
            'url': 'https://youtu.be/0NY2gAftzJE?t=3', 'language': 'en',
            'notes': 'More illustration; no subtitles',
        })
        self.assertEqual(response.status_code, 200, response.text)
        job = response.json()
        self.assertEqual(job['url'], 'https://www.youtube.com/watch?v=0NY2gAftzJE')
        self.assertEqual(job['status'], 'queued')
        self.assertEqual(job['progress'], 0)
        self.assertEqual(job['notes'], 'More illustration; no subtitles')
        self.assertTrue(all(s['status'] == 'pending' for s in job['stages']))
        for field in ('video_url', 'preview_url', 'audio_url'):
            self.assertIsNone(job[field])
        self.submit.assert_called_once_with(self.jobs / job['id'])
        self.assertEqual(self.client.get('/api/jobs/' + job['id']).json(), job)
        self.assertEqual(self.client.get('/api/jobs').json()['jobs'], [job])

    def test_invalid_input_never_creates_or_submits(self):
        for body in ({'url': 'https://example.com/foo'},
                     {'url': 'https://youtu.be/0NY2gAftzJE', 'language': 'vi'},
                     {'url': 'https://youtu.be/0NY2gAftzJE', 'notes': 'x' * 6001}):
            self.assertEqual(self.client.post('/api/jobs', json=body).status_code, 422)
        self.submit.assert_not_called()
        self.assertEqual(list(self.jobs.iterdir()), [])

    def test_retry_only_failed_or_interrupted(self):
        for status in ('failed', 'interrupted', 'running', 'queued', 'complete'):
            with self.subTest(status=status):
                folder = self.seed(status)
                self.submit.reset_mock()
                response = self.client.post('/api/jobs/' + folder.name + '/retry')
                if status in ('failed', 'interrupted'):
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.json()['status'], 'queued')
                    self.assertIsNone(response.json()['error'])
                    self.submit.assert_called_once_with(folder)
                else:
                    self.assertEqual(response.status_code, 409)
                    self.submit.assert_not_called()

    def test_foreign_origin_cannot_mutate(self):
        body = {'url': 'https://youtu.be/0NY2gAftzJE'}
        for origin in ('https://evil.example', 'http://localhost:9999', 'null'):
            response = self.client.post('/api/jobs', json=body, headers={'Origin': origin})
            self.assertEqual(response.status_code, 403)
        self.submit.assert_not_called()
        for origin in ('http://localhost:8010', 'http://127.0.0.1:8010'):
            self.assertEqual(self.client.post('/api/jobs', json=body,
                                             headers={'Origin': origin}).status_code, 200)

    def test_artifact_allowlist_and_missing_outputs(self):
        folder = self.seed('complete')
        base = '/api/jobs/' + folder.name
        self.assertIsNone(self.client.get(base).json()['video_url'])
        self.assertEqual(self.client.get(base + '/files/final.mp4').status_code, 404)
        deliverables = folder / 'deliverables'
        deliverables.mkdir()
        (deliverables / 'final.mp4').write_bytes(b'test-video-bytes')
        (deliverables / 'secret.txt').write_text('private')
        response = self.client.get(base + '/files/final.mp4')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'test-video-bytes')
        self.assertEqual(response.headers['content-type'], 'video/mp4')
        self.assertEqual(self.client.get(base).json()['video_url'], base + '/files/final.mp4')
        for name in ('secret.txt', 'job.json', '..%2Fjob.json', '%2E%2E%2Fjob.json',
                     '..%5Cjob.json', '%252e%252e%252fjob.json'):
            with self.subTest(name=name):
                self.assertEqual(self.client.get(base + '/files/' + name).status_code, 404)
        self.assertEqual(self.client.get('/api/jobs/not-a-job').status_code, 404)

    def test_startup_marks_only_inflight_jobs_interrupted(self):
        states = ('queued', 'running', 'failed', 'complete', 'interrupted')
        folders = [self.seed(state, f'{i:012x}') for i, state in enumerate(states)]
        server.recover()
        for folder, before in zip(folders, states):
            data = common.read_json(folder / 'job.json')
            self.assertEqual(data['status'], 'interrupted' if before in ('queued', 'running') else before)
            if before in ('queued', 'running'):
                self.assertTrue(data['error'])
        self.submit.assert_not_called()

    def test_startup_preserves_live_cli_job_and_retry_does_not_mutate_it(self):
        folder = self.seed('running')
        before = (folder / 'job.json').read_bytes()
        with pipeline.job_lock(folder):
            server.recover()
            response = self.client.post('/api/jobs/' + folder.name + '/retry')
            self.assertEqual(response.status_code, 409)
            self.assertEqual((folder / 'job.json').read_bytes(), before)
        self.submit.assert_not_called()

    def test_execution_failure_is_visible_and_releases_pending(self):
        folder = self.seed('running')
        data = common.read_json(folder / 'job.json')
        data['stages'][0]['status'] = 'running'
        common.write_json(folder / 'job.json', data)
        fake_pipeline = types.ModuleType('remake_studio.pipeline')
        def fail(_):
            raise RuntimeError('Offline execution failure')
        fake_pipeline.execute = fail
        with patch.dict(sys.modules, {'remake_studio.pipeline': fake_pipeline}), \
                patch.object(server.pool, 'submit', side_effect=lambda fn: fn()):
            # Bypass only our submit mock, preserving the production function.
            ORIGINAL_SUBMIT(folder)
        result = self.client.get('/api/jobs/' + folder.name).json()
        self.assertEqual(result['status'], 'failed')
        self.assertIn('Offline execution failure', result['error'])
        self.assertEqual(result['stages'][0]['status'], 'failed')
        self.assertIsNone(result['video_url'])
        self.assertNotIn(folder.name, server.pending)


ORIGINAL_SUBMIT = server.submit


class PipelineReliabilityTests(unittest.TestCase):
    def test_editorial_failure_repairs_and_retry_resumes_without_approved_visuals(self):
        original = {'title': 'Test', 'summary': 'Summary', 'scenes': [
            {'id': 's001', 'narration': 'An uncertain finding.', 'visual_brief': 'Wrong depiction.', 'mood': 'calm'}]}
        repaired = copy.deepcopy(original)
        repaired['scenes'][0]['visual_brief'] = 'Correct depiction with uncertainty.'
        visuals = {'scenes': [{'id': 's001', 'beats': [{'description': 'Wrong depiction', 'cue_word': 'finding'}]}]}
        failed = {'pass': False, 'issues': ['Fix the visual depiction.'], 'summary': 'One factual visual error'}
        passed = {'pass': True, 'issues': [], 'summary': 'Correct'}
        research = {'summary': 'Verified source'}
        with tempfile.TemporaryDirectory() as directory:
            job = Path(directory)
            common.write_json(job / 'approved-script.json', original)
            common.write_json(job / 'approved-visuals.json', visuals)
            original_bytes = (job / 'approved-script.json').read_bytes()
            with patch.object(pipeline, 'production_round', side_effect=[({}, job/'mix', failed, visuals), ({}, job/'mix', passed, visuals)]) as produce, \
                    patch.object(pipeline, 'invoke', return_value=repaired) as invoke, patch.object(pipeline, 'update'):
                result, _, _ = pipeline.editorial_production(job, original, research)
                self.assertEqual(result, repaired)
                self.assertTrue(produce.call_args_list[0].kwargs['allow_approved'])
                self.assertFalse(produce.call_args_list[1].kwargs['allow_approved'])
                self.assertEqual(invoke.call_args.args[1], 'script-repair-01')
                self.assertEqual(invoke.call_args.args[2]['issues'], failed['issues'])
            self.assertEqual((job/'approved-script.json').read_bytes(), original_bytes)
            self.assertEqual(common.read_json(job/'script-revision.json')['attempt'], 1)
            with patch.object(pipeline, 'production_round', return_value=({}, job/'mix', passed, visuals)) as produce, \
                    patch.object(pipeline, 'invoke') as invoke, patch.object(pipeline, 'update'):
                pipeline.editorial_production(job, original, research)
                invoke.assert_not_called()
                self.assertFalse(produce.call_args.kwargs['allow_approved'])
                self.assertEqual(produce.call_args.args[1], repaired)
            # Changing verified research invalidates the saved revision.
            with patch.object(pipeline, 'production_round', return_value=({}, job/'mix', passed, visuals)) as produce, patch.object(pipeline, 'update'):
                pipeline.editorial_production(job, original, {'summary': 'New evidence'})
                self.assertTrue(produce.call_args.kwargs['allow_approved'])
                self.assertEqual(produce.call_args.args[1], original)

    def test_editorial_repairs_are_bounded_and_noop_is_rejected(self):
        original = {'title': 'Test', 'scenes': [{'id': 's001', 'narration': 'Original.', 'visual_brief': 'Original depiction.'}]}
        revisions = [copy.deepcopy(original), copy.deepcopy(original)]
        for i, revision in enumerate(revisions):
            revision['scenes'][0]['visual_brief'] = f'Revision {i} depiction.'
        failed = {'pass': False, 'issues': ['Still incorrect'], 'summary': 'Failed'}
        visuals = {'scenes': []}
        with tempfile.TemporaryDirectory() as directory:
            job = Path(directory)
            with patch.object(pipeline, 'production_round', return_value=({}, job/'mix', failed, visuals)) as produce, \
                    patch.object(pipeline, 'invoke', side_effect=revisions) as invoke, patch.object(pipeline, 'update'):
                with self.assertRaisesRegex(RuntimeError, 'after 2 automatic repairs'):
                    pipeline.editorial_production(job, original, {})
                self.assertEqual(produce.call_count, 3)
                self.assertEqual(invoke.call_count, 2)
        with tempfile.TemporaryDirectory() as directory:
            job = Path(directory)
            with patch.object(pipeline, 'production_round', return_value=({}, job/'mix', failed, visuals)), \
                    patch.object(pipeline, 'invoke', return_value=original), patch.object(pipeline, 'update'):
                with self.assertRaisesRegex(RuntimeError, 'no meaningful'):
                    pipeline.editorial_production(job, original, {})

    def test_lock_rejects_duplicate_and_releases_after_exception(self):
        with tempfile.TemporaryDirectory() as directory:
            job = Path(directory)
            with self.assertRaisesRegex(ValueError, 'intentional'):
                with pipeline.job_lock(job):
                    self.assertTrue(pipeline.is_job_running(job))
                    with self.assertRaises(pipeline.JobAlreadyRunning):
                        with pipeline.job_lock(job):
                            self.fail('Duplicate execution acquired the lock')
                    raise ValueError('intentional')
            self.assertFalse(pipeline.is_job_running(job))
            with pipeline.job_lock(job):
                pass

    def test_render_cache_invalidates_on_engine_or_audio_change(self):
        with tempfile.TemporaryDirectory() as directory:
            job = Path(directory)
            src = job / 'project/src'
            src.mkdir(parents=True)
            engine = src / 'Video.tsx'
            engine.write_text('version one')
            mix = job / 'mix.mp3'
            mix.write_bytes(b'audio one')
            manifest = {'frames': 300, 'fps': 30}
            first = pipeline.render_signature(job, manifest, mix)
            self.assertEqual(first, pipeline.render_signature(job, manifest, mix))
            engine.write_text('version two')
            second = pipeline.render_signature(job, manifest, mix)
            self.assertNotEqual(first, second)
            mix.write_bytes(b'audio two')
            self.assertNotEqual(second, pipeline.render_signature(job, manifest, mix))

    def test_duration_check_rejects_truncated_or_invalid_exports(self):
        metadata = {'streams': [{'codec_type': 'audio'}, {'codec_type': 'video'}],
                    'format': {'duration': '10.05'}}
        manifest = {'frames': 300, 'fps': 30}
        pipeline.validate_export(metadata, manifest)
        for duration in ('8', '11', 'nan', '0'):
            metadata['format']['duration'] = duration
            with self.subTest(duration=duration), self.assertRaises(RuntimeError):
                pipeline.validate_export(metadata, manifest)

    def test_artwork_bytes_invalidate_render_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            job = Path(directory)
            artwork = job / 'project/public/art/scene.png'
            artwork.parent.mkdir(parents=True)
            artwork.write_bytes(b'first illustration')
            mix = job / 'mix.mp3'
            mix.write_bytes(b'audio')
            manifest = {'scenes': [{'beats': [{'art': {'file': 'art/scene.png'}}]}]}
            before = pipeline.render_signature(job, manifest, mix)
            artwork.write_bytes(b'revised illustration')
            self.assertNotEqual(before, pipeline.render_signature(job, manifest, mix))

    def test_approved_visuals_preserve_supplied_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            job = Path(directory)
            artifact = {'scenes': [{'id': 's001', 'beats': []}]}
            provenance = {'author': 'human-reviewed bootstrap', 'reference': 'original concept'}
            common.write_json(job / 'approved-visuals.json', {'artifact': artifact, 'provenance': provenance})
            self.assertEqual(pipeline.approved(job, 'visuals'), artifact)
            record = common.read_json(job / 'agents/visuals.provenance.json')
            self.assertEqual(record['provenance'], provenance)
            self.assertEqual(record['mode'], 'supplied-approved-artifact')
            self.assertEqual(len(record['sha256']), 64)

    def test_invalid_batch_gets_exactly_one_repair_with_original_and_error(self):
        initial, repaired = {'bad': True}, {'scenes': []}
        with patch.object(pipeline, 'invoke', side_effect=[initial, repaired]) as invoke, \
                patch.object(pipeline, 'validate_visuals', side_effect=[ValueError('Bad XML'), 2]):
            result = pipeline.visual_batch(Path('.'), 'Test', [{'id': 's001'}], 0)
            self.assertEqual(result, repaired)
            self.assertEqual(invoke.call_count, 2)
            payload = invoke.call_args.args[2]
            self.assertEqual(payload['invalid_result'], initial)
            self.assertEqual(payload['validation_error'], 'Bad XML')
            self.assertEqual(invoke.call_args.args[1], 'visuals-01-repair')
        with patch.object(pipeline, 'invoke', return_value=initial) as invoke, \
                patch.object(pipeline, 'validate_visuals', side_effect=ValueError('Bad XML')):
            with self.assertRaises(ValueError):
                pipeline.visual_batch(Path('.'), 'Test', [{'id': 's001'}], 0)
            self.assertEqual(invoke.call_count, 2)

    def test_failed_batch_does_not_launch_remaining_queue(self):
        script = {'title': 'Test', 'scenes': [{'id': f's{i:03d}'} for i in range(30)]}
        with patch.object(pipeline, 'visual_batch', side_effect=ValueError('invalid')) as batch, \
                patch.object(pipeline, 'update'):
            with self.assertRaises(ValueError):
                pipeline.generate_visuals(Path('.'), script)
            self.assertLessEqual(batch.call_count, 2)

if __name__ == '__main__':
    unittest.main()
