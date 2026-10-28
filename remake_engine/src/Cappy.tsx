import {useId} from 'react';
export type Pose='explain'|'smug'|'shock'|'pray'|'angry'|'laugh'|'think'|'sad'|'shrug'|'point'|'facepalm'|'dance'|'wave';
type Arm=[number,number,number,number,number,number,number,number];
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
const smooth=(v:number)=>{v=clamp(v);return v*v*(3-2*v)};
const arm=(pose:Pose,side:'left'|'right'):Arm=>{
 if(side==='left')return pose==='pray'?[105,188,70,225,130,226,145,193]:pose==='facepalm'?[104,193,58,173,106,104,110,102]:pose==='shrug'?[102,192,75,218,51,181,27,182]:pose==='dance'?[104,193,54,170,49,137,47,130]:pose==='sad'?[105,192,90,244,126,257,129,258]:[102,192,72,216,91,244,95,246];
 return pose==='pray'?[177,188,211,225,150,226,145,193]:pose==='point'?[180,191,211,198,250,153,265,151]:pose==='shrug'?[182,192,210,218,236,181,259,182]:pose==='dance'||pose==='wave'?[182,193,228,167,230,137,233,126]:pose==='think'?[182,194,215,190,190,143,185,139]:pose==='angry'?[183,194,224,186,214,159,209,156]:pose==='sad'?[181,192,198,243,161,257,157,258]:[182,194,220,218,245,194,253,190];
};
const armPath=(a:Arm,b:Arm,mix:number)=>{const p=a.map((n,i)=>n+(b[i]-n)*mix);return `M${p[0]} ${p[1]}Q${p[2]} ${p[3]} ${p[4]} ${p[5]}L${p[6]} ${p[7]}`};
const tilt=(p:Pose)=>p==='think'?-9:p==='shock'?5:p==='shrug'?-4:p==='wave'?-3:0;
/** Articulated, frame-driven doodle. Optional blending keeps existing callers compatible. */
export const Cappy=({frame,mouth,pose='explain',accent='white',poseFrom=pose,poseMix=1,look=0,gesture=0,fps=30}:{frame:number;mouth:number;pose?:Pose;accent?:string;poseFrom?:Pose;poseMix?:number;look?:number;gesture?:number;fps?:number})=>{
 const id=useId().replace(/:/g,''),mix=smooth(poseMix),t=frame/fps;
 const blink=(t%4.57)>4.43,talk=mouth>.07;
 const eyes=pose==='shock'||pose==='sad', grin=['smug','laugh','dance'].includes(pose);
 const headAngle=tilt(poseFrom)+(tilt(pose)-tilt(poseFrom))*mix+look*2;
 const left=armPath(arm(poseFrom,'left'),arm(pose,'left'),mix),right=armPath(arm(poseFrom,'right'),arm(pose,'right'),mix);
 const wave=pose==='wave'?Math.sin(clamp(gesture)*Math.PI*4)*14*Math.sin(clamp(gesture)*Math.PI)*mix:0;
 return <svg width="300" height="355" viewBox="0 0 300 355" overflow="visible"><defs><linearGradient id={`${id}paper`} x1="0" y1="0" x2=".8" y2="1"><stop offset="0" stopColor="#fffefb"/><stop offset=".62" stopColor="#fffefb"/><stop offset="1" stopColor="#e4edeb"/></linearGradient></defs><g fill={`url(#${id}paper)`} stroke="#121212" strokeWidth="3.3" strokeLinecap="round" strokeLinejoin="round">
  <ellipse cx="145" cy="330" rx="72" ry="9" fill="#182c35" opacity=".16" stroke="none"/>
  <g>
   <path d="M113 280L104 322L83 324M170 280L185 322L206 324" fill="none"/>
   <path d="M108 176Q93 202 105 280Q147 292 181 278L180 177Z"/>
   <path d="M171 202Q169 254 158 280L180 277L180 200Z" fill="#c6dbd9" opacity=".35" stroke="none"/>
   <path d={left} fill="none" strokeWidth="20"/><path d={left} fill="none" stroke="#e5eeec" strokeWidth="13"/>
   <g transform={`rotate(${wave} 182 193)`}><path d={right} fill="none" strokeWidth="20"/><path d={right} fill="none" stroke="#fffefb" strokeWidth="13"/></g>
   <path d="M105 184L144 216L181 181" fill={accent}/><path d="M105 184Q75 174 72 193Q89 201 105 184Q91 217 77 213Q79 194 105 184Z" fill={accent}/>
   <g transform={`rotate(${headAngle} 146 112)`}>
    <path d="M58 90Q35 65 54 56Q67 49 75 70"/>
    <path d="M47 102Q49 62 107 55Q160 49 190 67Q242 71 253 102L250 147Q239 181 180 182L93 178Q41 172 42 140Z"/>
    <path d="M65 83Q96 60 145 62M54 102Q53 88 61 82" fill="none" stroke="#fffefb" strokeWidth="6"/>
    <path d="M103 54L111 35M115 54L128 39" fill="none"/>
    <path d="M232 106L242 111L247 104M241 113L241 134M253 118L271 114M252 131L269 134" fill="none"/>
    {eyes?<><ellipse cx="96" cy="112" rx="13" ry="17"/><ellipse cx="163" cy="110" rx="13" ry="17"/><circle cx={98+look*3} cy="112" r="3" fill="#121212"/><circle cx={165+look*3} cy="111" r="3" fill="#121212"/></>:pose==='laugh'?<path d="M81 110L108 116L83 124M151 110L176 116L153 124" fill="none"/>:<><path d={pose==='angry'?'M81 105L112 115M147 115L177 104':'M78 110L111 106M145 106L178 101'} fill="none"/>{!blink&&<><path transform={'translate('+look*3+' 0)'} d="M95 111L96 118L104 117L105 109" fill="#121212"/><path transform={'translate('+look*3+' 0)'} d="M161 106L162 114L170 113L171 105" fill="#121212"/></>}</>}
    <path d={pose==='angry'?'M80 93L106 101M150 96L176 88':'M91 91L108 86M154 85L170 85'} fill="none"/>
    {talk?<ellipse cx="139" cy="146" rx={9+mouth*11} ry={3+mouth*16} fill="#343438"/>:pose==='shock'?<ellipse cx="137" cy="148" rx="9" ry="15"/>:grin?<path d="M115 140Q143 158 169 138Q147 174 115 140Z"/>:<path d={pose==='sad'?'M120 152Q137 135 154 151':pose==='angry'?'M121 153Q135 139 154 150':'M118 144Q135 152 151 143'} fill="none"/>}
    {pose==='sad'&&<><path d="M93 132L89 162M162 130L166 160" stroke="#7bb6d4" strokeWidth="6"/></>}
   </g>
  </g>
 </g></svg>;
};
