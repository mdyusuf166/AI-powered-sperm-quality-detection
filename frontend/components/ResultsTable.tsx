import Link from "next/link";
import { ExternalLink } from "lucide-react";
import type { AnalysisSummary } from "@/lib/api";

type Props = {
  analyses: AnalysisSummary[];
};

export function ResultsTable({ analyses }: Props) {
  return (
    <section className="panel">
      <div className="panel-header">
        <h3>Recent Analyses</h3>
        <p>Completed reports stay linked to coded sample identifiers only.</p>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Sample</th>
              <th>File</th>
              <th>Media</th>
              <th>Status</th>
              <th>Created</th>
              <th>Report</th>
            </tr>
          </thead>
          <tbody>
            {analyses.length === 0 ? (
              <tr>
                <td colSpan={6}>No analyses yet.</td>
              </tr>
            ) : (
              analyses.map((analysis) => (
                <tr key={analysis.id}>
                  <td>{analysis.patient_code ?? "Uncoded"}</td>
                  <td>{analysis.original_filename}</td>
                  <td>{analysis.media_type}</td>
                  <td>
                    <span className={`tag tag-${analysis.status}`}>{analysis.status}</span>
                  </td>
                  <td>{new Date(analysis.created_at).toLocaleString()}</td>
                  <td>
                    <Link className="link-button" href={`/analyses/${analysis.id}`}>
                      Open <ExternalLink size={15} aria-hidden="true" />
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

