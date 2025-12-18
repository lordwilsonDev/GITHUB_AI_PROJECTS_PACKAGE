import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Shield, Eye, AlertTriangle, Terminal, Play } from 'lucide-react';

const Dashboard = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [chaosMode, setChaosMode] = useState(false);
  const [metrics, setMetrics] = useState({ barrier: 1.0, vdr: 0.95 });
  const [agentPos, setAgentPos] = useState({ x: 200, y: 200 });
  const [logs, setLogs] = useState([]);
  
  // Physics State
  const [vectors, setVectors] = useState({ raw: {x:0,y:0}, safe: {x:0,y:0} });

  useEffect(() => {
    if (!isRunning) return;
    const interval = setInterval(async () => {
      try {
        // CALL THE PYTHON BACKEND
        const res = await axios.post('http://localhost:8000/simulate', null, {
          params: { chaos_mode: chaosMode },
          data: agentPos // Sending current position
        });

        const data = res.data;
        
        // Update Physics
        setVectors({ raw: data.raw_action, safe: data.safe_action });
        setAgentPos(prev => ({
            x: prev.x + data.safe_action.x,
            y: prev.y + data.safe_action.y
        }));
        
        // Update Metrics
        setMetrics({ barrier: data.barrier_value, vdr: data.vdr });
        
        // Update Logs
        const newLogs = data.logs.map(l => ({
            time: new Date().toLocaleTimeString().split(' ')[0],
            ...l
        }));
        setLogs(prev => [...prev.slice(-10), ...newLogs]); // Keep last 12
        
      } catch (err) {
        console.error("Backend Error", err);
        setIsRunning(false);
      }
    }, 100);
    return () => clearInterval(interval);
  }, [isRunning, chaosMode, agentPos]);

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200 font-mono">
      {/* VISUALIZATION PANEL */}
      <div className="w-2/3 p-6 border-r border-slate-800 flex flex-col items-center">
        <div className="mb-4 w-full flex justify-between items-center">
            <h1 className="text-xl font-bold text-indigo-400 flex gap-2"><Eye/> MoIE-OS PANOPTICON</h1>
            <div className="flex gap-2">
                <button onClick={() => setIsRunning(!isRunning)} className={`px-4 py-2 rounded flex gap-2 ${isRunning ? 'bg-red-900' : 'bg-emerald-700'}`}>
                    <Play size={16}/> {isRunning ? 'HALT' : 'RUN LOOP'}
                </button>
                <button onClick={() => setChaosMode(!chaosMode)} className={`px-4 py-2 rounded border ${chaosMode ? 'border-red-500 text-red-400' : 'border-slate-600'}`}>
                    <AlertTriangle size={16}/> {chaosMode ? 'CHAOS ACTIVE' : 'INJECT CHAOS'}
                </button>
            </div>
        </div>
        
        <svg width="400" height="400" className="border border-slate-800 bg-slate-900 rounded-xl shadow-2xl">
            {/* Safe Boundary */}
            <circle cx="200" cy="200" r="150" fill="none" stroke={metrics.barrier < 0.15 ? "red" : "#10b981"} strokeWidth="2" strokeDasharray="4 4"/>
            {/* Agent */}
            <circle cx={agentPos.x} cy={agentPos.y} r="8" fill="#60a5fa" />
            {/* Vectors */}
            <line x1={agentPos.x} y1={agentPos.y} x2={agentPos.x + vectors.raw.x * 20} y2={agentPos.y + vectors.raw.y * 20} stroke="red" strokeWidth="1" opacity="0.5" />
            <line x1={agentPos.x} y1={agentPos.y} x2={agentPos.x + vectors.safe.x * 20} y2={agentPos.y + vectors.safe.y * 20} stroke="#10b981" strokeWidth="2" />
        </svg>

        <div className="mt-6 w-full grid grid-cols-2 gap-4">
            <div className="bg-slate-900 p-4 rounded border border-slate-800">
                <div className="text-xs text-slate-500">BARRIER VALUE h(x)</div>
                <div className={`text-3xl ${metrics.barrier < 0.1 ? 'text-red-500' : 'text-slate-200'}`}>{metrics.barrier.toFixed(3)}</div>
            </div>
            <div className="bg-slate-900 p-4 rounded border border-slate-800">
                <div className="text-xs text-slate-500">VDR METRIC</div>
                <div className="text-3xl text-indigo-400">{metrics.vdr.toFixed(2)}</div>
            </div>
        </div>
      </div>

      {/* LOGS PANEL */}
      <div className="w-1/3 bg-slate-900 p-4 flex flex-col">
        <div className="text-xs text-slate-500 mb-2 flex gap-2"><Terminal size={14}/> SYSTEM TELEMETRY</div>
        <div className="flex-1 overflow-y-auto space-y-2 font-mono text-xs">
            {logs.map((l, i) => (
                <div key={i} className={`p-2 rounded ${l.msg.includes('VETO') ? 'bg-red-900/20 text-red-300' : 'bg-slate-800/50 text-slate-400'}`}>
                    <span className="text-slate-600">[{l.time}]</span> <span className="font-bold">{l.source}:</span> {l.msg}
                </div>
            ))}
        </div>
      </div>
    </div>
  );
};
export default Dashboard;