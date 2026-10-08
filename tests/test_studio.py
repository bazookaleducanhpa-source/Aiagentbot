import base64
import json
import os
import subprocess
import tempfile
import unittest
import uuid
import zipfile
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch, Mock

# Keep tests isolated and guarantee that no paid providers are called.
TEMP = tempfile.TemporaryDirectory(prefix='dreamforge-tests-')
os.environ['DATA_DIR'] = TEMP.name
os.environ['APP_MODE'] = 'demo'

from fastapi.testclient import TestClient
from app import store, pipeline, providers, media
from app.main import app
from app.models import Campaign, SourceInput
from app.config import ARTIFACTS

class StudioTests(unittest.TestCase):
    def setUp(self):
        store.init()
        with store.db() as c:
            for table in ('jobs','events','publications','sources','observations','skills'):
                c.execute('DELETE FROM ' + table)
        self.client = TestClient(app)
        self.submit_patch = patch.object(pipeline.executor, 'submit')
        self.submit = self.submit_patch.start()

    def tearDown(self):
        self.submit_patch.stop()
        self.client.close()

    def create(self, **extra):
        r = self.client.post('/api/jobs', json={'topic': 'A tiny robot discovers a forest of stars', 'duration': 15, **extra})
        self.assertEqual(r.status_code, 201, r.text)
        return r.json()

    def ready(self):
        j = self.create()
        script = pipeline.demo_script(j)
        store.update(j['id'], script=script, research={'sources':[], 'summary':'Demo only'}, status='review', artifacts={
            'video': f"/artifacts/{j['id']}/video.mp4", 'kit': f"/artifacts/{j['id']}/publish-kit.zip"})
        return store.job(j['id'])

    def approve(self, j):
        r = self.client.post(f"/api/jobs/{j['id']}/approve")
        self.assertEqual(r.status_code, 200, r.text)

    def test_demo_renders_real_mp4_and_publish_kit(self):
        j = self.create()
        with patch.object(providers, 'request', side_effect=AssertionError('No network in demo')):
            pipeline.run(j['id'])
        finished = store.job(j['id'])
        self.assertEqual(finished['status'], 'review', finished['error'])
        self.assertEqual(finished['artifacts']['voice'], 'silent-demo')
        folder = ARTIFACTS / j['id']
        self.assertGreater((folder / 'video.mp4').stat().st_size, 10000)
        probe = subprocess.run([media.ffmpeg_path(), '-i', str(folder / 'video.mp4'), '-f', 'null', '-'], capture_output=True, timeout=60)
        self.assertEqual(probe.returncode, 0, probe.stderr[-2000:])
        self.assertIn(b'720x1280', probe.stderr)
        with zipfile.ZipFile(folder / 'publish-kit.zip') as z:
            self.assertIn('caption.txt', z.namelist())
            self.assertIn('SAMPLE CONTENT', z.read('caption.txt').decode())
        self.assertIn('-->', (folder / 'captions.srt').read_text())
        self.assertEqual(self.client.get(f"/artifacts/{j['id']}/video.mp4").status_code, 200)

    def test_approval_gate_and_duplicate_post(self):
        j = self.ready()
        url = f"/api/jobs/{j['id']}/publish"
        self.assertEqual(self.client.post(url, json={'platform':'youtube'}).status_code, 409)
        self.approve(j)
        self.assertEqual(self.client.post(url, json={'platform':'youtube'}).status_code, 201)
        with patch.object(providers, 'youtube_upload', side_effect=AssertionError('No demo upload')):
            pipeline.dispatch_publications()
        self.assertEqual(store.job(j['id'])['publications'][0]['status'], 'simulated')
        self.assertEqual(self.client.post(url, json={'platform':'youtube'}).status_code, 409)

    def test_tiktok_is_manual_and_never_claims_published(self):
        j = self.ready(); self.approve(j)
        self.client.post(f"/api/jobs/{j['id']}/publish", json={'platform':'tiktok'})
        pipeline.dispatch_publications()
        p = store.job(j['id'])['publications'][0]
        self.assertEqual(p['status'], 'manual')
        self.assertIn('kit', p['result'])

    def test_edit_revokes_approval_and_cancels_pending_upload(self):
        j = self.ready(); self.approve(j)
        self.client.post(f"/api/jobs/{j['id']}/publish", json={'platform':'youtube','scheduled_at':(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat()})
        edited = dict(j['script'], title='A new original English title')
        self.assertEqual(self.client.put(f"/api/jobs/{j['id']}/script", json=edited).status_code, 200)
        current = store.job(j['id'])
        self.assertEqual(current['approved'], 0)
        self.assertIsNone(current['artifacts'])
        self.assertEqual(current['publications'][0]['status'], 'cancelled')
        self.assertEqual(self.client.post(f"/api/jobs/{j['id']}/approve").status_code, 409)

    def test_future_schedule_waits_and_can_be_cancelled(self):
        j = self.ready(); self.approve(j)
        self.client.post(f"/api/jobs/{j['id']}/publish", json={'platform':'youtube','scheduled_at':(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat()})
        pipeline.dispatch_publications()
        p = store.job(j['id'])['publications'][0]
        self.assertEqual(p['status'], 'queued')
        self.assertEqual(self.client.post(f"/api/publications/{p['id']}/cancel").status_code, 200)
        self.assertEqual(store.job(j['id'])['publications'][0]['status'], 'cancelled')

    def test_recovery_does_not_retry_interrupted_upload(self):
        j = self.ready(); self.approve(j)
        self.client.post(f"/api/jobs/{j['id']}/publish", json={'platform':'youtube'})
        with store.db() as c:
            c.execute("UPDATE publications SET status='sending'")
            c.execute("UPDATE jobs SET status='producing'")
        store.init()
        current = store.job(j['id'])
        self.assertEqual(current['status'], 'failed')
        self.assertEqual(current['publications'][0]['status'], 'unknown')
        self.assertEqual(self.client.post(f"/api/jobs/{j['id']}/retry").status_code, 409)

    def test_inputs_origin_and_secret_protection(self):
        self.assertEqual(self.client.post('/api/jobs', json={'topic':'ok'}).status_code, 422)
        self.assertEqual(self.client.post('/api/jobs', json={'topic':'hello'}, headers={'Origin':'https://evil.example'}).status_code, 403)
        self.assertEqual(self.client.get('/api/settings', headers={'Host':'evil.example'}).status_code, 403)
        with patch.dict(os.environ, {'OPENAI_API_KEY':'secret-never-expose'}):
            self.assertNotIn('secret-never-expose', self.client.get('/api/settings').text)
        self.assertEqual(self.client.get('/artifacts/'+'a'*32+'/.env').status_code, 404)
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.get('/static/app.js').status_code, 200)

    def test_sources_validation_and_upsert(self):
        value={'platform':'tiktok','url':'https://www.tiktok.com/@test/video/123','title':'An original tiny world','views':100,'published_at':store.now()}
        self.assertEqual(self.client.post('/api/sources',json=value).status_code,201)
        value['views']=200
        self.client.post('/api/sources',json=value)
        rows=self.client.get('/api/sources').json()
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['views'],200)
        value['url']='https://tiktok.com.evil.example/x'
        self.assertEqual(self.client.post('/api/sources',json=value).status_code,422)

    def test_live_content_uses_skills_and_feedback_in_english(self):
        j = self.ready()
        store.update(j['id'], feedback={'views':2000,'retention':72,'note':'Keep the opening short.'})
        j['mode']='live'
        with store.db() as c:
            c.execute("UPDATE jobs SET mode='live' WHERE id=?",(j['id'],))
        with patch.object(providers,'generate_json',return_value=j['script']) as mocked:
            value=pipeline.write(j)
        self.assertEqual(value,j['script'])
        model,instructions,payload=mocked.call_args.args
        self.assertIn('English',instructions)
        self.assertEqual(payload['recent_performance'][0]['feedback']['retention'],72)

    def test_demo_feedback_does_not_influence_live_scripts(self):
        j=self.ready()
        store.update(j['id'],feedback={'views':999999,'retention':100,'note':'Demo sample only'})
        self.assertEqual(pipeline.feedback_context(),[])

    def test_skill_edits_are_persistent_and_workflow_is_read_only(self):
        body='Write original English stories with a surprising final scene.'
        self.assertEqual(self.client.put('/api/skills/content',json={'body':body}).status_code,200)
        self.assertEqual(pipeline.skill('content'),body)
        self.assertEqual(self.client.put('/api/skills/publisher',json={'body':body}).status_code,422)

    def test_provider_json_contract_and_safe_error(self):
        response=Mock(is_error=False)
        response.json.return_value={'output':[{'content':[{'type':'output_text','text':'{"summary":"Original angle","angles":["Tiny worlds"]}'}]}]}
        with patch.dict(os.environ,{'OPENAI_API_KEY':'test-key'}), patch.object(providers,'request',return_value=response) as mocked:
            value=providers.generate_json('gpt-6-luna','English output',{'topic':'Tiny world'})
            self.assertEqual(value['angles'],['Tiny worlds'])
            self.assertEqual(mocked.call_args.kwargs['json']['text']['format']['type'],'json_object')
        import httpx
        with patch.object(httpx,'request',return_value=httpx.Response(401,text='secret-never-expose')):
            with self.assertRaises(providers.ProviderError) as error:
                providers.request('GET','https://example.com')
            self.assertNotIn('secret-never-expose',str(error.exception))

    def test_image_request_and_decoding(self):
        from io import BytesIO
        from PIL import Image
        buffer=BytesIO();Image.new('RGB',(16,16)).save(buffer,format='PNG')
        response=Mock();response.json.return_value={'data':[{'b64_json':base64.b64encode(buffer.getvalue()).decode()}]}
        output=ARTIFACTS/'image-test.png'
        with patch.dict(os.environ,{'OPENAI_API_KEY':'test-key'}),patch.object(providers,'request',return_value=response) as mocked:
            providers.image('A tiny silver robot',output)
            self.assertEqual(mocked.call_args.kwargs['json']['size'],'1024x1536')
        self.assertTrue(output.is_file())

    def test_growth_uses_separate_observations(self):
        source={'url':'https://www.youtube.com/watch?v=example','views':300,'published_at':(datetime.now(timezone.utc)-timedelta(hours=10)).isoformat()}
        with store.db() as c:
            c.execute('INSERT INTO observations VALUES(?,?,?)',(source['url'],100,(datetime.now(timezone.utc)-timedelta(hours=2)).isoformat()))
        result=providers.score_sources([source])[0]
        self.assertAlmostEqual(result['growth_per_hour'],100,delta=1)
        self.assertAlmostEqual(result['views_per_hour'],30,delta=1)

    def test_youtube_adapter_refreshes_token_and_declares_ai(self):
        j=self.ready()
        j['script']['made_for_kids']=True
        video=ARTIFACTS/'adapter-video.mp4';video.write_bytes(b'example-video-bytes')
        token=Mock();token.json.return_value={'access_token':'temporary-access-token'}
        init=Mock();init.headers={'Location':'https://www.googleapis.com/upload/youtube/v3/videos?upload_id=example'}
        final=Mock();final.json.return_value={'id':'example-id','status':{'privacyStatus':'private'}}
        credentials={'YOUTUBE_CLIENT_ID':'client','YOUTUBE_CLIENT_SECRET':'secret','YOUTUBE_REFRESH_TOKEN':'refresh'}
        with patch.dict(os.environ,credentials),patch.object(providers,'request',side_effect=[token,init,final]) as mocked:
            result=providers.youtube_upload(video,j['script'],'private')
        self.assertEqual(result['video_id'],'example-id')
        self.assertTrue(mocked.call_args_list[1].kwargs['json']['status']['containsSyntheticMedia'])
        self.assertTrue(mocked.call_args_list[1].kwargs['json']['status']['selfDeclaredMadeForKids'])
        self.assertEqual(mocked.call_args_list[1].kwargs['json']['snippet']['categoryId'],'24')
        self.assertIn('AI-generated',mocked.call_args_list[1].kwargs['json']['snippet']['description'])
        self.assertEqual(mocked.call_args_list[2].args[0],'PUT')

    def test_ambiguous_live_upload_stops_and_cannot_duplicate(self):
        j=self.ready();self.approve(j)
        with store.db() as c:
            c.execute("UPDATE jobs SET mode='live' WHERE id=?",(j['id'],))
            c.execute("INSERT INTO publications(job_id,platform,status,scheduled_at,privacy,created_at) VALUES(?, 'youtube', 'queued', ?, 'private', ?)",(j['id'],store.now(),store.now()))
        with patch.object(providers,'youtube_upload',side_effect=providers.ProviderError('Network failure')) as mocked:
            pipeline.dispatch_publications();pipeline.dispatch_publications()
            self.assertEqual(mocked.call_count,1)
        current=store.job(j['id'])
        self.assertEqual(current['publications'][0]['status'],'unknown')
        self.assertEqual(self.client.put(f"/api/jobs/{j['id']}/script",json=j['script']).status_code,409)

    def test_live_mode_needs_key_and_queue_is_bounded(self):
        with patch.dict(os.environ,{'APP_MODE':'live','OPENAI_API_KEY':''}):
            r=self.client.post('/api/jobs',json={'topic':'A tiny surreal world'})
            self.assertEqual(r.status_code,400)
        for _ in range(4):
            self.create()
        self.assertEqual(self.client.post('/api/jobs',json={'topic':'A fifth story'}).status_code,429)

    def test_buffer_demo_never_calls_external_providers(self):
        j=self.ready();self.approve(j)
        r=self.client.post(f"/api/jobs/{j['id']}/publish",json={'platform':'tiktok','tiktok_mode':'buffer','privacy':'public'})
        self.assertEqual(r.status_code,201)
        with patch.object(providers,'buffer_tiktok_publish',side_effect=AssertionError('No real demo post')):
            pipeline.dispatch_publications()
        p=store.job(j['id'])['publications'][0]
        self.assertEqual(p['provider'],'buffer');self.assertEqual(p['status'],'simulated')

    def test_live_buffer_requires_public_consent_and_credentials(self):
        j=self.ready();self.approve(j)
        with store.db() as c:
            c.execute("UPDATE jobs SET mode='live' WHERE id=?",(j['id'],))
        r=self.client.post(f"/api/jobs/{j['id']}/publish",json={'platform':'tiktok','tiktok_mode':'buffer','privacy':'private'})
        self.assertEqual(r.status_code,400)
        with patch.dict(os.environ,{k:'test-credential' for k in providers.BUFFER_KEYS}):
            r=self.client.post(f"/api/jobs/{j['id']}/publish",json={'platform':'tiktok','tiktok_mode':'buffer','privacy':'public'})
        self.assertEqual(r.status_code,201)
        with patch.object(providers,'buffer_tiktok_publish',return_value={'provider':'buffer','post_id':'test-post','remote_status':'buffer'}):
            pipeline.dispatch_publications()
        p=store.job(j['id'])['publications'][0]
        self.assertEqual(p['status'],'submitted')
        self.assertEqual(self.client.put(f"/api/jobs/{j['id']}/script",json=j['script']).status_code,409)
        with patch.object(providers,'buffer_post_status',return_value='sent'):
            r=self.client.post(f"/api/publications/{p['id']}/sync")
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json()['status'],'published')

    def test_buffer_adapter_uses_variables_and_ai_disclosure(self):
        j=self.ready()
        channel={'id':'tiktok-id','service':'tiktok','isQueuePaused':False}
        with patch.dict(os.environ,{**{k:'test-credential' for k in providers.BUFFER_KEYS},'BUFFER_TIKTOK_CHANNEL_ID':'tiktok-id'}), \
             patch.object(providers,'buffer_channels',return_value=[channel]), \
             patch.object(providers,'cloudinary_upload',return_value='https://res.cloudinary.com/demo/video/upload/story.mp4'), \
             patch.object(providers,'buffer_graphql',return_value={'createPost':{'__typename':'PostActionSuccess','post':{'id':'post123','status':'buffer'}}}) as mocked:
            result=providers.buffer_tiktok_publish(ARTIFACTS/'unused.mp4',j,store.now())
        payload=mocked.call_args.args[1]['input']
        self.assertEqual(payload['channelId'],'tiktok-id')
        self.assertTrue(payload['metadata']['tiktok']['isAiGenerated'])
        self.assertEqual(payload['mode'],'customScheduled')
        self.assertEqual(result['post_id'],'post123')
        self.assertGreater(datetime.fromisoformat(payload['dueAt']),datetime.now(timezone.utc))

    def test_cloudinary_upload_is_signed_and_secrets_are_not_returned(self):
        video=ARTIFACTS/'cloudinary-test.mp4';video.write_bytes(b'video')
        response=Mock();response.json.return_value={'secure_url':'https://res.cloudinary.com/demo/video/upload/test.mp4'}
        with patch.dict(os.environ,{'CLOUDINARY_CLOUD_NAME':'demo','CLOUDINARY_API_KEY':'key','CLOUDINARY_API_SECRET':'private-secret'}), \
             patch.object(providers,'request',return_value=response) as mocked:
            url=providers.cloudinary_upload(video,'a'*32)
        payload=mocked.call_args.kwargs['data']
        self.assertEqual(len(payload['signature']),64)
        self.assertNotIn('private-secret',str(payload))
        self.assertEqual(payload['overwrite'],'false')
        self.assertTrue(url.startswith('https://res.cloudinary.com'))

    def test_tiktok_research_normalizes_metadata_and_limits_actor_cost(self):
        response=Mock();response.json.return_value=[{'webVideoUrl':'https://www.tiktok.com/@creator/video/123','text':'A surreal tiny world','playCount':4200,'createTimeISO':store.now()}, {'error':'unavailable'}]
        with patch.dict(os.environ,{'APIFY_API_TOKEN':'secret-token','APIFY_MAX_CHARGE_USD':'0.5'}),patch.object(providers,'request',return_value=response) as mocked:
            values=providers.tiktok_search('AI fantasy story')
        self.assertEqual(len(values),1)
        self.assertEqual(values[0]['views'],4200)
        self.assertFalse(mocked.call_args.kwargs['json']['shouldDownloadVideos'])
        self.assertEqual(mocked.call_args.kwargs['params']['maxTotalChargeUsd'],.5)
        self.assertNotIn('secret-token',mocked.call_args.args[1])

    def test_youtube_helper_saves_token_locally(self):
        from scripts.connect_youtube import save_credentials
        path=Path(TEMP.name)/'oauth-test.env'
        credentials=Mock(refresh_token='refresh-test',client_id='client-test',client_secret='secret-test')
        save_credentials(credentials,path)
        from dotenv import dotenv_values
        saved=dotenv_values(path)
        self.assertEqual(saved['YOUTUBE_REFRESH_TOKEN'],'refresh-test')
        self.assertEqual(saved['YOUTUBE_CLIENT_ID'],'client-test')

    def test_connection_settings_never_expose_new_secrets(self):
        secrets={k:'do-not-expose-this' for k in (*providers.BUFFER_KEYS,'APIFY_API_TOKEN')}
        with patch.dict(os.environ,secrets):
            r=self.client.get('/api/settings')
        self.assertNotIn('do-not-expose-this',r.text)
        self.assertTrue(r.json()['connections']['tiktok'])
        self.assertEqual(self.client.get('/setup-guide').status_code,200)

if __name__=='__main__':
    unittest.main()
