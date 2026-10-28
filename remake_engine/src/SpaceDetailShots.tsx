import type {ReactNode} from 'react';
import {staticFile} from 'remotion';
import {Star,Astronaut,Clock} from './ContinuousSpace';
type Word={text?:string;start:number;end:number};
type Props={sceneId:string;frame:number;frames:number;fps:number;words:Word[];globalSeconds:number};
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
const smooth=(v:number)=>{v=clamp(v);return v*v*(3-2*v)};
const clean=(v:string)=>v.toLowerCase().replace(/[^a-z0-9]/g,'');
const plans:Record<string,{phrase:string;fallback:number;hold:number}>={
 'space-03':{phrase:'For much of its life',fallback:12.769,hold:5},
 'space-05':{phrase:'a larger mass',fallback:16.767,hold:3.3},
 'space-10':{phrase:'These observations test our models',fallback:14.375,hold:5},
 'space-13':{phrase:'The image fades away',fallback:16.676,hold:4.3},
 'space-15':{phrase:'It tells us that understanding',fallback:16.082,hold:5},
 'space-18':{phrase:'The growth pathways are being tested',fallback:14.852,hold:5},
 'space-21':{phrase:'It has not been directly detected',fallback:13.380,hold:4.8},
 'space-22':{phrase:'Smaller black holes would radiate more strongly',fallback:12.093,hold:5},
};
export function getSpaceDetailWindow(p:Pick<Props,'sceneId'|'frames'|'fps'|'words'>){
 const plan=plans[p.sceneId];if(!plan)return null;
 const wanted=plan.phrase.split(/\s+/).map(clean);
 const tokens=p.words.flatMap(w=>(w.text||'').split(/\s+/).map(text=>({text:clean(text),start:w.start}))).filter(w=>w.text);
 const hit=tokens.findIndex((_,i)=>wanted.every((token,j)=>tokens[i+j]?.text===token));
 const start=hit<0?plan.fallback:tokens[hit].start+.15,duration=p.frames/p.fps;
 const candidate=Math.min(duration,start+plan.hold),end=duration-candidate<1.8?duration:candidate;
 return {start,end,phrase:plan.phrase};
}
const tag=(text:string,x:number,y:number,color='#a6ded6')=>{
 const w=text.length*17+42;
 return <g><rect x={x-w/2} y={y-29} width={w} height="58" rx="22" fill="#17354c" stroke={color} strokeOpacity=".65"/><text x={x} y={y+1} textAnchor="middle" dominantBaseline="middle" fill="#f7f0d8" fontFamily="Arial, sans-serif" fontSize="30" fontWeight="600">{text}</text></g>;
};
function DarkBody({x,y,r,id}:{x:number;y:number;r:number;id:string}){
 return <g transform={`translate(${x} ${y})`}><defs><radialGradient id={id}><stop offset=".52" stopColor="#e6bd83" stopOpacity="0"/><stop offset=".72" stopColor="#e6bd83" stopOpacity=".45"/><stop offset="1" stopColor="#a98dbe" stopOpacity="0"/></radialGradient></defs><circle r={r*1.6} fill={`url(#${id})`}/><circle r={r} fill="#030814"/><circle r={r*1.02} fill="none" stroke="#d9bc8f" strokeOpacity=".55" strokeWidth="3"/></g>;
}
function Pulse({x,y,r,color='#b6ded4',alpha=1}:{x:number;y:number;r:number;color?:string;alpha?:number}){
 return <g opacity={alpha}><circle cx={x} cy={y} r={r*2.1} fill={color} opacity=".1"/><circle cx={x} cy={y} r={r} fill={color}/></g>;
}
function Arrow({x,y,angle,color,q}:{x:number;y:number;angle:number;color:string;q:number}){
 return <g transform={`translate(${x} ${y}) rotate(${angle})`} opacity={q}><path d="M-70 0H55M35-19L57 0 35 19" fill="none" stroke={color} strokeWidth="9" strokeLinecap="round" strokeLinejoin="round"/></g>;
}
/** Eight new explanatory shots; every shot changes the depicted mechanism,
 * rather than enlarging a still frame or replaying an earlier choreography. */
