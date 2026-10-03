import React, { useState, useEffect } from 'react';
import { 
  Bed, 
  Bath, 
  Layers, 
  Car, 
  Check, 
  Sparkles, 
  ArrowLeft, 
  AlertCircle,
  IndianRupee,
  RefreshCw
} from 'lucide-react';

export interface CustomerDesignRequirements {
  bedrooms: number;
  bathrooms: number;
  floors: number;
  parkingCars: number;
  twoWheelers: string;
  balcony: boolean;
  terrace: boolean;
  preferredStyle: 'MODERN' | 'MINIMAL' | 'TRADITIONAL' | 'CONTEMPORARY';
  budgetInr: number;
  specialRequirements: string;
}

interface DesignIntakeViewProps {
  initialRequirements?: Partial<CustomerDesignRequirements>;
  onGenerateOptions: (reqs: CustomerDesignRequirements) => Promise<boolean>;
  onBackToFeasibility: () => void;
  isGenerating?: boolean;
}

const STYLE_OPTIONS = [
  {
    id: 'MODERN',
    label: 'Modern',
    description: 'Clean geometry, open plan living, generous daylight',
    tag: 'Popular'
  },
  {
    id: 'MINIMAL',
    label: 'Minimal',
    description: 'Clutter-free layouts, pure architectural lines, functional',
    tag: 'Efficient'
  },
  {
    id: 'TRADITIONAL',
    label: 'Traditional',
    description: 'Courtyard elements, sheltered verandas, regional context',
    tag: 'Classic'
  },
  {
    id: 'CONTEMPORARY',
    label: 'Contemporary',
    description: 'Warm materials, indoor-outdoor flow, balanced proportions',
    tag: 'Balanced'
  }
] as const;

const BUDGET_PRESETS = [
  { label: '₹35L', value: 3500000 },
  { label: '₹45L (Recommended)', value: 4500000 },
  { label: '₹55L', value: 5500000 },
  { label: '₹75L', value: 7500000 },
  { label: '₹1 Cr', value: 10000000 }
];

const IMPORTANT_PREFERENCES = [
  "Parents' room on ground floor",
  "Large kitchen",
  "Home office",
  "Pooja room",
  "Natural light focus",
  "Small shop / workspace",
  "Balcony",
  "Terrace access"
];

