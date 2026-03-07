import React, { useState } from 'react';
import { Upload, BarChart3, Plus } from 'lucide-react';

const ResumeScreeningPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'jd' | 'screen' | 'results'>('jd');
  const [jdTitle, setJdTitle] = useState('');
  const [jdSkills, setJdSkills] = useState('');
  const [generating, setGenerating] = useState(false);
  const [generatedJD, setGeneratedJD] = useState<Record<string, unknown> | null>(null);

  const generateJD = async () => {
    if (!jdTitle.trim() || generating) return;
    setGenerating(true);

    try {
      const res = await fetch('/api/resume_screening/jd/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: jdTitle,
          skills: jdSkills.split(',').map(s => s.trim()).filter(Boolean),
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setGeneratedJD(data.jd);
      }
    } catch {
      // Handle error silently
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      {/* Tab Bar */}
      <div className="flex gap-1 p-1 bg-slate-800/50 rounded-xl mb-6">
        <button
          onClick={() => setActiveTab('jd')}
          className={`flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'jd' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Plus className="inline w-4 h-4 mr-1" /> JD Generator
        </button>
        <button
          onClick={() => setActiveTab('screen')}
          className={`flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'screen' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Upload className="inline w-4 h-4 mr-1" /> Screen Resumes
        </button>
        <button
          onClick={() => setActiveTab('results')}
          className={`flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'results' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
          }`}
        >
          <BarChart3 className="inline w-4 h-4 mr-1" /> Results
        </button>
      </div>

      {/* JD Generator Tab */}
      {activeTab === 'jd' && (
        <div className="bg-slate-800/30 rounded-2xl border border-slate-700/50 p-6">
          <h3 className="text-lg font-semibold text-white mb-6">Generate Job Description</h3>
          <div className="space-y-4">
            <div>
              <label className="text-sm text-slate-400 block mb-1.5">Job Title</label>
              <input
                type="text"
                value={jdTitle}
                onChange={(e) => setJdTitle(e.target.value)}
                placeholder="e.g. Senior Full Stack Developer"
                className="w-full bg-slate-700/50 border border-slate-600/50 rounded-xl px-4 py-3 text-white placeholder-slate-400 text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="text-sm text-slate-400 block mb-1.5">Required Skills (comma-separated)</label>
              <input
                type="text"
                value={jdSkills}
                onChange={(e) => setJdSkills(e.target.value)}
                placeholder="e.g. React, Node.js, PostgreSQL, AWS"
                className="w-full bg-slate-700/50 border border-slate-600/50 rounded-xl px-4 py-3 text-white placeholder-slate-400 text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
            <button
              onClick={generateJD}
              disabled={generating || !jdTitle.trim()}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-xl transition-colors font-medium"
            >
              {generating ? 'Generating...' : 'Generate JD with AI'}
            </button>
          </div>

          {generatedJD && (
            <div className="mt-6 p-4 bg-slate-700/30 rounded-xl border border-slate-600/30">
              <h4 className="text-md font-semibold text-white mb-3">Generated JD</h4>
              <pre className="text-sm text-slate-300 whitespace-pre-wrap">
                {JSON.stringify(generatedJD, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Screen Resumes Tab */}
      {activeTab === 'screen' && (
        <div className="bg-slate-800/30 rounded-2xl border border-slate-700/50 p-6">
          <div className="text-center py-12">
            <div className="w-20 h-20 bg-blue-500/10 rounded-2xl flex items-center justify-center mx-auto mb-4 border-2 border-dashed border-blue-500/30">
              <Upload className="w-8 h-8 text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Upload Resumes</h3>
            <p className="text-slate-400 text-sm mb-6">
              Upload PDF or DOCX resumes to screen against a job description.
            </p>
            <label className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-colors font-medium cursor-pointer inline-block">
              Select Files
              <input type="file" className="hidden" accept=".pdf,.docx,.doc" multiple />
            </label>
          </div>
        </div>
      )}

      {/* Results Tab */}
      {activeTab === 'results' && (
        <div className="bg-slate-800/30 rounded-2xl border border-slate-700/50 p-6">
          <div className="text-center py-12">
            <BarChart3 className="w-12 h-12 text-slate-500 mx-auto mb-3" />
            <h3 className="text-lg font-semibold text-white mb-2">Screening Results</h3>
            <p className="text-slate-400 text-sm">
              Results will appear here after screening resumes.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResumeScreeningPage;
