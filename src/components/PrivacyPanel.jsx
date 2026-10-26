import React from 'react';
import { KeyRound, ShieldOff, Clock, CheckCircle2, XCircle } from 'lucide-react';
import { formatDateTime } from '../utils/formatters';

export default function PrivacyPanel({
  pseudonyms = [],
  onExpirePseudonym,
  expiringPseudonym
}) {
  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-md">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <KeyRound className="w-4 h-4 text-teal-400" />
            <span>Ephemeral Local Pseudonyms Registry</span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Cryptographically random identifiers rotating independently of physical MAC/EUI-64.
          </p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider text-[11px]">
              <th className="py-2.5 px-3">Pseudonym Label</th>
              <th className="py-2.5 px-3">State</th>
              <th className="py-2.5 px-3">Created At (UTC)</th>
              <th className="py-2.5 px-3">Expiration (TTL)</th>
              <th className="py-2.5 px-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {pseudonyms.map((p) => {
              const isExpired = p.is_expired || p.is_revoked;
              const isProcessing = expiringPseudonym === p.pseudonym;

              return (
                <tr key={p.pseudonym} className="hover:bg-slate-800/30">
                  <td className="py-2.5 px-3 font-mono font-bold text-teal-300">
                    {p.pseudonym}
                  </td>
                  <td className="py-2.5 px-3">
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold border ${
                        !isExpired
                          ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                          : 'bg-slate-800 text-slate-400 border-slate-700'
                      }`}
                    >
                      {!isExpired ? <CheckCircle2 className="w-2.5 h-2.5" /> : <XCircle className="w-2.5 h-2.5" />}
                      {isExpired ? 'EXPIRED' : 'ACTIVE'}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 font-mono text-slate-400 text-[11px]">
                    {formatDateTime(p.created_at)}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-slate-400 text-[11px]">
                    {formatDateTime(p.expires_at)}
                  </td>
                  <td className="py-2.5 px-3 text-right">
                    {!isExpired ? (
                      <button
                        onClick={() => onExpirePseudonym(p.pseudonym)}
                        disabled={isProcessing}
                        className="px-2 py-1 rounded bg-slate-800 hover:bg-red-950/40 text-slate-300 hover:text-red-300 border border-slate-700 hover:border-red-500/30 text-[11px] font-medium transition cursor-pointer"
                      >
                        {isProcessing ? 'Revoking...' : 'Expire / Revoke'}
                      </button>
                    ) : (
                      <span className="text-slate-600 text-[11px] italic">Revoked</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
