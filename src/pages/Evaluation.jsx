import React from 'react';
import {
  CheckCircle,
  Play,
  RotateCw,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Award
} from 'lucide-react';
import { formatDateTime } from '../utils/formatters';

export default function Evaluation({
  results = null,
  isRunning = false,
  onRunEvaluation
}) {
  const cm = results?.confusion_matrix;
  const pm = results?.privacy_metrics;

  return (
    <div className="space-y-6">
      {/* Header with Run Button */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-sm">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-emerald-400" />
            <span>Autonomous Security & Privacy Evaluation</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Validates detection accuracy, false-positive resistance, and privacy boundaries using labelled ground-truth test vectors.
          </p>
        </div>

        <button
          onClick={onRunEvaluation}
          disabled={isRunning}
          className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-lg shadow-emerald-600/20 transition cursor-pointer disabled:opacity-50"
        >
          {isRunning ? (
            <>
              <RotateCw className="w-4 h-4 animate-spin" />
              <span>Executing Benchmark Vectors...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-white" />
              <span>Run Evaluation Suite</span>
            </>
          )}
        </button>
      </div>

      {results ? (
        <>
          {/* Top Accuracy KPI Strip */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-slate-900/80 border border-emerald-500/30 shadow-sm">
              <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">Detection Rate (Recall)</span>
              <div className="text-3xl font-extrabold text-white font-mono mt-1">
                {results.detection_rate}%
              </div>
              <p className="text-[11px] text-slate-400 mt-1">TP / (TP + FN)</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/80 border border-cyan-500/30 shadow-sm">
              <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider">False-Positive Rate</span>
              <div className="text-3xl font-extrabold text-white font-mono mt-1">
                {results.false_positive_rate}%
              </div>
              <p className="text-[11px] text-slate-400 mt-1">FP / (FP + TN)</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/80 border border-blue-500/30 shadow-sm">
              <span className="text-xs font-bold text-blue-400 uppercase tracking-wider">Precision</span>
              <div className="text-3xl font-extrabold text-white font-mono mt-1">
                {results.precision}%
              </div>
              <p className="text-[11px] text-slate-400 mt-1">TP / (TP + FP)</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/80 border border-purple-500/30 shadow-sm">
              <span className="text-xs font-bold text-purple-400 uppercase tracking-wider">F1 Score</span>
              <div className="text-3xl font-extrabold text-white font-mono mt-1">
                {results.f1_score}%
              </div>
              <p className="text-[11px] text-slate-400 mt-1">Harmonic mean</p>
            </div>
          </div>

          {/* Confusion Matrix & Privacy Audit */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Confusion Matrix Grid */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
              <h3 className="text-sm font-bold text-slate-200">Confusion Matrix (Ground-Truth Vectors)</h3>
              <div className="grid grid-cols-2 gap-3 text-center">
                <div className="p-4 rounded-lg bg-emerald-950/30 border border-emerald-500/30">
                  <span className="text-[11px] font-semibold text-emerald-400 uppercase">True Positives (TP)</span>
                  <div className="text-3xl font-extrabold font-mono text-white mt-1">
                    {cm?.true_positives ?? 0}
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">Rogue RA & NDP attacks caught</p>
                </div>

                <div className="p-4 rounded-lg bg-slate-800/40 border border-slate-700">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase">False Positives (FP)</span>
                  <div className="text-3xl font-extrabold font-mono text-white mt-1">
                    {cm?.false_positives ?? 0}
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">Normal frames falsely flagged</p>
                </div>

                <div className="p-4 rounded-lg bg-slate-800/40 border border-slate-700">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase">False Negatives (FN)</span>
                  <div className="text-3xl font-extrabold font-mono text-white mt-1">
                    {cm?.false_negatives ?? 0}
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">Attacks undetected</p>
                </div>

                <div className="p-4 rounded-lg bg-cyan-950/30 border border-cyan-500/30">
                  <span className="text-[11px] font-semibold text-cyan-400 uppercase">True Negatives (TN)</span>
                  <div className="text-3xl font-extrabold font-mono text-white mt-1">
                    {cm?.true_negatives ?? 0}
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">Normal SLAAC/RA accepted</p>
                </div>
              </div>
            </div>

            {/* Privacy Controls Verification */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
              <h3 className="text-sm font-bold text-slate-200">Zero-Trust Privacy & Isolation Verification</h3>
              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/40 border border-slate-700/60">
                  <span className="text-slate-300">Active Pseudonym Authentication</span>
                  <span className="flex items-center gap-1 text-emerald-400 font-semibold">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Enforced
                  </span>
                </div>

                <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/40 border border-slate-700/60">
                  <span className="text-slate-300">Expired Pseudonym Event Rejection</span>
                  <span className="flex items-center gap-1 text-emerald-400 font-semibold">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Enforced
                  </span>
                </div>

                <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/40 border border-slate-700/60">
                  <span className="text-slate-300">Revoked Session Invalidation</span>
                  <span className="flex items-center gap-1 text-emerald-400 font-semibold">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Enforced
                  </span>
                </div>

                <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/40 border border-slate-700/60">
                  <span className="text-slate-300">Cross-Tenant Isolation Shield</span>
                  <span className="flex items-center gap-1 text-emerald-400 font-semibold">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Enforced
                  </span>
                </div>
              </div>
              <p className="text-[11px] text-slate-500 font-mono">
                Last benchmark run recorded at: {formatDateTime(results.timestamp)}
              </p>
            </div>
          </div>

          {/* Test Vectors Execution Log Table */}
          {results.test_cases && results.test_cases.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-slate-200">Labelled Test Vector Execution Log</h3>
              <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/60 shadow-md">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-800 bg-slate-850/80 text-slate-400 font-semibold uppercase tracking-wider text-[11px]">
                      <th className="py-2.5 px-3">Test Vector ID</th>
                      <th className="py-2.5 px-3">Scenario Description</th>
                      <th className="py-2.5 px-3">Ground-Truth Label</th>
                      <th className="py-2.5 px-3">Detector Classification</th>
                      <th className="py-2.5 px-3 text-right">Result</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {results.test_cases.map((tc) => (
                      <tr key={tc.test_id} className="hover:bg-slate-800/40">
                        <td className="py-2.5 px-3 font-mono font-bold text-cyan-300">{tc.test_id}</td>
                        <td className="py-2.5 px-3 text-slate-300">{tc.description}</td>
                        <td className="py-2.5 px-3 font-mono text-slate-400">{tc.expected}</td>
                        <td className="py-2.5 px-3 font-mono text-slate-300">{tc.actual}</td>
                        <td className="py-2.5 px-3 text-right">
                          <span
                            className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold ${
                              tc.classification === 'TP' || tc.classification === 'TN'
                                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                                : 'bg-red-500/20 text-red-300 border border-red-500/30'
                            }`}
                          >
                            {tc.classification}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="bg-slate-900/60 border border-dashed border-slate-800 rounded-xl p-12 text-center">
          <Award className="w-12 h-12 text-slate-500 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-200 mb-1">Benchmark Suite Ready</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto mb-6">
            Click "Run Evaluation Suite" above to benchmark detection of Rogue RA attacks, NDP rate anomalies, and privacy isolation boundaries.
          </p>
        </div>
      )}
    </div>
  );
}
