import React, { useState } from 'react';
import { HouseOption, HandoffPackage } from '../types';
import { 
  Lock, 
  AlertTriangle, 
  CheckCircle2, 
  HardHat, 
  Hash 
} from 'lucide-react';

interface BuildReleaseViewProps {
  selectedOption: HouseOption;
  activeRelease: HandoffPackage | null;
  activeReleaseId: string;
  onLockBuild: (tier: string, acks: string[]) => Promise<void>;
  onGoToEngineerDashboard: () => void;
  isLocking: boolean;
}

export const BuildReleaseView: React.FC<BuildReleaseViewProps> = ({
  selectedOption,
  activeRelease,
  activeReleaseId,
  onLockBuild,
  onGoToEngineerDashboard,
  isLocking
}) => {
  const [qualityTier, setQualityTier] = useState<string>('STANDARD');
  const [ackDelivery, setAckDelivery] = useState<boolean>(true);
  const [ackSiteVerification, setAckSiteVerification] = useState<boolean>(true);
  const [ackPermits, setAckPermits] = useState<boolean>(true);
  const [ackChangeOrders, setAckChangeOrders] = useState<boolean>(true);

  const layout = selectedOption.layout;
  const boq = selectedOption.boq;
  const schedule = selectedOption.schedule;

  const allChecked = ackDelivery && ackSiteVerification && ackPermits && ackChangeOrders;

  const handleConfirm = async () => {
    if (!allChecked) return;
    const acks = [
      'PROFESSIONAL_DELIVERY',
      'ESTIMATE_RANGE',
      'SITE_VERIFICATION',
      'CHANGE_ORDER_RULES'
    ];
    await onLockBuild(qualityTier, acks);
  };

  // If a release has already been created and locked:
  if (activeRelease && activeReleaseId) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center bg-[#070b12] text-slate-200 p-8 select-none">
        <div className="glass-panel p-8 max-w-2xl w-full border border-emerald-500/40 shadow-2xl space-y-6 animate-in fade-in">
          {/* Header */}
          <div className="flex items-center gap-3 border-b border-white/10 pb-4">
            <div className="w-10 h-10 rounded-xl bg-emerald-600/30 border border-emerald-500/50 flex items-center justify-center">
              <CheckCircle2 className="w-6 h-6 text-emerald-400" />
            </div>
            <div>
              <span className="text-[10px] font-mono text-emerald-400 font-bold uppercase tracking-wider block">
                Release Created & Frozen
              </span>
              <h2 className="font-display font-bold text-xl text-white">
                Design Version Locked for Construction Delivery
              </h2>
            </div>
          </div>

          {/* Release Fingerprint & Metadata Card */}
          <div className="bg-slate-950 p-4 rounded-xl border border-white/10 space-y-3 font-mono text-xs">
            <div className="flex justify-between items-center text-slate-400">
              <span>Release ID:</span>
              <span className="text-white font-bold">{activeReleaseId}</span>
            </div>
            <div className="flex justify-between items-center text-slate-400">
              <span>Lifecycle State:</span>
              <span className="px-2 py-0.5 rounded bg-amber-950 text-amber-400 font-bold border border-amber-800/40">
                {activeRelease.lifecycleState}
              </span>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px] uppercase">SHA-256 Release Fingerprint:</span>
              <div className="text-cyan-300 font-bold text-xs break-all bg-slate-900/80 p-2 rounded mt-1 border border-white/5 flex items-center gap-1.5">
                <Hash className="w-4 h-4 text-blue-400 shrink-0" />
                <span>{activeRelease.releaseFingerprint}</span>
              </div>
            </div>
          </div>

          <div className="text-xs text-slate-300 leading-normal bg-blue-950/20 p-3 rounded-lg border border-blue-800/30">
            <strong>Next Step:</strong> This frozen release has been submitted to the Licensed Engineer Verification queue. You can now inspect the G0–G8 approval gates and download the coordinated BIM IFC4 package.
          </div>

          {/* Action Trigger */}
          <div className="pt-2 flex justify-end">
            <button
              onClick={onGoToEngineerDashboard}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 text-white font-display font-bold text-sm shadow-lg shadow-amber-600/30 flex items-center gap-2 transition-all active:scale-95"
            >
              <HardHat className="w-4 h-4" />
              <span>PROCEED TO ENGINEER REVIEW →</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Pre-confirmation Design Release Form
  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-[#070b12] text-slate-200 p-8 select-none overflow-y-auto">
      <div className="glass-panel p-8 max-w-2xl w-full border border-emerald-500/40 shadow-2xl space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-white/10 pb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-600/30 border border-emerald-500/50 flex items-center justify-center">
              <Lock className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <span className="text-[10px] font-mono text-cyan-400 font-bold uppercase tracking-wider block">
                Design Release Workflow (Delta Spec §12)
              </span>
              <h2 className="font-display font-bold text-lg text-white">
                Request Professional Delivery for {layout.label}
              </h2>
            </div>
          </div>

          <span className="text-xs font-mono font-bold px-2.5 py-1 rounded bg-slate-900 border border-white/10 text-slate-300">
            {selectedOption.designVersionId}
          </span>
        </div>

        {/* Option Specs Summary */}
        <div className="grid grid-cols-4 gap-3 bg-slate-950 p-3 rounded-xl border border-white/10 text-xs font-mono text-center">
          <div>
            <span className="text-[10px] text-slate-500 block uppercase">BUA</span>
            <span className="font-bold text-white text-sm">{layout.totalGrossBUASqm} m²</span>
          </div>
          <div>
            <span className="text-[10px] text-slate-500 block uppercase">Estimate</span>
            <span className="font-bold text-emerald-400 text-sm">₹{(boq.totalBaseEstimate / 100000).toFixed(1)}L</span>
          </div>
          <div>
            <span className="text-[10px] text-slate-500 block uppercase">Duration</span>
            <span className="font-bold text-amber-300 text-sm">{schedule.totalDurationMonths} Mos</span>
          </div>
          <div>
            <span className="text-[10px] text-slate-500 block uppercase">Regulation</span>
            <span className="font-bold text-cyan-400 text-sm">DCPR 2034</span>
          </div>
        </div>

        {/* Quality Tier Selector */}
        <div className="space-y-1.5">
          <label className="text-xs text-slate-300 font-semibold block">Select Finish Specification Tier:</label>
          <div className="grid grid-cols-3 gap-2 text-xs">
            {[
              { id: 'STANDARD', label: 'Standard', desc: 'Vitrified tiles, CPVC, premium emulsion' },
              { id: 'PREMIUM', label: 'Premium (+25%)', desc: 'Italian marble, teak frames, VRV AC' },
              { id: 'LUXURY', label: 'Luxury (+60%)', desc: 'Smart automation, imported stone' }
            ].map((t) => (
              <button
                type="button"
                key={t.id}
                onClick={() => setQualityTier(t.id)}
                className={`p-3 rounded-lg border text-left transition-all ${
                  qualityTier === t.id
                    ? 'border-emerald-500 bg-emerald-950/40 text-white shadow-sm'
                    : 'border-white/10 bg-slate-900/60 text-slate-400 hover:text-slate-200'
                }`}
              >
                <span className="font-bold text-xs block">{t.label}</span>
                <span className="text-[10px] text-slate-500 block leading-tight mt-0.5">{t.desc}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Mandatory Professional Delivery Acknowledgements */}
        <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-800/40 space-y-2.5">
          <div className="flex items-center gap-1.5 text-amber-400 font-semibold text-xs">
            <AlertTriangle className="w-4 h-4" />
            <span>Required Delivery & Statutory Acknowledgements</span>
          </div>

          <div className="space-y-2 text-xs text-slate-300">
            <label className="flex items-start gap-2.5 cursor-pointer">
              <input
                type="checkbox"
                checked={ackDelivery}
                onChange={(e) => setAckDelivery(e.target.checked)}
                className="mt-0.5 accent-emerald-500 w-4 h-4"
              />
              <span>
                <strong>Professional Delivery Request:</strong> I acknowledge this is a request for professional delivery under a frozen design version, not instant permission to construct.
              </span>
            </label>

            <label className="flex items-start gap-2.5 cursor-pointer">
              <input
                type="checkbox"
                checked={ackSiteVerification}
                onChange={(e) => setAckSiteVerification(e.target.checked)}
                className="mt-0.5 accent-emerald-500 w-4 h-4"
              />
              <span>
                <strong>Site Verification & Geotechnical Gate:</strong> I understand that field survey confirmation, soil borehole investigation, and foundation selection are mandatory before ground release.
              </span>
            </label>

            <label className="flex items-start gap-2.5 cursor-pointer">
              <input
                type="checkbox"
                checked={ackPermits}
                onChange={(e) => setAckPermits(e.target.checked)}
                className="mt-0.5 accent-emerald-500 w-4 h-4"
              />
              <span>
                <strong>Statutory Sanction Responsibility:</strong> Municipal permit processing will proceed under Mumbai MCGM DCPR 2034 by the licensed architect-of-record.
              </span>
            </label>

            <label className="flex items-start gap-2.5 cursor-pointer">
              <input
                type="checkbox"
                checked={ackChangeOrders}
                onChange={(e) => setAckChangeOrders(e.target.checked)}
                className="mt-0.5 accent-emerald-500 w-4 h-4"
              />
              <span>
                <strong>Immutable Versioning & Change Orders:</strong> Post-release variations require a formal engineering change order with recalculated BOQ and cost impacts.
              </span>
            </label>
          </div>
        </div>

        {/* CTA Button */}
        <div className="pt-2 flex justify-end">
          <button
            onClick={handleConfirm}
            disabled={!allChecked || isLocking}
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-display font-bold text-sm shadow-lg shadow-emerald-600/30 flex items-center gap-2 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Lock className="w-4 h-4" />
            <span>{isLocking ? "Hashing & Freezing Model..." : "REQUEST BUILD →"}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
