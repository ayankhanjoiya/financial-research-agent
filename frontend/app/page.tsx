'use client';

import React, { useState } from 'react';
import { AgentCard } from '../components/AgentCard';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface AgentState {
  status: 'idle' | 'in_progress' | 'completed' | 'error';
  message: string;
  time: string;
}

export default function Home() {
  const [ticker, setTicker] = useState('NVDA');
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'report' | 'financials' | 'news' | 'risk'>('report');
  const [report, setReport] = useState<string>('');
  const [financialData, setFinancialData] = useState<any>(null);
  const [newsData, setNewsData] = useState<any>(null);
  const [riskData, setRiskData] = useState<any>(null);

  const [agents, setAgents] = useState<Record<string, AgentState>>({
    manager: { status: 'idle', message: 'Awaiting ticker input...', time: '' },
    financial: { status: 'idle', message: 'Financial statements & ratios', time: '' },
    news: { status: 'idle', message: 'Catalysts & sentiment', time: '' },
    sec: { status: 'idle', message: '10-K SEC Filings', time: '' },
    competitor: { status: 'idle', message: 'Peer benchmarking', time: '' },
    risk: { status: 'idle', message: 'Threat matrix & leverage', time: '' },
  });

  const runResearch = (targetTicker?: string) => {
    const symbol = (targetTicker || ticker).trim().toUpperCase();
    if (!symbol) return;

    setIsLoading(true);
    setReport('');

    // Reset agents
    setAgents({
      manager: { status: 'in_progress', message: 'Dispatching tasks...', time: new Date().toLocaleTimeString() },
      financial: { status: 'in_progress', message: 'Fetching financial data...', time: new Date().toLocaleTimeString() },
      news: { status: 'in_progress', message: 'Scouring recent news...', time: new Date().toLocaleTimeString() },
      sec: { status: 'in_progress', message: 'Querying SEC EDGAR...', time: new Date().toLocaleTimeString() },
      competitor: { status: 'in_progress', message: 'Analyzing peer group...', time: new Date().toLocaleTimeString() },
      risk: { status: 'in_progress', message: 'Evaluating risk disclosures...', time: new Date().toLocaleTimeString() },
    });

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
    const es = new EventSource(`${apiUrl}/api/research/stream/${symbol}`);

    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.event === 'node_update') {
          const node = data.node.replace('_agent', '');
          setAgents((prev) => ({
            ...prev,
            [node]: {
              status: 'completed',
              message: data.message,
              time: new Date().toLocaleTimeString(),
            },
          }));
        } else if (data.event === 'complete') {
          setReport(data.final_report || '');
          setFinancialData(data.financial_data);
          setNewsData(data.news_data);
          setRiskData(data.risk_data);
          setIsLoading(false);
          es.close();
        }
      } catch (e) {
        console.error('SSE Error:', e);
      }
    };

    es.onerror = () => {
      setIsLoading(false);
      es.close();
    };
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-6">
      {/* Search Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="w-full md:w-96">
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
            Company Ticker
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              placeholder="e.g. NVDA, AAPL"
              className="bg-slate-950 border border-slate-700 rounded-xl px-4 py-2 text-sm font-mono text-white w-full uppercase"
            />
            <button
              onClick={() => runResearch()}
              disabled={isLoading}
              className="bg-sky-600 hover:bg-sky-500 disabled:bg-slate-800 text-white text-xs font-semibold px-4 py-2 rounded-xl transition"
            >
              {isLoading ? 'Running...' : 'Research'}
            </button>
          </div>
        </div>

        {/* Quick Presets */}
        <div className="flex items-center gap-2">
          {['NVDA', 'AAPL', 'MSFT', 'TSLA', 'AMZN'].map((sym) => (
            <button
              key={sym}
              onClick={() => {
                setTicker(sym);
                runResearch(sym);
              }}
              className="px-3 py-1.5 text-xs font-mono bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-sky-400"
            >
              {sym}
            </button>
          ))}
        </div>
      </div>

      {/* Swarm Agents Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <AgentCard name="Manager" role="Supervisor" {...agents.manager} />
        <AgentCard name="Financial Data" role="Statements & Ratios" {...agents.financial} />
        <AgentCard name="News & Sentiment" role="Catalysts" {...agents.news} />
        <AgentCard name="Annual Report" role="SEC 10-K" {...agents.sec} />
        <AgentCard name="Competitor" role="Peer Group" {...agents.competitor} />
        <AgentCard name="Risk Analysis" role="Threat Matrix" {...agents.risk} />
      </div>

      {/* Report Container */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 min-h-[500px]">
        {report ? (
          <div className="prose prose-invert max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{report}</ReactMarkdown>
          </div>
        ) : (
          <div className="text-center py-20 text-slate-500">
            {isLoading ? 'Autonomous swarm synthesizing report...' : 'Enter a ticker to generate report.'}
          </div>
        )}
      </div>
    </div>
  );
}
