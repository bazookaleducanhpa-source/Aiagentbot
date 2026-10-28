import React from 'react';

type Props={sceneId:string;frame:number;frames:number;fps:number};
type Kind='tumor'|'immune'|'healthy';
const colors={tumor:['#e2b8f5','#a071c2','#67418f'],immune:['#baf2e3','#43baa9','#187f82'],healthy:['#e5f5cf','#a4cf91','#608d75']} as const;
const clamp=(n:number)=>Math.max(0,Math.min(1,n));
const ease=(n:number)=>{const p=clamp(n);return p*p*(3-2*p);};
const phase=(p:number,a:number,b:number)=>ease((p-a)/(b-a));
const lerp=(a:number,b:number,p:number)=>a+(b-a)*p;
const TAU=Math.PI*2;

// A deforming membrane, not a rigid silhouette translated back and forth.
function membrane(r:number,t:number,seed:number,stretch=0){
 const pts=Array.from({length:18},(_,i)=>{const a=i/18*TAU;
 const d=r*(1+.035*Math.sin(a*3+t*.63+seed)+.023*Math.sin(a*5-t*.42+seed));
 return [Math.cos(a)*d*(1+stretch*.14),Math.sin(a)*d*(1-stretch*.09)];});
 const mid=(a:number[],b:number[])=>[(a[0]+b[0])/2,(a[1]+b[1])/2];
 const start=mid(pts[17],pts[0]);
 return `M${start[0]},${start[1]} `+pts.map((pt,i)=>{const next=mid(pt,pts[(i+1)%18]);return `Q${pt[0]},${pt[1]} ${next[0]},${next[1]}`;}).join(' ')+'Z';
}

function Cell({x,y,r,kind,t,id,seed=0,damage=0,stretch=0,defense=0,opacity=1}:{x:number;y:number;r:number;kind:Kind;t:number;id:string;seed?:number;damage?:number;stretch?:number;defense?:number;opacity?:number}){
 const c=colors[kind],uid=id+'-'+seed;
 return <g transform={`translate(${x} ${y})`} opacity={opacity}>
  <defs><radialGradient id={uid} cx="34%" cy="28%" r="78%"><stop stopColor={c[0]}/><stop offset=".62" stopColor={c[1]}/><stop offset="1" stopColor={c[2]}/></radialGradient></defs>
  <ellipse cy={r*.86} rx={r*.78} ry={r*.19} fill="#23364e" opacity=".11"/>
  <path d={membrane(r,t,seed,stretch)} fill={`url(#${uid})`} stroke={c[2]} strokeWidth="8" opacity={1-damage*.87}/>
  <path d={membrane(r*.91,t,seed,stretch)} fill="none" stroke={c[0]} strokeWidth="5" opacity={(1-damage)*.65}/>
  <g opacity={1-damage}>
   <ellipse cx={-r*.17} cy={r*.04} rx={r*.33} ry={r*.29} fill={c[2]} opacity=".67"/>
   <ellipse cx={-r*.22} cy={-r*.02} rx={r*.24} ry={r*.2} fill={c[0]} opacity=".32"/>
   <circle cx={-r*.12} cy={r*.07} r={r*.1} fill={c[2]}/>
   {Array.from({length:5},(_,i)=>{const a=i*1.17+.5;const ox=Math.cos(a)*r*.63,oy=Math.sin(a)*r*.6;return <g key={i} transform={`translate(${ox} ${oy}) rotate(${i*53})`}>
    <rect x={-r*.15} y={-r*.055} width={r*.3} height={r*.11} rx={r*.055} fill={c[0]} opacity=".7"/>
    <path d={`M${-r*.1},0 Q${-r*.04},${-r*.07} 0,0 T${r*.1},0`} fill="none" stroke={c[2]} strokeWidth="3" opacity=".7"/>
   </g>;})}
   {Array.from({length:11},(_,i)=><circle key={i} cx={Math.cos(i*2.4)*r*(.3+(i%3)*.17)} cy={Math.sin(i*2.4)*r*(.3+(i%3)*.17)} r={3+i%3} fill={c[0]} opacity=".6"/>)}
  </g>
  {defense>0&&<path d={membrane(r+18,t,seed)} fill="none" stroke="#ecffd9" strokeWidth={8+defense*8} opacity={defense*.85}/>}
  {damage>0&&Array.from({length:10},(_,i)=>{const a=i/10*TAU;const rr=r*(1+damage*.65);return <path key={i} d={`M${Math.cos(a-.12)*rr},${Math.sin(a-.12)*rr} Q${Math.cos(a)*rr*1.06},${Math.sin(a)*rr*1.06} ${Math.cos(a+.12)*rr},${Math.sin(a+.12)*rr}`} fill="none" stroke={c[1]} strokeWidth={10*(1-damage*.55)} opacity={damage*(1-damage*.65)} strokeLinecap="round"/>;})}
 </g>;
}

