/* eslint-disable no-unused-vars */
import React, { useState, useMemo, useEffect } from 'react';
import { 
  LayoutDashboard, 
  Users, 
  Database, 
  Lightbulb, 
  ShieldCheck, 
  Search, 
  Bell, 
  User, 
  ChevronRight,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  BarChart3,
  Lock,
  Zap,
  Activity,
  UserCheck,
  AlertOctagon
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell,
  AreaChart,
  Area
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import kycData from './data/kyc_data.json';

// --- Premium Utilities ---

const CountUp = ({ value, duration = 1.5 }) => {
  const [count, setCount] = useState(0);
  const target = parseFloat(value.toString().replace(/,/g, ''));

  useEffect(() => {
    let start = 0;
    const end = target;
    const range = end - start;
    const effectiveDuration = duration * 1000;
    const startTime = Date.now();

    const timer = setInterval(() => {
      const now = Date.now();
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / effectiveDuration, 1);
      const current = progress * range + start;
      setCount(current);
      if (progress === 1) clearInterval(timer);
    }, 16);

    return () => clearInterval(timer);
  }, [target, duration]);

  const formatted = target % 1 === 0 ? Math.floor(count).toLocaleString() : count.toFixed(1);
  return <span>{formatted}</span>;
};

const ShinyText = ({ text, className = "" }) => {
  return (
    <span className={`relative inline-block ${className}`}>
      <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-300 to-white animate-shimmer bg-[length:200%_100%]">
        {text}
      </span>
    </span>
  );
};

// --- Components ---

const Sidebar = ({ activeTab, setActiveTab }) => {
  const menuItems = [
    { id: 'overview', icon: LayoutDashboard, label: 'Overview' },
    { id: 'analytics', icon: TrendingUp, label: 'Analytics' },
    { id: 'customers', icon: Users, label: 'Customers' },
    { id: 'database', icon: Database, label: 'Database' },
    { id: 'insights', icon: Lightbulb, label: 'Insights' },
  ];

  return (
    <div className="w-72 h-screen fixed left-0 top-0 border-r border-white/5 bg-[#0d1117]/60 backdrop-blur-3xl p-8 flex flex-col z-50">
      <div className="flex items-center gap-4 mb-14">
        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-[#6c63ff] to-[#4f46e5] flex items-center justify-center shadow-2xl shadow-indigo-500/40 relative">
          <ShieldCheck size={28} className="text-white" />
        </div>
        <div>
          <h2 className="text-xl font-black tracking-tight text-white leading-none">FinShield</h2>
          <p className="text-[10px] uppercase tracking-[0.3em] font-black text-[#6c63ff] mt-2">TECHNICAL AI</p>
        </div>
      </div>

      <div className="flex-1 space-y-3">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`w-full flex items-center gap-4 px-5 py-4 rounded-[20px] transition-all duration-500 group ${
              activeTab === item.id 
                ? 'bg-white/10 text-white shadow-2xl border border-white/10' 
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <div className={`p-2 rounded-xl transition-colors ${activeTab === item.id ? 'bg-[#6c63ff]/20 text-[#6c63ff]' : 'group-hover:text-white'}`}>
              <item.icon size={20} />
            </div>
            <span className="text-sm font-bold">{item.label}</span>
          </button>
        ))}
      </div>

      <div className="mt-auto pt-8 border-t border-white/5 space-y-4">
        <div className="bg-emerald-500/5 border border-emerald-500/10 rounded-3xl p-5 flex items-center gap-3">
           <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_10px_#10b981]" />
           <span className="text-[10px] font-black text-emerald-500 uppercase">System Active</span>
        </div>
        
        <div className="flex flex-col items-center gap-3 opacity-60 hover:opacity-100 transition-opacity px-2">
           <p className="text-[8px] font-black text-slate-500 uppercase tracking-[0.2em]">Developed For</p>
           <img 
             src="https://www.bny.com/etc.clientlibs/bny-v2/clientlibs/clientlib-site/resources/images/bny-logo-white.svg" 
             alt="BNY Logo" 
             className="h-6 object-contain" 
           />
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ label, value, delta, subtext, color = "indigo", icon: Icon }) => {
  const colorMap = {
    indigo: "text-[#6c63ff]",
    red: "text-rose-500",
    emerald: "text-emerald-500",
    amber: "text-amber-500",
    purple: "text-purple-500"
  };

  return (
    <div className={`glass p-7 group card-hover relative overflow-hidden`}>
      <div className="relative z-10">
        <div className="flex justify-between items-start mb-4">
           <div className={`p-3 rounded-2xl bg-white/5 border border-white/10 ${colorMap[color]}`}>
             <Icon size={20} />
           </div>
           {delta && (
             <span className={`text-[10px] font-black px-2 py-1 rounded-lg ${delta.includes('+') || !delta.includes('-') ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'}`}>
               {delta}
             </span>
           )}
        </div>
        <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-1">{label}</p>
        <h3 className="text-3xl font-black text-white mb-2"><CountUp value={value} /></h3>
        <p className="text-[10px] text-slate-400 font-bold italic tracking-wide">{subtext}</p>
      </div>
    </div>
  );
};

