import React, { useState } from 'react';
import { Cpu, RefreshCw, X, Radio, History, Shield } from 'lucide-react';
import DeviceTable from '../components/DeviceTable';
import EmptyState from '../components/EmptyState';
import { formatDateTime, shortenIPv6 } from '../utils/formatters';

export default function Devices({
  devices = [],
  onRotateAddress,
  onToggleConnection,
  onFetchDeviceEvents,
  rotatingId,
  tenantId
}) {
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [deviceEvents, setDeviceEvents] = useState([]);
  const [loadingEvents, setLoadingEvents] = useState(false);

  const handleOpenEvents = async (device) => {
    setSelectedDevice(device);
    setLoadingEvents(true);
    try {
      const res = await onFetchDeviceEvents(device.device_id);
      setDeviceEvents(res?.events || []);
    } catch (e) {
      setDeviceEvents([]);
    } finally {
      setLoadingEvents(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-sm">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
            <Cpu className="w-5 h-5 text-cyan-400" />
            <span>Simulated IPv6 IoT Fleet</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Five emulated IoT sensors employing SLAAC RFC 4941 ephemeral address rotation and pseudonyms.
          </p>
        </div>
        <div className="text-xs text-slate-400 bg-slate-800/80 border border-slate-700/80 px-3 py-1.5 rounded-lg">
          Active Fleet: <span className="text-cyan-300 font-semibold">{devices.length} Nodes</span>
        </div>
      </div>

      {/* Main Devices Table */}
      {devices.length > 0 ? (
        <DeviceTable
          devices={devices}
          onRotateAddress={onRotateAddress}
          onToggleConnection={onToggleConnection}
          onViewEvents={handleOpenEvents}
          rotatingId={rotatingId}
        />
      ) : (
        <EmptyState
          title="No Devices Initialised"
          description="Click Reset Demo or check backend database initialisation to load the 5 IoT nodes."
        />
      )}

      {/* Device History Modal */}
      {selectedDevice && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-2xl w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <History className="w-4 h-4 text-cyan-400" />
                  <span>Telemetry Audit: {selectedDevice.device_name}</span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5 font-mono">
                  Current Pseudonym: <span className="text-teal-300 font-semibold">{selectedDevice.current_pseudonym}</span>
                </p>
              </div>
              <button
                onClick={() => setSelectedDevice(null)}
                className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="max-h-80 overflow-y-auto divide-y divide-slate-800/60">
              {loadingEvents ? (
                <div className="py-8 text-center text-xs text-slate-400">Loading device event log...</div>
              ) : deviceEvents.length > 0 ? (
                deviceEvents.map((evt) => (
                  <div key={evt.event_id} className="py-2.5 flex items-center justify-between text-xs">
                    <div>
                      <span className="font-semibold text-slate-200">{evt.event_type}</span>
                      <p className="text-[11px] text-slate-400 font-mono mt-0.5">
                        IPv6: {evt.source_ipv6}
                      </p>
                    </div>
                    <span className="text-[11px] text-slate-500 font-mono">
                      {formatDateTime(evt.timestamp)}
                    </span>
                  </div>
                ))
              ) : (
                <div className="py-8 text-center text-xs text-slate-500 italic">
                  No previous events recorded for this device's current pseudonym.
                </div>
              )}
            </div>

            <div className="border-t border-slate-800 pt-3 flex justify-end">
              <button
                onClick={() => setSelectedDevice(null)}
                className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
