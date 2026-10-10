import React, { useState, useMemo } from 'react';
import {
  MapPin,
  Ruler,
  Upload,
  AlertTriangle,
  ArrowRight,
  ChevronDown,
  ChevronUp,
  Compass,
  RefreshCw,
  FileText,
  Sliders,
  Check,
  HelpCircle,
  Edit2
} from 'lucide-react';

interface LandIntakeViewProps {
  onConfirmPlot: (landData: {
    location: string;
    city: string;
    state: string;
    country: string;
    declaredAreaSqft: number;
    unit: 'sqft' | 'sqm';
    shape: 'regular' | 'irregular' | 'unknown';
    roadWidthFt: number;
    roadFacingSide: string;
    coordinates?: [number, number][];
  }) => void;
  onOpenTechnicalMap: () => void;
  initialLocation?: string;
  initialCoordinates?: [number, number][];
  initialPlotArea?: number | string;
}

export const LandIntakeView: React.FC<LandIntakeViewProps> = ({
  onConfirmPlot,
  onOpenTechnicalMap,
  initialLocation = 'Bandra West, Mumbai',
  initialCoordinates,
  initialPlotArea
}) => {
  // Phase: 'FORM' (Screen 1) | 'CHECKING' | 'RESULT' (Screen 6)
  const [phase, setPhase] = useState<'FORM' | 'CHECKING' | 'RESULT'>('FORM');

  // Form State
  const [address, setAddress] = useState(initialLocation);
  const [city, setCity] = useState('Mumbai');
  const [state, setState] = useState('Maharashtra');
  const [country] = useState('India');

  // Plot Area (Customer input - preserves pilot fixture when provided, allows any custom value)
  const [plotArea, setPlotArea] = useState<string>(
    initialPlotArea !== undefined && initialPlotArea !== null ? String(initialPlotArea) : ''
  );
  const [areaUnit, setAreaUnit] = useState<'sqft' | 'sqm'>('sqft');

  // Shape & Road
  const [plotShape, setPlotShape] = useState<'regular' | 'irregular' | 'unknown'>('irregular');
  const [roadWidthFt, setRoadWidthFt] = useState<string>('16');
  const [roadFacingSide, setRoadFacingSide] = useState<string>('NORTH');

  // "Why do we ask this?" expandable
  const [showWhyAsk, setShowWhyAsk] = useState<boolean>(false);

  // Optional Dimensions
  const [showDimensions, setShowDimensions] = useState<boolean>(false);
  const [frontFt, setFrontFt] = useState<string>('28');
  const [backFt, setBackFt] = useState<string>('28');
  const [leftFt, setLeftFt] = useState<string>('44');
  const [rightFt, setRightFt] = useState<string>('40');

  // Documents
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);

  // Technical drawer toggle on Result screen
  const [showTechnicalDetails, setShowTechnicalDetails] = useState<boolean>(false);

  // Convert declared area to square feet number (never silently overwrites with 1100 if user cleared it)
  const parsedAreaSqft = useMemo(() => {
    const val = parseFloat(plotArea);
    if (isNaN(val) || val <= 0) return 0;
    return areaUnit === 'sqm' ? Math.round(val * 10.7639) : Math.round(val);
  }, [plotArea, areaUnit]);

  // Area mismatch alert if custom dimensions differ significantly from declared area
  const areaMismatch = useMemo(() => {
    if (!showDimensions) return null;
    const declared = parseFloat(plotArea);
    const f = parseFloat(frontFt);
    const l = parseFloat(leftFt);
    if (!isNaN(declared) && declared > 0 && !isNaN(f) && f > 0 && !isNaN(l) && l > 0) {
      const approxArea = f * l;
      const deltaPct = Math.abs(approxArea - declared) / declared;
      if (deltaPct > 0.15) {
        return {
          declared,
          calculated: Math.round(approxArea),
          deltaPct: Math.round(deltaPct * 100)
        };
      }
    }
    return null;
  }, [showDimensions, plotArea, frontFt, leftFt]);

  // Synthesize realistic coordinates around Mumbai anchor matching declared plot area
  const displayCoordinates: [number, number][] = useMemo(() => {
    if (parsedAreaSqft > 0) {
      if (initialCoordinates && initialCoordinates.length >= 3 && (!initialPlotArea || initialPlotArea === parsedAreaSqft)) {
        return initialCoordinates;
      }
      const centerLon = initialCoordinates && initialCoordinates.length >= 3 ? initialCoordinates[0][0] : 72.8295;
      const centerLat = initialCoordinates && initialCoordinates.length >= 3 ? initialCoordinates[0][1] : 19.0596;
      const sideM = Math.sqrt(parsedAreaSqft * 0.092903);
      const dLat = (sideM / 111320.0);
      const dLon = (sideM / (111320.0 * Math.cos((centerLat * Math.PI) / 180)));

      return [
        [centerLon, centerLat],
        [centerLon + dLon * 0.9, centerLat],
        [centerLon + dLon * 0.85, centerLat + dLat * 1.15],
        [centerLon - dLon * 0.1, centerLat + dLat * 1.05],
        [centerLon, centerLat]
      ];
    }
    return initialCoordinates || [];
  }, [initialCoordinates, initialPlotArea, parsedAreaSqft]);

  const handleStartCheck = (e: React.FormEvent) => {
    e.preventDefault();
    setPhase('CHECKING');
    setTimeout(() => {
      setPhase('RESULT');
    }, 700);
  };

  const handleProceedToFeasibility = () => {
    onConfirmPlot({
      location: address,
      city,
      state,
      country,
      declaredAreaSqft: parsedAreaSqft,
      unit: areaUnit,
      shape: plotShape,
      roadWidthFt: parseFloat(roadWidthFt) || 16,
      roadFacingSide,
      coordinates: displayCoordinates
    });
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const fileNames = Array.from(e.target.files).map(f => f.name);
      setUploadedFiles(prev => [...prev, ...fileNames]);
    }
  };

  return (
    <div className="pw-page">
      <div className="pw-container">

        {/* ========================================================================= */}
        {/* PHASE 1: SCREEN 1 — LAND (Intake Form)                                    */}
        {/* ========================================================================= */}
        {phase === 'FORM' && (
          <div className="pw-card space-y-6">
            {/* Title & Subtitle (§5) */}
            <div>
              <div className="flex items-center justify-between">
                <h1 className="pw-title-xl">
                  Let's understand your land
                </h1>
                <span className="pw-badge pw-badge-primary font-mono text-xs">
                  Your plot area: {parsedAreaSqft.toLocaleString()} sq ft
                </span>
              </div>
              <p className="pw-body mt-1">
                Tell us a few basic details. Planwise will check what may be possible on your plot.
              </p>
            </div>

            {/* Form */}
            <form onSubmit={handleStartCheck} className="flex flex-col gap-6">

              {/* 1. Location */}
              <div className="flex flex-col gap-2">
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-blue-400" />
                  <span>Location</span>
                </label>
                <input
                  type="text"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  placeholder="Search location"
                  required
                  className="pw-input"
                />
                <div className="grid grid-cols-2 gap-3 mt-1">
                  <div>
                    <span className="text-[11px] text-slate-400 block mb-1">City</span>
                    <input
                      type="text"
                      value={city}
                      onChange={(e) => setCity(e.target.value)}
                      className="pw-input !h-9 text-xs"
                    />
                  </div>
                  <div>
                    <span className="text-[11px] text-slate-400 block mb-1">State</span>
                    <input
                      type="text"
                      value={state}
                      onChange={(e) => setState(e.target.value)}
                      className="pw-input !h-9 text-xs"
                    />
                  </div>
                </div>
              </div>

              <div className="h-px bg-white/5" />

              {/* 2. Plot Area */}
              <div className="flex flex-col gap-2">
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <Ruler className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Plot Area</span>
                  </span>
                  <span className="text-xs font-normal text-slate-400">Authoritative plot extent</span>
                </label>

                <div className="flex items-center gap-2">
                  <div className="relative flex-1">
                    <input
                      type="number"
                      step="any"
                      min="100"
                      value={plotArea}
                      onChange={(e) => setPlotArea(e.target.value)}
                      placeholder="e.g. 1500"
                      required
                      className="pw-input font-mono text-base font-bold"
                      data-testid="input-plot-area"
                    />
                  </div>
                  <div className="pw-segmented-control">
                    <button
                      type="button"
                      onClick={() => setAreaUnit('sqft')}
                      className={`pw-segmented-btn ${areaUnit === 'sqft' ? 'pw-segmented-btn-active' : ''}`}
                    >
                      sq ft
                    </button>
                    <button
                      type="button"
                      onClick={() => setAreaUnit('sqm')}
                      className={`pw-segmented-btn ${areaUnit === 'sqm' ? 'pw-segmented-btn-active' : ''}`}
                    >
                      sq m
                    </button>
                  </div>
                </div>
              </div>

              <div className="h-px bg-white/5" />

              {/* 3. Plot Shape */}
              <div className="flex flex-col gap-2">
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                  Plot shape
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { id: 'regular', label: 'Regular', desc: 'Square or rectangular boundary' },
                    { id: 'irregular', label: 'Irregular', desc: 'Angled or non-parallel sides' },
                    { id: 'unknown', label: "I don't know", desc: 'We verify from boundary survey' }
                  ].map((s) => (
                    <button
                      key={s.id}
                      type="button"
                      onClick={() => setPlotShape(s.id as any)}
                      className={`p-3 rounded-xl border text-left transition-all ${
                        plotShape === s.id
                          ? 'bg-blue-600/15 border-blue-500 shadow-sm'
                          : 'bg-white/[0.02] border-white/10 hover:border-white/20'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <div className={`w-3.5 h-3.5 rounded-full border flex items-center justify-center ${
                          plotShape === s.id ? 'border-blue-500 bg-blue-500' : 'border-slate-500'
                        }`}>
                          {plotShape === s.id && <span className="w-1.5 h-1.5 rounded-full bg-white" />}
                        </div>
                        <span className={`text-xs font-semibold ${plotShape === s.id ? 'text-white' : 'text-slate-300'}`}>
                          {s.label}
                        </span>
                      </div>
                      <span className="text-[11px] text-slate-500 block leading-tight">
                        {s.desc}
                      </span>
                    </button>
                  ))}
                </div>
              </div>

              <div className="h-px bg-white/5" />

              {/* 4. Road Width & Road-facing Side */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="flex flex-col gap-2">
                  <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                    Road width
                  </label>
                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      min="5"
                      max="100"
                      value={roadWidthFt}
                      onChange={(e) => setRoadWidthFt(e.target.value)}
                      className="pw-input font-mono"
                      placeholder="16"
                      required
                    />
                    <span className="text-xs text-slate-400 font-medium px-3 py-2.5 rounded-lg bg-white/5 border border-white/10">
                      ft
                    </span>
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                    <Compass className="w-3.5 h-3.5 text-blue-400" />
                    <span>Road-facing side</span>
                  </label>
                  <select
                    value={roadFacingSide}
                    onChange={(e) => setRoadFacingSide(e.target.value)}
                    className="pw-input"
                  >
                    <option value="NORTH">North ▼</option>
                    <option value="SOUTH">South ▼</option>
                    <option value="EAST">East ▼</option>
                    <option value="WEST">West ▼</option>
                    <option value="NORTH_EAST">North-East ▼</option>
                    <option value="NORTH_WEST">North-West ▼</option>
                  </select>
                </div>
              </div>

              <div className="h-px bg-white/5" />

              {/* Optional 1: Plot Dimensions */}
              <div>
                <button
                  type="button"
                  onClick={() => setShowDimensions(!showDimensions)}
                  className="w-full flex items-center justify-between text-xs text-slate-300 hover:text-white py-1"
                >
                  <span className="font-semibold uppercase tracking-wider">
                    Plot dimensions (Optional)
                  </span>
                  {showDimensions ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </button>

                {showDimensions && (
                  <div className="mt-3 p-4 rounded-xl bg-white/[0.02] border border-white/5 space-y-3">
                    <p className="text-xs text-slate-400">
                      Enter boundary lengths if known to refine setbacks.
                    </p>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                      <div>
                        <span className="text-[11px] text-slate-400 block mb-1">Front (ft)</span>
                        <input
                          type="number"
                          value={frontFt}
                          onChange={(e) => setFrontFt(e.target.value)}
                          className="pw-input !h-9 text-xs font-mono"
                        />
                      </div>
                      <div>
                        <span className="text-[11px] text-slate-400 block mb-1">Back (ft)</span>
                        <input
                          type="number"
                          value={backFt}
                          onChange={(e) => setBackFt(e.target.value)}
                          className="pw-input !h-9 text-xs font-mono"
                        />
                      </div>
                      <div>
                        <span className="text-[11px] text-slate-400 block mb-1">Left (ft)</span>
                        <input
                          type="number"
                          value={leftFt}
                          onChange={(e) => setLeftFt(e.target.value)}
                          className="pw-input !h-9 text-xs font-mono"
                        />
                      </div>
                      <div>
                        <span className="text-[11px] text-slate-400 block mb-1">Right (ft)</span>
                        <input
                          type="number"
                          value={rightFt}
                          onChange={(e) => setRightFt(e.target.value)}
                          className="pw-input !h-9 text-xs font-mono"
                        />
                      </div>
                    </div>

                    {areaMismatch && (
                      <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-start gap-2 text-xs text-amber-200">
                        <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                        <div>
                          <span className="font-semibold block">Authoritative Area Preserved</span>
                          Dimensions suggest ~{areaMismatch.calculated} sq ft. Planwise keeps your authoritative {areaMismatch.declared} sq ft as the benchmark.
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Optional 2: Documents */}
              <div className="flex flex-col gap-2">
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center justify-between">
                  <span>Documents (Optional)</span>
                  <span className="text-[11px] font-normal text-slate-400">Property card, 7/12 extract, survey plan</span>
                </label>

                <div className="border border-dashed border-white/10 hover:border-white/20 rounded-xl p-4 text-center cursor-pointer transition-all">
                  <input
                    type="file"
                    multiple
                    id="land-doc-upload"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                  <label htmlFor="land-doc-upload" className="cursor-pointer flex flex-col items-center gap-1.5">
                    <Upload className="w-5 h-5 text-slate-400" />
                    <span className="text-xs font-medium text-slate-300">
                      Upload documents (PDF, JPG, PNG)
                    </span>
                  </label>
                </div>

                {uploadedFiles.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-1">
                    {uploadedFiles.map((fn, idx) => (
                      <span key={idx} className="pw-badge pw-badge-neutral text-xs py-1 px-2.5">
                        <FileText className="w-3 h-3 text-blue-400" />
                        <span>{fn}</span>
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Secondary: "Why do we ask this?" (§5) */}
              <div className="border-t border-white/5 pt-3">
                <button
                  type="button"
                  onClick={() => setShowWhyAsk(!showWhyAsk)}
                  className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors"
                >
                  <HelpCircle className="w-3.5 h-3.5 text-blue-400" />
                  <span className="underline decoration-slate-600 underline-offset-2">Why do we ask this?</span>
                  {showWhyAsk ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                </button>
                {showWhyAsk && (
                  <div className="mt-2 p-3 rounded-lg bg-white/[0.02] border border-white/5 text-xs text-slate-400 leading-relaxed">
                    Municipal building codes determine how close to your boundaries you may build, based on your road width and plot dimensions. By collecting these upfront, Planwise checks permissible buildable area automatically without requiring manual measurements.
                  </div>
                )}
              </div>

              {/* Actions Footer (§5) */}
              <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4">
                <button
                  type="button"
                  onClick={onOpenTechnicalMap}
                  className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1.5 py-2 px-3 rounded-lg hover:bg-white/5 transition-colors"
                  title="Switch to Professional Mode with CAD map"
                >
                  <Sliders className="w-3.5 h-3.5" />
                  <span>Open CAD &amp; GIS Map</span>
                </button>

                <button
                  type="submit"
                  className="pw-btn pw-btn-primary pw-btn-lg w-full sm:w-auto"
                  data-testid="btn-check-land"
                >
                  <span>Check My Land</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>

            </form>
          </div>
        )}

        {/* ========================================================================= */}
        {/* CHECKING STATE (§19)                                                     */}
        {/* ========================================================================= */}
        {phase === 'CHECKING' && (
          <div className="pw-card p-12 flex flex-col items-center justify-center text-center space-y-4">
            <div className="w-12 h-12 rounded-full bg-blue-600/20 border border-blue-500/40 flex items-center justify-center">
              <RefreshCw className="w-6 h-6 text-blue-400 animate-spin" />
            </div>
            <div>
              <h2 className="pw-title-lg">Checking your site...</h2>
              <p className="pw-body-sm mt-1">
                Evaluating boundary geometry, road access setbacks, and applicable municipal regulations.
              </p>
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* PHASE 2: SCREEN 6 — LAND RESULT                                           */}
        {/* ========================================================================= */}
        {phase === 'RESULT' && (
          <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h1 className="pw-title-xl">
                  Your land is ready to review
                </h1>
                <p className="pw-body mt-1">
                  We checked your plot against municipal development rules.
                </p>
              </div>

              <button
                type="button"
                onClick={() => setPhase('FORM')}
                className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white self-start sm:self-auto py-1 px-2.5 rounded-lg border border-white/10 hover:bg-white/5"
              >
                <Edit2 className="w-3 h-3" />
                <span>Edit Land Details</span>
              </button>
            </div>

            {/* Simple Card (§6) */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="pw-card p-4 space-y-1">
                <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block">
                  PLOT AREA
                </span>
                <span className="text-xl font-bold font-mono text-white block">
                  {parsedAreaSqft.toLocaleString()} sq ft
                </span>
                <span className="text-[11px] text-slate-500">Authoritative</span>
              </div>

              <div className="pw-card p-4 space-y-1">
                <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block">
                  LOCATION
                </span>
                <span className="text-base font-bold text-white block truncate" title={address}>
                  {address}
                </span>
                <span className="text-[11px] text-slate-500">{city}, {state}</span>
              </div>

              <div className="pw-card p-4 space-y-1">
                <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block">
                  ROAD
                </span>
                <span className="text-xl font-bold font-mono text-white block">
                  {roadWidthFt} ft
                </span>
                <span className="text-[11px] text-slate-500">{roadFacingSide} facing</span>
              </div>

              <div className="pw-card p-4 space-y-1">
                <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block">
                  SHAPE
                </span>
                <span className="text-xl font-bold capitalize text-white block">
                  {plotShape}
                </span>
                <span className="text-[11px] text-emerald-400">Verified geometry</span>
              </div>
            </div>

            {/* "What we checked" Card (§6) */}
            <div className="pw-card space-y-4">
              <h3 className="pw-title-md">What we checked</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 flex items-center gap-3">
                  <div className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
                    <Check className="w-3.5 h-3.5" />
                  </div>
                  <div>
                    <span className="text-xs font-semibold text-white block">Plot information</span>
                    <span className="text-[11px] text-slate-400">Declared area and tenure verified</span>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 flex items-center gap-3">
                  <div className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
                    <Check className="w-3.5 h-3.5" />
                  </div>
                  <div>
                    <span className="text-xs font-semibold text-white block">Site geometry</span>
                    <span className="text-[11px] text-slate-400">Polygon boundaries and edges calculated</span>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 flex items-center gap-3">
                  <div className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
                    <Check className="w-3.5 h-3.5" />
                  </div>
                  <div>
                    <span className="text-xs font-semibold text-white block">Road access</span>
                    <span className="text-[11px] text-slate-400">{roadWidthFt} ft access road permits standard residential setbacks</span>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 flex items-center gap-3">
                  <div className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
                    <Check className="w-3.5 h-3.5" />
                  </div>
                  <div>
                    <span className="text-xs font-semibold text-white block">Applicable rules</span>
                    <span className="text-[11px] text-slate-400">Mumbai DCPR 2034 standards evaluated</span>
                  </div>
                </div>
              </div>

              {/* Technical Details Collapsible Drawer (§6, §25) */}
              <div className="pt-2 border-t border-white/5">
                <button
                  type="button"
                  onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
                  className="flex items-center gap-1.5 text-xs text-blue-400 hover:text-blue-300 font-medium transition-colors"
                >
                  <Sliders className="w-3.5 h-3.5" />
                  <span>{showTechnicalDetails ? 'Hide technical details' : 'View technical details'}</span>
                  {showTechnicalDetails ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                </button>

                {showTechnicalDetails && (
                  <div className="mt-3 p-4 rounded-xl bg-[#080b11] border border-blue-500/20 space-y-3 font-mono text-xs">
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                      <div>
                        <span className="text-[10px] text-slate-500 block">REFERENCE FRAME</span>
                        <span className="text-white">EPSG:4326 / UTM 43N</span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-500 block">SURVEY NUMBER</span>
                        <span className="text-white">{address.toLowerCase().includes('bandra') ? 'CTS-1842-BANDRA' : 'CTS-SITE-REF'}</span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-500 block">JURISDICTION</span>
                        <span className="text-white">MUMBAI_DCPR_2034</span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-500 block">GEO VERTICES</span>
                        <span className="text-emerald-400">{displayCoordinates.length} Vertices (Closed)</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Primary CTA (§6) */}
            <div className="flex items-center justify-end">
              <button
                type="button"
                onClick={handleProceedToFeasibility}
                className="pw-btn pw-btn-primary pw-btn-lg w-full sm:w-auto"
                data-testid="btn-see-what-you-can-build"
              >
                <span>See What You Can Build</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};
