type Props={sceneId:string;frame:number;frames:number;fps:number};
type Label={id:string;text:string;x:number;y:number;targetX:number;targetY:number;start:number;end:number;color:string};
const clamp=(value:number)=>Math.max(0,Math.min(1,value));
const ease=(value:number)=>{const q=clamp(value);return q*q*(3-2*q)};
const phase=(p:number,a:number,b:number)=>ease((p-a)/(b-a));
const lerp=(a:number,b:number,p:number)=>a+(b-a)*p;

/** Brief identifiers, using the same scene-local trajectory equations as
 * ContinuousBiology. Render above the biology SVG, below source-media inserts.
 * These identify the depicted entities; they are not narration subtitles. */
export const BiologyLabels=({sceneId,frame,frames,fps}:Props)=>{
 const p=clamp(frame/Math.max(1,frames-1)),seconds=frame/fps,duration=frames/fps;
 const labels:Label[]=[];
 const add=(id:string,text:string,x:number,y:number,targetX:number,targetY:number,start:number,end:number,color:string)=>{
  labels.push({id,text,x,y,targetX,targetY,start,end,color});
 };
 switch(sceneId){
  case 'scene-01':{
   // Virus: (320,360) -> (995,455), phase .04–.34; fades from .38.
   const travel=phase(p,.04,.34),vx=lerp(320,995,travel),vy=lerp(360,455,travel);
   add('virus','Virus',vx,vy+112,vx,vy+52,.25,Math.min(3.45,duration*.37),'#ba5969');
   // Fixed tumor (1080,530), radius190. Its concealment starts clearing .22.
   const start=duration*.27;
   add('tumor','Cancer cell',1080,245,1080,333,start,Math.min(start+3.2,duration*.66),'#80549d');
   break;
  }
  case 'scene-04':{
   // Large cell (1040,540), radius285; incoming virus has fixed y430.
   const vx=lerp(320,790,phase(p,.04,.3));
   add('cell','Cell',1040,175,1040,245,.55,3.75,'#547d64');
   add('virus','Virus',vx,558,vx,492,.3,Math.min(3.5,duration*.37),'#ba5969');
   break;
  }
  case 'scene-05':{
   // First defended healthy cell (650,500), radius165; tumor (1570,510), r155.
   add('healthy','Healthy cell',650,244,650,325,.55,3.85,'#547d64');
   const start=Math.max(1.2,duration*.34);
   add('tumor','Cancer cell',1570,260,1570,345,start,start+3.2,'#80549d');
   break;
  }
  case 'scene-22':{
   add('resistant','Resistant cancer cell',1070,252,1070,345,1.0,4.3,'#80549d');
   break;
  }
  case 'scene-08':{
   const arrive=phase(p,.65,1),cx=lerp(230,610,arrive),cy=lerp(780,620,arrive);
   add('immune','Immune cell',cx+45,cy-205,cx,cy-135,4.0,7.2,'#267e77');
   break;
  }
  case 'scene-09':{
   // Presenter moves580->1040 at .31–.66; responder1600->1350 at .56–.86.
   const cx=lerp(580,1040,phase(p,.31,.66));
   add('presenter','Immune cell',cx,280,cx,360,4.0,7.2,'#267e77');
   const tx=lerp(1600,1350,phase(p,.56,.86)),start=4.3;
   add('responder','T cell',tx,315,tx,390,start,Math.min(start+3.2,duration*.85),'#267e77');
   break;
  }
  default:return null;
 }
 return <g pointerEvents="none" aria-label="Biological entity labels">
  {labels.map(label=>{
   if(seconds<label.start||seconds>=label.end)return null;
   const opacity=ease((seconds-label.start)/.25)*ease((label.end-seconds)/.35);
   const width=label.text.length*19+48,height=64;
   const x=Math.max(width/2+36,Math.min(1884-width/2,label.x));
   const lineY=label.targetY>label.y?label.y+height/2:label.y-height/2;
   return <g key={label.id} opacity={opacity}>
    <path d={`M${x} ${lineY} Q${x} ${(lineY+label.targetY)/2} ${label.targetX} ${label.targetY}`} fill="none" stroke={label.color} strokeWidth="2.5" strokeLinecap="round" opacity=".7"/>
    <circle cx={label.targetX} cy={label.targetY} r="4" fill={label.color}/>
    <rect x={x-width/2} y={label.y-height/2+3} width={width} height={height} rx="25" fill="#233f40" opacity=".09"/>
    <rect x={x-width/2} y={label.y-height/2} width={width} height={height} rx="25" fill="#fffdf5" fillOpacity=".96" stroke={label.color} strokeOpacity=".24" strokeWidth="2"/>
    <text x={x} y={label.y+1} fill={label.color} textAnchor="middle" dominantBaseline="middle" fontFamily="Arial, Helvetica, sans-serif" fontSize="35" fontWeight="600">{label.text}</text>
   </g>;
  })}
 </g>;
};
