import React, { useState } from 'react';
import { HouseOption } from '../types';
import { Lock, ShieldAlert, X } from 'lucide-react';

interface BuildLockModalProps {
  option: HouseOption | null;
  onClose: () => void;
  onConfirmBuild: (tier: string, acks: string[]) => Promise<void>;
  isLocking: boolean;
}

export const BuildLockModal: React.FC<BuildLockModalProps> = ({
  option,
  onClose,
  onConfirmBuild,
  isLocking
}) => {
  const [qualityTier, setQualityTier] = useState<string>('STANDARD');
  const [ackDelivery, setAckDelivery] = useState<boolean>(true);
  const [ackSiteVerification, setAckSiteVerification] = useState<boolean>(true);
  const [ackPermits, setAckPermits] = useState<boolean>(true);
  const [ackChangeOrders, setAckChangeOrders] = useState<boolean>(true);

  if (!option) return null;

  const allChecked = ackDelivery && ackSiteVerification && ackPermits && ackChangeOrders;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!allChecked) return;

    const acks = [
      'PROFESSIONAL_DELIVERY',
      'ESTIMATE_RANGE',
      'SITE_VERIFICATION',
      'CHANGE_ORDER_RULES'
    ];
    await onConfirmBuild(qualityTier, acks);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in">
      <div className="glass-panel w-full max-w-xl flex flex-col overflow-hidden shadow-2xl border border-emerald-500/40">
        {/* Header */}
        <div className="p-4 bg-gradient-to-r from-emerald-950/80 via-slate-900 to-slate-900 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-600/30 border border-emerald-500/40 flex items-center justify-center">
              <Lock className="w-4 h-4 text-emerald-400" />
            </div>
            <div>
              <h3 className="font-display font-bold text-sm text-white">
                Request Professional Delivery & Immutable Lock
              </h3>
              <p className="text-[11px] text-slate-400">
                Delta Specification §12 • Design Version Lock & SHA-256 Release
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4 text-xs">
          {/* Selected Option Summary Card */}
          <div className="p-3 rounded-lg bg-slate-900/90 border border-white/10 flex items-center justify-between">
            <div>
              <span className="text-[10px] text-slate-400 font-mono uppercase block">Candidate Option</span>
              <span className="font-display font-bold text-sm text-white">{option.layout.label}</span>
              <span className="text-[11px] text-cyan-400 font-mono block">
                {option.layout.totalGrossBUASqm} m² BUA • {option.layout.floors} Floor(s) • {option.layout.rooms.length} Rooms
              </span>
            </div>
            <div className="text-right">
              <span className="text-[10px] text-slate-400 uppercase block">Base Estimate</span>
              <span className="font-mono font-bold text-emerald-400 text-sm">
                ₹{(option.boq.totalBaseEstimate / 100000).toFixed(2)} Lakhs
              </span>
              <span className="text-[10px] text-slate-500 block font-mono">
                {option.schedule.totalDurationMonths} Months Delivery
              </span>
            </div>
          </div>

          {/* Quality Specification Tier */}
          <div className="space-y-1.5">
            <label className="text-slate-300 font-semibold block text-[11px]">
              Select Finish & Structural Specification Tier:
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: 'STANDARD', label: 'Standard', desc: 'Vitrified tiles, CPVC, premium emulsion' },
                { id: 'PREMIUM', label: 'Premium (+25%)', desc: 'Italian marble, teak frames, VRV AC' },
                { id: 'LUXURY', label: 'Luxury (+60%)', desc: 'Full smart automation, imported stone' }
              ].map((t) => (
                <button
                  type="button"
                  key={t.id}
                  onClick={() => setQualityTier(t.id)}
                  className={`p-2.5 rounded-lg border text-left transition-all ${
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

          {/* Mandatory Professional Acknowledgements (Delta Spec §12) */}
          <div className="p-3 rounded-lg bg-amber-950/20 border border-amber-800/40 space-y-2.5">
            <div className="flex items-center gap-1.5 text-amber-400 font-semibold text-xs">
              <ShieldAlert className="w-3.5 h-3.5" />
              <span>Mandatory Professional Delivery Acknowledgements</span>
            </div>

            <div className="space-y-2 text-[11px] text-slate-300">
              <label className="flex items-start gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={ackDelivery}
                  onChange={(e) => setAckDelivery(e.target.checked)}
                  className="mt-0.5 accent-emerald-500"
                />
                <span>
                  <strong>Professional Delivery Request:</strong> I understand that clicking "Request Build" submits this model for professional structural, MEP, and statutory verification, and does not grant instant autonomous construction permission.
                </span>
              </label>

              <label className="flex items-start gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={ackSiteVerification}
                  onChange={(e) => setAckSiteVerification(e.target.checked)}
                  className="mt-0.5 accent-emerald-500"
                />
                <span>
                  <strong>Site Verification & Geotechnical Gate:</strong> I acknowledge that plot boundary confirmation and soil investigation (Gate G0/G5) are mandatory prior to foundation release.
                </span>
              </label>

              <label className="flex items-start gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={ackPermits}
                  onChange={(e) => setAckPermits(e.target.checked)}
                  className="mt-0.5 accent-emerald-500"
                />
                <span>
                  <strong>Statutory Municipal Permits:</strong> I agree that official building sanction will be handled under Mumbai MCGM DCPR 2034 by the licensed architect-of-record.
                </span>
              </label>

              <label className="flex items-start gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={ackChangeOrders}
                  onChange={(e) => setAckChangeOrders(e.target.checked)}
                  className="mt-0.5 accent-emerald-500"
                />
                <span>
                  <strong>Immutable Versioning & Change Orders:</strong> Once frozen, field modifications will require a formal change order with recalculated BOQ and engineering approval.
                </span>
              </label>
            </div>
          </div>

          {/* Submit Action */}
          <div className="pt-2 flex items-center justify-end gap-2 border-t border-white/10">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-1.5 rounded-lg text-slate-400 hover:text-white text-xs transition-colors"
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={!allChecked || isLocking}
              className="px-4 py-2 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-bold shadow-lg shadow-emerald-600/30 flex items-center gap-1.5 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Lock className="w-3.5 h-3.5" />
              <span>{isLocking ? "Hashing & Locking Release..." : "Confirm & Lock Release"}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
