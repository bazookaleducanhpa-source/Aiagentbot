"""Local OmniVoice narration. Uses a designed voice, no creator voice reference."""
from pathlib import Path
import argparse,json,sys,time,os
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser()
 src=p.add_mutually_exclusive_group(required=True);src.add_argument('--text');src.add_argument('--text-file',type=Path)
 p.add_argument('--output',type=Path,default=ROOT/'output/omnivoice/preview.wav')
 p.add_argument('--steps',type=int,default=16);p.add_argument('--speed',type=float,default=1.0)
 p.add_argument('--instruct',default='male, young adult, moderate pitch')
 p.add_argument('--threads',type=int,default=8);p.add_argument('--seed',type=int,default=2026)
 p.add_argument('--model',type=Path,default=ROOT/'.tools/omnivoice-model')
 args=p.parse_args();args.output.parent.mkdir(parents=True,exist_ok=True)
 os.environ.setdefault('HF_HUB_OFFLINE','1')
 os.environ.setdefault('TOKENIZERS_PARALLELISM','false')
 ffmpeg_dir=ROOT/'.tools/ffmpeg/ffmpeg-9.0.2-full_build/bin'
 os.environ['PATH']=str(ffmpeg_dir)+os.pathsep+os.environ.get('PATH','')
 import torch,numpy as np,soundfile as sf
 from omnivoice import OmniVoice
 torch.set_num_threads(args.threads);torch.set_num_interop_threads(1);torch.manual_seed(args.seed)
 text=args.text if args.text is not None else args.text_file.read_text(encoding='utf-8-sig')
 print('Loading OmniVoice on CPU...',flush=True);start=time.perf_counter()
 model=OmniVoice.from_pretrained(str(args.model.resolve()),device_map='cpu',dtype=torch.float32,attn_implementation='sdpa')
 model.eval();loaded=time.perf_counter();print(f'Model loaded in {loaded-start:.1f}s; synthesizing...',flush=True)
 with torch.inference_mode():
  outputs=model.generate(text=text,instruct=args.instruct,num_step=args.steps,speed=args.speed)
 elapsed=time.perf_counter()-loaded;audio=np.asarray(outputs[0],dtype=np.float32).reshape(-1)
 if not np.isfinite(audio).all() or len(audio)<12000:raise RuntimeError('Invalid generated audio')
 rms=float(np.sqrt(np.mean(audio**2)));peak=float(np.max(np.abs(audio)))
 if rms<.0005:raise RuntimeError('Generated audio is silent')
 sf.write(args.output,audio,24000)
 report=dict(engine='omnivoice',engine_version=__import__('importlib.metadata',fromlist=['version']).version('omnivoice'),torch=torch.__version__,device='cpu',threads=args.threads,model=str(args.model.resolve()),model_revision='c5fdb5ccb189668d56333f77ba2629f4cd7535f4',instruct=args.instruct,steps=args.steps,speed=args.speed,seed=args.seed,load_seconds=loaded-start,generation_seconds=elapsed,audio_seconds=len(audio)/24000,real_time_factor=elapsed/(len(audio)/24000),rms=rms,peak=peak,output=str(args.output.resolve()),reference_audio=None,text=text)
 args.output.with_suffix('.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':main()
