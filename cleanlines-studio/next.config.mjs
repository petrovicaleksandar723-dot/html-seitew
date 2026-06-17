/** @type {import('next').NextConfig} */
const isExport = process.env.BUILD_EXPORT === "1";

const nextConfig = {
  reactStrictMode: true,
  ...(isExport
    ? {
        output: "export",
        assetPrefix: process.env.ASSET_PREFIX,
        images: { unoptimized: true },
      }
    : {}),
};

export default nextConfig;
