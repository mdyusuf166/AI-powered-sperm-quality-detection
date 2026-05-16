import type { AnalysisDetail } from "@/lib/api";

type Props = {
  analysis: AnalysisDetail | null;
};

export function MetricsCards({ analysis }: Props) {
  const result = analysis?.result_json as ResultShape | null | undefined;
  const report = analysis?.report_json as ReportShape | null | undefined;
  const count = result?.counting;
  const motility = result?.motility;
  const morphology = result?.morphology;

  const metrics = [
    {
      label: "Detected Cells",
      value: formatValue(count?.detected_cells),
      hint: analysis ? analysis.media_type : "Waiting for upload"
    },
    {
      label: "Concentration",
      value: formatValue(count?.concentration_million_per_ml),
      hint: "million / mL estimate"
    },
    {
      label: "Progressive Motility",
      value: percentValue(motility?.progressive_percent),
      hint: `${formatValue(motility?.tracked_cells)} tracked cells`
    },
    {
      label: "Normal-like Morphology",
      value: percentValue(morphology?.normal_like_percent),
      hint: report?.summary?.risk_level ?? "screening status"
    }
  ];

  return (
    <section className="metric-grid" aria-label="Key metrics">
      {metrics.map((metric) => (
        <article className="metric" key={metric.label}>
          <span>{metric.label}</span>
          <strong>{metric.value}</strong>
          <small>{metric.hint}</small>
        </article>
      ))}
    </section>
  );
}

type ResultShape = {
  counting?: {
    detected_cells?: number;
    concentration_million_per_ml?: number | null;
  };
  motility?: {
    tracked_cells?: number;
    progressive_percent?: number | null;
  };
  morphology?: {
    normal_like_percent?: number | null;
  };
};

type ReportShape = {
  summary?: {
    risk_level?: string;
  };
};

function formatValue(value: unknown) {
  if (value === null || value === undefined || value === "") {
    return "N/A";
  }
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(2);
  }
  return String(value);
}

function percentValue(value: unknown) {
  if (typeof value !== "number") {
    return "N/A";
  }
  return `${value.toFixed(1)}%`;
}

