import { NextRequest, NextResponse } from "next/server";

const API_HOSTPORT = process.env.SUPPLY_RISK_API_HOSTPORT;
const API_ORIGIN = process.env.SUPPLY_RISK_API_ORIGIN ?? (API_HOSTPORT ? `http://${API_HOSTPORT}` : undefined);

type RouteContext = {
  params: Promise<{
    path?: string[];
  }>;
};

export async function GET(request: NextRequest, context: RouteContext) {
  return proxyRequest(request, context);
}

export async function POST(request: NextRequest, context: RouteContext) {
  return proxyRequest(request, context);
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: corsHeaders()
  });
}

async function proxyRequest(request: NextRequest, context: RouteContext) {
  if (!API_ORIGIN) {
    return NextResponse.json(
      {
        request_id: crypto.randomUUID(),
        status: "error",
        data: null,
        metadata: {
          graph_version: "unavailable",
          feature_version: "unavailable",
          label_version: "unavailable",
          model_version: "unavailable",
          as_of_time: new Date().toISOString(),
          data_mode: "real",
          freshness_status: "unavailable"
        },
        warnings: ["SUPPLY_RISK_API_ORIGIN or SUPPLY_RISK_API_HOSTPORT is not configured."],
        errors: [
          {
            code: "api_proxy_unconfigured",
            message: "SupplyRiskAtlas API proxy is not configured."
          }
        ],
        mode: "real",
        source_status: "unavailable",
        source: {
          name: "SupplyRiskAtlas API proxy",
          lineage_ref: "proxy://unconfigured"
        }
      },
      { status: 503, headers: corsHeaders() }
    );
  }

  const params = await context.params;
  const path = params.path?.join("/") ?? "";
  const upstreamUrl = new URL(`/api/v1/${path}${request.nextUrl.search}`, API_ORIGIN);
  let upstreamResponse: Response;
  try {
    upstreamResponse = await fetch(upstreamUrl, {
      method: request.method,
      headers: forwardHeaders(request),
      body: request.method === "GET" || request.method === "HEAD" ? undefined : await request.text(),
      cache: "no-store"
    });
  } catch (error) {
    return NextResponse.json(
      {
        request_id: crypto.randomUUID(),
        status: "error",
        data: null,
        metadata: {
          graph_version: "unavailable",
          feature_version: "unavailable",
          label_version: "unavailable",
          model_version: "unavailable",
          as_of_time: new Date().toISOString(),
          data_mode: "real",
          freshness_status: "unavailable"
        },
        warnings: [`Unable to reach SupplyRiskAtlas API at ${API_ORIGIN}.`],
        errors: [
          {
            code: "api_proxy_upstream_unreachable",
            message: error instanceof Error ? error.message : "SupplyRiskAtlas API proxy upstream failed."
          }
        ],
        mode: "real",
        source_status: "unavailable",
        source: {
          name: "SupplyRiskAtlas API proxy",
          url: API_ORIGIN,
          lineage_ref: "proxy://upstream-unreachable"
        }
      },
      { status: 502, headers: corsHeaders() }
    );
  }

  return new NextResponse(upstreamResponse.body, {
    status: upstreamResponse.status,
    headers: {
      ...corsHeaders(),
      "content-type": upstreamResponse.headers.get("content-type") ?? "application/json; charset=utf-8"
    }
  });
}

function forwardHeaders(request: NextRequest): Headers {
  const headers = new Headers();
  const contentType = request.headers.get("content-type");
  const requestId = request.headers.get("x-request-id");
  if (contentType) headers.set("content-type", contentType);
  if (requestId) headers.set("x-request-id", requestId);
  return headers;
}

function corsHeaders() {
  return {
    "access-control-allow-origin": "*",
    "access-control-allow-methods": "GET, POST, OPTIONS",
    "access-control-allow-headers": "content-type, x-request-id"
  };
}
