import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";
export const revalidate = 0;

const COMMIT_PATTERN = /^[0-9a-f]{7,40}$/i;

function cleanCommit(value: string | undefined): string {
  const candidate = (value ?? "").trim().toLowerCase();
  return COMMIT_PATTERN.test(candidate) ? candidate : "not_verified";
}

function cleanBuildTime(value: string | undefined): string {
  const candidate = (value ?? "").trim();
  if (!candidate || candidate.length > 80) {
    return "not_verified";
  }
  return candidate.replace(/[^0-9A-Za-z:._+-]/g, "_");
}

function cleanMode(value: string | undefined, fallback: string): string {
  const candidate = (value ?? "").trim();
  if (!candidate || candidate.length > 80) {
    return fallback;
  }
  return candidate.replace(/[^0-9A-Za-z:._-]/g, "_");
}

export function GET() {
  return NextResponse.json(
    {
      status: "success",
      data: {
        web_commit: cleanCommit(process.env.NEXT_PUBLIC_SUPPLY_RISK_WEB_COMMIT),
        web_build_time: cleanBuildTime(process.env.NEXT_PUBLIC_SUPPLY_RISK_WEB_BUILD_TIME),
        data_mode: cleanMode(process.env.SUPPLY_RISK_DATA_MODE, "fixture"),
        graph_mode: cleanMode(process.env.SUPPLY_RISK_FIXTURE_GRAPH_MODE, "semirisk_fixture_v0.1"),
        deployment_readiness_state: "web_build_metadata",
        warnings: ["not_production_ready", "no_raw_payload"]
      }
    },
    {
      headers: {
        "Cache-Control": "no-store, max-age=0"
      }
    }
  );
}
