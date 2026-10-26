import React from 'react';
import { AlertOctagon, CheckCircle2, ShieldAlert, Clock } from 'lucide-react';
import { SEVERITY_COLORS } from '../utils/constants';
import { formatDateTime } from '../utils/formatters';

export default function AlertTable({
  alerts = [],
  onAcknowledge,
  acknowledgingId
}) {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/60 shadow-md">
      <table className="w-full text-left text-xs border-collapse">
        <thead>
          <tr className="border-b border-slate-800 bg-slate-850/80 text-slate-400 font-semibold uppercase tracking-wider text-[11px]">
            <th className="py-3 px-4">Severity</th>
            <th className="py-3 px-4">Category</th>
            <th className="py-3 px-4">Detection Reason & Evidence</th>
            <th className="py-3 px-4">Subject Pseudonym</th>
            <th className="py-3 px-4">Timestamp (UTC)</th>
            <th className="py-3 px-4 text-right">Audit Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/60">
          {alerts.map((alt) => {
            const sevStyle = SEVERITY_COLORS[alt.severity] || SEVERITY_COLORS.MEDIUM;
            const isAck = Boolean(alt.is_acknowledged);
            const isProcessing = acknowledgingId === alt.alert_id;

            return (
              <tr key={alt.alert_id} className="hover:bg-slate-800/40 transition">
                {/* Severity Badge */}
                <td className="py-3.5 px-4">
                  <span
                    className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold border ${sevStyle.badge}`}
                  >
                    <span className={`w-1.5 h-1.5 rounded-full ${sevStyle.dot}`}></span>
                    {alt.severity}
                  </span>
                </td>

                {/* Threat Category */}
                <td className="py-3.5 px-4 font-mono font-semibold text-slate-200">
                  <div className="flex items-center gap-1.5">
                    <ShieldAlert className="w-3.5 h-3.5 text-cyan-400" />
                    <span>{alt.category}</span>
                  </div>
                </td>

                {/* Detection Reason */}
                <td className="py-3.5 px-4 max-w-md">
                  <p className="text-slate-300 font-medium leading-relaxed">
                    {alt.detection_reason}
                  </p>
                  <span className="text-[10px] font-mono text-slate-400 mt-0.5 block">
                    ID: {alt.alert_id}
                  </span>
                </td>

                {/* Ephemeral Pseudonym */}
                <td className="py-3.5 px-4 font-mono text-teal-300 font-semibold">
                  {alt.pseudonym || <span className="text-slate-400 font-sans italic">External Link</span>}
                </td>

                {/* Timestamp */}
                <td className="py-3.5 px-4 text-slate-400 font-mono whitespace-nowrap">
                  {formatDateTime(alt.timestamp)}
                </td>

                {/* Acknowledgement Status / Action */}
                <td className="py-3.5 px-4 text-right whitespace-nowrap">
                  {isAck ? (
                    <div className="inline-flex items-center gap-1 text-emerald-400 text-[11px] font-medium">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Acknowledged</span>
                    </div>
                  ) : (
                    <button
                      onClick={() => onAcknowledge(alt.alert_id)}
                      disabled={isProcessing}
                      className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-[11px] font-medium transition cursor-pointer disabled:opacity-40"
                    >
                      {isProcessing ? 'Auditing...' : 'Acknowledge'}
                    </button>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