function Virus({x,y,r=26,opacity=1,angle=0}:{x:number;y:number;r?:number;opacity?:number;angle?:number}){
 return <g transform={`translate(${x} ${y}) rotate(${angle})`} opacity={opacity}>
  {Array.from({length:9},(_,i)=>{const a=i/9*TAU;return <g key={i}><path d={`M${Math.cos(a)*r*.7},${Math.sin(a)*r*.7} L${Math.cos(a)*r*1.27},${Math.sin(a)*r*1.27}`} stroke="#d96570" strokeWidth={r*.14} strokeLinecap="round"/><circle cx={Math.cos(a)*r*1.3} cy={Math.sin(a)*r*1.3} r={r*.16} fill="#fbb2a5"/></g>;})}
  <circle r={r} fill="#ef8b86" stroke="#c85c76" strokeWidth="3"/><ellipse cx={-r*.25} cy={-r*.32} rx={r*.48} ry={r*.28} fill="#ffd4b9" opacity=".7"/>
  <path d={`M${-r*.45},${r*.15} Q${-r*.1},${-r*.35} ${r*.13},${r*.16} T${r*.5},0`} fill="none" stroke="#a34b6e" strokeWidth="3" strokeLinecap="round"/>
 </g>;
}

function Fragment({x,y,i,opacity=1}:{x:number;y:number;i:number;opacity?:number}){
 return <g transform={`translate(${x} ${y}) rotate(${i*43})`} opacity={opacity}><path d="M-17 0 Q-11 -19 5 -13 Q22 -7 14 9 Q3 21 -12 12 Z" fill={i%2?'#c297dd':'#ecd2f4'} stroke="#9569b5" strokeWidth="3"/><circle cx="3" cy="-2" r="4" fill="#875aa9"/></g>;
}
function Signal({x,y,p,r=250,color='#f6d29a'}:{x:number;y:number;p:number;r?:number;color?:string}){
 return <g>{[0,.32,.64].map((offset,i)=>{const q=clamp((p-offset)/(1-offset));return <circle key={i} cx={x} cy={y} r={25+q*r} fill="none" stroke={color} strokeWidth={7*(1-q)} opacity={q>0?(1-q)*.6:0}/>;})}</g>;
}

// Material moves to a specific destination, assembles, then leaves it. The
// same pieces persist throughout the action instead of appearing as a flash.
function Assembly({x,y,q,index}:{x:number;y:number;q:number;index:number}){
 const gather=phase(q,0,.48),close=phase(q,.38,.8);
 return <g transform={`translate(${x} ${y})`} opacity={phase(q,0,.08)}>
  {[0,1,2,3,4,5].map(i=>{const a=i/6*TAU,rr=lerp(63,23,gather);return <path key={i} d={`M${Math.cos(a-.19)*rr} ${Math.sin(a-.19)*rr} Q${Math.cos(a)*rr*1.06} ${Math.sin(a)*rr*1.06} ${Math.cos(a+.19)*rr} ${Math.sin(a+.19)*rr}`} stroke="#ed9b96" fill="none" strokeWidth="9" strokeLinecap="round" opacity={1-close}/>;})}
  <path d={`M${-35+gather*23} 2Q-7 -17 2 0T14 0`} stroke="#b96285" strokeWidth="5" strokeLinecap="round" fill="none" opacity={1-close}/>
  <Virus x={0} y={0} r={23} opacity={close} angle={index*31}/>
 </g>;
}

