import React, { useState } from "react";
import { Network, ChevronDown, ChevronUp } from "lucide-react";
import { SectionHeader, SeverityBadge, EmptyState } from "./Primitives";

export default function NetworkExposure({ services, findings }) {
  const [expanded, setExpanded] = useState(null);

  if (!services.length) {
    return (
      <div className="card">
        <SectionHeader icon={<Network className="w-4 h-4" />} title="Network Exposure" />
        <EmptyState message="Run an assessment to discover reachable services." />
      </div>
    );
  }

  const findingByService = Object.fromEntries(findings.map((f) => [f.service_id, f]));

  return (
    <div className="card">
      <SectionHeader icon={<Network className="w-4 h-4" />} title="Network Exposure" />
      <div className="overflow-x-auto -mx-2">
        <table className="w-full text-sm min-w-[560px]">
          <thead>
            <tr className="text-left text-xs text-slate-500 border-b border-base-700">
              <th className="py-2 px-2">Port</th>
              <th className="px-2">Service</th>
              <th className="px-2">Reachability</th>
              <th className="px-2">Exposure</th>
              <th className="px-2">Risk</th>
              <th className="px-2" />
            </tr>
          </thead>
          <tbody>
            {services.map((svc) => {
              const finding = findingByService[svc.id];
              const isOpenPanel = expanded === svc.id;
              return (
                <React.Fragment key={svc.id}>
                  <tr className="border-b border-base-800 hover:bg-base-800/50">
                    <td className="py-2 px-2 font-mono">{svc.port}</td>
                    <td className="px-2 font-medium text-slate-200">{svc.service_name}</td>
                    <td className="px-2">
                      <span className={svc.reachable === "open" ? "text-sev-high" : "text-slate-500"}>
                        {svc.reachable}
                      </span>
                    </td>
                    <td className="px-2 text-slate-400">{svc.exposure}</td>
                    <td className="px-2">
                      {finding ? <SeverityBadge level={finding.risk} /> : <span className="text-slate-600">—</span>}
                    </td>
                    <td className="px-2 text-right">
                      {finding && (
                        <button
                          onClick={() => setExpanded(isOpenPanel ? null : svc.id)}
                          className="text-slate-400 hover:text-slate-200"
                        >
                          {isOpenPanel ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </button>
                      )}
                    </td>
                  </tr>
                  {isOpenPanel && finding && (
                    <tr className="bg-base-900/60">
                      <td colSpan={6} className="px-4 py-3 text-xs text-slate-300">
                        <p className="mb-2">
                          <span className="text-slate-500">Reason: </span>
                          {finding.reason}
                        </p>
                        <p className="mb-2">
                          <span className="text-slate-500">Business impact: </span>
                          {finding.business_impact}
                        </p>
                        <p className="mb-2">
                          <span className="text-slate-500">Detection considerations: </span>
                          {finding.detection_considerations}
                        </p>
                        <div>
                          <span className="text-slate-500">Recommended controls:</span>
                          <ul className="list-disc list-inside mt-1 space-y-0.5">
                            {(finding.recommended_controls || []).map((c, i) => (
                              <li key={i}>{c}</li>
                            ))}
                          </ul>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
