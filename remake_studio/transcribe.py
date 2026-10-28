from pathlib import Path
import subprocess,sys,numpy as np
from faster_whisper import WhisperModel
root=Path(__file__).resolve().parents[1]
raw=subprocess.check_output(['ffmpeg','-v','error','-i',sys.argv[1],'-f','f32le','-ac','1','-ar','16000','pipe:1'])
model=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=6,download_root=str(root/'.tools/whisper-models'),local_files_only=True)
segments,_=model.transcribe(np.frombuffer(raw,dtype=np.float32),beam_size=3)
Path(sys.argv[2]).write_text('\n'.join(s.text.strip() for s in segments),encoding='utf-8')
