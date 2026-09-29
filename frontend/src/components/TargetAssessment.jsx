import React, { useState } from "react";
import { Search, Loader2 } from "lucide-react";
import { SectionHeader } from "./Primitives";

export default function TargetAssessment({ onScan, scanState }) {
  const [target, setTarget] = useState("healthcare.example.org");
  const [demo, setDemo] = useState(true);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!target.trim()) return;
    onScan(target.trim(), demo);
  };

  return (
    <div className="card">
      <SectionHeader icon={<Search className="w-4 h-4" />} title="Target Assessment" />
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
        <input
          value={target}
          onChange={(e) => setTarget(e.target.value)}
          placeholder="example.com or 192.168.1.10"
          className="flex-1 bg-base-900 border border-base-600 rounded-lg px-3 py-2 text-sm
                     focus:outline-none focus:ring-2 focus:ring-accent-teal/50"
        />
        <label className="flex items-center gap-2 text-xs text-slate-400 whitespace-nowrap px-1">
          <input
            type="checkbox"
            checked={demo}
            onChange={(e) => setDemo(e.target.checked)}
            className="accent-accent-teal"
          />
          Demo mode (no live network I/O)
        </label>
        <button
          type="submit"
          disabled={scanState.status === "SCANNING"}
          className="bg-accent-teal/90 hover:bg-accent-teal text-base-950 font-semibold text-sm
                     px-4 py-2 rounded-lg flex items-center justify-center gap-2 transition disabled:opacity-60"
        >
          {scanState.status === "SCANNING" ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" /> Scanning…
            </>
          ) : (
            "Start Assessment"
          )}
        </button>
      </form>

      <div className="mt-3 flex flex-wrap gap-x-6 gap-y-1 text-xs text-slate-400">
        <span>
          Status: <span className="text-slate-200 font-medium">{scanState.status || "Ready"}</span>
        </span>
        {scanState.resolved_host && (
          <span>
            Resolved: <span className="text-slate-200 font-mono">{scanState.resolved_host}</span>
          </span>
        )}
        {scanState.duration_ms != null && (
          <span>
            Duration: <span className="text-slate-200">{scanState.duration_ms} ms</span>
          </span>
        )}
        {scanState.error_message && (
          <span className="text-sev-high">{scanState.error_message}</span>
        )}
      </div>
      <p className="mt-2 text-[11px] text-slate-500">
        Authorized, non-destructive assessment only — a bare TCP connect against a fixed,
        whitelisted port set. No exploitation, credential access, or payload delivery.
      </p>
    </div>
  );
}
