import React from "react";
import { ShieldCheck } from "lucide-react";

export default function Header({ systemStatus }) {
  return (
    <header className="border-b border-base-700 bg-base-900/80 backdrop-blur sticky top-0 z-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-accent-teal/10 border border-accent-teal/30 flex items-center justify-center">
            <ShieldCheck className="w-5 h-5 text-accent-teal" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-slate-100 leading-tight">
              SecureScope
            </h1>
            <p className="text-xs text-slate-400 leading-tight">
              Healthcare Security Operations Platform
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-slate-300 hidden sm:inline">{systemStatus}</span>
        </div>
      </div>
    </header>
  );
}
