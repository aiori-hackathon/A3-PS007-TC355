import React from 'react';
import {
  Radio,
  Play,
  Square,
  Flame,
  Zap,
  PlusCircle,
  RefreshCw,
  RotateCcw,
  Sliders,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import EmptyState from '../components/EmptyState';
import { formatDateTime, shortenIPv6 } from '../utils/formatters';

export default function Monitoring({
  monitoringActive,
  onStartMonitoring,
  onStopMonitoring,
  onSimulateRogueRA,
  onSimulateNDPAnomaly,
  onGenerateNormalTraffic,
  onRotateAddress,
  onResetDemo,
  events = [],
  status = {}
}) {
  return (
    <div className="space-y-6">
      {/* Control Dashboard Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-sm">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
            <Radio className="w-5 h-5 text-cyan-400" />
            <span>Live IPv6 Inspection & Simulation Controls</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time ICMPv6 packet ingestion engine, rate anomaly detectors, and attack inject simulation.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {monitoringActive ? (
            <button
              onClick={onStopMonitoring}
              className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-amber-500/15 hover:bg-amber-500/25 text-amber-300 border border-amber-500/30 text-xs font-semibold transition cursor-pointer"
            >
              <Square className="w-3.5 h-3.5 fill-amber-300" />
              <span>Pause Inspection</span>
            </button>
          ) : (
            <button
              onClick={onStartMonitoring}
              className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-300 border border-emerald-500/30 text-xs font-semibold transition cursor-pointer"
            >
              <Play className="w-3.5 h-3.5 fill-emerald-300" />
              <span>Resume Inspection</span>
            </button>
          )}
        </div>
      </div>

      {/* KPI & Config Strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <p className="text-xs text-slate-400 font-semibold uppercase">Inspection Status</p>
          <div className="flex items-center gap-2 mt-1">
            <span className={`w-2 h-2 rounded-full ${monitoringActive ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`}></span>
            <span className="text-base font-bold text-white">{monitoringActive ? 'ACTIVE' : 'PAUSED'}</span>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <p className="text-xs text-slate-400 font-semibold uppercase">Total Packets</p>
          <div className="text-xl font-bold font-mono text-cyan-400 mt-1">
            {status.total_events ?? 0}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <p className="text-xs text-slate-400 font-semibold uppercase">Normal Traffic</p>
          <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
            {status.normal_events ?? 0}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <p className="text-xs text-slate-400 font-semibold uppercase">NDP Detection Limit</p>
          <div className="text-sm font-bold font-mono text-amber-300 mt-1 flex items-center gap-1.5">
            <Sliders className="w-3.5 h-3.5" />
            <span>{status.ndp_threshold ?? 50} msgs / {status.ndp_window_seconds ?? 10}s</span>
          </div>
        </div>
      </div>

      {/* Simulation Command Deck */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
          Attack Injection & Traffic Control Deck
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <button
            onClick={onSimulateRogueRA}
            className="flex flex-col items-start p-3.5 rounded-lg bg-red-950/30 hover:bg-red-900/40 text-red-300 border border-red-500/30 text-left transition cursor-pointer"
          >
            <div className="flex items-center gap-2 mb-1">
              <Flame className="w-4 h-4 text-red-400" />
              <span className="font-bold text-xs">Simulate Rogue RA</span>
            </div>
            <p className="text-[11px] text-red-300/70">
              Inject unverified ICMPv6 Type 134 packet from rogue gateway.
            </p>
          </button>

          <button
            onClick={onSimulateNDPAnomaly}
            className="flex flex-col items-start p-3.5 rounded-lg bg-amber-950/30 hover:bg-amber-900/40 text-amber-300 border border-amber-500/30 text-left transition cursor-pointer"
          >
            <div className="flex items-center gap-2 mb-1">
              <Zap className="w-4 h-4 text-amber-400" />
              <span className="font-bold text-xs">Simulate NDP Anomaly</span>
            </div>
            <p className="text-[11px] text-amber-300/70">
              Generate 55-message Neighbor Solicitation flood burst.
            </p>
          </button>

          <button
            onClick={onGenerateNormalTraffic}
            className="flex flex-col items-start p-3.5 rounded-lg bg-cyan-950/30 hover:bg-cyan-900/40 text-cyan-300 border border-cyan-500/30 text-left transition cursor-pointer"
          >
            <div className="flex items-center gap-2 mb-1">
              <PlusCircle className="w-4 h-4 text-cyan-400" />
              <span className="font-bold text-xs">Generate Normal Traffic</span>
            </div>
            <p className="text-[11px] text-cyan-300/70">
              Transmit legitimate NDP packets & trusted default gateway RA.
            </p>
          </button>

          <button
            onClick={onResetDemo}
            className="flex flex-col items-start p-3.5 rounded-lg bg-slate-800/80 hover:bg-slate-750 text-slate-300 border border-slate-700 text-left transition cursor-pointer"
          >
            <div className="flex items-center gap-2 mb-1">
              <RotateCcw className="w-4 h-4 text-slate-400" />
              <span className="font-bold text-xs">Reset Demonstration</span>
            </div>
            <p className="text-[11px] text-slate-400">
              Clear all events & alerts and re-seed pristine 5-device state.
            </p>
          </button>
        </div>
      </div>

      {/* Network Event Stream Table */}
      <div className="space-y-3">
        <h3 className="text-sm font-bold text-slate-200">Live Ingested Event Stream</h3>
        {events.length > 0 ? (
          <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/60 shadow-md">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-850/80 text-slate-400 font-semibold uppercase tracking-wider text-[11px]">
                  <th className="py-3 px-4">Event Type</th>
                  <th className="py-3 px-4">Subject Pseudonym</th>
                  <th className="py-3 px-4">Source IPv6</th>
                  <th className="py-3 px-4">Security Classification</th>
                  <th className="py-3 px-4 text-right">Timestamp (UTC)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {events.map((evt) => (
                  <tr key={evt.event_id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-4 font-mono font-medium text-slate-200">
                      {evt.event_type}
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-teal-300">
                      {evt.pseudonym || <span className="text-slate-400 font-sans italic">Network Router</span>}
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-300">
                      {shortenIPv6(evt.source_ipv6)}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-semibold ${
                          evt.is_suspicious
                            ? 'bg-red-500/20 text-red-300 border border-red-500/40'
                            : 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30'
                        }`}
                      >
                        {evt.is_suspicious ? <AlertTriangle className="w-3 h-3" /> : <CheckCircle2 className="w-3 h-3" />}
                        {evt.is_suspicious ? 'ANOMALY DETECTED' : 'NORMAL TRAFFIC'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-slate-400 whitespace-nowrap">
                      {formatDateTime(evt.timestamp)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState
            title="Telemetry Stream Idle"
            description="Generate normal traffic or trigger an attack simulation to populate the live stream."
          />
        )}
      </div>
    </div>
  );
}
