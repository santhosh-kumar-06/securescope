import React from "react";
import { Activity, Zap } from "lucide-react";
import { SectionHeader, SeverityBadge, EmptyState } from "./Primitives";

export default function SecurityEvents({ events, onGenerateDemo, onCorrelate, loading }) {
  return (
    <div className="card">
      <SectionHeader icon={<Activity className="w-4 h-4" />} title="Security Events">
        <div className="flex gap-2">
          <button
            onClick={onGenerateDemo}
            className="text-xs bg-base-700 hover:bg-base-600 text-slate-200 px-3 py-1.5 rounded-md flex items-center gap-1.5"
          >
            <Zap className="w-3.5 h-3.5" /> Load demo scenario
          </button>
          <button
            onClick={onCorrelate}
            disabled={loading}
            className="text-xs bg-accent-teal/90 hover:bg-accent-teal text-base-950 font-semibold px-3 py-1.5 rounded-md disabled:opacity-60"
          >
            Run correlation
          </button>
        </div>
      </SectionHeader>

      {!events.length ? (
        <EmptyState message="No security events yet. Load the demo scenario to see detection in action." />
      ) : (
        <div className="overflow-x-auto -mx-2">
          <table className="w-full text-sm min-w-[720px]">
            <thead>
              <tr className="text-left text-xs text-slate-500 border-b border-base-700">
                <th className="py-2 px-2">Timestamp</th>
                <th className="px-2">Event ID</th>
                <th className="px-2">Source</th>
                <th className="px-2">User</th>
                <th className="px-2">Asset</th>
                <th className="px-2">Event</th>
                <th className="px-2">Severity</th>
                <th className="px-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {events.map((e) => (
                <tr key={e.id} className="border-b border-base-800 hover:bg-base-800/50">
                  <td className="py-2 px-2 font-mono text-xs">
                    {new Date(e.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </td>
                  <td className="px-2 font-mono text-xs">{e.event_code}</td>
                  <td className="px-2 text-slate-400">{e.source}</td>
                  <td className="px-2">{e.user || "—"}</td>
                  <td className="px-2">{e.asset || "—"}</td>
                  <td className="px-2">{e.event_type}</td>
                  <td className="px-2"><SeverityBadge level={e.severity} /></td>
                  <td className="px-2 text-slate-400">{e.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
