import React from 'react';
import { Layers, Database, Cpu, Search, Sparkles, Shield, ArrowRight, Globe, CheckCircle2 } from 'lucide-react';

export default function ArchitectureView() {
  const pipelineSteps = [
    {
      title: "1. Citizen Query Ingestion",
      desc: "Natural language query input (e.g., 'small farmer owning 2 acres looking for fertilizer support').",
      icon: Search,
      color: "bg-blue-50 text-blue-700 border-blue-200"
    },
    {
      title: "2. Dual Hybrid Retrieval",
      desc: "Parallel execution: Lexical BM25 / FTS on tsvector + 384-dim Dense vector nearest-neighbor search.",
      icon: Database,
      color: "bg-purple-50 text-purple-700 border-purple-200"
    },
    {
      title: "3. Reciprocal Rank Fusion (RRF)",
      desc: "Score = 0.4/(60+Rank_lex) + 0.6/(60+Rank_dense) to fuse rankings without score scale mismatch.",
      icon: Layers,
      color: "bg-amber-50 text-amber-700 border-amber-200"
    },
    {
      title: "4. Grounded Generation",
      desc: "Prompt strictly conditioned on top K retrieved chunks. Disallows fabricated eligibility criteria.",
      icon: Sparkles,
      color: "bg-emerald-50 text-emerald-700 border-emerald-200"
    },
    {
      title: "5. RAGAS Evaluation & Tracing",
      desc: "Automated verification of Faithfulness (claim support) and Answer Relevancy scores.",
      icon: Shield,
      color: "bg-rose-50 text-rose-700 border-rose-200"
    }
  ];

  const techStack = [
    { component: "Core Languages", tech: "Python 3.12, SQL, JavaScript (ES2024)" },
    { component: "Backend Framework", tech: "FastAPI, LangChain, Pydantic v2, Uvicorn" },
    { component: "Frontend Interface", tech: "React.js 18, Vite, Tailwind CSS, Lucide Icons" },
    { component: "Database & Storage", tech: "PostgreSQL with pgvector & tsvector (Dual support for SQLite fallback)" },
    { component: "AI & Search Engine", tech: "Sentence Transformers (all-MiniLM-L6-v2), BM25 Lexical + Cosine Semantic" },
    { component: "Evaluation & Tracing", tech: "RAGAS-style Faithfulness & Relevancy Engine, Latency Tracking" },
    { component: "Deployment & Containers", tech: "Docker, Docker-Compose (images prefixed with 'minor_')" }
  ];

  return (
    <div className="space-y-8">
      {/* Title */}
      <div>
        <h2 className="text-2xl font-bold text-slate-900">System Architecture & SDG Alignment</h2>
        <p className="text-sm text-slate-500">
          Complete technical architecture, hybrid retrieval dataflow, and social impact mapping as detailed in the project synopsis.
        </p>
      </div>

      {/* Interactive Dataflow Pipeline */}
      <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-xs space-y-6">
        <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
          <Cpu className="w-5 h-5 text-emerald-600" />
          <span>End-to-End Hybrid RAG Pipeline</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {pipelineSteps.map((step, idx) => {
            const Icon = step.icon;
            return (
              <div key={idx} className="relative flex flex-col justify-between p-4 rounded-xl border bg-slate-50/50 space-y-3">
                <div className="space-y-2">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center border ${step.color}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <h4 className="font-bold text-xs text-slate-900">{step.title}</h4>
                  <p className="text-[11px] text-slate-600 leading-relaxed">{step.desc}</p>
                </div>
                {idx < pipelineSteps.length - 1 && (
                  <div className="hidden md:block absolute -right-3 top-1/2 -translate-y-1/2 z-10 bg-white rounded-full p-1 border border-slate-200 shadow-2xs">
                    <ArrowRight className="w-3 h-3 text-slate-400" />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Technology Stack Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden p-6 space-y-4">
        <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
          <Layers className="w-5 h-5 text-emerald-600" />
          <span>Technology Stack Implementation</span>
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider">
                <th className="py-3 px-4 w-1/3">Component</th>
                <th className="py-3 px-4">Technologies & Libraries</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {techStack.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-50/80 transition">
                  <td className="py-3 px-4 font-semibold text-slate-900">{row.component}</td>
                  <td className="py-3 px-4 font-mono text-emerald-800">{row.tech}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Sustainable Development Goals (SDG 16) Alignment */}
      <div className="bg-gradient-to-br from-slate-900 to-emerald-950 text-white rounded-2xl p-6 sm:p-8 space-y-4 border border-emerald-900/50 shadow-lg">
        <div className="flex items-center space-x-2 text-emerald-400">
          <Globe className="w-6 h-6" />
          <h3 className="text-base font-bold tracking-wide uppercase">
            Sustainable Development Goal (SDG 16) Alignment
          </h3>
        </div>

        <div className="bg-slate-800/80 p-5 rounded-xl border border-slate-700 space-y-3">
          <div className="flex items-center space-x-2">
            <span className="bg-emerald-500 text-slate-950 font-extrabold text-xs px-2.5 py-0.5 rounded">
              SDG 16
            </span>
            <span className="font-bold text-sm text-white">Peace, Justice and Strong Institutions</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            By making government welfare schemes searchable in plain natural language and grounding every answer in official public documents with source citations, this platform directly addresses public information asymmetry. It empowers vulnerable and unorganized citizens to become aware of their constitutional and statutory welfare rights.
          </p>
        </div>
      </div>
    </div>
  );
}
