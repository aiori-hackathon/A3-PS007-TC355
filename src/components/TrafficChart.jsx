import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';

export default function TrafficChart({ data = [] }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-500 text-xs italic">
        Awaiting live IPv6 traffic telemetry...
      </div>
    );
  }

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="normalGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
            </linearGradient>
            <linearGradient id="suspiciousGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#ef4444" stopOpacity={0.0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
          <XAxis dataKey="time_slot" stroke="#64748b" fontSize={11} tickLine={false} />
          <YAxis stroke="#64748b" fontSize={11} tickLine={false} allowDecimals={false} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#0f172a',
              borderColor: '#334155',
              borderRadius: '0.5rem',
              color: '#f8fafc',
              fontSize: '12px'
            }}
          />
          <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
          <Area
            type="monotone"
            dataKey="normal_count"
            name="Normal Traffic"
            stroke="#06b6d4"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#normalGrad)"
          />
          <Area
            type="monotone"
            dataKey="suspicious_count"
            name="Suspicious Anomaly"
            stroke="#ef4444"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#suspiciousGrad)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
