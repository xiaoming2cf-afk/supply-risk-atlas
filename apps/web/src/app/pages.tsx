import { useEffect, useMemo, useState, type ChangeEvent } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowLeftRight,
  ArrowRight,
  CheckCircle2,
  Clipboard,
  Database,
  Factory,
  Filter,
  GitBranch,
  Languages,
  Layers3,
  Play,
  Search,
  ShieldAlert,
  SlidersHorizontal,
  TerminalSquare
} from "lucide-react";
import type { SupplyRiskApiClient, SupplyRiskMockData } from "@supply-risk/api-client";
import type {
  DashboardPageId,
  EvidenceItem,
  ExplainedPath,
  GraphLink,
  GraphNode,
  GraphNodeKind,
  GraphVersion,
  RiskLevel,
  ShockSimulationInput,
  ShockSimulationResult
} from "@supply-risk/shared-types";
import { formatCompactNumber, formatPercent, formatUsdCompact, riskClassByLevel } from "@supply-risk/design-system";
import { Button, Field, IconButton, MetricTile, Panel, ProgressBar, RiskPill, ScoreDial, StatusPill } from "./components";

export interface PageRenderProps {
  data: SupplyRiskMockData;
  apiClient: SupplyRiskApiClient;
}

export function renderPage(pageId: DashboardPageId, props: PageRenderProps) {
  switch (pageId) {
    case "global-risk-cockpit":
      return <GlobalRiskCockpit data={props.data} />;
    case "graph-explorer":
      return <GraphExplorer data={props.data} />;
    case "company-risk-360":
      return <CompanyRisk360 data={props.data} />;
    case "path-explainer":
      return <PathExplainer data={props.data} />;
    case "shock-simulator":
      return <ShockSimulator apiClient={props.apiClient} />;
    case "causal-evidence-board":
      return <CausalEvidenceBoard data={props.data} />;
    case "graph-version-studio":
      return <GraphVersionStudio data={props.data} />;
    case "translator":
      return <TranslatorWorkbench />;
    case "system-health-center":
      return <SystemHealthCenter data={props.data} />;
    default:
      return (
        <div className="empty-state">
          <p>Page not configured.</p>
        </div>
      );
  }
}

type TranslationLanguage = "zh" | "en" | "fr";

interface TranslationEntry {
  zh: string;
  en: string;
  fr: string;
}

const translationLanguages: Array<{ code: TranslationLanguage; label: string; nativeLabel: string }> = [
  { code: "zh", label: "Chinese", nativeLabel: "中文" },
  { code: "en", label: "English", nativeLabel: "English" },
  { code: "fr", label: "French", nativeLabel: "Français" }
];

const translationMemory: TranslationEntry[] = [
  { zh: "全球产业风险操作系统", en: "Global Industrial Risk Operating System", fr: "système mondial d'exploitation des risques industriels" },
  { zh: "供应链风险", en: "supply chain risk", fr: "risque de chaîne d'approvisionnement" },
  { zh: "风险传播", en: "risk propagation", fr: "propagation du risque" },
  { zh: "冲击模拟", en: "shock simulation", fr: "simulation de choc" },
  { zh: "反事实模拟", en: "counterfactual simulation", fr: "simulation contrefactuelle" },
  { zh: "因果证据", en: "causal evidence", fr: "preuve causale" },
  { zh: "异质图", en: "heterogeneous graph", fr: "graphe hétérogène" },
  { zh: "动态图谱", en: "dynamic graph", fr: "graphe dynamique" },
  { zh: "实体注册表", en: "entity registry", fr: "registre des entités" },
  { zh: "事件溯源", en: "event sourcing", fr: "journalisation événementielle" },
  { zh: "图快照", en: "graph snapshot", fr: "instantané du graphe" },
  { zh: "路径索引", en: "path index", fr: "index des chemins" },
  { zh: "特征工厂", en: "feature factory", fr: "fabrique de caractéristiques" },
  { zh: "标签工厂", en: "label factory", fr: "fabrique d'étiquettes" },
  { zh: "模型注册表", en: "model registry", fr: "registre des modèles" },
  { zh: "数据血缘", en: "data lineage", fr: "lignage des données" },
  { zh: "系统健康", en: "system health", fr: "santé du système" },
  { zh: "供应商", en: "supplier", fr: "fournisseur" },
  { zh: "客户", en: "customer", fr: "client" },
  { zh: "港口", en: "port", fr: "port" },
  { zh: "产品", en: "product", fr: "produit" },
  { zh: "国家", en: "country", fr: "pays" },
  { zh: "企业", en: "firm", fr: "entreprise" },
  { zh: "设施", en: "facility", fr: "installation" },
  { zh: "路线", en: "route", fr: "itinéraire" },
  { zh: "预测", en: "prediction", fr: "prédiction" },
  { zh: "解释", en: "explanation", fr: "explication" },
  { zh: "报告", en: "report", fr: "rapport" },
  { zh: "韧性", en: "resilience", fr: "résilience" },
  { zh: "严重", en: "severe", fr: "sévère" },
  { zh: "关键", en: "critical", fr: "critique" },
  { zh: "升高", en: "elevated", fr: "élevé" },
  { zh: "受控", en: "guarded", fr: "surveillé" },
  { zh: "低", en: "low", fr: "faible" },
  { zh: "风险", en: "risk", fr: "risque" },
  { zh: "图", en: "graph", fr: "graphe" }
];

