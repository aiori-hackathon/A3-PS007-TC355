import React, { useState } from 'react';
import { AlertOctagon, Filter, CheckCircle2, ShieldAlert } from 'lucide-react';
import AlertTable from '../components/AlertTable';
import EmptyState from '../components/EmptyState';

export default function SecurityAlerts({
  alerts = [],
  onAcknowledgeAlert,
  acknowledgingId,
  selectedSeverity,
  onSeverityChange,
  selectedCategory,
  onCategoryChange
}) {
  const categories = ['ALL', 'ROGUE_RA', 'NDP_ANOMALY', 'PRIVACY_EXPIRATION'];
  const severities = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];

  const filteredAlerts = alerts.filter((a) => {
    if (selectedSeverity && selectedSeverity !== 'ALL' && a.severity !== selectedSeverity) {
      return false;
    }
    if (selectedCategory && selectedCategory !== 'ALL' && a.category !== selectedCategory) {
      return false;
    }
    return true;
  });

  const unacknowledgedCount = alerts.filter((a) => !a.is_acknowledged).length;

  return (
    <div className="space-y-6">
      {/* Header and Filter Strip */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-sm">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
            <AlertOctagon className="w-5 h-5 text-red-400" />
            <span>Security Alerts & Incident Management</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Tamper-proof threat detection logs for Rogue Router Advertisements and abnormal NDP bursts.
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-1.5 bg-slate-800/80 border border-slate-700/80 rounded-lg px-2.5 py-1.5 text-xs">
            <span className="text-slate-400">Category:</span>
            <select
              value={selectedCategory}
              onChange={(e) => onCategoryChange(e.target.value)}
              className="bg-transparent text-slate-200 font-semibold focus:outline-none cursor-pointer"
            >
              {categories.map((c) => (
                <option key={c} value={c} className="bg-slate-900 text-slate-200">
                  {c}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-1.5 bg-slate-800/80 border border-slate-700/80 rounded-lg px-2.5 py-1.5 text-xs">
            <span className="text-slate-400">Severity:</span>
            <select
              value={selectedSeverity}
              onChange={(e) => onSeverityChange(e.target.value)}
              className="bg-transparent text-slate-200 font-semibold focus:outline-none cursor-pointer"
            >
              {severities.map((s) => (
                <option key={s} value={s} className="bg-slate-900 text-slate-200">
                  {s}
                </option>
              ))}
            </select>
          </div>

          <div className="px-3 py-1.5 rounded-lg bg-red-950/40 border border-red-500/30 text-xs font-semibold text-red-300">
            {unacknowledgedCount} Pending
          </div>
        </div>
      </div>

      {/* Main Alerts Table */}
      {filteredAlerts.length > 0 ? (
        <AlertTable
          alerts={filteredAlerts}
          onAcknowledge={onAcknowledgeAlert}
          acknowledgingId={acknowledgingId}
        />
      ) : (
        <EmptyState
          title="No Alerts Match Query"
          description="There are no security alerts matching the selected filter criteria for this tenant."
        />
      )}
    </div>
  );
}
