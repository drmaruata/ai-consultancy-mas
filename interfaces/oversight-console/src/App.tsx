import { Activity, Server, Cpu, Database, CheckCircle, AlertCircle, Clock, ShieldAlert } from 'lucide-react';

// Mock Data
const MOCK_AGENTS = [
  { id: 'ceo-1', name: 'CEO Orchestrator', layer: 0, status: 'idle', lastTask: '2 mins ago', vertical: 'all' },
  { id: 'qc-1', name: 'Quality & Compliance', layer: 2, status: 'running', lastTask: 'Just now', vertical: 'all' },
  { id: 'legal-mgr', name: 'Legal Vertical Manager', layer: 3, status: 'idle', lastTask: '1 hr ago', vertical: 'legal' },
  { id: 'health-mgr', name: 'Healthcare Vertical Manager', layer: 3, status: 'error', lastTask: '10 mins ago', vertical: 'healthcare' },
];

const MOCK_TASKS = [
  { id: 'tsk-001', agent: 'CEO Orchestrator', state: 'COMPLETE', time: '10:42 AM', title: 'Route new Lead to Legal' },
  { id: 'tsk-002', agent: 'Quality & Compliance', state: 'EXECUTING', time: '10:45 AM', title: 'Verify Deliverable A-042' },
  { id: 'tsk-003', agent: 'Legal Vertical Manager', state: 'ESCALATED', time: '10:30 AM', title: 'Review Non-Disclosure Agreement' },
];

const MOCK_INFRA = [
  { name: 'Redpanda (Kafka)', status: 'operational', latency: '24ms' },
  { name: 'Supabase (DB)', status: 'operational', latency: '45ms' },
  { name: 'Upstash (Vector)', status: 'operational', latency: '12ms' },
  { name: 'Upstash (Redis)', status: 'operational', latency: '8ms' },
  { name: 'LLM Router API', status: 'operational', latency: '350ms' },
];

function App() {
  const agents = MOCK_AGENTS;
  const tasks = MOCK_TASKS;
  const infra = MOCK_INFRA;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-emerald-500/30">
      {/* Header */}
      <header className="sticky top-0 z-50 flex items-center justify-between px-8 py-4 bg-slate-900/80 backdrop-blur-xl border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-emerald-500/10 rounded-lg border border-emerald-500/20">
            <Activity className="w-6 h-6 text-emerald-400" />
          </div>
          <h1 className="text-xl font-semibold tracking-tight">MAS Oversight Console <span className="text-slate-500 text-sm ml-2">v3.0</span></h1>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <span className="flex items-center gap-2 px-3 py-1.5 bg-slate-800/50 rounded-full border border-slate-700/50 text-slate-300">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Live
          </span>
        </div>
      </header>

      <main className="p-8 max-w-7xl mx-auto space-y-8">
        
        {/* Infrastructure Status */}
        <section>
          <h2 className="flex items-center gap-2 text-lg font-medium mb-4 text-slate-300">
            <Server className="w-5 h-5" />
            Infrastructure Status
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {infra.map((item, idx) => (
              <div key={idx} className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 flex flex-col gap-2 hover:bg-slate-800/50 transition-colors">
                <div className="flex items-start justify-between">
                  <Database className="w-5 h-5 text-slate-500" />
                  <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></span>
                </div>
                <div className="mt-2">
                  <p className="text-sm font-medium text-slate-200">{item.name}</p>
                  <p className="text-xs text-slate-500">{item.latency}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Agent Status Board */}
          <section className="lg:col-span-2 space-y-4">
            <h2 className="flex items-center gap-2 text-lg font-medium text-slate-300">
              <Cpu className="w-5 h-5" />
              Agent Status Board
            </h2>
            <div className="bg-slate-900/40 border border-slate-800 rounded-2xl overflow-hidden">
              <table className="w-full text-sm text-left">
                <thead className="bg-slate-800/50 text-slate-400">
                  <tr>
                    <th className="px-6 py-4 font-medium">Agent</th>
                    <th className="px-6 py-4 font-medium">Layer & Vertical</th>
                    <th className="px-6 py-4 font-medium">Status</th>
                    <th className="px-6 py-4 font-medium text-right">Last Task</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {agents.map((agent, i) => (
                    <tr key={i} className="hover:bg-slate-800/20 transition-colors">
                      <td className="px-6 py-4">
                        <div className="font-medium text-slate-200">{agent.name}</div>
                        <div className="text-xs text-slate-500 font-mono mt-0.5">{agent.id}</div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-800 text-slate-300 capitalize mr-2">
                          Layer {agent.layer}
                        </span>
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-800 text-slate-300 capitalize">
                          {agent.vertical}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        {agent.status === 'idle' && <span className="inline-flex items-center gap-1.5 text-slate-400"><Clock className="w-4 h-4"/> Idle</span>}
                        {agent.status === 'running' && <span className="inline-flex items-center gap-1.5 text-blue-400"><Activity className="w-4 h-4"/> Running</span>}
                        {agent.status === 'error' && <span className="inline-flex items-center gap-1.5 text-red-400"><AlertCircle className="w-4 h-4"/> Error</span>}
                      </td>
                      <td className="px-6 py-4 text-right text-slate-400">
                        {agent.lastTask}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {/* Task Log Feed */}
          <section className="space-y-4">
            <h2 className="flex items-center gap-2 text-lg font-medium text-slate-300">
              <Activity className="w-5 h-5" />
              Live Task Feed
            </h2>
            <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-4 h-[400px] overflow-y-auto">
              <div className="space-y-4">
                {tasks.map((task, i) => (
                  <div key={i} className="relative pl-6 pb-4 last:pb-0 border-l border-slate-800">
                    <div className="absolute -left-1.5 top-0 w-3 h-3 rounded-full bg-slate-900 border-2 border-slate-700">
                      {task.state === 'COMPLETE' && <div className="absolute inset-0 m-auto w-1.5 h-1.5 rounded-full bg-emerald-500" />}
                      {task.state === 'EXECUTING' && <div className="absolute inset-0 m-auto w-1.5 h-1.5 rounded-full bg-blue-500" />}
                      {task.state === 'ESCALATED' && <div className="absolute inset-0 m-auto w-1.5 h-1.5 rounded-full bg-orange-500" />}
                    </div>
                    <div className="flex flex-col gap-1 -mt-1.5">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-mono text-slate-500">{task.id}</span>
                        <span className="text-slate-500">{task.time}</span>
                      </div>
                      <p className="text-sm font-medium text-slate-200">{task.title}</p>
                      <p className="text-xs text-slate-400">Assigned to: {task.agent}</p>
                      <div className="mt-2">
                        {task.state === 'COMPLETE' && <span className="inline-flex items-center gap-1 text-xs font-medium text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-md"><CheckCircle className="w-3.5 h-3.5"/> Complete</span>}
                        {task.state === 'EXECUTING' && <span className="inline-flex items-center gap-1 text-xs font-medium text-blue-400 bg-blue-400/10 px-2 py-1 rounded-md"><Activity className="w-3.5 h-3.5"/> Executing</span>}
                        {task.state === 'ESCALATED' && <span className="inline-flex items-center gap-1 text-xs font-medium text-orange-400 bg-orange-400/10 px-2 py-1 rounded-md"><ShieldAlert className="w-3.5 h-3.5"/> Escalated</span>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>

        </div>
      </main>
    </div>
  );
}

export default App;