function ContactArms({x,y,toX,toY,q}:{x:number;y:number;toX:number;toY:number;q:number}){
 const reach=phase(q,0,.6),join=phase(q,.45,1),tx=lerp(x,toX,reach),ty=lerp(y,toY,reach);
 return <g opacity={phase(q,0,.12)}>
  {[-1,1].map(side=><path key={side} d={`M${x} ${y+side*45} Q${lerp(x,toX,.5)} ${y+side*(95-join*35)} ${tx} ${ty+side*(48-join*33)}`} fill="none" stroke="#76ccbd" strokeWidth="17" strokeLinecap="round"/>)}
  <ellipse cx={toX} cy={toY} rx={12+join*10} ry={45-join*20} fill="#c2efdb" opacity={join}/>
 </g>;
}
function Tissue({t,id}:{t:number;id:string}){
 return <g opacity=".28">{[0,1,2,3,4].map(i=><Cell key={i} id={id+'bg'} x={250+i*350} y={i%2?180:880} r={85+i%2*35} kind="healthy" t={t} seed={i}/>)}</g>;
}

/** Continuous scene-length causal rigs. Parent provides scene-local frame. */
export const ContinuousBiology=({sceneId,frame,frames,fps}:Props)=>{
 const p=clamp(frame/Math.max(1,frames-1)),t=frame/fps,id='bio-'+sceneId;
 const cell=(x:number,y:number,r:number,kind:Kind,seed:number,extra:Partial<React.ComponentProps<typeof Cell>>={})=><Cell key={seed} id={id} x={x} y={y} r={r} kind={kind} seed={seed} t={t} {...extra}/>;
 const tumorX=1030,tumorY=530;
 const entry=phase(p,.03,.33),replication=phase(p,.34,.68),lysis=phase(p,.7,.98);
 const viralProcess=(r=205,die=true)=><g>
  {cell(tumorX,tumorY,r,'tumor',10,{damage:die?lysis:0})}
  <Virus x={lerp(330,tumorX-35,entry)} y={lerp(360,tumorY+15,entry)} r={32} opacity={1-phase(p,.32,.43)}/>
  <path d={`M${tumorX-35} ${tumorY+15} C${tumorX+60} ${tumorY-100} ${tumorX-120} ${tumorY-115} ${tumorX-75} ${tumorY+10}`} stroke="#f2b2a5" fill="none" strokeWidth="8" strokeLinecap="round" pathLength="1" strokeDasharray="1" strokeDashoffset={1-phase(p,.3,.47)} opacity={phase(p,.28,.35)*(1-phase(p,.59,.72))}/>
  {Array.from({length:9},(_,i)=>{const a=i*2.4,spread=die?lysis:0,assemble=phase(p,.36+i*.023,.55+i*.023);return <Assembly key={i} x={tumorX+Math.cos(a)*(65+replication*r*.35+spread*300)} y={tumorY+Math.sin(a)*(65+replication*r*.35+spread*240)} q={assemble} index={i}/>;})}
  {die&&Array.from({length:8},(_,i)=><Fragment key={i} i={i} x={tumorX+Math.cos(i*.8)*(r+lysis*180)} y={tumorY+Math.sin(i*.8)*(r+lysis*160)} opacity={lysis}/>) }
 </g>;

 let content:React.ReactNode;
 switch(sceneId){
 case 'scene-03': {
  const join=phase(p,.06,.8),surgery=phase(p,.3,.6),medicine=phase(p,.6,.95);
  content=<g>
   <path d="M390 620 C650 820 760 820 970 620 S1350 430 1550 620" fill="none" stroke="#b6c9d6" strokeWidth="32" strokeLinecap="round" pathLength="1" strokeDasharray="1" strokeDashoffset={1-join}/>
   <ellipse cx="400" cy="620" rx="180" ry="55" fill="#d5e8dc" stroke="#8fb3ab" strokeWidth="8"/>
   <Virus x={370} y={420} r={65}/>{cell(500,510,65,'tumor',71)}
   <g transform={`translate(970 ${lerp(820,490,surgery)})`} opacity={surgery}>
    <rect x="-170" y="80" width="340" height="90" rx="40" fill="#d2e8ea" stroke="#7ea7b6" strokeWidth="9"/>
    <path d="M-125 45 Q0 -100 125 45" fill="#82b4b6" stroke="#5a8995" strokeWidth="9"/>
    <path d="M-85 10 Q0 -45 85 10" fill="none" stroke="#bde1d9" strokeWidth="10" strokeLinecap="round"/>
   </g>
   <g transform={`translate(1510 ${lerp(780,430,medicine)})`} opacity={medicine}>
    <path d="M0 -125 V-80 M-100 -80 H100" stroke="#739ba8" strokeWidth="12" strokeLinecap="round"/>
    <rect x="-85" y="-70" width="170" height="235" rx="38" fill="#e2efdc" stroke="#83b5ad" strokeWidth="8"/>
    <path d="M-60 65 Q0 40 60 65 V135 Q0 160 -60 135Z" fill="#e5c996"/>
    <path d="M0 168 V220 Q0 280 80 280" fill="none" stroke="#83b5ad" strokeWidth="8" strokeLinecap="round"/>
   </g>
  </g>;break;
 }
 case 'scene-22': {
  const select=phase(p,.06,.4),expand=phase(p,.38,.68),combine=phase(p,.65,.96);
  content=<g>
   {[0,1,2].map(i=>cell(440+i*135,410+i%2*180,100,'tumor',i,{damage:select*.83}))}
   {[0,1,2].map(i=><Virus key={i} x={lerp(240,440+i*135,phase(p,.02,.24))} y={lerp(180+i*70,410+i%2*180,phase(p,.02,.24))} r={27} opacity={1-select*.7}/>)}
   {cell(1070,480,125,'tumor',10,{defense:.28})}
   {cell(lerp(1070,1360,expand),lerp(480,380,expand),100,'tumor',11,{opacity:expand})}
   {cell(lerp(1070,1310,expand),lerp(480,690,expand),100,'tumor',12,{opacity:expand})}
   {[0,1,2].map(i=><g key={i} transform={`translate(${lerp(1750,1470-i*70,combine)} ${lerp(180+i*170,380+i*120,combine)})`} opacity={combine}>
    <path d="M0 40 V0 M0 0 Q-20 -12 -32 -38 M0 0 Q20 -12 32 -38" fill="none" stroke="#f0ce94" strokeWidth="15" strokeLinecap="round"/>
   </g>)}
   <Signal x={1370} y={490} p={phase(p,.77,1)} r={180} color="#f0ce94"/>
  </g>;break;
 }
 case 'scene-28': {
  const damage=phase(p,.12,.4),release=phase(p,.3,.63),recognize=phase(p,.59,.96);
  content=<g>
   {cell(520,510,180,'tumor',1,{damage:damage*.76})}
   {cell(520,820,78,'tumor',2)}
   {[0,1,2].map(i=><Virus key={i} x={480+i*45} y={470+i%2*65} r={24} opacity={1-damage*.5}/>)}
   {[0,1,2,3,4,5].map(i=><Fragment key={i} i={i} x={lerp(520+Math.cos(i)*100,900+i%3*60,release)} y={lerp(510+Math.sin(i)*100,420+Math.floor(i/3)*150,release)} opacity={phase(p,.15,.32)}/>)}
   <Signal x={800} y={510} p={phase(p,.35,.95)} r={430}/>
   {cell(lerp(1620,1230,recognize),520,155,'immune',3,{stretch:recognize*.5})}
   <ContactArms x={lerp(1620,1230,recognize)-100} y={520} toX={1010} toY={500} q={phase(p,.72,.98)}/>
  </g>;break;
 }
 case 'scene-01': {
  const reveal=phase(p,.22,.55),approach=phase(p,.48,.83),strike=phase(p,.82,1);
  content=<g>
   {cell(1080,530,190,'tumor',1)}
   <ellipse cx="1080" cy="530" rx="278" ry="250" fill="#69728c" opacity={.65*(1-reveal)}/>
   <Virus x={lerp(320,995,phase(p,.04,.34))} y={lerp(360,455,phase(p,.04,.34))} r={36} opacity={1-phase(p,.38,.53)}/>
   <Signal x={1080} y={530} p={phase(p,.3,.85)} color="#e7c6f5" r={410}/>
   {Array.from({length:5},(_,i)=><Fragment key={i} i={i} x={1080+Math.cos(i*1.2)*(170+reveal*110)} y={530+Math.sin(i*1.2)*(170+reveal*110)} opacity={reveal}/>) }
   {cell(lerp(250,825,approach),lerp(750,570,approach),100,'immune',2,{stretch:approach})}
   {cell(lerp(1660,1320,approach),lerp(280,450,approach),85,'immune',3)}
   {/* Hook stops at immune attention, without an assured successful attack. */}
   {cell(1430,740,95,'tumor',4)}
  </g>;break;
 }
 case 'scene-14': {
  const shrink=phase(p,.15,.68),recruit=phase(p,.3,.86);
  content=<g>
   <ellipse cx="500" cy="470" rx="230" ry="210" fill="#e8e3ef" fillOpacity=".3" stroke="#adb8cd" strokeWidth="12"/>
   <ellipse cx="1120" cy="470" rx="230" ry="210" fill="#e8e3ef" fillOpacity=".3" stroke="#adb8cd" strokeWidth="12" opacity={phase(p,.08,.3)}/>
   {cell(500,470,150,'tumor',1)}
   {cell(1120,470,100,'tumor',2,{opacity:phase(p,.08,.3)})}
   {/* Matched specimen views are observations, not a live virus-induced shrink. */}
   <g transform={`translate(${lerp(1700,1000,phase(p,.38,.68))} 760)`} opacity={phase(p,.38,.68)}>
    <ellipse rx="310" ry="150" fill="#eae1ef" stroke="#9eafc4" strokeWidth="12"/>
    {[-1,0,1].map(i=>cell(i*150,0,65,'tumor',30+i))}
    {Array.from({length:8},(_,i)=>cell(-230+i*65,i%2?75:-75,28,'immune',40+i,{opacity:phase(p,.55+i*.025,.73+i*.025)}))}
   </g>
   {sceneId==='scene-14'&&<g opacity={phase(p,.67,.87)}><rect x="1450" y="330" width="170" height="350" rx="60" fill="#bce9db" opacity=".25" stroke="#c1f0df" strokeWidth="7"/>{[0,1,2].map(i=>cell(1535,405+i*100,32,'immune',50+i))}</g>}
  </g>;break;
 }
 case 'scene-04': {
  const approach=phase(p,.04,.3),inject=phase(p,.3,.48),copy=phase(p,.5,.9);
  content=<g>
   {cell(1040,540,285,'healthy',0)}
   <Virus x={lerp(320,790,approach)} y={430} r={44} opacity={1-phase(p,.38,.55)}/>
   <path d="M790 430 C850 390 850 540 960 500 S1100 470 1160 560" fill="none" stroke="#e99396" strokeWidth="10" strokeLinecap="round" strokeDasharray="550" strokeDashoffset={550*(1-inject)} opacity={1-copy*.6}/>
   {Array.from({length:6},(_,i)=>{const a=i/6*TAU;const q=phase(p,.45+i*.035,.68+i*.035),leave=phase(p,.75+i*.015,.91+i*.015);return <g key={i}><circle cx={1040+Math.cos(a)*175} cy={540+Math.sin(a)*175} r={32} fill="#e6f7ca" stroke="#8cb88b" strokeWidth="5"/><Assembly x={1040+Math.cos(a)*(175+leave*45)} y={540+Math.sin(a)*(175+leave*45)} q={q} index={i}/></g>;})}
  </g>;break;
 }
 case 'scene-05': {
  const warn=phase(p,.18,.63),defend=phase(p,.45,.85),contact=phase(p,.03,.26),bounce=phase(p,.36,.66);
  content=<g>
   {cell(650,500,165,'healthy',0,{defense:warn})}
   {cell(1050,360,145,'healthy',1,{defense:defend})}
   {cell(1160,720,150,'healthy',2,{defense:defend})}
   <Signal x={650} y={500} p={warn} r={600} color="#dcf4ba"/>
   <Virus x={lerp(250,480,contact)-bounce*200} y={400-bounce*150} r={33}/>
   {cell(1570,510,155,'tumor',3)}
   <Virus x={lerp(1790,1550,phase(p,.55,.95))} y={lerp(270,500,phase(p,.55,.95))} r={28}/>
   {[0,1,2,3].map(i=><circle key={i} cx={lerp(720,1100,phase(p,.24+i*.04,.58+i*.04))} cy={lerp(500,370+i*100,phase(p,.24+i*.04,.58+i*.04))} r="9" fill="#e7f8be" opacity={warn*(1-defend)}/>)}
  </g>;break;
 }
 case 'scene-06': {
  const hit=phase(p,.08,.5),late=phase(p,.55,.94);
  content=<g>{[0,1,2,3].map(i=>{
   const x=480+i*340,y=i%2?640:420,vulnerable=i%2===0;
   return <g key={i}>
    {cell(x,y,130,'tumor',i,{damage:vulnerable?late*.82:0,defense:vulnerable?0:.4})}
    <Virus x={lerp(x-220,vulnerable?x:x-140,hit)-(vulnerable?0:late*130)} y={lerp(170,y,hit)-(vulnerable?0:late*100)} r={30} opacity={vulnerable?1-late*.7:1}/>
    {vulnerable&&[0,1,2,3].map(j=><Virus key={j} x={x+Math.cos(j*1.6)*(45+late*70)} y={y+Math.sin(j*1.6)*(45+late*70)} r={18} opacity={late}/>)}
   </g>;
  })}</g>;break;
 }
 case 'scene-07':content=viralProcess();break;
 case 'scene-08': {
  const dying=phase(p,.03,.4),release=phase(p,.3,.77),arrive=phase(p,.65,1);
  content=<g>{cell(1010,520,200,'tumor',1,{damage:dying})}
   {Array.from({length:14},(_,i)=>{const a=i*2.4,rr=lerp(80,380,release),collect=i%4===0?phase(p,.8,1):0;return <Fragment key={i} i={i} x={lerp(1010+Math.cos(a)*rr,640,collect)} y={lerp(520+Math.sin(a)*rr*.72,610,collect)} opacity={phase(p,.15,.43)*(1-collect*.75)}/>;})}
   <Signal x={1010} y={520} p={release} r={600}/>
   {cell(lerp(230,610,arrive),lerp(780,620,arrive),130,'immune',2,{stretch:arrive})}
   {cell(lerp(1700,1420,arrive),lerp(220,420,arrive),95,'immune',3)}
   <ContactArms x={lerp(230,610,arrive)+80} y={lerp(780,620,arrive)} toX={800} toY={600} q={phase(p,.78,1)}/>
  </g>;break;
 }
 case 'scene-09': {
  const pickup=phase(p,.02,.3),travel=phase(p,.31,.66),present=phase(p,.62,.84),respond=phase(p,.82,1),cx=lerp(580,1040,travel);
  content=<g>
   {cell(cx,540,170,'immune',1,{stretch:pickup*(1-travel)})}
   <path d={`M${cx-120} 445 Q${cx-290*pickup} 390 ${cx-205*pickup} 525 Q${cx-270*pickup} 680 ${cx-110} 650`} fill="none" stroke="#7ad8bc" strokeWidth="24" strokeLinecap="round" opacity={1-travel}/>
   {Array.from({length:4},(_,i)=><Fragment key={i} i={i} x={lerp(330+i*33,cx-50+i*20,pickup)} y={lerp(440+i*67,520+i*12,pickup)} opacity={1-phase(p,.38,.58)}/>) }
   <Fragment i={4} x={cx+lerp(-40,155,phase(p,.45,.74))} y={lerp(545,490,phase(p,.45,.74))} opacity={phase(p,.43,.55)}/>
   {cell(lerp(1600,1350,phase(p,.56,.86)),520,120,'immune',2,{defense:respond*.5})}
   <ContactArms x={lerp(1600,1350,phase(p,.56,.86))-70} y={510} toX={cx+lerp(-40,155,phase(p,.45,.74))} toY={490} q={present}/>
   {[0,1,2].map(i=>{const transfer=phase(p,.76+i*.035,.86+i*.035);return <circle key={i} cx={lerp(1205,1350,transfer)} cy={lerp(490,520+i*20,transfer)} r={6} fill="#b8edcf" opacity={transfer*(1-phase(p,.94,1))}/>;})}
   {[0,1].map(i=>cell(lerp(1460,1630,respond),lerp(520,300+i*440,respond),70,'immune',7+i,{opacity:respond}))}
  </g>;break;
 }
 case 'scene-10': {
  const move=phase(p,.1,.68),suppress=phase(p,.42,.85);
  content=<g>{cell(1090,530,210,'tumor',1)}
   <ellipse cx="1090" cy="530" rx="315" ry="295" fill="#bd9bda" opacity={suppress*.2}/>
   {cell(lerp(290,740,move),540,125,'immune',2,{opacity:1-suppress*.5})}
   <path d="M800 290 C710 400 710 670 815 780" stroke="#b59cce" strokeWidth={15+suppress*20} fill="none" strokeLinecap="round" opacity={suppress}/>
   {cell(lerp(1650,1430,move),360,105,'immune',3)}
   {[0,1,2].map(i=><Virus key={i} x={lerp(1250+i*40,1430,phase(p,.4,.87))} y={lerp(140+i*60,360,phase(p,.4,.87))} r={26} opacity={1-phase(p,.78,1)}/>)}
   {cell(1490,780,90,'tumor',4)}
  </g>;break;
 }
 case 'scene-20': {
  const arrive=phase(p,.04,.45),detour=phase(p,.45,.86);
  content=<g>
   {cell(1230,500,170,'tumor',1)}{cell(1590,760,105,'tumor',2)}
   {[0,1,2,3].map(i=><path key={i} d={`M${900+i*37} 190 C${730+i*35} 360 ${1030+i*20} 550 ${870+i*35} 870`} fill="none" stroke={i%2?'#c6a6bc':'#e3c1c5'} strokeWidth="28" strokeLinecap="round" opacity=".8"/>)}
   {[0,1,2,3,4,5].map(i=><Virus key={i} x={lerp(250+i*50,800-i%2*45,arrive)+(i===0?detour*360:-detour*70)} y={lerp(300+i*82,340+i*58,arrive)+(i===0?-Math.sin(detour*Math.PI)*220:detour*30)} r={26} opacity={i===0?1:1-detour*.3}/>)}
   <path d="M1390 480 Q1630 440 1660 660" stroke="#b3c4ce" strokeWidth="17" strokeDasharray="4 28" strokeLinecap="round" fill="none" opacity=".45"/>
  </g>;break;
 }
 case 'scene-21': {
  const clear=phase(p,.12,.58),inflame=phase(p,.55,.96);
  content=<g>
   {cell(700,530,180,'immune',1,{stretch:clear})}
   {[0,1,2,3,4].map(i=><Virus key={i} x={lerp(270+i*50,700,clear)} y={lerp(250+i*120,530,clear)} r={30} opacity={1-phase(p,.48,.69)}/>)}
   {cell(1330,500,170,'healthy',2,{damage:inflame*.2})}
   <Signal x={1000} y={520} p={inflame} r={530} color="#eeb293"/>
   {[0,1,2,3,4].map(i=><circle key={i} cx={lerp(750,1250+i*35,inflame)} cy={lerp(510,330+i*90,inflame)} r={10+inflame*9} fill="#f2be8e" opacity={inflame*.65}/>)}
   {cell(lerp(1740,1530,inflame),lerp(750,650,inflame),100,'immune',3,{opacity:.5+inflame*.5})}
  </g>;break;
 }
 default:return null;
 }
 return <g><Tissue t={t} id={id}/>{content}</g>;
};
