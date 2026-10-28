type Word={text?:string;start:number;end:number};
type Props={sceneId:string;frame:number;frames:number;fps:number;words?:Word[]};
export type SpaceLabel={id:string;text:string;x:number;y:number;tx:number;ty:number;start:number;end:number;visible:boolean};
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
const ease=(v:number)=>{v=clamp(v);return v*v*(3-2*v)};
const phase=(t:number,a:number,b:number)=>ease((t-a)/(b-a));
const mix=(a:number,b:number,q:number)=>a+(b-a)*q;
const clean=(s:string)=>s.toLowerCase().replace(/[^a-z0-9]/g,'');

/** Geometry mirrors ContinuousSpace exactly. Exported data permits frame-level
 * QA of label windows and attachment points without rendering the whole film. */
export function getSpaceLabels({sceneId,frame,frames,fps,words=[]}:Props):SpaceLabel[]{
 const sec=frame/fps,duration=frames/fps,t=clamp(frame/Math.max(1,frames-1)),n=Number(sceneId.slice(-2));
 const entries:SpaceLabel[]=[];
 const cue=(phrase:string,fallback:number)=>{
  const wanted=phrase.split(/\s+/).map(clean),tokens=words.flatMap(w=>(w.text||'').split(/\s+/).map(text=>({text:clean(text),start:w.start}))).filter(w=>w.text);
  const hits=tokens.flatMap((w,i)=>wanted.every((token,j)=>tokens[i+j]?.text===token)?[clamp((w.start+.15)/duration)]:[]);
  return hits.length?hits.reduce((a,b)=>Math.abs(a-fallback)<Math.abs(b-fallback)?a:b):fallback;
 };
 const action=(phrase:string,a:number,b:number)=>{const start=Math.min(.88,cue(phrase,a));return phase(t,start,Math.min(1,start+Math.min(b-a,3.0/duration)));};
 const at=(phrase:string,fallback:number)=>cue(phrase,fallback)*duration;
 const add=(id:string,text:string,tx:number,ty:number,start:number,x:number,y:number,hold=3.7,visible=true,endLimit=duration-.2)=>{
  const width=text.length*17+40;
  entries.push({id,text,tx,ty,start:Math.max(.2,start),end:Math.min(start+hold,endLimit),x:Math.max(width/2+30,Math.min(1890-width/2,x)),y:Math.max(205,Math.min(960,y)),visible});
 };
 const bh=(tx:number,ty:number,r:number,start:number,x=tx+270,y=ty-r-95,text='Black hole')=>add('black-hole',text,tx+r*.72,ty-r*.72,start,x,y);
 switch(n){
 case 1:
  add('star','Star',290,305,.6,290,225);add('planet','Planet',1620,770,1.9,1620,695);
  bh(1140,540,155,at('black hole',.64),1420,300);break;
 case 2:{
  const q=phase(t,.08,.94),px=320+q*120,py=800-q*35;
  // Left-side edge of this background planet remains outside Cappy's body.
  add('planet','Planet',px-63,py,1.2,160,720,3.4);
  bh(1450,450,145,3.7,1690,230);break;
 }
 case 3:
  add('star','Massive star',990,330,at('massive star',.08),990,235);
  add('fusion','Fusion core',990,460,at('nuclear fusion',.35),1340,375);break;
 case 4:{
  const collapse=action('core collapses',.32,.56),blast=action('supernova',.57,.9),r=mix(210,65,collapse);
  add('star','Massive star',970,535-r,.6,650,275,3.6,blast<.15);
  add('collapse','Collapsing core',970,535,at('core collapses',.32),1320,300,3.5,blast<.25);
  const start=Math.max(duration*.73,at('black hole',.82));bh(970,535,70+blast*15,start,1270,325);break;
 }
 case 5:{
  const compress=action('Pack enough mass',.05,.65),horizon=action('event horizon',.52,.9),hr=mix(30,145,horizon);
  add('matter','Matter',960+mix(290,38,compress)*.5,535,.5,1330,370,3.5,horizon<.15);
  const px=960+Math.cos(sec*.3)*510,py=535+Math.sin(sec*.3)*300;
  add('orbiting-body','Orbiting body',px,py-32,2,px,py-110,4);
  add('horizon','Event horizon',960+hr*.707,535-hr*.707,at('event horizon',.52)+1.2,1300,275,3.7,horizon>.05);break;
 }
 case 6:{
  const change=action('same',.3,.62),theta=-1+sec*.42,px=960+Math.cos(theta)*540,py=535+Math.sin(theta)*310;
  const changeStart=at('same',.3),changeEnd=Math.min(duration,changeStart+Math.min(.32*duration,3.0));
  add('sun','Sun',960,535-mix(120,50,change),at('Sun',.3),960,310,4,change<.15,changeStart+.6);
  add('earth','Earth',px,py-43,at('Earth’s',.53),py<330?px+220:px,py<330?Math.max(230,py+50):py-125,4.5);
  add('earth-late','Earth',px,py-43,at('planet',.8),py<330?px+220:px,py<330?Math.max(230,py+50):py-125,3.6);
  add('same-mass','Same-mass black hole',995,500,changeEnd+.15,1050,330,4.2,change>.97);break;
 }
 case 7:
  bh(1040,535,230,.7,1370,225);
  add('horizon','Event horizon',1040+235*.707,535-235*.707,at('event horizon',.04)+4.1,1450,290);
  add('light','Light path',970,535,at('even light',.58),690,620,3.4);break;
 case 8:{
  bh(980,540,130,.6,670,300);
  add('disk','Accretion disk',1260,465,at('accretion disk',.3),1450,350);
  const jets=action('jets',.7,.96);
  add('jets','Jets',1045,230,at('jets',.7)+.7,1300,230,3.4,jets>.1);break;
 }
 case 9:{
  const align=action('bends',.1,.68),sx=mix(680,1050,align);
  add('background-star','Star behind black hole',sx,335,.65,sx-110,225,3.7,align<.8);
  bh(1050,535,155,4.4,1410,325);
  add('lensed-image','Lensed starlight',1220,405,at('arcs',.4),1440,220,3.7);break;
 }
 case 10:
  add('earth','Earth',365,390,.65,365,285);
  add('observatories','Radio observatories',455,530,at('observatories',.3),660,720,3.7);
  add('shadow','Black-hole shadow',1160,405,at('shadow',.5),1400,300,3.8);break;
 case 11:{
  const fall=action('approaching',.08,.92),x=mix(440,1010,fall),y=mix(360,520,fall);
  add('traveler','Traveler',x-35,y-28,.7,x-70,y-125,4);
  bh(1320,560,150,4.8,1590,320);
  add('tides','Tidal stretching',x+40,y+20,at('tidal force',.38),x-40,y+230,3.5);break;
 }
 case 12:
  add('small-hole','Stellar-mass black hole',635,535,at('small black hole',.12),565,310,4.2);
  add('large-hole','Supermassive black hole',1510,280,at('supermassive',.25),1490,210,4.5);break;
 case 13:{
  const fall=action('distant observer',.07,.8),nearX=mix(790,1190,fall),fade=action('image fades away',.72,.98);
  add('far-clock','Distant clock',370,305,.7,370,220,4);
  add('falling-clock','Clock seen from afar',nearX,505,4.5,nearX,410,4.2,fade<.2);
  bh(1460,540,165,9,1670,300, 'Black hole');break;
 }
 case 14:{
  const cross=action('crossing can happen',.12,.83),x=mix(550,1260,cross),clockX=mix(540,1250,cross);
  add('traveler','Infalling traveler',x-18,435,.7,x-30,300,3.8);
  add('local-clock','Local clock',clockX,778,4.6,clockX,885,3.8);
  add('horizon','Event horizon',975,540,at('horizon',.5),1400,270,3.7);
  add('outside-receiver','Outside receiver',432,265,at('sending a message',.57),430,205,3.4);
  // The co-moving gold dot is not a physical outgoing photon trajectory.
  // Leave it unlabeled rather than misidentify it as a planet or light ray.
  break;
 }
 case 15:
  add('paths','Inward paths',750,420,.8,540,280,3.7);
  add('classical-limit','Predicted singularity',960,750,at('singularity',.3),1280,820,3.7);
  add('unresolved','Unknown interior physics',960,750,at('understanding',.6)+1,1250,850,3.8);break;
 case 16:{
  const mergeStart=Math.min(.88,cue('orbit each other',.04)),mergeEnd=Math.max(mergeStart+.08,cue('Their merger',.55));
  const merge=phase(t,mergeStart,mergeEnd),r=mix(280,0,merge),angle=sec*.9;
  const x=990+Math.cos(angle)*r,y=540+Math.sin(angle)*r*.6;
  add('pair','Orbiting black holes',x,y-94,1,990,235,4.2,merge<.85);
  add('waves','Gravitational waves',1450,680,at('gravitational waves',.45),1490,850,3.8);
  add('remnant','Merged black hole',1070,455,Math.max(duration*.84,at('merger',.6)+2),1270,310,3.8,merge>.95);
  add('detector','Wave detector',1540,730,at('Detectors on Earth',.73)+.65,1540,930,3.6);break;
 }
 case 17:{
  const zoom=action('supermassive',.3,.93),ox=mix(700,450,zoom),scale=mix(1,.55,zoom),right=mix(.25,1,zoom);
  add('star','Star',ox-240*scale,560-155*scale,.7,ox-240*scale,560-240*scale,3.5);
  add('stellar-hole','Stellar-mass black hole',ox+75*scale,560-75*scale,at('Stellar-mass',.1),ox+120,300,4);
  add('supermassive','Supermassive black hole',1390+105*right,540-105*right,at('Supermassive',.3)+1.7,1440,255,4.5,phase(t,.25,.55)>.3);
  add('intermediate','Intermediate-mass candidates',825,798,at('between these categories',.75)+.5,825,930,3.5,action('between these categories',.75,.91)>.1);break;
 }
 case 18:{
  const feed=action('gas',.1,.85),rr=mix(500,170,feed),angle=feed*3+Math.max(0,sec-at('gas',.1))*.3;
  add('gas','Orbiting gas',990+Math.cos(angle)*rr,535+Math.sin(angle)*rr*.52,.7,1490,290,3.8);
  bh(990,535,mix(85,145,feed),4.8,1270,325);
  add('seeds','Possible seeds',530,860,at('seeds',.7)+.8,560,945,3.5,action('seeds',.7,.97)>.1);break;
 }
 case 19:{
  const orbit=action('stars',.03,.96),rx=230,ry=120,c=Math.sqrt(rx*rx-ry*ry),e=c/rx,mean=-1+sec*.58;let E=mean;
  for(let j=0;j<7;j++)E-=(E-e*Math.sin(E)-mean)/(1-e*Math.cos(E));
  const lx=-c+Math.cos(E)*rx,ly=Math.sin(E)*ry,rot=-25*Math.PI/180;
  const x=1000+lx*Math.cos(rot)-ly*Math.sin(rot),y=535+lx*Math.sin(rot)+ly*Math.cos(rot);
  add('star','Orbiting star',x,y-24,.8,710,255,4.5);
  add('telescope','Telescope',330,785,5.2,370,670,3.8);
  add('mass','Central dark mass',1000,505,at('mass concentrated',.4),1350,385,4);break;
 }
 case 20:{
  const move=action('orbits',.04,.97);
  bh(990,530,95,.6,990,310);
  [0,1,2].forEach(i=>{const rx=285+i*180,ry=150+i*115,angle=i*2+sec*(.48-i*.09),x=990+Math.cos(angle)*rx,y=530+Math.sin(angle)*ry;
   add('star-'+i,'Orbiting star',x,y-(20+i*9),3.2+i*3.8,y<320?x+280:x,y<320?270:y-120,3.6);
  });
  const transfer=action('transfer energy',.4,.85),meet=phase(transfer,0,.4),separate=phase(transfer,.4,1);
  const gasX=separate>0?(1-separate)**2*825+2*(1-separate)*separate*730+separate*separate*555:mix(760,825,meet);
  const gasY=separate>0?(1-separate)**2*635+2*(1-separate)*separate*510+separate*separate*645:mix(800,635,meet);
  add('gas-exchange','Gas',gasX,gasY,at('transfer energy',.4)+1,gasX-70,gasY+150,3.7,transfer>.05);
  break;
 }
 case 21:
  bh(990,535,170,.7,1310,300);
  add('predicted-radiation','Predicted Hawking radiation',1060,315,at('Hawking radiation',.35),1050,220,4.2);break;
 case 22:{
  const age=action('slow',.07,.96);
  bh(1050,490,mix(175,166,age),.7,1340,265);
  add('clock','Time (schematic)',400,343,4.8,400,250,3.8);
  add('timeline','Compressed timeline',mix(300,1600,age),845,at('vastly longer',.3),1180,955,4.2);
  add('smaller-hole','Smaller black hole',1570,450,at('Smaller black holes',.53)+1.2,1550,300,3.8,action('Smaller black holes',.53,.84)>.15);break;
 }
 case 23:{
  const observe=action('Stellar orbits',.06,.56),angle=mix(-10,-32,observe)*Math.PI/180;
  const tx=400+(115*Math.cos(angle)+10*Math.sin(angle))*1.05,ty=600+(115*Math.sin(angle)-10*Math.cos(angle))*1.05;
  add('telescope','Telescope',tx,ty,.7,415,390,4);
  add('detector','Gravitational-wave detector',1330,660,5.1,1450,820,4.2);
  add('hole','Black-hole model',1045,275,at('consistent story',.5)+1.4,1280,220,3.8,action('consistent story',.5,.96)>.15);break;
 }
 case 24:
  // Outro's planet and hole form a decorative host backdrop; identifying them
  // here would compete with the like/subscribe/question/comment interaction.
  break;
 }
 return entries;
}

