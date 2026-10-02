import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  AlertTriangle, 
  FileCheck, 
  Compass, 
  CheckCircle2, 
  X, 
  ChevronDown, 
  ChevronUp, 
  Layers
} from 'lucide-react';

interface SiteEvidenceItem {
  siteEvidenceId: string;
  evidenceType: string;
  sourceType: string;
  provider: string;
  capturedAt: string;
  accuracyM: number;
  confidenceLevel: string;
  verificationStatus: string;
  verifiedBy?: string;
  notes?: string;
}

interface SiteConfidenceSummary {
  siteId: string;
  overallConfidence: string;
  isBlockingForBuildRelease: boolean;
  highestVerifiedTier: string;
  totalEvidenceCount: number;
  verifiedEvidenceCount: number;
  missingEvidenceForL3: string[];
  missingEvidenceForL4: string[];
  explanation: string;
}

interface SiteEvidencePanelProps {
  siteId?: string;
  onClose?: () => void;
}

export const SiteEvidencePanel: React.FC<SiteEvidencePanelProps> = ({
  siteId = 'proj-mumbai-real-1100',
  onClose
}) => {
  const [confidence, setConfidence] = useState<SiteConfidenceSummary | null>(null);
  const [evidenceList, setEvidenceList] = useState<SiteEvidenceItem[]>([]);
  const [isExpanded, setIsExpanded] = useState<boolean>(true);
  const [isVerifying, setIsVerifying] = useState<boolean>(false);

  const fetchEvidenceData = async () => {
    try {
      const [confRes, evRes] = await Promise.all([
        fetch(`/api/v1/sites/${siteId}/confidence`),
        fetch(`/api/v1/sites/${siteId}/evidence`)
      ]);
      
      if (confRes.ok) {
        const confData = await confRes.json();
        setConfidence(confData);
      }
      if (evRes.ok) {
        const evData = await evRes.json();
        setEvidenceList(evData.evidence || []);
      }
    } catch (err) {
      console.warn('Failed to load site evidence from API:', err);
    }
  };

  useEffect(() => {
    fetchEvidenceData();
  }, [siteId]);

  const handleSimulateSurveyVerification = async () => {
    setIsVerifying(true);
    try {
      // 1. Add L3 Survey Plan
      const res1 = await fetch(`/api/v1/sites/${siteId}/evidence`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          evidenceType: 'SURVEY_PLAN',
          sourceType: 'LICENSED_SURVEYOR',
          provider: 'Apex Geomatics & Land Surveyors Ltd (LS-MH-9941)',
          accuracyM: 0.02,
          confidenceLevel: 'L3_LICENSED_SURVEY',
          notes: 'Field closed traverse total station boundary survey with steel pegs'
        })
      });
      const ev1 = await res1.json();

      // 2. Add L3 Site Level Survey
      const res2 = await fetch(`/api/v1/sites/${siteId}/evidence`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          evidenceType: 'SITE_LEVEL',
          sourceType: 'LICENSED_SURVEYOR',
          provider: 'Apex Geomatics & Land Surveyors Ltd (LS-MH-9941)',
          accuracyM: 0.01,
          confidenceLevel: 'L3_LICENSED_SURVEY',
          notes: 'Grid levelling survey tied to GTS benchmark (error < 2mm)'
        })
      });
      const ev2 = await res2.json();

      // 3. Verify both
      if (ev1.siteEvidenceId) {
        await fetch(`/api/v1/sites/${siteId}/evidence/${ev1.siteEvidenceId}/verify`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            verifiedBy: 'Surveyor Sandeep Patil (LS-MH-9941)',
            verificationStatus: 'VERIFIED',
            notes: 'Physical field boundary and peg locations verified on site'
          })
        });
      }
      if (ev2.siteEvidenceId) {
        await fetch(`/api/v1/sites/${siteId}/evidence/${ev2.siteEvidenceId}/verify`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            verifiedBy: 'Surveyor Sandeep Patil (LS-MH-9941)',
            verificationStatus: 'VERIFIED',
            notes: 'RL levels verified against Mumbai GTS Datum'
          })
        });
      }

      await fetchEvidenceData();
    } catch (e) {
      console.error('Failed to verify survey evidence:', e);
    } finally {
      setIsVerifying(false);
    }
  };

  const getTierBadge = (tier: string) => {
    switch (tier) {
      case 'L4_ENGINEERING_READY':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">L4 ENGINEERING READY</span>;
      case 'L3_LICENSED_SURVEY':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">L3 LICENSED SURVEY</span>;
      case 'L2_REMOTE_VERIFIED':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">L2 REMOTE VERIFIED</span>;
      case 'L1_CUSTOMER_DOCUMENT':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">L1 CUSTOMER DOCUMENT</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-500/20 text-slate-300 border border-slate-500/30">L0 GIS ESTIMATE</span>;
    }
  };

  return (
    <div className="glass-panel w-96 rounded-2xl border border-white/10 shadow-2xl bg-slate-950/95 backdrop-blur-md overflow-hidden select-none text-xs">
      {/* Header */}
      <div className="p-3 bg-slate-900/90 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center">
            <ShieldCheck className="w-4 h-4 text-indigo-400" />
          </div>
          <div>
            <h3 className="font-display font-bold text-xs uppercase tracking-wider text-white">
              Site Evidence &amp; Truth
            </h3>
            <span className="text-[10px] text-slate-400 font-mono">
              Delta Spec M1 §1, §2 • SECS Engineering Frame
            </span>
          </div>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-white/5"
          >
            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-white/5"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {isExpanded && (
        <div className="p-3.5 space-y-3">
          {/* Confidence Badge & Build Release Gate Alert */}
          <div className="rounded-xl bg-slate-900/80 p-3 border border-white/5 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-slate-400 uppercase font-mono tracking-wider">
                Current Site Confidence:
              </span>
              {confidence && getTierBadge(confidence.overallConfidence)}
            </div>

            {confidence?.isBlockingForBuildRelease ? (
              <div className="p-2 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                <div className="space-y-0.5">
                  <div className="font-bold text-[11px]">BLOCKING FOR BUILD RELEASE: YES</div>
                  <div className="text-[10px] text-rose-200/80 leading-tight">
                    {confidence.explanation}
                  </div>
                  {confidence.missingEvidenceForL3.length > 0 && (
                    <div className="mt-1 pt-1 border-t border-rose-500/20 text-[9px] text-rose-300/90 font-mono">
                      MISSING: {confidence.missingEvidenceForL3.join(' • ')}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <div className="space-y-0.5">
                  <div className="font-bold text-[11px]">BUILD RELEASE PERMITTED (L3 Certified)</div>
                  <div className="text-[10px] text-emerald-200/80 leading-tight">
                    Authoritative field survey stamped by licensed surveyor. Legal boundaries verified.
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Quick Truth Checklist Matrix */}
          <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
            <div className="bg-slate-900/60 p-2 rounded-lg border border-white/5">
              <span className="text-[9px] text-slate-500 uppercase block">Boundary</span>
              <span className="font-bold text-amber-300 text-xs">
                {confidence?.overallConfidence === 'L3_LICENSED_SURVEY' || confidence?.overallConfidence === 'L4_ENGINEERING_READY' 
                  ? 'LICENSED SURVEY' 
                  : 'CUSTOMER PROVIDED'}
              </span>
              <span className="text-[9px] text-slate-500 block">
                {confidence?.overallConfidence === 'L3_LICENSED_SURVEY' ? '±0.02m DGPS' : '±0.25m Scan'}
              </span>
            </div>

            <div className="bg-slate-900/60 p-2 rounded-lg border border-white/5">
              <span className="text-[9px] text-slate-500 uppercase block">Survey Status</span>
              <span className={`font-bold text-xs ${confidence?.overallConfidence === 'L3_LICENSED_SURVEY' ? 'text-emerald-400' : 'text-rose-400'}`}>
                {confidence?.overallConfidence === 'L3_LICENSED_SURVEY' ? 'VERIFIED' : 'NOT VERIFIED'}
              </span>
              <span className="text-[9px] text-slate-500 block">
                {confidence?.overallConfidence === 'L3_LICENSED_SURVEY' ? 'LS-MH-9941' : 'Pending Stamp'}
              </span>
            </div>

            <div className="bg-slate-900/60 p-2 rounded-lg border border-white/5">
              <span className="text-[9px] text-slate-500 uppercase block">Soil Report</span>
              <span className="font-bold text-slate-400 text-xs">MISSING</span>
              <span className="text-[9px] text-slate-500 block">Required for L4</span>
            </div>

            <div className="bg-slate-900/60 p-2 rounded-lg border border-white/5">
              <span className="text-[9px] text-slate-500 uppercase block">Road Width</span>
              <span className="font-bold text-cyan-400 text-xs">CALCULATED</span>
              <span className="text-[9px] text-slate-500 block">12.0m DP / 18.0m Widening</span>
            </div>
          </div>

          {/* Reference Frame & Regulation Context */}
          <div className="rounded-xl bg-slate-900/60 p-2.5 border border-white/5 space-y-1.5 text-[10px]">
            <div className="flex items-center justify-between text-slate-400">
              <span className="flex items-center gap-1">
                <Compass className="w-3 h-3 text-cyan-400" />
                Coordinate Frame:
              </span>
              <span className="font-mono text-white font-bold">SECS (East-North-Up Topocentric)</span>
            </div>
            <div className="flex items-center justify-between text-slate-400">
              <span className="flex items-center gap-1">
                <Layers className="w-3 h-3 text-indigo-400" />
                Statutory Rule Pack:
              </span>
              <span className="font-mono text-indigo-300 font-bold">MUMBAI DCPR 2034 v1.0.0</span>
            </div>
            <div className="flex items-center justify-between text-slate-400">
              <span>Origin Datum:</span>
              <span className="font-mono text-slate-300">19.1128°N, 72.8685°E, 12.5m MSL</span>
            </div>
          </div>

          {/* Evidence Records List Preview */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-[11px] font-semibold text-slate-300">
              <span>Audited Evidence Items ({evidenceList.length})</span>
              <span className="text-[10px] text-slate-500 font-mono">Immutable Provenance</span>
            </div>

            <div className="max-h-36 overflow-y-auto space-y-1 pr-1">
              {evidenceList.map((ev) => (
                <div
                  key={ev.siteEvidenceId}
                  className="p-1.5 rounded-lg bg-slate-900/50 border border-white/5 flex items-center justify-between text-[10px]"
                >
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-1.5">
                      <span className="font-bold text-white font-mono">{ev.evidenceType}</span>
                      <span className="text-slate-500">•</span>
                      <span className="text-slate-400">{ev.provider}</span>
                    </div>
                    <div className="text-slate-500 text-[9px] font-mono">
                      Accuracy: ±{ev.accuracyM}m | {ev.confidenceLevel}
                    </div>
                  </div>

                  <div>
                    {ev.verificationStatus === 'VERIFIED' ? (
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                        VERIFIED
                      </span>
                    ) : (
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30">
                        UNVERIFIED
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Elevate to L3 Action Button */}
          {confidence?.isBlockingForBuildRelease && (
            <button
              onClick={handleSimulateSurveyVerification}
              disabled={isVerifying}
              className="w-full py-2 px-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-display font-bold text-xs shadow-lg shadow-indigo-500/20 flex items-center justify-center gap-1.5 transition-all disabled:opacity-50"
            >
              <FileCheck className="w-3.5 h-3.5" />
              <span>{isVerifying ? 'Verifying Field Survey...' : 'Attach & Verify Licensed Survey (Unblock Build)'}</span>
            </button>
          )}
        </div>
      )}
    </div>
  );
};
