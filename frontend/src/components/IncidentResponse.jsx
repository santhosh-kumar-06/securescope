import React, { useState } from "react";
import { AlertTriangle } from "lucide-react";
import { SectionHeader, SeverityBadge, StatusPill, EmptyState } from "./Primitives";

const IMMEDIATE_ACTIONS = [
  { type: "Disable compromised credential", desc: "Disable the affected credential immediately." },
  { type: "Revoke active sessions", desc: "Revoke all active sessions for the affected identity." },
  { type: "Rotate exposed secrets", desc: "Rotate any secrets potentially exposed during the incident." },
  { type: "Isolate affected host", desc: "Isolate the affected host from the network." },
  { type: "Investigate destination", desc: "Investigate the destination of the suspicious transfer." },
  { type: "Preserve evidence", desc: "Preserve logs and volatile evidence for investigation." },
];

const STATUS_FLOW = ["MONITORING", "INVESTIGATING", "CONTAINED", "RESOLVED"];

export default function IncidentResponse({ incidents, onRecordAction, onUpdateStatus }) {
  const [activeId, setActiveId] = useState(null);
  const active = incidents.find((i) => i.id === activeId) || incidents[0];

  return (
    <div className="card">
      <SectionHeader icon={<AlertTriangle className="w-4 h-4" />} title="Incident Response" />
      {!incidents.length ? (
        <EmptyState message="No correlated incidents yet. Run correlation after loading events." />
      ) : (
        <div className="grid md:grid-cols-[240px_1fr] gap-4">
          <div className="space-y-2">
            {incidents.map((inc) => (
              <button
                key={inc.id}
                onClick={() => setActiveId(inc.id)}
                className={`w-full text-left border rounded-lg px-3 py-2 transition ${
                  (active && active.id === inc.id)
                    ? "border-accent-teal bg-accent-teal/5"
                    : "border-base-700 hover:bg-base-800/50"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-slate-400">{inc.incident_code}</span>
                  <SeverityBadge level={inc.severity} />
                </div>
                <div className="text-xs text-slate-300 mt-1">{inc.affected_identity || "unknown identity"}</div>
                <StatusPill status={inc.status} />
              </button>
            ))}
          </div>

          {active && (
            <div className="border border-base-700 rounded-lg p-4 text-sm">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <div className="font-semibold text-slate-100">{active.incident_code}</div>
                  <div className="text-xs text-slate-400">
                    {active.event_count} correlated event(s) · {active.affected_asset || "asset unknown"}
                  </div>
                </div>
                <SeverityBadge level={active.severity} />
              </div>

              <p className="text-xs text-slate-300 mb-4">{active.summary}</p>

              <div className="mb-4">
                <span className="text-xs text-slate-500 uppercase tracking-wide">Update status</span>
                <div className="flex flex-wrap gap-2 mt-1.5">
                  {STATUS_FLOW.map((s) => (
                    <button
                      key={s}
                      onClick={() => onUpdateStatus(active.id, s)}
                      className={`text-xs px-2.5 py-1 rounded-md border ${
                        active.status === s
                          ? "border-accent-teal text-accent-teal bg-accent-teal/10"
                          : "border-base-600 text-slate-400 hover:text-slate-200"
                      }`}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <span className="text-xs text-slate-500 uppercase tracking-wide">Recommended actions</span>
                <div className="grid sm:grid-cols-2 gap-2 mt-1.5">
                  {IMMEDIATE_ACTIONS.map((a) => (
                    <button
                      key={a.type}
                      onClick={() => onRecordAction(active.id, a.type, a.desc)}
                      title="Simulate Response — no live action performed"
                      className="text-left text-xs border border-base-600 rounded-md px-2.5 py-2 hover:bg-base-800/50"
                    >
                      <div className="font-medium text-slate-200">{a.type}</div>
                      <div className="text-slate-500">Simulate Response</div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
