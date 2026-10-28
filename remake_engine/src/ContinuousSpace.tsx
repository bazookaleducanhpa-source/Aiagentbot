import React from 'react';
import {staticFile} from 'remotion';

type Word={text:string;start:number;end:number};
type Props={sceneId:string;frame:number;frames:number;fps:number;words?:Word[];backgroundFile?:string;backgroundSeconds?:number};
const TAU=Math.PI*2;
const clamp=(x:number)=>Math.max(0,Math.min(1,x));
const smooth=(x:number)=>{x=clamp(x);return x*x*(3-2*x)};
const phase=(t:number,a:number,b:number)=>smooth((t-a)/(b-a));
// Integral of a smooth phase, used for clocks: reducing the rate must never
// accidentally reverse the hand as a multiplication by a changing rate would.
const integratedPhase=(t:number,a:number,b:number)=>{const span=b-a,q=clamp((t-a)/span);return span*(q*q*q-.5*q*q*q*q)+Math.max(0,t-b);};
const mix=(a:number,b:number,q:number)=>a+(b-a)*q;
const point=(a:[number,number],b:[number,number],c:[number,number],q:number)=>({x:(1-q)**2*a[0]+2*(1-q)*q*b[0]+q*q*c[0],y:(1-q)**2*a[1]+2*(1-q)*q*b[1]+q*q*c[1]});
const clean=(s:string)=>s.toLowerCase().replace(/[^a-z0-9]/g,'');

