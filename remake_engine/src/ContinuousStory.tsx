const ease=(x:number)=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x)};
const p=(t:number,a:number,b:number)=>ease((t-a)/(b-a));
const lerp=(a:number,b:number,t:number)=>a+(b-a)*t;
const Person=({x,y,scale=1,walk=0,coat=false,arm=0}:{x:number;y:number;scale?:number;walk?:number;coat?:boolean;arm?:number})=><g transform={`translate(${x} ${y}) scale(${scale})`} strokeLinecap="round" strokeLinejoin="round">
 <ellipse cy="180" rx="68" ry="15" fill="#244559" opacity=".08"/>
 <path d={`M-28 85Q${-30+walk*20} 130 ${-38+walk*45} 168M28 85Q${30-walk*20} 130 ${38-walk*45} 168`} fill="none" stroke="#3c6079" strokeWidth="31"/>
 <path d="M-47-55Q-68 0-50 95Q0 119 50 95Q68 0 47-55Q0-80-47-55Z" fill={coat?'#fffef7':'#6dbdb7'} stroke="#3d7484" strokeWidth="5"/>
 <path d={`M-43-32Q-97 10 ${-80-arm*25} ${45-arm*75}M43-32Q${87+arm*20} ${20-arm*65} ${82+arm*65} ${38-arm*95}`} fill="none" stroke={coat?'#fffef7':'#6dbdb7'} strokeWidth="27"/>
 <circle cy="-112" r="56" fill="#dca584"/><path d="M-54-114Q-65-181 2-179Q68-178 54-107Q38-150 10-137Q-27-111-54-114Z" fill="#654f60"/>
 <circle cx="-18" cy="-109" r="4" fill="#40536c"/><circle cx="18" cy="-109" r="4" fill="#40536c"/><path d="M-14-86Q0-76 14-86" fill="none" stroke="#9b6366" strokeWidth="4"/>
 {coat&&<path d="M-23-58L0-10L23-58M0-10V95" fill="none" stroke="#a9cfce" strokeWidth="5"/>}
</g>;
const Dish=({x,y,scale=1}:{x:number;y:number;scale?:number})=><g transform={`translate(${x} ${y}) scale(${scale})`}><path d="M-100-12V30Q0 83 100 30V-12" fill="#c4e7e4" stroke="#6daeb6" strokeWidth="6"/><ellipse rx="100" ry="35" cy="-12" fill="#eaf8ef" stroke="#6daeb6" strokeWidth="6"/></g>;
const Tumor=({x,y,r=50}:{x:number;y:number;r?:number})=><g transform={`translate(${x} ${y}) scale(${r/50})`}><path d="M-46-10Q-63-45-24-48Q5-76 31-48Q67-45 51-12Q76 26 37 41Q14 65-15 45Q-61 50-46 12Q-63 0-46-10Z" fill="url(#story-purple)" stroke="#8e6aaf" strokeWidth="4"/><ellipse cx="-11" cy="-13" rx="13" ry="18" fill="#dbbce8"/><ellipse cx="23" cy="15" rx="11" ry="14" fill="#b38ac9"/></g>;
const Virus=({x,y,r=30}:{x:number;y:number;r?:number})=><g transform={`translate(${x} ${y}) scale(${r/30})`} stroke="#dc8c91" strokeLinecap="round" strokeWidth="7">{Array.from({length:8},(_,i)=><path key={i} d="M0-27V-42" transform={`rotate(${i*45})`}/>)}<circle r="29" fill="#f5b0a2"/><path d="M-14 8Q-24-13-3-15Q15-24 15 0Q10 20-14 8" fill="none" stroke="#ffe5bc" strokeWidth="5"/></g>;
const Care=({x,y,kind=0}:{x:number;y:number;kind?:number})=><g transform={`translate(${x} ${y})`} strokeLinecap="round" strokeLinejoin="round">
 <circle r="90" fill="#ffffff" opacity=".8"/>
 {kind===0?<><path d="M-42 35Q-65 5-34-19L28-66Q53-82 68-58Q75-43 54-27L-3 17" stroke="#7b9eae" strokeWidth="15" fill="none"/><path d="M-30 21L-62 58" stroke="#b0cace" strokeWidth="13"/></>:kind===1?<><rect x="-37" y="-56" width="74" height="112" rx="37" fill="#edb4a7"/><path d="M-37 0H37V19Q37 57 0 57Q-37 57-37 19Z" fill="#fff2dc"/></>:<><path d="M0 50V-5M0-5Q-20-35-44-46M0-5Q20-35 44-46" fill="none" stroke="#e6bf78" strokeWidth="22"/></>}
