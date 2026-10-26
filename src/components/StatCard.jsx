import React from 'react';

export default function StatCard({
  title,
  value,
  subtext,
  icon: Icon,
  accent = 'cyan', // 'cyan', 'teal', 'red', 'amber', 'blue', 'purple'
  badge
}) {
  const accentStyles = {
    cyan: {
      border: 'border-cyan-500/20 hover:border-cyan-500/40',
      iconBg: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
      shadow: 'hover:shadow-cyan-500/5'
    },
    teal: {
      border: 'border-teal-500/20 hover:border-teal-500/40',
      iconBg: 'bg-teal-500/10 text-teal-400 border-teal-500/20',
      shadow: 'hover:shadow-teal-500/5'
    },
    red: {
      border: 'border-red-500/20 hover:border-red-500/40',
      iconBg: 'bg-red-500/10 text-red-400 border-red-500/20',
      shadow: 'hover:shadow-red-500/5'
    },
    amber: {
      border: 'border-amber-500/20 hover:border-amber-500/40',
      iconBg: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      shadow: 'hover:shadow-amber-500/5'
    },
    blue: {
      border: 'border-blue-500/20 hover:border-blue-500/40',
      iconBg: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
      shadow: 'hover:shadow-blue-500/5'
    },
    purple: {
      border: 'border-purple-500/20 hover:border-purple-500/40',
      iconBg: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
      shadow: 'hover:shadow-purple-500/5'
    }
  };

  const style = accentStyles[accent] || accentStyles.cyan;

  return (
    <div
      className={`bg-slate-900/80 border rounded-xl p-4 transition-all duration-200 hover:shadow-lg ${style.border} ${style.shadow}`}
    >
      <div className="flex items-start justify-between mb-3">
        <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</p>
        <div className={`w-8 h-8 rounded-lg border flex items-center justify-center ${style.iconBg}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <div className="flex items-baseline justify-between">
        <div className="text-2xl font-bold tracking-tight text-white font-mono">{value}</div>
        {badge && (
          <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
            {badge}
          </span>
        )}
      </div>
      {subtext && <p className="text-xs text-slate-400 mt-1 font-sans">{subtext}</p>}
    </div>
  );
}
