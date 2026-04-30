/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: [
    "@supply-risk/api-client",
    "@supply-risk/shared-types",
    "@supply-risk/design-system"
  ],
  async headers() {
    return [
      {
        source: "/",
        headers: [
          {
            key: "Cache-Control",
            value: "no-store, max-age=0"
          }
        ]
      }
    ];
  }
};

export default nextConfig;
