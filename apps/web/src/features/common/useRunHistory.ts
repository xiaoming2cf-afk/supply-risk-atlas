import { useCallback, useEffect, useMemo, useState } from "react";
import type { SupplyRiskApiClient } from "@supply-risk/api-client";
import type { RunHistoryData, RunReference, RunType } from "@supply-risk/shared-types";

export function useRunHistory(apiClient: SupplyRiskApiClient) {
  const [history, setHistory] = useState<RunHistoryData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(() => {
    setIsLoading(true);
    setError(null);
    return apiClient
      .listRuns()
      .then((response) => {
        if (response.envelope.status === "success" && response.data) {
          setHistory(response.data);
          return response.data;
        }
        const message = response.envelope.warnings[0] ?? response.envelope.errors[0]?.message ?? "Run history unavailable.";
        setError(message);
        return null;
      })
      .catch((caught) => {
        const message = caught instanceof Error ? caught.message : "Run history request failed.";
        setError(message);
        return null;
      })
      .finally(() => setIsLoading(false));
  }, [apiClient]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const runs = history?.runs ?? [];
  const latestForward = useMemo(() => latestRun(runs, "forward_scenario"), [runs]);
  const latestReverse = useMemo(() => latestRun(runs, "reverse_stress"), [runs]);
  const latestOptimization = useMemo(() => latestRun(runs, "intervention_optimization"), [runs]);
  const latestReport = useMemo(() => latestRun(runs, "investigation_report"), [runs]);
  const forwardRuns = useMemo(() => runs.filter((run) => run.run_type === "forward_scenario"), [runs]);
  const optimizationRuns = useMemo(() => runs.filter((run) => run.run_type === "intervention_optimization"), [runs]);

  return {
    error,
    forwardRuns,
    history,
    isLoading,
    latestForward,
    latestOptimization,
    latestReport,
    latestReverse,
    optimizationRuns,
    refresh,
    runs,
  };
}

function latestRun(runs: RunReference[], runType: RunType) {
  return runs.find((run) => run.run_type === runType);
}
