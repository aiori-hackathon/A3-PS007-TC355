import React from 'react';
import { BarChart3, Activity, ShieldAlert, PieChart, TrendingUp } from 'lucide-react';
import TrafficChart from '../components/TrafficChart';
import DetectionChart from '../components/DetectionChart';

export default function Analytics({
  traffic = {},
  alertStats = {},
  detection = {},
  tenantId
}) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-sm">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-cyan-400" />
            <span>Network Traffic & Threat Analytics</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Historical distribution, temporal traffic density, and anomaly classification metrics for {tenantId}.
          </p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <p className="text-xs text-slate-400 font-semibold uppercase">Normal Traffic</p>
          <div className="text-2xl font-bold font-mono text-cyan-400 mt-1">
            {traffic.normal_events ?? 0}
          </div>
          <p className="text-[11px] text-slate-500 mt-0.5">Authorised SLAAC/NDP frames</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <p className="text-xs text-slate-400 font-semibold uppercase">Flagged Anomalies</p>
          <div className="text-2xl font-bold font-mono text-red-400 mt-1">
            {traffic.suspicious_events ?? 0}
          </div>
          <p className="text-[11px] text-slate-500 mt-0.5">Threat violations detected</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <p className="text-xs text-slate-400 font-semibold uppercase">Rogue RA Injections</p>
          <div className="text-2xl font-bold font-mono text-orange-400 mt-1">
            {detection.rogue_ra_count ?? 0}
          </div>
          <p className="text-[11px] text-slate-500 mt-0.5">Unauthorised router frames</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <p className="text-xs text-slate-400 font-semibold uppercase">NDP Flood Bursts</p>
          <div className="text-2xl font-bold font-mono text-amber-400 mt-1">
            {detection.ndp_anomaly_count ?? 0}
          </div>
          <p className="text-[11px] text-slate-500 mt-0.5">Rate threshold breaches</p>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-sm">
          <h3 className="text-sm font-bold text-slate-200 mb-1">Temporal Traffic Trends</h3>
          <p className="text-xs text-slate-400 mb-4">Ingested frames grouped by time interval</p>
          <TrafficChart data={traffic.time_series || []} />
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-sm">
          <h3 className="text-sm font-bold text-slate-200 mb-1">Threat Type Breakdown</h3>
          <p className="text-xs text-slate-400 mb-4">Volume of Rogue RA vs NDP rate anomaly</p>
          <DetectionChart
            rogueRACount={detection.rogue_ra_count ?? 0}
            ndpAnomalyCount={detection.ndp_anomaly_count ?? 0}
            privacyExpirationCount={detection.privacy_expiration_count ?? 0}
          />
        </div>
      </div>
    </div>
  );
}
