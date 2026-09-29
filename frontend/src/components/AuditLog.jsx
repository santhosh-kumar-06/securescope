import React from "react";
import { FileClock } from "lucide-react";
import { SectionHeader, EmptyState } from "./Primitives";

export default function AuditLog({ logs }) {
  return (
    <div className="card">
      <SectionHeader icon={<FileClock className="w-4 h-4" />} title="Evidence / Audit Log" />
      {!logs.length ? (
        <EmptyState message="No audit entries yet." />
      ) : (
        <div className="overflow-x-auto -mx-2 max-h-72 overflow-y-auto">
          <table className="w-full text-xs min-w-[520px]">
            <thead className="sticky top-0 bg-base-850">
              <tr className="text-left text-slate-500 border-b border-base-700">
                <th className="py-2 px-2">Timestamp</th>
                <th className="px-2">Actor</th>
                <th className="px-2">Action</th>
                <th className="px-2">Details</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((l) => (
                <tr key={l.id} className="border-b border-base-800">
                  <td className="py-1.5 px-2 font-mono text-slate-400">
                    {new Date(l.timestamp).toLocaleString()}
                  </td>
                  <td className="px-2">{l.actor}</td>
                  <td className="px-2 text-slate-300">{l.action}</td>
                  <td className="px-2 text-slate-500 truncate max-w-[260px]">
                    {l.details ? JSON.stringify(l.details) : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
