export function HeroLights() {
  return (
    <>
      <ambientLight intensity={0.85} color="#16100a" />
      <directionalLight position={[5, 4, 6]} intensity={2.6} color="#ffce86" />
      <directionalLight position={[-5, -2, 2]} intensity={1.3} color="#d6772a" />
      <directionalLight position={[-3, 5, -4]} intensity={1.5} color="#f4d7a1" />
    </>
  );
}
