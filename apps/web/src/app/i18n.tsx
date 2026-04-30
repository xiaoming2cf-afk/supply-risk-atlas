"use client";

import { createContext, useContext, type ReactNode } from "react";
import type { DashboardPage, DashboardPageId, RiskLevel } from "@supply-risk/shared-types";
import type { SupplyRiskMockData } from "@supply-risk/api-client";

export type PageLanguage = "en" | "zh" | "fr";

export const pageLanguages: Array<{ code: PageLanguage; label: string; nativeLabel: string }> = [
  { code: "zh", label: "Chinese", nativeLabel: "中文" },
  { code: "en", label: "English", nativeLabel: "English" },
  { code: "fr", label: "French", nativeLabel: "Français" }
];

type TranslationPair = Record<Exclude<PageLanguage, "en">, string>;

const pageCopy: Record<DashboardPageId, Record<PageLanguage, Pick<DashboardPage, "label" | "shortLabel" | "description">>> = {
  "global-risk-cockpit": {
    en: {
      label: "Global Risk Cockpit",
      shortLabel: "Cockpit",
      description: "Live exposure map, risk pressure, and incident queue"
    },
    zh: {
      label: "全球风险驾驶舱",
      shortLabel: "驾驶舱",
      description: "实时暴露地图、风险压力和事件队列"
    },
    fr: {
      label: "Poste de pilotage des risques mondiaux",
      shortLabel: "Pilotage",
      description: "Carte d'exposition, pression du risque et file d'incidents"
    }
  },
  "graph-explorer": {
    en: {
      label: "Graph Explorer",
      shortLabel: "Graph",
      description: "Supplier, facility, commodity, route, and country network"
    },
    zh: {
      label: "图谱探索器",
      shortLabel: "图谱",
      description: "供应商、设施、商品、路线和国家网络"
    },
    fr: {
      label: "Explorateur de graphe",
      shortLabel: "Graphe",
      description: "Réseau de fournisseurs, sites, produits, routes et pays"
    }
  },
  "company-risk-360": {
    en: {
      label: "Company Risk 360",
      shortLabel: "Risk 360",
      description: "Company-level exposure, suppliers, and mitigation posture"
    },
    zh: {
      label: "企业风险 360",
      shortLabel: "风险 360",
      description: "企业级暴露、供应商和缓释状态"
    },
    fr: {
      label: "Risque entreprise 360",
      shortLabel: "Risque 360",
      description: "Exposition, fournisseurs et posture d'atténuation par entreprise"
    }
  },
  "path-explainer": {
    en: {
      label: "Path Explainer",
      shortLabel: "Paths",
      description: "Why a risk score moved and which paths carried the signal"
    },
    zh: {
      label: "路径解释器",
      shortLabel: "路径",
      description: "解释风险分数为何变化以及哪些路径承载了信号"
    },
    fr: {
      label: "Explicateur de chemins",
      shortLabel: "Chemins",
      description: "Pourquoi un score a bougé et quels chemins ont porté le signal"
    }
  },
  "shock-simulator": {
    en: {
      label: "Shock Simulator",
      shortLabel: "Simulator",
      description: "Stress test regions, commodities, severity, and recovery"
    },
    zh: {
      label: "冲击模拟器",
      shortLabel: "模拟",
      description: "对地区、商品、严重度和恢复过程进行压力测试"
    },
    fr: {
      label: "Simulateur de choc",
      shortLabel: "Simulation",
      description: "Tester régions, produits, sévérité et reprise"
    }
  },
  "causal-evidence-board": {
    en: {
      label: "Causal Evidence Board",
      shortLabel: "Evidence",
      description: "Evidence quality, causal claims, and disagreement tracking"
    },
    zh: {
      label: "因果证据看板",
      shortLabel: "证据",
      description: "证据质量、因果主张和分歧跟踪"
    },
    fr: {
      label: "Tableau des preuves causales",
      shortLabel: "Preuves",
      description: "Qualité des preuves, affirmations causales et désaccords"
    }
  },
  "graph-version-studio": {
    en: {
      label: "Graph Version Studio",
      shortLabel: "Versions",
      description: "Compare graph builds, schema drift, and promotion readiness"
    },
    zh: {
      label: "图版本工作室",
      shortLabel: "版本",
      description: "比较图构建、模式漂移和发布就绪度"
    },
    fr: {
      label: "Studio des versions de graphe",
      shortLabel: "Versions",
      description: "Comparer builds, dérive de schéma et préparation à la promotion"
    }
  },
  "system-health-center": {
    en: {
      label: "System Health Center",
      shortLabel: "Health",
      description: "Data pipeline, model, API, and graph service health"
    },
    zh: {
      label: "系统健康中心",
      shortLabel: "健康",
      description: "数据管道、模型、API 和图服务健康状态"
    },
    fr: {
      label: "Centre de santé du système",
      shortLabel: "Santé",
      description: "Santé des pipelines, modèles, API et services de graphe"
    }
  }
};

