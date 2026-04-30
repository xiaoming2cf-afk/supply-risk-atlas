/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: [
    "@supply-risk/api-client",
    "@supply-risk/shared-types",
    "@supply-risk/design-system"
  ]
};

export default nextConfig;
