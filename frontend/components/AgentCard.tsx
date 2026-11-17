'use client';

import React from 'react';

interface AgentCardProps {
  name: string;
  role: string;
  status: 'idle' | 'in_progress' | 'completed' | 'error';
  lastMessage: string;
  timestamp: string;
}

export const AgentCard: React.FC<AgentCardProps> = ({
  name,
  role,
  status,
  lastMessage,
  timestamp,
}) => {
  const getStatusBadge = () => {
    switch (status) {
      case 'in_progress':
        return <span className="w-2.5 h-2.5 rounded-full bg-sky-400 animate-ping" />;
      case 'completed':
        return <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />;
      case 'error':
        return <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />;
      default:
        return <span className="w-2.5 h-2.5 rounded-full bg-slate-600" />;
    }
  };

  const getCardBorder = () => {
    switch (status) {
      case 'in_progress':
        return 'border-sky-500/80 shadow-lg shadow-sky-500/10';
      case 'completed':
        return 'border-emerald-500/50';
      case 'error':
        return 'border-rose-500/80';
      default:
        return 'border-slate-800';
    }
  };

  return (
    <div className={`bg-slate-900 border rounded-xl p-3 flex flex-col justify-between transition-all duration-300 ${getCardBorder()}`}>
      <div>
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-xs font-bold text-slate-200">{name}</span>
          {getStatusBadge()}
        </div>
        <p className="text-[10px] text-slate-400 font-medium">{role}</p>
        <p className="text-[11px] text-slate-300 mt-2 line-clamp-2 leading-snug">
          {lastMessage || 'Standing by...'}
        </p>
      </div>
      <div className="mt-3 text-[10px] text-slate-500 font-mono">
        {timestamp || '--:--:--'}
      </div>
    </div>
  );
};