export function Star({x,y,r=80,id,color='gold',opacity=1,time=0}:{x:number;y:number;r?:number;id:string;color?:'gold'|'blue'|'red';opacity?:number;time?:number}){
 const colors=color==='blue'?['#f1fff7','#92e5ef','#5079d0']:color==='red'?['#fff1c2','#f8ab72','#b94e70']:['#fff8c5','#ffd078','#d97956'];
 return <g opacity={opacity} transform={`translate(${x} ${y})`}><defs>
  <radialGradient id={id} cx="37%" cy="34%" r="69%"><stop stopColor={colors[0]}/><stop offset=".48" stopColor={colors[1]}/><stop offset=".8" stopColor={colors[2]}/><stop offset="1" stopColor={colors[2]} stopOpacity=".78"/></radialGradient>
  <radialGradient id={id+'corona'}><stop offset=".25" stopColor={colors[0]} stopOpacity=".45"/><stop offset=".5" stopColor={colors[1]} stopOpacity=".29"/><stop offset=".72" stopColor={colors[2]} stopOpacity=".1"/><stop offset="1" stopColor={colors[2]} stopOpacity="0"/></radialGradient>
  <radialGradient id={id+'granule'} cx="34%" cy="28%"><stop stopColor={colors[0]} stopOpacity=".9"/><stop offset=".52" stopColor={colors[1]} stopOpacity=".6"/><stop offset="1" stopColor={colors[2]} stopOpacity=".08"/></radialGradient>
  <clipPath id={id+'clip'}><circle r={r*.95}/></clipPath>
 </defs>
 <circle r={r*1.95} fill={`url(#${id}corona)`}/>
 {[0,1,2,3,4,5].map(i=>{const a=i/6*TAU+.24,activity=(Math.sin(time*.45+i*1.7)+1)/2;return <path key={i} d={`M${Math.cos(a-.14)*r*.91} ${Math.sin(a-.14)*r*.91}Q${Math.cos(a)*r*(1.18+activity*.11)} ${Math.sin(a)*r*(1.18+activity*.11)} ${Math.cos(a+.14)*r*.91} ${Math.sin(a+.14)*r*.91}`} stroke={colors[1]} strokeWidth={r*.035} fill="none" opacity={.25+activity*.2}/>;})}
 <circle r={r} fill={`url(#${id})`}/>
 <g clipPath={`url(#${id}clip)`}>
  {Array.from({length:19},(_,i)=>{const a=i*2.399,timePhase=(time*.085+i*.127)%1,rr=r*(.16+(i%4)*.19),w=r*(.075+(i%3)*.016),h=r*.045;return <g key={i} transform={`rotate(${i*31}) translate(${Math.cos(a+time*.012)*rr} ${Math.sin(a+time*.012)*rr-r*timePhase*.12})`} opacity={Math.sin(timePhase*Math.PI)*.64}>
   <path d={`M${-w} 0C${-w*1.04} ${-h*.8} ${-w*.42} ${-h*1.1} 0 ${-h*.8}C${w*.65} ${-h*1.2} ${w*1.1} ${-h*.35} ${w} ${h*.2}C${w*.8} ${h*1.1} ${w*.1} ${h*.9} ${-w*.25} ${h*.72}C${-w*.9} ${h*.9} ${-w*1.1} ${h*.38} ${-w} 0Z`} fill={`url(#${id}granule)`}/>
   <path d={`M${-w*.55} ${-h*.2}Q${-w*.1} ${-h*.6} ${w*.52} ${-h*.22}`} stroke={colors[0]} strokeWidth={r*.008} fill="none" opacity=".45"/>
  </g>;})}
  {[0,1,2].map(i=><path key={i} d={`M${-r*.85} ${r*(.14+i*.17)}Q${-r*.3} ${r*(-.36+i*.17)} ${r*.2} ${r*(.04+i*.17)}T${r*.9} ${r*(-.03+i*.17)}`} stroke={colors[0]} strokeWidth={r*.018} fill="none" opacity=".12"/>)}
 </g>
 <path d={`M${-r*.83} ${-r*.22}A${r*.86} ${r*.86} 0 0 1 ${r*.28} ${-r*.82}`} stroke={colors[0]} strokeWidth={r*.026} opacity=".46" fill="none"/>
 <ellipse cx={-r*.24} cy={-r*.26} rx={r*.5} ry={r*.31} fill={colors[0]} opacity=".1"/>
 </g>;
}
function Hole({x,y,r=125,disk=0,id,time=0}:{x:number;y:number;r?:number;disk?:number;id:string;time?:number}){
 const ribbon=(outer:number,inner:number)=>`M${-r*outer} 0A${r*outer} ${r*outer*.3} 0 1 0 ${r*outer} 0A${r*outer} ${r*outer*.3} 0 1 0 ${-r*outer} 0M${-r*inner} 0A${r*inner} ${r*inner*.3} 0 1 1 ${r*inner} 0A${r*inner} ${r*inner*.3} 0 1 1 ${-r*inner} 0Z`;
 return <g transform={`translate(${x} ${y})`}>
  <defs><radialGradient id={id+'halo'}><stop offset=".48" stopColor="#050716" stopOpacity="0"/><stop offset=".64" stopColor="#e8a76e" stopOpacity=".16"/><stop offset=".77" stopColor="#f6cc91" stopOpacity=".4"/><stop offset="1" stopColor="#9d80c9" stopOpacity="0"/></radialGradient>
   <linearGradient id={id+'disk'} x1=".08" x2=".9" y1=".05" y2=".9"><stop stopColor="#6b526e"/><stop offset=".2" stopColor="#c27962"/><stop offset=".39" stopColor="#f0ac5e"/><stop offset=".56" stopColor="#ffe0a0"/><stop offset=".7" stopColor="#fff2c8"/><stop offset=".87" stopColor="#d39e85"/><stop offset="1" stopColor="#7e789e"/></linearGradient>
   <linearGradient id={id+'sheen'} x1="0" y1="0" x2=".8" y2="1"><stop stopColor="#fff5d5" stopOpacity="0"/><stop offset=".46" stopColor="#ffd58b" stopOpacity=".22"/><stop offset=".72" stopColor="#fff6ce" stopOpacity=".9"/><stop offset="1" stopColor="#f2bb83" stopOpacity=".25"/></linearGradient>
   <mask id={id+'outside'} maskUnits="userSpaceOnUse" x={-r*3} y={-r*2} width={r*6} height={r*4}><rect x={-r*3} y={-r*2} width={r*6} height={r*4} fill="white"/><circle r={r*1.025} fill="black"/></mask>
   <clipPath id={id+'near'}><rect x={-r*3} y="0" width={r*6} height={r*2}/></clipPath>
  </defs>
  <circle r={r*1.8} fill={`url(#${id}halo)`}/>
  {disk>0&&<g opacity={disk}>
   <g transform="rotate(-14)">
    <path d={ribbon(2.81,1.43)} fill={`url(#${id}disk)`} fillRule="evenodd" opacity=".78"/>
    <path d={ribbon(2.64,1.49)} fill={`url(#${id}sheen)`} fillRule="evenodd" opacity=".66"/>
    <path d={ribbon(2.28,1.52)} fill="#f8cb88" fillRule="evenodd" opacity=".18"/>
    <ellipse rx={r*2.72} ry={r*.816} fill="none" stroke="#a8a0c1" strokeWidth={r*.014} opacity=".5"/>
    {Array.from({length:8},(_,i)=>{const a=time*(.18+i*.009)+i*.78,rr=r*(1.65+i%3*.34);return <path key={i} d={`M${Math.cos(a)*rr} ${Math.sin(a)*rr*.3}Q${Math.cos(a+.18)*rr} ${Math.sin(a+.18)*rr*.3} ${Math.cos(a+.36)*rr} ${Math.sin(a+.36)*rr*.3}`} stroke="#fff0bc" strokeWidth={r*.025} fill="none" opacity={.45-i%3*.09}/>;})}
   </g>
   <path d={`M${-r*1.57} 0C${-r*1.25} ${-r*2.33} ${r*1.25} ${-r*2.33} ${r*1.57} 0L${r*1.48} 0C${r*1.16} ${-r*2.12} ${-r*1.16} ${-r*2.12} ${-r*1.48} 0Z`} fill={`url(#${id}disk)`} opacity=".7"/>
   <path d={`M${-r*1.54} 0C${-r*1.23} ${-r*2.27} ${r*1.23} ${-r*2.27} ${r*1.54} 0`} fill="none" stroke="#f9d9a6" strokeWidth={r*.019} opacity=".5"/>
  </g>}
  <circle r={r} fill="#030611"/><circle r={r*1.025} fill="none" stroke={disk?'#f6d49e':'#aaa9c9'} strokeWidth={disk?3:1.8} opacity={disk?.62:.35}/>
  {disk>0&&<g mask={`url(#${id}outside)`} opacity={disk} transform="rotate(-14)"><g clipPath={`url(#${id}near)`}>
   <path d={ribbon(2.7,1.43)} fill={`url(#${id}sheen)`} fillRule="evenodd" opacity=".67"/>
   <path d={`M${-r*2.4} 0A${r*2.4} ${r*.72} 0 0 0 ${r*2.4} 0`} fill="none" stroke="#ffe5af" strokeWidth={r*.028} opacity=".6"/>
  </g></g>}
 </g>;
}
function Planet({x,y,r=24,color='#68c9c5',earth=false}:{x:number;y:number;r?:number;color?:string;earth?:boolean}){
 const id=`planet-${Math.round(x)}-${Math.round(y)}-${r}`;
 const land='M-80-65Q-62-82-43-70Q-35-58-24-56L-11-18Q-16-2-40 10L-36 42Q-42 62-60 68L-75 25L-91-18ZM12-72Q45-82 66-45L82-8Q73 14 53 17L38 6L25 46Q10 50-2 31L6-3L-12-32Z';
 return <g transform={`translate(${x} ${y})`}><defs>
  <radialGradient id={id} cx="28%" cy="23%" r="86%"><stop stopColor={earth?'#b7dce6':'#d1e8d6'}/><stop offset=".28" stopColor={earth?'#4d9aba':color}/><stop offset=".63" stopColor={earth?'#285986':color}/><stop offset="1" stopColor="#111e36"/></radialGradient>
  <linearGradient id={id+'land'} x1=".05" y1=".15" x2=".9" y2=".85"><stop stopColor="#e0d5a0"/><stop offset=".35" stopColor="#a7be94"/><stop offset=".7" stopColor="#649589"/><stop offset="1" stopColor="#385e68"/></linearGradient>
  <linearGradient id={id+'shade'}><stop offset=".3" stopColor="#0b1730" stopOpacity="0"/><stop offset=".66" stopColor="#0b1730" stopOpacity=".14"/><stop offset="1" stopColor="#071127" stopOpacity=".85"/></linearGradient>
  <clipPath id={id+'clip'}><circle r={r}/></clipPath></defs>
  <circle r={r*1.08} fill="none" stroke="#a4d3dc" strokeWidth={r*.045} opacity=".38"/><circle r={r} fill={`url(#${id})`}/>
  <g clipPath={`url(#${id}clip)`}>
   {earth?<g transform={`scale(${r/100})`}>
    <path d={land} transform="translate(2 3)" fill="#194f6d" opacity=".55"/><path d={land} fill={`url(#${id}land)`} stroke="#cad2aa" strokeWidth=".8"/>
    <path d="M-68-53Q-54-64-41-48M25-54Q43-57 54-36M-59 28L-53 45M38-5L31 16" stroke="#d7d0a0" strokeWidth="3" fill="none" opacity=".5"/>
    <ellipse cx="66" cy="44" rx="7" ry="11" fill="#a1b99a"/><ellipse cx="-19" cy="-66" rx="4" ry="8" fill="#b6c5a4"/>
    <path d="M-93-35Q-55-55-12-30Q18-17 39-23M15-56Q52-66 90-30M-50 62Q-5 36 53 62" stroke="#dcebe6" strokeWidth="10" opacity=".24" fill="none"/>
    <path d="M-90-38Q-45-55-7-28M19-59Q55-63 85-32M-44 59Q0 42 48 60" stroke="#fff8e7" strokeWidth="4.5" opacity=".8" fill="none"/>
    <path d="M-20 79Q7 66 28 77" stroke="#dfe9e3" strokeWidth="6" opacity=".7" fill="none"/>
   </g>:<g opacity=".23"><path d={`M${-r} ${-r*.17}Q${-r*.4} ${-r*.4} ${r*.18} ${-r*.14}T${r} ${-r*.21}`} fill="none" stroke="#e8ebd3" strokeWidth={r*.11}/><path d={`M${-r} ${r*.36}Q${-r*.2} ${r*.1} ${r} ${r*.39}`} fill="none" stroke="#385b70" strokeWidth={r*.15}/></g>}
   <circle r={r} fill={`url(#${id}shade)`}/>
  </g>
  <path d={`M${-r*.83} ${-r*.36}A${r*.9} ${r*.9} 0 0 1 ${r*.03} ${-r*.91}`} fill="none" stroke="#f5e9c9" strokeWidth={r*.035} opacity=".65"/>
  <path d={`M${r*.72} ${r*.55}A${r*.91} ${r*.91} 0 0 0 ${r*.87} ${-r*.17}`} fill="none" stroke="#83c9dc" strokeWidth={r*.025} opacity=".5"/>
 </g>;
}
function Ray({a,b,c,q,color='#a1eee0',opacity=1}:{a:[number,number];b:[number,number];c:[number,number];q:number;color?:string;opacity?:number}){
 const tip=point(a,b,c,q);
 return <g opacity={opacity}><path d={`M${a[0]} ${a[1]}Q${b[0]} ${b[1]} ${c[0]} ${c[1]}`} pathLength="1" strokeDasharray="1" strokeDashoffset={1-q} stroke={color} strokeWidth="5" fill="none" strokeLinecap="round"/><circle cx={tip.x} cy={tip.y} r="9" fill={color}/></g>;
}
export function Astronaut({x,y,scale=1,stretch=0,angle=0}:{x:number;y:number;scale?:number;stretch?:number;angle?:number}){
 const id=`suit-${Math.round(x)}-${Math.round(y)}`;
 return <g transform={`translate(${x} ${y}) rotate(${angle}) scale(${scale*(1-stretch*.18)} ${scale*(1+stretch*.8)})`} strokeLinecap="round" strokeLinejoin="round">
  <defs><linearGradient id={id+'cloth'} x1="0" y1=".2" x2="1" y2=".8"><stop stopColor="#fff3d9"/><stop offset=".45" stopColor="#dce6df"/><stop offset="1" stopColor="#789aa9"/></linearGradient><radialGradient id={id+'visor'} cx="35%" cy="25%"><stop stopColor="#d7b58e"/><stop offset=".34" stopColor="#718d9b"/><stop offset=".7" stopColor="#314c6c"/><stop offset="1" stopColor="#15273f"/></radialGradient></defs>
  <rect x="-43" y="-8" width="86" height="85" rx="22" fill="#648291"/>
  <path d="M-25 80L-35 140M25 80L35 140M-36 12L-68 69M36 12L68 69" fill="none" stroke={`url(#${id}cloth)`} strokeWidth="23"/>
  <path d="M-31 108L-13 112M17 112L36 109M-61 46L-46 54M47 53L61 45" stroke="#6d8e9c" strokeWidth="5" fill="none"/>
  <path d="M-39 139L-29 142M29 142L40 140M-70 67L-64 72M64 72L70 67" stroke="#9db9bc" strokeWidth="13" fill="none"/>
  <rect x="-42" y="-12" width="84" height="105" rx="29" fill={`url(#${id}cloth)`} stroke="#9ab6bd" strokeWidth="5"/>
  <path d="M-31 2V63Q-29 77-18 78M34 4V68M-35 70Q0 83 35 70" fill="none" stroke="#8aa6b1" strokeWidth="3"/>
  <path d="M-27 1Q-20-8-8-8" fill="none" stroke="#fff6df" strokeWidth="4"/>
  <circle cy="-45" r="47" fill={`url(#${id}cloth)`} stroke="#a5c3c7" strokeWidth="6"/>
  <ellipse cy="-46" rx="38" ry="32" fill="#546f82"/><ellipse cy="-46" rx="34" ry="28" fill={`url(#${id}visor)`}/>
  <path d="M-25-55Q-4-75 21-58" stroke="#fff0cc" strokeWidth="5" opacity=".75" fill="none"/>
  <path d="M-23-42Q-15-49-8-48M21-38Q17-29 8-25" stroke="#a5dce3" strokeWidth="3" opacity=".75" fill="none"/>
  <path d="M-32-79Q-17-91 0-90" stroke="#fff8e8" strokeWidth="3" opacity=".8" fill="none"/>
  <rect x="-21" y="17" width="42" height="32" rx="9" fill="#678b9c" stroke="#bed1cc" strokeWidth="2"/>
  <rect x="-14" y="23" width="17" height="11" rx="3" fill="#b9d7cd"/><circle cx="11" cy="27" r="3" fill="#f4c38d"/><circle cx="11" cy="38" r="3" fill="#c5e5d2"/>
  <path d="M-8 49Q-18 58-7 64H14" fill="none" stroke="#9bb6b7" strokeWidth="4"/>
 </g>;
}
export function Clock({x,y,r=80,hand=0,id}:{x:number;y:number;r?:number;hand:number;id:string}){
 return <g transform={`translate(${x} ${y})`}>
  <defs><linearGradient id={id+'rim'} x1="0" y1="0" x2=".8" y2="1"><stop stopColor="#f0dfb7"/><stop offset=".32" stopColor="#afd0cd"/><stop offset=".65" stopColor="#567e95"/><stop offset="1" stopColor="#92bec9"/></linearGradient><radialGradient id={id+'face'} cx="35%" cy="28%"><stop stopColor="#385c78"/><stop offset=".65" stopColor="#203c58"/><stop offset="1" stopColor="#12243e"/></radialGradient></defs>
  <circle r={r} fill={`url(#${id}rim)`} stroke="#8bc7ce" strokeWidth="7"/>
  <circle r={r*.91} fill={`url(#${id}face)`} stroke="#153148" strokeWidth="3"/>
  <path d={`M${-r*.77} ${-r*.44}A${r*.89} ${r*.89} 0 0 1 ${r*.44} ${-r*.77}`} fill="none" stroke="#fff0cc" strokeWidth="3" opacity=".7"/>
  {[0,1,2,3,4,5,6,7,8,9,10,11].map(i=><path key={id+i} d={`M${Math.cos(i/12*TAU)*r*.78} ${Math.sin(i/12*TAU)*r*.78}L${Math.cos(i/12*TAU)*r*.88} ${Math.sin(i/12*TAU)*r*.88}`} stroke={i%3?'#a8d9d8':'#f4d8a5'} strokeWidth={i%3?3:4} strokeLinecap="round"/>)}
  <circle r={r*.69} fill="none" stroke="#8aafbd" strokeWidth="1" opacity=".14"/>
  <path d={`M2 3L${Math.sin(hand)*r*.66+2} ${-Math.cos(hand)*r*.66+3}`} stroke="#08172b" strokeWidth="9" opacity=".4" strokeLinecap="round"/>
  <path d={`M0 0L${Math.sin(hand)*r*.66} ${-Math.cos(hand)*r*.66}`} stroke="#f4cf9a" strokeWidth="7" strokeLinecap="round"/>
  <circle r="8" fill="#d9e7d5"/><circle cx="-2" cy="-2" r="3" fill="#fff5d8"/>
  <path d={`M${-r*.6} ${-r*.3}Q${-r*.2} ${-r*.63} ${r*.4} ${-r*.45}`} fill="none" stroke="#c7e2dd" strokeWidth={r*.075} opacity=".08"/>
 </g>;
}
function Waves({x,y,q,max=650,color='#87cbd8'}:{x:number;y:number;q:number;max?:number;color?:string}){
 return <g>{[0,.16,.32,.48].map((offset,i)=>{const v=clamp((q-offset)/(1-offset));return <ellipse key={i} cx={x} cy={y} rx={30+v*max} ry={18+v*max*.7} fill="none" stroke={color} strokeWidth={8*(1-v)+1} opacity={v>0?(1-v)*.55:0}/>;})}</g>;
}
function Telescope({x,y,angle=-25,scale=1}:{x:number;y:number;angle?:number;scale?:number}){
 const id=`scope-${Math.round(x)}-${Math.round(y)}`;
 return <g transform={`translate(${x} ${y}) scale(${scale})`}>
  <defs><linearGradient id={id+'barrel'} x1="0" y1="0" x2="0" y2="1"><stop stopColor="#f2e7c9"/><stop offset=".24" stopColor="#bcd8d4"/><stop offset=".55" stopColor="#83aebc"/><stop offset="1" stopColor="#42647f"/></linearGradient><radialGradient id={id+'glass'} cx="25%" cy="20%"><stop stopColor="#b2d9df"/><stop offset=".3" stopColor="#547e9e"/><stop offset=".75" stopColor="#233e5c"/><stop offset="1" stopColor="#0b1a32"/></radialGradient></defs>
  <path d="M0 30L-70 180M0 30L65 180M0 30V180" stroke="#779ba9" strokeWidth="15" strokeLinecap="round"/>
  <path d="M-3 44L-66 174M3 44L61 174" stroke="#c1d0c7" strokeWidth="4" strokeLinecap="round"/>
  <path d="M-44 125H40" stroke="#57778d" strokeWidth="6"/>
  <rect x="-20" y="17" width="40" height="28" rx="10" fill="#658b9d"/>
  <g transform={`rotate(${angle})`}>
   <rect x="-115" y="-55" width="230" height="90" rx="28" fill={`url(#${id}barrel)`}/>
   <rect x="-150" y="-30" width="40" height="40" rx="9" fill="#4b7089"/>
   <path d="M-142-21V1M-133-21V1" stroke="#8eafb8" strokeWidth="3"/>
   <path d="M-84-50V30M65-50V30" stroke="#5f859b" strokeWidth="11"/>
   <path d="M-84-48V27M65-48V27" stroke="#bad4d0" strokeWidth="3" opacity=".8"/>
   <path d="M-61-35H43" stroke="#f6efda" strokeWidth="7" opacity=".55" strokeLinecap="round"/>
   <ellipse cx="115" cy="-10" rx="16" ry="45" fill="#1b3453" stroke="#a2d1d3" strokeWidth="7"/>
   <ellipse cx="115" cy="-10" rx="12" ry="39" fill={`url(#${id}glass)`}/>
   <path d="M110-39Q104-16 110 6" stroke="#c3e5e4" strokeWidth="3" opacity=".65" fill="none"/>
   <circle cx="-14" cy="20" r="10" fill="#bdc9b7"/><circle cx="-14" cy="20" r="4" fill="#5b7d90"/>
  </g>
 </g>;
}

