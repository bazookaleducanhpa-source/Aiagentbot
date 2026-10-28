import {useRef} from 'react';
import {gsap} from 'gsap';
import {useGSAP} from '@gsap/react';
gsap.registerPlugin(useGSAP);
/** Loading indicator for interactive React pages. Use frame-driven animation in Remotion. */
export function GsapLoader() {
  const container = useRef<HTMLDivElement>(null);
  useGSAP(() => {
    const media = gsap.matchMedia();
    media.add('(prefers-reduced-motion: no-preference)', () => {
      gsap.to('[data-loader-dot]', {y: -12, duration: 0.38, stagger: 0.12, repeat: -1, yoyo: true, ease: 'sine.inOut'});
    });
    return () => media.revert();
  }, {scope: container});
  return <div ref={container} role="status" aria-label="Đang tải" style={{display: 'flex', gap: 8, padding: 16}}>
    {[0, 1, 2].map(i => <span key={i} data-loader-dot style={{display: 'block', width: 12, height: 12, borderRadius: '50%', background: '#70dfd1'}}/>)}
  </div>;
}
