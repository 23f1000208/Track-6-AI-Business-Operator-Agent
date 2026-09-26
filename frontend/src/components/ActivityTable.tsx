import React from 'react';
import { History, Shield } from 'lucide-react';

interface ActivityTableProps {
  logs: any[];
}

export const ActivityTable: React.FC<ActivityTableProps> = ({ logs }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <History className="w-5 h-5 text-sky-400" />
          <h3 className="text-base font-bold text-white tracking-wide uppercase">AUDIT TRAIL LOG</h3>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-slate-400 bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800 font-mono">
          <Shield className="w-3.5 h-3.5 text-emerald-400" />
          <span>Secret-Scrubbed Trail</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead className="bg-slate-950/60 text-slate-400 border-b border-slate-800 uppercase tracking-wider text-[10px]">
            <tr>
              <th className="py-2.5 px-3">Timestamp</th>
              <th className="py-2.5 px-3">Event</th>
              <th className="py-2.5 px-3">Run ID</th>
              <th className="py-2.5 px-3">Event Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {logs.map((log, idx) => (
              <tr key={idx} className="hover:bg-slate-800/30 transition">
                <td className="py-2.5 px-3 text-slate-400 whitespace-nowrap">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </td>
                <td className="py-2.5 px-3 font-bold text-sky-400 whitespace-nowrap">
                  {log.event}
                </td>
                <td className="py-2.5 px-3 text-slate-400 whitespace-nowrap">
                  {log.run_id || 'SYSTEM'}
                </td>
                <td className="py-2.5 px-3 text-slate-300 max-w-md truncate">
                  {typeof log.details === 'object' ? JSON.stringify(log.details) : String(log.details)}
                </td>
              </tr>
            ))}
            {logs.length === 0 && (
              <tr>
                <td colSpan={4} className="py-8 text-center text-slate-500 font-sans">
                  No activity events recorded yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