export function SpaceDetailShots(p:Props){
 const win=getSpaceDetailWindow(p),sec=p.frame/p.fps;if(!win||sec<win.start||sec>=win.end)return null;
 const elapsed=sec-win.start,u=clamp(elapsed/(win.end-win.start)),n=Number(p.sceneId.slice(-2));
 const opacity=smooth(elapsed/.25)*(win.end===p.frames/p.fps?1:smooth((win.end-sec)/.25));
 const id=`detail-${p.sceneId}`,appear=(a:number,b:number)=>smooth((elapsed-a)/(b-a));
 let content:ReactNode=null;
 if(n===3){
  const equilibrium=appear(1.3,2.8),radius=155+(1-equilibrium)*Math.sin(elapsed*4)*12;
  content=<g><defs><radialGradient id={id+'core'} cx="35%" cy="30%"><stop stopColor="#fff3ba"/><stop offset=".5" stopColor="#f2b564"/><stop offset="1" stopColor="#cd6f64"/></radialGradient></defs>
   <Star x={960} y={545} r={radius} id={id+'surface'} time={elapsed}/><circle cx="960" cy="545" r={radius*.42} fill="#fff0b7" opacity=".4"/>
   {Array.from({length:12},(_,i)=>{const a=i*Math.PI/6,cycle=(elapsed*.65+i*.17)%1,r=55+cycle*245;return <Pulse key={i} x={960+Math.cos(a)*r} y={545+Math.sin(a)*r} r={8} color="#ffe1a3" alpha={Math.sin(cycle*Math.PI)*.8}/>;})}
   {[0,1,2,3].map(i=>{const a=i*Math.PI/2;return <g key={i}><Arrow x={960+Math.cos(a)*340} y={545+Math.sin(a)*340} angle={i*90+180} color="#97cee0" q={1}/><Arrow x={960+Math.cos(a)*220} y={545+Math.sin(a)*220} angle={i*90} color="#ffd196" q={appear(.4,1.2)}/></g>;})}
   {tag('Fusion core',960,240)}{tag('Gravity',420,410,'#98d6e5')}{tag('Pressure',1500,700,'#ffd196')}
   <circle cx="960" cy="545" r={radius+18} stroke="#fff4c8" strokeWidth="3" fill="none" opacity={equilibrium*.4}/>
  </g>;
 }else if(n===5){
  const grow=appear(.45,2.1),r=88+88*grow;
  content=<g><DarkBody x={590} y={555} r={88} id={id+'small'}/><DarkBody x={1330} y={555} r={r} id={id+'large'}/>
   <path d="M280 840H1640" stroke="#64869e" strokeWidth="3"/>
   {[0,1].map(i=><g key={i}><path d={`M${590+i*740-88} 790H${590+i*740+88}`} stroke="#afc7d0" strokeWidth="5"/><path d={`M${590+i*740-88} 776V804M${590+i*740+88} 776V804`} stroke="#afc7d0" strokeWidth="4"/></g>)}
   <path d={`M${1330-r} 730H${1330+r}M${1330-r} 715V745M${1330+r} 715V745`} stroke="#f3cf9b" strokeWidth="5" fill="none"/>
   <path d={`M${1330-r} 555V715M${1330+r} 555V715`} stroke="#9dbdc4" strokeWidth="2" strokeDasharray="5 9" opacity=".35"/>
   {[0,1,2].map(i=>{const py=310+i*25+appear(i*.18,.85+i*.18)*125;return <Pulse key={i} x={1330} y={py} r={7} alpha={py<555-r-8?1-grow:0}/>;})}
   {tag('Lower mass',590,290)}{tag('Higher mass',1330,290,'#f2cd97')}
   {tag('Event horizon',1330,900,'#f2cd97')}
  </g>;
 }else if(n===10){
  const align=appear(.8,2.5);
  content=<g><defs><clipPath id={id+'observation'}><rect x="350" y="350" width="440" height="410" rx="38"/></clipPath></defs>{[0,1].map(i=><g key={i} transform={`translate(${570+i*760} 555)`}>
   <circle r="164" fill="#020916"/><ellipse rx="185" ry="160" stroke={i?'#a6d9d4':'#e7b17c'} strokeWidth={i?9:40} strokeDasharray={i?'10 8':undefined} fill="none" opacity={i?.9:.65}/>
   {!i&&Array.from({length:28},(_,j)=>{const a=j/28*Math.PI*2;return <circle key={j} cx={Math.cos(a)*175} cy={Math.sin(a)*153} r={12+j%3*3} fill={j%4?'#e8ad75':'#f7d19a'} opacity={.2+(j%4)*.12}/>;})}
   <path d="M-210 0H210M0-205V205" stroke="#89abb6" strokeWidth="2" opacity=".3"/>
   {i===1&&<ellipse rx={185+(1-align)*25} ry={160+(1-align)*20} fill="none" stroke="#f2d29a" strokeWidth="4" opacity={align}/>}</g>)}
   <image href={staticFile('real-media/m87-eht.jpg')} x="350" y="350" width="440" height="410" preserveAspectRatio="xMidYMid slice" clipPath={`url(#${id}observation)`}/>
   <path d="M800 555H1090" stroke="#7eabb8" strokeWidth="4" strokeDasharray="6 14" pathLength="1" strokeDashoffset={1-align}/>
   {tag('Radio observation',570,285,'#efc28d')}{tag('Model schematic',1330,285)}
   <text x="570" y="790" textAnchor="middle" fill="#afc6cf" fontSize="21" fontFamily="Arial, sans-serif">EHT Collaboration</text>
   <path d="M480 775Q960 935 1420 775" stroke="#a3bfc5" strokeWidth="2" fill="none" opacity={align*.6}/>
   {tag('Shadow',960,890)}
  </g>;
 }else if(n===13){
  const dim=1-appear(.4,3.7);
  const received=Array.from({length:5},(_,i)=>Math.exp(-(((elapsed-(2.7+i*.6))/.16)**2))*(.9-i*.15)).reduce((a,b)=>a+b,0);
  const trace=Array.from({length:49},(_,i)=>{const x=-88+i*176/48,amp=Math.exp(-(((i/48-.67)/.22)**2))*received*45;return `${i?'L':'M'}${x} ${Math.sin(i*.65-elapsed*15)*amp}`;}).join(' ');
  content=<g><defs><linearGradient id={id+'housing'} x1="0" y1="0" x2=".8" y2="1"><stop stopColor="#486d80"/><stop offset=".4" stopColor="#29495f"/><stop offset="1" stopColor="#183044"/></linearGradient></defs><g opacity={dim}><Astronaut x={470} y={555} scale={1.35}/></g>
   {Array.from({length:5},(_,i)=>{const q=clamp((elapsed-i*.6)/2.7),x=550+q*720;return <Pulse key={i} x={x} y={535+Math.sin(q*Math.PI)*25} r={9-i*.8} color={i<2?'#eac790':'#d07888'} alpha={Math.sin(q*Math.PI)*Math.max(.05,dim)*(.8-i*.1)}/>;})}
   <g transform="translate(1430 550)"><rect x="-120" y="-130" width="240" height="260" rx="42" fill={`url(#${id}housing)`} stroke="#9ac8cc" strokeWidth="5"/><path d="M-101-76V-98Q-101-114-83-114H64" fill="none" stroke="#c2dcd5" strokeWidth="3" opacity=".6"/>
    <rect x="-101" y="-35" width="202" height="90" rx="15" fill="#11273b" stroke="#638998" strokeWidth="2"/><path d="M-88 0H88" stroke="#87adaf" strokeWidth="2" opacity=".4"/>
    <path d={trace} stroke="#eab38c" strokeWidth="5" fill="none"/>
    <circle cx="0" cy="-82" r="15" fill="#b2ddd2" opacity={.12+Math.min(1,received)*.88}/><path d="M-65 92H65" stroke="#0d2338" strokeWidth="6"/></g>
   {tag('Traveler image',470,310,'#e9ba94')}{tag('Receiver',1430,310)}
   <Clock x={1000} y={820} r={66} hand={elapsed*2.3} id={id+'clock'}/>{tag('Distant clock',1000,945)}
  </g>;
 }else if(n===15){
  const converge=appear(0,2.7),uncertain=appear(2,4);
  content=<g><ellipse cx="1070" cy="555" rx="170" ry="170" fill="#735c8c" opacity=".1"/>
   {Array.from({length:13},(_,i)=>{const y=240+i*52,endY=555+(y-555)*(1-converge*.86);return <g key={i}><path d={`M330 ${y}Q680 ${y} 935 ${endY}`} stroke="#9cc4ce" strokeWidth="3" fill="none"/><path d={`M935 ${endY}Q1040 555 1205 ${555+(y-555)*.12}`} stroke="#d7b5b2" strokeWidth="3" fill="none" strokeDasharray="5 14" opacity={1-uncertain*.75}/></g>;})}
   <circle cx="1100" cy="555" r="115" fill="#142038" stroke="#a399bd" strokeWidth="3" strokeDasharray="6 15"/>
   {[0,1,2].map(i=><path key={i} d={`M${1015+i*52} 530q22-25 40 0t40 0`} fill="none" stroke="#a99fc0" strokeWidth="3" opacity={.35+uncertain*.2}/>)}
   {tag('Classical model',550,250)}{tag('Unresolved physics',1310,820,'#c1b0d0')}
  </g>;
 }else if(n===18){
  const compare=appear(1,3.8);
  content=<g>{[0,1].map(i=><g key={i}><path d={`M360 ${410+i*290}Q800 ${360+i*270} 1240 555`} stroke={i?'#d6b4b9':'#9cd6d3'} strokeWidth="4" fill="none" strokeDasharray="6 13"/>
   {[0,1,2,3].map(j=>{const x=370+j*210,r=(i?28:12)+j*(i?10:16);return <g key={j} transform={`translate(${x} ${410+i*290+(555-(410+i*290))*j/4})`} opacity={appear(j*.22,.6+j*.22)*.42}><circle r={r} fill="#050b18" stroke={i?'#d3b2b9':'#a3d6cf'} strokeWidth="2" strokeDasharray="4 7"/></g>;})}
   {(()=>{const q=appear(.3+i*.2,3.7+i*.2),x=360+q*880,y=(1-q)**2*(410+i*290)+2*(1-q)*q*(360+i*270)+q*q*555,r=(i?28:12)+q*(i?40:56);return <g transform={`translate(${x} ${y})`}><circle r={r*1.4} fill={i?'#d3aab9':'#97d2cc'} opacity=".09"/><circle r={r} fill="#050b18" stroke={i?'#d3b2b9':'#a3d6cf'} strokeWidth="3" strokeDasharray="5 9"/></g>;})()}
   </g>)}
   <g transform="translate(1460 555)" opacity={compare}><ellipse rx="145" ry="85" fill="#b3b1d5" opacity=".1"/>{Array.from({length:34},(_,i)=>{const a=i*.8+elapsed*.12,r=20+i*3;return <circle key={i} cx={Math.cos(a)*r} cy={Math.sin(a)*r*.5} r="3" fill={i%2?'#e5ccb0':'#bad7df'}/>;})}<circle r="11" fill="#e6d1b3"/></g>
   {tag('Possible seed paths',710,250)}{tag('Distant galaxy',1460,800)}
  </g>;
 }else if(n===21){
  const fades=1-appear(2,4.5);
  content=<g><DarkBody x={570} y={555} r={145} id={id}/>
   {Array.from({length:6},(_,i)=>{const q=(elapsed*.25+i*.16)%1;return <path key={i} d={`M${750+q*340} ${510-i*9}q22-23 44 0t44 0`} stroke="#bfa7d2" strokeWidth="3" strokeDasharray="5 8" fill="none" opacity={Math.sin(q*Math.PI)*.35}/>;})}
   <g transform="translate(1410 555)"><rect x="-140" y="-115" width="280" height="230" rx="35" fill="#24435b" stroke="#8ebac5" strokeWidth="4"/><path d="M-100 20H100" stroke="#6e9baa" strokeWidth="3"/><path d="M-100 18l30-4 20 6 28-4 23 6 31-5 28 3 40-3" stroke="#b3c5c9" strokeWidth="3" fill="none"/><circle cx="90" cy="-65" r="9" fill="#d4c6b3" opacity=".4"/></g>
   {tag('Predicted radiation',570,280,'#c3afd5')}{tag('Detector',1410,280,'#d7cbb7')}{tag('Not detected',1410,810,'#d7cbb7')}
   <path d="M940 745H1120" stroke="#ad99c4" strokeWidth="3" strokeDasharray="5 11" opacity={fades*.5}/>
  </g>;
 }else if(n===22){
  const unknown=appear(2.7,4.5);
  content=<g>{[0,1].map(i=><g key={i}><DarkBody x={560+i*780} y={555} r={i?66:145} id={id+i}/>
   {Array.from({length:i?12:4},(_,j)=>{const a=j/(i?12:4)*Math.PI*2,q=(elapsed*(i?.55:.22)+j*.17)%1,r=(i?95:175)+q*160;return <path key={j} d={`M${560+i*780+Math.cos(a)*r} ${555+Math.sin(a)*r}q${Math.cos(a+.6)*17} ${Math.sin(a+.6)*17} ${Math.cos(a)*32} ${Math.sin(a)*32}`} stroke={i?'#f1c78d':'#b5a8ca'} strokeWidth={i?5:3} fill="none" opacity={Math.sin(q*Math.PI)*(i?.7:.25)*(1-unknown*.45)}/>;})}
   </g>)}
   {tag('Larger black hole',560,255)}{tag('Smaller black hole',1340,255,'#efc891')}
   <path d="M560 875H1340" stroke="#9eacc0" strokeWidth="3" strokeDasharray="5 13" opacity={unknown}/>
   {unknown>.1&&<g opacity={unknown}>{tag('Final stages uncertain',960,910,'#c5b4d0')}</g>}
  </g>;
 }
 return <g opacity={opacity} strokeLinecap="round" strokeLinejoin="round"><defs><radialGradient id={id+'bg'} cx="50%" cy="45%"><stop stopColor="#223952"/><stop offset="1" stopColor="#0a152b"/></radialGradient></defs><rect width="1920" height="1080" fill={`url(#${id}bg)`}/>
  {Array.from({length:45},(_,i)=><circle key={i} cx={((i*317-p.globalSeconds*(i%2?18:6)+18000)%2200)-140} cy={((i*191+p.globalSeconds*(i%2?3:1))%1300)-100} r={1.2+i%3*.7} fill="#b6cedd" opacity={.15+i%4*.08}/>)}
  {content}
 </g>;
}
