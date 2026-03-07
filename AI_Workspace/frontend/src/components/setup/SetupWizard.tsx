import React, { useState } from 'react';
import { Building2, Palette, Sparkles, ArrowRight, ArrowLeft, Check, Loader2 } from 'lucide-react';
import { useWorkspace } from '../../context/WorkspaceContext';

interface SetupData {
  name: string;
  tagline: string;
  logo: string;
  primaryColor: string;
  accentColor: string;
}

const STEPS = ['Company Info', 'Branding', 'Review & Launch'];

const defaultData: SetupData = {
  name: '',
  tagline: '',
  logo: '',
  primaryColor: '#3b82f6',
  accentColor: '#8b5cf6',
};

const COLOR_PRESETS = [
  { label: 'Blue', primary: '#3b82f6', accent: '#8b5cf6' },
  { label: 'Emerald', primary: '#10b981', accent: '#06b6d4' },
  { label: 'Rose', primary: '#f43f5e', accent: '#ec4899' },
  { label: 'Amber', primary: '#f59e0b', accent: '#ef4444' },
  { label: 'Indigo', primary: '#6366f1', accent: '#a855f7' },
  { label: 'Teal', primary: '#14b8a6', accent: '#22d3ee' },
];

const SetupWizard: React.FC = () => {
  const { refetch } = useWorkspace();
  const [step, setStep] = useState(0);
  const [data, setData] = useState<SetupData>(defaultData);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const update = (field: keyof SetupData, value: string) => {
    setData(prev => ({ ...prev, [field]: value }));
  };

  const canProceed = step === 0 ? data.name.trim().length > 0 : true;

  const handleSubmit = async () => {
    setSubmitting(true);
    setError(null);
    try {
      const res = await fetch('/api/setup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company: {
            name: data.name.trim(),
            tagline: data.tagline.trim() || undefined,
            logo: data.logo.trim() || undefined,
            primaryColor: data.primaryColor,
            accentColor: data.accentColor,
          },
        }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || 'Setup failed');
      }
      refetch();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 mb-4">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white">Welcome to AI Workspace</h1>
          <p className="text-slate-400 mt-2">Let's set up your workspace in a few quick steps.</p>
        </div>

        {/* Step indicator */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {STEPS.map((label, i) => (
            <div key={label} className="flex items-center gap-2">
              <div
                className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-semibold transition-colors ${
                  i < step
                    ? 'bg-green-500 text-white'
                    : i === step
                    ? 'bg-blue-500 text-white'
                    : 'bg-slate-700 text-slate-400'
                }`}
              >
                {i < step ? <Check className="w-4 h-4" /> : i + 1}
              </div>
              <span className={`text-sm hidden sm:inline ${i === step ? 'text-white' : 'text-slate-500'}`}>
                {label}
              </span>
              {i < STEPS.length - 1 && <div className="w-8 h-px bg-slate-700" />}
            </div>
          ))}
        </div>

        {/* Card */}
        <div className="bg-slate-800 border border-slate-700 rounded-2xl p-8 shadow-xl">
          {/* Step 0 — Company Info */}
          {step === 0 && (
            <div className="space-y-6">
              <div className="flex items-center gap-3 mb-2">
                <Building2 className="w-5 h-5 text-blue-400" />
                <h2 className="text-lg font-semibold text-white">Company Information</h2>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">
                  Company Name <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  value={data.name}
                  onChange={e => update('name', e.target.value)}
                  placeholder="Acme Corp"
                  className="w-full px-4 py-2.5 bg-slate-900 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  autoFocus
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">Tagline</label>
                <input
                  type="text"
                  value={data.tagline}
                  onChange={e => update('tagline', e.target.value)}
                  placeholder="AI-powered everything"
                  className="w-full px-4 py-2.5 bg-slate-900 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">Logo URL</label>
                <input
                  type="url"
                  value={data.logo}
                  onChange={e => update('logo', e.target.value)}
                  placeholder="https://example.com/logo.png"
                  className="w-full px-4 py-2.5 bg-slate-900 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                {data.logo && (
                  <div className="mt-3 flex items-center gap-3">
                    <img
                      src={data.logo}
                      alt="Logo preview"
                      className="w-10 h-10 rounded-lg object-contain bg-slate-700 p-1"
                      onError={e => ((e.target as HTMLImageElement).style.display = 'none')}
                    />
                    <span className="text-xs text-slate-500">Preview</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Step 1 — Branding */}
          {step === 1 && (
            <div className="space-y-6">
              <div className="flex items-center gap-3 mb-2">
                <Palette className="w-5 h-5 text-purple-400" />
                <h2 className="text-lg font-semibold text-white">Brand Colors</h2>
              </div>
              <p className="text-sm text-slate-400">Pick a preset or choose your own colors.</p>

              {/* Presets */}
              <div className="grid grid-cols-3 gap-3">
                {COLOR_PRESETS.map(preset => {
                  const active = data.primaryColor === preset.primary && data.accentColor === preset.accent;
                  return (
                    <button
                      key={preset.label}
                      onClick={() => {
                        update('primaryColor', preset.primary);
                        update('accentColor', preset.accent);
                      }}
                      className={`flex items-center gap-2 px-3 py-2.5 rounded-lg border transition-colors ${
                        active
                          ? 'border-blue-500 bg-slate-700'
                          : 'border-slate-600 bg-slate-800 hover:bg-slate-700'
                      }`}
                    >
                      <div
                        className="w-5 h-5 rounded-full"
                        style={{ background: `linear-gradient(135deg, ${preset.primary}, ${preset.accent})` }}
                      />
                      <span className="text-sm text-white">{preset.label}</span>
                    </button>
                  );
                })}
              </div>

              {/* Custom pickers */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1.5">Primary</label>
                  <div className="flex items-center gap-3">
                    <input
                      type="color"
                      value={data.primaryColor}
                      onChange={e => update('primaryColor', e.target.value)}
                      className="w-10 h-10 rounded-lg border border-slate-600 cursor-pointer bg-transparent"
                    />
                    <span className="text-sm text-slate-400 font-mono">{data.primaryColor}</span>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1.5">Accent</label>
                  <div className="flex items-center gap-3">
                    <input
                      type="color"
                      value={data.accentColor}
                      onChange={e => update('accentColor', e.target.value)}
                      className="w-10 h-10 rounded-lg border border-slate-600 cursor-pointer bg-transparent"
                    />
                    <span className="text-sm text-slate-400 font-mono">{data.accentColor}</span>
                  </div>
                </div>
              </div>

              {/* Live preview bar */}
              <div className="rounded-lg overflow-hidden">
                <div
                  className="h-2"
                  style={{ background: `linear-gradient(90deg, ${data.primaryColor}, ${data.accentColor})` }}
                />
                <div className="bg-slate-900 p-4 flex items-center gap-3">
                  {data.logo && (
                    <img src={data.logo} alt="" className="w-8 h-8 rounded object-contain" />
                  )}
                  <span className="font-semibold text-white">{data.name || 'Your Company'}</span>
                  {data.tagline && (
                    <span className="text-xs text-slate-500 ml-1">— {data.tagline}</span>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Step 2 — Review */}
          {step === 2 && (
            <div className="space-y-6">
              <div className="flex items-center gap-3 mb-2">
                <Sparkles className="w-5 h-5 text-emerald-400" />
                <h2 className="text-lg font-semibold text-white">Review & Launch</h2>
              </div>

              <div className="bg-slate-900 rounded-xl p-5 space-y-4">
                <div className="flex items-center gap-4">
                  {data.logo ? (
                    <img src={data.logo} alt="" className="w-12 h-12 rounded-xl object-contain bg-slate-800 p-1" />
                  ) : (
                    <div
                      className="w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold text-lg"
                      style={{ background: data.primaryColor }}
                    >
                      {data.name.charAt(0).toUpperCase()}
                    </div>
                  )}
                  <div>
                    <h3 className="text-white font-semibold text-lg">{data.name}</h3>
                    {data.tagline && <p className="text-slate-400 text-sm">{data.tagline}</p>}
                  </div>
                </div>

                <div
                  className="h-1.5 rounded-full"
                  style={{ background: `linear-gradient(90deg, ${data.primaryColor}, ${data.accentColor})` }}
                />

                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-slate-500">Primary</span>
                    <div className="flex items-center gap-2 mt-1">
                      <div className="w-4 h-4 rounded" style={{ backgroundColor: data.primaryColor }} />
                      <span className="text-slate-300 font-mono">{data.primaryColor}</span>
                    </div>
                  </div>
                  <div>
                    <span className="text-slate-500">Accent</span>
                    <div className="flex items-center gap-2 mt-1">
                      <div className="w-4 h-4 rounded" style={{ backgroundColor: data.accentColor }} />
                      <span className="text-slate-300 font-mono">{data.accentColor}</span>
                    </div>
                  </div>
                </div>
              </div>

              {error && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 text-red-400 text-sm">
                  {error}
                </div>
              )}
            </div>
          )}

          {/* Navigation buttons */}
          <div className="flex items-center justify-between mt-8 pt-6 border-t border-slate-700">
            {step > 0 ? (
              <button
                onClick={() => setStep(s => s - 1)}
                disabled={submitting}
                className="flex items-center gap-2 px-4 py-2 text-slate-400 hover:text-white transition-colors disabled:opacity-50"
              >
                <ArrowLeft className="w-4 h-4" /> Back
              </button>
            ) : (
              <div />
            )}

            {step < STEPS.length - 1 ? (
              <button
                onClick={() => setStep(s => s + 1)}
                disabled={!canProceed}
                className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Next <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="flex items-center gap-2 px-6 py-2.5 bg-green-600 hover:bg-green-500 text-white rounded-lg font-medium transition-colors disabled:opacity-60"
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" /> Setting up...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" /> Launch Workspace
                  </>
                )}
              </button>
            )}
          </div>
        </div>

        <p className="text-center text-slate-600 text-xs mt-6">
          You can update these settings later from the workspace configuration.
        </p>
      </div>
    </div>
  );
};

export default SetupWizard;
