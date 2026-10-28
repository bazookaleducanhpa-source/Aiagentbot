"""Clone an authorized reference with the locally installed OmniVoice model."""
import argparse
import json
import os
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--reference-text', type=Path, required=True)
    parser.add_argument('--text-file', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--steps', type=int, default=24)
    parser.add_argument('--speed', type=float, default=1.0)
    parser.add_argument('--threads', type=int, default=8)
    args = parser.parse_args()
    os.environ.setdefault('HF_HUB_OFFLINE', '1')
    os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
    os.environ['PATH'] = str(ROOT / '.tools/ffmpeg/ffmpeg-9.0.2-full_build/bin') + os.pathsep + os.environ.get('PATH', '')
    import numpy as np
    import soundfile as sf
    import torch
    from omnivoice import OmniVoice

    torch.set_num_threads(args.threads)
    torch.set_num_interop_threads(1)
    torch.manual_seed(2026)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    target_text = args.text_file.read_text(encoding='utf-8-sig').strip()
    reference_text = args.reference_text.read_text(encoding='utf-8-sig').strip()
    if not target_text or not reference_text:
        raise ValueError('Target and reference transcripts must be nonempty')
    start = time.perf_counter()
    print('Loading local OmniVoice...', flush=True)
    model = OmniVoice.from_pretrained(str(ROOT / '.tools/omnivoice-model'), device_map='cpu', dtype=torch.float32, attn_implementation='sdpa')
    model.eval()
    reference_audio, sample_rate = sf.read(args.reference, dtype='float32')
    if reference_audio.ndim > 1:
        reference_audio = reference_audio.mean(axis=1)
    with torch.inference_mode():
        prompt = model.create_voice_clone_prompt(ref_audio=(torch.from_numpy(reference_audio), sample_rate), ref_text=reference_text, preprocess_prompt=False)
        prompt.save(str(args.output.parent / 'voice-prompt.pt'))
        print('Reference encoded; generating cloned speech...', flush=True)
        audio = model.generate(text=target_text, language='vi', voice_clone_prompt=prompt, num_step=args.steps, speed=args.speed, denoise=True)[0]
    audio = np.asarray(audio, dtype=np.float32).reshape(-1)
    if not np.isfinite(audio).all() or len(audio) < model.sampling_rate or np.sqrt(np.mean(audio ** 2)) < .0005:
        raise RuntimeError('Generated audio is invalid or silent')
    sf.write(args.output, audio, model.sampling_rate)
    report = dict(reference=str(args.reference.resolve()), reference_text=reference_text, text=target_text, seconds=len(audio)/model.sampling_rate, sample_rate=model.sampling_rate, peak=float(np.abs(audio).max()), rms=float(np.sqrt(np.mean(audio**2))), processing_seconds=time.perf_counter()-start, steps=args.steps, speed=args.speed, engine='OmniVoice', device='cpu', subjective_similarity_verified=False)
    args.output.with_suffix('.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=True), flush=True)


if __name__ == '__main__':
    main()
