import {Cappy} from './Cappy';
const ease=(x:number)=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x)};
export const HostMoments=({outro,frame,frames,fps,speaking,words}:{outro:boolean;frame:number;frames:number;fps:number;speaking:boolean;words:{text?:string;start:number;end:number}[]})=>{
 const t=frame/Math.max(1,frames-1),step=(a:number,b:number)=>ease((t-a)/(b-a));
 const cue=(text:string,fallback:number)=>((words.find(w=>w.text?.toLowerCase()===text)?.start??fallback)+.15)*fps/Math.max(1,frames-1);
 const like=cue('like',2.1),subscribe=cue('subscribe',2.49),question=cue('what',5.35),comment=cue('comments',12.69);
 const enter=step(0,.16),turn=step(.21,.40);
 return <g strokeLinecap="round" strokeLinejoin="round">
  <rect width="1920" height="1080" fill="#edf5e9"/>
  <path d="M0 870Q510 710 1010 860Q1550 720 1920 840V1080H0Z" fill="#c4dfcb"/>
  <circle cx="1560" cy="210" r="105" fill="#f6dca2"/>
  <g transform={`translate(${-480+enter*860} 315) scale(1.65)`}>
   <Cappy frame={frame} mouth={speaking?.2+Math.abs(Math.sin(frame*.45))*.3:0} pose={t<.22?'dance':t>.85?'explain':'point'}/>
  </g>
  {outro?<>
   <g transform={`translate(1170 ${330+(1-step(.04,.17))*480}) rotate(${-14*(1-step(.04,.17))})`}>
    <circle r={100+step(like,like+.035)*12} fill="#d5e6f4"/>
    <path d="M-52 5H-19L3-54Q11-82 26-60L24-14H57Q72-12 67 8L51 57H-20V8M-52 5V60H-25V5Z" fill={t>like?'#edc585':'#fffdf5'} stroke="#537b8b" strokeWidth="8"/>
   </g>
   <g transform={`translate(1500 ${340+(1-step(subscribe-.09,subscribe))*480}) rotate(${t>subscribe&&t<subscribe+.13?Math.sin((t-subscribe)*90)*14*(1-step(subscribe,subscribe+.13)):0})`}>
    <circle r="105" fill="#f5e4c4"/><path d="M-58 35Q-43 14-43-15Q-43-62 0-62Q43-62 43-15Q43 14 58 35Z" fill="#f3bf76" stroke="#997d61" strokeWidth="8"/>
    <circle cy="54" r="12" fill="#997d61"/>
    {[0,1].map(i=><path key={i} d={i?'M77-44Q108-8 80 24':'M-77-44Q-108-8-80 24'} fill="none" stroke="#b89863" strokeWidth="8" opacity={step(subscribe,subscribe+.04)*(1-step(subscribe+.10,subscribe+.17))}/>)}
   </g>
   {[0,1,2].map(i=>{const start=i===2?comment-.1:question+i*.13;const q=step(start,start+.1);return <g key={i} transform={`translate(${1130+i*170} ${780-i*55-(1-q)*260}) scale(${.4+.6*q})`} opacity={q}>
    <path d="M-105-62Q-125-62-125-35V35Q-125 62-95 62H-45L-65 103L5 62H96Q125 62 125 32V-32Q125-62 95-62Z" fill={['#b8d9cf','#d4c0e3','#f0cfb1'][i]} stroke="#708d91" strokeWidth="6"/>
    {[-45,0,45].map(x=><circle key={x} cx={x} r="10" fill="#fffdf5"/>)}
   </g>})}
  </>:<>
   <g transform={`translate(${1450-turn*180} 530) scale(${.5+enter*.5})`}>
    <path d="M-170-95Q-215-185-110-195Q-20-265 60-190Q190-210 192-83Q270 0 170 110Q130 220 15 170Q-120 230-170 100Q-255 30-170-95Z" fill="#cfb0df" stroke="#9477b3" strokeWidth="12"/>
    <ellipse rx="70" ry="95" fill="#e5d0ed"/>
   </g>
   {[0,1,2].map(i=>{const q=step(.27+i*.12,.52+i*.12);return <g key={i} transform={`translate(${1720-q*(350+i*90)} ${190+i*290+Math.sin(q*Math.PI)*100}) scale(${1-q*.25})`} opacity={1-step(.88,1)}>
    {Array.from({length:8},(_,k)=><path key={k} d="M0-32V-54" transform={`rotate(${k*45})`} stroke="#dc8c91" strokeWidth="10"/>)}<circle r="35" fill="#f0b5a7"/>
   </g>})}
   <path d="M800 580Q980 420 1130 520" fill="none" stroke="#89bcb4" strokeWidth="14" pathLength="1" strokeDasharray="1" strokeDashoffset={1-turn}/>
  </>}
 </g>;
};
