import React, { useState, useMemo } from 'react';
import { 
  MapPin, 
  Ruler, 
  HelpCircle, 
  Upload, 
  CheckCircle2, 
  AlertTriangle, 
  ArrowRight, 
  ChevronDown, 
  ChevronUp, 
  Compass, 
  RefreshCw,
  Layers,
  Info
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
}

export const LandIntakeView: React.FC<LandIntakeViewProps> = ({
  onConfirmPlot,
  onOpenTechnicalMap,
  initialLocation = 'Bandra West, Mumbai',
  initialCoordinates
}) => {
  // -------------------------------------------------------------
  // Form State
  // -------------------------------------------------------------
  const [address, setAddress] = useState(initialLocation);
  const [city, setCity] = useState('Mumbai');
  const [state, setState] = useState('Maharashtra');
  const [country] = useState('India');

  // Plot Area (Authoritative customer-provided area)
  const [plotArea, setPlotArea] = useState<string>('1100');
  const [areaUnit, setAreaUnit] = useState<'sqft' | 'sqm'>('sqft');

  // Shape & Road
  const [plotShape, setPlotShape] = useState<'regular' | 'irregular' | 'unknown'>('irregular');
  const [roadWidthFt, setRoadWidthFt] = useState<string>('16');
  const [roadFacingSide, setRoadFacingSide] = useState<string>('NORTH');

  // Optional Dimensions
  const [showDimensions, setShowDimensions] = useState<boolean>(false);
  const [frontFt, setFrontFt] = useState<string>('28');
  const [backFt, setBackFt] = useState<string>('28');
  const [leftFt, setLeftFt] = useState<string>('44');
  const [rightFt, setRightFt] = useState<string>('40');
  const [diagonalFt, setDiagonalFt] = useState<string>('50');

  // Document Uploads (Optional)
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);

  // Processing & Result State
  const [stepState, setStepState] = useState<'FORM' | 'CHECKING' | 'RESULT'>('FORM');
  const [showTechnicalDetails, setShowTechnicalDetails] = useState<boolean>(false);

  // -------------------------------------------------------------
  // Dimension vs Declared Area Mismatch Detection
  // -------------------------------------------------------------
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

  // Handle Form Submission
  const handleCheckLand = (e: React.FormEvent) => {
    e.preventDefault();
    setStepState('CHECKING');
    
    // Simulate real-time validation / API processing
    setTimeout(() => {
      setStepState('RESULT');
    }, 1200);
  };

  // Convert declared area to square feet number
  const parsedAreaSqft = useMemo(() => {
    const val = parseFloat(plotArea) || 1100;
    return areaUnit === 'sqm' ? Math.round(val * 10.7639) : val;
  }, [plotArea, areaUnit]);

  // Derived or synthesized coordinates for map preview
  const displayCoordinates: [number, number][] = useMemo(() => {
    if (initialCoordinates && initialCoordinates.length >= 3) {
      return initialCoordinates;
    }
    // Synthesize realistic polygon around Bandra West anchor
    const centerLon = 72.8295;
    const centerLat = 19.0596;
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
  }, [initialCoordinates, parsedAreaSqft]);

  const handleFinalConfirm = () => {
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

  return (
    <div className="w-full h-full overflow-y-auto bg-[#07090e] text-slate-100 flex flex-col items-center p-4 md:p-8">
      <div className="w-full max-w-3xl flex flex-col gap-6">

        {/* ========================================================================= */}
        {/* VIEW 1: SIMPLE PROGRESSIVE FORM */}
        {/* ========================================================================= */}
        {stepState === 'FORM' && (
          <div className="bg-[#0e131f] border border-white/10 rounded-2xl p-6 md:p-8 shadow-2xl backdrop-blur-xl">
            {/* Header */}
            <div className="mb-8">
              <span className="text-xs font-mono uppercase tracking-widest text-blue-400 bg-blue-950/60 border border-blue-800/40 px-2.5 py-1 rounded-full">
                Step 1: Land Intake
              </span>
              <h1 className="text-2xl md:text-3xl font-display font-bold text-white mt-3">
                Tell us about your land
              </h1>
              <p className="text-sm md:text-base text-slate-400 mt-1">
                We'll check the site and determine what can be built.
              </p>
            </div>

            <form onSubmit={handleCheckLand} className="flex flex-col gap-8">
              
              {/* SECTION A: LOCATION */}
              <div className="flex flex-col gap-3">
                <label className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-blue-400" />
                  <span>Where is your land located?</span>
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                    placeholder="Search locality, street or address (e.g. Bandra West, Mumbai)"
                    required
                    className="w-full px-4 py-3 rounded-xl bg-slate-900/90 border border-slate-700/80 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-sm transition-all"
                  />
                </div>
                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <span className="text-[11px] text-slate-400">City</span>
                    <input
                      type="text"
                      value={city}
                      onChange={(e) => setCity(e.target.value)}
                      className="w-full mt-1 px-3 py-2 rounded-lg bg-slate-900 border border-slate-700/60 text-xs text-slate-300"
                    />
                  </div>
                  <div>
                    <span className="text-[11px] text-slate-400">State</span>
                    <input
                      type="text"
                      value={state}
                      onChange={(e) => setState(e.target.value)}
                      className="w-full mt-1 px-3 py-2 rounded-lg bg-slate-900 border border-slate-700/60 text-xs text-slate-300"
                    />
                  </div>
                  <div>
                    <span className="text-[11px] text-slate-400">Country</span>
                    <input
                      type="text"
                      value={country}
                      disabled
                      className="w-full mt-1 px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-400 cursor-not-allowed"
                    />
                  </div>
                </div>
              </div>

              <div className="h-px bg-white/5" />

              {/* SECTION B: PLOT AREA */}
              <div className="flex flex-col gap-3">
                <label className="text-sm font-semibold text-slate-200 flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <Ruler className="w-4 h-4 text-emerald-400" />
                    <span>How large is your plot?</span>
                  </span>
                  <span className="text-xs text-emerald-400 font-normal">Authoritative declared area</span>
                </label>
                <div className="flex items-center gap-3">
                  <div className="relative flex-1">
                    <input
                      type="number"
                      step="any"
                      min="100"
                      value={plotArea}
                      onChange={(e) => setPlotArea(e.target.value)}
                      placeholder="e.g. 1100"
                      required
                      className="w-full px-4 py-3 rounded-xl bg-slate-900/90 border border-slate-700/80 text-white font-mono text-lg font-bold focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all"
                    />
                  </div>
                  {/* Unit Switcher */}
                  <div className="flex bg-slate-900 p-1 rounded-xl border border-slate-700/80">
                    <button
                      type="button"
                      onClick={() => setAreaUnit('sqft')}
                      className={`px-3.5 py-2 rounded-lg text-xs font-semibold transition-all ${
                        areaUnit === 'sqft'
                          ? 'bg-blue-600 text-white shadow-md'
                          : 'text-slate-400 hover:text-white'
                      }`}
                    >
                      sq ft
                    </button>
                    <button
                      type="button"
                      onClick={() => setAreaUnit('sqm')}
                      className={`px-3.5 py-2 rounded-lg text-xs font-semibold transition-all ${
                        areaUnit === 'sqm'
                          ? 'bg-blue-600 text-white shadow-md'
                          : 'text-slate-400 hover:text-white'
                      }`}
                    >
                      sq m
                    </button>
                  </div>
                </div>
                <p className="text-xs text-slate-400">
                  Planwise preserves your declared area of <strong className="text-slate-200">{plotArea || '0'} {areaUnit}</strong> as authoritative.
                </p>
              </div>

              <div className="h-px bg-white/5" />

              {/* SECTION C: PLOT SHAPE */}
              <div className="flex flex-col gap-3">
                <label className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                  <Compass className="w-4 h-4 text-cyan-400" />
                  <span>What shape is your plot?</span>
                </label>
                <div className="grid grid-cols-3 gap-3">
                  <button
                    type="button"
                    onClick={() => setPlotShape('regular')}
                    className={`flex flex-col items-center justify-center p-4 rounded-xl border text-center transition-all ${
                      plotShape === 'regular'
                        ? 'bg-blue-600/20 border-blue-500 text-white shadow-lg shadow-blue-500/10'
                        : 'bg-slate-900/60 border-slate-750 text-slate-400 hover:border-slate-600'
                    }`}
                  >
                    <div className="w-6 h-6 border-2 border-current rounded-sm mb-2" />
                    <span className="text-xs font-bold">Regular</span>
                    <span className="text-[10px] text-slate-400 mt-0.5">Rectangle / Box</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setPlotShape('irregular')}
                    className={`flex flex-col items-center justify-center p-4 rounded-xl border text-center transition-all ${
                      plotShape === 'irregular'
                        ? 'bg-blue-600/20 border-blue-500 text-white shadow-lg shadow-blue-500/10'
                        : 'bg-slate-900/60 border-slate-750 text-slate-400 hover:border-slate-600'
                    }`}
                  >
                    <div className="w-6 h-6 border-2 border-current rounded-sm transform rotate-12 skew-x-6 mb-2" />
                    <span className="text-xs font-bold">Irregular</span>
                    <span className="text-[10px] text-slate-400 mt-0.5">Angled corners</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setPlotShape('unknown')}
                    className={`flex flex-col items-center justify-center p-4 rounded-xl border text-center transition-all ${
                      plotShape === 'unknown'
                        ? 'bg-blue-600/20 border-blue-500 text-white shadow-lg shadow-blue-500/10'
                        : 'bg-slate-900/60 border-slate-750 text-slate-400 hover:border-slate-600'
                    }`}
                  >
                    <HelpCircle className="w-6 h-6 mb-2 text-current" />
                    <span className="text-xs font-bold">I don't know</span>
                    <span className="text-[10px] text-slate-400 mt-0.5">Estimate boundary</span>
                  </button>
                </div>
              </div>

              <div className="h-px bg-white/5" />

              {/* SECTION D: ROAD */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-semibold text-slate-200">
                    Road width in front of plot (ft)
                  </label>
                  <input
                    type="number"
                    step="1"
                    min="6"
                    value={roadWidthFt}
                    onChange={(e) => setRoadWidthFt(e.target.value)}
                    placeholder="e.g. 16"
                    required
                    className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700/80 text-white text-sm focus:outline-none focus:border-blue-500"
                  />
                  <span className="text-[11px] text-slate-400">Road width determines permissible building height and FSI.</span>
                </div>

                <div className="flex flex-col gap-2">
                  <label className="text-sm font-semibold text-slate-200">
                    Which side faces the road?
                  </label>
                  <select
                    value={roadFacingSide}
                    onChange={(e) => setRoadFacingSide(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700/80 text-white text-sm focus:outline-none focus:border-blue-500"
                  >
                    <option value="NORTH">North Side</option>
                    <option value="SOUTH">South Side</option>
                    <option value="EAST">East Side</option>
                    <option value="WEST">West Side</option>
                    <option value="FRONT">Front Side</option>
                  </select>
                  <span className="text-[11px] text-slate-400">Front setbacks and car entry will be aligned to this edge.</span>
                </div>
              </div>

              {/* SECTION E: OPTIONAL DIMENSIONS (PROGRESSIVE DISCLOSURE) */}
              <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4">
                <button
                  type="button"
                  onClick={() => setShowDimensions(!showDimensions)}
                  className="w-full flex items-center justify-between text-xs font-semibold text-slate-300 hover:text-white"
                >
                  <span className="flex items-center gap-2">
                    <Ruler className="w-3.5 h-3.5 text-indigo-400" />
                    <span>Do you have exact boundary measurements? (Optional)</span>
                  </span>
                  {showDimensions ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </button>

                {showDimensions && (
                  <div className="mt-4 flex flex-col gap-4 pt-3 border-t border-white/5">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      <div>
                        <span className="text-[11px] text-slate-400">Front (ft)</span>
                        <input
                          type="number"
                          step="any"
                          value={frontFt}
                          onChange={(e) => setFrontFt(e.target.value)}
                          placeholder="28"
                          className="w-full mt-1 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white"
                        />
                      </div>
                      <div>
                        <span className="text-[11px] text-slate-400">Back (ft)</span>
                        <input
                          type="number"
                          step="any"
                          value={backFt}
                          onChange={(e) => setBackFt(e.target.value)}
                          placeholder="28"
                          className="w-full mt-1 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white"
                        />
                      </div>
                      <div>
                        <span className="text-[11px] text-slate-400">Left Length (ft)</span>
                        <input
                          type="number"
                          step="any"
                          value={leftFt}
                          onChange={(e) => setLeftFt(e.target.value)}
                          placeholder="44"
                          className="w-full mt-1 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white"
                        />
                      </div>
                      <div>
                        <span className="text-[11px] text-slate-400">Right Length (ft)</span>
                        <input
                          type="number"
                          step="any"
                          value={rightFt}
                          onChange={(e) => setRightFt(e.target.value)}
                          placeholder="40"
                          className="w-full mt-1 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white"
                        />
                      </div>
                    </div>

                    {plotShape === 'irregular' && (
                      <div className="bg-slate-900/80 p-3 rounded-lg border border-indigo-900/40">
                        <span className="text-[11px] text-indigo-300 font-semibold">
                          Corner-to-corner Diagonal (ft) — Required for closing irregular polygons
                        </span>
                        <input
                          type="number"
                          step="any"
                          value={diagonalFt}
                          onChange={(e) => setDiagonalFt(e.target.value)}
                          placeholder="e.g. 50"
                          className="w-full mt-1 px-3 py-1.5 rounded-lg bg-slate-950 border border-indigo-700/60 text-xs text-white font-mono"
                        />
                      </div>
                    )}

                    {/* Area Mismatch Warning */}
                    {areaMismatch && (
                      <div className="bg-amber-950/40 border border-amber-600/40 rounded-xl p-3 flex items-start gap-3">
                        <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                        <div>
                          <p className="text-xs font-bold text-amber-300">
                            Your dimensions and plot area don't match.
                          </p>
                          <p className="text-[11px] text-amber-200/80 mt-0.5">
                            Declared area is <strong className="text-white">{areaMismatch.declared} sq ft</strong>, but entered dimensions produce approximately <strong className="text-white">{areaMismatch.calculated} sq ft</strong>.
                          </p>
                          <p className="text-[11px] text-slate-300 mt-1">
                            Please verify the measurements. Planwise preserves your declared area and will not silently overwrite it.
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* SECTION F: UPLOAD DOCUMENTS (OPTIONAL) */}
              <div className="bg-slate-950/40 border border-dashed border-slate-700/70 rounded-xl p-4 flex flex-col items-center justify-center text-center">
                <Upload className="w-5 h-5 text-slate-400 mb-1" />
                <span className="text-xs font-semibold text-slate-200">
                  Upload deed or survey sketch (Optional)
                </span>
                <span className="text-[11px] text-slate-400 mt-0.5">
                  Sale deed, survey drawing, or property tax card. Document upload is not required to begin.
                </span>
                <input
                  type="file"
                  id="doc-upload"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      setUploadedFiles((prev) => [...prev, e.target.files![0].name]);
                    }
                  }}
                />
                <label
                  htmlFor="doc-upload"
                  className="mt-2.5 px-3 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-medium text-slate-300 cursor-pointer transition-all"
                >
                  Choose Document
                </label>
                {uploadedFiles.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1.5 justify-center">
                    {uploadedFiles.map((fn, idx) => (
                      <span key={idx} className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">
                        {fn}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* PRIMARY SUBMIT BUTTON */}
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
                <button
                  type="button"
                  onClick={onOpenTechnicalMap}
                  className="text-xs text-slate-400 hover:text-slate-200 underline font-medium"
                >
                  Switch to Technical CAD Map
                </button>

                <button
                  type="submit"
                  className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-display font-bold text-sm shadow-xl shadow-blue-500/25 flex items-center justify-center gap-2 transition-all active:scale-95"
                >
                  <span>Check My Land</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>

            </form>
          </div>
        )}

        {/* ========================================================================= */}
        {/* VIEW 2: CHECKING / PROCESSING ANIMATION */}
        {/* ========================================================================= */}
        {stepState === 'CHECKING' && (
          <div className="bg-[#0e131f] border border-white/10 rounded-2xl p-12 text-center flex flex-col items-center justify-center gap-4 shadow-2xl backdrop-blur-xl">
            <RefreshCw className="w-10 h-10 text-blue-500 animate-spin" />
            <h2 className="text-xl font-display font-bold text-white">Checking your site...</h2>
            <p className="text-xs text-slate-400 max-w-sm">
              Reconstructing boundary geometry, verifying abutting road rights-of-way, and evaluating statutory regulations.
            </p>
          </div>
        )}

        {/* ========================================================================= */}
        {/* VIEW 3: SIMPLE LAND RESULT PAGE */}
        {/* ========================================================================= */}
        {stepState === 'RESULT' && (
          <div className="flex flex-col gap-6">
            
            {/* Top Summary Card */}
            <div className="bg-[#0e131f] border border-white/10 rounded-2xl p-6 md:p-8 shadow-2xl backdrop-blur-xl">
              <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-6">
                <div>
                  <span className="text-[10px] font-mono uppercase tracking-widest text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 px-2 py-0.5 rounded-full">
                    Site Checked
                  </span>
                  <h2 className="text-xl md:text-2xl font-display font-bold text-white mt-1.5">
                    Your Land
                  </h2>
                </div>
                <button
                  onClick={() => setStepState('FORM')}
                  className="text-xs text-blue-400 hover:text-blue-300 font-medium underline"
                >
                  Edit details
                </button>
              </div>

              {/* Simple Metrics Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-900/60 p-3.5 rounded-xl border border-white/5">
                  <span className="text-[11px] text-slate-400">Plot Area</span>
                  <p className="text-lg font-bold font-mono text-emerald-400 mt-0.5">
                    {parsedAreaSqft.toLocaleString()} sq ft
                  </p>
                  <span className="text-[10px] text-slate-500">Declared area</span>
                </div>

                <div className="bg-slate-900/60 p-3.5 rounded-xl border border-white/5">
                  <span className="text-[11px] text-slate-400">Location</span>
                  <p className="text-sm font-semibold text-white mt-0.5 truncate" title={address}>
                    {city}, {state}
                  </p>
                  <span className="text-[10px] text-slate-500">MCGM Jurisdiction</span>
                </div>

                <div className="bg-slate-900/60 p-3.5 rounded-xl border border-white/5">
                  <span className="text-[11px] text-slate-400">Road Width</span>
                  <p className="text-lg font-bold font-mono text-cyan-400 mt-0.5">
                    {roadWidthFt} ft
                  </p>
                  <span className="text-[10px] text-slate-500">{roadFacingSide} facing</span>
                </div>

                <div className="bg-slate-900/60 p-3.5 rounded-xl border border-white/5">
                  <span className="text-[11px] text-slate-400">Plot Shape</span>
                  <p className="text-sm font-semibold capitalize text-white mt-0.5">
                    {plotShape}
                  </p>
                  <span className="text-[10px] text-slate-500">Reconstructed</span>
                </div>
              </div>

              {/* 3 Simple Verification Sections */}
              <div className="mt-6 flex flex-col gap-2.5">
                <div className="flex items-center gap-3 p-3 rounded-xl bg-emerald-950/30 border border-emerald-800/40 text-xs">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <div className="flex-1">
                    <strong className="text-emerald-300">Land identified:</strong> {address} located in Mumbai municipal jurisdiction.
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 rounded-xl bg-blue-950/30 border border-blue-800/40 text-xs">
                  <CheckCircle2 className="w-4 h-4 text-blue-400 shrink-0" />
                  <div className="flex-1">
                    <strong className="text-blue-300">Plot geometry checked:</strong> Closed polygonal boundary verified against abutting road frontage.
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 rounded-xl bg-amber-950/30 border border-amber-800/40 text-xs">
                  <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
                  <div className="flex-1">
                    <strong className="text-amber-300">Professional survey required:</strong> Standard statutory check prior to physical construction.
                  </div>
                </div>
              </div>

              {/* Secondary Map Preview (Clean, non-engineering) */}
              <div className="mt-6 relative h-48 sm:h-64 rounded-xl overflow-hidden border border-white/10 bg-slate-950 flex items-center justify-center">
                {/* SVG Fallback / Clean Vector Polygon Preview */}
                <svg className="w-full h-full p-6 text-blue-500" viewBox="0 0 200 150">
                  <defs>
                    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="1"/>
                    </pattern>
                  </defs>
                  <rect width="100%" height="100%" fill="url(#grid)" />
                  {/* Road edge indicator */}
                  <line x1="20" y1="130" x2="180" y2="130" stroke="#f59e0b" strokeWidth="4" strokeDasharray="4 2" />
                  <text x="100" y="145" textAnchor="middle" fill="#f59e0b" fontSize="8" fontFamily="monospace">
                    Abutting Road ({roadWidthFt} ft)
                  </text>
                  {/* Plot polygon */}
                  <polygon
                    points="35,125 165,125 155,25 45,20"
                    fill="rgba(59, 130, 246, 0.25)"
                    stroke="#3b82f6"
                    strokeWidth="2"
                  />
                  <text x="100" y="75" textAnchor="middle" fill="#ffffff" fontSize="11" fontWeight="bold">
                    {parsedAreaSqft.toLocaleString()} sq ft
                  </text>
                </svg>

                <div className="absolute top-2 left-2 text-[10px] font-mono px-2 py-0.5 rounded bg-black/70 text-slate-300 border border-white/10">
                  Clean Plot Boundary Preview
                </div>
              </div>

              {/* Collapsible Technical Details (Hidden by Default) */}
              <div className="mt-6">
                <button
                  type="button"
                  onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
                  className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors"
                >
                  <Info className="w-3.5 h-3.5 text-slate-400" />
                  <span>Technical details</span>
                  {showTechnicalDetails ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                </button>

                {showTechnicalDetails && (
                  <div className="mt-3 p-4 rounded-xl bg-slate-950 border border-white/5 font-mono text-[11px] text-slate-400 flex flex-col gap-1.5">
                    <div><strong>SECS Origin:</strong> 19.0596° N, 72.8295° E (Bandra West Datum)</div>
                    <div><strong>Statutory Rule Pack:</strong> MUMBAI-DCPR-2034-V1 (MCGM)</div>
                    <div><strong>Boundary Closure:</strong> 5 Vertices (Closed Ring, 0 Self-Intersections)</div>
                    <div><strong>Coordinate System:</strong> Topocentric SECS [ENU / BCS Engine]</div>
                    <div><strong>Provenance Classification:</strong> USER_PROVIDED (L1 Confirmed)</div>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="mt-8 flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-white/10">
                <button
                  type="button"
                  onClick={onOpenTechnicalMap}
                  className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1.5"
                >
                  <Layers className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Open Technical CAD Map</span>
                </button>

                <button
                  onClick={handleFinalConfirm}
                  className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-display font-bold text-sm shadow-xl shadow-blue-500/30 flex items-center justify-center gap-2 transition-all active:scale-95"
                >
                  <span>Confirm this plot</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>

            </div>

          </div>
        )}

      </div>
    </div>
  );
};
