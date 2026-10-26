import React from 'react';
import { Loader2 } from 'lucide-react';

export default function LoadingSpinner({ message = 'Loading security telemetry...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <Loader2 className="w-9 h-9 text-cyan-400 animate-spin mb-3" />
      <p className="text-slate-400 text-sm font-medium tracking-wide">{message}</p>
    </div>
  );
}