function GasTrail({cx,cy,base,q,outer,inner,turns,flatten=.32,color='#f2c896',width=5,angularOffset=0}:{cx:number;cy:number;base:number;q:number;outer:number;inner:number;turns:number;flatten?:number;color?:string;width?:number;angularOffset?:number}){
 const coords=(v:number)=>{const a=base+v*turns+angularOffset,r=mix(outer,inner,v);return [cx+Math.cos(a)*r,cy+Math.sin(a)*r*flatten]};
 const points=Array.from({length:17},(_,i)=>coords(Math.max(0,q-.18)+Math.min(q,.18)*i/16));
 const d=points.map((pt,i)=>`${i?'L':'M'}${pt[0]} ${pt[1]}`).join(' '),tip=coords(q);
 const ribbonId=`gas-ribbon-${cx}-${cy}-${base.toFixed(4).replace('.','-')}`;
 const edge=(side:number)=>points.map((pt,i)=>{const prev=points[Math.max(0,i-1)],next=points[Math.min(points.length-1,i+1)],dx=next[0]-prev[0],dy=next[1]-prev[1],len=Math.max(.01,Math.hypot(dx,dy)),w=width*(.18+Math.sin(i/16*Math.PI)*1.25);return [pt[0]-dy/len*w*side,pt[1]+dx/len*w*side]});
 const outline=[...edge(1),...edge(-1).reverse()].map((pt,i)=>`${i?'L':'M'}${pt[0]} ${pt[1]}`).join(' ')+'Z';
 return <g><defs><linearGradient id={ribbonId} x1="0" y1="0" x2="1" y2="1"><stop stopColor={color} stopOpacity=".1"/><stop offset=".55" stopColor={color} stopOpacity=".75"/><stop offset="1" stopColor="#ffe4b7"/></linearGradient></defs><path d={d} stroke={color} strokeWidth={width*4} fill="none" opacity=".07"/><path d={outline} fill={`url(#${ribbonId})`}/><path d={d} stroke={color} strokeWidth={width*.6} fill="none" opacity=".72"/><ellipse cx={tip[0]} cy={tip[1]} rx={width*1.7} ry={width*.9} fill="#f9deac" opacity=".9"/></g>;
}

function LightTrain({a,b,c,elapsed,color='#bde8dc',period=2.8}:{a:[number,number];b:[number,number];c:[number,number];elapsed:number;color?:string;period?:number}){
 return <g>{[0,1].map(i=>{const e=elapsed-i*period*.5;if(e<0)return null;const q=(e%period)/period,pt=point(a,b,c,q);return <g key={i} opacity={Math.sin(q*Math.PI)}><circle cx={pt.x} cy={pt.y} r="17" fill={color} opacity=".12"/><circle cx={pt.x} cy={pt.y} r="7" fill={color}/></g>;})}</g>;
}

/** Small irregular mass parcels: distinct from planets, with a consistent
 * upper-left key light. Their silhouette contracts with the matter itself. */
function MatterParcel({x,y,size=20,angle=0,tint='#b6a4d6',id}:{x:number;y:number;size?:number;angle?:number;tint?:string;id:string}){
 return <g transform={`translate(${x} ${y}) rotate(${angle}) scale(${size/20})`}><defs><radialGradient id={id} cx="27%" cy="22%" r="86%"><stop stopColor="#e9decc"/><stop offset=".38" stopColor={tint}/><stop offset="1" stopColor="#46516e"/></radialGradient></defs>
  <path d="M-21-3Q-20-18-6-19Q9-24 20-10Q27 3 14 16Q2 25-14 16Q-25 11-21-3Z" fill={`url(#${id})`}/>
  <path d="M-16-7Q-12-17 0-16" fill="none" stroke="#fff0d7" strokeWidth="2" opacity=".55"/>
  <path d="M-9 10Q2 17 12 8" fill="none" stroke="#48526b" strokeWidth="3" opacity=".35"/>
 </g>;
}

/** Scene-local cosmic causal animation. Cue matches use spoken word timings;
 * fallback fractions make previews deterministic before voice is available. */
