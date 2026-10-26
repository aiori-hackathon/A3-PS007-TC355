import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';

export default function DetectionChart({
  rogueRACount = 0,
  ndpAnomalyCount = 0,
  privacyExpirationCount = 0
}) {
  const chartData = [
    { name: 'Rogue RA', count: rogueRACount, color: '#ef4444' },
    { name: 'NDP Anomaly', count: ndpAnomalyCount, color: '#f97316' },
    { name: 'Expired Token Rejection', count: privacyExpirationCount, color: '#14b8a6' }
  ];

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
          <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
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
          <Bar dataKey="count" name="Detections" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
