import React from 'react';

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = '' }) => {
  const norm = status ? status.toUpperCase() : 'UNKNOWN';

  let bg = 'bg-slate-800 text-slate-300 border-slate-700';

  if (norm === 'CONNECTED' || norm === 'COMPLETED' || norm === 'SUCCESS' || norm === 'VERIFIED' || norm === 'APPROVED' || norm === 'ALL_ACTIONS_VERIFIED_SUCCESSFUL') {
    bg = 'bg-emerald-950/70 text-emerald-400 border-emerald-800/60';
  } else if (norm === 'DEMO MODE' || norm === 'DEMO') {
    bg = 'bg-indigo-950/70 text-indigo-300 border-indigo-800/60';
  } else if (norm === 'RUNNING' || norm === 'STARTED' || norm === 'IN_PROGRESS') {
    bg = 'bg-sky-950/70 text-sky-400 border-sky-800/60 animate-pulse';
  } else if (norm === 'PENDING' || norm === 'PENDING_APPROVAL' || norm === 'PAUSED_APPROVAL') {
    bg = 'bg-amber-950/70 text-amber-400 border-amber-800/60';
  } else if (norm === 'FAILED' || norm === 'CRITICAL' || norm === 'ERROR' || norm === 'REJECTED') {
    bg = 'bg-rose-950/70 text-rose-400 border-rose-800/60';
  } else if (norm === 'HIGH') {
    bg = 'bg-orange-950/70 text-orange-400 border-orange-800/60';
  } else if (norm === 'MEDIUM') {
    bg = 'bg-yellow-950/70 text-yellow-400 border-yellow-800/60';
  } else if (norm === 'PARTIAL_SUCCESS' || norm === 'PARTIAL_FAILURE') {
    bg = 'bg-amber-950/70 text-amber-300 border-amber-800/60';
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${bg} ${className}`}>
      {status}
    </span>
  );
};
