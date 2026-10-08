"""Original 2D short: procedural character animation, timed captions and audio mix."""
import json
import math
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.media import ffmpeg_path, font, wrap, timestamp

ROOT = Path(__file__).resolve().parent.parent
FOLDER = ROOT / 'data' / 'lemon-bakery'
W, H, FPS, DURATION = 720, 1280, 30, 35
INK = '#31263a'
WORDS = json.loads((FOLDER / 'transcription.json').read_text(encoding='utf-8'))['words']
CUTS = [0, 6.76, 9.64, 11.9, 22.24, 26.66, 35]
LABELS = ['FIRED FOR BEING SOUR', 'THE SWEET REPLACEMENT', 'SALES EXPLODED',
          'SOMETHING WAS MISSING', 'ONE CONDITION', 'WHO IS SOUR NOW?']


def centered(draw, text, y, size, color=INK):
    face = font(size, True)
    draw.text(((W - draw.textlength(text, font=face)) / 2, y), text, font=face, fill=color)


def cupcake(draw, x, y, size=1, bad=False):
    s = size
    draw.polygon([(x-25*s, y), (x+25*s,y), (x+19*s,y+36*s), (x-19*s,y+36*s)], fill='#efb761', outline=INK)
    draw.ellipse((x-32*s,y-34*s,x+32*s,y+12*s), fill='#f794bc' if not bad else '#e7e2d8', outline=INK, width=3)
    draw.ellipse((x-7*s,y-42*s,x+7*s,y-28*s), fill='#db4754')


def character(draw, kind, x, y, t, mood='happy', scale=1, pose='idle', talking=False):
    s = scale
    bob = math.sin(t*6)*4*s if pose != 'kneel' else 0
    y += bob
    def box(a,b,c,d): return (x+a*s,y+b*s,x+c*s,y+d*s)
    def line(points, fill=INK, width=8):
        draw.line([(x+a*s,y+b*s) for a,b in points],fill=fill,width=max(1,int(width*s)),joint='curve')
    draw.ellipse(box(-82,112,82,135),fill='#d4a66c')
    walk = math.sin(t*13)*22 if pose=='walk' else math.sin(t*3)*3
    line([(-33,73),(-37-walk,122)])
    line([(33,73),(37+walk,122)])
    draw.ellipse(box(-57-walk,110,-21-walk,130),fill=INK)
    draw.ellipse(box(21+walk,110,57+walk,130),fill=INK)
    if kind == 'lemon':
        draw.ellipse(box(-91,-105,91,84),fill='#ffdb42',outline=INK,width=max(2,int(5*s)))
        draw.polygon([(x-14*s,y-109*s),(x+28*s,y-144*s),(x+48*s,y-108*s)],fill='#51ad66',outline=INK)
        draw.rounded_rectangle(box(-59,12,59,78),radius=12*s,fill='#274964',outline=INK,width=3)
        draw.rounded_rectangle(box(-60,-150,60,-108),radius=13*s,fill='#fff9ed',outline=INK,width=3)
        for a in [-37,0,37]: draw.ellipse(box(a-28,-180,a+28,-130),fill='#fff9ed',outline=INK,width=3)
    elif kind == 'orange':
        draw.ellipse(box(-94,-105,94,84),fill='#ff9142',outline=INK,width=max(2,int(5*s)))
        draw.polygon([(x-7*s,y-105*s),(x+10*s,y-135*s),(x+42*s,y-115*s)],fill='#5aaa57',outline=INK)
        draw.rounded_rectangle(box(-63,16,63,79),radius=12*s,fill='#82509b',outline=INK,width=3)
        draw.polygon([(x-28*s,y+9*s),(x,y+22*s),(x+28*s,y+9*s),(x+28*s,y+34*s),(x,y+22*s),(x-28*s,y+34*s)],fill='#f7cf65')
    elif kind == 'sugar':
        draw.rounded_rectangle(box(-76,-92,76,82),radius=15*s,fill='#fffcf1',outline=INK,width=5)
        draw.rounded_rectangle(box(-57,20,57,76),radius=8*s,fill='#ed91b8',outline=INK,width=3)
        for a,b in [(-50,-66),(38,-62),(-16,-78),(52,8)]: draw.rectangle(box(a,b,a+6,b+6),fill='#d7d1c5')
    else:
        draw.ellipse(box(-85,-100,85,85),fill='#e96878',outline=INK,width=max(2,int(5*s)))
        line([(0,-100),(10,-140),(38,-152)],fill='#50925f',width=6)
        draw.rounded_rectangle(box(-60,17,60,79),radius=12*s,fill='#458c92',outline=INK,width=3)
    blink = (int(t*30)%117 in (0,1,2))
    for eye in [-32,32]:
        if blink: line([(eye-8,-40),(eye+8,-40)],width=4)
        else:
            draw.ellipse(box(eye-12,-57,eye+12,-27),fill=INK)
            draw.ellipse(box(eye-7,-51,eye-1,-43),fill='white')
    if mood in ('angry','smug'):
        line([(-47,-77),(-20,-65)],width=5); line([(20,-65),(47,-77)],width=5)
    elif mood in ('sad','shock'):
        line([(-47,-65),(-20,-77)],width=5); line([(20,-77),(47,-65)],width=5)
    if talking or mood=='shock': draw.ellipse(box(-12,-13,12,5+7*abs(math.sin(t*16))),fill=INK)
    elif mood=='sad': draw.arc(box(-22,-6,22,25),185,355,fill=INK,width=4)
    else: draw.arc(box(-25,-26,25,3),5,175,fill=INK,width=4)
    arm = math.sin(t*5)*14
    if pose=='point':
        line([(-86,-4),(-125,22)]); line([(86,-4),(138,-38),(178,-40)])
        draw.ellipse(box(164,-50,188,-30),fill='#ffb374')
    elif pose=='kneel':
        line([(-86,-4),(-22,44)]); line([(86,-4),(22,44)])
    elif pose=='wave':
        line([(-86,-4),(-111,31)]); line([(86,-4),(123,-64+arm),(134,-105+arm)])
    else:
        line([(-86,-4),(-117,24+arm)]); line([(86,-4),(117,24-arm)])