</g>;

const Paper=({x,y,scale=1,progress=1}:{x:number;y:number;scale?:number;progress?:number})=><g transform={`translate(${x} ${y}) scale(${scale})`}>
 <rect x="-110" y="-145" width="220" height="290" rx="25" fill="#fffdf3" stroke="#a2bcb9" strokeWidth="6"/>
 <circle cy="-65" r="42" fill="#d8e9dd"/><path d="M-22-67Q0-102 23-67Q39-37 0-30Q-35-39-22-67" fill="#a17caf"/>
 <path d="M-72 55Q-40 10-10 45T70 20" fill="none" stroke="#84b9b0" strokeWidth="8" pathLength="1" strokeDasharray="1" strokeDashoffset={1-progress}/>
 <circle cx="-58" cy="108" r="9" fill="#b9d4ca"/><circle cx="-10" cy="108" r="9" fill="#dcbeb6"/><circle cx="38" cy="108" r="9" fill="#c6c5dc"/>
</g>;
const Bottle=({x,y,scale=1,color='#b9d8d1'}:{x:number;y:number;scale?:number;color?:string})=><g transform={`translate(${x} ${y}) scale(${scale})`}>
 <rect x="-33" y="-85" width="66" height="34" rx="9" fill="#7796a7"/><path d="M-29-52V-26Q-53-16-53 5V77Q-53 96-30 96H30Q53 96 53 77V5Q53-16 29-26V-52Z" fill="#f1f8f2" stroke="#7ca6ad" strokeWidth="6"/>
 <path d="M-46 25H46V76Q46 88 29 88H-29Q-46 88-46 76Z" fill={color}/><path d="M-29-6V52" stroke="#fff" strokeWidth="8" opacity=".6"/>
</g>;
const Seat=({x,y}:{x:number;y:number})=><g transform={`translate(${x} ${y})`}><rect x="-95" y="-95" width="190" height="160" rx="40" fill="#aacbc5"/><rect x="-120" y="40" width="240" height="60" rx="28" fill="#7daaa9"/><path d="M-76 95V190M76 95V190" stroke="#688e98" strokeWidth="15"/></g>;
const Link=({d,q,color='#83b7ae',width=9}:{d:string;q:number;color?:string;width?:number})=><path d={d} fill="none" stroke={color} strokeWidth={width} pathLength="1" strokeDasharray="1" strokeDashoffset={1-q}/>;
const Body=({x,y,scale=1}:{x:number;y:number;scale?:number})=><g transform={`translate(${x} ${y}) scale(${scale})`}>
 <circle cy="-150" r="49" fill="#e7c7b4"/><path d="M-44-95Q-105-83-110 0L-92 96Q-67 116-64 85L-58 20V195Q-55 220-30 213L0 80L30 213Q55 220 58 195V20L64 85Q67 116 92 96L110 0Q105-83 44-95Z" fill="#e6c7b6" stroke="#bfabac" strokeWidth="5"/>
</g>;

