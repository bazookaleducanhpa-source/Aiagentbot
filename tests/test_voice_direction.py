import unittest
from remake_studio.voice import directed_segments, cache_key

class VoiceDirectionTests(unittest.TestCase):
    def test_cannot_drop_or_reorder_words(self):
        for text in ['Hello.', 'world Hello.']:
            with self.assertRaises(ValueError):
                directed_segments({'narration':'Hello world.','voice_segments':[{'text':text}]})

    def test_prosody_and_pause_invalidate_cache(self):
        base=directed_segments({'narration':'Hello world.'})
        for field,value in [('rate','-5%'),('pitch','+3Hz'),('pause_after',.3)]:
            changed=[{**base[0],field:value}]
            self.assertNotEqual(cache_key(base),cache_key(changed))

    def test_neutral_preserves_whole_text(self):
        parts=directed_segments({'narration':'Hello world. Welcome back!'})
        self.assertEqual(len(parts),1)
        self.assertEqual(parts[0]['pause_after'],0)

    def test_conversational_preserves_connected_delivery(self):
        text = "Imagine a beam of light. One escapes; another never returns. Why?"
        parts = directed_segments({'narration':text,'voice_direction':'conversational'})
        self.assertEqual(len(parts),1)
        self.assertEqual(parts[0]['text'],text)
        self.assertEqual(parts[0]['pause_after'],0)
        self.assertEqual(parts[0]['pitch'],'+0Hz')

    def test_profile_splits_without_losing_words(self):
        parts=directed_segments({'narration':'Hello world. Welcome back!','voice_direction':'engaging'})
        self.assertEqual([p['text'] for p in parts],['Hello world.','Welcome back!'])
        self.assertGreater(parts[0]['pause_after'],0)
        self.assertEqual(parts[-1]['pause_after'],0)

if __name__=='__main__': unittest.main()
