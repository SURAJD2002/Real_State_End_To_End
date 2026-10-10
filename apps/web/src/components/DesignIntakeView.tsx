import React, { useState } from 'react';
import {
  ArrowLeft,
  ArrowRight,
  RefreshCw,
  AlertCircle
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
  plotAreaSqFt?: number | null;
}

const STYLE_OPTIONS: { id: 'MODERN' | 'MINIMAL' | 'TRADITIONAL' | 'CONTEMPORARY'; label: string }[] = [
  { id: 'MODERN', label: 'Modern' },
  { id: 'MINIMAL', label: 'Minimal' },
  { id: 'TRADITIONAL', label: 'Traditional' },
  { id: 'CONTEMPORARY', label: 'Contemporary' }
];

const BUDGET_OPTIONS = [
  { label: '₹20L', value: 2000000 },
  { label: '₹30L', value: 3000000 },
  { label: '₹50L', value: 5000000 },
  { label: '₹75L', value: 7500000 },
  { label: '₹1Cr+', value: 10000000 }
];

const SPECIAL_REQUIREMENTS_LIST = [
  'Balcony',
  'Terrace',
  'Puja',
  'Home Office',
  'Large Kitchen',
  'Parents Bedroom',
  'Natural Light'
];

export const DesignIntakeView: React.FC<DesignIntakeViewProps> = ({
  initialRequirements,
  onGenerateOptions,
  onBackToFeasibility,
  isGenerating = false,
  plotAreaSqFt
}) => {
  const [bedrooms, setBedrooms] = useState<number>(initialRequirements?.bedrooms || 2);
  const [bathrooms, setBathrooms] = useState<number>(initialRequirements?.bathrooms || 2);
  const [floors, setFloors] = useState<number>(initialRequirements?.floors || 2);
  const [parkingCars, setParkingCars] = useState<number>(initialRequirements?.parkingCars ?? 1);
  const [preferredStyle, setPreferredStyle] = useState<'MODERN' | 'MINIMAL' | 'TRADITIONAL' | 'CONTEMPORARY'>(
    initialRequirements?.preferredStyle || 'MODERN'
  );
  const [budgetInr, setBudgetInr] = useState<number>(initialRequirements?.budgetInr || 5000000);
  const [selectedSpecial, setSelectedSpecial] = useState<string[]>([
    'Balcony',
    'Parents Bedroom',
    'Natural Light'
  ]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const toggleSpecial = (item: string) => {
    setSelectedSpecial(prev =>
      prev.includes(item) ? prev.filter(i => i !== item) : [...prev, item]
    );
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    const reqs: CustomerDesignRequirements = {
      bedrooms,
      bathrooms,
      floors,
      parkingCars,
      twoWheelers: '1',
      balcony: selectedSpecial.includes('Balcony'),
      terrace: selectedSpecial.includes('Terrace'),
      preferredStyle,
      budgetInr,
      specialRequirements: selectedSpecial.join(', ')
    };

    const success = await onGenerateOptions(reqs);
    if (!success) {
      setErrorMessage("We couldn't find a suitable layout with these requirements. Try adjusting the rooms or number of floors.");
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

          <span
            className={`pw-badge font-mono text-[11px] ${plotAreaSqFt ? 'pw-badge-neutral' : 'pw-badge-error'}`}
            data-testid="design-plot-badge"
          >
            {plotAreaSqFt ? `${plotAreaSqFt.toLocaleString()} sq ft Plot` : 'Plot Area Unavailable'}
          </span>
        </div>

        {/* Title & Subtitle (§8) */}
        <div>
          <h1 className="pw-title-xl">
            Tell us about your dream home
          </h1>
          <p className="pw-body mt-1">
            We'll create a few practical options for your land.
          </p>
        </div>

        {/* Loading State Animation (§8, §19) */}
        {isGenerating && (
          <div className="pw-card p-12 flex flex-col items-center justify-center text-center space-y-4">
            <div className="w-14 h-14 rounded-full bg-blue-600/20 border border-blue-500/40 flex items-center justify-center">
              <RefreshCw className="w-7 h-7 text-blue-400 animate-spin" />
            </div>
            <div>
              <h2 className="pw-title-lg">Designing your options...</h2>
              <p className="pw-body-sm mt-1">
                Creating practical home layouts tailored to your plot and preferences.
              </p>
            </div>
          </div>
        )}

        {/* Clean Error State (§18) */}
        {errorMessage && !isGenerating && (
          <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            <div className="text-xs">
              <span className="font-semibold text-amber-200 block">We couldn't find a suitable layout with these requirements.</span>
              <span className="text-amber-300/80">Please adjust your room requirements or floors to match your plot footprint.</span>
            </div>
          </div>
        )}

        {/* Main Card-Based Selector Form (§8) */}
        {!isGenerating && (
          <form onSubmit={handleGenerate} className="space-y-5">

            {/* 1. Bedrooms & Bathrooms */}
            <div className="pw-card p-5 space-y-4">
              {/* Bedrooms */}
              <div>
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-2">
                  BEDROOMS
                </label>
                <div className="grid grid-cols-4 gap-3">
                  {[1, 2, 3, 4].map((n) => (
                    <button
                      key={n}
                      type="button"
                      onClick={() => setBedrooms(n)}
                      data-testid={`btn-bedrooms-${n}`}
                      className={`h-12 rounded-xl border text-sm font-semibold transition-all ${
                        bedrooms === n
                          ? 'bg-blue-600 text-white border-blue-500 shadow-sm'
                          : 'bg-white/[0.02] text-slate-300 border-white/10 hover:border-white/20'
                      }`}
                    >
                      {n}
                    </button>
                  ))}
                </div>
              </div>

              {/* Bathrooms */}
              <div>
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-2">
                  BATHROOMS
                </label>
                <div className="grid grid-cols-4 gap-3">
                  {[1, 2, 3, 4].map((n) => (
                    <button
                      key={n}
                      type="button"
                      onClick={() => setBathrooms(n)}
                      data-testid={`btn-bathrooms-${n}`}
                      className={`h-12 rounded-xl border text-sm font-semibold transition-all ${
                        bathrooms === n
                          ? 'bg-blue-600 text-white border-blue-500 shadow-sm'
                          : 'bg-white/[0.02] text-slate-300 border-white/10 hover:border-white/20'
                      }`}
                    >
                      {n}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* 2. Floors & Parking */}
            <div className="pw-card p-5 space-y-4">
              {/* Floors */}
              <div>
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-2">
                  FLOORS
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { num: 1, label: 'Ground only' },
                    { num: 2, label: 'G+1' },
                    { num: 3, label: 'G+2' }
                  ].map((f) => (
                    <button
                      key={f.num}
                      type="button"
                      onClick={() => setFloors(f.num)}
                      data-testid={`btn-floors-${f.num}`}
                      className={`h-12 rounded-xl border text-sm font-semibold transition-all ${
                        floors === f.num
                          ? 'bg-blue-600 text-white border-blue-500 shadow-sm'
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
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-2">
                  PARKING
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { count: 0, label: 'No car' },
                    { count: 1, label: '1 car' },
                    { count: 2, label: '2 cars' }
                  ].map((p) => (
                    <button
                      key={p.count}
                      type="button"
                      onClick={() => setParkingCars(p.count)}
                      className={`h-12 rounded-xl border text-sm font-semibold transition-all ${
                        parkingCars === p.count
                          ? 'bg-blue-600 text-white border-blue-500 shadow-sm'
                          : 'bg-white/[0.02] text-slate-300 border-white/10 hover:border-white/20'
                      }`}
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* 3. Style & Budget */}
            <div className="pw-card p-5 space-y-4">
              {/* Style */}
              <div>
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-2">
                  STYLE
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {STYLE_OPTIONS.map((s) => (
                    <button
                      key={s.id}
                      type="button"
                      onClick={() => setPreferredStyle(s.id)}
                      className={`h-12 rounded-xl border text-sm font-semibold transition-all ${
                        preferredStyle === s.id
                          ? 'bg-blue-600 text-white border-blue-500 shadow-sm'
                          : 'bg-white/[0.02] text-slate-300 border-white/10 hover:border-white/20'
                      }`}
                    >
                      {s.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Budget */}
              <div>
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-2">
                  BUDGET
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                  {BUDGET_OPTIONS.map((b) => (
                    <button
                      key={b.value}
                      type="button"
                      onClick={() => setBudgetInr(b.value)}
                      className={`h-12 rounded-xl border text-sm font-semibold transition-all ${
                        budgetInr === b.value
                          ? 'bg-blue-600 text-white border-blue-500 shadow-sm'
                          : 'bg-white/[0.02] text-slate-300 border-white/10 hover:border-white/20'
                      }`}
                    >
                      {b.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* 4. Special Requirements */}
            <div className="pw-card p-5 space-y-3">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block">
                SPECIAL REQUIREMENTS
              </label>
              <div className="flex flex-wrap gap-2.5">
                {SPECIAL_REQUIREMENTS_LIST.map((req) => {
                  const isChecked = selectedSpecial.includes(req);
                  return (
                    <button
                      key={req}
                      type="button"
                      onClick={() => toggleSpecial(req)}
                      className={`px-4 py-2 rounded-xl border text-xs font-semibold transition-all ${
                        isChecked
                          ? 'bg-blue-600 text-white border-blue-500 shadow-sm'
                          : 'bg-white/[0.02] text-slate-300 border-white/10 hover:border-white/20'
                      }`}
                    >
                      {req}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Primary CTA (§8) */}
            <div className="pt-2 flex justify-end">
              <button
                type="submit"
                className="pw-btn pw-btn-primary pw-btn-lg w-full sm:w-auto"
                data-testid="btn-generate-home-options"
              >
                <span>Generate My Home Options</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>

          </form>
        )}

      </div>
    </div>
  );
};
