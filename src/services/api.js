/**
 * REST API Client for PrivacyGuard IPv6
 * Communicates with Flask / fullstack backend endpoints.
 */

const BASE_URL = '/api';

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  };

  try {
    const res = await fetch(url, config);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const errorMsg = data.error || `HTTP ${res.status}: ${res.statusText}`;
      throw new Error(errorMsg);
    }
    return data;
  } catch (err) {
    console.error(`API Error on [${options.method || 'GET'} ${url}]:`, err.message);
    throw err;
  }
}

export const api = {
  // General & Dashboard
  getHealth: () => request('/health'),
  getDashboard: (tenantId) => request(`/dashboard?tenant_id=${tenantId}`),

  // Devices
  getDevices: (tenantId) => request(`/devices?tenant_id=${tenantId}`),
  getDeviceEvents: (deviceId, tenantId) => request(`/devices/${deviceId}/events?tenant_id=${tenantId}`),
  rotateAddress: (deviceId, tenantId) =>
    request(`/devices/${deviceId}/rotate-address`, {
      method: 'POST',
      body: JSON.stringify({ tenant_id: tenantId })
    }),
  connectDevice: (deviceId, tenantId) =>
    request(`/devices/${deviceId}/connect`, {
      method: 'POST',
      body: JSON.stringify({ tenant_id: tenantId })
    }),
  disconnectDevice: (deviceId, tenantId) =>
    request(`/devices/${deviceId}/disconnect`, {
      method: 'POST',
      body: JSON.stringify({ tenant_id: tenantId })
    }),

  // Monitoring
  getMonitoringStatus: (tenantId) => request(`/monitoring/status?tenant_id=${tenantId}`),
  startMonitoring: () => request('/monitoring/start', { method: 'POST' }),
  stopMonitoring: () => request('/monitoring/stop', { method: 'POST' }),

  // Simulation
  simulateNormalTraffic: (tenantId, count = 5) =>
    request('/simulation/normal-traffic', {
      method: 'POST',
      body: JSON.stringify({ tenant_id: tenantId, count })
    }),
  simulateRogueRA: (tenantId, source, prefix) =>
    request('/simulation/rogue-ra', {
      method: 'POST',
      body: JSON.stringify({ tenant_id: tenantId, source_ipv6: source, advertised_prefix: prefix })
    }),
  simulateNDPAnomaly: (tenantId, burstCount = 55, pseudonym = null) =>
    request('/simulation/ndp-anomaly', {
      method: 'POST',
      body: JSON.stringify({ tenant_id: tenantId, burst_count: burstCount, pseudonym })
    }),
  resetDemo: () => request('/simulation/reset', { method: 'POST' }),

  // Alerts
  getAlerts: (tenantId, severity, category) => {
    let q = `/alerts?tenant_id=${tenantId}`;
    if (severity) q += `&severity=${severity}`;
    if (category) q += `&category=${category}`;
    return request(q);
  },
  getAlertDetail: (alertId, tenantId) => request(`/alerts/${alertId}?tenant_id=${tenantId}`),
  acknowledgeAlert: (alertId, tenantId, analyst = 'SOC-Analyst-1') =>
    request(`/alerts/${alertId}/acknowledge`, {
      method: 'POST',
      body: JSON.stringify({ tenant_id: tenantId, analyst })
    }),

  // Privacy
  getPrivacyStatus: (tenantId) => request(`/privacy/status?tenant_id=${tenantId}`),
  getPseudonyms: (tenantId) => request(`/privacy/pseudonyms?tenant_id=${tenantId}`),
  expirePseudonym: (pseudonym, tenantId) =>
    request('/privacy/pseudonyms/expire', {
      method: 'POST',
      body: JSON.stringify({ pseudonym, tenant_id: tenantId })
    }),
  getSessions: (tenantId) => request(`/privacy/sessions?tenant_id=${tenantId}`),
  revokeSession: (sessionId, tenantId) =>
    request('/privacy/sessions/revoke', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, tenant_id: tenantId })
    }),

  // Analytics
  getTrafficAnalytics: (tenantId) => request(`/analytics/traffic?tenant_id=${tenantId}`),
  getAlertAnalytics: (tenantId) => request(`/analytics/alerts?tenant_id=${tenantId}`),
  getDetectionBreakdown: (tenantId) => request(`/analytics/detection?tenant_id=${tenantId}`),

  // Evaluation
  runEvaluation: (tenantId) =>
    request('/evaluation/run', {
      method: 'POST',
      body: JSON.stringify({ tenant_id: tenantId })
    }),
  getEvaluationResults: () => request('/evaluation/results'),

  // Settings
  getSettings: () => request('/settings'),
  updateSettings: (settings) =>
    request('/settings', {
      method: 'PUT',
      body: JSON.stringify(settings)
    })
};