const riskLevelCopy: Record<RiskLevel, Record<PageLanguage, string>> = {
  low: { en: "Low", zh: "低", fr: "Faible" },
  guarded: { en: "Guarded", zh: "受控", fr: "Surveillé" },
  elevated: { en: "Elevated", zh: "升高", fr: "Élevé" },
  severe: { en: "Severe", zh: "严重", fr: "Sévère" },
  critical: { en: "Critical", zh: "关键", fr: "Critique" }
};

const phraseCopy: Record<string, TranslationPair> = {
  "industrial graph console": { zh: "产业图谱控制台", fr: "console de graphe industriel" },
  "Page language": { zh: "页面语言", fr: "Langue de la page" },
  "API linked": { zh: "API 已连接", fr: "API connectée" },
  "API fallback": { zh: "API 回退", fr: "repli API" },
  "mock data": { zh: "模拟数据", fr: "données simulées" },
  refresh: { zh: "刷新", fr: "actualisation" },
  Refresh: { zh: "刷新", fr: "Actualiser" },
  Refreshing: { zh: "刷新中", fr: "Actualisation" },
  "Graph build": { zh: "图构建", fr: "Build du graphe" },
  "Open live monitor": { zh: "打开实时监控", fr: "Ouvrir le moniteur en direct" },
  "Open layer catalog": { zh: "打开图层目录", fr: "Ouvrir le catalogue des couches" },
  "Using mock fallback; API endpoint unavailable.": {
    zh: "正在使用模拟回退；API 端点不可用。",
    fr: "Repli sur les données simulées ; le point d'API est indisponible."
  },
  "Page not configured.": { zh: "页面尚未配置。", fr: "Page non configurée." },
  "of 100": { zh: "/100", fr: "sur 100" },
  percent: { zh: "百分比", fr: "pour cent" },
  "Global exposure canvas": { zh: "全球暴露画布", fr: "Canevas d'exposition mondiale" },
  "Search exposure graph": { zh: "搜索暴露图谱", fr: "Rechercher dans le graphe d'exposition" },
  "Global supply risk hotspot map": { zh: "全球供应风险热点地图", fr: "Carte des points chauds du risque d'approvisionnement" },
  "Incident queue": { zh: "事件队列", fr: "File d'incidents" },
  "Ranked by signal strength and graph reach.": { zh: "按信号强度和图谱触达范围排序。", fr: "Classé par force du signal et portée du graphe." },
  "Corridor stress": { zh: "走廊压力", fr: "Stress des corridors" },
  "Trade lanes carrying disproportionate revenue exposure.": {
    zh: "承载不成比例收入暴露的贸易通道。",
    fr: "Voies commerciales portant une exposition de chiffre d'affaires disproportionnée."
  },
  "Graph filters": { zh: "图谱筛选", fr: "Filtres du graphe" },
  "Scope the visible network without losing node context.": {
    zh: "限定可见网络，同时保留节点上下文。",
    fr: "Délimiter le réseau visible sans perdre le contexte des nœuds."
  },
  "Graph node type": { zh: "图节点类型", fr: "Type de nœud du graphe" },
  all: { zh: "全部", fr: "Tous" },
  company: { zh: "企业", fr: "entreprise" },
  supplier: { zh: "供应商", fr: "fournisseur" },
  facility: { zh: "设施", fr: "site" },
  commodity: { zh: "商品", fr: "produit" },
  route: { zh: "路线", fr: "route" },
  country: { zh: "国家", fr: "pays" },
  signal: { zh: "信号", fr: "signal" },
  "Visible nodes": { zh: "可见节点", fr: "Nœuds visibles" },
  "Visible links": { zh: "可见链接", fr: "Liens visibles" },
  "Focus score": { zh: "焦点分数", fr: "Score focal" },
  "Focus type": { zh: "焦点类型", fr: "Type focal" },
  "Entity network": { zh: "实体网络", fr: "Réseau d'entités" },
  "Click a node to inspect metadata and high-risk adjacency.": {
    zh: "点击节点查看元数据和高风险邻接关系。",
    fr: "Cliquer sur un nœud pour inspecter les métadonnées et adjacences à risque."
  },
  "Save view": { zh: "保存视图", fr: "Enregistrer la vue" },
  "Node inspector": { zh: "节点检查器", fr: "Inspecteur de nœud" },
  "Live metadata attached to the selected graph node.": {
    zh: "所选图节点附带的实时元数据。",
    fr: "Métadonnées actives liées au nœud sélectionné."
  },
  Name: { zh: "名称", fr: "Nom" },
  "Risk level": { zh: "风险等级", fr: "Niveau de risque" },
  Score: { zh: "分数", fr: "Score" },
  Kind: { zh: "类型", fr: "Type" },
  sector: { zh: "行业", fr: "secteur" },
  exposure: { zh: "暴露", fr: "exposition" },
  tier: { zh: "层级", fr: "rang" },
  dependency: { zh: "依赖度", fr: "dépendance" },
  utilization: { zh: "利用率", fr: "utilisation" },
  substitute: { zh: "替代项", fr: "substitut" },
  inventory: { zh: "库存", fr: "stock" },
  volatility: { zh: "波动", fr: "volatilité" },
  delay: { zh: "延迟", fr: "retard" },
  freight: { zh: "运费", fr: "fret" },
  customs: { zh: "海关", fr: "douanes" },
  labor: { zh: "劳工", fr: "main-d'œuvre" },
  "Company watchlist": { zh: "企业观察名单", fr: "Liste de surveillance des entreprises" },
  "Board-level exposure by target company.": { zh: "按目标企业展示董事会级暴露。", fr: "Exposition de niveau direction par entreprise cible." },
  "risk posture": { zh: "风险态势", fr: "posture de risque" },
  confidence: { zh: "置信度", fr: "confiance" },
  "Create watch": { zh: "创建观察", fr: "Créer une veille" },
  "Risk score": { zh: "风险分数", fr: "Score de risque" },
  "Revenue at risk": { zh: "风险收入", fr: "Chiffre d'affaires à risque" },
  "Supplier count": { zh: "供应商数量", fr: "Nombre de fournisseurs" },
  "Top dependency": { zh: "最高依赖", fr: "Dépendance principale" },
  Confidence: { zh: "置信度", fr: "Confiance" },
  None: { zh: "无", fr: "Aucun" },
  "Drivers and mitigations": { zh: "驱动因素与缓释措施", fr: "Facteurs et atténuations" },
  "Highest contribution factors and current response plan.": {
    zh: "最高贡献因素和当前响应计划。",
    fr: "Facteurs les plus contributifs et plan de réponse actuel."
  },
  "Supplier exposure table": { zh: "供应商暴露表", fr: "Table d'exposition fournisseurs" },
  "Spend share, dependency, and lead time by supplier.": {
    zh: "按供应商展示支出占比、依赖度和交付周期。",
    fr: "Part de dépense, dépendance et délai par fournisseur."
  },
  Supplier: { zh: "供应商", fr: "Fournisseur" },
  Country: { zh: "国家", fr: "Pays" },
  Category: { zh: "类别", fr: "Catégorie" },
  Spend: { zh: "支出", fr: "Dépense" },
  Dependency: { zh: "依赖度", fr: "Dépendance" },
  "Lead time": { zh: "交付周期", fr: "Délai" },
  Level: { zh: "等级", fr: "Niveau" },
  "Explained path selector": { zh: "解释路径选择器", fr: "Sélecteur de chemin expliqué" },
  "Trace the concrete graph route behind a risk score movement.": {
    zh: "追踪风险分数变化背后的具体图路径。",
    fr: "Tracer la route du graphe derrière un mouvement de score."
  },
  "Pin explanation": { zh: "固定解释", fr: "Épingler l'explication" },
  "Explained path": { zh: "解释路径", fr: "Chemin expliqué" },
  "point score move": { zh: "分风险变化", fr: "points de mouvement du score" },
  "explanation confidence": { zh: "解释置信度", fr: "confiance de l'explication" },
  "Shock controls": { zh: "冲击控制", fr: "Contrôles du choc" },
  "Change the scenario and the impact model recalculates against the active graph.": {
    zh: "调整场景后，影响模型会基于当前图重新计算。",
    fr: "Modifier le scénario recalcule l'impact sur le graphe actif."
  },
  Running: { zh: "运行中", fr: "En cours" },
  Run: { zh: "运行", fr: "Lancer" },
  Region: { zh: "地区", fr: "Région" },
  Commodity: { zh: "商品", fr: "Produit" },
  Duration: { zh: "持续时间", fr: "Durée" },
  Scope: { zh: "范围", fr: "Portée" },
  Facility: { zh: "设施", fr: "Site" },
  Regional: { zh: "区域", fr: "Régional" },
  Global: { zh: "全球", fr: "Mondial" },
  "Projected impact": { zh: "预测影响", fr: "Impact projeté" },
  "Mock mode uses deterministic scenario math; API mode posts the same payload.": {
    zh: "模拟模式使用确定性场景计算；API 模式发送同一载荷。",
    fr: "Le mode simulé utilise un calcul déterministe ; le mode API envoie la même charge utile."
  },
  "Impact score": { zh: "影响分数", fr: "Score d'impact" },
  "EBITDA at risk": { zh: "风险 EBITDA", fr: "EBITDA à risque" },
  "Recovery time": { zh: "恢复时间", fr: "Temps de reprise" },
  "Awaiting simulation result.": { zh: "等待模拟结果。", fr: "En attente du résultat de simulation." },
  "Affected paths": { zh: "受影响路径", fr: "Chemins affectés" },
  "Mitigation queue": { zh: "缓释队列", fr: "File d'atténuation" },
  "Operational actions ranked by speed-to-impact.": {
    zh: "按见效速度排序的运营动作。",
    fr: "Actions opérationnelles classées par rapidité d'impact."
  },
  "Evidence register": { zh: "证据登记簿", fr: "Registre des preuves" },
  "Causal claims are scored for confidence and disagreement.": {
    zh: "因果主张按置信度和分歧度评分。",
    fr: "Les affirmations causales sont notées par confiance et désaccord."
  },
  "Causal claim focus": { zh: "因果主张焦点", fr: "Focus sur l'affirmation causale" },
  "Causal evidence mini graph": { zh: "因果证据小图", fr: "Mini-graphe des preuves causales" },
  Shock: { zh: "冲击", fr: "Choc" },
  Mechanism: { zh: "机制", fr: "Mécanisme" },
  Outcome: { zh: "结果", fr: "Résultat" },
  causes: { zh: "导致", fr: "cause" },
  shifts: { zh: "改变", fr: "déplace" },
  Disagreement: { zh: "分歧度", fr: "Désaccord" },
  Reviewed: { zh: "已审查", fr: "Révisé" },
  "Evidence quality": { zh: "证据质量", fr: "Qualité des preuves" },
  "Confidence and disagreement are tracked separately.": {
    zh: "置信度和分歧度被分别跟踪。",
    fr: "La confiance et le désaccord sont suivis séparément."
  },
  Claim: { zh: "主张", fr: "Affirmation" },
  Method: { zh: "方法", fr: "Méthode" },
  "Graph builds": { zh: "图构建", fr: "Builds du graphe" },
  "Select a candidate and compare it against the promoted baseline.": {
    zh: "选择候选版本并与已发布基线比较。",
    fr: "Sélectionner un candidat et le comparer à la référence promue."
  },
  "Candidate readiness": { zh: "候选就绪度", fr: "Préparation du candidat" },
  Promote: { zh: "发布", fr: "Promouvoir" },
  Nodes: { zh: "节点", fr: "Nœuds" },
  Edges: { zh: "边", fr: "Arêtes" },
  "Schema changes": { zh: "模式变更", fr: "Changements de schéma" },
  "Validation pass rate": { zh: "校验通过率", fr: "Taux de validation" },
  "Diff matrix": { zh: "差异矩阵", fr: "Matrice de différences" },
  "Material graph changes detected against the promoted baseline.": {
    zh: "相对于已发布基线检测到的重大图变化。",
    fr: "Changements matériels détectés face à la référence promue."
  },
  Area: { zh: "区域", fr: "Zone" },
  Change: { zh: "变化", fr: "Changement" },
  Count: { zh: "数量", fr: "Nombre" },
  Severity: { zh: "严重度", fr: "Sévérité" },
  promoted: { zh: "已发布", fr: "promu" },
  candidate: { zh: "候选", fr: "candidat" },
  archived: { zh: "已归档", fr: "archivé" },
  draft: { zh: "草稿", fr: "brouillon" },
  "Services operational": { zh: "服务运行正常", fr: "Services opérationnels" },
  operational: { zh: "运行正常", fr: "opérationnel" },
  degraded: { zh: "降级", fr: "dégradé" },
  down: { zh: "宕机", fr: "en panne" },
  complete: { zh: "完成", fr: "terminé" },
  queued: { zh: "排队中", fr: "en file" },
  blocked: { zh: "阻塞", fr: "bloqué" },
  "API, graph, model, and signal ingest fleet.": {
    zh: "API、图、模型和信号接入服务群。",
    fr: "Flotte API, graphe, modèle et ingestion de signaux."
  },
  "Pipeline processed": { zh: "管道处理进度", fr: "Pipeline traité" },
  "Current build is advancing through entity resolution.": {
    zh: "当前构建正在推进实体解析。",
    fr: "Le build actuel progresse dans la résolution d'entités."
  },
  "Median latency": { zh: "中位延迟", fr: "Latence médiane" },
  "Across API, graph query, ingest, and scorer endpoints.": {
    zh: "覆盖 API、图查询、接入和评分端点。",
    fr: "Sur les points API, requête graphe, ingestion et scoring."
  },
  "Freshness lag": { zh: "新鲜度滞后", fr: "Retard de fraîcheur" },
  "Signal ingest is the current freshness constraint.": {
    zh: "信号接入是当前新鲜度瓶颈。",
    fr: "L'ingestion de signaux contraint actuellement la fraîcheur."
  },
  "Service status": { zh: "服务状态", fr: "État des services" },
  "Runtime health by service owner.": { zh: "按服务负责人展示运行健康。", fr: "Santé d'exécution par propriétaire de service." },
  "Build pipeline": { zh: "构建管道", fr: "Pipeline de build" },
  "Current graph and scoring run progress.": { zh: "当前图和评分运行进度。", fr: "Progression du graphe et du scoring en cours." },
  "Runtime log": { zh: "运行日志", fr: "Journal d'exécution" },
  "Recent platform events.": { zh: "最近平台事件。", fr: "Événements récents de la plateforme." },
  "Open terminal log": { zh: "打开终端日志", fr: "Ouvrir le journal terminal" },
  "Global risk index": { zh: "全球风险指数", fr: "Indice de risque mondial" },
  "Suppliers watched": { zh: "监控供应商", fr: "Fournisseurs surveillés" },
  "Model confidence": { zh: "模型置信度", fr: "Confiance du modèle" },
  "Port congestion and rare earth exposure raised the composite index.": {
    zh: "港口拥堵和稀土暴露推高了综合指数。",
    fr: "La congestion portuaire et l'exposition aux terres rares ont relevé l'indice composite."
  },
  "Expanded coverage across tier-2 electronics and chemicals.": {
    zh: "扩大了二级电子和化工供应覆盖。",
    fr: "Couverture élargie des fournisseurs électroniques et chimiques de rang 2."
  },
  "Near-term risk concentrated in semiconductors and battery inputs.": {
    zh: "近期风险集中在半导体和电池投入品。",
    fr: "Le risque à court terme se concentre sur les semi-conducteurs et intrants batteries."
  },
  "Evidence coverage improved after graph build 2026.04.30-candidate.": {
    zh: "图构建 2026.04.30-candidate 后证据覆盖有所改善。",
    fr: "La couverture des preuves s'est améliorée après le build 2026.04.30-candidate."
  },
  "Taiwan Strait": { zh: "台湾海峡", fr: "Détroit de Taïwan" },
  "Suez / Red Sea": { zh: "苏伊士 / 红海", fr: "Suez / mer Rouge" },
  "Panama Canal": { zh: "巴拿马运河", fr: "Canal de Panama" },
  "Rhine Industrial Belt": { zh: "莱茵工业带", fr: "Ceinture industrielle du Rhin" },
  "East Asia": { zh: "东亚", fr: "Asie de l'Est" },
  MENA: { zh: "中东北非", fr: "MENA" },
  "Central America": { zh: "中美洲", fr: "Amérique centrale" },
  Europe: { zh: "欧洲", fr: "Europe" },
  China: { zh: "中国", fr: "Chine" },
  Taiwan: { zh: "中国台湾", fr: "Taïwan" },
  Germany: { zh: "德国", fr: "Allemagne" },
  "South Korea": { zh: "韩国", fr: "Corée du Sud" },
  Mexico: { zh: "墨西哥", fr: "Mexique" },
  "Semiconductor bottleneck": { zh: "半导体瓶颈", fr: "Goulot semi-conducteur" },
  "Naval routing alerts": { zh: "海上航线警报", fr: "Alertes de routage maritime" },
  "Insurance spread widening": { zh: "保险价差扩大", fr: "Élargissement des primes d'assurance" },
  "Container reroutes": { zh: "集装箱改道", fr: "Détournements de conteneurs" },
  "Freight rate shock": { zh: "运费冲击", fr: "Choc des taux de fret" },
  "Lead-time variance": { zh: "交付周期波动", fr: "Variance des délais" },
  "Drought restrictions": { zh: "干旱限制", fr: "Restrictions liées à la sécheresse" },
  "Slot scarcity": { zh: "船闸名额稀缺", fr: "Rareté des créneaux" },
  "Water-level watch": { zh: "水位观察", fr: "Surveillance du niveau d'eau" },
  "Chemical feedstock sensitivity": { zh: "化工原料敏感性", fr: "Sensibilité des intrants chimiques" },
  "Foundry wafer allocation tightens after rolling power curbs": {
    zh: "滚动限电后晶圆代工产能分配趋紧",
    fr: "L'allocation de wafers se resserre après des restrictions électriques tournantes"
  },
  "Container dwell time exceeds 7-day threshold on Red Sea diversion lanes": {
    zh: "红海改道航线集装箱滞留时间超过 7 天阈值",
    fr: "Le temps de séjour des conteneurs dépasse 7 jours sur les routes détournées de la mer Rouge"
  },
  "Battery-grade graphite export checks add customs variance": {
    zh: "电池级石墨出口检查增加海关波动",
    fr: "Les contrôles d'exportation du graphite batterie accroissent la variance douanière"
  },
  Shenzhen: { zh: "深圳", fr: "Shenzhen" },
  "Los Angeles": { zh: "洛杉矶", fr: "Los Angeles" },
  Kaohsiung: { zh: "高雄", fr: "Kaohsiung" },
  Rotterdam: { zh: "鹿特丹", fr: "Rotterdam" },
  "Jebel Ali": { zh: "杰贝阿里", fr: "Jebel Ali" },
  Savannah: { zh: "萨凡纳", fr: "Savannah" },
  "Consumer electronics": { zh: "消费电子", fr: "Électronique grand public" },
  "Advanced logic chips": { zh: "先进逻辑芯片", fr: "Puces logiques avancées" },
  "Specialty chemicals": { zh: "特种化学品", fr: "Produits chimiques de spécialité" },
  "EV platforms": { zh: "电动车平台", fr: "plateformes VE" },
  target: { zh: "目标", fr: "cible" },
  none: { zh: "无", fr: "aucun" },
  "31 days": { zh: "31 天", fr: "31 jours" },
  high: { zh: "高", fr: "élevé" },
  stable: { zh: "稳定", fr: "stable" },
  watch: { zh: "观察", fr: "surveillance" },
  "tier-1 dependency": { zh: "一级依赖", fr: "dépendance de rang 1" },
  "sole-source fab": { zh: "单一来源晶圆厂", fr: "fab mono-source" },
  "input exposure": { zh: "投入品暴露", fr: "exposition aux intrants" },
  "shipping lane": { zh: "航运通道", fr: "voie maritime" },
  "alternate assembly": { zh: "替代组装", fr: "assemblage alternatif" },
  "chemical shipments": { zh: "化学品运输", fr: "expéditions chimiques" },
  "Electric vehicles": { zh: "电动车", fr: "véhicules électriques" },
  "Medical devices": { zh: "医疗器械", fr: "dispositifs médicaux" },
  "Grid batteries": { zh: "电网电池", fr: "batteries réseau" },
  "Battery cells": { zh: "电池电芯", fr: "cellules de batterie" },
  "ADAS silicon": { zh: "ADAS 芯片", fr: "silicium ADAS" },
  "Wire harness": { zh: "线束", fr: "faisceau électrique" },
  "Medical resin": { zh: "医用树脂", fr: "résine médicale" },
  "Battery graphite": { zh: "电池石墨", fr: "graphite batterie" },
  "Battery cell sole-source exposure": { zh: "电池电芯单一来源暴露", fr: "exposition mono-source des cellules batterie" },
  "Advanced logic dependency": { zh: "先进逻辑依赖", fr: "dépendance logique avancée" },
  "Red Sea shipping delay": { zh: "红海航运延迟", fr: "retard maritime mer Rouge" },
  "Qualify Vietnam battery pack line": { zh: "认证越南电池包产线", fr: "qualifier la ligne de packs batterie au Vietnam" },
  "Forward-buy power modules": { zh: "提前采购功率模块", fr: "achat anticipé de modules de puissance" },
  "Lock alternate Gulf routing": { zh: "锁定海湾替代路线", fr: "verrouiller un routage alternatif par le Golfe" },
  "Sterile resin feedstock": { zh: "无菌树脂原料", fr: "intrant de résine stérile" },
  "Single port import lane": { zh: "单港进口通道", fr: "voie d'importation à port unique" },
  "Regulatory supplier lock-in": { zh: "监管型供应商锁定", fr: "verrouillage fournisseur réglementaire" },
  "Pre-clear alternate resin": { zh: "预先清关替代树脂", fr: "pré-approuver une résine alternative" },
  "Add EU safety stock": { zh: "增加欧盟安全库存", fr: "ajouter un stock de sécurité UE" },
  "Negotiate expedited validation": { zh: "谈判加速验证", fr: "négocier une validation accélérée" },
  "Graphite export checks": { zh: "石墨出口检查", fr: "contrôles d'exportation du graphite" },
  "Cell separator concentration": { zh: "隔膜供应集中", fr: "concentration des séparateurs" },
  "Port labor watch": { zh: "港口劳工观察", fr: "surveillance sociale portuaire" },
  "Dual-source separator film": { zh: "双来源隔膜薄膜", fr: "double sourcing du film séparateur" },
  "Shift graphite blend": { zh: "调整石墨配方", fr: "modifier le mélange de graphite" },
  "Reserve inland rail capacity": { zh: "预留内陆铁路运力", fr: "réserver de la capacité ferroviaire intérieure" }
};

