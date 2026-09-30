import React, { useState } from 'react';
import { HandoffPackage, VerificationGate } from '../types';
import { 
  Download, 
  FileCode, 
  CheckCircle2, 
  AlertTriangle, 
  Clock,
  HardHat, 
  ArrowLeft,
  Hash,
  Award,
  UserCheck
} from 'lucide-react';

interface EngineerDashboardProps {
  handoffPackage: HandoffPackage;
  releaseId: string;
  onBackToStudio: () => void;
  onApproveGate: (gateId: string, decision: string, notes: string) => Promise<void>;
}

export const EngineerDashboard: React.FC<EngineerDashboardProps> = ({
  handoffPackage,
  releaseId,
  onBackToStudio,
  onApproveGate
}) => {
  const [selectedGate, setSelectedGate] = useState<VerificationGate | null>(
    handoffPackage.humanVerificationGates[3] // G3 Structural by default
  );
  const [reviewNotes, setReviewNotes] = useState<string>(
    'Structural member spans and load-path graph checked against IS 456 & NBC 2016 Part 6. Column dimensions 300x450mm verified.'
  );
  const [isUpdating, setIsUpdating] = useState<boolean>(false);

  const handleDecision = async (decision: string) => {
    if (!selectedGate) return;
    setIsUpdating(true);
    await onApproveGate(selectedGate.gate, decision, reviewNotes);
    setIsUpdating(false);
  };

  const downloadIFC = () => {
    window.open(`/api/v1/releases/${releaseId}/ifc`, '_blank');
  };

  const downloadManifest = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(handoffPackage, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `MANIFEST_${releaseId}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="w-full h-full flex flex-col bg-[#070b12] text-slate-200 overflow-y-auto p-6 space-y-6 select-none">
      {/* Top Professional Header Bar */}
      <div className="flex items-center justify-between pb-4 border-b border-white/10">
        <div className="flex items-center gap-3">
          <button
            onClick={onBackToStudio}
            className="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-white/10 transition-colors flex items-center gap-1.5 text-xs font-semibold"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Customer Studio</span>
          </button>

          <div className="h-4 w-px bg-white/10" />

          <div>
            <div className="flex items-center gap-2">
              <HardHat className="w-4 h-4 text-amber-400" />
              <h2 className="font-display font-bold text-base text-white tracking-wide">
                Licensed Engineer & Contractor Verification Workspace
              </h2>
            </div>
            <span className="text-[11px] text-slate-400 font-mono">
              Delta Specification §13 & §14 • Attributable Gate Sign-off & IFC4 Coordination
            </span>
          </div>
        </div>

        {/* Action Downloads */}
        <div className="flex items-center gap-2">
          <button
            onClick={downloadIFC}
            className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-indigo-600/20 transition-all"
          >
            <FileCode className="w-3.5 h-3.5" />
            <span>Download IFC4 (.ifc)</span>
          </button>

          <button
            onClick={downloadManifest}
            className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-500/20 transition-all"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download Manifest (.json)</span>
          </button>
        </div>
      </div>

      {/* Release Cryptographic Banner */}
      <div className="glass-panel p-5 bg-gradient-to-r from-blue-950/40 via-slate-900 to-slate-950 border border-blue-500/30 flex items-center justify-between">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2.5">
            <span className="text-[10px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-blue-600/30 text-blue-400 border border-blue-500/30">
              Frozen Release Manifest
            </span>
            <span className="text-xs font-mono font-bold text-emerald-400 flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              {handoffPackage.releaseStatus}
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 text-slate-300 border border-white/10">
              Release ID: {releaseId}
            </span>
          </div>

          <div className="font-mono text-sm text-cyan-300 font-bold break-all flex items-center gap-1.5 pt-1">
            <Hash className="w-4 h-4 text-blue-400 shrink-0" />
            <span>{handoffPackage.releaseFingerprint}</span>
          </div>
          <p className="text-[11px] text-slate-400">
            Geometry version, statutory DCPR 2034 ruleset snapshot, and rate catalog cryptographically pinned.
          </p>
        </div>

        <div className="text-right shrink-0 pl-6 border-l border-white/10 space-y-1">
          <span className="text-[10px] text-slate-400 uppercase font-mono block">Lifecycle State</span>
          <span className="font-mono font-bold text-sm text-amber-400 block px-2 py-0.5 rounded bg-amber-950/80 border border-amber-800/40">
            {handoffPackage.lifecycleState}
          </span>
          <span className="text-[10px] text-slate-500 font-mono block">CTS-1842-BANDRA</span>
        </div>
      </div>

      {/* Two-Column Engineering Workspace: Left Vertical Gate Timeline, Right Attributable Review Console */}
      <div className="grid grid-cols-3 gap-6">
        {/* Left 2 Cols: Vertical Verification Gates Timeline (G0 to G8) */}
        <div className="col-span-2 glass-panel p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-white/10 pb-3">
            <div className="flex items-center gap-2">
              <Award className="w-4 h-4 text-cyan-400" />
              <h3 className="font-display font-bold text-xs uppercase tracking-wider text-white">
                Human Verification Gates Timeline (G0 to G8)
              </h3>
            </div>
            <span className="text-[11px] font-mono text-slate-400">Delta Specification §14</span>
          </div>

          <div className="space-y-2.5">
            {handoffPackage.humanVerificationGates.map((gate) => {
              const isSelected = selectedGate?.gate === gate.gate;
              const isApproved = gate.status === 'APPROVED';
              const isPending = gate.status === 'PENDING_REVIEW';

              return (
                <div
                  key={gate.gate}
                  onClick={() => setSelectedGate(gate)}
                  className={`p-3 rounded-lg border cursor-pointer transition-all flex items-center justify-between ${
                    isSelected
                      ? 'border-blue-500 bg-blue-950/30 ring-1 ring-blue-500 shadow-md'
                      : 'border-white/5 bg-slate-900/60 hover:bg-slate-900'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className={`font-mono font-bold text-xs px-2 py-1 rounded border ${
                      isApproved
                        ? 'bg-emerald-950 text-emerald-400 border-emerald-800/60'
                        : isPending
                        ? 'bg-amber-950 text-amber-400 border-amber-800/60 animate-pulse'
                        : 'bg-slate-800 text-slate-400 border-slate-700'
                    }`}>
                      {gate.gate}
                    </span>
                    <div>
                      <span className="font-display font-bold text-xs text-white block">{gate.title}</span>
                      <span className="text-[10px] text-slate-400 font-mono">Authority: {gate.requiredBy}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    {isApproved ? (
                      <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800/50 flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3" />
                        APPROVED
                      </span>
                    ) : isPending ? (
                      <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded-full bg-amber-950 text-amber-400 border border-amber-800/50 flex items-center gap-1 animate-pulse">
                        <Clock className="w-3 h-3" />
                        PENDING REVIEW
                      </span>
                    ) : (
                      <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-500 border border-slate-700">
                        {gate.status}
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right 1 Col: Attributable Sign-off Panel */}
        <div className="glass-panel p-5 flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center gap-2 border-b border-white/10 pb-3 mb-3">
              <UserCheck className="w-4 h-4 text-emerald-400" />
              <h3 className="font-display font-bold text-xs uppercase tracking-wider text-white">
                Professional Attestation & Sign-Off
              </h3>
            </div>

            {selectedGate ? (
              <div className="space-y-3">
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-mono block">Reviewing Gate</span>
                  <span className="font-display font-bold text-sm text-white">{selectedGate.gate}: {selectedGate.title}</span>
                  <span className="text-[11px] text-cyan-400 block mt-0.5 font-mono">Sign-off: {selectedGate.requiredBy}</span>
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] text-slate-300 font-medium block">
                    Engineering Sign-Off Memo & Compliance Statement:
                  </label>
                  <textarea
                    rows={4}
                    value={reviewNotes}
                    onChange={(e) => setReviewNotes(e.target.value)}
                    className="w-full bg-slate-950 border border-white/10 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500 font-mono resize-none leading-normal"
                  />
                </div>

                <div className="p-2.5 rounded-lg bg-slate-900/80 border border-white/5 text-[11px] space-y-1.5 font-mono">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Professional License:</span>
                    <span className="text-slate-200 font-bold">ENG-MH-48201</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Current Gate Status:</span>
                    <span className="text-amber-400 font-bold">{selectedGate.status}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Governing Code:</span>
                    <span className="text-white">NBC 2016 / IS 456</span>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-400">Select a gate from the timeline to review.</p>
            )}
          </div>

          {/* Action Buttons */}
          <div className="space-y-2 pt-3 border-t border-white/10">
            <button
              onClick={() => handleDecision('APPROVED')}
              disabled={isUpdating}
              className="w-full py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-md shadow-emerald-600/20 flex items-center justify-center gap-1.5 transition-all active:scale-95 disabled:opacity-50"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Attest & Approve Gate</span>
            </button>

            <button
              onClick={() => handleDecision('REQUEST_REVISION')}
              disabled={isUpdating}
              className="w-full py-2.5 rounded-lg bg-amber-600/80 hover:bg-amber-500 text-white text-xs font-semibold flex items-center justify-center gap-1.5 transition-all active:scale-95 disabled:opacity-50"
            >
              <AlertTriangle className="w-4 h-4" />
              <span>Request Engineering Revision</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
