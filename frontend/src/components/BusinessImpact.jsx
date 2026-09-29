import React from "react";
import { HeartPulse } from "lucide-react";
import { SectionHeader } from "./Primitives";

const ASSETS = [
  { name: "Patient records", note: "Confidentiality and integrity of clinical history." },
  { name: "Clinical scheduling", note: "Availability of appointment and care-coordination systems." },
  { name: "Administrative systems", note: "Billing, HR, and operational continuity." },
  { name: "Identity systems", note: "Trust anchor for every other access decision." },
];

export default function BusinessImpact() {
  return (
    <div className="card">
      <SectionHeader icon={<HeartPulse className="w-4 h-4" />} title="Why This Matters" />
      <p className="text-xs text-slate-300 mb-3">
        A compromised identity or exposed administrative service can provide an indirect path
        toward systems supporting patient records and clinical scheduling. No real patient data
        is used anywhere in this tool — all findings and events are fictional/demo.
      </p>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {ASSETS.map((a) => (
          <div key={a.name} className="border border-base-700 rounded-lg p-2.5">
            <div className="text-xs font-semibold text-slate-200">{a.name}</div>
            <div className="text-[11px] text-slate-500 mt-0.5">{a.note}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
