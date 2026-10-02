import React, { useState, useEffect } from 'react';
import { 
  Bed, 
  Bath, 
  Layers, 
  Car, 
  Bike, 
  Sun, 
  Check, 
  Sparkles, 
  ArrowRight, 
  ArrowLeft,
  CheckCircle2, 
  AlertCircle,
  Home,
  Palette,
  IndianRupee,
  MessageSquare
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

const STYLE_CARDS = [
  {
    id: 'MODERN',
    label: 'Modern',
    description: 'Clean geometry, glass accents, open plan living',
    tag: 'Popular'
  },
  {
    id: 'MINIMAL',
    label: 'Minimal',
    description: 'Functional spaces, clutter-free layouts, pure forms',
    tag: 'Efficient'
  },
  {
    id: 'TRADITIONAL',
    label: 'Traditional',
    description: 'Courtyard elements, sheltered verandas, regional charm',
    tag: 'Classic'
  },
  {
    id: 'CONTEMPORARY',
    label: 'Contemporary',
    description: 'Warm materials, indoor-outdoor flow, natural daylight',
    tag: 'Balanced'
  }
] as const;

const BUDGET_PRESETS = [
  { label: '₹20 lakh', value: 2000000 },
  { label: '₹30 lakh', value: 3000000 },
  { label: '₹50 lakh', value: 5000000 },
  { label: '₹75 lakh', value: 7500000 },
  { label: '₹1 crore+', value: 10000000 }
];

const SUGGESTION_CHIPS = [
  'Parents bedroom on ground floor',
  'Large kitchen',
  'Home office',
  'Small shop',
  'Prayer room / Pooja',
  'More natural light'
];

export const DesignIntakeView: React.FC<DesignIntakeViewProps> = ({
  initialRequirements,
  onGenerateOptions,
  onBackToFeasibility,
  isGenerating = false
}) => {
  // Form State
  const [bedrooms, setBedrooms] = useState<number>(initialRequirements?.bedrooms || 2);
  const [bathrooms, setBathrooms] = useState<number>(initialRequirements?.bathrooms || 2);
  const [floors, setFloors] = useState<number>(initialRequirements?.floors || 2);
  const [parkingCars, setParkingCars] = useState<number>(initialRequirements?.parkingCars ?? 1);
  const [twoWheelers, setTwoWheelers] = useState<string>(initialRequirements?.twoWheelers || '1');
  const [balcony, setBalcony] = useState<boolean>(initialRequirements?.balcony ?? true);
  const [terrace, setTerrace] = useState<boolean>(initialRequirements?.terrace ?? true);
  const [preferredStyle, setPreferredStyle] = useState<'MODERN' | 'MINIMAL' | 'TRADITIONAL' | 'CONTEMPORARY'>(
    initialRequirements?.preferredStyle || 'MODERN'
  );
  const [budgetInr, setBudgetInr] = useState<number>(initialRequirements?.budgetInr || 5000000);
  const [specialRequirements, setSpecialRequirements] = useState<string>(
    initialRequirements?.specialRequirements || ''
  );

  // Generation loading progress state
  const [generationStep, setGenerationStep] = useState<number>(0);
  const [generationError, setGenerationError] = useState<string | null>(null);

  useEffect(() => {
    let timer: any;
    if (isGenerating) {
      setGenerationStep(1);
      timer = setTimeout(() => {
        setGenerationStep(2);
        timer = setTimeout(() => {
          setGenerationStep(3);
        }, 1200);
      }, 1000);
    } else {
      setGenerationStep(0);
    }
    return () => clearTimeout(timer);
  }, [isGenerating]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerationError(null);
    const reqs: CustomerDesignRequirements = {
      bedrooms,
      bathrooms,
      floors,
      parkingCars,
      twoWheelers,
      balcony,
      terrace,
      preferredStyle,
      budgetInr,
      specialRequirements
    };

    const success = await onGenerateOptions(reqs);
    if (!success) {
      setGenerationError("Planwise couldn't find a suitable layout with these requirements.");
    }
  };

  const handleAddSuggestion = (chip: string) => {
    setSpecialRequirements((prev) => {
      if (!prev.trim()) return chip;
      if (prev.includes(chip)) return prev;
      return `${prev.trim()}, ${chip}`;
    });
  };

  const formatBudgetDisplay = (val: number) => {
    if (val >= 10000000) {
      return `₹${(val / 10000000).toFixed(2)} Crore`;
    }
    return `₹${(val / 100000).toFixed(0)} Lakh`;
  };

  return (
    <div className="flex-1 w-full h-full overflow-y-auto bg-[#07090e] p-6 lg:p-10 flex flex-col items-center">
      <div className="w-full max-w-4xl space-y-8 animate-fade-in pb-20">

        {/* Top Progress Breadcrumb */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-5">
          <button
            type="button"
            onClick={onBackToFeasibility}
            className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Feasibility</span>
          </button>

          {/* Stepper */}
          <div className="flex items-center gap-2 text-xs font-mono">
            <span className="text-emerald-400 font-medium">1 Land ✓</span>
            <span className="text-slate-600">→</span>
            <span className="text-emerald-400 font-medium">2 Feasibility ✓</span>
            <span className="text-slate-600">→</span>
            <span className="text-blue-400 font-bold bg-blue-950/80 border border-blue-500/40 px-2.5 py-0.5 rounded-full">
              3 Design ●
            </span>
            <span className="text-slate-600">→</span>
            <span className="text-slate-500">4 Cost</span>
            <span className="text-slate-600">→</span>
            <span className="text-slate-500">5 Build</span>
            <span className="text-slate-600">→</span>
            <span className="text-slate-500">6 Engineer</span>
          </div>
        </div>

        {/* Page Header */}
        <div className="space-y-2">
          <h1 className="text-3xl lg:text-4xl font-display font-bold text-white tracking-tight">
            What kind of home do you want?
          </h1>
          <p className="text-slate-400 text-sm lg:text-base leading-relaxed">
            Tell us your basic requirements. Planwise will generate suitable house options for your site.
          </p>
        </div>

        {/* Active Generation Loading Overlay */}
        {isGenerating && (
          <div className="rounded-2xl bg-slate-900/90 border border-blue-500/40 p-8 shadow-2xl flex flex-col items-center text-center space-y-6 animate-pulse">
            <div className="w-14 h-14 rounded-full bg-blue-600/20 border border-blue-500/40 flex items-center justify-center">
              <Sparkles className="w-7 h-7 text-blue-400 animate-spin" />
            </div>

            <div className="space-y-1">
              <h2 className="text-xl font-bold text-white">Generating your house options...</h2>
              <p className="text-xs text-slate-400">
                Evaluating layout configurations, room placements, and solar access for your plot.
              </p>
            </div>

            {/* Checklist */}
            <div className="w-full max-w-sm space-y-2.5 text-left text-xs font-mono">
              <div className="flex items-center gap-2.5 text-emerald-400">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>Understanding your requirements</span>
              </div>
              <div className="flex items-center gap-2.5 text-emerald-400">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>Checking your site & setbacks</span>
              </div>
              <div className={`flex items-center gap-2.5 ${generationStep >= 2 ? 'text-emerald-400' : 'text-blue-400 animate-pulse'}`}>
                {generationStep >= 2 ? (
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                ) : (
                  <div className="w-4 h-4 rounded-full border-2 border-blue-400 border-t-transparent animate-spin" />
                )}
                <span>Creating layouts</span>
              </div>
              <div className={`flex items-center gap-2.5 ${generationStep >= 3 ? 'text-emerald-400' : 'text-slate-500'}`}>
                {generationStep >= 3 ? (
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                ) : (
                  <div className="w-4 h-4 rounded-full border border-slate-700" />
                )}
                <span>Preparing house options</span>
              </div>
            </div>
          </div>
        )}

        {/* Generation Error State */}
        {generationError && !isGenerating && (
          <div className="rounded-2xl bg-rose-950/40 border border-rose-500/40 p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-6 h-6 text-rose-400 shrink-0" />
              <div>
                <h3 className="text-sm font-semibold text-rose-200">
                  {generationError}
                </h3>
                <p className="text-xs text-rose-300/80">
                  Try reducing the number of bedrooms or floors to fit your plot envelope.
                </p>
              </div>
            </div>
            <button
              onClick={() => setGenerationError(null)}
              className="text-xs px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-medium transition-colors"
            >
              Change requirements
            </button>
          </div>
        )}

        {/* The Clean Form */}
        {!isGenerating && (
          <form onSubmit={handleSubmit} className="space-y-8">

            {/* SECTION 1 — HOME SIZE */}
            <div className="rounded-2xl bg-slate-900/40 border border-white/10 p-6 space-y-6">
              <div className="border-b border-white/10 pb-3">
                <h2 className="text-base font-semibold text-white flex items-center gap-2">
                  <Home className="w-4 h-4 text-blue-400" />
                  <span>Section 1 — Home Size</span>
                </h2>
                <p className="text-xs text-slate-400">Choose the number of bedrooms, bathrooms, and floor levels</p>
              </div>

              {/* Bedrooms */}
              <div className="space-y-2">
                <label className="text-xs font-medium text-slate-300 flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <Bed className="w-4 h-4 text-blue-400" />
                    Bedrooms
                  </span>
                  <span className="text-[11px] text-blue-400 font-mono font-bold">{bedrooms} BHK</span>
                </label>
                <div className="grid grid-cols-4 gap-3">
                  {[1, 2, 3, 4].map((num) => (
                    <button
                      key={`bed-${num}`}
                      type="button"
                      onClick={() => setBedrooms(num)}
                      className={`py-3 rounded-xl border text-sm font-semibold transition-all ${
                        bedrooms === num
                          ? 'bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-500/30'
                          : 'bg-slate-900/60 border-white/10 text-slate-300 hover:border-white/20 hover:text-white'
                      }`}
                    >
                      {num} {num === 1 ? 'Bedroom' : 'Bedrooms'}
                    </button>
                  ))}
                </div>
              </div>

              {/* Bathrooms */}
              <div className="space-y-2">
                <label className="text-xs font-medium text-slate-300 flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <Bath className="w-4 h-4 text-cyan-400" />
                    Bathrooms
                  </span>
                  <span className="text-[11px] text-cyan-400 font-mono font-bold">{bathrooms} Baths</span>
                </label>
                <div className="grid grid-cols-4 gap-3">
                  {[1, 2, 3, 4].map((num) => (
                    <button
                      key={`bath-${num}`}
                      type="button"
                      onClick={() => setBathrooms(num)}
                      className={`py-3 rounded-xl border text-sm font-semibold transition-all ${
                        bathrooms === num
                          ? 'bg-cyan-600 border-cyan-500 text-white shadow-lg shadow-cyan-500/30'
                          : 'bg-slate-900/60 border-white/10 text-slate-300 hover:border-white/20 hover:text-white'
                      }`}
                    >
                      {num} {num === 1 ? 'Bathroom' : 'Bathrooms'}
                    </button>
                  ))}
                </div>
              </div>

              {/* Floors */}
              <div className="space-y-2">
                <label className="text-xs font-medium text-slate-300 flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <Layers className="w-4 h-4 text-purple-400" />
                    Floors
                  </span>
                  <span className="text-[11px] text-purple-400 font-mono font-bold">
                    {floors === 1 ? 'Ground Only' : `Ground + ${floors - 1}`}
                  </span>
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { value: 1, label: 'Ground only', desc: 'Single-storey bungalow' },
                    { value: 2, label: 'Ground + 1', desc: 'Duplex (2 levels)' },
                    { value: 3, label: 'Ground + 2', desc: 'Triplex (3 levels)' }
                  ].map((fl) => (
                    <button
                      key={`floor-${fl.value}`}
                      type="button"
                      onClick={() => setFloors(fl.value)}
                      className={`p-3 rounded-xl border text-left transition-all flex flex-col justify-between ${
                        floors === fl.value
                          ? 'bg-purple-600/30 border-purple-500 text-white shadow-lg shadow-purple-500/20'
                          : 'bg-slate-900/60 border-white/10 text-slate-300 hover:border-white/20 hover:text-white'
                      }`}
                    >
                      <span className="font-semibold text-sm">{fl.label}</span>
                      <span className="text-[11px] text-slate-400 mt-1">{fl.desc}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* SECTION 2 — PARKING */}
            <div className="rounded-2xl bg-slate-900/40 border border-white/10 p-6 space-y-6">
              <div className="border-b border-white/10 pb-3">
                <h2 className="text-base font-semibold text-white flex items-center gap-2">
                  <Car className="w-4 h-4 text-cyan-400" />
                  <span>Section 2 — Parking</span>
                </h2>
                <p className="text-xs text-slate-400">Specify on-site vehicle and two-wheeler requirements</p>
              </div>

              {/* Cars */}
              <div className="space-y-2">
                <label className="text-xs font-medium text-slate-300">
                  How many cars do you need?
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { value: 0, label: 'No parking' },
                    { value: 1, label: '1 Car' },
                    { value: 2, label: '2 Cars' }
                  ].map((p) => (
                    <button
                      key={`car-${p.value}`}
                      type="button"
                      onClick={() => setParkingCars(p.value)}
                      className={`py-3 rounded-xl border text-sm font-semibold transition-all ${
                        parkingCars === p.value
                          ? 'bg-cyan-600 border-cyan-500 text-white shadow-lg shadow-cyan-500/30'
                          : 'bg-slate-900/60 border-white/10 text-slate-300 hover:border-white/20 hover:text-white'
                      }`}
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Two-Wheelers */}
              <div className="space-y-2">
                <label className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
                  <Bike className="w-4 h-4 text-slate-400" />
                  Two-wheelers (Bikes / Scooters)
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {['None', '1', '2+'].map((tw) => (
                    <button
                      key={`tw-${tw}`}
                      type="button"
                      onClick={() => setTwoWheelers(tw)}
                      className={`py-2.5 rounded-xl border text-xs font-medium transition-all ${
                        twoWheelers === tw
                          ? 'bg-slate-800 border-white/40 text-white font-semibold'
                          : 'bg-slate-900/60 border-white/10 text-slate-400 hover:text-white'
                      }`}
                    >
                      {tw === 'None' ? 'No bike' : `${tw} ${tw === '1' ? 'bike' : 'bikes'}`}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* SECTION 3 — HOME FEATURES */}
            <div className="rounded-2xl bg-slate-900/40 border border-white/10 p-6 space-y-6">
              <div className="border-b border-white/10 pb-3">
                <h2 className="text-base font-semibold text-white flex items-center gap-2">
                  <Sun className="w-4 h-4 text-amber-400" />
                  <span>Section 3 — Home Features</span>
                </h2>
                <p className="text-xs text-slate-400">Outdoor connectivity and open-to-sky preferences</p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Balcony */}
                <div className="p-4 rounded-xl bg-slate-900/60 border border-white/10 flex items-center justify-between">
                  <div>
                    <span className="text-sm font-semibold text-white block">Balcony</span>
                    <span className="text-xs text-slate-400">Attached to living room or master bedroom</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => setBalcony(true)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                        balcony ? 'bg-amber-600 text-white shadow-md' : 'bg-slate-800 text-slate-400 hover:text-white'
                      }`}
                    >
                      Yes
                    </button>
                    <button
                      type="button"
                      onClick={() => setBalcony(false)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                        !balcony ? 'bg-slate-700 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'
                      }`}
                    >
                      No
                    </button>
                  </div>
                </div>

                {/* Terrace */}
                <div className="p-4 rounded-xl bg-slate-900/60 border border-white/10 flex items-center justify-between">
                  <div>
                    <span className="text-sm font-semibold text-white block">Terrace / Roof Garden</span>
                    <span className="text-xs text-slate-400">Private accessible rooftop area</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => setTerrace(true)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                        terrace ? 'bg-amber-600 text-white shadow-md' : 'bg-slate-800 text-slate-400 hover:text-white'
                      }`}
                    >
                      Yes
                    </button>
                    <button
                      type="button"
                      onClick={() => setTerrace(false)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                        !terrace ? 'bg-slate-700 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'
                      }`}
                    >
                      No
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* SECTION 4 — STYLE */}
            <div className="rounded-2xl bg-slate-900/40 border border-white/10 p-6 space-y-4">
              <div className="border-b border-white/10 pb-3">
                <h2 className="text-base font-semibold text-white flex items-center gap-2">
                  <Palette className="w-4 h-4 text-emerald-400" />
                  <span>Section 4 — Architectural Style</span>
                </h2>
                <p className="text-xs text-slate-400">
                  Select your aesthetic preference. (Aesthetic preference only; statutory geometry remains compliant).
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
                {STYLE_CARDS.map((style) => (
                  <button
                    key={style.id}
                    type="button"
                    onClick={() => setPreferredStyle(style.id)}
                    className={`p-4 rounded-xl border text-left transition-all flex flex-col justify-between ${
                      preferredStyle === style.id
                        ? 'bg-emerald-950/40 border-emerald-500 text-white shadow-lg shadow-emerald-500/20'
                        : 'bg-slate-900/60 border-white/10 text-slate-300 hover:border-white/20 hover:text-white'
                    }`}
                  >
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-bold text-sm text-white">{style.label}</span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/10 font-mono text-slate-300">
                          {style.tag}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                        {style.description}
                      </p>
                    </div>

                    <div className="mt-4 pt-2 border-t border-white/5 flex items-center gap-1.5 text-xs">
                      {preferredStyle === style.id ? (
                        <span className="text-emerald-400 font-medium flex items-center gap-1">
                          <Check className="w-3.5 h-3.5" /> Selected
                        </span>
                      ) : (
                        <span className="text-slate-500">Click to select</span>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* SECTION 5 — BUDGET */}
            <div className="rounded-2xl bg-slate-900/40 border border-white/10 p-6 space-y-4">
              <div className="border-b border-white/10 pb-3">
                <h2 className="text-base font-semibold text-white flex items-center gap-2">
                  <IndianRupee className="w-4 h-4 text-emerald-400" />
                  <span>Section 5 — Approximate Budget</span>
                </h2>
                <p className="text-xs text-slate-400">
                  Estimated construction budget guide. (Detailed Bill of Quantities computed in Step 4).
                </p>
              </div>

              <div className="space-y-3">
                <div className="relative max-w-md">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400 font-bold">
                    ₹
                  </div>
                  <input
                    type="number"
                    value={budgetInr || ''}
                    onChange={(e) => setBudgetInr(Number(e.target.value))}
                    step="100000"
                    placeholder="5000000"
                    className="w-full pl-9 pr-24 py-3 rounded-xl bg-slate-950/80 border border-white/10 text-white font-mono font-bold text-base focus:outline-none focus:border-blue-500"
                  />
                  <div className="absolute inset-y-0 right-0 pr-3.5 flex items-center pointer-events-none text-xs text-blue-400 font-mono font-medium">
                    {formatBudgetDisplay(budgetInr)}
                  </div>
                </div>

                {/* Quick Presets */}
                <div className="flex flex-wrap gap-2 pt-1">
                  {BUDGET_PRESETS.map((p) => (
                    <button
                      key={p.label}
                      type="button"
                      onClick={() => setBudgetInr(p.value)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all ${
                        budgetInr === p.value
                          ? 'bg-blue-600 text-white font-bold'
                          : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                      }`}
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* SECTION 6 — SPECIAL REQUIREMENTS */}
            <div className="rounded-2xl bg-slate-900/40 border border-white/10 p-6 space-y-4">
              <div className="border-b border-white/10 pb-3">
                <h2 className="text-base font-semibold text-white flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-purple-400" />
                  <span>Section 6 — Special Requirements (Optional)</span>
                </h2>
                <p className="text-xs text-slate-400">
                  Anything else you'd like in your home? We will use this to guide layout space allocations.
                </p>
              </div>

              <div className="space-y-3">
                <textarea
                  rows={3}
                  value={specialRequirements}
                  onChange={(e) => setSpecialRequirements(e.target.value)}
                  placeholder="e.g. Parents bedroom on ground floor, puja room facing east, large airy kitchen..."
                  className="w-full p-3.5 rounded-xl bg-slate-950/80 border border-white/10 text-white text-sm focus:outline-none focus:border-blue-500 leading-relaxed"
                />

                {/* Quick Suggestions Chips */}
                <div className="flex flex-wrap gap-2">
                  <span className="text-[11px] text-slate-500 self-center">Suggestions:</span>
                  {SUGGESTION_CHIPS.map((chip) => (
                    <button
                      key={chip}
                      type="button"
                      onClick={() => handleAddSuggestion(chip)}
                      className="px-2.5 py-1 rounded-md bg-slate-800/80 border border-white/5 text-[11px] text-slate-300 hover:text-white hover:border-white/20 transition-all"
                    >
                      + {chip}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* SUMMARY CARD & PRIMARY ACTION */}
            <div className="rounded-2xl bg-slate-900/80 border border-blue-500/30 p-6 space-y-5">
              <div className="flex items-center justify-between border-b border-white/10 pb-3">
                <div>
                  <h3 className="text-xs uppercase tracking-wider font-semibold text-blue-400">
                    Your Requirements Summary
                  </h3>
                  <p className="text-[11px] text-slate-400">Ready to synthesize floor plan designs</p>
                </div>
                <span className="text-xs font-mono text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 px-2.5 py-1 rounded-md">
                  Authoritative Plot: 1,100 sq ft
                </span>
              </div>

              {/* Requirement Tags */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="p-2.5 rounded-xl bg-slate-950/60 border border-white/5">
                  <span className="text-slate-500 block text-[10px]">ROOMS</span>
                  <span className="text-white font-bold">{bedrooms} BHK / {bathrooms} Baths</span>
                </div>

                <div className="p-2.5 rounded-xl bg-slate-950/60 border border-white/5">
                  <span className="text-slate-500 block text-[10px]">LEVELS</span>
                  <span className="text-white font-bold">{floors === 1 ? 'Ground Only' : `Ground + ${floors - 1}`}</span>
                </div>

                <div className="p-2.5 rounded-xl bg-slate-950/60 border border-white/5">
                  <span className="text-slate-500 block text-[10px]">PARKING</span>
                  <span className="text-white font-bold">{parkingCars === 0 ? 'No Parking' : `${parkingCars} Car`}</span>
                </div>

                <div className="p-2.5 rounded-xl bg-slate-950/60 border border-white/5">
                  <span className="text-slate-500 block text-[10px]">STYLE & BUDGET</span>
                  <span className="text-emerald-400 font-bold">{preferredStyle} • {formatBudgetDisplay(budgetInr)}</span>
                </div>
              </div>

              {/* Submit CTA */}
              <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4">
                <button
                  type="button"
                  onClick={onBackToFeasibility}
                  className="w-full sm:w-auto text-xs text-slate-400 hover:text-white px-4 py-2.5 transition-colors"
                >
                  ← Back to Feasibility
                </button>

                <button
                  type="submit"
                  className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-display font-semibold text-sm shadow-xl shadow-blue-500/25 flex items-center justify-center gap-2 transition-all hover:scale-[1.01]"
                >
                  <span>Generate House Options</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>

          </form>
        )}

      </div>
    </div>
  );
};
