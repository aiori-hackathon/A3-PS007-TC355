import React, { useState, useEffect } from 'react';
import { Shield, RefreshCw, Radio, CheckCircle2, AlertCircle, Building2, Download } from 'lucide-react';
import { TENANTS } from '../utils/constants';

export default function Header({
  activeTenant,
  onTenantChange,
  monitoringActive,
  onRefresh,
  isRefreshing,
  backendConnected,
  onExportZip
}) {
  const [timeStr, setTimeStr] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(
        now.toUTCString().replace('GMT', 'UTC')
      );
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-16 bg-slate-900/90 border-b border-slate-800 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-40">
      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 via-teal-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 text-white">
          <Shield className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-base font-bold text-white tracking-tight">PrivacyGuard IPv6</h1>
            <span className="text-[10px] font-semibold tracking-wider uppercase px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
              PS-007
            </span>
          </div>
          <p className="text-xs text-slate-400">Privacy-Aware IPv6 IoT Security SOC</p>
        </div>
      </div>

      {/* Middle Status Indicators */}
      <div className="hidden lg:flex items-center gap-6 text-xs text-slate-300">
        {/* Monitoring State */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/60 border border-slate-700/60">
          <span className="relative flex h-2 w-2">
            {monitoringActive && (
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            )}
            <span
              className={`relative inline-flex rounded-full h-2 w-2 ${
                monitoringActive ? 'bg-emerald-500' : 'bg-amber-500'
              }`}
            ></span>
          </span>
          <span className="font-medium text-slate-300">
            Engine: {monitoringActive ? 'Active Inspection' : 'Inspection Paused'}
          </span>
        </div>

        {/* Backend Connectivity */}
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/60 border border-slate-700/60">
          {backendConnected ? (
            <>
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-emerald-300 font-medium">Backend Linked (SQLite)</span>
            </>
          ) : (
            <>
              <AlertCircle className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
              <span className="text-amber-300 font-medium">Backend Reconnecting</span>
            </>
          )}
        </div>

        {/* Real-time Clock */}
        <div className="font-mono text-slate-400 text-xs">
          {timeStr}
        </div>
      </div>

      {/* Right Controls: Tenant Switcher & Action */}
      <div className="flex items-center gap-3">
        {/* Tenant Selector */}
        <div className="flex items-center gap-2 bg-slate-800/80 border border-slate-700 rounded-lg px-2.5 py-1.5">
          <Building2 className="w-4 h-4 text-cyan-400" />
          <select
            value={activeTenant}
            onChange={(e) => onTenantChange(e.target.value)}
            className="bg-transparent text-xs font-semibold text-slate-200 focus:outline-none cursor-pointer"
          >
            {TENANTS.map((t) => (
              <option key={t.id} value={t.id} className="bg-slate-900 text-slate-200">
                {t.name}
              </option>
            ))}
          </select>
        </div>

        {/* Download Project ZIP */}
        {onExportZip && (
          <button
            onClick={onExportZip}
            title="Download complete standalone project ZIP with Python backend, tests, and documentation"
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-teal-600/20 hover:bg-teal-600/30 text-teal-300 border border-teal-500/40 text-xs font-medium transition cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Export ZIP</span>
          </button>
        )}

        {/* Refresh Button */}
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition cursor-pointer disabled:opacity-50"
          title="Refresh Dashboard Data"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-cyan-400' : ''}`} />
        </button>
      </div>
    </header>
  );
}
