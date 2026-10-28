import {Cappy,type Pose} from './Cappy';
const ease=(v:number)=>{v=Math.max(0,Math.min(1,v));return v*v*(3-2*v)};
export const SpaceHost=({frame,frames,fps,outro,speaking,words}:{frame:number;frames:number;fps:number;outro:boolean;speaking:boolean;words:{text?:string;start:number;end:number}[]})=>{
 const t=frame/fps,phase=(a:number,b:number)=>ease((t-a)/Math.max(.001,b-a));
 const cue=(text:string,fallback:number)=>.15+(words.find(w=>w.text?.toLowerCase().replace(/[^a-z]/g,'')===text)?.start??fallback);
 const like=cue('like',2),sub=cue('subscribe',3),question=cue('which',5),comment=cue('comments',13);
 // Gaze prepares each gesture; the arm finishes its reach on the measured word.
 const events:{at:number;pose:Pose;look:number}[]=outro?[
  {at:0,pose:'explain',look:0},{at:like-.32,pose:'point',look:1},
  {at:question-.32,pose:'think',look:.6},{at:cue('or',question+4)-.32,pose:'shrug',look:1},
  {at:comment-.32,pose:'explain',look:.4},{at:cue('thanks',frames/fps-2)-.32,pose:'wave',look:0}
 ]:[
  {at:0,pose:'explain',look:0},{at:cue('hi',.15)-.1,pose:'wave',look:0},
  {at:cue('follow',2)-.32,pose:'point',look:1},{at:cue('death',4)-.32,pose:'think',look:1},
  {at:cue('future',7)-.32,pose:'explain',look:1},{at:cue('observed',10)-.32,pose:'point',look:1},
  {at:cue('predicts',13)-.32,pose:'shrug',look:.5}
 ];
 events.sort((a,b)=>a.at-b.at);
 let ei=0;while(ei<events.length-1&&events[ei+1].at<=t)ei++;
 const current=events[ei],prior=events[Math.max(0,ei-1)],mix=phase(current.at,current.at+.32);
 let gi=0;while(gi<events.length-1&&events[gi+1].at-.12<=t)gi++;
 const gaze=events[gi],gazePrior=events[Math.max(0,gi-1)];
 const look=gazePrior.look+(gaze.look-gazePrior.look)*phase(gaze.at-.12,gaze.at+.08);
 return <g strokeLinecap="round" strokeLinejoin="round">
  <g opacity={phase(0,.25)} transform="translate(340 370) scale(1.55)">
   <Cappy frame={frame} fps={fps} mouth={speaking?.22+.18*Math.abs(Math.sin(frame*.42)):0} pose={current.pose} poseFrom={prior.pose} poseMix={mix} look={look} gesture={phase(current.at+.2,current.at+1.5)}/>
  </g>
  {outro?<>
   <g opacity={phase(like-.5,like)} transform={`translate(1040 ${350+(1-phase(like-.5,like))*160})`}>
    <circle r="88" fill="#233c60"/><path d="M-48 0H-15L5-48Q12-66 25-49L23-12H55Q65-8 59 12L45 51H-14V3M-48 0V54H-22V0Z" fill="#f4cf90" stroke="#fff0cb" strokeWidth="5"/>
   </g>
   <g opacity={phase(sub-.4,sub)} transform={`translate(1325 350) rotate(${t>sub&&t<sub+1?Math.sin((t-sub)*15)*13*(1-phase(sub,sub+1)):0})`}>
    <circle r="88" fill="#233c60"/><path d="M-53 30Q-38 8-38-15Q-38-54 0-54Q38-54 38-15Q38 8 53 30Z" fill="#f4cf90"/><circle cy="47" r="10" fill="#fff0cb"/>
   </g>
   <g opacity={phase(question,question+1)}>
    <g transform={`translate(${1150-phase(question,question+1)*85} 640)`}><circle r="76" fill="#1d395c" stroke="#94dbda" strokeWidth="7"/><path d={`M0 0L${Math.sin(t*.4)*48} ${-Math.cos(t*.4)*48}M0 0H34`} fill="none" stroke="#f1d7a2" strokeWidth="7"/></g>
    <g transform="translate(1430 640)">{[0,1,2,3].map(i=><ellipse key={i} rx={35+i*19} ry={12+i*8} transform={`rotate(${i*36+t*9})`} fill="none" stroke={i%2?'#be9fe4':'#8cd6d8'} strokeWidth="5"/>)}<circle r="13" fill="#f9db9d"/></g>
   </g>
   {[0,1].map(i=><g key={i} opacity={phase(comment-.7+i*.3,comment+i*.3)} transform={`translate(${1100+i*260} ${875-i*45})`}><path d="M-95-45Q-115-45-115-25V25Q-115 45-90 45H-30L-44 75L10 45H90Q115 45 115 25V-25Q115-45 90-45Z" fill={i?'#b5a4d6':'#8dd0c7'}/>{[-40,0,40].map(x=><circle key={x} cx={x} r="8" fill="#fff8df"/>)}</g>)}
  </>:<>
   <path d="M880 720Q1130 930 1580 720" fill="none" stroke="#88d5d0" strokeWidth="9" pathLength="1" strokeDasharray="1" strokeDashoffset={1-phase(cue('follow',2),cue('future',7))}/>
   <circle cx={880+phase(cue('follow',2),cue('future',7))*700} cy={720+Math.sin(phase(cue('follow',2),cue('future',7))*Math.PI)*105} r="18" fill="#ffe1a4"/>
  </>}
 </g>;
};
