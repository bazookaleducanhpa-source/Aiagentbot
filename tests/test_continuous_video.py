"""Motion continuity and source-media cache regression tests; no rendering."""
import copy
import tempfile
import unittest
from pathlib import Path

from remake_studio.production import validate_visuals
from remake_studio.pipeline import render_signature


SCRIPT = {'scenes': [{'id': 'scene-01'}]}


def key(at, x=100, **overrides):
    return {'at': at, 'x': x, 'y': 200, 'scale': 1, 'rotation': 0,
            'opacity': 1, **overrides}


def fixture(animated=True):
    beats = []
    for i in range(2):
        layers = []
        for j in range(2):
            layer = {'svg': f'<circle cx="0" cy="0" r="{30+j}" fill="#aa88cc"/>',
                     'x': 100, 'y': 200, 'delay': 0, 'motion': 'none'}
            if animated:
                layer.update(entity_id=f'cell-{j}',
                             keyframes=[key(0, 100+i*200), key(1, 300+i*200)])
            layers.append(layer)
        beats.append({'id': f'b{i}', 'background': '#e5f1ed', 'layers': layers})
    return {'scenes': [{'id': 'scene-01', 'beats': beats}]}


class ContinuousMotionTests(unittest.TestCase):
    def test_identifying_labels_require_real_targets_and_brief_names(self):
        visuals=fixture()
        label={'text':'Cancer cell','target_entity_id':'cell-0','x':0,'y':-120,'from':.2,'duration':3}
        visuals['scenes'][0]['beats'][0]['labels']=[label]
        self.assertEqual(validate_visuals(visuals,SCRIPT),2)
        for override in ({'target_entity_id':'absent'},{'text':'This is a whole narration sentence'},{'duration':0},{'from':-1},{'x':float('nan')}):
            bad=copy.deepcopy(visuals)
            bad['scenes'][0]['beats'][0]['labels'][0].update(override)
            with self.subTest(override=override),self.assertRaises(ValueError):validate_visuals(bad,SCRIPT)

    def test_continuous_entities_and_legacy_layers_are_accepted(self):
        self.assertEqual(validate_visuals(fixture(), SCRIPT), 2)
        self.assertEqual(validate_visuals(fixture(animated=False), SCRIPT), 2)

    def test_all_keyframe_numbers_must_be_finite(self):
        for field in ('at', 'x', 'y', 'scale', 'rotation', 'opacity'):
            for value in (float('nan'), float('inf'), -float('inf')):
                with self.subTest(field=field, value=value):
                    visuals = fixture()
                    visuals['scenes'][0]['beats'][0]['layers'][0]['keyframes'][0][field] = value
                    with self.assertRaises(ValueError):
                        validate_visuals(visuals, SCRIPT)

    def test_keyframes_require_ordered_zero_to_one_domain(self):
        for times in ((.1, 1), (0, .9), (0, .8, .3, 1), (-.1, 0, 1), (0, 1, 1.1)):
            with self.subTest(times=times):
                visuals = fixture()
                visuals['scenes'][0]['beats'][0]['layers'][0]['keyframes'] = [key(at) for at in times]
                with self.assertRaisesRegex(ValueError, 'order from 0 to 1'):
                    validate_visuals(visuals, SCRIPT)

    def test_scale_and_opacity_stay_in_renderable_range(self):
        for field, value in (('scale', 0), ('scale', -1), ('opacity', -.01), ('opacity', 1.01)):
            with self.subTest(field=field, value=value):
                visuals = fixture()
                visuals['scenes'][0]['beats'][0]['layers'][0]['keyframes'][0][field] = value
                with self.assertRaises(ValueError):
                    validate_visuals(visuals, SCRIPT)

    def test_animated_layers_need_stable_id_and_two_keys(self):
        for mutation in ('missing_id', 'one_key'):
            visuals = fixture()
            layer = visuals['scenes'][0]['beats'][0]['layers'][0]
            if mutation == 'missing_id':
                del layer['entity_id']
            else:
                layer['keyframes'] = [key(0)]
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, 'stable entity IDs'):
                validate_visuals(visuals, SCRIPT)

    def test_persistent_entity_cannot_change_geometry(self):
        visuals = fixture()
        second = visuals['scenes'][0]['beats'][1]['layers'][0]
        second['svg'] = '<ellipse rx="100" ry="10"/>'
        with self.assertRaisesRegex(ValueError, 'retain its geometry'):
            validate_visuals(visuals, SCRIPT)
        second['entity_id'] = 'a-different-object'
        self.assertEqual(validate_visuals(visuals, SCRIPT), 2)

    def test_every_boundary_transform_must_match_previous_end(self):
        for field in ('x', 'y', 'scale', 'rotation', 'opacity'):
            with self.subTest(field=field):
                visuals = fixture()
                start = visuals['scenes'][0]['beats'][1]['layers'][0]['keyframes'][0]
                start[field] += -.2 if field == 'opacity' else .2
                with self.assertRaisesRegex(ValueError, 'jumps at a beat boundary'):
                    validate_visuals(visuals, SCRIPT)
        visuals = fixture()
        visuals['scenes'][0]['beats'][1]['layers'][0]['keyframes'][0]['x'] += .0001
        self.assertEqual(validate_visuals(visuals, SCRIPT), 2)

    def test_entity_ids_are_scoped_to_each_scene(self):
        visuals = fixture()
        other = copy.deepcopy(visuals['scenes'][0])
        other['id'] = 'scene-02'
        # Different geometry for the same ID is legal in a new scene.
        for beat in other['beats']:
            beat['layers'][0]['svg'] = '<ellipse rx="55" ry="40"/>'
        visuals['scenes'].append(other)
        self.assertEqual(validate_visuals(visuals, {'scenes': [{'id': 'scene-01'}, {'id': 'scene-02'}]}), 4)


class MediaCacheTests(unittest.TestCase):
    def test_changed_source_media_bytes_invalidate_render_signature(self):
        with tempfile.TemporaryDirectory() as directory:
            job = Path(directory)
            media = job / 'project/public/source/reference.mp4'
            media.parent.mkdir(parents=True)
            media.write_bytes(b'original clip')
            mix = job / 'full-mix.mp3'
            mix.write_bytes(b'unchanged narration and music')
            manifest = {'scenes': [{'id': 'scene-01', 'media': [
                {'file': 'source/reference.mp4', 'type': 'video', 'from': 2, 'duration': 4}]}]}
            first = render_signature(job, manifest, mix)
            self.assertEqual(first, render_signature(job, manifest, mix))
            media.write_bytes(b'revised clip with the same filename')
            self.assertNotEqual(first, render_signature(job, manifest, mix))


if __name__ == '__main__':
    unittest.main()
