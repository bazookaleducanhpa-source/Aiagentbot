import json
import os
import shutil
import subprocess
import wave
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
from .config import ARTIFACTS, env
from . import providers

def ffmpeg_path():
    configured = env('FFMPEG_PATH')
    if configured:
        if not Path(configured).is_file():
            raise providers.ProviderError('FFMPEG_PATH does not exist.')
        return configured
    found = shutil.which('ffmpeg')
    if found:
        return found
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()

def font(size, bold=False):
    candidates = [Path(os.getenv('WINDIR', 'C:/Windows')) / 'Fonts' / ('arialbd.ttf' if bold else 'arial.ttf'),
                  Path('/usr/share/fonts/truetype/dejavu') / ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')]
    for path in candidates:
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size=size)

def wrap(draw, text, face, width):
    lines, line = [], ''
    for word in text.split():
        test = (line + ' ' + word).strip()
        if line and draw.textlength(test, font=face) > width:
            lines.append(line)
            line = word
        else:
            line = test
    if line:
        lines.append(line)
    return lines

def slide(scene, index, count, path, is_demo, background=None):
    image = Image.new('RGB', (720, 1280), '#0b1720')
    if background:
        with Image.open(background) as src:
            image = ImageOps.fit(src.convert('RGB'), (720, 1280))
        shade = Image.new('RGBA', image.size, (0, 0, 0, 0))
        shading = ImageDraw.Draw(shade)
        shading.rectangle((0, 720, 720, 1280), fill=(6, 15, 27, 218))
        shading.rectangle((0, 0, 720, 190), fill=(6, 15, 27, 145))
        image = Image.alpha_composite(image.convert('RGBA'), shade).convert('RGB')
        draw = ImageDraw.Draw(image)
        draw.text((40, 35), 'DREAMFORGE / ORIGINAL AI STORIES', font=font(21, True), fill='#82f0c3')
        face = font(37, True)
        y = 760
        for line in wrap(draw, scene['heading'], face, 640):
            draw.text((40, y), line, font=face, fill='white')
            y += 48
        face = font(26)
        lines = wrap(draw, scene['narration'], face, 640)
        while len(lines) * (face.size + 8) > 1210 - y and face.size > 16:
            face = font(face.size - 2)
            lines = wrap(draw, scene['narration'], face, 640)
        y += 12
        for line in lines:
            draw.text((40, y), line, font=face, fill='#e5ecf4')
            y += face.size + 8
        draw.text((40, 1240), 'AI-generated visuals and voice', font=font(17), fill='#a8beca')
        image.save(path)
        return
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((40, 40, 680, 1240), 32, fill='#122631', outline='#28424c', width=2)
    draw.text((80, 90), 'DREAMFORGE / AI STORIES', font=font(24, True), fill='#82f0c3')
    draw.text((80, 175), f'{index + 1:02} / {count:02}', font=font(36), fill='#8297a4')
    y = 270
    face = font(48, True)
    for line in wrap(draw, scene['heading'], face, 560):
        draw.text((80, y), line, font=face, fill='#f0f7fa')
        y += 62
    draw.line((80, y + 25, 250, y + 25), fill='#82f0c3', width=5)
    face = font(32)
    lines = wrap(draw, scene['narration'], face, 560)
    # Shrink long narration so nothing is silently cropped.
    while len(lines) * (face.size + 12) > 1040 - (y + 65) and face.size > 18:
        face = font(face.size - 2)
        lines = wrap(draw, scene['narration'], face, 560)
    y += 65
    for line in lines:
        draw.text((80, y), line, font=face, fill='#c9d9e1')
        y += face.size + 12
    if is_demo and y < 820:
        # Original geometric character art; live mode replaces this with AI scene images.
        draw.ellipse((170, 1010, 550, 1090), fill='#193943')
        draw.rounded_rectangle((275, 830, 445, 930), 30, fill='#a9bdc7', outline='#d8e5eb', width=3)
        draw.rounded_rectangle((295, 920, 425, 1040), 22, fill='#849eab')
        draw.rounded_rectangle((292, 855, 428, 905), 18, fill='#102833')
        draw.ellipse((318, 868, 340, 890), fill='#82f0c3')
        draw.ellipse((380, 868, 402, 890), fill='#82f0c3')
        draw.rounded_rectangle((280, 922, 440, 946), 8, fill='#ebc86a')
        draw.polygon([(410, 934), (443, 978), (420, 997), (395, 936)], fill='#ebc86a')
        draw.rounded_rectangle((302, 1030, 337, 1065), 8, fill='#a9bdc7')
        draw.rounded_rectangle((383, 1030, 418, 1065), 8, fill='#a9bdc7')
        for sx, sy, radius in [(200, 875, 18), (525, 860, 26), (490, 980, 12), (230, 990, 10)]:
            color = '#ebc86a' if index > 1 else '#537d88'
            draw.polygon([(sx,sy-radius),(sx+radius/3,sy-radius/3),(sx+radius,sy),(sx+radius/3,sy+radius/3),(sx,sy+radius),(sx-radius/3,sy+radius/3),(sx-radius,sy),(sx-radius/3,sy-radius/3)], fill=color)
    draw.rounded_rectangle((80, 1140, 640, 1150), 5, fill='#29434c')
    draw.rounded_rectangle((80, 1140, int(80 + 560 * (index + 1) / count), 1150), 5, fill='#82f0c3')
    draw.text((80, 1180), 'DEMO • SAMPLE STORY • SILENT AUDIO' if is_demo else 'AI-generated visuals and voice', font=font(19), fill='#8297a4')
    image.save(path)

