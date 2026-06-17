import { ReactNode, RefObject } from "react";

/** Premium glass/metal tablet device chrome. */
export function IpadFrame({
  children,
  innerRef,
}: {
  children: ReactNode;
  innerRef?: RefObject<HTMLDivElement>;
}) {
  return (
    <div className="ipad" ref={innerRef}>
      <div className="ipad-rim" aria-hidden />
      <div className="ipad-screen">
        <span className="ipad-cam" aria-hidden />
        {children}
      </div>
    </div>
  );
}
