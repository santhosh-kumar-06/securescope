import React from "react";
import { ShieldPlus } from "lucide-react";
import { SectionHeader, EmptyState } from "./Primitives";

export default function PermanentControls({ defenses }) {
  const grouped = defenses.reduce((acc, d) => {
    acc[d.category] = acc[d.category] || [];
    acc[d.category].push(d);
    return acc;
  }, {});

  return (
    <div className="card">
      <SectionHeader icon={<ShieldPlus className="w-4 h-4" />} title="Permanent Security Controls" />
      {!defenses.length ? (
        <EmptyState message="No recommendations loaded." />
      ) : (
        <div className="grid sm:grid-cols-2 gap-4">
          {Object.entries(grouped).map(([category, items]) => (
            <div key={category}>
              <h4 className="text-xs font-semibold text-accent-teal mb-1.5">{category}</h4>
              <ul className="text-xs text-slate-300 space-y-1">
                {items.map((d) => (
                  <li key={d.id} className="flex gap-1.5">
                    <span className="text-slate-600">–</span>
                    <span>{d.recommendation}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