def background(draw, outside=False, dim=False, final=False):
    draw.rectangle((0,0,W,H),fill='#ffe9bd' if not outside else '#bbdfed')
    draw.rectangle((0,800,W,H),fill='#e7bd82' if not outside else '#b1c4a5')
    for a in range(0,W,90):
        draw.rectangle((a,190,a+45,265),fill='#dc776d')
        draw.rectangle((a+45,190,a+90,265),fill='#fff5e0')
    draw.rounded_rectangle((40,280,680,405),radius=22,fill=INK)
    centered(draw, 'LEMON & CO.' if final else 'THE SWEET SPOT',310,40,'#fff3d1')
    for x in [60,490]:
        draw.rounded_rectangle((x,445,x+170,655),radius=17,fill='#789db7',outline=INK,width=6)
        draw.line((x+85,450,x+85,650),fill=INK,width=4)
    draw.rounded_rectangle((280,445,440,750),radius=15,fill='#ddb481',outline=INK,width=5)
    draw.ellipse((404,598,418,612),fill=INK)
    if not outside:
        draw.rectangle((0,830,W,870),fill='#8d614e')
        draw.rectangle((0,870,W,1000),fill='#c78c62')
        for x in [85,170,255,465,550,635]: cupcake(draw,x,839,.62)
    if dim:
        draw.rectangle((45,1020,675,1075),fill='#d06864')
        centered(draw,'CUSTOMERS LEFT',1028,30,'white')


