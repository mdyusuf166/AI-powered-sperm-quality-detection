"use client";

import { Microscope } from "lucide-react";
import { useEffect, useState } from "react";
import { MetricsCards } from "@/components/MetricsCards";
import { ResultsTable } from "@/components/ResultsTable";
import { UploadPanel } from "@/components/UploadPanel";
import { API_BASE, apiHeaders, type AnalysisDetail, type AnalysisSummary } from "@/lib/api";

export default function DashboardPage() {
  const [analyses, setAnalyses] = useState<AnalysisSummary[]>([]);
  const [activeAnalysis, setActiveAnalysis] = useState<AnalysisDetail | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  async function loadAnalyses() {
    try {
      const response = await fetch(`${API_BASE}/api/v1/analyses`, {
        headers: apiHeaders()
      });
      if (!response.ok) {
        throw new Error("Could not load analyses.");
      }
      setAnalyses((await response.json()) as AnalysisSummary[]);
      setLoadError(null);
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : "Could not load analyses.");
    }
  }

  useEffect(() => {
    void loadAnalyses();
  }, []);

  function onCompleted(analysis: AnalysisDetail) {
    setActiveAnalysis(analysis);
    void loadAnalyses();
  }

  return (
    <div className="dashboard">
      <header className="topbar">
        <div className="brand">
          <h1>AI-Based Sperm Detection and Male Infertility Analysis</h1>
          <span>Clinical decision-support research dashboard</span>
        </div>
        <div className="status-pill">
          <Microscope size={18} aria-hidden="true" />
          Research Mode
        </div>
      </header>

      <div className="content">
        <UploadPanel onCompleted={onCompleted} />
        <div className="main-column">
          {loadError ? <div className="alert alert-error">{loadError}</div> : null}
          {activeAnalysis?.status === "failed" ? (
            <div className="alert alert-error">{activeAnalysis.error_message}</div>
          ) : null}
          <MetricsCards analysis={activeAnalysis} />
          {activeAnalysis?.report_json ? (
            <section className="panel">
              <div className="panel-header">
                <h3>Latest Report</h3>
                <p>{String((activeAnalysis.report_json.summary as { risk_level?: string })?.risk_level ?? "review")}</p>
              </div>
              <div className="detail-body">
                <pre className="mono-block">{JSON.stringify(activeAnalysis.report_json, null, 2)}</pre>
              </div>
            </section>
          ) : (
            <div className="alert alert-info">Upload a sample to generate the first automated report.</div>
          )}
          <ResultsTable analyses={analyses} />
        </div>
      </div>

      <p className="footer-note">
        This tool is for research and clinical decision-support only. It is not a final medical diagnosis.
      </p>
    </div>
  );
}

