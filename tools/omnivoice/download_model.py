from pathlib import Path
import os,sys
os.environ['HF_HUB_DISABLE_XET']='1'
os.environ['HF_HUB_DOWNLOAD_TIMEOUT']='60'
sys.stdout.reconfigure(encoding='utf-8')
from huggingface_hub import snapshot_download
root=Path(__file__).resolve().parents[2]
print(snapshot_download('k2-fsa/OmniVoice',revision='c5fdb5ccb189668d56333f77ba2629f4cd7535f4',local_dir=str(root/'.tools/omnivoice-model'),max_workers=2),flush=True)
