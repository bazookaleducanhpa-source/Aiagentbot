"""Keep the installed Skill intact; fix URL paths in this project's copy."""
from pathlib import Path
import shutil
root = Path(__file__).resolve().parents[1]
source = Path('C:/Users/Tonny/.agents/skills/bs-paper-cutout-story-video')
target = root / 'output/tesla-cappy-skillry-v3/skillry/vendor'
if not target.exists():
    shutil.copytree(source, target)
for relative in ['scripts/build.mjs', 'scripts/lib/browser.mjs']:
    file = target / relative
    text = file.read_text(encoding='utf-8')
    if 'new URL(import.meta.url).pathname' in text:
        text = text.replace("import fs from 'node:fs';", "import fs from 'node:fs';\nimport { fileURLToPath } from 'node:url';")
        text = text.replace('new URL(import.meta.url).pathname', 'fileURLToPath(import.meta.url)')
        file.write_text(text, encoding='utf-8')
        print('Windows path fix:', relative)
