/** @type {import('next').NextConfig} */
const nextConfig = {
  // Static export → deployable on Netlify drop, Vercel, any static host.
  output: "export",
  reactStrictMode: true,
  images: { unoptimized: true },
  // R3F / three transpile safety
  transpilePackages: ["three", "@react-three/fiber", "@react-three/drei", "@react-three/postprocessing"],
};

export default nextConfig;
