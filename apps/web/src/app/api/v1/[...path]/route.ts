import { NextRequest, NextResponse } from "next/server";

const API_HOSTPORT = process.env.SUPPLY_RISK_API_HOSTPORT;
const API_ORIGIN = process.env.SUPPLY_RISK_API_ORIGIN?.trim();
const RENDER_WEB_HOSTNAME = "supply-risk-atlas-web.onrender.com";
const RENDER_API_ORIGIN = "https://supply-risk-atlas-api.onrender.com";
const MAX_PROXY_PATH_SEGMENTS = 8;
const MAX_PROXY_PATH_SEGMENT_LENGTH = 120;
const TRANSIENT_UPSTREAM_STATUSES = new Set([502, 503, 504]);
const MAX_GET_PROXY_ATTEMPTS = 4;
const GET_PROXY_RETRY_DELAY_MS = 750;

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
  const apiOrigin = resolveApiOrigin(request);
  if (!apiOrigin) {
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
        warnings: ["Public data service is temporarily unavailable."],
        errors: [
          {
            code: "api_proxy_unconfigured",
            message: "Public data service is temporarily unavailable."
          }
        ],
        mode: "real",
        source_status: "unavailable",
        source: {
          name: "SupplyRiskAtlas public data service",
          lineage_ref: "proxy://unconfigured"
        }
      },
      { status: 503, headers: corsHeaders() }
    );
  }

  const params = await context.params;
  const pathSegments = params.path ?? [];
  const pathError = validateProxyPath(pathSegments);
  if (pathError) {
    return proxyErrorResponse("api_proxy_invalid_path", pathError, 400);
  }
  const path = pathSegments.map((segment) => encodeURIComponent(segment)).join("/");
  const upstreamUrl = new URL(`/api/v1/${path}${request.nextUrl.search}`, apiOrigin);
  let upstreamResponse: Response;
  try {
    upstreamResponse = await fetchUpstreamWithRetries(
      upstreamUrl,
      request.method,
      forwardHeaders(request),
      request.method === "GET" || request.method === "HEAD" ? undefined : await request.text()
    );
  } catch {
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
        warnings: ["Public data service is temporarily unavailable."],
        errors: [
          {
            code: "api_proxy_upstream_unreachable",
            message: "Public data service is temporarily unavailable."
          }
        ],
        mode: "real",
        source_status: "unavailable",
        source: {
          name: "SupplyRiskAtlas public data service",
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

async function fetchUpstreamWithRetries(
  upstreamUrl: URL,
  method: string,
  headers: Headers,
  body: string | undefined
): Promise<Response> {
  const isReadRequest = method === "GET" || method === "HEAD";
  const attempts = isReadRequest ? MAX_GET_PROXY_ATTEMPTS : 1;
  let lastError: unknown;
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      const response = await fetch(upstreamUrl, {
        method,
        headers,
        body,
        cache: "no-store"
      });
      if (!isReadRequest || !TRANSIENT_UPSTREAM_STATUSES.has(response.status) || attempt === attempts) {
        return response;
      }
    } catch (error) {
      lastError = error;
      if (attempt === attempts) {
        throw error;
      }
    }
    await sleep(GET_PROXY_RETRY_DELAY_MS * attempt);
  }
  throw lastError instanceof Error ? lastError : new Error("Upstream public data service is unreachable.");
}

function resolveApiOrigin(request: NextRequest): string | undefined {
  const requestHost = request.headers.get("host")?.split(":")[0]?.toLowerCase();
  const deployTarget = process.env.SUPPLY_RISK_DEPLOY_TARGET?.trim().toLowerCase() || RENDER_WEB_HOSTNAME;
  if (requestHost === deployTarget || requestHost === RENDER_WEB_HOSTNAME) {
    if (API_ORIGIN) return API_ORIGIN;
    return RENDER_API_ORIGIN;
  }
  if (API_ORIGIN) return API_ORIGIN;
  if (API_HOSTPORT) return `http://${API_HOSTPORT}`;
  return undefined;
}

function sleep(milliseconds: number) {
  return new Promise((resolve) => {
    setTimeout(resolve, milliseconds);
  });
}

function validateProxyPath(pathSegments: string[]): string | null {
  if (pathSegments.length > MAX_PROXY_PATH_SEGMENTS) {
    return "Requested public data path is not available.";
  }
  for (const segment of pathSegments) {
    if (
      !segment ||
      segment === "." ||
      segment === ".." ||
      segment.includes("/") ||
      segment.includes("\\") ||
      segment.length > MAX_PROXY_PATH_SEGMENT_LENGTH
    ) {
      return "Requested public data path is not available.";
    }
  }
  return null;
}

function proxyErrorResponse(code: string, message: string, status: number) {
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
      warnings: [message],
      errors: [{ code, message }],
      mode: "real",
      source_status: "unavailable",
      source: {
        name: "SupplyRiskAtlas public data service",
        lineage_ref: "proxy://invalid-path"
      }
    },
    { status, headers: corsHeaders() }
  );
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
