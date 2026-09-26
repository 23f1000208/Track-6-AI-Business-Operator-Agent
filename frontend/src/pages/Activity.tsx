import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { ActivityTable } from '../components/ActivityTable';
import { RefreshCw, Search } from 'lucide-react';

export const ActivityPage: React.FC = () => {
  const [logs, setLogs] = useState<any[]>([]);
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const data = await api.getActivity(100);
      setLogs(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const filteredLogs = logs.filter(l =>
    (l.event && l.event.toLowerCase().includes(filter.toLowerCase())) ||
    (l.run_id && l.run_id.toLowerCase().includes(filter.toLowerCase())) ||
    (typeof l.details === 'string' && l.details.toLowerCase().includes(filter.toLowerCase())) ||
    (typeof l.details === 'object' && JSON.stringify(l.details).toLowerCase().includes(filter.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-xl font-bold text-white tracking-wide">
            OPERATIONAL AUDIT TRAIL
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Complete tamper-evident record of all agent steps, tool executions, and security sanitizations.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              placeholder="Filter by event or run ID..."
              className="bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500 transition w-64"
            />
          </div>

          <button
            onClick={fetchLogs}
            disabled={loading}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      <ActivityTable logs={filteredLogs} />
    </div>
  );
};