def silence(path, seconds):
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(24000)
        w.writeframes(b'\0\0' * int(seconds * 24000))

def timestamp(seconds):
    ms = round(seconds * 1000)
    return f'{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}'

def render(job, on_event, local_images=None):
    binary = ffmpeg_path()
    folder = ARTIFACTS / job['id']
    folder.mkdir(exist_ok=True)
    script = job['script']
    scenes = script['scenes']
    if local_images is not None:
        if len(local_images) != len(scenes) or any(not Path(p).is_file() for p in local_images):
            raise providers.ProviderError('Provide one existing local image for each scene.')
    is_demo = job['mode'] == 'demo'
    captions, cursor, parts = [], 0.0, []
    for i, scene in enumerate(scenes):
        on_event(f'Rendering scene {i + 1}/{len(scenes)}')
        png, wav, part = folder / f'scene-{i}.png', folder / f'voice-{i}.wav', folder / f'part-{i}.mp4'
        background = None
        if not is_demo:
            background = folder / f'image-{i}.png'
            if local_images is not None:
                if Path(local_images[i]).resolve() != background.resolve():
                    shutil.copyfile(local_images[i], background)
            else:
                providers.image(scene.get('visual') or scene['heading'], background)
        slide(scene, i, len(scenes), png, is_demo, background)
        if is_demo:
            silence(wav, job['spec']['duration'] / len(scenes))
        else:
            providers.speech(scene['narration'], wav, binary)
        with wave.open(str(wav), 'rb') as w:
            duration = w.getnframes() / w.getframerate()
        words = scene['narration'].split()
        for start in range(0, len(words), 9):
            end = min(start + 9, len(words))
            captions.append(f'{len(captions) + 1}\n{timestamp(cursor + duration * start / len(words))} --> {timestamp(cursor + duration * end / len(words))}\n' + ' '.join(words[start:end]) + '\n')
        cursor += duration
        command = [binary, '-y', '-loop', '1', '-framerate', '30', '-i', str(png), '-i', str(wav),
                   '-t', str(duration), '-vf', "zoompan=z='min(zoom+0.000072,1.04)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=720x1280:fps=30", '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '24',
                   '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '24000', '-ac', '1', '-movflags', '+faststart', str(part)]
        subprocess.run(command, check=True, capture_output=True, timeout=240)
        parts.append(part)
    concat = folder / 'concat.txt'
    concat.write_text('\n'.join(f"file '{p.name}'" for p in parts), encoding='utf-8')
    video = folder / 'video.mp4'
    subprocess.run([binary, '-y', '-f', 'concat', '-safe', '0', '-i', str(concat), '-c', 'copy', '-movflags', '+faststart', str(video)],
                   check=True, capture_output=True, timeout=120)
    (folder / 'captions.srt').write_text('\n'.join(captions), encoding='utf-8')
    (folder / 'script.json').write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding='utf-8')
    (folder / 'research.json').write_text(json.dumps(job['research'], ensure_ascii=False, indent=2), encoding='utf-8')
    caption = script['title'] + '\n\n' + script['description'] + '\n\n' + ' '.join(script['hashtags']) + '\nAI-generated visuals and narration. Fictional story.'
    if is_demo:
        caption = 'DEMO — SAMPLE CONTENT, SILENT AUDIO\n' + caption
    (folder / 'caption.txt').write_text(caption, encoding='utf-8')
    shutil.copyfile(folder / 'scene-0.png', folder / 'cover.png')
    with zipfile.ZipFile(folder / 'publish-kit.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name in ('video.mp4', 'captions.srt', 'caption.txt', 'cover.png', 'script.json', 'research.json'):
            z.write(folder / name, name)
    return {'video': f"/artifacts/{job['id']}/video.mp4", 'cover': f"/artifacts/{job['id']}/cover.png",
            'kit': f"/artifacts/{job['id']}/publish-kit.zip", 'captions': f"/artifacts/{job['id']}/captions.srt",
            'duration': round(cursor, 1), 'voice': 'silent-demo' if is_demo else env('TTS_PROVIDER', 'openai')}