export const SpaceLabels=(props:Props)=>{
 const seconds=props.frame/props.fps;
 const active=getSpaceLabels(props).filter(e=>e.visible&&seconds>=e.start&&seconds<e.end).slice(0,3);
 // If two pill rectangles approach, keep targets exact and move only the pill.
 const placed:{x:number;y:number;width:number}[]=[];
 const surfaceId=`${props.sceneId}-label-surface`;
 return <g pointerEvents="none"><defs><linearGradient id={surfaceId} x1="0" y1="0" x2="0" y2="1"><stop stopColor="#25445c"/><stop offset="1" stopColor="#13293f"/></linearGradient></defs>{active.map(e=>{
  const width=e.text.length*17+40;let y=e.y;
  for(let attempt=0;attempt<4;attempt++){
   if(!placed.some(p=>Math.abs(p.x-e.x)<(p.width+width)/2+20&&Math.abs(p.y-y)<78))break;
   y=y+84<970?y+84:y-84;
  }
  placed.push({x:e.x,y,width});
  const opacity=ease((seconds-e.start)/.25)*ease((e.end-seconds)/.4),edge=y+(e.ty>=y?31:-31);
  return <g key={e.id} opacity={opacity}>
   <path d={`M${e.x} ${edge}Q${e.x} ${(edge+e.ty)/2} ${e.tx} ${e.ty}`} stroke="#a5d3d5" strokeWidth="2.5" fill="none" opacity=".85"/>
   <circle cx={e.tx} cy={e.ty} r="8" fill="#a9e4dc" opacity=".16"/>
   <circle cx={e.tx} cy={e.ty} r="4" fill="#ccf3e4"/>
   <rect x={e.x-width/2} y={y-25} width={width} height="62" rx="24" fill="#030e20" opacity=".24"/>
   <rect x={e.x-width/2} y={y-31} width={width} height="62" rx="24" fill={`url(#${surfaceId})`} fillOpacity=".98" stroke="#8db7c4" strokeOpacity=".8" strokeWidth="1.7"/>
   <path d={`M${e.x-width/2+24} ${y-28}H${e.x+width/2-24}`} stroke="#e8f8ed" strokeWidth="1.5" opacity=".22"/>
   <text x={e.x} y={y+1} dominantBaseline="middle" textAnchor="middle" fontFamily="Arial, Helvetica, sans-serif" fontWeight="600" fontSize="32" fill="#fff1d2">{e.text}</text>
  </g>;
 })}</g>;
};
