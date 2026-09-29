const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = "Request failed.";
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      // ignore parse errors, keep generic message
    }
    throw new Error(detail);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  health: () => request("/api/health"),
  startScan: (target, demo = false) =>
    request(`/api/scan?demo=${demo}`, { method: "POST", body: JSON.stringify({ target }) }),
  getScan: (id) => request(`/api/scans/${id}`),
  listAttackTechniques: () => request("/api/attack-techniques"),
  listEvents: () => request("/api/events"),
  createTestEvent: (payload) => request("/api/test-events", { method: "POST", body: JSON.stringify(payload) }),
  listIncidents: () => request("/api/incidents"),
  getIncident: (id) => request(`/api/incidents/${id}`),
  correlateIncidents: () => request("/api/incidents/correlate", { method: "POST" }),
  updateIncidentStatus: (id, status) =>
    request(`/api/incidents/${id}/status`, { method: "PATCH", body: JSON.stringify({ status }) }),
  recordResponseAction: (payload) =>
    request("/api/response-actions", { method: "POST", body: JSON.stringify(payload) }),
  listDefenses: () => request("/api/defenses"),
  listAuditLogs: () => request("/api/audit-logs"),
};
