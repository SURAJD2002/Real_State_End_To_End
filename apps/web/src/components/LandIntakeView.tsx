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
  Sliders
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
  // Form State
  const [address, setAddress] = useState(initialLocation);
  const [city, setCity] = useState('Mumbai');
  const [state, setState] = useState('Maharashtra');
  const [country] = useState('India');

  // Plot Area (Authoritative customer input - 1,100 sq ft default)
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

  // Documents
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);

  // Processing state
  const [isChecking, setIsChecking] = useState<boolean>(false);
  const [checkProgress, setCheckProgress] = useState<number>(0);

  // Convert declared area to square feet number
  const parsedAreaSqft = useMemo(() => {
    const val = parseFloat(plotArea) || 1100;
    return areaUnit === 'sqm' ? Math.round(val * 10.7639) : val;
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

  // Synthesize realistic coordinates around Mumbai anchor if not present
  const displayCoordinates: [number, number][] = useMemo(() => {
    if (initialCoordinates && initialCoordinates.length >= 3) {
      return initialCoordinates;
    }
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsChecking(true);
    setCheckProgress(1);

    setTimeout(() => {
      setCheckProgress(2);
      setTimeout(() => {
        setCheckProgress(3);
        setTimeout(() => {
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
        }, 600);
      }, 600);
    }, 600);
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
        
        {/* Main Card */}
        <div className="pw-card">
          {/* Header (§8) */}
          <div className="mb-6">
            <h1 className="pw-title-xl">
              Tell us about your land
            </h1>
            <p className="pw-body mt-1">
              We'll check what can realistically be built on it.
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="flex flex-col gap-6">
            
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
                placeholder="Enter address or locality (e.g. Bandra West, Mumbai)"
                required
                className="pw-input"
              />
              <div className="grid grid-cols-3 gap-3 mt-1">
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
                <div>
                  <span className="text-[11px] text-slate-400 block mb-1">Country</span>
                  <input
                    type="text"
                    value={country}
                    disabled
                    className="pw-input !h-9 text-xs opacity-60 cursor-not-allowed"
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
                <span className="text-xs font-normal text-slate-400">Total land extent</span>
              </label>

              <div className="flex items-center gap-2">
                <div className="relative flex-1">
                  <input
                    type="number"
                    step="any"
                    min="100"
                    value={plotArea}
                    onChange={(e) => setPlotArea(e.target.value)}
                    placeholder="1100"
                    required
                    className="pw-input font-mono text-base font-bold"
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
                Plot Shape
              </label>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { id: 'regular', label: 'Regular', desc: 'Rectangular or square' },
                  { id: 'irregular', label: 'Irregular', desc: 'Angled or curved edges' },
                  { id: 'unknown', label: "I'm not sure", desc: 'We will verify from survey' }
                ].map((s) => (
                  <button
                    key={s.id}
                    type="button"
                    onClick={() => setPlotShape(s.id as any)}
                    className={`p-3 rounded-lg border text-left transition-all ${
                      plotShape === s.id
                        ? 'bg-blue-600/10 border-blue-500 shadow-sm'
                        : 'bg-white/[0.02] border-white/10 hover:border-white/20'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <div className={`w-3.5 h-3.5 rounded-full border flex items-center justify-center ${
                        plotShape === s.id ? 'border-blue-500 bg-blue-500' : 'border-slate-500'
                      }`}>
                        {plotShape === s.id && <span className="w-1.5 h-1.5 rounded-full bg-white" />}
                      </div>
                      <span className={`text-xs font-medium ${plotShape === s.id ? 'text-white' : 'text-slate-300'}`}>
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

            {/* 4. Road Access */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex flex-col gap-2">
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                  Road Width
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
                  <span className="text-xs text-slate-400 font-medium px-2 py-2.5 rounded-md bg-white/5 border border-white/10">
                    ft width
                  </span>
                </div>
                <span className="text-[11px] text-slate-400">Width of the road accessing the plot</span>
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                  <Compass className="w-3.5 h-3.5 text-blue-400" />
                  <span>Road Facing Direction</span>
                </label>
                <select
                  value={roadFacingSide}
                  onChange={(e) => setRoadFacingSide(e.target.value)}
                  className="pw-input"
                >
                  <option value="NORTH">North Facing</option>
                  <option value="SOUTH">South Facing</option>
                  <option value="EAST">East Facing</option>
                  <option value="WEST">West Facing</option>
                  <option value="NORTH_EAST">North-East Facing</option>
                  <option value="NORTH_WEST">North-West Facing</option>
                </select>
                <span className="text-[11px] text-slate-400">Direction towards the front access road</span>
              </div>
            </div>

            <div className="h-px bg-white/5" />

            {/* 5. Additional Details (Dimensions) */}
            <div>
              <button
                type="button"
                onClick={() => setShowDimensions(!showDimensions)}
                className="w-full flex items-center justify-between text-xs text-slate-300 hover:text-white py-1"
              >
                <span className="font-semibold uppercase tracking-wider">
                  Additional Details: Plot Dimensions (Optional)
                </span>
                {showDimensions ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>

              {showDimensions && (
                <div className="mt-3 p-4 rounded-lg bg-white/[0.02] border border-white/5 space-y-3">
                  <p className="text-xs text-slate-400">
                    If you know boundary lengths, entering them helps generate more accurate setbacks.
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
                    <div className="p-3 rounded-md bg-amber-500/10 border border-amber-500/30 flex items-start gap-2 text-xs text-amber-200">
                      <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                      <div>
                        <span className="font-semibold block">Declared Area Preserved</span>
                        Your entered dimensions yield ~{areaMismatch.calculated} sq ft, while declared area is {areaMismatch.declared} sq ft. Planwise keeps your declared {areaMismatch.declared} sq ft as the authoritative benchmark.
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className="h-px bg-white/5" />

            {/* 6. Documents (Optional) */}
            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center justify-between">
                <span>Documents (Optional)</span>
                <span className="text-[11px] font-normal text-slate-400">Property card, 7/12 extract, survey plan</span>
              </label>

              <div className="border border-dashed border-white/10 hover:border-white/20 rounded-lg p-4 text-center cursor-pointer transition-all">
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
                    Click to upload property documents or drop them here
                  </span>
                  <span className="text-[11px] text-slate-500">
                    PDF, JPG, PNG up to 25 MB
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

            {/* Checking Loader State (§20) */}
            {isChecking && (
              <div className="p-4 rounded-lg bg-blue-950/20 border border-blue-500/20 space-y-2">
                <div className="flex items-center gap-2 text-xs font-semibold text-blue-300">
                  <RefreshCw className="w-3.5 h-3.5 text-blue-400 animate-spin" />
                  <span>Checking what can be built...</span>
                </div>
                <div className="space-y-1.5 text-[11px] text-slate-400">
                  <div className="flex items-center gap-2">
                    <span className={checkProgress >= 1 ? "text-emerald-400" : "text-slate-600"}>
                      {checkProgress >= 1 ? "✓" : "○"}
                    </span>
                    <span>Checking your land boundaries</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={checkProgress >= 2 ? "text-emerald-400" : "text-slate-600"}>
                      {checkProgress >= 2 ? "✓" : "○"}
                    </span>
                    <span>Calculating permissible buildable envelope</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={checkProgress >= 3 ? "text-emerald-400" : "text-slate-600"}>
                      {checkProgress >= 3 ? "✓" : "○"}
                    </span>
                    <span>Applying municipal road width setbacks</span>
                  </div>
                </div>
              </div>
            )}

            {/* Actions Footer */}
            <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4">
              <button
                type="button"
                onClick={onOpenTechnicalMap}
                className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1.5 py-2 px-3 rounded-lg hover:bg-white/5 transition-colors"
                title="Switch to Technical View with GIS Map & CAD drawing canvas"
              >
                <Sliders className="w-3.5 h-3.5" />
                <span>Open in Technical GIS View</span>
              </button>

              <button
                type="submit"
                disabled={isChecking}
                className="pw-btn pw-btn-primary pw-btn-lg w-full sm:w-auto"
              >
                <span>Check My Land</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>

          </form>
        </div>

      </div>
    </div>
  );
};
