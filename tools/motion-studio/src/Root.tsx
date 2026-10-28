import {AbsoluteFill, Composition, useCurrentFrame} from 'remotion';
const ToolkitDemo = () => {
  const frame = useCurrentFrame();
  return <AbsoluteFill style={{background: '#071422', alignItems: 'center', justifyContent: 'center', color: '#70dfd1', fontFamily: 'Segoe UI', fontSize: 58}}>
    <div style={{transform: `translateY(${Math.sin(frame / 12) * 16}px)`}}>Motion Studio</div>
  </AbsoluteFill>;
};
export const Root = () => <Composition id="ToolkitDemo" component={ToolkitDemo} durationInFrames={120} fps={30} width={1280} height={720}/>;