export const ContinuousStory=({sceneId,frame,frames,fps}:{sceneId:string;frame:number;frames:number;fps:number})=>{
 const t=frame/Math.max(1,frames-1),sec=frame/fps,n=Number(sceneId.slice(-2));
 const a=p(t,.03,.27),b=p(t,.28,.56),c=p(t,.57,.81),d=p(t,.81,1);
 let action:React.ReactNode=null;
 switch(n){
 case 2:{ // Recurrence creates a new decision: patient, medical history, new route.
  const turn=p(t,.43,.77);
  action=<g>
   <Seat x={530} y={650}/><Person x={lerp(250,530,a)} y={580} scale={1.12} walk={Math.sin(sec*6)*(1-a)} arm={b*.5}/>
   <rect x="805" y="470" width="780" height="230" rx="55" fill="#b8d3cc"/><path d="M860 700V885M1530 700V885" stroke="#89aaa9" strokeWidth="20"/>
   <Paper x={lerp(1060,925,a)} y={lerp(530,440,a)} scale={.75} progress={b}/>
   <g opacity={p(t,.2,.4)}><Body x={1370} y={360} scale={.68}/><Tumor x={1390} y={320} r={27}/><circle cx="1390" cy="320" r={35+b*24} fill="none" stroke="#b58bc5" strokeWidth="5" opacity={1-b*.5}/></g>
   <Link d="M940 660Q1140 890 1490 765" q={turn} color="#c8aa8b" width={13}/>
   <g transform={`translate(${lerp(960,1480,turn)} ${lerp(660,760,turn)-Math.sin(turn*Math.PI)*70})`} opacity={turn}><Virus x={0} y={0} r={33}/></g>
   <Person x={lerp(1790,1650,c)} y={610} coat scale={.85} arm={d*.6}/>
  </g>;break;
 }
 case 11:{ // Baseline local anatomy and consultation; no scanner or extraction.
  const reveal=p(t,.18,.48),focus=p(t,.48,.82);
  action=<g>
   <Person x={370} y={650} scale={1.05} arm={a*.45}/><Person x={740} y={620} coat scale={1.05} arm={b*.75}/>
   <rect x="1030" y="190" width="660" height="620" rx="65" fill="#f4f7ec" stroke="#a5c5bd" strokeWidth="12"/>
   <g opacity={1-focus*.6}><Body x={1310} y={485} scale={1.12}/><Tumor x={1342} y={425} r={28}/></g>
   <Link d="M1340 425Q1490 330 1520 470" q={focus} color="#b390c0"/>
   <g opacity={focus} transform={`translate(${lerp(1340,1515,focus)} ${lerp(425,585,focus)})`}>
    <rect x="-110" y="-100" width="220" height="190" rx="42" fill="#e8b8a6"/><path d="M-90-55H90M-90 45Q0 15 90 45" stroke="#bc8f93" strokeWidth="26" fill="none"/><Tumor x={0} y={-8} r={48}/>
   </g>
   <path d="M870 350Q925 275 1010 340" stroke="#89b3ac" strokeWidth="8" fill="none" opacity={reveal}/>
   <circle cx={lerp(835,995,reveal)} cy={lerp(400,345,reveal)} r="13" fill="#91bcb3" opacity={reveal}/>
  </g>;break;
 }
 case 12:{ // Specialized laboratory access and two distinct preparations.
  const access=p(t,.04,.3),prepare=p(t,.3,.66),finish=p(t,.67,.95);
  action=<g>
   <rect x="180" y="180" width="330" height="650" rx="55" fill="#c7dce0" stroke="#8aaeb9" strokeWidth="15"/><rect x={lerp(220,450,access)} y="220" width="250" height="570" rx="30" fill="#ecf3e9" opacity={1-access*.6}/>
   <Person x={lerp(210,680,access)} y={650} coat scale={1.05} walk={Math.sin(sec*6)*(1-access)} arm={prepare*.55}/>
   <rect x="910" y="220" width="730" height="600" rx="50" fill="#dcece6" stroke="#96b9b7" strokeWidth="14"/><rect x="950" y="270" width="650" height="365" rx="20" fill="#eff8ef" fillOpacity=".7"/>
   <path d="M920 760H1630M1030 820V950M1520 820V950" stroke="#789caa" strokeWidth="22"/>
   {[0,1].map(i=><g key={i} transform={`translate(${lerp(970+i*340,1110+i*300,prepare)} ${lerp(710,575,prepare)})`}>
    <Bottle x={0} y={0} scale={.85} color={i?'#d7c0df':'#eac2b4'}/><Virus x={0} y={25} r={i?21:16}/>
   </g>)}
   <path d={`M1040 ${lerp(280,420,finish)}H1510`} stroke="#91b6bc" strokeWidth="14"/>
   <rect x="1000" y="650" width="555" height="80" rx="25" fill="#b6d2c8" opacity={finish}/>
   <g opacity={finish}><path d="M1660 530V585Q1660 640 1700 665Q1740 640 1740 585V530Z" fill="#d6e8d9" stroke="#8cae9f" strokeWidth="6"/><path d="M1683 588L1698 605L1720 568" stroke="#719b8b" strokeWidth="7" fill="none"/></g>
  </g>;break;
 }
 case 13:{ // The only imaging scene: probe sweeps, matching image evolves.
  const sweep=p(t,.13,.74),change=p(t,.4,.88),probeX=lerp(660,940,sweep);
  action=<g>
   <rect x="280" y="720" width="820" height="76" rx="37" fill="#edf3eb" stroke="#91aaa9" strokeWidth="8"/><path d="M360 800V915M1000 800V915" stroke="#8da6aa" strokeWidth="24"/>
   <circle cx="410" cy="645" r="53" fill="#deb095"/><path d="M465 635Q680 570 965 665L1010 717H455Z" fill="#8dbbb7"/>
   <Person x={1130} y={640} coat arm={.65+sweep*.15}/>
   <path d={`M1140 520Q1110 330 ${probeX} 425V590`} fill="none" stroke="#7795a5" strokeWidth="12"/>
   <g transform={`translate(${probeX} 599)`}><rect x="-25" y="-58" width="50" height="80" rx="18" fill="#e0eae3" stroke="#7d9aa9" strokeWidth="5"/><path d="M-36 20Q0 36 36 20" stroke="#708d9a" strokeWidth="14"/></g>
   <rect x="1270" y="250" width="440" height="355" rx="42" fill="#5b7c88"/><rect x="1300" y="280" width="380" height="285" rx="25" fill="#294a61"/>
   <path d="M1340 375Q1470 315 1640 360M1340 495Q1470 445 1640 485" fill="none" stroke="#80aaa8" strokeWidth="14"/>
   <g transform={`translate(${1475+change*12} ${420+Math.sin(change*Math.PI)*18})`}><Tumor x={0} y={0} r={lerp(67,43,change)}/></g>
   <path d={`M${1320+sweep*330} 300V550`} stroke="#c2e5d7" strokeWidth="3" opacity=".45"/>
   <path d="M1490 605V735M1390 735H1590" stroke="#7996a0" strokeWidth="20"/>
   <Paper x={1550} y={lerp(940,825,d)} scale={.4} progress={d}/>
  </g>;break;
 }
 case 15:{ // The single extraction: one tumor follows one continuous trajectory.
  const lift=p(t,.25,.59),care=p(t,.63,.87),depart=p(t,.84,1);
  const tx=lerp(830,1390,lift),ty=lerp(635,710,lift)-Math.sin(lift*Math.PI)*220;
  action=<g>
   <rect x="260" y="700" width="820" height="65" rx="32" fill="#eaf0e7" stroke="#91aaa9" strokeWidth="8"/><path d="M350 770V930M1000 770V930" stroke="#8da6aa" strokeWidth="24"/>
   <circle cx="390" cy="625" r="50" fill="#deb095"/><path d="M450 620Q660 580 970 655L1010 697H445Z" fill="#73aaa6"/>
   <Person x={1050} y={485} coat scale={.95} arm={p(t,.06,.3)*.8}/>
   <path d="M470 270Q730 175 950 270" stroke="#b3c9c1" strokeWidth="24" fill="none"/><ellipse cx="710" cy="280" rx="110" ry="35" fill="#fcf7d7"/>
   <Dish x={1390} y={735} scale={1.1}/>
   <Tumor x={tx} y={ty} r={35}/>
   <g opacity={p(t,.15,.25)*(1-p(t,.59,.68))}><path d={`M${tx-8} ${ty-125}Q${tx-32} ${ty-60} ${tx-20} ${ty-8}M${tx+8} ${ty-125}Q${tx+32} ${ty-60} ${tx+20} ${ty-8}`} stroke="#b0c7ca" strokeWidth="9" fill="none"/></g>
   <g opacity={care} transform={`translate(${lerp(1640,1580,care)} 380)`}><Bottle x={0} y={0} color="#e5c6a0"/><path d="M0 100Q80 160 30 230" stroke="#c6a783" strokeWidth="8" fill="none"/></g>
   <g opacity={depart}><Person x={lerp(1440,1620,depart)} y={800} scale={.7} walk={Math.sin(sec*5)*depart}/></g>
  </g>;break;
 }
 case 16:{ // Attribution: three contributions feed one follow-up record.
  const visit=p(t,.02,.25),medicine=p(t,.2,.56),review=p(t,.5,.92);
  action=<g>
   <Seat x={520} y={650}/><Person x={lerp(280,520,visit)} y={570} scale={1.05} walk={Math.sin(sec*5)*(1-visit)}/>
   <Person x={1040} y={610} coat arm={review*.7}/><path d="M730 750H1260M800 770V900M1200 770V900" stroke="#93b1aa" strokeWidth="22"/>
   <Bottle x={lerp(1100,740,medicine)} y={690} scale={.65} color="#e6c6a3"/>
   <Paper x={1430} y={560} scale={1.15} progress={review}/>
   <Virus x={1280} y={245} r={35}/><g transform="translate(1490 245) scale(.6)"><Care x={0} y={0} kind={0}/></g><Bottle x={1680} y={245} scale={.5}/>
   {[0,1,2].map(i=><Link key={i} d={`M${1280+i*200} 305Q${1280+i*200} 380 1430 410`} q={p(t,.45+i*.08,.68+i*.08)} color={['#dba8a1','#9cb5c5','#d8c5a5'][i]} width={7}/>)}
   <path d="M1260 820Q1430 900 1600 820" fill="none" stroke="#a7c7bb" strokeWidth="12" pathLength="1" strokeDasharray="1" strokeDashoffset={1-d}/>
  </g>;break;
 }
 case 17:{ // One observational file; an empty comparison remains visibly empty.
  const open=p(t,.12,.5),inspect=p(t,.48,.85);
  action=<g>
   <Person x={400} y={630} scale={1.2} arm={a*.6}/>
   <path d="M640 800H1540" stroke="#a8bfb4" strokeWidth="23"/>
   <g transform={`translate(${lerp(550,900,open)} ${lerp(620,500,open)}) rotate(${lerp(-12,0,open)})`}><Paper x={0} y={0} scale={1.35} progress={open}/></g>
   <rect x="1240" y="300" width="280" height="390" rx="40" fill="none" stroke="#bdc7c2" strokeWidth="7" strokeDasharray="14 18"/>
   <path d="M1050 500H1190" stroke="#b8b6c0" strokeWidth="7" strokeDasharray="12 18" opacity={open}/>
   <g transform={`translate(${lerp(630,970,inspect)} ${lerp(300,510,inspect)})`}><circle r="115" fill="#d6efea" fillOpacity=".12" stroke="#719ca5" strokeWidth="17"/><path d="M82 85L165 170" stroke="#719ca5" strokeWidth="30"/></g>
   {[0,1,2].map(i=><circle key={i} cx={1300+i*80} cy="760" r="12" fill="#b7c6c1" opacity={p(t,.75+i*.05,.85+i*.05)}/>)}
  </g>;break;
 }
 case 18:{ // Research history travels across a bench toward a specific approval.
  const progress=p(t,.07,.84);
  action=<g>
   <path d="M240 740Q800 640 1650 740" fill="none" stroke="#a9c4bb" strokeWidth="18"/>
   {[0,1,2,3].map(i=>{const q=p(t,.03+i*.17,.24+i*.17);return <g key={i} transform={`translate(${330+i*365} ${lerp(830,500,q)})`} opacity={q}>
    {i===0?<><Dish x={0} y={40} scale={.85}/><Virus x={0} y={10} r={27}/></>:i===1?<><Paper x={0} y={-5} scale={.75} progress={q}/><Paper x={30} y={20} scale={.7} progress={q}/></>:i===2?<><Person x={-50} y={0} scale={.5} coat/><Person x={65} y={30} scale={.45}/></>:<><Bottle x={0} y={0} scale={1.15} color="#d7bfdd"/><circle cx="80" cy="80" r="37" fill="#d3e8d2"/><path d="M61 80L76 95L103 60" fill="none" stroke="#73a18b" strokeWidth="10"/></>}
   </g>;})}
   <circle cx={lerp(240,1650,progress)} cy={740-Math.sin(progress*Math.PI)*70} r="21" fill="#c7a582"/>
   <g opacity={d}><rect x="1320" y="205" width="330" height="90" rx="40" fill="#e6d5c8"/><ellipse cx="1480" cy="247" rx="36" ry="23" fill="#96758c"/></g>
  </g>;break;
 }
 case 19:{ // Specific eligibility: one recognized setting, others remain separate.
  const select=p(t,.12,.55),arrive=p(t,.55,.88);
  action=<g>
   {[0,1,2].map(i=><g key={i} transform={`translate(${540+i*470} 560)`}>
    <rect x="-165" y="-210" width="330" height="420" rx="70" fill={i===0?'#f0ead9':'#e4eae3'} stroke={i===0?'#b49d84':'#b3c4c0'} strokeWidth="9"/>
    {i===0?<><path d="M-120-50Q0-90 120-50V75Q0 110-120 75Z" fill="#e3b7a4"/><ellipse cy="4" rx="42" ry="28" fill="#927383"/></>:i===1?<Body x={0} y={0} scale={.6}/>:<><ellipse cx="-48" cy="0" rx="55" ry="90" fill="#c6abbf"/><ellipse cx="48" cy="0" rx="55" ry="90" fill="#c6abbf"/></>}
    {i>0&&<path d="M-110 120H110" stroke="#b4c4c0" strokeWidth="15"/>}
   </g>)}
   <Bottle x={lerp(1020,540,select)} y={lerp(200,340,arrive)} scale={.7} color="#d4bdd9"/>
   <path d="M400 820Q540 900 680 820" fill="none" stroke="#9fc5aa" strokeWidth="12" pathLength="1" strokeDasharray="1" strokeDashoffset={1-arrive}/>
   <Person x={1740} y={720} coat scale={.75} arm={select*.6}/>
  </g>;break;
 }
 case 23:{ // A tool cabinet opens; tools are considered together, not replaced.
  const open=p(t,.05,.42),choose=p(t,.45,.87);
  action=<g>
   <Person x={410} y={650} coat scale={1.2} arm={open*.7}/>
   <rect x="740" y="275" width="900" height="550" rx="65" fill="#d6e5dc" stroke="#a1bbb6" strokeWidth="12"/>
   <path d="M780 535H1600M1190 310V790" stroke="#a4bcb5" strokeWidth="10"/>
   <g transform={`translate(${lerp(1180,1650,open)} 300)`} opacity={1-open}><rect width="430" height="495" rx="40" fill="#b0c9c3"/></g>
   <Care x={970} y={420} kind={0}/><Bottle x={1390} y={420} scale={.7}/><Care x={1390} y={670} kind={2}/>
   <g transform="translate(970 670)"><circle r="70" fill="#fbf5df"/><path d="M-85-40Q0-100 85-40M-55-15Q0-55 55-15M0 0V55" fill="none" stroke="#acb5c9" strokeWidth="15"/></g>
   <rect x={lerp(800,1250,choose)} y={lerp(315,565,choose)} width="280" height="220" rx="44" stroke="#c7aa77" strokeWidth="8" fill="none"/>
   <Virus x={lerp(280,655,d)} y={lerp(300,500,d)} r={33}/>
  </g>;break;
 }
 case 24:{ // Matched comparison lanes, multiple measurements over time.
  const enroll=p(t,.03,.35),measure=p(t,.3,.9);
  action=<g>
   <path d="M300 440H1600M300 740H1600" stroke="#bdd2c7" strokeWidth="17"/>
   {[0,1].map(row=><g key={row}>
    {[0,1,2].map(i=><Person key={i} x={lerp(290+i*50,430+i*190,enroll)} y={340+row*300} scale={.45} walk={Math.sin(sec*5)*(1-enroll)}/>)}
    {[0,1,2].map(i=>{const q=p(t,.33+i*.14,.52+i*.14);return <g key={i} opacity={q} transform={`translate(${1050+i*245} ${350+row*300})`}>
     <circle r="65" fill="#f5f7ee" stroke="#a1bbb6" strokeWidth="5"/>
     {i===0?<Tumor x={0} y={0} r={row?29:24}/>:i===1?<path d="M-38 5L-17 5L-4-25L13 29L28 0H43" stroke={row?'#c6a48c':'#ca9da4'} strokeWidth="7" fill="none"/>:<path d={`M-35 20L-10 ${row?-5:5}L13 ${row?9:-15}L40-22`} stroke="#88ada8" strokeWidth="7" fill="none"/>}
    </g>;})}
   </g>)}
   <path d={`M${lerp(900,1640,measure)} 200V815`} stroke="#7caba7" strokeWidth="6" opacity=".5"/>
   <Person x={1725} y={775} coat scale={.7} arm={d*.65}/>
  </g>;break;
 }
 case 25:{ // Time, evidence accumulation, and an explicit safety stop.
  const elapsed=p(t,.05,.9),assess=p(t,.48,.94);
  action=<g>
   <Seat x={420} y={665}/><Person x={420} y={585} scale={1.1} arm={p(t,.1,.4)*.25}/>
   <g transform="translate(850 520)"><path d="M-125-230H125M-125 230H125" stroke="#a0aaa3" strokeWidth="24"/><path d="M-110-215Q-110-70-12 0Q-110 70-110 215H110Q110 70 12 0Q110-70 110-215Z" fill="#e8f1e4" stroke="#9fbcb5" strokeWidth="9"/>
    <path d={`M-90 ${-185+elapsed*140}H90Q70-65 0-25Q-70-65-90 ${-185+elapsed*140}`} fill="#d9c390" opacity={1-elapsed*.8}/>
    <path d={`M-90 205Q0 ${205-elapsed*170} 90 205Z`} fill="#d9c390"/><path d="M0-20V145" stroke="#d9c390" strokeWidth="5" opacity={1-p(t,.88,1)}/>
   </g>
   {[0,1,2].map(i=><g key={i} opacity={p(t,.22+i*.16,.4+i*.16)}><Paper x={1250+i*85} y={570-i*50} scale={.65} progress={assess}/></g>)}
   <g transform={`translate(${lerp(1620,1480,assess)} ${lerp(300,360,assess)})`} opacity={assess}><path d="M-65-70Q0-105 65-70V5Q65 68 0 110Q-65 68-65 5Z" fill="#ead2c2" stroke="#bd9c92" strokeWidth="7"/><path d="M-28 0H28" stroke="#b4898c" strokeWidth="12"/></g>
  </g>;break;
 }
 case 26:{ // A private decision becomes publicity; the uncertainty stays with it.
  const publish=p(t,.18,.58),spread=p(t,.48,.89);
  action=<g>
   <Person x={500} y={620} coat scale={1.2} arm={a*.6}/>
   <path d="M300 820H900" stroke="#a9bdb2" strokeWidth="23"/><Paper x={750} y={630} scale={.65} progress={a}/>
   <g transform={`translate(${lerp(750,1120,publish)} ${lerp(630,430,publish)})`} opacity={publish}><rect x="-105" y="-180" width="210" height="360" rx="34" fill="#6e909d"/><rect x="-88" y="-145" width="176" height="273" rx="15" fill="#f1f5e7"/><Virus x={0} y={-25} r={39}/><circle cy="151" r="12" fill="#c2d7d2"/></g>
   {[0,1,2].map(i=>{const q=p(t,.45+i*.09,.7+i*.09),x=1510+i%2*170,y=290+i*240;return <g key={i}><Link d={`M1230 430Q1360 ${y} ${x} ${y}`} q={q} color="#b6bbc9" width={7}/><Person x={x} y={y+40} scale={.45} arm={q*.3}/></g>;})}
   <g opacity={spread}><circle cx="1120" cy="800" r="75" fill="#eee4cc" stroke="#c9b996" strokeWidth="7"/><path d="M1092 770Q1092 735 1120 735Q1160 735 1145 777Q1120 790 1120 810M1120 837V841" fill="none" stroke="#9e8e7f" strokeWidth="10"/></g>
  </g>;break;
 }
 case 27:{ // Patient approaches the team, referral moves to a trial pathway.
  const arrive=p(t,.03,.34),discuss=p(t,.3,.65),refer=p(t,.64,.96);
  action=<g>
   <Person x={lerp(220,620,arrive)} y={660} scale={1.1} walk={Math.sin(sec*5)*(1-arrive)} arm={discuss*.4}/>
   <ellipse cx="1080" cy="750" rx="420" ry="105" fill="#a8c8bb"/>
   <Person x={1030} y={535} coat scale={.88} arm={discuss*.7}/><Person x={1390} y={610} coat scale={.9} arm={refer*.5}/>
   <Paper x={lerp(1050,790,discuss)} y={700} scale={.45} progress={discuss}/>
   <Link d="M1180 790Q1390 990 1630 770" q={refer} width={14}/>
   <g opacity={refer} transform={`translate(1640 ${lerp(910,690,refer)})`}><rect x="-115" y="-125" width="230" height="250" rx="38" fill="#eef4e7" stroke="#9bb9b0" strokeWidth="7"/><Person x={-44} y={5} scale={.3}/><Person x={44} y={5} scale={.3} coat/></g>
  </g>;break;
 }
 case 29:{ // A clue feeds a larger, explicitly unfinished research construction.
  const inspect=p(t,.05,.32),build=p(t,.3,.9);
  action=<g>
   <Paper x={430} y={570} scale={1.1} progress={inspect}/>
   <g transform={`translate(${lerp(200,475,inspect)} ${lerp(250,500,inspect)})`}><circle r="85" fill="#d6efea" fillOpacity=".15" stroke="#789ca9" strokeWidth="13"/><path d="M60 60L130 135" stroke="#789ca9" strokeWidth="25"/></g>
   <Link d="M620 570Q740 370 930 490" q={build} width={10}/>
   {[0,1,2,3,4].map(i=>{const q=p(t,.3+i*.09,.5+i*.09),x=1010+i%3*220,y=430+Math.floor(i/3)*260;return <g key={i} transform={`translate(${lerp(730,x,q)} ${lerp(780,y,q)})`} opacity={q}>
    <rect x="-90" y="-95" width="180" height="190" rx="32" fill={['#d1e3d4','#d9cce0','#e9d9bc'][i%3]} stroke="#a3bbb4" strokeWidth="6"/>
    {i%3===0?<Person x={0} y={10} scale={.35}/>:i%3===1?<path d="M-55 35L-25-15L0 10L25-35L55-8" fill="none" stroke="#a18cb4" strokeWidth="8"/>:<><circle r="53" fill="#f1ead8" stroke="#b8ab8b" strokeWidth="5"/><path d="M0-32V0L24 15" stroke="#ac9c80" strokeWidth="6" fill="none"/></>}
   </g>;})}
   <rect x="1360" y="595" width="180" height="190" rx="32" fill="none" stroke="#b5c5bd" strokeWidth="6" strokeDasharray="12 14"/>
  </g>;break;
 }
 case 30:{ // Individualized choice: adjust matching parameters, then walk onward.
  const assess=p(t,.04,.4),match=p(t,.39,.77),future=p(t,.77,1);
  action=<g>
   <Person x={440} y={630} scale={1.25} arm={assess*.5}/>
   <rect x="760" y="235" width="520" height="540" rx="65" fill="#f2f5e7" stroke="#a9c2b4" strokeWidth="10"/>
   {[0,1,2].map(i=><g key={i}><path d={`M840 ${350+i*140}H1200`} stroke="#c0d1c4" strokeWidth="17"/><circle cx={lerp(860,940+i%2*150,p(t,.1+i*.12,.4+i*.12))} cy={350+i*140} r="30" fill={['#bd9dca','#e3bc9b','#8fc2b7'][i]}/></g>)}
   <Virus x={1510} y={300} r={36}/><Bottle x={1510} y={535} scale={.75}/><Care x={1510} y={765} kind={2}/>
   <Link d="M1280 490Q1380 470 1440 535" q={match} color="#c9af88" width={12}/>
   <g opacity={future}><path d="M0 950Q450 760 970 940Q1500 760 1920 930V1080H0Z" fill="#a6c9a7"/><path d="M980 1080Q1100 915 1530 895" stroke="#e6d6af" strokeWidth="100" fill="none"/><Person x={lerp(1150,1510,future)} y={820} scale={.6} walk={Math.sin(sec*5)*future}/></g>
  </g>;break;
 }
 default:return null;
 }
 return <g strokeLinecap="round" strokeLinejoin="round">
  <defs><linearGradient id="story-purple" x2=".8" y2="1"><stop stopColor="#dbb5e9"/><stop offset="1" stopColor="#9973bb"/></linearGradient><linearGradient id="story-wall" x2="0" y2="1"><stop stopColor="#f6f4e9"/><stop offset="1" stopColor="#dfede4"/></linearGradient></defs>
  <rect width="1920" height="1080" fill="url(#story-wall)"/>
  <path d="M0 905Q950 835 1920 905V1080H0Z" fill="#cfdfd5"/>
  <path d={`M${n%2?60:1500} 170Q${n%2?260:1730} 60 ${n%2?440:1880} 180`} fill="none" stroke="#e7e4ce" strokeWidth="90" opacity=".6"/>
  {action}
 </g>;
};
