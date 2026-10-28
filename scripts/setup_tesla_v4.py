from pathlib import Path
import json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'output/tesla-cappy-v4-draft'
(DEST/'src').mkdir(parents=True,exist_ok=True)
(DEST/'public').mkdir(exist_ok=True)
(DEST/'research').mkdir(exist_ok=True)
OLD=ROOT/'output/tesla-cappy-skillry-v3'
for relative,source in [('node_modules',ROOT/'tools/motion-studio/node_modules'),('public/footage',OLD/'public/footage-hd')]:
    link=DEST/relative
    if not link.exists():subprocess.run(['rtk','proxy','cmd','/c','mklink','/J',str(link),str(source)],check=True)
shutil.copy2(OLD/'src/Cappy.tsx',DEST/'src/Cappy.tsx')
shutil.copy2(OLD/'tsconfig.json',DEST/'tsconfig.json')
(DEST/'package.json').write_text(json.dumps(dict(name='tesla-cappy-v4-draft',version='1.0.0',private=True,scripts=dict(dev='remotion studio src/index.tsx --port=3147',check='tsc --noEmit'),dependencies={'remotion':'4.0.537','@remotion/media':'4.0.537','@remotion/transitions':'4.0.537','react':'19.3.1','react-dom':'19.3.1'}),indent=2),encoding='utf-8')
if not (DEST/'src/index.tsx').exists():
    (DEST/'src/index.tsx').write_text('''import {registerRoot,Composition,AbsoluteFill} from 'remotion';
const Draft=()=> <AbsoluteFill style={{background:'#10212c',color:'white',justifyContent:'center',alignItems:'center',fontFamily:'Segoe UI',fontSize:65}}>Cappy · Đang biên tập bản nháp mới</AbsoluteFill>;
registerRoot(()=><Composition id="TeslaCappyV4" component={Draft} width={1920} height={1080} fps={30} durationInFrames={300}/>);
''',encoding='utf-8')
print(DEST)