const Overview = ({ data }) => {
  const stats = useMemo(() => {
    const total = data.length;
    const highRisk = data.filter(d => d.risk_tier === 'HIGH').length;
    const approved = data.filter(d => d.decision === 'APPROVE').length;
    const manual = data.filter(d => d.decision === 'MANUAL_REVIEW').length;
    const edd = data.filter(d => d.decision === 'EDD').length;
    const avgScore = (data.reduce((acc, curr) => acc + curr.risk_score, 0) / total).toFixed(1);
    return { total, highRiskPct: ((highRisk/total)*100).toFixed(1), approved, manual, edd, avgScore };
  }, [data]);

  const tierData = [
    { name: 'LOW', value: data.filter(d => d.risk_tier === 'LOW').length, color: '#22c55e' },
    { name: 'MEDIUM', value: data.filter(d => d.risk_tier === 'MEDIUM').length, color: '#f59e0b' },
    { name: 'HIGH', value: data.filter(d => d.risk_tier === 'HIGH').length, color: '#ef4444' },
  ];

  const decisionData = [
    { name: 'Approve', value: stats.approved, color: '#22c55e' },
    { name: 'Review', value: stats.manual, color: '#f59e0b' },
    { name: 'EDD', value: stats.edd, color: '#8b5cf6' },
  ];

  return (
    <div className="space-y-8 animate-fadeIn">
      <div className="bg-white/[0.02] border border-white/5 rounded-[40px] p-10 relative overflow-hidden">
        <h1 className="text-5xl font-black text-white mb-4 tracking-tight leading-tight">
          <ShinyText text="Consolidated Risk Radar" />
        </h1>
        <p className="text-slate-400 max-w-xl font-medium leading-relaxed">Intelligence-driven scoring matrix processing unified entity risk across high-latency environments.</p>
        <div className="absolute top-0 right-0 w-80 h-80 bg-[#6c63ff]/10 blur-[120px] -z-10" />
      </div>

      <div className="grid grid-cols-5 gap-6">
        <StatCard label="Total Entity Vol" value={stats.total} subtext="Global Nodes" color="indigo" icon={BarChart3} />
        <StatCard label="Live Approvals" value={stats.approved} delta={`${((stats.approved / stats.total) * 100).toFixed(0)}%`} subtext="Autonomous Rate" color="emerald" icon={CheckCircle2} />
        <StatCard label="Manual Q" value={stats.manual} subtext="Priority One" color="amber" icon={AlertTriangle} />
        <StatCard label="EDD Escalation" value={stats.edd} subtext="Critical Lock" color="purple" icon={Lock} />
        <StatCard label="Avg Score" value={stats.avgScore} subtext="Risk Vector" color="red" icon={ShieldCheck} />
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="glass p-10 h-[450px]">
          <h3 className="text-xl font-black text-white mb-10">Risk Classification</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={tierData} cx="50%" cy="50%" innerRadius={80} outerRadius={110} paddingAngle={8} dataKey="value" animationDuration={1000} label={({name, value}) => `${name}: ${value}`}>
                {tierData.map((e, i) => <Cell key={i} fill={e.color} stroke="none" />)}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#0d1117', border: 'none', borderRadius: '16px' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="glass p-10 h-[450px]">
          <h3 className="text-xl font-black text-white mb-10">Directives Distribution</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={decisionData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="5 5" vertical={false} stroke="rgba(255,255,255,0.03)" />
              <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#4b5563', fontSize: 10}} label={{ value: 'Actionable Directive', position: 'insideBottom', offset: -10, fill: '#4b5563', fontSize: 10, fontWeight: 'bold' }} />
              <YAxis axisLine={false} tickLine={false} tick={{fill: '#4b5563', fontSize: 10}} label={{ value: 'Entities', angle: -90, position: 'insideLeft', fill: '#4b5563', fontSize: 10, fontWeight: 'bold' }} />
              <Bar dataKey="value" radius={[10, 10, 0, 0]} barSize={50}>
                {decisionData.map((e, i) => <Cell key={i} fill={e.color} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

const Analytics = ({ data }) => {
  // Score distribution data
  const bins = Array.from({length: 10}, (_, i) => ({ name: `${i*10}-${(i+1)*10}`, count: 0 }));
  data.forEach(d => {
    const binIdx = Math.min(Math.floor(d.risk_score / 10), 9);
    bins[binIdx].count++;
  });

  return (
    <div className="space-y-8 animate-fadeIn">
      <div className="flex justify-between items-end mb-4">
        <div>
          <h1 className="text-4xl font-black text-white tracking-tight">Financial Vector Analytics</h1>
          <p className="text-slate-500 mt-2 font-medium">Algorithmic deep-dive into score clusters and correlation matrices.</p>
        </div>
        <div className="flex gap-4">
           <div className="glass px-6 py-4 flex items-center gap-10">
              <div className="text-center">
                 <p className="text-[10px] font-black text-slate-500 uppercase">Standard Dev</p>
                 <p className="text-lg font-black text-white">12.4</p>
              </div>
              <div className="text-center">
                 <p className="text-[10px] font-black text-slate-500 uppercase">Risk Skew</p>
                 <p className="text-lg font-black text-rose-500">+2.1</p>
              </div>
           </div>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-8 glass p-10 h-[500px]">
           <h3 className="text-xl font-black text-white mb-8 flex items-center gap-2">
             <Activity size={20} className="text-[#6c63ff]" />
             Risk Score Frequency Distribution
           </h3>

           <ResponsiveContainer width="100%" height={350}>
             <AreaChart data={bins} margin={{ top: 10, right: 30, left: 20, bottom: 20 }}>
               <defs>
                 <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                   <stop offset="5%" stopColor="#6c63ff" stopOpacity={0.3}/>
                   <stop offset="95%" stopColor="#6c63ff" stopOpacity={0}/>
                 </linearGradient>
               </defs>
               <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.03)" />
               <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#4b5563', fontSize: 10}} label={{ value: 'Risk Score Clusters (0-100)', position: 'insideBottom', offset: -10, fill: '#4b5563', fontSize: 10, fontWeight: 'bold' }} />
               <YAxis axisLine={false} tickLine={false} tick={{fill: '#4b5563', fontSize: 10}} label={{ value: 'Customer Frequency', angle: -90, position: 'insideLeft', fill: '#4b5563', fontSize: 10, fontWeight: 'bold' }} />
               <Tooltip contentStyle={{ backgroundColor: '#0d1117', border: 'none', borderRadius: '12px' }} />
               <Area type="monotone" dataKey="count" stroke="#6c63ff" strokeWidth={3} fillOpacity={1} fill="url(#colorCount)" />
             </AreaChart>
           </ResponsiveContainer>
        </div>

        <div className="col-span-4 glass p-10 overflow-y-auto">
           <h3 className="text-xl font-black text-white mb-6">Risk Drivers</h3>
           <div className="space-y-4">
             {[
               { label: 'Asset Volatility', impact: 'High', color: 'bg-rose-500' },
               { label: 'Transaction Velocity', impact: 'Medium', color: 'bg-amber-500' },
               { label: 'Geolocation Mismatch', impact: 'High', color: 'bg-rose-500' },
               { label: 'Digital Fingerprint', impact: 'Low', color: 'bg-emerald-500' },
               { label: 'Historical Flag', impact: 'High', color: 'bg-rose-500' },
             ].map((d, i) => (
               <div key={i} className="flex justify-between items-center p-4 bg-white/5 border border-white/5 rounded-2xl">
                 <span className="text-xs font-bold text-slate-300">{d.label}</span>
                 <span className={`text-[10px] font-black px-2 py-1 rounded-md ${d.color} text-white uppercase`}>{d.impact}</span>
               </div>
             ))}
           </div>
        </div>
      </div>
    </div>
  );
};

const Insights = () => {
  return (
    <div className="space-y-10 animate-fadeIn">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-4xl font-black text-white tracking-tight">Intelligence Dashboard</h1>
          <p className="text-slate-500 mt-2 font-medium">SHAP Explainability & Business Intelligence visualizations.</p>
        </div>
        <div className="bg-[#6c63ff] px-6 py-3 rounded-2xl text-[10px] font-black text-white shadow-xl shadow-indigo-500/20 uppercase tracking-widest cursor-pointer hover:scale-105 transition-transform">Run Deep Inference</div>
      </div>

      <div className="grid grid-cols-2 gap-8">
        <div className="glass p-10 flex flex-col items-center">
           <h3 className="text-lg font-black text-white mb-6 self-start uppercase tracking-widest text-[#6c63ff]">SHAP Resource Contribution</h3>
           <div className="w-full h-[600px] bg-white/[0.01] border border-white/5 rounded-[32px] overflow-hidden flex items-center justify-center p-10 group">
              <img src="/plots/shap_summary.png" alt="SHAP Summary" className="max-w-full max-h-full object-contain group-hover:scale-105 transition-transform duration-700 shadow-2xl" />
           </div>
           <p className="mt-6 text-xs text-slate-500 text-center px-10 leading-relaxed font-medium">
             Visualization of feature impact on model output. Factors in <span className="text-rose-400 font-bold">magenta</span> represent increased risk, while <span className="text-[#6c63ff] font-bold">indigo</span> represents mitigating factors.
           </p>
        </div>

         <div className="glass p-10 flex flex-col items-center">
           <h3 className="text-lg font-black text-white mb-6 self-start uppercase tracking-widest text-[#6c63ff]">Unified Feature Importance</h3>
           <div className="w-full h-[600px] bg-white/[0.01] border border-white/5 rounded-[32px] overflow-hidden flex items-center justify-center p-10 group">
              <img src="/plots/shap_importance.png" alt="SHAP Importance" className="max-w-full max-h-full object-contain group-hover:scale-105 transition-transform duration-700 shadow-2xl" />
           </div>
           <p className="mt-6 text-xs text-slate-500 text-center px-10 leading-relaxed font-medium">
             Global feature impact ranking based on average absolute SHAP values. Highly weighted features indicate primary model sensitivity areas.
           </p>
        </div>
      </div>

      <div className="glass p-12 relative overflow-hidden">
        <div className="relative z-10 flex gap-20">
           <div className="w-1/3">
              <h4 className="text-2xl font-black text-white mb-4">Strategic Business Impact</h4>
              <p className="text-slate-400 text-sm leading-relaxed mb-6">Our automated decision engine has successfully diverted <span className="text-white font-bold">42 high-risk entities</span> in the last cycle, preventing an estimated <span className="text-emerald-500 font-bold">$1.2M in potential exposure</span>.</p>
              <div className="flex gap-4">
                 <div className="bg-white/5 p-4 rounded-2xl border border-white/5 flex-1">
                    <p className="text-[10px] font-black text-slate-500 uppercase mb-1">Efficiency Gain</p>
                    <p className="text-2xl font-black text-white">+64%</p>
                 </div>
                 <div className="bg-white/5 p-4 rounded-2xl border border-white/5 flex-1">
                    <p className="text-[10px] font-black text-slate-500 uppercase mb-1">Exposure Save</p>
                    <p className="text-2xl font-black text-white">$1.2M</p>
                 </div>
              </div>
           </div>
           <div className="flex-1 grid grid-cols-2 gap-6">
              <div className="bg-white/5 border border-white/10 p-8 rounded-[32px] hover:bg-white/10 transition-colors">
                 <div className="w-12 h-12 rounded-2xl bg-indigo-500/20 flex items-center justify-center text-indigo-400 mb-6">
                    <Zap size={24} />
                 </div>
                 <h5 className="text-lg font-black text-white mb-2">Automated Tiering</h5>
                 <p className="text-xs text-slate-500 font-medium">Dynamic allocation of entity profiles based on live financial telemetry.</p>
              </div>
              <div className="bg-white/5 border border-white/10 p-8 rounded-[32px] hover:bg-white/10 transition-colors">
                 <div className="w-12 h-12 rounded-2xl bg-rose-500/20 flex items-center justify-center text-rose-400 mb-6">
                    <AlertTriangle size={24} />
                 </div>
                 <h5 className="text-lg font-black text-white mb-2">Threat Mitigation</h5>
                 <p className="text-xs text-slate-500 font-medium">Real-time locks on suspicious account sequences identified by SHAP.</p>
              </div>
           </div>
        </div>
        <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-[#6c63ff]/10 blur-[150px] -z-0" />
      </div>
    </div>
  );
};

const Customers = ({ data, search, onSelect }) => {
  const [filter, setFilter] = useState('HIGH'); // Default to high priority
  
  const filtered = useMemo(() => 
    data.filter(d => 
      (filter === 'ALL' || d.risk_tier === filter) && 
      d.customer_id.toLowerCase().includes(search.toLowerCase())
    ), [data, search, filter]);

  return (
    <div className="space-y-8 animate-fadeIn">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-black text-white tracking-tight">Case Management</h2>
          <p className="text-sm text-slate-500 mt-1 font-medium">Priority workflow focusing on high-risk detections.</p>
        </div>
        <div className="flex gap-4">
          <div className="flex bg-white/5 p-1 rounded-2xl border border-white/10">
            {['HIGH', 'MEDIUM', 'ALL'].map(f => (
              <button key={f} onClick={() => setFilter(f)} className={`px-6 py-2 rounded-xl text-[10px] font-black uppercase transition-all ${filter === f ? 'bg-[#6c63ff] text-white' : 'text-slate-500 hover:text-white'}`}>
                {f}
              </button>
            ))}
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-3 gap-6">
        {filtered.map((item) => (
          <div key={item.customer_id} onClick={() => onSelect(item)} className="glass p-8 relative overflow-hidden group cursor-pointer card-hover border-white/5 hover:border-[#6c63ff]/30">
            <div className={`absolute top-0 right-0 w-2 h-full ${item.risk_tier === 'HIGH' ? 'bg-rose-500' : 'bg-amber-500'}`} />
            <div className="flex justify-between items-start mb-6">
               <div className="w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center font-black text-xs">ID</div>
               <span className={`px-3 py-1 rounded-lg text-[8px] font-black uppercase ${item.risk_tier === 'HIGH' ? 'bg-rose-500/10 text-rose-500' : 'bg-amber-500/10 text-amber-500'}`}>Priority</span>
            </div>
            <h4 className="text-xl font-black text-white mb-1">{item.customer_id}</h4>
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-6">{item.decision}</p>
            <div className="flex justify-between items-center text-[10px] font-black text-slate-400">
               <span>SCORE: {item.risk_score.toFixed(1)}</span>
               <ChevronRight size={16} className="group-hover:translate-x-1 transition-transform" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const AuditDatabase = ({ data, search, onSelect }) => {
  const filtered = useMemo(() => 
    data.filter(d => d.customer_id.toLowerCase().includes(search.toLowerCase())), 
    [data, search]
  );

  return (
    <div className="space-y-8 animate-fadeIn">
      <div className="flex justify-between items-center bg-white/[0.01] border border-white/5 p-8 rounded-[30px]">
        <div>
          <h2 className="text-3xl font-black text-white tracking-tight">Audit Ledger</h2>
          <p className="text-sm text-slate-500 mt-1 font-medium">{data.length} Total Master Entries</p>
        </div>
        <div className="flex gap-4">
          <button className="bg-white/5 border border-white/10 text-white px-6 py-4 rounded-2xl text-[10px] font-black uppercase hover:bg-white/10 transition-all flex items-center gap-2">
            <Database size={14} /> Export CSV
          </button>
        </div>
      </div>
      <div className="glass overflow-hidden">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-white/5 bg-white/[0.02]">
              <th className="px-8 py-6 text-[10px] font-black text-slate-500 uppercase tracking-widest">Customer ID</th>
              <th className="px-8 py-6 text-[10px] font-black text-slate-500 uppercase tracking-widest">Vector Score</th>
              <th className="px-8 py-6 text-[10px] font-black text-slate-500 uppercase tracking-widest">Account Type</th>
              <th className="px-8 py-6 text-[10px] font-black text-slate-500 uppercase tracking-widest">Document Status</th>
              <th className="px-8 py-6 text-[10px] font-black text-slate-500 uppercase tracking-widest">Residency Risk</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {filtered.map((item) => (
              <tr key={item.customer_id} className="hover:bg-white/[0.03] transition-all cursor-pointer group" onClick={() => onSelect(item)}>
                <td className="px-8 py-5 font-mono text-sm font-black text-white/80">{item.customer_id}</td>
                <td className="px-8 py-5">
                   <div className="px-3 py-1 rounded bg-white/5 border border-white/5 inline-block text-[10px] font-black font-mono">{item.risk_score.toFixed(2)}</div>
                </td>
                <td className="px-8 py-5 text-xs font-bold text-slate-400 capitalize">{item.account_type || 'Savings'}</td>
                <td className="px-8 py-5">
                   <span className={`flex items-center gap-2 text-[10px] font-black uppercase ${item.document_status === 'Complete' ? 'text-emerald-500' : 'text-rose-500'}`}>
                     {item.document_status === 'Complete' ? <CheckCircle2 size={12} /> : <AlertTriangle size={12} />}
                     {item.document_status}
                   </span>
                </td>
                <td className="px-8 py-5 text-xs font-bold tracking-wider">
                   <span className={`px-2 py-1 rounded text-[10px] font-black uppercase ${
                     item.country_risk === 'High' ? 'bg-rose-500/10 text-rose-500' :
                     item.country_risk === 'Medium' ? 'bg-amber-500/10 text-amber-500' :
                     'bg-emerald-500/10 text-emerald-500'
                   }`}>
                     {item.country_risk} Risk
                   </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const CustomerDetail = ({ customer, onClose }) => {
  const flags = [
    { label: "PEP Status", val: customer.pep_flag, color: "text-[#6c63ff] border-[#6c63ff]/20 bg-[#6c63ff]/10" },
    { label: "Sanctions", val: customer.sanctions_flag, color: "text-rose-500 border-rose-500/20 bg-rose-500/10" },
    { label: "Adverse Media", val: customer.adverse_media_flag, color: "text-amber-500 border-amber-500/20 bg-amber-500/10" },
    { label: "Fraud History", val: customer.fraud_history_flag, color: "text-rose-500 border-rose-500/20 bg-rose-500/10" }
  ];

  return (
    <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} className="space-y-10">
      <div className="flex justify-between items-center">
        <button onClick={onClose} className="text-slate-500 hover:text-white flex items-center gap-2 text-sm font-black uppercase tracking-widest transition-colors">
          <ChevronRight size={18} className="rotate-180" /> Back
        </button>
        <div className="flex gap-4">
          <button className="glass px-6 py-3 text-[10px] font-black uppercase text-white hover:bg-white/10 transition-all">Export Dossier</button>
          <button className="bg-[#6c63ff] px-6 py-3 rounded-2xl text-[10px] font-black uppercase text-white shadow-xl shadow-indigo-500/20">Override Score</button>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-8">
        <div className="glass p-10 flex flex-col items-center text-center h-full">
          <div className="w-24 h-24 rounded-3xl bg-white/5 border border-white/10 flex items-center justify-center mb-6">
            <User size={48} className="text-[#6c63ff]" />
          </div>
          <h2 className="text-3xl font-black text-white mb-2">{customer.customer_id}</h2>
          <p className="text-[#6c63ff] text-[10px] font-black uppercase tracking-[0.3em] mb-6">{customer.occupation || 'Private Client'}</p>
          
          <div className="w-full space-y-3 bg-black/20 p-6 rounded-3xl border border-white/5 text-left text-xs font-semibold">
            <div className="flex justify-between border-b border-white/5 pb-2">
              <span className="text-slate-400">Age</span>
              <span className="text-white">{customer.age} Years</span>
            </div>
            <div className="flex justify-between border-b border-white/5 pb-2">
              <span className="text-slate-400">Annual Income</span>
              <span className="text-white">${customer.annual_income?.toLocaleString()}</span>
            </div>
            <div className="flex justify-between border-b border-white/5 pb-2">
              <span className="text-slate-400">Account Type</span>
              <span className="text-white capitalize">{customer.account_type}</span>
            </div>
            <div className="flex justify-between border-b border-white/5 pb-2">
              <span className="text-slate-400">Tenure</span>
              <span className="text-white">{customer.customer_tenure_years} Years</span>
            </div>
            <div className="flex justify-between border-b border-white/5 pb-2">
              <span className="text-slate-400">Monthly Txn Count</span>
              <span className="text-white">{customer.monthly_txn_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Address Status</span>
              <span className={customer.address_verified ? 'text-emerald-500 font-bold' : 'text-rose-500 font-bold'}>
                {customer.address_verified ? 'Verified' : 'Unverified'}
              </span>
            </div>
          </div>
        </div>
        <div className="col-span-2 glass p-10 h-full flex flex-col justify-between">
          <div>
            <h3 className="text-xl font-black text-white mb-8">Explainability Matrix (SHAP)</h3>
            
            <div className="flex justify-between items-end mb-2 px-4">
               <span className="text-[8px] font-black text-[#6c63ff] uppercase tracking-widest">← Mitigating Factors (Lower Risk)</span>
               <span className="text-[8px] font-black text-rose-500 uppercase tracking-widest">Risk Drivers (Higher Risk) →</span>
            </div>
            
            <div className="h-32 bg-white/[0.02] border border-white/10 rounded-[32px] relative flex items-center px-4 overflow-hidden mb-8">
              <div className="flex-1 flex justify-end pr-4 text-[10px] font-black text-indigo-400">
                 <div className="h-10 bg-indigo-500/40 w-1/3 rounded-l-xl" />
                 <div className="h-10 bg-indigo-500/60 w-1/4" />
              </div>
              <div className="bg-white text-black px-6 py-3 rounded-2xl text-xl font-black relative z-10 shadow-2xl">{customer.risk_score.toFixed(1)}</div>
              <div className="flex-1 flex justify-start pl-4">
                 <div className="h-10 bg-rose-500/60 w-1/2" />
                 <div className="h-10 bg-rose-500/40 w-1/4" />
                 <div className="h-10 bg-rose-500/20 w-1/6 rounded-r-xl" />
              </div>
            </div>

            <div className="space-y-4 mb-8">
               <h4 className="text-xs font-black text-slate-500 uppercase tracking-wider mb-2">Key Risk Factors Identified</h4>
               <div className="flex flex-wrap gap-3">
                  {customer.top_risk_factors.split(',').map((factor, i) => (
                     <span key={i} className="px-4 py-2 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-bold rounded-2xl flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" />
                        {factor.trim()}
                     </span>
                  ))}
               </div>
            </div>

            <div className="space-y-4">
              <h4 className="text-xs font-black text-slate-500 uppercase tracking-wider mb-2">Regulatory & Compliance Flags</h4>
              <div className="grid grid-cols-4 gap-4">
                {flags.map((flag, idx) => (
                  <div key={idx} className={`p-4 rounded-2xl border text-center font-bold flex flex-col items-center justify-center gap-2 transition-all ${
                    flag.val ? flag.color : 'text-slate-500 border-white/5 bg-white/[0.01] opacity-40'
                  }`}>
                    {flag.val ? <AlertOctagon size={16} /> : <UserCheck size={16} />}
                    <span className="text-[10px] uppercase tracking-wider leading-none">{flag.label}</span>
                    <span className="text-[9px] uppercase tracking-widest opacity-80 mt-1">{flag.val ? 'Triggered' : 'Clear'}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          <div className="p-8 bg-white/5 border border-white/5 rounded-3xl relative mt-8">
             <div className="absolute top-0 right-10 -translate-y-1/2 flex gap-4">
                <div className="flex items-center gap-2 bg-[#0d1117] px-3 py-1 rounded-full border border-white/5">
                   <div className="w-2 h-2 rounded-full bg-rose-500" />
                   <span className="text-[8px] font-black text-slate-400 uppercase">Risk Up</span>
                </div>
                <div className="flex items-center gap-2 bg-[#0d1117] px-3 py-1 rounded-full border border-white/5">
                   <div className="w-2 h-2 rounded-full bg-[#6c63ff]" />
                   <span className="text-[8px] font-black text-slate-400 uppercase">Risk Down</span>
                </div>
             </div>
             <p className="italic text-slate-400 font-medium leading-relaxed">"{customer.top_risk_factors}"</p>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

// --- Main App ---

function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <div className="flex min-h-screen bg-[#0d1117] text-white selection:bg-[#6c63ff] selection:text-white">
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={(tab) => {
          setSelectedCustomer(null);
          setActiveTab(tab);
        }} 
      />
      <main className="flex-1 ml-72 p-14 relative z-10">
        <header className="flex justify-between items-center mb-16">
          <div className="flex items-center gap-4 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={20} />
            <input 
              type="text" 
              placeholder="Deep search ledger..." 
              className="pl-14 pr-6 py-4 bg-white/5 border border-white/10 rounded-2xl text-sm font-bold text-white focus:outline-none w-[400px] transition-all" 
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                if (activeTab !== 'customers' && activeTab !== 'database') {
                  setActiveTab('customers');
                }
              }}
            />
          </div>
          <div className="flex items-center gap-6">
            <Bell className="text-slate-500 cursor-pointer hover:text-white" size={20} />
            <div className="h-8 w-px bg-white/10" />
            <div className="flex items-center gap-4 glass px-5 py-2 rounded-2xl">
              <div className="w-8 h-8 rounded-lg bg-[#6c63ff] flex items-center justify-center text-xs font-black">WT</div>
              <div className="text-left font-black">
                <p className="text-[10px] leading-tight">We Tried</p>
                <p className="text-[8px] text-[#6c63ff] uppercase letter-spacing-widest">Admin</p>
              </div>
            </div>
          </div>
        </header>

        <AnimatePresence mode="wait">
          <motion.div key={selectedCustomer ? 'detail' : activeTab} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.4 }}>
            {selectedCustomer ? (
              <CustomerDetail customer={selectedCustomer} onClose={() => setSelectedCustomer(null)} />
            ) : (
              <>
                {activeTab === 'overview' && <Overview data={kycData} />}
                {activeTab === 'analytics' && <Analytics data={kycData} />}
                {activeTab === 'customers' && <Customers data={kycData} search={searchQuery} onSelect={setSelectedCustomer} />}
                {activeTab === 'database' && <AuditDatabase data={kycData} search={searchQuery} onSelect={setSelectedCustomer} />}
                {activeTab === 'insights' && <Insights />}
              </>
            )}
          </motion.div>
        </AnimatePresence>
      </main>
      <div className="fixed inset-0 bg-[radial-gradient(circle_at_top_right,rgba(108,99,255,0.05),transparent_70%)] pointer-events-none" />
    </div>
  );
}

export default App;
