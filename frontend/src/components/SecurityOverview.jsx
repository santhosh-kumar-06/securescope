import React from "react";
import { StatCard } from "./Primitives";

export default function SecurityOverview({ scanState, incidents }) {
  const highExposures = (scanState.findings || []).filter(
    (f) => f.risk === "HIGH" || f.risk === "CRITICAL"
  ).length;
  const activeIncidents = incidents.filter(
    (i) => i.status !== "RESOLVED" && i.status !== "CONTAINED"
  ).length;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      <StatCard label="Target" value={scanState.target || "—"} />
      <StatCard label="Host/IP" value={scanState.resolved_host || "—"} />
      <StatCard label="Scan status" value={scanState.status || "Ready"} />
      <StatCard label="Open services" value={(scanState.services || []).filter(s => s.reachable === "open").length} />
      <StatCard label="High-risk exposures" value={highExposures} />
      <StatCard label="Active incidents" value={activeIncidents} />
    </div>
  );
}
