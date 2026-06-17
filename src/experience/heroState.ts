/** Shared, render-loop-friendly state for the hero WebGL scene. */
export const heroState = {
  px: 0, // pointer x  (-1..1)
  py: 0, // pointer y  (-1..1)
  tx: 0, // smoothed pointer x
  ty: 0, // smoothed pointer y
  scroll: 0, // hero scroll progress 0..1
};
