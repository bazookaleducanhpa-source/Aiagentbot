import {registerRoot,Composition,AbsoluteFill,Sequence,staticFile,useCurrentFrame,useVideoConfig,Img} from 'remotion';
import {Audio,Video} from '@remotion/media';
import data from './manifest.json';
import {Cappy} from './Cappy';
import {ContinuousBiology} from './ContinuousBiology';
import {ContinuousStory} from './ContinuousStory';
import {HostMoments} from './HostMoments';
import {BiologyLabels} from './BiologyLabels';
import {ContinuousSpace} from './ContinuousSpace';
import {SpaceHost} from './SpaceHost';
import {SpaceLabels} from './SpaceLabels';
import {SpaceDetailShots,getSpaceDetailWindow} from './SpaceDetailShots';
import {AmbientBackdrop} from './AmbientBackdrop';
type Key={at:number;x:number;y:number;scale:number;rotation:number;opacity:number};
type Layer={svg:string;x:number;y:number;delay:number;motion:string;entity_id?:string;keyframes?:Key[]};
type EntityLabel={text:string;x:number;y:number;target_entity_id:string;from:number;duration:number};
type Beat={id:string;background:string;layers:Layer[];labels?:EntityLabel[];show_mascot:boolean;frames:number;from:number;art?:{file:string}};
type Media={file:string;type:'video'|'image';from:number;duration:number;trim?:number;width:number;height:number;crop?:number[];credit?:string;label?:string};
type Scene={id:string;section_title?:string;from:number;frames:number;words:{text?:string;start:number;end:number}[];beats:Beat[];motion?:{kind:string;backgroundFile?:string};media?:Media[]};
const film=data as unknown as {width:number;height:number;fps:number;frames:number;scenes:Scene[]};
const clamp=(x:number)=>Math.max(0,Math.min(1,x));
const smooth=(x:number)=>{x=clamp(x);return x*x*(3-2*x)};
const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
function Tracks({scene,frame}:{scene:Scene;frame:number}){
 const entities=new Map<string,{svg:string;keys:Key[];first:number;last:number}>();
 scene.beats.forEach((b,bi)=>b.layers.forEach((l,li)=>{
  const id=l.entity_id||`${bi}-${li}`,old=entities.get(id);
  const keys=(l.keyframes?.length?l.keyframes:[{at:0,x:l.x,y:l.y,scale:1,rotation:0,opacity:1},{at:1,x:l.x,y:l.y,scale:1,rotation:0,opacity:1}]).map(k=>({...k,at:b.from+k.at*b.frames}));
  if(old){old.keys.push(...keys);old.last=b.from+b.frames}else entities.set(id,{svg:l.svg,keys,first:b.from,last:b.from+b.frames});
 }));
 return <><AmbientBackdrop seconds={(scene.from+frame)/film.fps}/>{Array.from(entities.entries()).map(([id,e])=>{
  if(frame<e.first||frame>=e.last)return null;
  const keys=e.keys.sort((a,b)=>a.at-b.at);let i=0;while(i<keys.length-2&&keys[i+1].at<=frame)i++;
  const a=keys[i],b=keys[Math.min(i+1,keys.length-1)],q=smooth((frame-a.at)/Math.max(1,b.at-a.at));
  return <g key={id} opacity={mix(a.opacity,b.opacity,q)} transform={`translate(${mix(a.x,b.x,q)} ${mix(a.y,b.y,q)}) rotate(${mix(a.rotation,b.rotation,q)}) scale(${mix(a.scale,b.scale,q)})`} dangerouslySetInnerHTML={{__html:e.svg}}/>;
 })}{scene.beats.flatMap(b=>(b.labels||[]).map((l,li)=>{
  const start=b.from+l.from*film.fps,end=Math.min(b.from+b.frames,start+l.duration*film.fps);
  const e=entities.get(l.target_entity_id);if(!e||frame<start||frame>=end)return null;
  const keys=e.keys.sort((a,b)=>a.at-b.at);let i=0;while(i<keys.length-2&&keys[i+1].at<=frame)i++;
  const a=keys[i],z=keys[Math.min(i+1,keys.length-1)],q=smooth((frame-a.at)/Math.max(1,z.at-a.at));
  const tx=mix(a.x,z.x,q),ty=mix(a.y,z.y,q),width=l.text.length*19+44;
  const x=Math.max(width/2+40,Math.min(1880-width/2,tx+l.x)),y=Math.max(155,Math.min(970,ty+l.y));
  const opacity=smooth((frame-start)/7)*smooth((end-frame)/10)*mix(a.opacity,z.opacity,q);
  return <g key={`${b.id}-label-${li}`} opacity={opacity}>
   <path d={`M${x} ${y}L${tx} ${ty}`} fill="none" stroke="#607f86" strokeWidth="2"/>
   <rect x={x-width/2} y={y-30} width={width} height="60" rx="23" fill="#fffdf4" stroke="#b1c7c9" strokeWidth="2"/>
   <text x={x} y={y+1} dominantBaseline="middle" textAnchor="middle" fontFamily="Arial, sans-serif" fontSize="34" fontWeight="600" fill="#365963">{l.text}</text>
  </g>;
 }))}</>;
}
function SourceMedia({media}:{media:Media}){
 const f=useCurrentFrame(),{fps}=useVideoConfig(),seconds=f/fps;
 const opacity=smooth(seconds/.5)*smooth((media.duration-seconds)/.5);
 const [x,y,cw,ch]=media.crop||[0,0,media.width,media.height];
 const w=Math.min(1700,870*cw/ch),h=w*ch/cw;
 const style={position:'absolute' as const,width:`${media.width/cw*100}%`,height:`${media.height/ch*100}%`,left:`${-x/cw*100}%`,top:`${-y/ch*100}%`,maxWidth:'none'};
 return <AbsoluteFill style={{opacity,background:'#183b42'}}><div style={{position:'absolute',left:(1920-w)/2,top:(1080-h)/2,width:w,height:h,overflow:'hidden',borderRadius:48,boxShadow:'0 30px 70px #0005'}}>
 {media.type==='video'?<Video src={staticFile(media.file)} muted trimBefore={Math.round((media.trim||0)*fps)} style={style}/>:<Img src={staticFile(media.file)} style={style}/>}</div>{media.label&&<div style={{position:'absolute',left:70,bottom:110,color:'#fff7df',font:'600 32px Arial',background:'#102335dc',padding:'10px 18px',borderRadius:14}}>{media.label}</div>}{media.credit&&<div style={{position:'absolute',left:70,bottom:55,color:'#e0eded',font:'24px Arial',background:'#102335dc',padding:'8px 14px',borderRadius:10}}>{media.credit}</div>}</AbsoluteFill>;
}
function SceneFilm({scene}:{scene:Scene}){
 const frame=useCurrentFrame(),{fps}=useVideoConfig();
 const speaking=scene.words.some(w=>frame/fps>=w.start+.15&&frame/fps<w.end+.15);
 const hasMedia=scene.media?.some(m=>frame/fps>=m.from&&frame/fps<m.from+m.duration);
 const detailProps={sceneId:scene.id,frame,frames:scene.frames,fps,words:scene.words,globalSeconds:(scene.from+frame)/fps};
 const detailWindow=scene.motion?.kind==='space'?getSpaceDetailWindow(detailProps):null;
 const hasDetail=!!detailWindow&&!hasMedia&&frame/fps>=detailWindow.start&&frame/fps<detailWindow.end;
 return <AbsoluteFill style={{background:scene.beats[0]?.background||'#e5f1ed'}}>
  <svg viewBox="0 0 1920 1080" width="100%" height="100%" strokeLinecap="round" strokeLinejoin="round">
   {scene.motion?.kind==='host'?<HostMoments outro={scene.id==='host-outro'} frame={frame} frames={scene.frames} fps={fps} speaking={speaking} words={scene.words}/>:scene.motion?.kind==='space'?<ContinuousSpace backgroundSeconds={(scene.from+frame)/fps} backgroundFile={scene.motion.backgroundFile} sceneId={scene.id} frame={frame} frames={scene.frames} fps={fps} words={scene.words.map(w=>({...w,text:w.text||''}))}/>:scene.motion?.kind==='biology'?<ContinuousBiology sceneId={scene.id} frame={frame} frames={scene.frames} fps={fps}/>:scene.motion?.kind==='story'?<ContinuousStory sceneId={scene.id} frame={frame} frames={scene.frames} fps={fps}/>:<Tracks scene={scene} frame={frame}/>}
   {scene.motion?.kind==='space'&&['space-02','space-24'].includes(scene.id)&&<SpaceHost frame={frame} frames={scene.frames} fps={fps} speaking={speaking} words={scene.words} outro={scene.id==='space-24'}/>}
   {scene.motion?.kind==='biology'&&!hasMedia&&<BiologyLabels sceneId={scene.id} frame={frame} frames={scene.frames} fps={fps}/>}
   {scene.motion?.kind==='space'&&!hasMedia&&!hasDetail&&<SpaceLabels sceneId={scene.id} frame={frame} frames={scene.frames} fps={fps} words={scene.words}/>}
   {hasDetail&&<SpaceDetailShots {...detailProps}/>}
   {scene.motion?.kind!=='host'&&!['space-02','space-24'].includes(scene.id)&&!hasMedia&&scene.beats.some(b=>b.show_mascot)&&<g transform="translate(38 800) scale(.6)"><Cappy frame={frame} mouth={speaking?.22+.25*Math.abs(Math.sin(frame*.45)):0} pose="point" accent="white"/></g>}
  </svg>
  {!scene.motion&&scene.beats.filter(b=>b.art).map(b=><Sequence key={b.id} from={b.from} durationInFrames={b.frames}><SourceMedia media={{file:b.art!.file,type:'image',from:0,duration:b.frames/fps,width:1920,height:1080}}/></Sequence>)}
  {(scene.media||[]).map((m,i)=><Sequence key={i} from={Math.round(m.from*fps)} durationInFrames={Math.round(m.duration*fps)}><SourceMedia media={m}/></Sequence>)}
  {scene.section_title&&<div style={{position:'absolute',left:54,top:40,padding:'14px 24px',borderRadius:20,background:scene.motion?.kind==='space'?'linear-gradient(145deg,#2c475ff5,#182e45f5)':'#fffdf4ed',color:scene.motion?.kind==='space'?'#f0f6e8':'#365963',fontFamily:'Arial, sans-serif',fontWeight:600,fontSize:32,border:scene.motion?.kind==='space'?'1px solid #8fc3c768':'none',borderLeft:scene.motion?.kind==='space'?'5px solid #a8dfd2':undefined,boxShadow:'0 8px 22px #020c242d'}}>{scene.section_title}</div>}
 </AbsoluteFill>;
}
const Film=()=> <AbsoluteFill><Audio src={staticFile('sound/full-mix.mp3')}/>{film.scenes.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.frames}><SceneFilm scene={s}/></Sequence>)}</AbsoluteFill>;
registerRoot(()=> <Composition id="Remake" component={Film} width={film.width} height={film.height} fps={film.fps} durationInFrames={film.frames}/>);