export const ContinuousSpace=({sceneId,frame,frames,fps,words=[],backgroundFile,backgroundSeconds}:Props)=>{
 const seconds=frame/fps,duration=Math.max(1,frames/fps),t=clamp(frame/Math.max(1,frames-1));
 const bgTime=backgroundSeconds??seconds;
 const id='space-'+sceneId;
 const cue=(phrase:string,fallback:number)=>{
  const wanted=phrase.split(/\s+/).map(clean).filter(Boolean);
  const tokens=words.flatMap(w=>w.text.split(/\s+/).map(text=>({text:clean(text),start:w.start}))).filter(w=>w.text);
  const hits=tokens.flatMap((w,i)=>wanted.every((token,j)=>tokens[i+j]?.text===token)?[clamp((w.start+.15)/duration)]:[]);
  return hits.length?hits.reduce((a,b)=>Math.abs(a-fallback)<Math.abs(b-fallback)?a:b):fallback;
 };
 const action=(word:string,a:number,b:number)=>{const start=Math.min(.88,cue(word,a));return phase(t,start,Math.min(1,start+Math.min(b-a,3.0/duration)));};
 const elapsed=(phrase:string,fallback:number)=>Math.max(0,seconds-cue(phrase,fallback)*duration);
 const n=Number(sceneId.slice(-2));
 const star=(x:number,y:number,r:number,index=0,color:'gold'|'blue'|'red'='gold',opacity=1)=><Star x={x} y={y} r={r} id={id+'star'+index} color={color} opacity={opacity} time={seconds}/>;
 const hole=(x:number,y:number,r:number,disk=0,index=0)=><Hole x={x} y={y} r={r} disk={disk} id={id+'hole'+index} time={seconds}/>;
 let content:React.ReactNode=null;
 switch(n){
 case 1:{
  const bend=action('beam of light',.08,.7),caught=action('crosses a boundary',.35,.89);
  content=<g>{hole(1140,540,155,.45)}{star(290,350,40)}
   <Ray a={[300,350]} b={[950,240]} c={[1720,300]} q={bend}/>
   <Ray a={[300,350]} b={[830,610]} c={[1140,540]} q={caught} color="#edba9c" opacity={1-phase(caught,.9,1)*.8}/>
   <LightTrain a={[300,350]} b={[950,240]} c={[1720,300]} elapsed={elapsed('beam of light',.08)}/>
   <LightTrain a={[300,350]} b={[830,610]} c={[1140,540]} elapsed={elapsed('crosses a boundary',.35)} color="#edba9c"/>
   <Planet x={1620} y={805} r={32}/>
   <g opacity={action('escapes',.25,.4)}><path d="M1660 265L1720 300L1660 335" fill="none" stroke="#bde8dc" strokeWidth="5"/><circle cx="1720" cy="300" r={15+((elapsed('escapes',.25)%2)/2)*35} fill="none" stroke="#bde8dc" opacity={.5*(1-elapsed('escapes',.25)%2/2)}/></g>
   <circle cx="1140" cy="540" r="159" fill="none" stroke="#ddb499" strokeWidth="3" strokeDasharray="5 16" opacity={action('That boundary',.65,.8)*.65}/>
  </g>;break;
 }
 case 2:case 24:{
  const q=phase(t,.08,.94);
  content=<g>{hole(1450,450,145,.7)}
   {[0,1,2].map(i=><Ray key={i} a={[250,240+i*160]} b={[850,150+i*180]} c={[1250,250+i*190]} q={phase(q,i*.16,.65+i*.1)} opacity={.24} color={i%2?'#a8a0d8':'#73c9d1'}/>)}
   <Planet x={320+q*120} y={800-q*35} r={68}/>
  </g>;break;
 }
 case 3:{
  const balance=action('gravity',.1,.84),r=195;
  content=<g>{star(990,535,r)}
   {[0,1,2,3,4,5,6,7].map(i=>{const a=i/8*TAU,cycle=(elapsed('gravity',.1)*.46+i*.08)%1;const inner=110+cycle*110,outer=365-cycle*130;return <g key={i}>
    <path d={`M${990+Math.cos(a)*105} ${535+Math.sin(a)*105}L${990+Math.cos(a)*220} ${535+Math.sin(a)*220}`} stroke="#f3c792" strokeWidth="4" opacity=".35"/>
    <circle cx={990+Math.cos(a)*inner} cy={535+Math.sin(a)*inner} r="10" fill="#f4d69f" opacity={Math.sin(cycle*Math.PI)}/>
    <circle cx={990+Math.cos(a)*outer} cy={535+Math.sin(a)*outer} r="11" fill="#91b5db" opacity={Math.sin(cycle*Math.PI)}/>
    <path d={`M${990+Math.cos(a)*360} ${535+Math.sin(a)*360}L${990+Math.cos(a)*235} ${535+Math.sin(a)*235}`} stroke="#91b5db" strokeWidth="4" opacity=".3"/>
   </g>;})}
   <circle cx="990" cy="535" r="71" fill="#fff0c0" opacity=".5"/>
  </g>;break;
 }
 case 4:{
  const exhausted=action('no longer',.06,.31),collapse=action('core collapses',.32,.56),blast=action('supernova',.57,.9);
  content=<g>{star(970,535,mix(210,65,collapse),0,'red',1-blast)}
   {/* A cutaway makes loss of support and infall visible before ejecta leave.
       Layer boundaries shrink with the same body, preserving subject identity. */}
   <g opacity={(1-blast)*.85}>
    <defs><radialGradient id={id+'iron-core'} cx="32%" cy="28%"><stop stopColor="#f3d7aa"/><stop offset=".45" stopColor="#b298a4"/><stop offset="1" stopColor="#5d587e"/></radialGradient></defs>
    <path d={`M970 ${535-mix(190,59,collapse)}A${mix(190,59,collapse)} ${mix(190,59,collapse)} 0 0 1 970 ${535+mix(190,59,collapse)}Z`} fill="#a25e73" opacity=".45"/>
    {[.72,.48].map((factor,i)=><path key={'stratum'+i} d={`M970 ${535-mix(210,65,collapse)*factor}A${mix(210,65,collapse)*factor} ${mix(210,65,collapse)*factor} 0 0 1 970 ${535+mix(210,65,collapse)*factor}`} fill="none" stroke={i?'#bd9ca6':'#edb990'} strokeWidth={i?9:13} opacity=".8"/>)}
    <circle cx="970" cy="535" r={mix(49,17,collapse)} fill={`url(#${id}iron-core)`}/>
    {Array.from({length:8},(_,i)=>{const a=-Math.PI/2+i*Math.PI/7,q=collapse*collapse,rr=mix(158,27,q);return <MatterParcel key={'infall'+i} x={970+Math.cos(a)*rr} y={535+Math.sin(a)*rr} size={mix(8,4,collapse)} angle={i*43} id={id+'infall'+i} tint="#d8ac9a"/>;})}
   </g>
   {[0,1,2].map(i=>{const q=phase(blast,i*.1,.73+i*.1);return <ellipse key={'shock'+i} cx="970" cy="535" rx={90+q*750} ry={65+q*455} stroke={i%2?'#d3a3b4':'#f3cc9c'} strokeWidth={18*(1-q)+2} opacity={q>0?Math.sin(q*Math.PI)*.5:0} fill="none"/>;})}
   {Array.from({length:16},(_,i)=>{const a=i/16*TAU,q=phase(blast,i%3*.06,.8+i%3*.06),r=90+q*620;return <path key={'ejecta'+i} d={`M${970+Math.cos(a)*Math.max(90,r-130)} ${535+Math.sin(a)*Math.max(90,r-130)*.68}Q${970+Math.cos(a+.045)*(r-65)} ${535+Math.sin(a+.045)*(r-65)*.68} ${970+Math.cos(a)*r} ${535+Math.sin(a)*r*.68}`} stroke={i%2?'#ddab9d':'#bd9dcb'} strokeWidth={6+q*7} fill="none" opacity={Math.sin(q*Math.PI)*.5}/>;})}
   {[0,1,2,3,4,5].map(i=><circle key={i} cx={970+Math.cos(i*1.06)*50*(1-collapse)} cy={535+Math.sin(i*1.06)*50*(1-collapse)} r={14*(1-exhausted)+2} fill="#fff2bf" opacity={1-exhausted}/>)}
   {[0,1,2,3,4,5,6,7,8,9,10,11].map(i=>{const a=i/12*TAU,rr=mix(90,650,blast);return <ellipse key={i} cx={970+Math.cos(a)*rr} cy={535+Math.sin(a)*rr*.68} rx={18+blast*55} ry={10+blast*22} fill={i%2?'#e5ac91':'#b78ec5'} opacity={blast*(1-blast*.75)} transform={`rotate(${i*30} ${970+Math.cos(a)*rr} ${535+Math.sin(a)*rr*.68})`}/>;})}
   <g opacity={phase(t,.57,.72)}>{hole(970,535,70+blast*15,.12)}</g>
   <g opacity={action('remnant keeps contracting',.62,.77)}>{[0,1,2].map(i=>{const q=(elapsed('remnant keeps contracting',.62)/1.8+i/3)%1;return <ellipse key={i} cx="970" cy="535" rx={160-q*70} ry={110-q*45} fill="none" stroke="#bc9bb8" strokeWidth="3" opacity={Math.sin(q*Math.PI)*.45}/>;})}</g>
   {Array.from({length:8},(_,i)=>{const e=elapsed('supernova',.57),a=i*TAU/8,rr=220+e*70;return <ellipse key={'late-shell'+i} cx={970+Math.cos(a)*rr} cy={535+Math.sin(a)*rr*.68} rx={18+e*6} ry={8+e*2} transform={`rotate(${i*45} ${970+Math.cos(a)*rr} ${535+Math.sin(a)*rr*.68})`} fill="#cda1bc" opacity={Math.min(.25,e*.15)*Math.max(0,1-e/12)}/>;})}
  </g>;break;
 }
 case 5:{
  const compress=action('Pack enough mass',.05,.65),horizon=action('event horizon',.52,.9);
  content=<g>
   {[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17].map(i=>{const a=i*2.4,rr=mix(290,38,compress)*(0.5+i%3*.2);return <MatterParcel key={i} x={960+Math.cos(a)*rr} y={535+Math.sin(a)*rr} size={mix(20,12,compress)} angle={i*37} tint={i%2?'#d7b4a3':'#b6a4d6'} id={id+'matter'+i}/>;})}
   <circle cx="960" cy="535" r={mix(30,145,horizon)} fill="#030611" opacity={horizon}/>
   <circle cx="960" cy="535" r={mix(30,145,horizon)} fill="none" stroke="#b0d6dc" strokeWidth="4" strokeDasharray="9 13" opacity={horizon}/>
   <ellipse cx="960" cy="535" rx="510" ry="300" stroke="#536e97" strokeWidth="3" fill="none"/>
   <Planet x={960+Math.cos(seconds*.3)*510} y={535+Math.sin(seconds*.3)*300} r={28}/>
  </g>;break;
 }
 case 6:{
  const change=action('same',.3,.62),theta=-1+seconds*.42;
  content=<g><ellipse cx="960" cy="535" rx="540" ry="310" fill="none" stroke="#7996b8" strokeWidth="4"/>
   {star(960,535,mix(120,50,change),0,'gold',1-change)}<g opacity={change}>{hole(960,535,50)}</g>
   <Planet x={960+Math.cos(theta)*540} y={535+Math.sin(theta)*310} r={39} earth/>
   <path d={`M960 535L${960+Math.cos(theta)*540} ${535+Math.sin(theta)*310}`} stroke="#8ecacb" strokeWidth="2" opacity=".25"/>
   <circle cx="960" cy="535" r="175" fill="none" stroke="#7a6b9f" strokeWidth="2" strokeDasharray="4 15"/>
   <g opacity={1-action('sunlight would disappear',.65,.82)}>{[0,1,2].map(i=><LightTrain key={i} a={[960,535]} b={[1180,450+i*45]} c={[1500,400+i*80]} elapsed={seconds+i*.5} color="#ebc792" period={2.1}/>)}</g>
   <g opacity={action('remain much the same',.54,.68)}>{[0,1,2,3].map(i=>{const a=theta-.22*(i+1);return <circle key={i} cx={960+Math.cos(a)*540} cy={535+Math.sin(a)*310} r="5" fill="#acd8d6" opacity={.7-i*.13}/>;})}</g>
  </g>;break;
 }
 case 7:{
  const crossing=action('Outside',.1,.7),inside=action('Inside',.45,.94);
  content=<g>{hole(1040,535,230)}<circle cx="1040" cy="535" r="235" stroke="#88bdcc" strokeWidth="3" strokeDasharray="8 16" fill="none"/>
   <Ray a={[420,340]} b={[620,80]} c={[1460,140]} q={crossing}/>
   <g opacity={phase(t,.2,.35)}><path d="M970 535Q1095 370 1140 430L1140 640Q1095 700 970 535Z" fill="#75a8c8" opacity=".2"/><path d="M970 535Q1095 370 1140 430M970 535Q1095 700 1140 640" stroke="#88bed2" strokeWidth="4" fill="none"/></g>
   <Ray a={[970,535]} b={[1020,465]} c={[1040,535]} q={inside} color="#ebb695"/>
   <Ray a={[970,535]} b={[1020,620]} c={[1040,535]} q={phase(t,.55,.96)} color="#bca5dd"/>
   <LightTrain a={[420,340]} b={[620,80]} c={[1460,140]} elapsed={elapsed('Outside',.1)}/>
   <LightTrain a={[970,535]} b={[1020,465]} c={[1040,535]} elapsed={elapsed('Inside',.45)} color="#edba9c" period={1.8}/>
   <LightTrain a={[970,535]} b={[1020,620]} c={[1040,535]} elapsed={elapsed('even light',.58)} color="#c8b0e0" period={1.4}/>
   <g opacity={action('not a solid shell',.1,.25)}>{[0,1,2].map(i=>{const q=(elapsed('not a solid shell',.1)/2+i/3)%1;return <path key={i} d={`M${680+q*250} 715h18`} stroke="#a5c8ce" strokeWidth="5" opacity={Math.sin(q*Math.PI)*.6}/>;})}</g>
  </g>;break;
 }
 case 8:{
  const orbit=action('accretion disk',.04,.95),heat=action('heat',.3,.84),jets=action('jets',.7,.96);
  content=<g>{hole(980,540,130,.85)}
   {Array.from({length:14},(_,i)=><GasTrail key={i} cx={980} cy={540} base={i/14*TAU} q={clamp(orbit+i*.012)} outer={430} inner={165} turns={5} angularOffset={elapsed('accretion disk',.04)*(.42+i%3*.12)} width={3+heat*3} color={i%2?'#f3c88c':'#dca1a2'}/>)}
   <circle cx="980" cy="540" r="130" fill="#030611"/>
   {/* Local neighbouring streams approach, exchange energy, then leave a
       short-lived hot wake. No independent sparkle or universal impact ring. */}
   <g opacity={heat}>{[0,1,2].map(i=>{const e=elapsed('heat',.3),a=e*(1.5-i*.24)+i*2.1,q=(e/2.6+i/3)%1,near=1-phase(q,0,.52),release=phase(q,.52,1),rr=205+i*42,x=980+Math.cos(a)*rr,y=540+Math.sin(a)*rr*.32,dx=Math.cos(a+Math.PI/2)*near*33,dy=Math.sin(a+Math.PI/2)*near*12,hot=Math.sin(phase(q,.3,1)*Math.PI);return <g key={i} opacity={Math.sin(q*Math.PI)}>
    <ellipse cx={x+dx} cy={y+dy} rx={12-release*3} ry="5" transform={`rotate(${Math.cos(a)*12} ${x+dx} ${y+dy})`} fill="#d9a195"/>
    <ellipse cx={x-dx} cy={y-dy} rx={10-release*3} ry="4" fill="#f0c18f"/>
    <path d={`M${x} ${y}Q${x-Math.sin(a)*27} ${y+Math.cos(a)*9} ${x-Math.sin(a)*64} ${y+Math.cos(a)*20}`} stroke="#f2a878" strokeWidth={7+hot*8} fill="none" opacity={hot*.35}/>
    <ellipse cx={x} cy={y} rx={8+hot*13} ry={3+hot*5} fill="#ffe5af" opacity={hot}/>
   </g>;})}</g>
   <circle cx="980" cy="540" r="130" fill="#030611"/>
   <g opacity={phase(jets,0,.15)}>
    {[-1,1].map(side=><g key={side}>
     <path d={`M820 540Q850 ${540+side*160} 980 ${540+side*195}Q1030 ${540+side*255} 1055 ${540+side*455}`} fill="none" stroke="#8bcbd6" strokeWidth="13" pathLength="1" strokeDasharray="1" strokeDashoffset={1-jets} opacity=".55"/>
     <path d={`M1140 540Q1110 ${540+side*160} 980 ${540+side*195}Q950 ${540+side*255} 935 ${540+side*455}`} fill="none" stroke="#b0a7d9" strokeWidth="9" pathLength="1" strokeDasharray="1" strokeDashoffset={1-jets} opacity=".45"/>
     <LightTrain a={[980,540+side*195]} b={[1030,540+side*255]} c={[1055,540+side*455]} elapsed={elapsed('jets',.7)} color="#b9e2e3" period={1.7}/>
    </g>)}
   </g>
  </g>;break;
 }
 case 9:{
  const align=action('bends',.1,.68),arc=action('lensing',.45,.96);
  content=<g>{star(mix(680,1050,align),380,43,0,'blue')}
   {[0,1,2,3,4].map(i=><path key={i} d={`M250 ${270+i*120}Q${mix(950,600,align)} ${270+i*120} 1050 ${270+i*120}Q${mix(1200,1500,align)} ${270+i*120} 1760 ${270+i*120}`} stroke="#455f8b" strokeWidth="2" fill="none" opacity=".5"/>)}
   {hole(1050,535,155)}
   <path d="M850 470A215 215 0 0 1 1240 425" pathLength="1" strokeDasharray="1" strokeDashoffset={1-arc} fill="none" stroke="#b6ece3" strokeWidth="12"/>
   <path d="M900 700A220 220 0 0 0 1230 650" pathLength="1" strokeDasharray="1" strokeDashoffset={1-arc} fill="none" stroke="#a59ddf" strokeWidth="10"/>
   <Ray a={[350,370]} b={[1000,80]} c={[1650,440]} q={phase(t,.12,.86)} opacity={.5}/>
   <LightTrain a={[680,380]} b={[990,85]} c={[1650,440]} elapsed={elapsed('bends',.1)} period={2.4}/>
   <LightTrain a={[680,380]} b={[1010,900]} c={[1650,440]} elapsed={elapsed('lensing',.45)} color="#c2b7e9" period={2.7}/>
   {[0,1,2].map(i=>{const q=phase(t,.16+i*.12,.58+i*.12);const top=point([680,380],[990,85],[1650,440],q),bottom=point([680,380],[1010,900],[1650,440],q);return <g key={i} opacity={Math.sin(q*Math.PI)}>
    <circle cx={top.x} cy={top.y} r="8" fill="#d4f3de"/><circle cx={bottom.x} cy={bottom.y} r="7" fill="#c2b7e9"/>
   </g>;})}
   <g opacity={action('toward us',.12,.27)}><path d="M1680 400Q1740 440 1680 480Q1710 440 1680 400Z" fill="#89b5c5"/><circle cx="1693" cy="440" r="12" fill="#d4e5d9"/></g>
   <g opacity={action('curved paths',.83,.96)}><path d="M1500 365L1635 435M1500 510L1635 445" fill="none" stroke="#bddedb" strokeWidth="3" strokeDasharray="5 11"/></g>
  </g>;break;
 }
 case 10:{
  const resolve=action('shadow',.15,.82),network=action('across Earth',.12,.46);
  content=<g>{hole(1060,515,155,.8)}
   <circle cx="1060" cy="515" r="185" fill="none" stroke="#f2c19a" strokeWidth={55-resolve*28} opacity=".45"/>
   <circle cx="1060" cy="515" r="100" fill="none" stroke="#8dbccc" strokeWidth="2" strokeDasharray="6 14" opacity={resolve*.6}/>
   <g transform="translate(365 560)">
    <Planet x={0} y={0} r={165} earth/>
    <ellipse rx="78" ry="165" fill="none" stroke="#89c1ce" strokeWidth="2" opacity=".5"/>
    <ellipse rx="165" ry="58" fill="none" stroke="#89c1ce" strokeWidth="2" opacity=".5"/>
    {[[-85,-70],[90,-30],[-55,75]].map(([x,y],i)=><g key={i}><circle cx={x} cy={y} r="12" fill="#f2c599"/>
     <path d={`M${x} ${y}Q0 ${-150+i*60} ${i===0?90:-55} ${i===0?-30:75}`} stroke="#f2c599" strokeWidth="3" fill="none" pathLength="1" strokeDasharray="1" strokeDashoffset={1-network}/>
    </g>)}
   </g>
   {[0,1,2].map(i=><LinkArc key={i} q={phase(network,i*.12,.75+i*.1)} d={`M${i===0?280:i===1?455:310} ${i===0?490:i===1?530:635}Q650 ${350+i*140} 850 515`}/>)}
  </g>;break;
 }
 case 11:{
  const fall=action('approaching',.08,.92),stretch=action('tidal force',.38,.92),x=mix(440,1010,fall),y=mix(360,520,fall);
  content=<g>{hole(1320,560,150,.12)}
   <Astronaut x={x} y={y} scale={.8} stretch={stretch} angle={-60}/>
   <Ray a={[x+15,y+30]} b={[1160,560]} c={[1260,560]} q={phase(t,.3,.82)} color="#dfad99" opacity={.6}/>
   <path d={`M${x-70} ${y-40}L${x+60+fall*100} ${y+30}`} fill="none" stroke="#99c4d2" strokeWidth="3" strokeDasharray="7 12"/>
   <g opacity={action('nearer side',.24,.4)}>{[-1,1].map(side=><g key={side}><path d={`M${x+side*55} ${y+side*28-100}h${side>0?130:60}`} stroke="#efba96" strokeWidth="6"/><path d={`M${x+side*55+(side>0?130:60)-12} ${y+side*28-108}l12 8-12 8`} fill="none" stroke="#efba96" strokeWidth="4"/></g>)}</g>
   <g opacity={action('squeezes sideways',.7,.85)}><path d={`M${x-100} ${y+140}l40-35m-40 35h22m-22 0v-22M${x+140} ${y-140}l-40 35m40-35h-22m22 0v22`} fill="none" stroke="#9cd9d9" strokeWidth="5"/></g>
  </g>;break;
 }
 case 12:{
  const fall=action('supermassive',.25,.93),smallFall=action('small black hole',.12,.72);
  content=<g>
   <path d="M960 150V920" stroke="#405c85" strokeWidth="3"/>
   {hole(570,600,95,0,0)}{hole(1510,600,310,0,1)}
   <Astronaut x={mix(300,440,smallFall)} y={mix(350,500,smallFall)} scale={.55} stretch={smallFall*.95} angle={-35}/>
   <Astronaut x={mix(1070,1255,fall)} y={mix(330,500,fall)} scale={.55} stretch={fall*.08} angle={-20}/>
   {[0,1,2].map(i=><path key={i} d={`M${350+i*42} 760L${350+i*42} ${760-smallFall*(70+i*30)}`} stroke="#deae9e" strokeWidth="6"/>)}
   {[0,1,2].map(i=><path key={i} d={`M${1120+i*42} 760V${760-fall*(60+i*3)}`} stroke="#9dc6cc" strokeWidth="6"/>)}
   <g opacity={action('relatively gentle',.65,.8)}><path d="M1130 800H1280M1130 790V810M1280 790V810" fill="none" stroke="#a7d6cf" strokeWidth="3"/><LightTrain a={[1130,790]} b={[1190,780]} c={[1280,790]} elapsed={elapsed('relatively gentle',.65)} period={1.7}/></g>
  </g>;break;
 }
 case 13:{
  const fall=action('distant observer',.07,.8),red=action('toward red',.42,.97),nearX=mix(790,1190,fall);
  const start=Math.min(.88,cue('distant observer',.07)),end=Math.min(1,start+Math.min(.73,3.0/duration));
  const nearHand=.9*(seconds-.72*duration*integratedPhase(t,start,end));
  content=<g>{hole(1460,540,165)}
   <Clock x={370} y={390} hand={seconds*1.5} id={id+'far'}/>
   <g opacity={1-action('image fades away',.72,.98)*.95}><Clock x={nearX} y={570} r={60} hand={nearHand} id={id+'near'}/></g>
   {[0,1,2,3,4].map(i=>{
    // Equal emission intervals, increasingly separated reception times. The
    // origin is fixed at the clock's position when this particular pulse left.
    const emission=.12+i*.09,arrival=[.33,.43,.57,.75,.97][i];
    const q=phase(t,emission,arrival),emissionX=mix(790,1190,phase(emission,start,end));
    const pos=point([emissionX,510],[750,240],[400,350],q);
    return <g key={i} opacity={Math.sin(q*Math.PI)*(1-i*.13)}><ellipse cx={pos.x} cy={pos.y} rx={10+i*6} ry="7" fill={['#afdfe6','#b9ccd9','#d3b4be','#e6a597','#e29a86'][i]}/></g>;
   })}
   <path d={`M500 790Q${560+red*50} 720 ${620+red*100} 790T${740+red*180} 790T${860+red*260} 790`} stroke="#e7aa96" strokeWidth="6" fill="none" opacity={red}/>
  </g>;break;
 }
 case 14:{
  const cross=action('crossing can happen',.12,.83),crossStart=Math.min(.88,cue('crossing can happen',.12)),crossEnd=Math.min(1,crossStart+Math.min(.71,3.0/duration));
  const messageStart=Math.max(cue('sending a message',.57),crossStart+(crossEnd-crossStart)*.64),message=phase(t,messageStart,Math.min(1,messageStart+.25));
  const emissionX=mix(550,1260,phase(messageStart,crossStart,crossEnd))+30;
  content=<g>
   <path d="M1130-200Q820 540 1130 1300H1920V-200Z" fill="#040918" opacity=".8"/>
   <path d="M1130-200Q820 540 1130 1300" fill="none" stroke="#7499b6" strokeWidth="3" strokeDasharray="10 22" opacity=".6"/>
   <Astronaut x={mix(550,1260,cross)} y={490} scale={.95} angle={15}/>
   <Clock x={mix(540,1250,cross)} y={730} r={44} hand={seconds*1.2} id={id+'local'}/>
   <Planet x={mix(680,1390,cross)} y={510} r={14} color="#edc69d"/>
   <g opacity={phase(t,.15,.3)}><rect x="370" y="265" width="125" height="80" rx="20" fill="#1d3551" stroke="#789cac" strokeWidth="4"/><path d="M390 305H475" stroke="#789cac" strokeWidth="3"/><circle cx="453" cy="289" r="5" fill="#4b647c"/></g>
   <Ray a={[emissionX,435]} b={[1090,375]} c={[1260,345]} q={message} color="#edbe95" opacity={Math.sin(message*Math.PI)*.8}/>
   <g opacity={phase(t,messageStart,messageStart+.025)}>{[0,1].map(i=><LightTrain key={i} a={[emissionX,435+i*10]} b={[1090,375+i*35]} c={[1260,345+i*80]} elapsed={Math.max(0,seconds-messageStart*duration-i*.6)} color="#dfb58f" period={2.3+i*.3}/>)}</g>
   <g opacity={action('locally obvious wall',.35,.5)}>{[-1,0,1].map(i=><path key={i} d={`M${mix(550,1260,cross)-95} ${620+i*22}h190`} stroke="#6d9cba" strokeWidth="2" opacity=".35"/>)}</g>
   <path d="M450 850H1450" stroke="#547a9a" strokeWidth="2" opacity=".4"/>
  </g>;break;
 }
 case 15:{
  const converge=action('singularity',.05,.8),unknown=action('understanding',.6,.98);
  content=<g>
   {[0,1,2,3,4,5,6].map(i=><Ray key={i} a={[390+i*190,210]} b={[480+i*145,570]} c={[960,750]} q={converge} color={i%2?'#a69bd7':'#83c8d5'} opacity={.55}/>) }
   <ellipse cx="960" cy="750" rx={90+unknown*90} ry={35+unknown*55} fill="#8d85bc" opacity={.13+unknown*.12}/>
   {[0,1,2,3,4,5].map(i=><circle key={i} cx={960+Math.cos(i*1.1)*unknown*90} cy={750+Math.sin(i*1.1)*unknown*45} r={5+unknown*7} fill="#b6afd6" opacity={unknown*.5}/>)}
   <path d="M720 900H1200" stroke="#657799" strokeWidth="3" strokeDasharray="5 19" opacity={unknown}/>
  </g>;break;
 }
 case 16:{
  const mergeStart=Math.min(.88,cue('orbit each other',.04)),mergeEnd=Math.max(mergeStart+.08,cue('Their merger',.55));
  const merge=phase(t,mergeStart,mergeEnd),wave=phase(t,cue('gravitational waves',.45),1),r=mix(280,0,merge),angle=seconds*.9;
  content=<g><Waves x={990} y={540} q={wave} max={850}/>
   {[0,1].map(i=>{const sign=i?1:-1;const pts=Array.from({length:30},(_,j)=>{const prior=Math.max(0,t-.12+j*.12/29),oldMerge=phase(prior,mergeStart,mergeEnd),rr=mix(280,0,oldMerge);return [990+sign*Math.cos(prior*duration*.9)*rr,540+sign*Math.sin(prior*duration*.9)*rr*.6]});return <path key={i} d={pts.map((pt,j)=>`${j?'L':'M'}${pt[0]} ${pt[1]}`).join(' ')} stroke="#968fba" strokeWidth="3" opacity={.35*(1-merge)} fill="none"/>;})}
   <g opacity={1-phase(merge,.9,1)}>{hole(990+Math.cos(angle)*r,540+Math.sin(angle)*r*.6,90,0,0)}{hole(990-Math.cos(angle)*r,540-Math.sin(angle)*r*.6,70,0,1)}</g>
   <g opacity={phase(merge,.88,1)}>{hole(990,540,118,.1,2)}</g>
   <path d="M270 890Q370 830 470 890T670 890T870 890T1070 890T1270 890T1470 890T1670 890" fill="none" stroke="#b3a2d9" strokeWidth="5" pathLength="1" strokeDasharray="1" strokeDashoffset={1-wave} opacity=".6"/>
   {(()=>{const e=elapsed('Detectors on Earth',.73),show=phase(e,0,.6),strain=Math.sin(e*8)*Math.exp(-e*.65);return <g opacity={show} transform="translate(1540 730)">
    <path d={`M0 0H${135+strain*7}M0 0V${-110+strain*6}`} stroke="#a5c9cf" strokeWidth="12" fill="none"/><circle r="13" fill="#e9d7ad"/>
    <path d={`M-80 110Q-40 ${110-strain*34} 0 110T80 110T160 110`} stroke="#c2b0db" strokeWidth="4" fill="none"/>
    <LightTrain a={[0,0]} b={[70,0]} c={[135+strain*7,0]} elapsed={e} period={1.2} color="#d7ebd7"/><LightTrain a={[0,0]} b={[0,-55]} c={[0,-110+strain*6]} elapsed={e} period={1.2} color="#a6d9df"/>
   </g>;})()}
  </g>;break;
 }
 case 17:{
  const zoom=action('supermassive',.3,.93);
  content=<g>
   <g transform={`translate(${mix(700,450,zoom)} 560) scale(${mix(1,.55,zoom)})`}>{hole(0,0,105,.3,0)}{star(-240,-100,55,0,'blue')}</g>
   <g opacity={phase(t,.25,.55)} transform={`translate(1390 540) scale(${mix(.25,1,zoom)})`}>
    {Array.from({length:46},(_,i)=>{const a=i*.6+seconds*(.16-i*.002),rr=50+i*8;return <ellipse key={i} cx={Math.cos(a)*rr} cy={Math.sin(a)*rr*.48} rx="7" ry="4" fill={i%3?'#8abaca':'#c7add8'} opacity=".65"/>;})}{hole(0,0,145,.5,1)}
   </g>
   <g opacity={action('millions or even billions',.4,.6)}><path d="M1160 835H1620M1160 825V845M1620 825V845" fill="none" stroke="#a9bfd1" strokeWidth="3"/>{[0,1,2,3,4].map(i=><circle key={i} cx={1160+i*115} cy="835" r="5" fill="#c1d3d8" opacity={phase(elapsed('millions or even billions',.4),i*.35,i*.35+.4)}/>)}</g>
   <g opacity={action('between these categories',.75,.91)}><path d="M650 800Q820 860 1000 800" fill="none" stroke="#b9a6cd" strokeWidth="3" strokeDasharray="5 13"/><circle cx="825" cy="825" r="27" fill="#14203a" stroke="#b9a6cd" strokeWidth="3" strokeDasharray="4 8"/></g>
  </g>;break;
 }
 case 18:{
  const feed=action('gas',.1,.85),uncertain=action('seeds',.7,.97);
  content=<g>
   {Array.from({length:18},(_,i)=><GasTrail key={i} cx={990} cy={535} base={i/18*TAU} q={clamp(feed+i*.004)} outer={500} inner={170} turns={3} angularOffset={elapsed('gas',.1)*(.3+i%3*.08)} flatten={.52} width={4.5} color={i%2?'#aaa0d0':'#9acbc6'}/>)}
   {hole(990,535,mix(85,145,feed),.45)}
   <g opacity={uncertain*.8}>
    {[0,1].map(i=><g key={i}><circle cx={450+i*160} cy="860" r={i?29:12} fill="#060c1b" stroke="#8aa3bb" strokeWidth="3" strokeDasharray="4 8"/>
     <path d={`M${450+i*160} 820Q${500+i*140} 680 850 620`} stroke={i?'#a6a0c7':'#83b7bf'} strokeWidth="3" strokeDasharray="4 12" fill="none" pathLength="1" strokeDashoffset={1-uncertain}/>
    </g>)}
    <circle cx="850" cy="620" r="12" fill="none" stroke="#b1abc7" strokeWidth="3" strokeDasharray="3 5"/>
   </g>
  </g>;break;
 }
 case 19:{
  const orbit=action('stars',.03,.96);
  content=<g>
   {[0,1,2].map(i=>{
    const rx=230+i*110,ry=120+i*60,focusOffset=Math.sqrt(rx*rx-ry*ry),e=focusOffset/rx;
    const mean=-1+seconds*(.58-i*.1);let eccentric=mean;
    for(let j=0;j<7;j++)eccentric-=(eccentric-e*Math.sin(eccentric)-mean)/(1-e*Math.cos(eccentric));
    const centerX=1000-focusOffset;
    return <g key={i} transform={`rotate(${i*28-25} 1000 535)`}>
     <ellipse cx={centerX} cy="535" rx={rx} ry={ry} fill="none" stroke={['#83c7ce','#b6a2d6','#ddaf95'][i]} strokeWidth="3" opacity=".65"/>
     {star(centerX+Math.cos(eccentric)*rx,535+Math.sin(eccentric)*ry,20+i*4,i,'blue')}
     {Array.from({length:7},(_,k)=>{const recorded=cue('Track stars',.16)*duration+k*.75;if(seconds<recorded)return null;const m=-1+recorded*(.58-i*.1);let E=m;for(let j=0;j<7;j++)E-=(E-e*Math.sin(E)-m)/(1-e*Math.cos(E));return <circle key={k} cx={centerX+Math.cos(E)*rx} cy={535+Math.sin(E)*ry} r="5" fill={['#83c7ce','#b6a2d6','#ddaf95'][i]} opacity=".75"/>;})}
     <path d={`M1000 535L${centerX+Math.cos(eccentric)*rx} ${535+Math.sin(eccentric)*ry}`} stroke="#9fb6c8" strokeWidth="2" strokeDasharray="4 10" opacity={action('measuring instruments',.84,.97)*.5}/>
    </g>;
   })}
   <circle cx="1000" cy="535" r="23" fill="#040816"/><path d="M970 535H1030M1000 505V565" stroke="#bad4d4" strokeWidth="2" opacity=".45"/>
   <g opacity={action('mass concentrated',.4,.64)}><circle cx="1000" cy="535" r="42" fill="none" stroke="#b8d5d4" strokeWidth="3" strokeDasharray="5 8"/><path d="M1000 535L1480 720" stroke="#91aebd" strokeWidth="2" opacity=".5"/><path d="M1460 700L1500 740M1460 740L1500 700" stroke="#b7c5d1" strokeWidth="3"/></g>
   <Telescope x={290} y={810} angle={-30} scale={.65}/>
  </g>;break;
 }
 case 20:{
  const move=action('orbits',.04,.97),transfer=action('transfer energy',.4,.85),meet=phase(transfer,0,.4),separate=phase(transfer,.4,1);
  content=<g>{hole(990,530,95,.2)}
   {[0,1,2].map(i=>{const rx=285+i*180,ry=150+i*115,a=i*2+seconds*(.48-i*.09);return <g key={i}><ellipse cx="990" cy="530" rx={rx} ry={ry} fill="none" stroke="#516f95" strokeWidth="3"/>{star(990+Math.cos(a)*rx,530+Math.sin(a)*ry,20+i*9,i,i===0?'gold':i===1?'blue':'red')}</g>;})}
   <Ray a={[180,230]} b={[780,40]} c={[1770,260]} q={phase(t,.25,.88)} opacity={.3}/>
   <g opacity={phase(transfer,0,.08)}>
    <path d="M650 700Q650 570 825 635Q940 680 965 565M760 800Q720 695 825 635Q730 510 555 645" fill="none" stroke="#dbb992" strokeWidth="3" opacity=".35"/>
    {(()=>{const q1=point([825,635],[940,680],[965,565],separate),q2=point([825,635],[730,510],[555,645],separate);return <>
     <ellipse cx={separate>0?q1.x:mix(650,825,meet)} cy={separate>0?q1.y:mix(700,635,meet)} rx="20" ry="12" fill="#edc58f" opacity={1-phase(separate,.78,1)}/>
     <ellipse cx={separate>0?q2.x:mix(760,825,meet)} cy={separate>0?q2.y:mix(800,635,meet)} rx="23" ry="13" fill="#a7d1cf"/>
    </>;})()}
    <circle cx="825" cy="635" r={12+phase(transfer,.35,.62)*35} fill="none" stroke="#f2dab0" strokeWidth="3" opacity={Math.sin(phase(transfer,.32,.66)*Math.PI)*.5}/>
    <g opacity={action('angular momentum',.63,.78)}><path d="M770 600Q650 510 540 600" fill="none" stroke="#a7d1cf" strokeWidth="4" pathLength="1" strokeDasharray="1" strokeDashoffset={1-action('angular momentum',.63,.78)}/><path d="M555 580l-15 20 27-2" fill="none" stroke="#a7d1cf" strokeWidth="4"/></g>
    <g opacity={action('surroundings',.71,.85)}>{[0,1,2].map(i=>{const e=elapsed('surroundings',.71),a=2.8+e*.65+i*.16;return <ellipse key={i} cx={990+Math.cos(a)*(420+i*17)} cy={530+Math.sin(a)*(245+i*7)} rx="12" ry="6" fill="#a7d1cf" opacity={.55-i*.12}/>;})}</g>
   </g>
  </g>;break;
 }
 case 21:{
  const radiation=action('Quantum theory',.12,.97);
  content=<g>{hole(990,535,170)}
   {[0,1,2,3].map(i=>{const q=(elapsed('Quantum theory',.12)/4+i*.25)%1,a=-1.8+i*1.35,rr=200+q*390;return <g key={i} opacity={radiation*Math.sin(q*Math.PI)*.5}><path d={`M${990+Math.cos(a)*(rr-50)} ${535+Math.sin(a)*(rr-50)}Q${990+Math.cos(a+.05)*rr} ${535+Math.sin(a+.05)*rr} ${990+Math.cos(a)*(rr+45)} ${535+Math.sin(a)*(rr+45)}`} stroke="#a5becf" strokeWidth="4" fill="none"/></g>;})}
   <circle cx="990" cy="535" r="218" fill="none" stroke="#7185ab" strokeWidth="2" strokeDasharray="2 20" opacity=".3"/>
  </g>;break;
 }
 case 22:{
  const age=action('slow',.07,.96),timeZoom=action('longer than the universe',.28,.64),small=action('Smaller black holes',.53,.84),uncertain=action('uncertain',.7,.96);
  content=<g>{hole(1050,490,mix(175,166,age))}
   <path d="M300 845H1640" stroke="#587497" strokeWidth="6"/>
   {[0,1,2,3,4,5,6,7].map(i=><path key={i} d={`M${300+i*185} 825V865`} stroke="#7ca2b7" strokeWidth="4"/>)}
   <circle cx={mix(300,1600,age)} cy="845" r="15" fill="#d9c2a5"/>
   <Clock x={400} y={420} r={72} hand={seconds*2.4} id={id+'time'}/>
   <path d={`M300 875H${300+mix(1030,32,timeZoom)}`} stroke="#b8cbca" strokeWidth="13" opacity=".65"/>
   <path d={`M${300+mix(1030,32,timeZoom)} 860V890`} stroke="#cedbd1" strokeWidth="4"/>
   <g opacity={small}>{hole(1530,490,55,0,1)}
    {Array.from({length:6},(_,i)=>{const q=phase(small,i*.055,.7+i*.05),a=i/6*TAU,rr=70+q*110;return <path key={i} d={`M${1530+Math.cos(a)*(rr-20)} ${490+Math.sin(a)*(rr-20)}Q${1530+Math.cos(a+.06)*rr} ${490+Math.sin(a+.06)*rr} ${1530+Math.cos(a)*(rr+20)} ${490+Math.sin(a)*(rr+20)}`} stroke="#c4c2dc" strokeWidth="4" fill="none" opacity={Math.sin(q*Math.PI)*.65}/>;})}
    <circle cx="1530" cy="490" r="110" fill="none" stroke="#9b97bb" strokeWidth="3" strokeDasharray="3 13" opacity={uncertain*.55}/>
   </g>
   <path d="M625 845l-18-25m50 25l-18-25M995 845l-18-25m50 25l-18-25" stroke="#b6a6cc" strokeWidth="7"/>
  </g>;break;
 }
 case 23:{
  const observe=action('Stellar orbits',.06,.56),combine=action('consistent story',.5,.96),gas=action('glowing gas',.3,.64),shadow=action('shadow images',.35,.7),detect=action('gravitational waves',.4,.78);
  content=<g>
   <Telescope x={400} y={600} angle={mix(-10,-32,observe)} scale={1.05}/>
   <g transform="translate(1330 660)"><path d="M0 0H350M0 0V-300" stroke="#95b8c4" strokeWidth="26"/><path d="M0 0H350M0 0V-300" stroke="#bce7dd" strokeWidth="5"/><rect x="-40" y="-40" width="80" height="80" rx="15" fill="#668da3"/></g>
   <g opacity={phase(observe,0,.15)}><ellipse cx="590" cy="270" rx="120" ry="55" fill="none" stroke="#7eb6c4" strokeWidth="3"/>{star(590+Math.cos(elapsed('Stellar orbits',.06)*1.3)*120,270+Math.sin(elapsed('Stellar orbits',.06)*1.3)*55,14,4,'blue')}<circle cx="590" cy="270" r="8" fill="#080e20"/></g>
   <g opacity={gas}><path d="M550 740Q620 650 700 730T860 730" stroke="#edc49b" strokeWidth="4" fill="none" pathLength="1" strokeDasharray="1" strokeDashoffset={1-gas}/>{[0,1,2].map(i=><circle key={i} cx={mix(570,850,phase(gas,i*.1,.75+i*.1))} cy={730-i*12} r="6" fill={i%2?'#dca7ba':'#ebcb9d'}/>)}</g>
   <g opacity={shadow}><ellipse cx="780" cy="580" rx="75" ry="66" stroke="#e6ae7f" strokeWidth="18" fill="#060b1a"/><path d="M850 550Q900 450 940 400" stroke="#dfb491" strokeWidth="4" fill="none" pathLength="1" strokeDasharray="1" strokeDashoffset={1-combine}/></g>
   <g opacity={phase(detect,0,.1)}><circle cx={1330+350*Math.sin(detect*Math.PI)} cy="660" r="9" fill="#eff0d0"/><circle cx="1330" cy={660-300*Math.sin(detect*Math.PI)} r="9" fill="#a9e7de"/>
    <LightTrain a={[1330,660]} b={[1505,660]} c={[1680,660]} elapsed={elapsed('gravitational waves',.4)} period={1.4}/><LightTrain a={[1330,660]} b={[1330,510]} c={[1330,360]} elapsed={elapsed('gravitational waves',.4)} period={1.4} color="#c5b4e0"/>
    <path d="M1410 810Q1440 760 1470 810T1530 810T1590 810T1650 810" fill="none" stroke="#c0add9" strokeWidth="5" pathLength="1" strokeDasharray="1" strokeDashoffset={1-detect}/>
   </g>
   <LinkArc d="M510 510Q760 190 920 340" q={observe}/><LinkArc d="M1300 600Q1170 320 1040 340" q={phase(t,.32,.77)}/>
   <g opacity={combine}>{hole(980,340,95,.5)}<path d="M870 700Q980 790 1090 700" fill="none" stroke="#a5a0c4" strokeWidth="4" strokeDasharray="5 14"/><circle cx="980" cy="760" r="35" fill="none" stroke="#a5a0c4" strokeWidth="4" strokeDasharray="4 10"/></g>
   <g opacity={gas}><LightTrain a={[550,740]} b={[700,675]} c={[860,730]} elapsed={elapsed('glowing gas',.3)} period={1.8} color="#ebcb9d"/></g>
   <g opacity={action('keep testing',.88,.98)}><path d="M870 700L800 775M1090 700L1160 775" fill="none" stroke="#a5a0c4" strokeWidth="3" strokeDasharray="4 12"/></g>
  </g>;break;
 }
 default:return null;
 }
 return <g strokeLinecap="round" strokeLinejoin="round">
  <defs><radialGradient id={id+'background'} cx="55%" cy="45%" r="75%"><stop stopColor="#202e48"/><stop offset=".55" stopColor="#101d35"/><stop offset="1" stopColor="#070e21"/></radialGradient>
   <radialGradient id={id+'cloud-teal'}><stop stopColor="#548a9a" stopOpacity=".15"/><stop offset=".5" stopColor="#386b85" stopOpacity=".07"/><stop offset="1" stopColor="#27445e" stopOpacity="0"/></radialGradient>
   <radialGradient id={id+'cloud-violet'}><stop stopColor="#886896" stopOpacity=".14"/><stop offset=".55" stopColor="#674d81" stopOpacity=".06"/><stop offset="1" stopColor="#3a315c" stopOpacity="0"/></radialGradient>
  </defs>
  <rect width="1920" height="1080" fill={`url(#${id}background)`}/>
  {backgroundFile&&[3,4,17,18].includes(n)&&<image href={staticFile(backgroundFile)} x={-270-150*Math.sin(bgTime*.065)} y={-155+75*Math.sin(bgTime*.05)} width="2460" height="1390" preserveAspectRatio="xMidYMid slice" opacity=".38"/>}
  <g transform={`translate(${160*Math.sin(bgTime*.075)} ${-90*Math.sin(bgTime*.07)})`}><ellipse cx="220" cy="320" rx="650" ry="350" fill={`url(#${id}cloud-teal)`}/><ellipse cx="1580" cy="760" rx="720" ry="390" fill={`url(#${id}cloud-violet)`}/></g>
  {[0,1].map(layer=><g key={layer}>
   {Array.from({length:layer?34:64},(_,i)=><circle key={i} cx={(((i*283+layer*113-bgTime*(layer?18:6))%2300+2300)%2300)-190} cy={((i*179+layer*67+bgTime*(layer?3:1))%1320)-120} r={layer?2.2+i%3*.6:1+i%3*.25} fill={i%3?'#c6d7e4':'#c6b5e2'} opacity={layer?.3+(i%4)*.08:.17+(i%4)*.055}/>) }
  </g>)}
  {content}
 </g>;
};

function LinkArc({d,q}:{d:string;q:number}){return <path d={d} stroke="#85bacb" strokeWidth="5" fill="none" pathLength="1" strokeDasharray="1" strokeDashoffset={1-q} opacity=".65"/>;}
