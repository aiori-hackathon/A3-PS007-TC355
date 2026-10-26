import React from 'react';
import { Cpu, RefreshCw, Power, Radio, History, Shield, Wifi, WifiOff } from 'lucide-react';
import { formatTimeAgo, shortenIPv6 } from '../utils/formatters';

export default function DeviceTable({
  devices = [],
  onRotateAddress,
  onToggleConnection,
  onViewEvents,
  rotatingId
}) {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/60 shadow-md">
      <table className="w-full text-left text-xs border-collapse">
        <thead>
          <tr className="border-b border-slate-800 bg-slate-850/80 text-slate-400 font-semibold uppercase tracking-wider text-[11px]">
            <th className="py-3 px-4">Local Pseudonym</th>
            <th className="py-3 px-4">Device Profile</th>
            <th className="py-3 px-4">Temporary IPv6 Address (RFC 4941)</th>
            <th className="py-3 px-4">Status</th>
            <th className="py-3 px-4">Last Telemetry</th>
            <th className="py-3 px-4 text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/60">
          {devices.map((dev) => {
            const isConnected = dev.status === 'CONNECTED';
            const isRotating = rotatingId === dev.device_id;

            return (
              <tr key={dev.device_id} className="hover:bg-slate-800/40 transition">
                {/* Ephemeral Pseudonym (Primary Identity) */}
                <td className="py-3.5 px-4 font-mono font-bold text-teal-300">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-teal-400 shadow-sm shadow-teal-400/50"></span>
                    <span>{dev.current_pseudonym}</span>
                  </div>
                </td>

                {/* Device Name and Type */}
                <td className="py-3.5 px-4">
                  <div className="font-medium text-slate-200">{dev.device_name}</div>
                  <div className="text-[11px] text-slate-400 font-mono">{dev.device_type}</div>
                </td>

                {/* Temporary SLAAC IPv6 Address */}
                <td className="py-3.5 px-4 font-mono text-slate-300">
                  <span className="px-2 py-1 rounded bg-slate-800/80 border border-slate-700/80 text-[11px]" title={dev.current_ipv6}>
                    {shortenIPv6(dev.current_ipv6)}
                  </span>
                </td>

                {/* Status Badge */}
                <td className="py-3.5 px-4">
                  <span
                    className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold border ${
                      isConnected
                        ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                        : 'bg-slate-700/30 text-slate-400 border-slate-600/40'
                    }`}
                  >
                    {isConnected ? <Wifi className="w-3 h-3 text-emerald-400" /> : <WifiOff className="w-3 h-3 text-slate-400" />}
                    {dev.status}
                  </span>
                </td>

                {/* Last Telemetry */}
                <td className="py-3.5 px-4 text-slate-400">
                  {formatTimeAgo(dev.last_event_at)}
                </td>

                {/* Actions */}
                <td className="py-3.5 px-4 text-right">
                  <div className="flex items-center justify-end gap-1.5">
                    {/* Rotate Address Button */}
                    <button
                      onClick={() => onRotateAddress(dev.device_id)}
                      disabled={isRotating || !isConnected}
                      title="Rotate temporary RFC 4941 IPv6 address and generate new pseudonym"
                      className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-teal-500/15 hover:bg-teal-500/25 text-teal-300 border border-teal-500/30 font-medium transition cursor-pointer disabled:opacity-40"
                    >
                      <RefreshCw className={`w-3 h-3 ${isRotating ? 'animate-spin' : ''}`} />
                      <span>Rotate IP</span>
                    </button>

                    {/* Connect / Disconnect Button */}
                    <button
                      onClick={() => onToggleConnection(dev.device_id, isConnected)}
                      title={isConnected ? 'Disconnect simulated device' : 'Connect simulated device'}
                      className={`p-1.5 rounded-lg border transition cursor-pointer ${
                        isConnected
                          ? 'bg-slate-800 hover:bg-red-950/40 text-slate-300 hover:text-red-300 border-slate-700 hover:border-red-500/30'
                          : 'bg-emerald-950/40 hover:bg-emerald-900/50 text-emerald-300 border-emerald-500/40'
                      }`}
                    >
                      <Power className="w-3.5 h-3.5" />
                    </button>

                    {/* View Events Button */}
                    {onViewEvents && (
                      <button
                        onClick={() => onViewEvents(dev)}
                        title="View device event timeline"
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition cursor-pointer"
                      >
                        <History className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
