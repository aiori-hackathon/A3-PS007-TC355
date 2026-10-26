import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorMessage from './components/ErrorMessage';

// Pages
import Dashboard from './pages/Dashboard';
import Devices from './pages/Devices';
import Monitoring from './pages/Monitoring';
import SecurityAlerts from './pages/SecurityAlerts';
import PrivacyCenter from './pages/PrivacyCenter';
import Analytics from './pages/Analytics';
import Evaluation from './pages/Evaluation';
import Settings from './pages/Settings';

import { api } from './services/api';
import { dashboardService } from './services/dashboardService';

export default function App() {
  const [activePage, setActivePage] = useState('dashboard');
  const [activeTenant, setActiveTenant] = useState('tenant-alpha');
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [backendConnected, setBackendConnected] = useState(true);
  const [errorMessage, setErrorMessage] = useState(null);
  const [toast, setToast] = useState(null);

  // Core Data States
  const [overview, setOverview] = useState({
    summary: {},
    monitoringActive: true,
    recentAlerts: [],
    recentEvents: [],
    traffic: {},
    alertsMeta: {}
  });

  const [devices, setDevices] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [selectedSeverity, setSelectedSeverity] = useState('ALL');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [pseudonyms, setPseudonyms] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [monitoringStatus, setMonitoringStatus] = useState({});
  const [evalResults, setEvalResults] = useState(null);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [settings, setSettings] = useState({});
  const [detectionBreakdown, setDetectionBreakdown] = useState({});

  // Loading indicator states for specific actions
  const [rotatingId, setRotatingId] = useState(null);
  const [acknowledgingId, setAcknowledgingId] = useState(null);
  const [expiringPseudonym, setExpiringPseudonym] = useState(null);
  const [revokingSessionId, setRevokingSessionId] = useState(null);
  const [isSavingSettings, setIsSavingSettings] = useState(false);

  // Toast helper
  const showToast = (message, type = 'info') => {
    setToast({ message, type });
    setTimeout(() => {
      setToast(null);
    }, 4500);
  };

  // Main data loader
  const loadData = useCallback(async (isInitial = false) => {
    if (isInitial) setIsLoading(true);
    else setIsRefreshing(true);
    setErrorMessage(null);

    try {
      // 1. Health check
      await api.getHealth();
      setBackendConnected(true);

      // 2. Fetch page-specific or global overview
      const [ov, devs, alts, pseudos, sess, mon, det] = await Promise.all([
        dashboardService.fetchOverview(activeTenant),
        api.getDevices(activeTenant).catch(() => ({ devices: [] })),
        api.getAlerts(activeTenant, selectedSeverity, selectedCategory).catch(() => ({ alerts: [] })),
        api.getPseudonyms(activeTenant).catch(() => ({ pseudonyms: [] })),
        api.getSessions(activeTenant).catch(() => ({ sessions: [] })),
        api.getMonitoringStatus(activeTenant).catch(() => ({})),
        api.getDetectionBreakdown(activeTenant).catch(() => ({}))
      ]);

      setOverview(ov);
      setDevices(devs.devices || []);
      setAlerts(alts.alerts || []);
      setPseudonyms(pseudos.pseudonyms || []);
      setSessions(sess.sessions || []);
      setMonitoringStatus(mon);
      setDetectionBreakdown(det);

      // Lazy load settings and eval results if needed
      if (isInitial) {
        api.getSettings().then((res) => setSettings(res.settings || {})).catch(() => {});
        api.getEvaluationResults().then((res) => {
          if (res.has_run) setEvalResults(res.results);
        }).catch(() => {});
      }
    } catch (err) {
      setBackendConnected(false);
      setErrorMessage(
        `Unable to communicate with the PrivacyGuard backend: ${err.message}. Please verify the server is running.`
      );
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, [activeTenant, selectedSeverity, selectedCategory]);

  useEffect(() => {
    loadData(true);
  }, [loadData]);

  // Periodic polling for live monitoring telemetry (every 8 seconds)
  useEffect(() => {
    const timer = setInterval(() => {
      loadData(false);
    }, 8000);
    return () => clearInterval(timer);
  }, [loadData]);

  // ========================================================
  // Action Handlers
  // ========================================================

  const handleSimulateRogueRA = async () => {
    try {
      const res = await api.simulateRogueRA(activeTenant);
      showToast(
        res.alert_generated
          ? `[ALERT DETECTED] ${res.detection?.reason || 'Rogue RA detected!'}`
          : 'Rogue RA simulated (no violation flagged).',
        res.alert_generated ? 'error' : 'info'
      );
      await loadData(false);
    } catch (err) {
      showToast(`Simulation failed: ${err.message}`, 'error');
    }
  };

  const handleSimulateNDPAnomaly = async () => {
    try {
      const res = await api.simulateNDPAnomaly(activeTenant, 55);
      showToast(
        res.alert_generated
          ? `[BURST FLAGGED] High-rate NDP burst detected exceeding threshold.`
          : 'NDP packet flood simulated.',
        'warning'
      );
      await loadData(false);
    } catch (err) {
      showToast(`Simulation failed: ${err.message}`, 'error');
    }
  };

  const handleGenerateNormalTraffic = async () => {
    try {
      const res = await api.simulateNormalTraffic(activeTenant, 5);
      showToast(`Transmitted 5 normal ICMPv6 SLAAC & NDP packets without alert.`, 'success');
      await loadData(false);
    } catch (err) {
      showToast(`Failed generating normal traffic: ${err.message}`, 'error');
    }
  };

  const handleRotateAddress = async (deviceId) => {
    setRotatingId(deviceId);
    try {
      const res = await api.rotateAddress(deviceId, activeTenant);
      showToast(
        `Temporary IPv6 rotated to ${res.new_ipv6}. Issued pseudonym: ${res.new_pseudonym} (No alert raised)`,
        'success'
      );
      await loadData(false);
    } catch (err) {
      showToast(`Address rotation failed: ${err.message}`, 'error');
    } finally {
      setRotatingId(null);
    }
  };

  const handleToggleConnection = async (deviceId, isCurrentlyConnected) => {
    try {
      if (isCurrentlyConnected) {
        await api.disconnectDevice(deviceId, activeTenant);
        showToast(`Device ${deviceId} disconnected.`, 'info');
      } else {
        await api.connectDevice(deviceId, activeTenant);
        showToast(`Device ${deviceId} connected.`, 'success');
      }
      await loadData(false);
    } catch (err) {
      showToast(`Status update failed: ${err.message}`, 'error');
    }
  };

  const handleAcknowledgeAlert = async (alertId) => {
    setAcknowledgingId(alertId);
    try {
      await api.acknowledgeAlert(alertId, activeTenant, 'SOC-Lead');
      showToast(`Alert ${alertId} acknowledged with audit trail.`, 'success');
      await loadData(false);
    } catch (err) {
      showToast(`Failed to acknowledge alert: ${err.message}`, 'error');
    } finally {
      setAcknowledgingId(null);
    }
  };

  const handleExpirePseudonym = async (pseudonym) => {
    setExpiringPseudonym(pseudonym);
    try {
      await api.expirePseudonym(pseudonym, activeTenant);
      showToast(`Pseudonym ${pseudonym} expired. Any new event using this token will be rejected.`, 'info');
      await loadData(false);
    } catch (err) {
      showToast(`Failed expiring pseudonym: ${err.message}`, 'error');
    } finally {
      setExpiringPseudonym(null);
    }
  };

  const handleRevokeSession = async (sessionId) => {
    setRevokingSessionId(sessionId);
    try {
      await api.revokeSession(sessionId, activeTenant);
      showToast(`Monitoring session ${sessionId} revoked.`, 'info');
      await loadData(false);
    } catch (err) {
      showToast(`Failed revoking session: ${err.message}`, 'error');
    } finally {
      setRevokingSessionId(null);
    }
  };

  const handleRunEvaluation = async () => {
    setIsEvaluating(true);
    try {
      const res = await api.runEvaluation(activeTenant);
      setEvalResults(res.results);
      showToast(
        `Evaluation complete: Recall: ${res.results.detection_rate}%, FPR: ${res.results.false_positive_rate}%, F1: ${res.results.f1_score}%`,
        'success'
      );
      await loadData(false);
    } catch (err) {
      showToast(`Evaluation run failed: ${err.message}`, 'error');
    } finally {
      setIsEvaluating(false);
    }
  };

  const handleSaveSettings = async (newSettings) => {
    setIsSavingSettings(true);
    try {
      await api.updateSettings(newSettings);
      setSettings(newSettings);
      showToast('Settings saved successfully.', 'success');
      await loadData(false);
    } catch (err) {
      throw err;
    } finally {
      setIsSavingSettings(false);
    }
  };

  const handleResetDemo = async () => {
    try {
      await api.resetDemo();
      showToast('Demonstration environment reset. Baseline 5 IoT devices reseeded.', 'info');
      await loadData(true);
    } catch (err) {
      showToast(`Reset failed: ${err.message}`, 'error');
    }
  };

  const handleExportZip = () => {
    window.location.href = '/api/export-zip';
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Toast Notification */}
      {toast && (
        <div
          className={`fixed bottom-5 right-5 z-50 px-4 py-3 rounded-xl border shadow-2xl flex items-center gap-3 text-xs font-semibold backdrop-blur-md transition-all duration-300 max-w-md ${
            toast.type === 'error'
              ? 'bg-red-950/90 border-red-500/50 text-red-200'
              : toast.type === 'warning'
              ? 'bg-amber-950/90 border-amber-500/50 text-amber-200'
              : toast.type === 'success'
              ? 'bg-emerald-950/90 border-emerald-500/50 text-emerald-200'
              : 'bg-slate-900/90 border-cyan-500/50 text-cyan-200'
          }`}
        >
          <span>{toast.message}</span>
          <button
            onClick={() => setToast(null)}
            className="text-slate-400 hover:text-white ml-2 text-base leading-none cursor-pointer"
          >
            &times;
          </button>
        </div>
      )}

      {/* Top Header */}
      <Header
        activeTenant={activeTenant}
        onTenantChange={setActiveTenant}
        monitoringActive={overview.monitoringActive}
        onRefresh={() => loadData(false)}
        isRefreshing={isRefreshing}
        backendConnected={backendConnected}
        onExportZip={handleExportZip}
      />

      {/* Main Workspace */}
      <div className="flex-1 flex">
        {/* Navigation Sidebar */}
        <Sidebar
          activePage={activePage}
          onNavigate={setActivePage}
          alertCount={alerts.filter((a) => !a.is_acknowledged).length}
          onTriggerRogueRA={handleSimulateRogueRA}
          onTriggerNDPAnomaly={handleSimulateNDPAnomaly}
          onResetDemo={handleResetDemo}
        />

        {/* Content View */}
        <main className="flex-1 p-6 lg:p-8 max-w-7xl mx-auto overflow-y-auto">
          {errorMessage && (
            <ErrorMessage error={errorMessage} onRetry={() => loadData(true)} />
          )}

          {isLoading ? (
            <LoadingSpinner message="Ingesting IPv6 security telemetry & connecting to SQLite..." />
          ) : (
            <>
              {activePage === 'dashboard' && (
                <Dashboard
                  summary={overview.summary}
                  traffic={overview.traffic}
                  recentAlerts={overview.recentAlerts}
                  recentEvents={overview.recentEvents}
                  onSimulateRogueRA={handleSimulateRogueRA}
                  onSimulateNDPAnomaly={handleSimulateNDPAnomaly}
                  onGenerateNormalTraffic={handleGenerateNormalTraffic}
                  onResetDemo={handleResetDemo}
                  onAcknowledgeAlert={handleAcknowledgeAlert}
                  acknowledgingId={acknowledgingId}
                  onNavigate={setActivePage}
                />
              )}

              {activePage === 'devices' && (
                <Devices
                  devices={devices}
                  onRotateAddress={handleRotateAddress}
                  onToggleConnection={handleToggleConnection}
                  onFetchDeviceEvents={(devId) => api.getDeviceEvents(devId, activeTenant)}
                  rotatingId={rotatingId}
                  tenantId={activeTenant}
                />
              )}

              {activePage === 'monitoring' && (
                <Monitoring
                  monitoringActive={overview.monitoringActive}
                  onStartMonitoring={async () => {
                    await api.startMonitoring();
                    loadData(false);
                  }}
                  onStopMonitoring={async () => {
                    await api.stopMonitoring();
                    loadData(false);
                  }}
                  onSimulateRogueRA={handleSimulateRogueRA}
                  onSimulateNDPAnomaly={handleSimulateNDPAnomaly}
                  onGenerateNormalTraffic={handleGenerateNormalTraffic}
                  onRotateAddress={() => handleRotateAddress(devices[0]?.device_id)}
                  onResetDemo={handleResetDemo}
                  events={overview.recentEvents}
                  status={monitoringStatus}
                />
              )}

              {activePage === 'alerts' && (
                <SecurityAlerts
                  alerts={alerts}
                  onAcknowledgeAlert={handleAcknowledgeAlert}
                  acknowledgingId={acknowledgingId}
                  selectedSeverity={selectedSeverity}
                  onSeverityChange={setSelectedSeverity}
                  selectedCategory={selectedCategory}
                  onCategoryChange={setSelectedCategory}
                />
              )}

              {activePage === 'privacy' && (
                <PrivacyCenter
                  pseudonyms={pseudonyms}
                  sessions={sessions}
                  onExpirePseudonym={handleExpirePseudonym}
                  expiringPseudonym={expiringPseudonym}
                  onRevokeSession={handleRevokeSession}
                  revokingSessionId={revokingSessionId}
                  tenantId={activeTenant}
                  onSwitchTenant={setActiveTenant}
                />
              )}

              {activePage === 'analytics' && (
                <Analytics
                  traffic={overview.traffic}
                  alertStats={overview.alertsMeta}
                  detection={detectionBreakdown}
                  tenantId={activeTenant}
                />
              )}

              {activePage === 'evaluation' && (
                <Evaluation
                  results={evalResults}
                  isRunning={isEvaluating}
                  onRunEvaluation={handleRunEvaluation}
                />
              )}

              {activePage === 'settings' && (
                <Settings
                  settings={settings}
                  onSaveSettings={handleSaveSettings}
                  isSaving={isSavingSettings}
                />
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}
