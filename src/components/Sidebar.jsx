import React from 'react';
import {
  LayoutDashboard,
  Cpu,
  Radio,
  AlertOctagon,
  KeyRound,
  BarChart3,
  CheckCircle,
  Settings,
  Flame,
  Zap,
  RotateCcw
} from 'lucide-react';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'devices', label: 'Devices', icon: Cpu, badge: '5' },
  { id: 'monitoring', label: 'Live Monitoring', icon: Radio },
  { id: 'alerts', label: 'Security Alerts', icon: AlertOctagon },
  { id: 'privacy', label: 'Privacy Center', icon: KeyRound },
  { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  { id: 'evaluation', label: 'Evaluation', icon: CheckCircle },
  { id: 'settings', label: 'Settings', icon: Settings }
];

export default function Sidebar({
  activePage,
  onNavigate,
  alertCount = 0,
  onTriggerRogueRA,
  onTriggerNDPAnomaly,
  onResetDemo
}) {
  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between shrink-0 min-h-[calc(100vh-4rem)]">
      {/* Navigation Links */}
      <div className="py-4 px-3 space-y-1">
        <div className="px-3 pb-2 text-[11px] font-semibold tracking-wider text-slate-500 uppercase">
          SOC Navigation
        </div>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition cursor-pointer ${
                isActive
                  ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 shadow-sm shadow-cyan-500/10'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
                <span>{item.label}</span>
              </div>
              {item.id === 'alerts' && alertCount > 0 && (
                <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-red-500/20 text-red-300 border border-red-500/40">
                  {alertCount}
                </span>
              )}
              {item.badge && item.id !== 'alerts' && (
                <span className="px-1.5 py-0.5 text-[11px] font-medium rounded bg-slate-800 text-slate-400 border border-slate-700">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Quick Simulation Trigger Deck */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-950/40">
        <div className="px-2 pb-2 text-[11px] font-semibold tracking-wider text-slate-500 uppercase flex items-center justify-between">
          <span>Simulation Deck</span>
          <span className="text-[10px] text-teal-400 font-mono">HOT KEYS</span>
        </div>
        <div className="space-y-1.5">
          <button
            onClick={onTriggerRogueRA}
            className="w-full flex items-center gap-2 px-2.5 py-2 rounded-lg bg-red-950/40 hover:bg-red-900/50 text-red-300 border border-red-500/30 text-xs font-medium transition cursor-pointer"
          >
            <Flame className="w-3.5 h-3.5 text-red-400 shrink-0" />
            <span>Simulate Rogue RA</span>
          </button>

          <button
            onClick={onTriggerNDPAnomaly}
            className="w-full flex items-center gap-2 px-2.5 py-2 rounded-lg bg-amber-950/40 hover:bg-amber-900/50 text-amber-300 border border-amber-500/30 text-xs font-medium transition cursor-pointer"
          >
            <Zap className="w-3.5 h-3.5 text-amber-400 shrink-0" />
            <span>Simulate NDP Anomaly</span>
          </button>

          <button
            onClick={onResetDemo}
            className="w-full flex items-center gap-2 px-2.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-300 border border-slate-700 text-xs font-medium transition cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <span>Reset Demo State</span>
          </button>
        </div>
      </div>
    </aside>
  );
}
