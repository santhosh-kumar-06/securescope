import React, { useState } from "react";
import { GitCommitHorizontal } from "lucide-react";
import { SectionHeader, SeverityBadge, EmptyState } from "./Primitives";

export default function IncidentTimeline({ events }) {
  const [selected, setSelected] = useState(null);
  const sorted = [...events].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

  return (
    <div className="card">
      <SectionHeader icon={<GitCommitHorizontal className="w-4 h-4" />} title="Incident Timeline" />
      {!sorted.length ? (
        <EmptyState message="No events to plot yet." />
      ) : (
        <div className="overflow-x-auto pb-2">
          <div className="flex items-start gap-0 min-w-max px-2">
            {sorted.map((e, i) => (
              <div key={e.id} className="flex items-center">
                <button
                  onClick={() => setSelected(e)}
                  className="flex flex-col items-center w-36 group"
                >
                  <span className="text-[11px] text-slate-500 font-mono mb-1">
                    {new Date(e.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </span>
                  <span className="w-3 h-3 rounded-full bg-accent-teal border-2 border-base-950 group-hover:scale-125 transition" />
                  <span className="text-xs text-slate-300 text-center mt-1.5 leading-tight px-1">
                    {e.event_type}
                  </span>
                </button>
                {i < sorted.length - 1 && <div className="w-10 h-px bg-base-600 mt-[18px]" />}
              </div>
            ))}
          </div>
        </div>
      )}

      {selected && (
        <div className="mt-4 border border-base-700 rounded-lg p-3 bg-base-900/60 text-xs text-slate-300">
          <div className="flex items-center justify-between mb-2">
            <span className="font-semibold text-slate-100">{selected.event_type}</span>
            <SeverityBadge level={selected.severity} />
          </div>
          <p>Timestamp: {new Date(selected.timestamp).toLocaleString()}</p>
          <p>Source: {selected.source}</p>
          <p>User: {selected.user || "—"}</p>
          <p>Asset: {selected.asset || "—"}</p>
          <p>Event ID: {selected.event_code}</p>
        </div>
      )}
    </div>
  );
}