def frame(t):
    picture = Image.new('RGB',(W,H))
    d = ImageDraw.Draw(picture)
    stage = min(5,next((i for i in range(6) if CUTS[i]<=t<CUTS[i+1]),5))
    u = (t-CUTS[stage])/(CUTS[stage+1]-CUTS[stage])
    background(d,outside=stage in (0,4),dim=stage==3,final=stage==5)
    if stage==0:
        character(d,'orange',505,747,t,'angry',1.05,'point')
        character(d,'lemon',290-230*u,774,t,'sad',1.0,'walk')
        if t<2.5:
            d.rounded_rectangle((65,475,320,555),radius=18,fill='#e45e58')
            d.text((92,488),'YOU ARE FIRED!',font=font(24,True),fill='white')
        else:
            for k in range(2):
                x=80-210*u+k*35; y=718+(t*120+k*15)%100
                d.ellipse((x,y,x+8,y+15),fill='#659dde')
    elif stage==1:
        character(d,'orange',230,733,t,'smug',1,'wave')
        character(d,'sugar',580-170*u,757,t,'happy',.95,'walk')
    elif stage==2:
        character(d,'sugar',370,720,t,'happy',1.0,'wave')
        for k in range(5):
            y=470+(t*160+k*65)%245; x=270+math.sin(t*5+k)*30
            d.rounded_rectangle((x,y,x+15,y+15),radius=2,fill='white',outline='#d4cabb')
        for k in range(4):
            centered(d,'$'*(k+1), 465+k*58-math.sin(t*4+k)*9,31,'#3a9869')
        d.ellipse((282,758,460,812),fill='#98b8ca',outline=INK,width=5)
    elif stage==3:
        character(d,'orange',500,731,t,'shock' if t<17.4 else 'sad',.98)
        character(d,'cherry' if t<17.4 else 'sugar',195-(max(0,u-.25)*290),777,t,'shock',.8,'walk')
        cupcake(d,210,730,1.0,bad=True)
        if 15<t<17.4:
            for k in range(8):
                x=235+((t-15)*125+k*12)%200; y=722+math.sin(k+t)*28
                d.ellipse((x,y,x+7,y+7),fill='#ec9bb3')
        if t>=17.4:
            d.rounded_rectangle((80,460,410,595),radius=18,fill='#fff9e9',outline=INK,width=4)
            d.text((110,478),'SECRET RECIPE',font=font(26,True),fill=INK)
            d.text((110,523),'SWEET + SOUR',font=font(30,True),fill='#61835e')
    elif stage==4:
        character(d,'orange',220+45*u,800,t,'sad',.95,'kneel')
        character(d,'lemon',510,745,t,'smug',1.0,'point')
        d.rounded_rectangle((140,458,580,570),radius=18,fill='#fff8e9',outline=INK,width=4)
        centered(d,'PUT MY NAME',473,33); centered(d,'ON THE DOOR.',516,33)
    else:
        character(d,'lemon',330,715,t,'happy',1.1,'wave')
        character(d,'orange',600,755,t,'sad',.68,'kneel')
        d.ellipse((557,820,657,854),fill='#aec6d5',outline=INK,width=3)
        cupcake(d,185+30*math.sin(t*3),665-abs(math.sin(t*3))*130,.9)
        for k in range(18):
            x=(k*53+int(t*25))%W; y=440+(k*37+int(t*80))%330
            d.rectangle((x,y,x+6,y+13),fill=['#ec6d74','#f3cf4e','#5da486'][k%3])
    centered(d,'DREAMFORGE STORIES',64,23,'#765773')
    # Short title and word-aligned caption stay clear of platform controls.
    for n,line in enumerate(wrap(d,LABELS[stage],font(36,True),620)):
        centered(d,line,110+n*43,36)
    active = next((i for i,w in enumerate(WORDS) if w['start']<=t<=w['end']),None)
    if active is not None:
        first=(active//4)*4
        chunk=WORDS[first:first+4]
        text=' '.join(w['word'] for w in chunk)
        lines=wrap(d,text,font(35,True),590)
        d.rounded_rectangle((48,1085,672,1108+len(lines)*43),radius=18,fill=INK)
        for n,line in enumerate(lines): centered(d,line,1096+n*43,35,'#ffedb3')
    d.text((46,1210),'ORIGINAL FICTION / AI VOICE',font=font(17,True),fill=INK)
    d.rounded_rectangle((48,1183,672,1189),radius=3,fill='#cfab84')
    d.rectangle((48,1183,48+624*t/DURATION,1189),fill='#7f5692')
    return picture


def main():
    for moment in [1.2,8.1,11,15.8,24.7,30.5]:
        frame(moment).save(FOLDER/f'preview-{moment}.png')
    silent=FOLDER/'animation-silent.mp4'
    command=[ffmpeg_path(),'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24',
        '-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264',
        '-preset','fast','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',str(silent)]
    log=FOLDER/'render-errors.log'
    with log.open('wb') as errors:
        process=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=errors)
        try:
            for i in range(DURATION*FPS):
                process.stdin.write(frame(i/FPS).tobytes())
                if i%150==0: print(f'Animated {i/FPS:.0f}/{DURATION}s',flush=True)
            process.stdin.close()
            if process.wait(timeout=120): raise RuntimeError('FFmpeg failed; inspect render-errors.log')
        finally:
            if process.poll() is None: process.kill(); process.wait()
    subprocess.run([ffmpeg_path(),'-v','error','-y','-i',str(silent),'-i',str(FOLDER/'audio-preview.mp3'),
        '-c:v','copy','-c:a','aac','-ar','48000','-b:a','192k','-t',str(DURATION),
        '-movflags','+faststart',str(FOLDER/'video-2d.mp4')],check=True,capture_output=True,timeout=120)
    captions=[]
    for first in range(0,len(WORDS),4):
        chunk=WORDS[first:first+4]
        captions.append(f'{len(captions)+1}\n{timestamp(chunk[0]["start"])} --> {timestamp(chunk[-1]["end"])}\n'+
            ' '.join(w['word'] for w in chunk)+'\n')
    (FOLDER/'captions.srt').write_text('\n'.join(captions),encoding='utf-8')
    print('VIDEO='+str(FOLDER/'video-2d.mp4'),flush=True)


if __name__=='__main__': main()
