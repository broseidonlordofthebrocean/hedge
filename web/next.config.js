/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  reactStrictMode: true,
  images: {
    domains: ['localhost'],
    unoptimized: true,
  },
  trailingSlash: true,
  // Make dynamic routes work in static export
  dynamicParams: false,
};

module.exports = nextConfig;
