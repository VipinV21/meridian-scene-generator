import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  BookOpen, 
  Sparkles, 
  CheckCircle2, 
  XCircle, 
  HelpCircle, 
  Eye, 
  EyeOff, 
  Grid, 
  Cpu, 
  RefreshCw,
  FileText
} from 'lucide-react';

interface EpistemicAudit {
  is_epistemically_valid: boolean;
  verification_score: number;
  detected_leaks: string[];
  allowed_knowledge_used: string[];
  forbidden_knowledge_avoided: string[];
  justification: string;
}

interface CaseSample {
  case_number: number;
  character: string;
  point_in_story: string;
  scene_prompt: string;
  scene_text: string;
  word_count: number;
  epistemic_audit: EpistemicAudit;
  allowed_knowledge: string[];
  suspicions_and_misconceptions?: string[];
  forbidden_knowledge: string[];
  test_case_analysis: string;
  generation_mode: string;
}

// Human-readable label + tone for each generation_mode value the backend can return.
function describeGenerationMode(mode: string | undefined): { label: string; isLive: boolean } {
  if (!mode) return { label: 'Unknown', isLive: false };
  if (mode.startsWith('openai_gpt4o')) return { label: 'Live — OpenAI GPT-4o', isLive: true };
  if (mode.startsWith('gemini')) return { label: 'Live — Gemini 1.5 Pro', isLive: true };
  if (mode.startsWith('groq')) return { label: 'Live — Groq Llama 3.3 70B', isLive: true };
  if (mode.includes('using_curated_fallback')) return { label: 'Offline fallback (curated scene, no API key set)', isLive: false };
  if (mode.includes('no_fallback_available')) return { label: 'No scene generated — no API key and no fallback for this input', isLive: false };
  return { label: mode, isLive: false };
}

const API_BASES = [
  import.meta.env.VITE_API_BASE,
  'http://localhost:8001/api',
  'http://localhost:8000/api'
].filter(Boolean) as string[];

async function apiFetch(path: string, options?: RequestInit): Promise<Response> {
  for (const base of API_BASES) {
    try {
      const res = await fetch(`${base}${path}`, options);
      if (res.ok) return res;
    } catch (e) {
      // try next port
    }
  }
  // final attempt
  return fetch(`${API_BASES[0]}${path}`, options);
}