const skipLocalizationKeys = new Set([
  "id",
  "level",
  "status",
  "kind",
  "method",
  "scope",
  "trend",
  "ticker",
  "startedAt",
  "createdAt",
  "lastReviewed",
  "operatingMode"
]);

interface I18nContextValue {
  language: PageLanguage;
  setLanguage: (language: PageLanguage) => void;
  t: (value: string) => string;
}

const I18nContext = createContext<I18nContextValue>({
  language: "en",
  setLanguage: () => undefined,
  t: (value) => value
});

export function I18nProvider({
  children,
  language,
  setLanguage
}: {
  children: ReactNode;
  language: PageLanguage;
  setLanguage: (language: PageLanguage) => void;
}) {
  return <I18nContext.Provider value={{ language, setLanguage, t: (value) => translateText(value, language) }}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  return useContext(I18nContext);
}

export function translateDashboardPage(page: DashboardPage, language: PageLanguage): DashboardPage {
  return {
    ...page,
    ...(pageCopy[page.id]?.[language] ?? page)
  };
}

export function translateRiskLevel(level: RiskLevel, language: PageLanguage) {
  return riskLevelCopy[level]?.[language] ?? riskLevelCopy[level].en;
}

export function translateText(value: string, language: PageLanguage): string {
  if (language === "en" || !value) return value;
  const exact = phraseCopy[value]?.[language];
  if (exact) return exact;

  const lowerExact = phraseCopy[value.toLowerCase()]?.[language];
  if (lowerExact) return lowerExact;

  return value
    .replace(/(\d+(?:\.\d+)?)% vs prior build/g, (_, valuePart: string) =>
      language === "zh" ? `较上一构建 ${valuePart}%` : `${valuePart} % vs build précédent`
    )
    .replace(/Last refreshed (.*); hotspots are positioned by route and supplier concentration\./g, (_, time: string) =>
      language === "zh"
        ? `最后刷新 ${time}；热点按路线和供应商集中度定位。`
        : `Dernière actualisation ${time} ; les points chauds sont positionnés par route et concentration fournisseur.`
    )
    .replace(/(\d+) companies/g, (_, count: string) => (language === "zh" ? `${count} 家企业` : `${count} entreprises`))
    .replace(/(\d+)% signal strength/g, (_, count: string) => (language === "zh" ? `${count}% 信号强度` : `${count} % de force du signal`))
    .replace(/(\d+)\/100 risk/g, (_, count: string) => (language === "zh" ? `${count}/100 风险` : `${count}/100 risque`))
    .replace(/(\d+)% volume share/g, (_, count: string) => (language === "zh" ? `${count}% 货量占比` : `${count} % de part de volume`))
    .replace(/(.*) to (.*)/g, (_, source: string, target: string) =>
      language === "zh"
        ? `${translateText(source, language)} 至 ${translateText(target, language)}`
        : `${translateText(source, language)} vers ${translateText(target, language)}`
    )
    .replace(/(.*); confidence (.*)\./g, (_, place: string, confidence: string) =>
      language === "zh"
        ? `${translateText(place, language)}；置信度 ${confidence}。`
        : `${translateText(place, language)} ; confiance ${confidence}.`
    )
    .replace(/(.*) risk posture/g, (_, name: string) =>
      language === "zh" ? `${name} 风险态势` : `Posture de risque de ${name}`
    )
    .replace(/(\d+) days/g, (_, days: string) => (language === "zh" ? `${days} 天` : `${days} jours`))
    .replace(/(\d+)d/g, (_, days: string) => (language === "zh" ? `${days}天` : `${days} j`))
    .replace(/(\d+) ms/g, (_, ms: string) => (language === "zh" ? `${ms} 毫秒` : `${ms} ms`))
    .replace(/(\d+) m freshness/g, (_, minutes: string) => (language === "zh" ? `新鲜度 ${minutes} 分钟` : `fraîcheur ${minutes} min`))
    .replace(/(\d+(?:\.\d+)?)% errors/g, (_, errors: string) => (language === "zh" ? `${errors}% 错误` : `${errors} % erreurs`))
    .replace(/(.*); built by (.*)\./g, (_, label: string, author: string) =>
      language === "zh" ? `${translateText(label, language)}；构建者 ${author}。` : `${translateText(label, language)} ; construit par ${author}.`
    )
    .replace(/(.*) point score move; (.*) explanation confidence\./g, (_, scoreMove: string, confidence: string) =>
      language === "zh"
        ? `${scoreMove} 分风险变化；解释置信度 ${confidence}。`
        : `Mouvement de score de ${scoreMove} points ; confiance d'explication ${confidence}.`
    )
    .replace(/(\d+) companies touched by this scenario\./g, (_, count: string) =>
      language === "zh" ? `该场景触达 ${count} 家企业。` : `${count} entreprises touchées par ce scénario.`
    );
}

export function localizeSupplyRiskData(data: SupplyRiskMockData, language: PageLanguage): SupplyRiskMockData {
  if (language === "en") return data;
  return localizeValue(data, language) as SupplyRiskMockData;
}

function localizeValue(value: unknown, language: PageLanguage, key?: string): unknown {
  if (typeof value === "string") {
    return key && skipLocalizationKeys.has(key) ? value : translateText(value, language);
  }
  if (Array.isArray(value)) {
    return value.map((item) => localizeValue(item, language));
  }
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value).map(([entryKey, entryValue]) => [
        entryKey,
        localizeValue(entryValue, language, entryKey)
      ])
    );
  }
  return value;
}
