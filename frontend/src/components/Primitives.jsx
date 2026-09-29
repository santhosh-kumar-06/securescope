import React from "react";

const SEVERITY_STYLES = {
  CRITICAL: "bg-sev-critical/15 text-sev-critical border-sev-critical/40",
  HIGH: "bg-sev-high/15 text-sev-high border-sev-high/40",
  MEDIUM: "bg-sev-medium/15 text-sev-medium border-sev-medium/40",
  LOW: "bg-sev-low/15 text-sev-low border-sev-low/40",
  INFO: "bg-sev-info/15 text-sev-info border-sev-info/40",
};

export function SeverityBadge({ level }) {
  const style = SEVERITY_STYLES[level] || SEVERITY_STYLES.INFO;
  return (
    <span className={`px-2 py-0.5 rounded-md text-xs font-semibold border ${style}`}>
      {level}
    </span>
  );
}

const STATUS_STYLES = {
  NORMAL: "text-slate-400",
  MONITORING: "text-accent-blue",
  INVESTIGATING: "text-sev-high",
  CONTAINED: "text-accent-teal",
  RESOLVED: "text-emerald-400",
};

export function StatusPill({ status }) {
  return (
    <span className={`text-xs font-medium ${STATUS_STYLES[status] || "text-slate-400"}`}>
      ● {status}
    </span>
  );
}

export function StatCard({ label, value, sub }) {
  return (
    <div className="card flex flex-col gap-1">
      <span className="text-xs text-slate-400">{label}</span>
      <span className="text-2xl font-semibold text-slate-100">{value}</span>
      {sub && <span className="text-xs text-slate-500">{sub}</span>}
    </div>
  );
}

export function SectionHeader({ icon, title, children }) {
  return (
    <div className="flex items-center justify-between mb-3">
      <div className="section-title">
        {icon}
        {title}
      </div>
      {children}
    </div>
  );
}

export function EmptyState({ message }) {
  return <div className="text-sm text-slate-500 py-6 text-center">{message}</div>;
}