export function App() {
  const [activeTab, setActiveTab] = useState<'samples' | 'generator' | 'matrix'>('samples');
  const [samples, setSamples] = useState<CaseSample[]>([]);
  const [selectedCaseNum, setSelectedCaseNum] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);

  // Custom Generator State
  const [customChar, setCustomChar] = useState<string>('Kamala');
  const [customPoint, setCustomPoint] = useState<string>('end of Ep 5');
  const [customPrompt, setCustomPrompt] = useState<string>('Kamala confronts Dev in the empty auditorium about whether he still wants to be here.');
  const [customResult, setCustomResult] = useState<CaseSample | null>(null);
  const [generating, setGenerating] = useState<boolean>(false);

  // Epistemic Matrix State
  const [matrixData, setMatrixData] = useState<any>(null);

  useEffect(() => {
    fetchSamples();
    fetchMatrix();
  }, []);

  const fetchSamples = async () => {
    try {
      setLoading(true);
      const res = await apiFetch('/samples');
      if (res.ok) {
        const data = await res.json();
        setSamples(data);
      }
    } catch (err) {
      console.error('Failed to fetch samples:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchMatrix = async () => {
    try {
      const res = await apiFetch('/story/epistemic-matrix');
      if (res.ok) {
        const data = await res.json();
        setMatrixData(data);
      }
    } catch (err) {
      console.error('Failed to fetch matrix:', err);
    }
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);
    try {
      const res = await apiFetch('/generate-scene', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          character: customChar,
          point_in_story: customPoint,
          scene_prompt: customPrompt
        })
      });
      if (res.ok) {
        const data = await res.json();
        setCustomResult({
          case_number: 0,
          character: data.character,
          point_in_story: data.point_in_story,
          scene_prompt: data.scene_prompt,
          scene_text: data.scene_text,
          word_count: data.word_count,
          epistemic_audit: data.epistemic_audit,
          allowed_knowledge: data.allowed_knowledge,
          suspicions_and_misconceptions: data.suspicions_and_misconceptions,
          forbidden_knowledge: data.forbidden_knowledge,
          generation_mode: data.generation_mode,
          test_case_analysis: 'Scene generated for a custom character/point/prompt combination, filtered through the same epistemic ledger as the 6 assessment cases.'
        });
      }
    } catch (err) {
      console.error('Generation error:', err);
    } finally {
      setGenerating(false);
    }
  };

  const currentSample = samples.find(s => s.case_number === selectedCaseNum) || samples[0];

  return (
    <div style={{ padding: '24px 40px', maxWidth: '1440px', margin: '0 auto' }}>
      {/* Header */}
      <header className="glass-panel" style={{ padding: '24px 32px', marginBottom: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '6px' }}>
            <BookOpen style={{ color: 'var(--accent-gold)' }} size={28} />
            <h1 className="serif-title" style={{ fontSize: '28px', fontWeight: 700, letterSpacing: '-0.5px' }}>
              The Meridian Company
            </h1>
            <span style={{ 
              background: 'rgba(56, 189, 248, 0.15)', 
              color: 'var(--accent-cyan)', 
              padding: '4px 12px', 
              borderRadius: '20px', 
              fontSize: '12px', 
              fontWeight: 600,
              border: '1px solid rgba(56, 189, 248, 0.3)'
            }}>
              Epistemic Engine v1.0
            </span>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
            Bounded Character Point-of-View Scene Generator & Verification Auditor
          </p>
        </div>

        {/* Tab Selector */}
        <div style={{ display: 'flex', background: 'rgba(15, 23, 42, 0.6)', padding: '6px', borderRadius: '12px', gap: '4px' }}>
          <button 
            onClick={() => setActiveTab('samples')}
            style={{
              padding: '10px 20px',
              borderRadius: '8px',
              border: 'none',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '14px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              background: activeTab === 'samples' ? 'var(--accent-cyan)' : 'transparent',
              color: activeTab === 'samples' ? '#0f172a' : 'var(--text-secondary)',
              transition: 'all 0.2s ease'
            }}
          >
            <Sparkles size={16} /> 6 Assessment Cases
          </button>

          <button 
            onClick={() => setActiveTab('generator')}
            style={{
              padding: '10px 20px',
              borderRadius: '8px',
              border: 'none',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '14px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              background: activeTab === 'generator' ? 'var(--accent-cyan)' : 'transparent',
              color: activeTab === 'generator' ? '#0f172a' : 'var(--text-secondary)',
              transition: 'all 0.2s ease'
            }}
          >
            <Cpu size={16} /> Live Generator
          </button>

          <button 
            onClick={() => setActiveTab('matrix')}
            style={{
              padding: '10px 20px',
              borderRadius: '8px',
              border: 'none',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '14px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              background: activeTab === 'matrix' ? 'var(--accent-cyan)' : 'transparent',
              color: activeTab === 'matrix' ? '#0f172a' : 'var(--text-secondary)',
              transition: 'all 0.2s ease'
            }}
          >
            <Grid size={16} /> Epistemic Matrix
          </button>
        </div>
      </header>

      {/* TAB 1: 6 ASSESSMENT SAMPLES */}
      {activeTab === 'samples' && (
        <div>
          {/* Test Case Picker Pills */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '12px', marginBottom: '28px' }}>
            {[1, 2, 3, 4, 5, 6].map((num) => {
              const sample = samples.find(s => s.case_number === num);
              const isSelected = selectedCaseNum === num;
              return (
                <button
                  key={num}
                  onClick={() => setSelectedCaseNum(num)}
                  className="glass-panel"
                  style={{
                    padding: '16px',
                    textAlign: 'left',
                    cursor: 'pointer',
                    borderColor: isSelected ? 'var(--accent-gold)' : 'var(--border-color)',
                    background: isSelected ? 'rgba(251, 191, 36, 0.1)' : 'var(--bg-card)',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <div style={{ fontSize: '11px', color: 'var(--accent-gold)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>
                    Case {num}
                  </div>
                  <div style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)' }}>
                    {sample ? sample.character : `Case ${num}`}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                    {sample ? sample.point_in_story : ''}
                  </div>
                </button>
              );
            })}
          </div>

          {loading ? (
            <div style={{ textAlign: 'center', padding: '60px' }}>
              <RefreshCw className="spin" size={32} style={{ color: 'var(--accent-cyan)' }} />
              <p style={{ marginTop: '12px', color: 'var(--text-secondary)' }}>Loading Epistemic Audit Data...</p>
            </div>
          ) : currentSample ? (
            <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '28px' }}>
              {/* Left Column: Scene Text & Prompt */}
              <div className="glass-panel" style={{ padding: '32px' }}>
                <div style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '20px', marginBottom: '24px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ color: 'var(--accent-gold)', fontWeight: 700, fontSize: '14px' }}>
                      TEST CASE #{currentSample.case_number}
                    </span>
                    <span className="mono-code" style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                      ~{currentSample.word_count} words
                    </span>
                  </div>
                  <h2 className="serif-title" style={{ fontSize: '24px', fontWeight: 700, marginBottom: '12px' }}>
                    {currentSample.character} — <span style={{ color: 'var(--accent-cyan)' }}>{currentSample.point_in_story}</span>
                  </h2>
                  <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: '14px 18px', borderRadius: '10px', fontSize: '14px', color: 'var(--text-secondary)', borderLeft: '3px solid var(--accent-gold)' }}>
                    <strong>Prompt:</strong> "{currentSample.scene_prompt}"
                  </div>
                </div>

                {/* Generation Mode Badge — how this scene text was actually produced */}
                {(() => {
                  const gm = describeGenerationMode(currentSample.generation_mode);
                  return (
                    <div style={{
                      display: 'inline-flex', alignItems: 'center', gap: '8px',
                      padding: '6px 12px', borderRadius: '999px', fontSize: '12px', fontWeight: 600,
                      background: gm.isLive ? 'rgba(16,185,129,0.15)' : 'rgba(148,163,184,0.15)',
                      color: gm.isLive ? 'var(--accent-emerald)' : 'var(--text-secondary)',
                      border: `1px solid ${gm.isLive ? 'var(--accent-emerald)' : 'var(--text-muted)'}`,
                      width: 'fit-content'
                    }}>
                      <Cpu size={13} />
                      {gm.label}
                    </div>
                  );
                })()}

                {/* Scene Content */}
                <div style={{ fontSize: '15px', lineHeight: '1.8', color: '#e2e8f0', whiteSpace: 'pre-line' }}>
                  {currentSample.scene_text}
                </div>
              </div>

              {/* Right Column: Epistemic Proof & Verification Inspector */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                {/* Audit Verdict Card */}
                <div className="glass-panel" style={{ padding: '24px', borderLeft: `6px solid ${currentSample.epistemic_audit.is_epistemically_valid ? 'var(--accent-emerald)' : 'var(--accent-rose)'}` }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      {currentSample.epistemic_audit.is_epistemically_valid ? (
                        <ShieldCheck size={28} style={{ color: 'var(--accent-emerald)' }} />
                      ) : (
                        <ShieldAlert size={28} style={{ color: 'var(--accent-rose)' }} />
                      )}
                      <div>
                        <h3 style={{ fontSize: '18px', fontWeight: 700 }}>
                          {currentSample.epistemic_audit.is_epistemically_valid ? 'EPISTEMICALLY VALID' : 'BOUNDARY VIOLATION'}
                        </h3>
                        <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Automated Verification Result</span>
                      </div>
                    </div>

                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '24px', fontWeight: 800, color: currentSample.epistemic_audit.is_epistemically_valid ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}>
                        {currentSample.epistemic_audit.verification_score}/100
                      </div>
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Epistemic Verification Score</span>
                    </div>
                  </div>

                  <p style={{ fontSize: '13px', color: '#cbd5e1', lineHeight: '1.5', marginTop: '8px' }}>
                    {currentSample.epistemic_audit.justification}
                  </p>
                </div>

                {/* Why this case is a trap / assessment analysis */}
                <div className="glass-panel" style={{ padding: '20px', background: 'rgba(56, 189, 248, 0.05)', borderColor: 'rgba(56, 189, 248, 0.2)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color: 'var(--accent-cyan)', fontWeight: 700, fontSize: '14px' }}>
                    <HelpCircle size={18} /> Assessment Trap & Design Intent
                  </div>
                  <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                    {currentSample.test_case_analysis}
                  </p>
                </div>

                {/* Allowed Knowledge Panel */}
                <div className="glass-panel" style={{ padding: '20px' }}>
                  <h4 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--accent-emerald)', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                    <Eye size={16} /> Allowed Knowledge Baseline
                  </h4>
                  <ul style={{ listStyle: 'none', fontSize: '13px', color: 'var(--text-secondary)' }}>
                    {currentSample.allowed_knowledge.map((item, idx) => (
                      <li key={idx} style={{ display: 'flex', gap: '8px', marginBottom: '8px', alignItems: 'flex-start' }}>
                        <CheckCircle2 size={14} style={{ color: 'var(--accent-emerald)', flexShrink: 0, marginTop: '3px' }} />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Suspicions & Misconceptions */}
                {currentSample.suspicions_and_misconceptions && currentSample.suspicions_and_misconceptions.length > 0 && (
                  <div className="glass-panel" style={{ padding: '20px', background: 'rgba(251, 191, 36, 0.05)', borderColor: 'rgba(251, 191, 36, 0.2)' }}>
                    <h4 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--accent-gold)', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                      <HelpCircle size={16} /> Inferred Misconceptions & Suspicions
                    </h4>
                    <ul style={{ listStyle: 'none', fontSize: '13px', color: 'var(--text-secondary)' }}>
                      {currentSample.suspicions_and_misconceptions.map((item, idx) => (
                        <li key={idx} style={{ display: 'flex', gap: '8px', marginBottom: '8px', alignItems: 'flex-start' }}>
                          <span style={{ color: 'var(--accent-gold)', fontWeight: 700 }}>•</span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Explicit Forbidden Facts Panel */}
                <div className="glass-panel" style={{ padding: '20px' }}>
                  <h4 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--accent-rose)', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                    <EyeOff size={16} /> Explicit Forbidden Knowledge (Zero-Leakage)
                  </h4>
                  <ul style={{ listStyle: 'none', fontSize: '13px', color: 'var(--text-secondary)' }}>
                    {currentSample.forbidden_knowledge.map((item, idx) => (
                      <li key={idx} style={{ display: 'flex', gap: '8px', marginBottom: '8px', alignItems: 'flex-start' }}>
                        <XCircle size={14} style={{ color: 'var(--accent-rose)', flexShrink: 0, marginTop: '3px' }} />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ) : null}
        </div>
      )}

      {/* TAB 2: LIVE GENERATOR */}
      {activeTab === 'generator' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '28px' }}>
          {/* Controls */}
          <div className="glass-panel" style={{ padding: '28px' }}>
            <h2 className="serif-title" style={{ fontSize: '22px', fontWeight: 700, marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Cpu style={{ color: 'var(--accent-cyan)' }} /> Generate Custom Scene
            </h2>

            <form onSubmit={handleGenerate}>
              <div style={{ marginBottom: '18px' }}>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '6px' }}>
                  Character Point-of-View
                </label>
                <select 
                  value={customChar} 
                  onChange={(e) => setCustomChar(e.target.value)}
                  style={{ width: '100%', padding: '12px', borderRadius: '8px', background: 'var(--bg-secondary)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', fontSize: '14px' }}
                >
                  <option value="Kamala">Kamala (Artistic Director)</option>
                  <option value="Tomas">Tomas (Board Chair / Owner)</option>
                  <option value="Priya">Priya (Stage Manager)</option>
                  <option value="Wren">Wren (Actor / Understudy)</option>
                  <option value="Dev">Dev (Lead Actor)</option>
                </select>
              </div>

              <div style={{ marginBottom: '18px' }}>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '6px' }}>
                  Point in Story (Episode)
                </label>
                <select 
                  value={customPoint} 
                  onChange={(e) => setCustomPoint(e.target.value)}
                  style={{ width: '100%', padding: '12px', borderRadius: '8px', background: 'var(--bg-secondary)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', fontSize: '14px' }}
                >
                  <option value="end of Ep 1">End of Ep 1 (Call Sheet)</option>
                  <option value="end of Ep 2">End of Ep 2 (Blocking)</option>
                  <option value="end of Ep 3">End of Ep 3 (The Grant)</option>
                  <option value="end of Ep 4">End of Ep 4 (Car Park)</option>
                  <option value="end of Ep 5">End of Ep 5 (Dry Run)</option>
                  <option value="end of Ep 6">End of Ep 6 (Closing Night)</option>
                </select>
              </div>

              <div style={{ marginBottom: '24px' }}>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '6px' }}>
                  Scene Prompt
                </label>
                <textarea 
                  rows={4}
                  value={customPrompt} 
                  onChange={(e) => setCustomPrompt(e.target.value)}
                  style={{ width: '100%', padding: '12px', borderRadius: '8px', background: 'var(--bg-secondary)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', fontSize: '14px', lineHeight: '1.5' }}
                />
              </div>

              <button
                type="submit"
                disabled={generating}
                style={{
                  width: '100%',
                  padding: '14px',
                  borderRadius: '10px',
                  border: 'none',
                  background: 'linear-gradient(135deg, var(--accent-cyan), #0284c7)',
                  color: '#0f172a',
                  fontWeight: 700,
                  fontSize: '15px',
                  cursor: 'pointer',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                {generating ? <RefreshCw className="spin" size={18} /> : <Sparkles size={18} />}
                {generating ? 'Enforcing Epistemic Bounds...' : 'Generate & Audit Scene'}
              </button>
            </form>
          </div>

          {/* Results Output */}
          <div className="glass-panel" style={{ padding: '28px' }}>
            {customResult ? (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <h3 className="serif-title" style={{ fontSize: '20px', fontWeight: 700 }}>
                    {customResult.character} — {customResult.point_in_story}
                  </h3>
                  <span className="mono-code" style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    {customResult.word_count} words
                  </span>
                </div>

                {(() => {
                  const gm = describeGenerationMode(customResult.generation_mode);
                  return (
                    <div style={{
                      display: 'inline-flex', alignItems: 'center', gap: '8px',
                      padding: '6px 12px', borderRadius: '999px', fontSize: '12px', fontWeight: 600,
                      background: gm.isLive ? 'rgba(16,185,129,0.15)' : 'rgba(148,163,184,0.15)',
                      color: gm.isLive ? 'var(--accent-emerald)' : 'var(--text-secondary)',
                      border: `1px solid ${gm.isLive ? 'var(--accent-emerald)' : 'var(--text-muted)'}`,
                      width: 'fit-content', marginBottom: '14px'
                    }}>
                      <Cpu size={13} />
                      {gm.label}
                    </div>
                  );
                })()}

                <div style={{
                  background: customResult.epistemic_audit.is_epistemically_valid ? 'rgba(16, 185, 129, 0.1)' : 'rgba(244, 63, 94, 0.1)',
                  border: `1px solid ${customResult.epistemic_audit.is_epistemically_valid ? 'rgba(16, 185, 129, 0.3)' : 'rgba(244, 63, 94, 0.3)'}`,
                  padding: '12px 16px', borderRadius: '8px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px'
                }}>
                  {customResult.epistemic_audit.is_epistemically_valid ? (
                    <ShieldCheck style={{ color: 'var(--accent-emerald)' }} size={20} />
                  ) : (
                    <ShieldAlert style={{ color: 'var(--accent-rose)' }} size={20} />
                  )}
                  <span style={{ fontSize: '13px', color: '#e2e8f0', fontWeight: 600 }}>
                    Verification Score: {customResult.epistemic_audit.verification_score}/100 — {
                      customResult.epistemic_audit.is_epistemically_valid
                        ? 'Zero Leaks Detected'
                        : `${customResult.epistemic_audit.detected_leaks.length} Possible Leak(s) Detected`
                    }
                  </span>
                </div>

                {!customResult.epistemic_audit.is_epistemically_valid && (
                  <div style={{ fontSize: '12px', color: 'var(--accent-rose)', marginBottom: '16px' }}>
                    {customResult.epistemic_audit.detected_leaks.map((leak, i) => (
                      <div key={i}>• {leak}</div>
                    ))}
                  </div>
                )}

                <div style={{ fontSize: '14px', lineHeight: '1.8', color: '#e2e8f0', whiteSpace: 'pre-line', maxHeight: '450px', overflowY: 'auto', paddingRight: '8px' }}>
                  {customResult.scene_text}
                </div>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '80px 20px', color: 'var(--text-muted)' }}>
                <FileText size={48} style={{ opacity: 0.3, marginBottom: '12px' }} />
                <p>Select inputs and click generate to run the epistemic pipeline.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 3: EPISTEMIC MATRIX */}
      {activeTab === 'matrix' && matrixData && (
        <div className="glass-panel" style={{ padding: '32px' }}>
          <h2 className="serif-title" style={{ fontSize: '22px', fontWeight: 700, marginBottom: '8px' }}>
            Story Epistemic Knowledge Matrix
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '24px' }}>
            Complete observer breakdown mapping what each character knows, suspects, or is forbidden from knowing at each episode checkpoint.
          </p>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--border-color)', textAlign: 'left' }}>
                  <th style={{ padding: '12px', color: 'var(--accent-gold)' }}>Character</th>
                  {[1, 2, 3, 4, 5, 6].map(ep => (
                    <th key={ep} style={{ padding: '12px', color: 'var(--accent-cyan)' }}>Ep {ep} Bounds</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Object.keys(matrixData.matrix).map(char => (
                  <tr key={char} style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '16px 12px', fontWeight: 700, color: 'var(--text-primary)' }}>{char}</td>
                    {[1, 2, 3, 4, 5, 6].map(ep => {
                      const ctx = matrixData.matrix[char][ep];
                      return (
                        <td key={ep} style={{ padding: '12px', verticalAlign: 'top', background: 'rgba(15, 23, 42, 0.3)' }}>
                          <div style={{ fontSize: '11px', color: 'var(--accent-emerald)', fontWeight: 600 }}>
                            {ctx.allowed_knowledge ? ctx.allowed_knowledge.length : 0} Known
                          </div>
                          <div style={{ fontSize: '11px', color: 'var(--accent-rose)', fontWeight: 600 }}>
                            {ctx.forbidden_knowledge ? ctx.forbidden_knowledge.length : 0} Forbidden
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
