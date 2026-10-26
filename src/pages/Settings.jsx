import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Save, RefreshCw, CheckCircle2, AlertTriangle, Sliders } from 'lucide-react';

export default function Settings({
  settings = {},
  onSaveSettings,
  isSaving
}) {
  const [formData, setFormData] = useState({
    ndp_threshold: 50,
    ndp_window_seconds: 10,
    pseudonym_lifetime_seconds: 300,
    session_lifetime_seconds: 180,
    event_retention_days: 7,
    simulation_speed: '1x'
  });

  const [message, setMessage] = useState(null);

  useEffect(() => {
    if (settings && Object.keys(settings).length > 0) {
      setFormData({
        ndp_threshold: settings.ndp_threshold ?? 50,
        ndp_window_seconds: settings.ndp_window_seconds ?? 10,
        pseudonym_lifetime_seconds: settings.pseudonym_lifetime_seconds ?? 300,
        session_lifetime_seconds: settings.session_lifetime_seconds ?? 180,
        event_retention_days: settings.event_retention_days ?? 7,
        simulation_speed: settings.simulation_speed ?? '1x'
      });
    }
  }, [settings]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage(null);
    try {
      await onSaveSettings(formData);
      setMessage({ type: 'success', text: 'Operational parameters updated successfully in SQLite database.' });
    } catch (err) {
      setMessage({ type: 'error', text: err.message || 'Failed to update settings.' });
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-sm">
        <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
          <SettingsIcon className="w-5 h-5 text-cyan-400" />
          <span>System Parameters & Detection Policies</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Configure NDP rate-limiting windows, ephemeral pseudonym lifetimes, and persistent audit retention rules.
        </p>
      </div>

      {message && (
        <div
          className={`p-4 rounded-xl border flex items-center gap-3 text-xs ${
            message.type === 'success'
              ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300'
              : 'bg-red-950/40 border-red-500/40 text-red-300'
          }`}
        >
          {message.type === 'success' ? <CheckCircle2 className="w-4 h-4 shrink-0" /> : <AlertTriangle className="w-4 h-4 shrink-0" />}
          <span>{message.text}</span>
        </div>
      )}

      {/* Settings Form */}
      <form onSubmit={handleSubmit} className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 shadow-sm space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* NDP Threshold */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">
              NDP Anomaly Message Threshold (per window)
            </label>
            <input
              type="number"
              min="1"
              max="1000"
              value={formData.ndp_threshold}
              onChange={(e) => setFormData({ ...formData, ndp_threshold: parseInt(e.target.value) || 0 })}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
              required
            />
            <p className="text-[11px] text-slate-500">
              Number of ICMPv6 NS/NA messages before flagging DoS cache exhaustion (default: 50).
            </p>
          </div>

          {/* NDP Window Seconds */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">
              NDP Sliding Window Duration (Seconds)
            </label>
            <input
              type="number"
              min="1"
              max="3600"
              value={formData.ndp_window_seconds}
              onChange={(e) => setFormData({ ...formData, ndp_window_seconds: parseInt(e.target.value) || 0 })}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
              required
            />
            <p className="text-[11px] text-slate-500">
              Rolling window size for calculating message arrival rates (default: 10s).
            </p>
          </div>

          {/* Pseudonym Lifetime Seconds */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">
              Pseudonym Lifetime TTL (Seconds)
            </label>
            <input
              type="number"
              min="10"
              max="86400"
              value={formData.pseudonym_lifetime_seconds}
              onChange={(e) => setFormData({ ...formData, pseudonym_lifetime_seconds: parseInt(e.target.value) || 0 })}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
              required
            />
            <p className="text-[11px] text-slate-500">
              Validity duration of ephemeral device pseudonyms before forced rotation (default: 300s).
            </p>
          </div>

          {/* Session Lifetime Seconds */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">
              Bearer Session Lifetime (Seconds)
            </label>
            <input
              type="number"
              min="10"
              max="86400"
              value={formData.session_lifetime_seconds}
              onChange={(e) => setFormData({ ...formData, session_lifetime_seconds: parseInt(e.target.value) || 0 })}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
              required
            />
            <p className="text-[11px] text-slate-500">
              Expiration of cryptographic bearer session tokens (default: 180s).
            </p>
          </div>

          {/* Event Retention Days */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">
              Event Audit Retention (Days)
            </label>
            <input
              type="number"
              min="1"
              max="365"
              value={formData.event_retention_days}
              onChange={(e) => setFormData({ ...formData, event_retention_days: parseInt(e.target.value) || 0 })}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
              required
            />
            <p className="text-[11px] text-slate-500">
              Number of days telemetry logs are retained in SQLite database (default: 7 days).
            </p>
          </div>

          {/* Simulation Speed */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">
              Simulation Acceleration
            </label>
            <select
              value={formData.simulation_speed}
              onChange={(e) => setFormData({ ...formData, simulation_speed: e.target.value })}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
            >
              <option value="0.5x">0.5x (Slow)</option>
              <option value="1x">1.0x (Standard)</option>
              <option value="2x">2.0x (Fast)</option>
              <option value="5x">5.0x (Stress Test)</option>
            </select>
            <p className="text-[11px] text-slate-500">
              Relative multiplier for simulated background traffic generator.
            </p>
          </div>
        </div>

        <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
          <p className="text-[11px] text-slate-400 italic">
            * Thresholds are configurable demonstration baselines for testing, not immutable global standards.
          </p>
          <button
            type="submit"
            disabled={isSaving}
            className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold shadow-lg shadow-cyan-600/20 transition cursor-pointer disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            <span>{isSaving ? 'Updating...' : 'Save Parameters'}</span>
          </button>
        </div>
      </form>
    </div>
  );
}
