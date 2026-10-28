import {Circle, makeScene2D, Txt} from '@motion-canvas/2d';
import {all, createRef, waitFor} from '@motion-canvas/core';
export default makeScene2D(function* (view) {
  view.fill('#071422');
  const dot = createRef<Circle>();
  view.add(<><Circle ref={dot} size={100} fill="#70dfd1" x={-500}/><Txt text="Motion Canvas sẵn sàng" fill="white" fontSize={64} y={180}/></>);
  yield* all(dot().position.x(500, 2), dot().scale(1.6, 2));
  yield* waitFor(1);
});