export const DesignIntakeView: React.FC<DesignIntakeViewProps> = ({
  initialRequirements,
  onGenerateOptions,
  onBackToFeasibility,
  isGenerating = false
}) => {
  // Step 1: Who is it for?
  const [bedrooms, setBedrooms] = useState<number>(initialRequirements?.bedrooms || 2);
  const [bathrooms, setBathrooms] = useState<number>(initialRequirements?.bathrooms || 2);

  // Step 2: How do you want to use it?
  const [floors, setFloors] = useState<number>(initialRequirements?.floors || 2);
  const [parkingCars, setParkingCars] = useState<number>(initialRequirements?.parkingCars ?? 1);
  const [balcony, setBalcony] = useState<boolean>(initialRequirements?.balcony ?? true);
  const [terrace, setTerrace] = useState<boolean>(initialRequirements?.terrace ?? true);

  // Step 3: What should it feel like?
  const [preferredStyle, setPreferredStyle] = useState<'MODERN' | 'MINIMAL' | 'TRADITIONAL' | 'CONTEMPORARY'>(
    initialRequirements?.preferredStyle || 'MODERN'
  );

  // Step 4: Anything important?
  const [selectedTags, setSelectedTags] = useState<string[]>([
    "Parents' room on ground floor",
    "Natural light focus"
  ]);
  const [budgetInr, setBudgetInr] = useState<number>(initialRequirements?.budgetInr || 4500000);
  const [specialRequirements, setSpecialRequirements] = useState<string>(
    initialRequirements?.specialRequirements || ''
  );

  // Polished generation steps
  const [genStep, setGenStep] = useState<number>(0);
  const [generationError, setGenerationError] = useState<string | null>(null);

  useEffect(() => {
    let t1: any, t2: any, t3: any;
    if (isGenerating) {
      setGenStep(1);
      t1 = setTimeout(() => setGenStep(2), 800);
      t2 = setTimeout(() => setGenStep(3), 1600);
      t3 = setTimeout(() => setGenStep(4), 2400);
    } else {
      setGenStep(0);
    }
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, [isGenerating]);

  const toggleTag = (tag: string) => {
    setSelectedTags(prev => 
      prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerationError(null);

    const mergedNotes = [
      ...selectedTags,
      specialRequirements.trim()
    ].filter(Boolean).join(', ');

    const reqs: CustomerDesignRequirements = {
      bedrooms,
      bathrooms,
      floors,
      parkingCars,
      twoWheelers: '1',
      balcony,
      terrace,
      preferredStyle,
      budgetInr,
      specialRequirements: mergedNotes
    };

    const ok = await onGenerateOptions(reqs);
    if (!ok) {
      setGenerationError("We couldn't create a suitable plan matching all these requirements. Try reducing the number of rooms or adjusting floors.");
    }
  };

  return (
    <div className="pw-page">
      <div className="pw-container">
        
        {/* Navigation Breadcrumb */}
        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={onBackToFeasibility}
            className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Feasibility</span>
          </button>

          <span className="pw-badge pw-badge-neutral">
            Step 3 of 6: Design Intake
          </span>
        </div>

        {/* Headline (§10) */}
        <div>
          <h1 className="pw-title-xl">
            Tell us how you want your home to work.
          </h1>
          <p className="pw-body mt-1">
            Answer a few simple questions so we can generate tailored architectural house options for your 1,100 sq ft plot.
          </p>
        </div>

        {/* Polished Generation Progress (§10, §20) */}
        {isGenerating && (
          <div className="pw-card border-blue-500/40 p-8 flex flex-col items-center text-center space-y-5 animate-pulse">
            <div className="w-12 h-12 rounded-full bg-blue-600/20 border border-blue-500/40 flex items-center justify-center">
              <RefreshCw className="w-6 h-6 text-blue-400 animate-spin" />
            </div>

            <div>
              <h2 className="pw-title-lg">Creating your house options</h2>
              <p className="pw-body-sm mt-1">
                Applying architectural layout rules and circulation geometry to your plot envelope.
              </p>
            </div>

            <div className="w-full max-w-sm space-y-2.5 text-left text-xs font-mono">
              <div className="flex items-center gap-2 text-emerald-400">
                <Check className="w-3.5 h-3.5 shrink-0" />
                <span>Creating feasible house options...</span>
              </div>
              <div className={`flex items-center gap-2 ${genStep >= 2 ? 'text-emerald-400' : 'text-blue-400'}`}>
                {genStep >= 2 ? <Check className="w-3.5 h-3.5 shrink-0" /> : <span className="w-3.5 h-3.5 rounded-full border border-blue-400 animate-spin" />}
                <span>Checking space requirements...</span>
              </div>
              <div className={`flex items-center gap-2 ${genStep >= 3 ? 'text-emerald-400' : genStep >= 2 ? 'text-blue-400' : 'text-slate-600'}`}>
                {genStep >= 3 ? <Check className="w-3.5 h-3.5 shrink-0" /> : <span className="w-3.5 h-3.5 rounded-full border border-slate-700" />}
                <span>Checking circulation...</span>
              </div>
              <div className={`flex items-center gap-2 ${genStep >= 4 ? 'text-emerald-400' : genStep >= 3 ? 'text-blue-400' : 'text-slate-600'}`}>
                {genStep >= 4 ? <Check className="w-3.5 h-3.5 shrink-0" /> : <span className="w-3.5 h-3.5 rounded-full border border-slate-700" />}
                <span>Preparing 3D models...</span>
              </div>
            </div>
          </div>
        )}

        {/* Error State (§21) */}
        {generationError && !isGenerating && (
          <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/30 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
            <div className="text-xs">
              <span className="font-semibold text-rose-200 block">We couldn't create a suitable plan from these requirements.</span>
              <span className="text-rose-300/80">Try reducing the number of rooms or changing the number of floors to match the buildable envelope.</span>
            </div>
          </div>
        )}

        {/* Guided Form (§10) */}
        {!isGenerating && (
          <form onSubmit={handleSubmit} className="flex flex-col gap-5">
            
            {/* STEP 1: Who is it for? */}
            <div className="pw-card">
              <div className="flex items-center justify-between border-b border-white/10 pb-3 mb-4">
                <div>
                  <span className="text-[10px] font-mono uppercase tracking-wider text-blue-400 font-semibold block">
                    Step 1
                  </span>
                  <h3 className="pw-title-md">Who is it for?</h3>
                </div>
                <span className="pw-body-sm">Room requirements</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                {/* Bedrooms */}
                <div>
                  <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5 mb-2">
                    <Bed className="w-3.5 h-3.5 text-blue-400" />
                    <span>Bedrooms</span>
                  </label>
                  <div className="grid grid-cols-4 gap-2">
                    {[1, 2, 3, 4].map(n => (
                      <button
                        key={n}
                        type="button"
                        onClick={() => setBedrooms(n)}
                        className={`h-10 rounded-md border text-xs font-semibold transition-all ${
                          bedrooms === n
                            ? 'bg-blue-600 text-white border-blue-500'
                            : 'bg-white/[0.02] text-slate-300 border-white/10 hover:border-white/20'
                        }`}
                      >
                        {n} BHK
                      </button>
                    ))}
                  </div>
                </div>

                {/* Bathrooms */}
                <div>
                  <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5 mb-2">
                    <Bath className="w-3.5 h-3.5 text-blue-400" />
                    <span>Bathrooms</span>
                  </label>
                  <div className="grid grid-cols-4 gap-2">
                    {[1, 2, 3, 4].map(n => (
                      <button
                        key={n}
                        type="button"
                        onClick={() => setBathrooms(n)}
                        className={`h-10 rounded-md border text-xs font-semibold transition-all ${
                          bathrooms === n
                            ? 'bg-blue-600 text-white border-blue-500'
                            : 'bg-white/[0.02] text-slate-300 border-white/10 hover:border-white/20'
                        }`}
                      >
                        {n} Bath
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* STEP 2: How do you want to use it? */}
            <div className="pw-card">
              <div className="flex items-center justify-between border-b border-white/10 pb-3 mb-4">
                <div>
                  <span className="text-[10px] font-mono uppercase tracking-wider text-blue-400 font-semibold block">
                    Step 2
                  </span>
                  <h3 className="pw-title-md">How do you want to use it?</h3>
                </div>
                <span className="pw-body-sm">Floors, parking, and outdoor spaces</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                {/* Floors */}
                <div>
                  <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5 mb-2">
                    <Layers className="w-3.5 h-3.5 text-blue-400" />
                    <span>Floors</span>
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {[
                      { num: 1, label: 'Ground (G)' },
                      { num: 2, label: 'G+1 Storey' },
                      { num: 3, label: 'G+2 Storeys' }
                    ].map(f => (
                      <button
                        key={f.num}
                        type="button"
                        onClick={() => setFloors(f.num)}
                        className={`h-10 rounded-md border text-xs font-semibold transition-all ${
                          floors === f.num
                            ? 'bg-blue-600 text-white border-blue-500'
                            : 'bg-white/[0.02] text-slate-300 border-white/10 hover:border-white/20'
                        }`}
                      >
                        {f.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Parking */}
                <div>
                  <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5 mb-2">
                    <Car className="w-3.5 h-3.5 text-blue-400" />
                    <span>Car Parking</span>
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {[
                      { count: 0, label: 'None' },
                      { count: 1, label: '1 Car (Standard)' },
                      { count: 2, label: '2 Cars' }
                    ].map(p => (
                      <button
                        key={p.count}
                        type="button"
                        onClick={() => setParkingCars(p.count)}
                        className={`h-10 rounded-md border text-xs font-semibold transition-all ${
                          parkingCars === p.count
                            ? 'bg-blue-600 text-white border-blue-500'
                            : 'bg-white/[0.02] text-slate-300 border-white/10 hover:border-white/20'
                        }`}
                      >
                        {p.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Outdoor features */}
                <div className="sm:col-span-2 flex items-center gap-4 pt-1">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={balcony}
                      onChange={(e) => setBalcony(e.target.checked)}
                      className="w-4 h-4 rounded border-slate-700 bg-slate-900 text-blue-600 focus:ring-0"
                    />
                    <span className="text-xs font-medium text-slate-300">Include Balcony</span>
                  </label>

                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={terrace}
                      onChange={(e) => setTerrace(e.target.checked)}
                      className="w-4 h-4 rounded border-slate-700 bg-slate-900 text-blue-600 focus:ring-0"
                    />
                    <span className="text-xs font-medium text-slate-300">Terrace Access</span>
                  </label>
                </div>
              </div>
            </div>

            {/* STEP 3: What should it feel like? */}
            <div className="pw-card">
              <div className="flex items-center justify-between border-b border-white/10 pb-3 mb-4">
                <div>
                  <span className="text-[10px] font-mono uppercase tracking-wider text-blue-400 font-semibold block">
                    Step 3
                  </span>
                  <h3 className="pw-title-md">What should it feel like?</h3>
                </div>
                <span className="pw-body-sm">Architectural design language</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {STYLE_OPTIONS.map(s => {
                  const isSelected = preferredStyle === s.id;
                  return (
                    <button
                      key={s.id}
                      type="button"
                      onClick={() => setPreferredStyle(s.id as any)}
                      className={`p-3.5 rounded-lg border text-left transition-all ${
                        isSelected
                          ? 'bg-blue-600/10 border-blue-500 shadow-sm'
                          : 'bg-white/[0.02] border-white/10 hover:border-white/20'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className={`text-xs font-bold ${isSelected ? 'text-white' : 'text-slate-300'}`}>
                          {s.label}
                        </span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-slate-400">
                          {s.tag}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-500 leading-tight">
                        {s.description}
                      </p>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* STEP 4: Anything important? */}
            <div className="pw-card">
              <div className="flex items-center justify-between border-b border-white/10 pb-3 mb-4">
                <div>
                  <span className="text-[10px] font-mono uppercase tracking-wider text-blue-400 font-semibold block">
                    Step 4
                  </span>
                  <h3 className="pw-title-md">Anything important?</h3>
                </div>
                <span className="pw-body-sm">Specific needs &amp; target budget</span>
              </div>

              {/* Quick Preferences Chips */}
              <div className="space-y-2 mb-4">
                <span className="text-xs text-slate-400 block">Select any that apply:</span>
                <div className="flex flex-wrap gap-2">
                  {IMPORTANT_PREFERENCES.map(tag => {
                    const isSelected = selectedTags.includes(tag);
                    return (
                      <button
                        key={tag}
                        type="button"
                        onClick={() => toggleTag(tag)}
                        className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-all ${
                          isSelected
                            ? 'bg-blue-600/20 text-blue-300 border-blue-500'
                            : 'bg-white/[0.02] text-slate-400 border-white/10 hover:border-white/20 hover:text-white'
                        }`}
                      >
                        {isSelected && <span className="mr-1">✓</span>}
                        {tag}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Freeform Notes */}
              <div className="mb-5">
                <input
                  type="text"
                  value={specialRequirements}
                  onChange={(e) => setSpecialRequirements(e.target.value)}
                  placeholder="Other requirements (e.g. lift provision, solar inverter space, prayer nook)..."
                  className="pw-input text-xs"
                />
              </div>

              {/* Budget Clear Display (§10) */}
              <div className="pt-3 border-t border-white/5">
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center justify-between mb-2">
                  <span className="flex items-center gap-1.5">
                    <IndianRupee className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Target Construction Budget</span>
                  </span>
                  <span className="font-mono text-emerald-400 text-sm font-bold">
                    ₹{(budgetInr / 100000).toFixed(1)} Lakh
                  </span>
                </label>

                <div className="flex flex-wrap items-center gap-2">
                  {BUDGET_PRESETS.map(bp => (
                    <button
                      key={bp.value}
                      type="button"
                      onClick={() => setBudgetInr(bp.value)}
                      className={`px-3 py-1.5 rounded-md text-xs font-mono transition-all ${
                        budgetInr === bp.value
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500 font-bold'
                          : 'bg-white/[0.02] text-slate-400 border border-white/10 hover:border-white/20'
                      }`}
                    >
                      {bp.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Submit Action (§10) */}
            <div className="pt-2 flex items-center justify-end">
              <button
                type="submit"
                disabled={isGenerating}
                className="pw-btn pw-btn-primary pw-btn-lg w-full sm:w-auto"
              >
                <Sparkles className="w-4 h-4" />
                <span>Generate House Options</span>
              </button>
            </div>

          </form>
        )}

      </div>
    </div>
  );
};
