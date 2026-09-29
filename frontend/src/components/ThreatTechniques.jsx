import React, { useState } from "react";
import { Crosshair, ChevronDown, ChevronUp } from "lucide-react";
import { SectionHeader, EmptyState } from "./Primitives";

export default function ThreatTechniques({ techniques }) {
  const [open, setOpen] = useState(techniques[0]?.id || null);

  return (
    <div className="card">
      <SectionHeader icon={<Crosshair className="w-4 h-4" />} title="Threat & Attack Techniques" />
      {!techniques.length && <EmptyState message="No technique data loaded." />}
      <div className="space-y-2">
        {techniques.map((t) => {
          const isOpen = open === t.id;
          return (
            <div key={t.id} className="border border-base-700 rounded-lg overflow-hidden">
              <button
                onClick={() => setOpen(isOpen ? null : t.id)}
                className="w-full flex items-center justify-between px-3 py-2 bg-base-900/60 hover:bg-base-900"
              >
                <span className="text-sm font-medium text-slate-200">
                  {t.name} {t.mitre_ref && <span className="text-xs text-slate-500 font-mono">({t.mitre_ref})</span>}
                </span>
                {isOpen ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
              </button>
              {isOpen && (
                <div className="px-3 py-3 text-xs text-slate-300 space-y-2">
                  <p>{t.description}</p>
                  <div>
                    <span className="text-slate-500">Detection indicators:</span>
                    <ul className="list-disc list-inside mt-1 space-y-0.5">
                      {(t.detection_indicators || []).map((d, i) => <li key={i}>{d}</li>)}
                    </ul>
                  </div>
                  <div>
                    <span className="text-slate-500">Defensive controls:</span>
                    <ul className="list-disc list-inside mt-1 space-y-0.5">
                      {(t.defensive_controls || []).map((d, i) => <li key={i}>{d}</li>)}
                    </ul>
                  </div>
                  <div>
                    <span className="text-slate-500">Affected assets: </span>
                    {(t.affected_assets || []).join(", ")}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
