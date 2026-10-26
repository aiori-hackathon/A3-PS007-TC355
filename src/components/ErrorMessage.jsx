import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export default function ErrorMessage({ error, onRetry }) {
  const message = error?.message || (typeof error === 'string' ? error : 'An unexpected error occurred.');

  return (
    <div className="bg-red-950/40 border border-red-500/30 rounded-xl p-6 text-center my-6 max-w-xl mx-auto shadow-lg shadow-red-950/20">
      <div className="w-12 h-12 bg-red-500/20 border border-red-500/30 rounded-full flex items-center justify-center mx-auto mb-4 text-red-400">
        <AlertTriangle className="w-6 h-6" />
      </div>
      <h3 className="text-lg font-semibold text-red-200 mb-2">Backend Connection Alert</h3>
      <p className="text-sm text-slate-300 mb-5 leading-relaxed">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg text-sm font-medium transition cursor-pointer shadow"
        >
          <RefreshCw className="w-4 h-4" />
          Retry Request
        </button>
      )}
    </div>
  );
}
