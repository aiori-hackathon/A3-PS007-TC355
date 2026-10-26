import React from 'react';
import { Building2, ShieldCheck, Lock, ArrowRight } from 'lucide-react';
import { TENANTS } from '../utils/constants';

export default function TenantIsolationPanel({
  currentTenantId,
  onSwitchTenant
}) {
  const currentTenant = TENANTS.find((t) => t.id === currentTenantId) || TENANTS[0];
  const otherTenant = TENANTS.find((t) => t.id !== currentTenantId) || TENANTS[1];

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-md">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <Building2 className="w-4 h-4 text-cyan-400" />
            <span>Multi-Tenant Cryptographic Partitioning</span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Strict isolation boundaries prevent cross-tenant correlation and telemetry leakage.
          </p>
        </div>
        <button
          onClick={() => onSwitchTenant(otherTenant.id)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-500/15 hover:bg-cyan-500/25 text-cyan-300 border border-cyan-500/30 text-xs font-semibold transition cursor-pointer"
        >
          <span>Switch to {otherTenant.name.split(' ')[0]} {otherTenant.name.split(' ')[1]}</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        {/* Active Tenant Box */}
        <div className="p-4 rounded-lg bg-slate-800/40 border border-slate-700/80">
          <div className="flex items-center justify-between mb-2">
            <span className="font-semibold text-slate-200">{currentTenant.name}</span>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              ACTIVE SCOPE
            </span>
          </div>
          <div className="space-y-1.5 text-slate-400 font-mono text-[11px]">
            <div>Assigned Prefix: <span className="text-slate-200">{currentTenant.prefix}</span></div>
            <div>Identifier Scope: <span className="text-teal-300">{currentTenant.id}</span></div>
            <div>Cross-Query Permitted: <span className="text-red-400">DENIED (HTTP 403)</span></div>
          </div>
        </div>

        {/* Foreign Tenant Box */}
        <div className="p-4 rounded-lg bg-slate-950/40 border border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <span className="font-semibold text-slate-400">{otherTenant.name}</span>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-500 border border-slate-700">
              ISOLATED
            </span>
          </div>
          <div className="space-y-1.5 text-slate-500 font-mono text-[11px]">
            <div>Assigned Prefix: {otherTenant.prefix}</div>
            <div>Identifier Scope: {otherTenant.id}</div>
            <div>Correlation Shield: <span className="text-emerald-400">ENFORCED</span></div>
          </div>
        </div>
      </div>
    </div>
  );
}
