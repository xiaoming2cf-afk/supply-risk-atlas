import { execSync } from "node:child_process";

function firstDefined(...values) {
  return values.find((value) => typeof value === "string" && value.trim().length > 0)?.trim();
}

function gitCommit() {
  try {
    return execSync("git rev-parse HEAD", { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim();
  } catch {
    return undefined;
  }
}

const webCommit = firstDefined(
  process.env.NEXT_PUBLIC_SUPPLY_RISK_WEB_COMMIT,
  process.env.RENDER_GIT_COMMIT,
  process.env.SUPPLY_RISK_GIT_COMMIT,
  gitCommit(),
  "not_verified",
);

const webBuildTime = firstDefined(
  process.env.NEXT_PUBLIC_SUPPLY_RISK_WEB_BUILD_TIME,
  process.env.RENDER_BUILD_TIMESTAMP,
  "not_verified",
);

/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_SUPPLY_RISK_WEB_COMMIT: webCommit,
    NEXT_PUBLIC_SUPPLY_RISK_WEB_BUILD_TIME: webBuildTime
  },
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
