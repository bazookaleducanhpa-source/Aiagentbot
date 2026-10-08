import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / '.env')
DATA = Path(os.getenv('DATA_DIR', str(ROOT / 'data'))).resolve()
DATA.mkdir(parents=True, exist_ok=True)
ARTIFACTS = DATA / 'artifacts'
ARTIFACTS.mkdir(exist_ok=True)

def env(name, default=''):
    return os.getenv(name, default).strip()

def demo():
    return env('APP_MODE', 'demo') == 'demo'