const translatorSamples: Record<TranslationLanguage, string> = {
  zh: "供应链风险通过港口和供应商路径传播。冲击模拟需要图快照、因果证据和数据血缘。",
  en: "Supply chain risk propagates through port and supplier paths. Shock simulation needs graph snapshots, causal evidence, and data lineage.",
  fr: "Le risque de chaîne d'approvisionnement se propage par les ports et les fournisseurs. La simulation de choc nécessite des instantanés du graphe, des preuves causales et le lignage des données."
};

function normalizeTranslationText(value: string) {
  return value
    .toLocaleLowerCase()
    .replace(/[.,;:!?，。；：！？()[\]{}"]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function translateText(input: string, sourceLanguage: TranslationLanguage, targetLanguage: TranslationLanguage) {
  if (!input.trim()) {
    return { output: "", matchedTerms: [] as TranslationEntry[], coverage: 0 };
  }

  if (sourceLanguage === targetLanguage) {
    return { output: input, matchedTerms: [] as TranslationEntry[], coverage: 100 };
  }

  const exactMatch = translationMemory.find(
    (entry) => normalizeTranslationText(entry[sourceLanguage]) === normalizeTranslationText(input)
  );
  if (exactMatch) {
    return { output: exactMatch[targetLanguage], matchedTerms: [exactMatch], coverage: 100 };
  }

  const sortedEntries = [...translationMemory].sort((a, b) => b[sourceLanguage].length - a[sourceLanguage].length);
  const matchedTerms: TranslationEntry[] = [];
  let output = input;
  let matchedLength = 0;

  for (const entry of sortedEntries) {
    const sourceTerm = entry[sourceLanguage];
    const targetTerm = entry[targetLanguage];
    const hasCjkSource = sourceLanguage === "zh";
    const pattern = hasCjkSource
      ? new RegExp(escapeRegExp(sourceTerm), "g")
      : new RegExp(`\\b${escapeRegExp(sourceTerm)}\\b`, "gi");

    let replaced = false;
    output = output.replace(pattern, (match) => {
      replaced = true;
      matchedLength += match.length;
      return targetTerm;
    });

    if (replaced) matchedTerms.push(entry);
  }

  const coverage = Math.min(100, Math.round((matchedLength / Math.max(input.length, 1)) * 100));
  return { output, matchedTerms, coverage };
}

function TranslatorWorkbench() {
  const [sourceLanguage, setSourceLanguage] = useState<TranslationLanguage>("zh");
  const [targetLanguage, setTargetLanguage] = useState<TranslationLanguage>("en");
  const [input, setInput] = useState(translatorSamples.zh);
  const [copyState, setCopyState] = useState("Copy result");
  const translation = useMemo(
    () => translateText(input, sourceLanguage, targetLanguage),
    [input, sourceLanguage, targetLanguage]
  );

  const setLanguage = (kind: "source" | "target") => (event: ChangeEvent<HTMLSelectElement>) => {
    const nextLanguage = event.target.value as TranslationLanguage;
    if (kind === "source") {
      setSourceLanguage(nextLanguage);
      if (!input.trim() || input === translatorSamples[sourceLanguage]) {
        setInput(translatorSamples[nextLanguage]);
      }
      if (nextLanguage === targetLanguage) setTargetLanguage(sourceLanguage);
      return;
    }

    setTargetLanguage(nextLanguage === sourceLanguage ? targetLanguage : nextLanguage);
  };

  const swapLanguages = () => {
    setSourceLanguage(targetLanguage);
    setTargetLanguage(sourceLanguage);
    setInput(translation.output || translatorSamples[targetLanguage]);
  };

  const copyResult = async () => {
    if (!translation.output.trim()) return;
    await navigator.clipboard?.writeText(translation.output);
    setCopyState("Copied");
    window.setTimeout(() => setCopyState("Copy result"), 1400);
  };

  return (
    <div className="page-grid translator-layout">
      <Panel
        title="Manual translation workbench"
        subtitle="Select Chinese, English, or French explicitly; translations use the governed SupplyRiskAtlas glossary."
        action={<Button icon={Languages} onClick={() => setInput(translatorSamples[sourceLanguage])}>Load sample</Button>}
      >
        <div className="translator-controls">
          <label className="form-control">
            <span>Source language</span>
            <select value={sourceLanguage} onChange={setLanguage("source")}>
              {translationLanguages.map((language) => (
                <option key={language.code} value={language.code}>
                  {language.nativeLabel} / {language.label}
                </option>
              ))}
            </select>
          </label>
          <button className="language-swap" type="button" onClick={swapLanguages} aria-label="Swap source and target languages">
            <ArrowLeftRight aria-hidden="true" />
          </button>
          <label className="form-control">
            <span>Target language</span>
            <select value={targetLanguage} onChange={setLanguage("target")}>
              {translationLanguages.map((language) => (
                <option disabled={language.code === sourceLanguage} key={language.code} value={language.code}>
                  {language.nativeLabel} / {language.label}
                </option>
              ))}
            </select>
          </label>
        </div>

        <label className="form-control translator-input">
          <span>Text to translate</span>
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            rows={8}
            placeholder="Enter a supply-chain risk sentence or glossary term."
          />
        </label>
      </Panel>

      <Panel
        title="Translation result"
        subtitle={`${translation.coverage}% glossary coverage; unmatched words remain unchanged for auditability.`}
        action={<Button icon={Clipboard} onClick={() => void copyResult()}>{copyState}</Button>}
      >
        <div className="translation-output" aria-live="polite">
          {translation.output || "Translation output will appear here."}
        </div>
      </Panel>

      <Panel title="Governed glossary hits" subtitle="Matched terms are shown so analysts can audit the generated wording.">
        {translation.matchedTerms.length > 0 ? (
          <div className="glossary-grid">
            {translation.matchedTerms.slice(0, 12).map((entry) => (
              <article className="glossary-card" key={`${entry[sourceLanguage]}-${entry[targetLanguage]}`}>
                <span>{entry[sourceLanguage]}</span>
                <ArrowRight aria-hidden="true" />
                <strong>{entry[targetLanguage]}</strong>
              </article>
            ))}
          </div>
        ) : (
          <div className="empty-state">No governed glossary terms detected yet.</div>
        )}
      </Panel>
    </div>
  );
}

function GlobalRiskCockpit({ data }: { data: SupplyRiskMockData }) {
  const cockpit = data.globalRiskCockpit;

  return (
    <div className="page-grid">
      <div className="metrics-grid">
        {cockpit.metrics.map((metric) => (
          <MetricTile key={metric.id} metric={metric} />
        ))}
      </div>

      <div className="page-grid cockpit-layout">
        <Panel
          title="Global exposure canvas"
          subtitle={`Last refreshed ${cockpit.lastUpdated}; hotspots are positioned by route and supplier concentration.`}
          action={<IconButton icon={Search} label="Search exposure graph" />}
        >
          <div className="map-canvas" role="img" aria-label="Global supply risk hotspot map">
            {cockpit.hotspots.map((hotspot) => (
              <div key={hotspot.id}>
                <span
                  className={`hotspot ${riskClassByLevel[hotspot.level]}`}
                  style={{ left: `${hotspot.x}%`, top: `${hotspot.y}%` }}
                />
                <article
                  className="hotspot-card"
                  style={{
                    left: `${Math.min(hotspot.x + 1, 76)}%`,
                    top: `${Math.max(hotspot.y - 5, 6)}%`
                  }}
                >
                  <div className="row-top">
                    <strong>{hotspot.label}</strong>
                    <RiskPill level={hotspot.level} />
                  </div>
                  <span>{hotspot.drivers.slice(0, 2).join(" / ")}</span>
                </article>
              </div>
            ))}
          </div>
        </Panel>

        <div className="page-grid">
          <Panel title="Incident queue" subtitle="Ranked by signal strength and graph reach.">
            <ul className="incident-list">
              {cockpit.incidents.map((incident) => (
                <li className="data-row" key={incident.id}>
                  <div className="row-top">
                    <div>
                      <span className="row-title">{incident.title}</span>
                      <span className="row-subtitle">{incident.region}</span>
                    </div>
                    <RiskPill level={incident.level} />
                  </div>
                  <ProgressBar value={incident.signalStrength * 100} level={incident.level} />
                  <div className="row-meta">
                    <span>{incident.affectedCompanies} companies</span>
                    <span>{formatPercent(incident.signalStrength)} signal strength</span>
                  </div>
                </li>
              ))}
            </ul>
          </Panel>

          <Panel title="Corridor stress" subtitle="Trade lanes carrying disproportionate revenue exposure.">
            <ul className="corridor-list">
              {cockpit.corridors.map((corridor) => (
                <li className="data-row" key={corridor.id}>
                  <div className="row-top">
                    <div>
                      <span className="row-title">
                        {corridor.source} to {corridor.target}
                      </span>
                      <span className="row-subtitle">{corridor.commodity}</span>
                    </div>
                    <RiskPill level={corridor.level} />
                  </div>
                  <ProgressBar value={corridor.score} level={corridor.level} />
                  <div className="row-meta">
                    <span>{corridor.score}/100 risk</span>
                    <span>{formatPercent(corridor.volumeShare)} volume share</span>
                  </div>
                </li>
              ))}
            </ul>
          </Panel>
        </div>
      </div>
    </div>
  );
}

function GraphExplorer({ data }: { data: SupplyRiskMockData }) {
  const graph = data.graphExplorer;
  const [kind, setKind] = useState<GraphNodeKind | "all">("all");
  const [selectedNodeId, setSelectedNodeId] = useState(graph.selectedNodeId);

  const visibleNodes = useMemo(
    () => graph.nodes.filter((node) => kind === "all" || node.kind === kind),
    [graph.nodes, kind]
  );
  const visibleNodeIds = useMemo(() => new Set(visibleNodes.map((node) => node.id)), [visibleNodes]);
  const visibleLinks = graph.links.filter((link) => visibleNodeIds.has(link.source) && visibleNodeIds.has(link.target));
  const selectedNode = graph.nodes.find((node) => node.id === selectedNodeId) ?? visibleNodes[0] ?? graph.nodes[0];

  return (
    <div className="page-grid split-layout">
      <Panel title="Graph filters" subtitle="Scope the visible network without losing node context.">
        <div className="segmented" aria-label="Graph node type">
          {(["all", ...graph.filters] as Array<GraphNodeKind | "all">).map((filter) => (
            <button
              className={`segment ${kind === filter ? "is-active" : ""}`}
              key={filter}
              onClick={() => setKind(filter)}
              type="button"
            >
              {filter}
            </button>
          ))}
        </div>
        <div style={{ marginTop: 16 }} className="inspector-grid">
          <Field label="Visible nodes" value={visibleNodes.length} />
          <Field label="Visible links" value={visibleLinks.length} />
          <Field label="Focus score" value={`${selectedNode.score}/100`} />
          <Field label="Focus type" value={selectedNode.kind} />
        </div>
      </Panel>

      <Panel
        title="Entity network"
        subtitle="Click a node to inspect metadata and high-risk adjacency."
        action={<Button icon={Filter}>Save view</Button>}
      >
        <div className="graph-canvas">
          <NetworkSvg links={visibleLinks} nodes={graph.nodes} />
          {visibleNodes.map((node) => (
            <button
              className={`graph-node ${riskClassByLevel[node.level]} ${selectedNode.id === node.id ? "is-selected" : ""}`}
              key={node.id}
              onClick={() => setSelectedNodeId(node.id)}
              style={{ left: `${node.x}%`, top: `${node.y}%` }}
              type="button"
            >
              <strong>{node.label}</strong>
              <span>{node.kind}</span>
            </button>
          ))}
        </div>
      </Panel>

      <Panel title="Node inspector" subtitle="Live metadata attached to the selected graph node.">
        <div className="inspector-grid">
          <Field label="Name" value={selectedNode.label} />
          <Field label="Risk level" value={<RiskPill level={selectedNode.level} />} />
          <Field label="Score" value={`${selectedNode.score}/100`} />
          <Field label="Kind" value={selectedNode.kind} />
          {Object.entries(selectedNode.metadata).map(([label, value]) => (
            <Field key={label} label={label} value={String(value)} />
          ))}
        </div>
      </Panel>
    </div>
  );
}

function NetworkSvg({ links, nodes }: { links: GraphLink[]; nodes: GraphNode[] }) {
  const nodeById = new Map(nodes.map((node) => [node.id, node]));

  return (
    <svg className="svg-network" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
      {links.map((link) => {
        const source = nodeById.get(link.source);
        const target = nodeById.get(link.target);
        if (!source || !target) return null;

        return (
          <line
            key={link.id}
            x1={source.x}
            y1={source.y}
            x2={target.x}
            y2={target.y}
            stroke="rgba(196,255,77,0.32)"
            strokeDasharray={link.level === "critical" || link.level === "severe" ? "0" : "2 2"}
            strokeLinecap="round"
            strokeWidth={0.45 + link.weight}
            vectorEffect="non-scaling-stroke"
          />
        );
      })}
    </svg>
  );
}

function CompanyRisk360({ data }: { data: SupplyRiskMockData }) {
  const companyData = data.companyRisk360;
  const [selectedCompanyId, setSelectedCompanyId] = useState(companyData.selectedCompanyId);
  const selectedCompany =
    companyData.companies.find((company) => company.id === selectedCompanyId) ?? companyData.companies[0];

  return (
    <div className="page-grid split-layout">
      <Panel title="Company watchlist" subtitle="Board-level exposure by target company.">
        <div className="company-list">
          {companyData.companies.map((company) => (
            <button
              className={`version-card ${selectedCompany.id === company.id ? "is-selected" : ""}`}
              key={company.id}
              onClick={() => setSelectedCompanyId(company.id)}
              type="button"
            >
              <div className="row-top">
                <div>
                  <span className="row-title">{company.name}</span>
                  <span className="row-subtitle">
                    {company.ticker} / {company.sector}
                  </span>
                </div>
                <RiskPill level={company.level} />
              </div>
              <ProgressBar value={company.riskScore} level={company.level} />
            </button>
          ))}
        </div>
      </Panel>

      <div className="page-grid">
        <Panel
          title={`${selectedCompany.name} risk posture`}
          subtitle={`${selectedCompany.headquarters}; confidence ${formatPercent(selectedCompany.confidence)}.`}
          action={<Button icon={ShieldAlert}>Create watch</Button>}
        >
          <div className="driver-grid">
            <ScoreDial score={selectedCompany.riskScore} level={selectedCompany.level} label="Risk score" />
            <div className="inspector-grid">
              <Field label="Revenue at risk" value={formatUsdCompact(selectedCompany.revenueAtRiskUsd)} />
              <Field label="Supplier count" value={selectedCompany.suppliers.length} />
              <Field label="Top dependency" value={selectedCompany.suppliers[0]?.supplier ?? "None"} />
              <Field label="Confidence" value={formatPercent(selectedCompany.confidence)} />
            </div>
          </div>
        </Panel>

        <Panel title="Drivers and mitigations" subtitle="Highest contribution factors and current response plan.">
          <div className="driver-grid">
            <ul className="timeline-list">
              {selectedCompany.topDrivers.map((driver) => (
                <li className="data-row" key={driver}>
                  <span className="row-title">{driver}</span>
                </li>
              ))}
            </ul>
            <ul className="recommendation-list">
              {selectedCompany.mitigations.map((mitigation) => (
                <li className="data-row" key={mitigation}>
                  <span className="row-title">{mitigation}</span>
                </li>
              ))}
            </ul>
          </div>
        </Panel>

        <Panel title="Supplier exposure table" subtitle="Spend share, dependency, and lead time by supplier.">
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Supplier</th>
                  <th>Country</th>
                  <th>Category</th>
                  <th>Spend</th>
                  <th>Dependency</th>
                  <th>Lead time</th>
                  <th>Level</th>
                </tr>
              </thead>
              <tbody>
                {selectedCompany.suppliers.map((supplier) => (
                  <tr key={supplier.id}>
                    <td>{supplier.supplier}</td>
                    <td>{supplier.country}</td>
                    <td>{supplier.category}</td>
                    <td>{formatPercent(supplier.spendShare)}</td>
                    <td>{formatPercent(supplier.dependency)}</td>
                    <td>{supplier.leadTimeDays} days</td>
                    <td>
                      <RiskPill level={supplier.level} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>
    </div>
  );
}

function PathExplainer({ data }: { data: SupplyRiskMockData }) {
  const pathData = data.pathExplainer;
  const [selectedPathId, setSelectedPathId] = useState(pathData.selectedPathId);
  const selectedPath = pathData.paths.find((path) => path.id === selectedPathId) ?? pathData.paths[0];

  return (
    <div className="page-grid">
      <Panel
        title="Explained path selector"
        subtitle="Trace the concrete graph route behind a risk score movement."
        action={<Button icon={GitBranch}>Pin explanation</Button>}
      >
        <div className="segmented" aria-label="Explained path">
          {pathData.paths.map((path) => (
            <button
              className={`segment ${selectedPath.id === path.id ? "is-active" : ""}`}
              key={path.id}
              onClick={() => setSelectedPathId(path.id)}
              type="button"
            >
              {path.targetCompany}
            </button>
          ))}
        </div>
      </Panel>

      <Panel
        title={selectedPath.title}
        subtitle={`${selectedPath.scoreMove.toFixed(1)} point score move; ${formatPercent(selectedPath.confidence)} explanation confidence.`}
      >
        <p className="panel-subtitle" style={{ marginBottom: 16 }}>
          {selectedPath.summary}
        </p>
        <PathStrip path={selectedPath} />
      </Panel>
    </div>
  );
}

function PathStrip({ path }: { path: ExplainedPath }) {
  return (
    <div className="path-strip">
      {path.steps.map((step) => (
        <article className="path-step" key={step.id}>
          <div className="row-top">
            <RiskPill level={step.level} />
            <span className="method-pill">{step.kind}</span>
          </div>
          <p className="contribution">+{step.contribution}%</p>
          <span className="row-title">{step.label}</span>
          <span className="row-subtitle">{step.evidence}</span>
        </article>
      ))}
    </div>
  );
}

function ShockSimulator({ apiClient }: { apiClient: SupplyRiskApiClient }) {
  const [input, setInput] = useState<ShockSimulationInput>({
    region: "Taiwan Strait",
    commodity: "advanced semiconductor components",
    severity: 72,
    durationDays: 28,
    scope: "regional"
  });
  const [result, setResult] = useState<ShockSimulationResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    let isActive = true;
    setIsRunning(true);
    apiClient
      .runShockSimulation(input)
      .then((nextResult) => {
        if (isActive) setResult(nextResult);
      })
      .finally(() => {
        if (isActive) setIsRunning(false);
      });

    return () => {
      isActive = false;
    };
  }, [apiClient, input]);

  const setNumber = (key: "severity" | "durationDays") => (event: ChangeEvent<HTMLInputElement>) => {
    setInput((current) => ({ ...current, [key]: Number(event.target.value) }));
  };

  return (
    <div className="page-grid split-layout">
      <Panel
        title="Shock controls"
        subtitle="Change the scenario and the impact model recalculates against the active graph."
        action={<Button icon={Play} variant="primary">{isRunning ? "Running" : "Run"}</Button>}
      >
        <div className="form-grid">
          <label className="form-control">
            <span>Region</span>
            <select value={input.region} onChange={(event) => setInput((current) => ({ ...current, region: event.target.value }))}>
              <option>Taiwan Strait</option>
              <option>Red Sea / Suez</option>
              <option>Panama Canal</option>
              <option>Rhine Industrial Belt</option>
            </select>
          </label>
          <label className="form-control">
            <span>Commodity</span>
            <select
              value={input.commodity}
              onChange={(event) => setInput((current) => ({ ...current, commodity: event.target.value }))}
            >
              <option>advanced semiconductor components</option>
              <option>battery graphite</option>
              <option>specialty chemical feedstock</option>
              <option>consumer electronics assemblies</option>
            </select>
          </label>
          <label className="form-control">
            <span>Severity: {input.severity}</span>
            <input min="10" max="100" onChange={setNumber("severity")} type="range" value={input.severity} />
          </label>
          <label className="form-control">
            <span>Duration: {input.durationDays} days</span>
            <input min="3" max="90" onChange={setNumber("durationDays")} type="range" value={input.durationDays} />
          </label>
          <label className="form-control">
            <span>Scope</span>
            <select value={input.scope} onChange={(event) => setInput((current) => ({ ...current, scope: event.target.value as ShockSimulationInput["scope"] }))}>
              <option value="facility">Facility</option>
              <option value="regional">Regional</option>
              <option value="global">Global</option>
            </select>
          </label>
        </div>
      </Panel>

      <div className="page-grid">
        <Panel title="Projected impact" subtitle="Mock mode uses deterministic scenario math; API mode posts the same payload.">
          {result ? (
            <div className="three-column page-grid">
              <div className={`big-result ${riskClassByLevel[result.affectedPaths[0]?.level ?? "guarded"]}`}>
                <span>Impact score</span>
                <strong>{result.impactScore}</strong>
              </div>
              <div className="big-result tone-elevated">
                <span>EBITDA at risk</span>
                <strong>{formatUsdCompact(result.ebitdaAtRiskUsd)}</strong>
              </div>
              <div className="big-result tone-guarded">
                <span>Recovery time</span>
                <strong>{result.timeToRecoveryDays}d</strong>
              </div>
            </div>
          ) : (
            <div className="empty-state">Awaiting simulation result.</div>
          )}
        </Panel>

        {result ? (
          <>
            <Panel title="Affected paths" subtitle={`${result.affectedCompanies} companies touched by this scenario.`}>
              <ul className="timeline-list">
                {result.affectedPaths.map((path) => (
                  <li className="data-row" key={path.id}>
                    <div className="row-top">
                      <span className="row-title">{path.label}</span>
                      <RiskPill level={path.level} />
                    </div>
                    <ProgressBar value={path.impact} level={path.level} />
                  </li>
                ))}
              </ul>
            </Panel>

            <Panel title="Mitigation queue" subtitle="Operational actions ranked by speed-to-impact.">
              <ul className="recommendation-list">
                {result.recommendations.map((recommendation) => (
                  <li className="data-row" key={recommendation}>
                    <span className="row-title">{recommendation}</span>
                  </li>
                ))}
              </ul>
            </Panel>
          </>
        ) : null}
      </div>
    </div>
  );
}

function CausalEvidenceBoard({ data }: { data: SupplyRiskMockData }) {
  const board = data.causalEvidenceBoard;
  const [activeClaimId, setActiveClaimId] = useState(board.activeClaimId);
  const activeClaim = board.evidence.find((claim) => claim.id === activeClaimId) ?? board.evidence[0];

  return (
    <div className="page-grid split-layout">
      <Panel title="Evidence register" subtitle="Causal claims are scored for confidence and disagreement.">
        <div className="evidence-list">
          {board.evidence.map((item) => (
            <EvidenceButton
              item={item}
              isActive={item.id === activeClaim.id}
              key={item.id}
              onSelect={() => setActiveClaimId(item.id)}
            />
          ))}
        </div>
      </Panel>

      <div className="page-grid">
        <Panel
          title="Causal claim focus"
          subtitle={activeClaim.source}
          action={<span className="method-pill">{activeClaim.method}</span>}
        >
          <div className="driver-grid">
            <div>
              <p className="row-title">{activeClaim.claim}</p>
              <div className="inspector-grid" style={{ marginTop: 16 }}>
                <Field label="Confidence" value={formatPercent(activeClaim.confidence)} />
                <Field label="Disagreement" value={formatPercent(activeClaim.disagreement)} />
                <Field label="Reviewed" value={activeClaim.lastReviewed} />
                <Field label="Level" value={<RiskPill level={activeClaim.level} />} />
              </div>
            </div>
            <div className="causal-canvas" role="img" aria-label="Causal evidence mini graph">
              <NetworkSvg
                nodes={[
                  { id: "shock", label: "Shock", kind: "route", level: activeClaim.level, score: 80, x: 18, y: 48, metadata: {} },
                  { id: "mechanism", label: "Mechanism", kind: "facility", level: "elevated", score: 66, x: 50, y: 28, metadata: {} },
                  { id: "outcome", label: "Outcome", kind: "company", level: activeClaim.level, score: 78, x: 78, y: 62, metadata: {} }
                ]}
                links={[
                  { id: "a", source: "shock", target: "mechanism", label: "causes", weight: 0.76, level: activeClaim.level },
                  { id: "b", source: "mechanism", target: "outcome", label: "shifts", weight: 0.62, level: "elevated" }
                ]}
              />
            </div>
          </div>
        </Panel>

        <Panel title="Evidence quality" subtitle="Confidence and disagreement are tracked separately.">
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Claim</th>
                  <th>Method</th>
                  <th>Confidence</th>
                  <th>Disagreement</th>
                  <th>Level</th>
                </tr>
              </thead>
              <tbody>
                {board.evidence.map((item) => (
                  <tr key={item.id}>
                    <td>{item.claim}</td>
                    <td>{item.method}</td>
                    <td>{formatPercent(item.confidence)}</td>
                    <td>{formatPercent(item.disagreement)}</td>
                    <td>
                      <RiskPill level={item.level} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>
    </div>
  );
}

function EvidenceButton({ item, isActive, onSelect }: { item: EvidenceItem; isActive: boolean; onSelect: () => void }) {
  return (
    <button className={`evidence-card ${isActive ? "is-active" : ""}`} onClick={onSelect} type="button">
      <div className="row-top">
        <span className="row-title">{item.claim}</span>
        <RiskPill level={item.level} />
      </div>
      <span className="row-subtitle">{item.source}</span>
      <ProgressBar value={item.confidence * 100} level={item.level} />
      <div className="row-meta">
        <span>{item.method}</span>
        <span>{formatPercent(item.disagreement)} disagreement</span>
      </div>
    </button>
  );
}

function GraphVersionStudio({ data }: { data: SupplyRiskMockData }) {
  const studio = data.graphVersionStudio;
  const [candidateVersionId, setCandidateVersionId] = useState(studio.candidateVersionId);
  const [promotedVersionId, setPromotedVersionId] = useState(studio.baselineVersionId);
  const candidate = studio.versions.find((version) => version.id === candidateVersionId) ?? studio.versions[0];

  return (
    <div className="page-grid split-layout">
      <Panel title="Graph builds" subtitle="Select a candidate and compare it against the promoted baseline.">
        <div className="version-list">
          {studio.versions.map((version) => (
            <VersionButton
              isPromoted={version.id === promotedVersionId}
              isSelected={version.id === candidate.id}
              key={version.id}
              onSelect={() => setCandidateVersionId(version.id)}
              version={version}
            />
          ))}
        </div>
      </Panel>

      <div className="page-grid">
        <Panel
          title="Candidate readiness"
          subtitle={`${candidate.label}; built by ${candidate.author}.`}
          action={<Button icon={CheckCircle2} variant="primary" onClick={() => setPromotedVersionId(candidate.id)}>Promote</Button>}
        >
          <div className="version-grid">
            <Field label="Nodes" value={formatCompactNumber(candidate.nodes)} />
            <Field label="Edges" value={formatCompactNumber(candidate.edges)} />
            <Field label="Schema changes" value={candidate.schemaChanges} />
            <Field label="Validation pass rate" value={formatPercent(candidate.validationPassRate, 1)} />
          </div>
        </Panel>

        <Panel title="Diff matrix" subtitle="Material graph changes detected against the promoted baseline.">
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Area</th>
                  <th>Change</th>
                  <th>Count</th>
                  <th>Severity</th>
                </tr>
              </thead>
              <tbody>
                {studio.diffRows.map((row) => (
                  <tr key={row.id}>
                    <td>{row.area}</td>
                    <td>{row.change}</td>
                    <td>{formatCompactNumber(row.count)}</td>
                    <td>
                      <RiskPill level={row.severity} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>
    </div>
  );
}

function VersionButton({
  version,
  isSelected,
  isPromoted,
  onSelect
}: {
  version: GraphVersion;
  isSelected: boolean;
  isPromoted: boolean;
  onSelect: () => void;
}) {
  return (
    <button className={`version-card ${isSelected ? "is-selected" : ""}`} onClick={onSelect} type="button">
      <div className="row-top">
        <div>
          <span className="row-title">{version.label}</span>
          <span className="row-subtitle">{version.createdAt}</span>
        </div>
        <StatusPill status={isPromoted ? "promoted" : version.status} />
      </div>
      <ProgressBar
        value={version.validationPassRate * 100}
        level={version.validationPassRate > 0.98 ? "low" : "elevated"}
      />
      <div className="row-meta">
        <span>{formatCompactNumber(version.nodes)} nodes</span>
        <span>{formatCompactNumber(version.edges)} edges</span>
      </div>
    </button>
  );
}

function SystemHealthCenter({ data }: { data: SupplyRiskMockData }) {
  const health = data.systemHealthCenter;
  const operationalCount = health.services.filter((service) => service.status === "operational").length;
  const pipelineTotal = health.stages.reduce((total, stage) => total + stage.total, 0);
  const pipelineProcessed = health.stages.reduce((total, stage) => total + stage.processed, 0);

  return (
    <div className="page-grid">
      <div className="metrics-grid">
        <article className="metric-tile">
          <div className="metric-head">
            <p className="metric-label">Services operational</p>
            <StatusPill status="operational" />
          </div>
          <p className="metric-value">
            {operationalCount}
            <span className="metric-unit">/{health.services.length}</span>
          </p>
          <p className="metric-detail">API, graph, model, and signal ingest fleet.</p>
        </article>
        <article className="metric-tile">
          <div className="metric-head">
            <p className="metric-label">Pipeline processed</p>
            <StatusPill status="running" />
          </div>
          <p className="metric-value">{formatPercent(pipelineProcessed / pipelineTotal)}</p>
          <p className="metric-detail">Current build is advancing through entity resolution.</p>
        </article>
        <article className="metric-tile">
          <div className="metric-head">
            <p className="metric-label">Median latency</p>
            <StatusPill status="operational" />
          </div>
          <p className="metric-value">
            181<span className="metric-unit">ms</span>
          </p>
          <p className="metric-detail">Across API, graph query, ingest, and scorer endpoints.</p>
        </article>
        <article className="metric-tile">
          <div className="metric-head">
            <p className="metric-label">Freshness lag</p>
            <StatusPill status="degraded" />
          </div>
          <p className="metric-value">
            17<span className="metric-unit">m</span>
          </p>
          <p className="metric-detail">Signal ingest is the current freshness constraint.</p>
        </article>
      </div>

      <div className="page-grid split-layout">
        <Panel title="Service status" subtitle="Runtime health by service owner.">
          <ul className="health-list">
            {health.services.map((service) => (
              <li className="data-row" key={service.id}>
                <div className="row-top">
                  <div>
                    <span className="row-title">{service.service}</span>
                    <span className="row-subtitle">{service.owner}</span>
                  </div>
                  <StatusPill status={service.status} />
                </div>
                <div className="row-meta">
                  <span>{service.latencyMs} ms</span>
                  <span>{service.freshnessMinutes} m freshness</span>
                  <span>{formatPercent(service.errorRate, 1)} errors</span>
                </div>
              </li>
            ))}
          </ul>
        </Panel>

        <div className="page-grid">
          <Panel title="Build pipeline" subtitle="Current graph and scoring run progress.">
            <ul className="timeline-list">
              {health.stages.map((stage) => {
                const value = stage.total === 0 ? 0 : (stage.processed / stage.total) * 100;
                return (
                  <li className="data-row stage-row" key={stage.id}>
                    <span className="row-title">{stage.label}</span>
                    <ProgressBar value={value} level={stage.status === "blocked" ? "critical" : "guarded"} />
                    <StatusPill status={stage.status} />
                  </li>
                );
              })}
            </ul>
          </Panel>

          <Panel
            title="Runtime log"
            subtitle="Recent platform events."
            action={<IconButton icon={TerminalSquare} label="Open terminal log" />}
          >
            <pre className="terminal-log">
              {health.logs.map((line) => (
                <code key={line}>{line}</code>
              ))}
            </pre>
          </Panel>
        </div>
      </div>
    </div>
  );
}
