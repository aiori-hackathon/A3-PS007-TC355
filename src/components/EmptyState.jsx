import React from 'react';
import { ShieldCheck } from 'lucide-react';

export default function EmptyState({
  title = 'No Records Found',
  description = 'No security events or alerts match the current filter or monitoring window.',
  icon: Icon = ShieldCheck,
  action
}) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center border border-dashed border-slate-700/60 rounded-xl bg-slate-900/40 my-4">
      <div className="w-12 h-12 rounded-full bg-slate-800/80 border border-slate-700 flex items-center justify-center text-cyan-400 mb-3 shadow-inner">
        <Icon className="w-6 h-6" />
      </div>
      <h4 className="text-base font-semibold text-slate-200 mb-1">{title}</h4>
      <p className="text-sm text-slate-400 max-w-sm mb-4 leading-relaxed">{description}</p>
      {action && <div>{action}</div>}
    </div>
  );
}
