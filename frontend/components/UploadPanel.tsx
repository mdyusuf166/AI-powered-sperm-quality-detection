"use client";

import { Activity, ShieldCheck, UploadCloud } from "lucide-react";
import { FormEvent, useState } from "react";
import { API_BASE, apiHeaders, type AnalysisDetail } from "@/lib/api";

type Props = {
  onCompleted: (analysis: AnalysisDetail) => void;
};

export function UploadPanel({ onCompleted }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [patientCode, setPatientCode] = useState("");
  const [micronsPerPixel, setMicronsPerPixel] = useState("0.33");
  const [chamberDepth, setChamberDepth] = useState("20");
  const [maxFrames, setMaxFrames] = useState("300");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setError("Choose a microscope image or video first.");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    const metadata = {
      microns_per_pixel: Number(micronsPerPixel),
      chamber_depth_microns: Number(chamberDepth),
      max_frames: Number(maxFrames)
    };

    const formData = new FormData();
    formData.append("file", file);
    if (patientCode.trim()) {
      formData.append("patient_code", patientCode.trim());
    }
    formData.append("sample_metadata", JSON.stringify(metadata));

    try {
      const response = await fetch(`${API_BASE}/api/v1/analyses/uploads`, {
        method: "POST",
        headers: apiHeaders(),
        body: formData
      });
      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.detail ?? "Upload failed.");
      }
      const analysis = (await response.json()) as AnalysisDetail;
      onCompleted(analysis);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>New Analysis</h2>
        <p>Upload a calibrated microscopy image or video for automated screening.</p>
      </div>
      <form className="upload-form" onSubmit={submit}>
        <label className="file-zone">
          <UploadCloud size={30} aria-hidden="true" />
          <strong>{file ? file.name : "Select image or video"}</strong>
          <span>JPG, PNG, TIFF, MP4, MOV, AVI, MKV, WEBM</span>
          <input
            accept=".jpg,.jpeg,.png,.tif,.tiff,.bmp,.mp4,.mov,.avi,.mkv,.webm"
            hidden
            type="file"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
        </label>

        <div className="field">
          <label htmlFor="patient-code">Coded Patient / Sample ID</label>
          <input
            id="patient-code"
            placeholder="No names or direct identifiers"
            value={patientCode}
            onChange={(event) => setPatientCode(event.target.value)}
          />
        </div>

        <div className="form-grid">
          <div className="field">
            <label htmlFor="microns">Microns per pixel</label>
            <input
              id="microns"
              min="0.01"
              step="0.01"
              type="number"
              value={micronsPerPixel}
              onChange={(event) => setMicronsPerPixel(event.target.value)}
            />
          </div>
          <div className="field">
            <label htmlFor="depth">Chamber depth um</label>
            <input
              id="depth"
              min="1"
              step="1"
              type="number"
              value={chamberDepth}
              onChange={(event) => setChamberDepth(event.target.value)}
            />
          </div>
        </div>

        <div className="field">
          <label htmlFor="frames">Max video frames analyzed</label>
          <input
            id="frames"
            min="1"
            step="1"
            type="number"
            value={maxFrames}
            onChange={(event) => setMaxFrames(event.target.value)}
          />
        </div>

        {error ? <div className="alert alert-error">{error}</div> : null}

        <button className="primary-button" disabled={isSubmitting} type="submit">
          {isSubmitting ? <Activity size={18} aria-hidden="true" /> : <ShieldCheck size={18} aria-hidden="true" />}
          {isSubmitting ? "Analyzing" : "Run Analysis"}
        </button>
      </form>
    </section>
  );
}

