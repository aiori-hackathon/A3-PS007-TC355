import React from 'react';
import {
  Cpu,
  Radio,
  Activity,
  AlertOctagon,
  Flame,
  Zap,
  KeyRound,
  ShieldCheck,
  RotateCcw,
  PlusCircle
} from 'lucide-react';
import StatCard from '../components/StatCard';
import TrafficChart from '../components/TrafficChart';
import DetectionChart from '../components/DetectionChart';
import AlertTable from '../components/AlertTable';
import EmptyState from '../components/EmptyState';
import { formatTimeAgo, shortenIPv6 } from '../utils/formatters';

export default function Dashboard({
  summary = {},
  traffic = {},
  recentAlerts = [],
  recentEvents = [],
  onSimulateRogueRA,
  onSimulateNDPAnomaly,
  onGenerateNormalTraffic,
  onResetDemo,
  onAcknowledgeAlert,
  acknowledgingId,
  onNavigate
}) {
  return (
    <div className="space-y-6">
      {/* Top Banner & Quick Trigger Strip */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-slate-900/60 border border-slate-800 rounded-xl p-4 shadow-sm">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">Security Operations Center</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time IPv6 local area network telemetry and autonomous threat detection.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={onGenerateNormalTraffic}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-300 border border-cyan-500/30 text-xs font-semibold transition cursor-pointer"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>Normal Traffic</span>
          </button>
          <button
            onClick={onSimulateRogueRA}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-950/40 hover:bg-red-900/50 text-red-300 border border-red-500/40 text-xs font-semibold transition cursor-pointer"
          >
            <Flame className="w-3.5 h-3.5 text-red-400" />
            <span>Simulate Rogue RA</span>
          </button>
          <button
            onClick={onSimulateNDPAnomaly}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-950/40 hover:bg-amber-900/50 text-amber-300 border border-amber-500/40 text-xs font-semibold transition cursor-pointer"
          >
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span>Simulate NDP Anomaly</span>
          </button>
        </div>
      </div>

      {/* Eight SOC Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          title="Simulated Devices"
          value={summary.total_devices ?? 5}
          subtext="Active IoT sensors"
          icon={Cpu}
          accent="cyan"
          badge="RFC 4941"
        />
        <StatCard
          title="Active Sessions"
          value={summary.active_sessions ?? 0}
          subtext="Authenticated bearer leases"
          icon={Radio}
          accent="blue"
        />
        <StatCard
          title="Events Ingested"
          value={summary.total_events ?? 0}
          subtext="Processed ICMPv6 frames"
          icon={Activity}
          accent="teal"
        />
        <StatCard
          title="Security Alerts"
          value={summary.total_alerts ?? 0}
          subtext="Unresolved threat signals"
          icon={AlertOctagon}
          accent="red"
        />
        <StatCard
          title="Rogue RA Detections"
          value={summary.rogue_ra_alerts ?? 0}
          subtext="Unauthorised gateway alerts"
          icon={Flame}
          accent="red"
        />
        <StatCard
          title="NDP Anomalies"
          value={summary.ndp_alerts ?? 0}
          subtext="High-rate flood bursts"
          icon={Zap}
          accent="amber"
        />
        <StatCard
          title="Active Pseudonyms"
          value={summary.active_pseudonyms ?? 0}
          subtext="Fresh ephemeral labels"
          icon={KeyRound}
          accent="teal"
        />
        <StatCard
          title="Expired Pseudonyms"
          value={summary.expired_pseudonyms ?? 0}
          subtext="Safely revoked tokens"
          icon={ShieldCheck}
          accent="purple"
        />
      </div>

      {/* Visual Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Traffic Chart Card */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-200">Network Traffic Volume</h3>
              <p className="text-xs text-slate-400">Normal vs Suspicious ICMPv6 Frames</p>
            </div>
            <button
              onClick={() => onNavigate('analytics')}
              className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 transition cursor-pointer"
            >
              Full Analytics &rarr;
            </button>
          </div>
          <TrafficChart data={traffic.time_series || []} />
        </div>

        {/* Threat Distribution Card */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-200">Threat Detection Vectors</h3>
              <p className="text-xs text-slate-400">Rogue RA vs NDP Flood vs Expired Token</p>
            </div>
            <button
              onClick={() => onNavigate('evaluation')}
              className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 transition cursor-pointer"
            >
              Run Benchmark &rarr;
            </button>
          </div>
          <DetectionChart
            rogueRACount={summary.rogue_ra_alerts ?? 0}
            ndpAnomalyCount={summary.ndp_alerts ?? 0}
            privacyExpirationCount={summary.expired_pseudonyms ?? 0}
          />
        </div>
      </div>

      {/* Recent Alerts & Live Event Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Alerts Table (2 cols) */}
        <div className="lg:col-span-2 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
              <AlertOctagon className="w-4 h-4 text-red-400" />
              <span>Recent Security Alerts</span>
            </h3>
            <button
              onClick={() => onNavigate('alerts')}
              className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 cursor-pointer"
            >
              View All Alerts &rarr;
            </button>
          </div>
          {recentAlerts.length > 0 ? (
            <AlertTable
              alerts={recentAlerts}
              onAcknowledge={onAcknowledgeAlert}
              acknowledgingId={acknowledgingId}
            />
          ) : (
            <EmptyState
              title="No Active Threat Alerts"
              description="All monitored IPv6 devices and router gateways are operating within normal security policy thresholds."
            />
          )}
        </div>

        {/* Live Events Stream (1 col) */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              <span>Telemetry Feed</span>
            </h3>
            <button
              onClick={() => onNavigate('monitoring')}
              className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 cursor-pointer"
            >
              Live Feed &rarr;
            </button>
          </div>
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 divide-y divide-slate-800/60 max-h-96 overflow-y-auto">
            {recentEvents.length > 0 ? (
              recentEvents.map((evt) => (
                <div key={evt.event_id} className="py-2.5 first:pt-0 last:pb-0 flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-teal-300">
                        {evt.pseudonym || 'ROUTER'}
                      </span>
                      <span
                        className={`text-[10px] font-semibold px-1.5 py-0.2 rounded ${
                          evt.is_suspicious
                            ? 'bg-red-500/20 text-red-300 border border-red-500/40'
                            : 'bg-slate-800 text-slate-300'
                        }`}
                      >
                        {evt.event_type}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 font-mono mt-0.5 truncate">
                      {shortenIPv6(evt.source_ipv6)}
                    </p>
                  </div>
                  <span className="text-[10px] text-slate-500 whitespace-nowrap">
                    {formatTimeAgo(evt.timestamp)}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500 text-center py-6 italic">
                Awaiting network events...
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
