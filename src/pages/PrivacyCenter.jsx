import React from 'react';
import { KeyRound, Shield, Lock, EyeOff, CheckCircle2 } from 'lucide-react';
import PrivacyPanel from '../components/PrivacyPanel';
import SessionStatus from '../components/SessionStatus';
import TenantIsolationPanel from '../components/TenantIsolationPanel';

export default function PrivacyCenter({
  pseudonyms = [],
  sessions = [],
  onExpirePseudonym,
  expiringPseudonym,
  onRevokeSession,
  revokingSessionId,
  tenantId,
  onSwitchTenant
}) {
  return (
    <div className="space-y-6">
      {/* Privacy Center Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-sm">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
            <KeyRound className="w-5 h-5 text-teal-400" />
            <span>Zero-Trust Privacy & Pseudonymization Center</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Eliminates permanent MAC addresses and static IPv6 EUI-64 tracking through short-lived pseudonyms and bearer sessions.
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs font-semibold px-3 py-1.5 rounded-lg bg-teal-500/15 text-teal-300 border border-teal-500/30">
          <EyeOff className="w-3.5 h-3.5" />
          <span>Zero Long-Term Hardware Tracking</span>
        </div>
      </div>

      {/* Tenant Boundary Panel */}
      <TenantIsolationPanel
        currentTenantId={tenantId}
        onSwitchTenant={onSwitchTenant}
      />

      {/* Ephemeral Pseudonym Registry */}
      <PrivacyPanel
        pseudonyms={pseudonyms}
        onExpirePseudonym={onExpirePseudonym}
        expiringPseudonym={expiringPseudonym}
      />

      {/* Short-Lived Authenticated Sessions */}
      <SessionStatus
        sessions={sessions}
        onRevokeSession={onRevokeSession}
        revokingSessionId={revokingSessionId}
      />
    </div>
  );
}
