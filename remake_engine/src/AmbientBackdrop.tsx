/** Visible continuous frame-driven parallax behind the explanatory foreground. */
export function AmbientBackdrop({seconds}:{seconds:number}){
 return <g pointerEvents="none">
  {[0,1,2].map(i=>{
   const x=240+i*730+Math.sin(seconds*.075+i*1.7)*(160+i*25);
   const y=280+(i%2)*530+Math.cos(seconds*.07+i)*90;
   return <ellipse key={i} cx={x} cy={y} rx={320+i*50} ry={200+i*20}
    fill={i===1?'#a2c9d1':'#c7c2de'} opacity={.09}/>;
  })}
  {Array.from({length:24},(_,i)=><circle key={i} cx={(((i*347-seconds*(i%2?18:7))%2200+2200)%2200)-140}
   cy={((i*193+seconds*(i%2?3:1))%1300)-110} r={2+i%4} fill="#b9d1cd" opacity=".23"/>)}
 </g>;
}
