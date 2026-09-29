import React, { useEffect, useState, useCallback } from "react";
import { AlertCircle } from "lucide-react";
import { api } from "./api";

import Header from "./components/Header";
import TargetAssessment from "./components/TargetAssessment";
import SecurityOverview from "./components/SecurityOverview";
import NetworkExposure from "./components/NetworkExposure";
import ThreatTechniques from "./components/ThreatTechniques";
import BusinessImpact from "./components/BusinessImpact";
import SecurityEvents from "./components/SecurityEvents";
import IncidentTimeline from "./components/IncidentTimeline";
import IncidentResponse from "./components/IncidentResponse";
import PermanentControls from "./components/PermanentControls";
import AuditLog from "./components/AuditLog";

const DEMO_EVENTS = [
  { source: "203.0.113.10", event_type: "External service discovery", severity: "MEDIUM", offset_minutes: 0 },
  { source: "198.51.100.22", user: "admin01", asset: "Identity Provider", event_type: "recovery-code usage", severity: "HIGH", offset_minutes: 14 },
  { source: "198.51.100.22", user: "admin01", asset: "Patient Records System", event_type: "sensitive resource access", severity: "HIGH", offset_minutes: 55 },
  { source: "198.51.100.22", user: "admin01", asset: "Clinical Scheduling", event_type: "potential lateral movement indicator", severity: "HIGH", offset_minutes: 150 },
  { source: "198.51.100.45", user: "admin01", asset: "Patient Records System", event_type: "suspicious outbound transfer", severity: "CRITICAL", offset_minutes: 305 },
];

export default function App() {
  const [backendOnline, setBackendOnline] = useState(null);
  const [scanState, setScanState] = useState({ status: "Ready" });
  const [techniques, setTechniques] = useState([]);
  const [events, setEvents] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [defenses, setDefenses] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const refreshAll = useCallback(async () => {
    try {
      const [ev, inc, def, logs, tech] = await Promise.all([
        api.listEvents(),
        api.listIncidents(),
        api.listDefenses(),
        api.listAuditLogs(),
        api.listAttackTechniques(),
      ]);
      setEvents(ev);
      setIncidents(inc);
      setDefenses(def);
      setAuditLogs(logs);
      setTechniques(tech);
    } catch (e) {
      setError(e.message);
    }
  }, []);

  useEffect(() => {
    api
      .health()
      .then(() => setBackendOnline(true))
      .catch(() => setBackendOnline(false));
    refreshAll();
  }, [refreshAll]);

  const handleScan = async (target, demo) => {
    setError(null);
    setScanState({ status: "SCANNING" });
    try {
      const result = await api.startScan(target, demo);
      setScanState(result);
    } catch (e) {
      setScanState({ status: "FAILED", error_message: e.message });
      setError(e.message);
    }
  };

  const handleGenerateDemo = async () => {
    setError(null);
    setLoading(true);
    try {
      const base = Date.now();
      for (const e of DEMO_EVENTS) {
        await api.createTestEvent({
          source: e.source,
          user: e.user,
          asset: e.asset,
          event_type: e.event_type,
          severity: e.severity,
          timestamp: new Date(base + e.offset_minutes * 60000).toISOString(),
        });
      }
      await refreshAll();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCorrelate = async () => {
    setError(null);
    setLoading(true);
    try {
      await api.correlateIncidents();
      await refreshAll();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRecordAction = async (incidentId, actionType, description) => {
    try {
      await api.recordResponseAction({ incident_id: incidentId, action_type: actionType, description });
      await refreshAll();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleUpdateStatus = async (incidentId, status) => {
    try {
      await api.updateIncidentStatus(incidentId, status);
      await refreshAll();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <div className="min-h-full">
      <Header systemStatus={backendOnline === false ? "Backend unavailable" : "System Operational"} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-6">
        {backendOnline === false && (
          <div className="card border-sev-high/40 bg-sev-high/5 flex items-center gap-2 text-sm text-sev-high">
            <AlertCircle className="w-4 h-4 shrink-0" />
            Cannot reach the SecureScope API. Confirm the backend is running and VITE_API_URL is set correctly.
          </div>
        )}
        {error && (
          <div className="card border-sev-high/40 bg-sev-high/5 flex items-center gap-2 text-sm text-sev-high">
            <AlertCircle className="w-4 h-4 shrink-0" />
            {error}
          </div>
        )}

        <TargetAssessment onScan={handleScan} scanState={scanState} />
        <SecurityOverview scanState={scanState} incidents={incidents} />
        <NetworkExposure services={scanState.services || []} findings={scanState.findings || []} />
        <ThreatTechniques techniques={techniques} />
        <BusinessImpact />
        <SecurityEvents
          events={events}
          onGenerateDemo={handleGenerateDemo}
          onCorrelate={handleCorrelate}
          loading={loading}
        />
        <IncidentTimeline events={events} />
        <IncidentResponse
          incidents={incidents}
          onRecordAction={handleRecordAction}
          onUpdateStatus={handleUpdateStatus}
        />
        <PermanentControls defenses={defenses} />
        <AuditLog logs={auditLogs} />

        <footer className="text-center text-[11px] text-slate-600 py-4">
          SecureScope — a defensive-only training prototype. No real patient data, no offensive tooling.
        </footer>
      </main>
    </div>
  );
}
