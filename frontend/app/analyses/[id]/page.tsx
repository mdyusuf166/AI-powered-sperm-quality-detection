"use client";

import Link from "next/link";
import { ArrowLeft, FileText } from "lucide-react";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { MetricsCards } from "@/components/MetricsCards";
import { API_BASE, apiHeaders, type AnalysisDetail } from "@/lib/api";

export default function AnalysisDetailPage() {
  const params = useParams<{ id: string }>();
  const [analysis, setAnalysis] = useState<AnalysisDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const response = await fetch(`${API_BASE}/api/v1/analyses/${params.id}`, {
          headers: apiHeaders()
        });
        if (!response.ok) {
          throw new Error("Analysis not found.");
        }
        setAnalysis((await response.json()) as AnalysisDetail);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Could not load analysis.");
      }
    }
    void load();
  }, [params.id]);

  const report = analysis?.report_json as DetailReport | null | undefined;

  return (
    <div className="dashboard">
      <header className="topbar">
        <div className="brand">
          <h1>Analysis Report</h1>
          <span>{analysis?.original_filename ?? "Loading sample"}</span>
        </div>
        <Link className="status-pill" href="/">
          <ArrowLeft size={18} aria-hidden="true" />
          Dashboard
        </Link>
      </header>

      <div className="content">
        <section className="panel">
          <div className="panel-header">
            <h2>Sample Metadata</h2>
            <p>{analysis?.patient_code ?? "No coded sample identifier"}</p>
          </div>
          <div className="detail-body">
            {error ? <div className="alert alert-error">{error}</div> : null}
            <p>
              <strong>Status:</strong> {analysis?.status ?? "loading"}
            </p>
            <p>
              <strong>Media:</strong> {analysis?.media_type ?? "N/A"}
            </p>
            <p>
              <strong>Created:</strong>{" "}
              {analysis ? new Date(analysis.created_at).toLocaleString() : "N/A"}
            </p>
            {analysis?.error_message ? <div className="alert alert-error">{analysis.error_message}</div> : null}
          </div>
        </section>

        <div className="main-column">
          <MetricsCards analysis={analysis} />
          <section className="panel">
            <div className="panel-header">
              <h3>
                <FileText size={17} aria-hidden="true" /> Clinical Support Summary
              </h3>
              <p>{report?.summary?.risk_level ?? "Pending"}</p>
            </div>
            <div className="detail-body report-grid">
              <div>
                <h3>Interpretation</h3>
                <ul className="report-list">
                  {(report?.summary?.interpretation ?? []).map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
                <h3>Warnings</h3>
                <ul className="report-list">
                  {(report?.warnings ?? []).map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
              <pre className="mono-block">{JSON.stringify(analysis?.result_json ?? {}, null, 2)}</pre>
            </div>
          </section>
        </div>
      </div>

      <p className="footer-note">
        Research and clinical decision-support only. Confirm findings with validated laboratory procedures and clinician review.
      </p>
    </div>
  );
}

type DetailReport = {
  summary?: {
    risk_level?: string;
    interpretation?: string[];
  };
  warnings?: string[];
};

