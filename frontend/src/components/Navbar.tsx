'use client';

import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';
import { HiMoon, HiSun, HiXMark, HiTrash } from 'react-icons/hi2';
import Folder from './Folder';
import styles from './Navbar.module.css';
import {
  CarRecommendation,
  NLPMappingData,
  VikorSensitivityData,
  ClusterDetailData,
} from '@/types';

interface ClusterDist {
  name: string;
  count: number;
  percentage: number;
  color: string;
}

interface ClusterEval {
  silhouette_score: number;
  n_clusters: number;
  total_cars: number;
  cluster_distribution: ClusterDist[];
  features_used: string[];
}

interface HistoryItem {
  id: number;
  user_message: string;
  timestamp: string;
  nlp_preferences: string[];
  nlp_needs: string[];
  nlp_entities: string[];
  cluster_name: string | null;
  hard_filters_applied: Record<string, string>;
  weight_dict_used: Record<string, number>;
  cars_total: number;
  cars_after_constraint: number;
  top_recommendations: CarRecommendation[];
}

const SCENARIO_LABELS: Record<string, { label: string; emoji: string; color: string }> = {
  'A_efficiency_heavy': { label: 'Efisiensi', emoji: '⛽', color: '#00BB77' },
  'B_performance_heavy': { label: 'Performa', emoji: '⚡', color: '#F59E0B' },
  'C_equal_weights': { label: 'Equal', emoji: '⚖️', color: '#4090F7' },
};

const INDEX_SHORT: Record<string, string> = {
  INDEX_PERFORMANCE: '⚡ Perf',
  INDEX_EFFICIENCY: '⛽ Eff',
  INDEX_SAFETY: '🛡 Safe',
  INDEX_DRIVER_COMFORT: '🧑‍✈️ DrvCmf',
  INDEX_PASSENGER_COMFORT: '🛋 PsgCmf',
  INDEX_FUN_TO_DRIVE: '🎮 Fun',
  INDEX_TECH: '📡 Tech',
  INDEX_SPACE: '📦 Space',
  INDEX_OFFROAD: '🏔 Offrd',
  INDEX_LUXURY: '💎 Lux',
  INDEX_POPULARITY: '📈 Pop',
  INDEX_PRICE: '💰 Price',
  INDEX_CLUSTER_MATCH: '🎯 Cluster',
};

export default function Navbar() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [evalOpen, setEvalOpen] = useState(false);

  // Evaluation data
  const [clusterData, setClusterData] = useState<ClusterEval | null>(null);
  const [historyData, setHistoryData] = useState<HistoryItem[]>([]);
  const [nlpMapping, setNlpMapping] = useState<NLPMappingData | null>(null);
  const [vikorSensitivity, setVikorSensitivity] = useState<VikorSensitivityData | null>(null);
  const [clusterDetail, setClusterDetail] = useState<ClusterDetailData | null>(null);
  const [loadingEval, setLoadingEval] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const toggleTheme = () => setTheme(theme === 'dark' ? 'light' : 'dark');

  const openEvalWindow = async () => {
    setEvalOpen(true);
    setLoadingEval(true);
    try {
      const [clusterRes, historyRes, nlpRes, vikorRes, clusterDetailRes] = await Promise.all([
        fetch('http://localhost:8000/evaluasi/clustering'),
        fetch('http://localhost:8000/history'),
        fetch('http://localhost:8000/evaluasi/nlp/mapping'),
        fetch('http://localhost:8000/evaluasi/vikor/sensitivity'),
        fetch('http://localhost:8000/evaluasi/clustering/detail'),
      ]);
      if (clusterRes.ok) setClusterData(await clusterRes.json());
      if (historyRes.ok) setHistoryData(await historyRes.json());
      if (nlpRes.ok) setNlpMapping(await nlpRes.json());
      if (vikorRes.ok) setVikorSensitivity(await vikorRes.json());
      if (clusterDetailRes.ok) setClusterDetail(await clusterDetailRes.json());
    } catch (err) {
      console.error('Failed to fetch eval data:', err);
    } finally {
      setLoadingEval(false);
    }
  };

  const deleteHistory = async (id: number) => {
    try {
      const res = await fetch(`http://localhost:8000/history/${id}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        setHistoryData(prev => prev.filter(h => h.id !== id));
      } else {
        console.error('Failed to delete history item');
      }
    } catch (err) {
      console.error('Error deleting history:', err);
    }
  };

  return (
    <>
      <nav className={styles.navbar}>
        <div className={styles.inner}>
          {/* Logo */}
          <a href="/" className={styles.logo}>
            <div className={styles.logoWordmark}>
              <span className={styles.logoMain}>Otobot</span>
              <span className={styles.logoSub}>Otomotif Bot</span>
            </div>
          </a>

          {/* Center: empty spacer */}
          <div style={{ flex: 1 }} />

          {/* Actions */}
          <div className={styles.actions}>
            {/* Folder Icon — Opens Eval Window */}
            <div
              style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', marginRight: '6px' }}
              title="Evaluasi Sistem"
            >
              <Folder
                size={0.35}
                color="#5227FF"
                onClick={openEvalWindow}
              />
            </div>
            <button className={styles.themeToggle} onClick={toggleTheme} aria-label="Toggle theme">
              {mounted ? (
                theme === 'dark' ? <HiSun size={17} /> : <HiMoon size={17} />
              ) : <span style={{ width: 17, height: 17 }} />}
            </button>
          </div>
        </div>
      </nav>

      {/* ══════════════════════════════════════════ */}
      {/* FULL SYSTEM EVALUATION MODAL               */}
      {/* ══════════════════════════════════════════ */}
      {evalOpen && (
        <div
          style={{
            position: 'fixed', inset: 0, zIndex: 300,
            background: 'rgba(0,0,0,0.65)', backdropFilter: 'blur(6px)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            padding: '20px', animation: 'fadeIn 0.2s ease',
          }}
          onClick={() => setEvalOpen(false)}
        >
          <div
            onClick={e => e.stopPropagation()}
            style={{
              background: 'var(--bg-card)', borderRadius: '20px',
              width: '100%', maxWidth: '780px', maxHeight: '90vh',
              overflowY: 'auto', padding: '28px',
              boxShadow: '0 12px 48px rgba(0,0,0,0.3)',
              border: '1px solid var(--border-color)',
              display: 'flex', flexDirection: 'column', gap: '20px',
              animation: 'fadeUp 0.3s ease',
              position: 'relative',
            }}
          >
            {/* Close button */}
            <button
              onClick={() => setEvalOpen(false)}
              style={{ position: 'absolute', top: '20px', right: '20px', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: '8px', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '1.2rem', width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 10 }}
            >
              <HiXMark />
            </button>

            <div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 800, margin: 0, fontFamily: "'Space Grotesk', sans-serif" }}>
                📐 Evaluasi Matematika Sistem
              </h2>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: '4px 0 0' }}>
                Transparansi ilmiah untuk VIKOR, NLP (Rasa), dan Agglomerative Clustering
              </p>
            </div>

            {loadingEval ? (
              <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)' }}>Memuat data evaluasi...</div>
            ) : (
              <>
                {/* ═══════════════════════════════════════════════════ */}
                {/* SECTION 1: NLP MAPPING ACCURACY                     */}
                {/* ═══════════════════════════════════════════════════ */}
                <Section title="🧠 NLP → Decision Mapping Accuracy" color="#4090F7">
                  {nlpMapping ? (
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.9 }}>
                      {/* Pipeline Config */}
                      <div style={{ marginBottom: '12px' }}>
                        <strong>Pipeline:</strong> {nlpMapping.pipeline_config.pipeline.join(' → ')}
                      </div>
                      <div style={{ marginBottom: '12px' }}>
                        <strong>Entity Types:</strong>{' '}
                        {nlpMapping.pipeline_config.entity_types.map(e => <Badge key={e}>{e}</Badge>)}
                      </div>

                      {/* Overall Accuracy */}
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px', marginBottom: '14px' }}>
                        <MetricCard label="Overall Accuracy" value={`${(nlpMapping.overall_accuracy * 100).toFixed(1)}%`} color="#4090F7" />
                        <MetricCard label="Benar / Total" value={`${nlpMapping.correct} / ${nlpMapping.total}`} color="#00BB77" />
                        <MetricCard label="Jumlah Mapping" value={`${nlpMapping.mapping_tables.preference_index_count + nlpMapping.mapping_tables.preference_cluster_count + nlpMapping.mapping_tables.need_cluster_count}`} color="#8B5CF6" />
                      </div>

                      {/* Per-type accuracy */}
                      <div style={{ marginBottom: '12px' }}>
                        <strong>Accuracy per Tipe Mapping:</strong>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: '6px' }}>
                          {Object.entries(nlpMapping.per_type_accuracy).map(([type, stats]) => (
                            <div key={type} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                              <Badge>{type.replace(/_/g, ' ')}</Badge>
                              <div style={{ flex: 1, height: '6px', borderRadius: '3px', background: 'var(--border-color)' }}>
                                <div style={{ height: '100%', width: `${stats.accuracy * 100}%`, borderRadius: '3px', background: stats.accuracy === 1 ? '#00BB77' : stats.accuracy >= 0.8 ? '#F59E0B' : '#EF4444', transition: 'width 0.6s ease' }} />
                              </div>
                              <span style={{ fontWeight: 700, fontSize: '0.72rem', color: stats.accuracy === 1 ? '#00BB77' : '#F59E0B', minWidth: '60px', textAlign: 'right' }}>
                                {(stats.accuracy * 100).toFixed(0)}% ({stats.correct}/{stats.total})
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Test table */}
                      <div style={{ marginTop: '10px' }}>
                        <strong>Detail Tes Mapping:</strong>
                        <div style={{ maxHeight: '200px', overflowY: 'auto', marginTop: '6px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                          <table style={{ width: '100%', fontSize: '0.7rem', borderCollapse: 'collapse' }}>
                            <thead>
                              <tr style={{ background: 'var(--bg-secondary)', position: 'sticky', top: 0 }}>
                                <th style={{ padding: '6px 8px', textAlign: 'left', fontWeight: 700 }}>Input</th>
                                <th style={{ padding: '6px 8px', textAlign: 'left', fontWeight: 700 }}>Tipe</th>
                                <th style={{ padding: '6px 8px', textAlign: 'left', fontWeight: 700 }}>Expected</th>
                                <th style={{ padding: '6px 8px', textAlign: 'left', fontWeight: 700 }}>Actual</th>
                                <th style={{ padding: '6px 8px', textAlign: 'center', fontWeight: 700 }}>✓</th>
                              </tr>
                            </thead>
                            <tbody>
                              {nlpMapping.test_results.map((r, i) => (
                                <tr key={i} style={{ borderTop: '1px solid var(--border-color)', background: r.correct ? 'rgba(0,187,119,0.04)' : 'rgba(239,68,68,0.04)' }}>
                                  <td style={{ padding: '5px 8px', fontWeight: 600 }}>{r.input}</td>
                                  <td style={{ padding: '5px 8px', color: 'var(--text-muted)' }}>{r.type.replace(/_/g, ' ')}</td>
                                  <td style={{ padding: '5px 8px' }}>{r.expected}</td>
                                  <td style={{ padding: '5px 8px', color: r.correct ? '#00BB77' : '#EF4444', fontWeight: 600 }}>{r.actual}</td>
                                  <td style={{ padding: '5px 8px', textAlign: 'center', fontSize: '0.85rem' }}>{r.correct ? '✅' : '❌'}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>Gagal memuat data NLP mapping.</div>
                  )}
                </Section>

                {/* ═══════════════════════════════════════════════════ */}
                {/* SECTION 2: VIKOR FORMULAS + SENSITIVITY              */}
                {/* ═══════════════════════════════════════════════════ */}
                <Section title="🏆 VIKOR — Sensitivity Analysis" color="#00BB77">
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.9 }}>
                    {/* Formulas */}
                    <FormulaBlock label="S (Group Utility)" formula="S = Σ (wⱼ × Dᵢⱼ)" desc="Total jarak tertimbang alternatif terhadap solusi ideal." />
                    <FormulaBlock label="R (Regret Measure)" formula="R = max (wⱼ × Dᵢⱼ)" desc="Jarak maksimum (worst-case) satu alternatif terhadap solusi ideal." />
                    <FormulaBlock label="Q (Compromise Index)" formula="Q = v(S − S*) / (S⁻ − S*) + (1−v)(R − R*) / (R⁻ − R*)" desc="Indeks kompromi akhir. v = 0.5 (balanced strategy). Semakin kecil Q, semakin baik." />
                    <FormulaBlock label="DQ (Acceptable Advantage)" formula="DQ = 1 / (m − 1)" desc="Threshold minimum jarak Q₁ dan Q₂ agar peringkat 1 dianggap pemenang mutlak." />

                    {/* Sensitivity Results */}
                    {vikorSensitivity ? (
                      <div style={{ marginTop: '16px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                          <strong>Sensitivity Analysis</strong>
                          <span style={{
                            padding: '3px 10px', borderRadius: '20px', fontSize: '0.68rem', fontWeight: 700,
                            background: vikorSensitivity.is_sensitive ? 'rgba(0,187,119,0.12)' : 'rgba(239,68,68,0.12)',
                            color: vikorSensitivity.is_sensitive ? '#00BB77' : '#EF4444',
                            border: `1px solid ${vikorSensitivity.is_sensitive ? 'rgba(0,187,119,0.3)' : 'rgba(239,68,68,0.3)'}`,
                          }}>
                            {vikorSensitivity.is_sensitive ? '✅ SENSITIF' : '⚠️ TIDAK SENSITIF'}
                          </span>
                        </div>
                        <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '12px', fontStyle: 'italic' }}>
                          {vikorSensitivity.sensitivity_proof}
                        </p>

                        {/* Scenario comparison cards */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px' }}>
                          {Object.entries(vikorSensitivity.scenarios).map(([key, sc]) => {
                            const meta = SCENARIO_LABELS[key] || { label: key, emoji: '📊', color: '#888' };
                            return (
                              <div key={key} style={{ padding: '10px', borderRadius: '10px', background: `${meta.color}08`, border: `1px solid ${meta.color}20` }}>
                                <div style={{ fontWeight: 800, fontSize: '0.75rem', color: meta.color, marginBottom: '8px', textAlign: 'center' }}>
                                  {meta.emoji} {meta.label}
                                </div>
                                {sc.top_5.map((car, i) => (
                                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '3px 0', borderTop: i > 0 ? '1px solid var(--border-color)' : 'none', fontSize: '0.68rem' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                      <span style={{
                                        width: '16px', height: '16px', borderRadius: '50%',
                                        background: i === 0 ? meta.color : 'var(--border-color)',
                                        color: i === 0 ? '#fff' : 'var(--text-secondary)',
                                        display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                                        fontSize: '0.55rem', fontWeight: 800,
                                      }}>{i + 1}</span>
                                      <span style={{ fontWeight: 600, maxWidth: '80px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                        {car.model}
                                      </span>
                                    </div>
                                    <span style={{ fontWeight: 700, color: meta.color, fontSize: '0.65rem' }}>
                                      {car.VIKOR_Q.toFixed(3)}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    ) : (
                      <div style={{ color: 'var(--text-muted)', fontSize: '0.72rem', margin: '10px 0' }}>Gagal memuat data sensitivity.</div>
                    )}
                  </div>
                </Section>

                {/* ═══════════════════════════════════════════════════ */}
                {/* SECTION 3: CLUSTERING — STABILITY + SEMANTIC         */}
                {/* ═══════════════════════════════════════════════════ */}
                <Section title="📊 Agglomerative Clustering — Evaluasi Detail" color="#8B5CF6">
                  {clusterData && clusterDetail ? (
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.9 }}>
                      {/* Basic metrics */}
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px', marginBottom: '14px' }}>
                        <MetricCard label="Silhouette Score" value={clusterDetail.stability.current_silhouette.toFixed(4)} color="#8B5CF6" />
                        <MetricCard label="Jumlah Klaster" value={String(clusterData.n_clusters)} color="#00BB77" />
                        <MetricCard label="Total Mobil" value={String(clusterData.total_cars)} color="#4090F7" />
                      </div>

                      {/* Interpretation */}
                      <div style={{
                        padding: '8px 12px', borderRadius: '8px', marginBottom: '14px',
                        background: clusterDetail.stability.current_silhouette > 0.5 ? 'rgba(0,187,119,0.07)' : clusterDetail.stability.current_silhouette > 0.2 ? 'rgba(245,158,11,0.07)' : 'rgba(239,68,68,0.07)',
                        border: `1px solid ${clusterDetail.stability.current_silhouette > 0.5 ? 'rgba(0,187,119,0.2)' : clusterDetail.stability.current_silhouette > 0.2 ? 'rgba(245,158,11,0.2)' : 'rgba(239,68,68,0.2)'}`,
                        fontSize: '0.72rem',
                      }}>
                        <strong>Interpretasi: </strong>{clusterDetail.stability.interpretation}
                      </div>

                      {/* Stability: Silhouette per k */}
                      <div style={{ marginBottom: '16px' }}>
                        <strong>🔬 Stabilitas Cluster (Silhouette per k):</strong>
                        <div style={{ display: 'flex', alignItems: 'flex-end', gap: '8px', marginTop: '10px', height: '100px' }}>
                          {clusterDetail.stability.silhouette_per_k.map(item => {
                            const pct = item.silhouette != null ? Math.max(10, item.silhouette * 200) : 10;
                            const isSelected = item.k === clusterDetail.stability.current_k;
                            return (
                              <div key={item.k} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                                <span style={{ fontSize: '0.62rem', fontWeight: 700, color: isSelected ? '#8B5CF6' : 'var(--text-muted)' }}>
                                  {item.silhouette?.toFixed(3) ?? '-'}
                                </span>
                                <div style={{
                                  width: '100%', height: `${pct}%`, borderRadius: '4px',
                                  background: isSelected ? 'linear-gradient(180deg, #8B5CF6, #6D28D9)' : 'var(--border-color)',
                                  transition: 'height 0.6s ease',
                                  border: isSelected ? '2px solid #8B5CF6' : 'none',
                                }} />
                                <span style={{ fontSize: '0.65rem', fontWeight: isSelected ? 800 : 500, color: isSelected ? '#8B5CF6' : 'var(--text-muted)' }}>
                                  k={item.k}
                                </span>
                              </div>
                            );
                          })}
                        </div>
                        <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '6px', textAlign: 'center' }}>
                          Best k = {clusterDetail.stability.best_k.k} (sil = {clusterDetail.stability.best_k.silhouette.toFixed(4)}) | Digunakan: k = {clusterDetail.stability.current_k}
                        </div>
                      </div>

                      {/* Semantic Validation */}
                      <div style={{ marginBottom: '10px' }}>
                        <strong>🧬 Validasi Semantik Cluster:</strong>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '8px' }}>
                          {Object.entries(clusterDetail.semantic_validation).map(([cname, profile]) => {
                            const clr = {
                              'City Car': '#00BB77', 'Family Car': '#00A693',
                              'Offroad': '#1E6FD9', 'Performance': '#F59E0B',
                              'Luxury': '#8B5CF6',
                            }[cname] || '#00A693';
                            return (
                              <div key={cname} style={{ padding: '10px', borderRadius: '8px', background: `${clr}06`, border: `1px solid ${clr}15` }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                                  <span style={{ fontWeight: 800, color: clr }}>{cname}</span>
                                  <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{profile.count} mobil</span>
                                </div>
                                <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                                  Karakter: <strong style={{ color: 'var(--text-primary)' }}>{profile.character_summary}</strong>
                                </div>
                                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                                  {profile.top_features.map((f, i) => (
                                    <span key={i} style={{
                                      fontSize: '0.62rem', padding: '2px 8px', borderRadius: '4px',
                                      background: `${clr}12`, color: clr, fontWeight: 700,
                                      border: `1px solid ${clr}25`,
                                    }}>
                                      {INDEX_SHORT[f.name] || f.name.replace('INDEX_', '')} = {f.value.toFixed(3)}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>

                      {/* Distribution bars */}
                      <div style={{ marginTop: '12px' }}>
                        <strong>Distribusi Klaster:</strong>
                        {clusterData.cluster_distribution.map(c => (
                          <div key={c.name} style={{ marginBottom: '8px', marginTop: '4px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '3px' }}>
                              <span style={{ fontWeight: 600 }}>{c.name}</span>
                              <span style={{ color: 'var(--text-muted)' }}>{c.count} mobil ({c.percentage}%)</span>
                            </div>
                            <div style={{ height: '6px', borderRadius: '3px', background: 'var(--border-color)' }}>
                              <div style={{ height: '100%', width: `${c.percentage}%`, borderRadius: '3px', background: c.color, transition: 'width 0.6s ease' }} />
                            </div>
                          </div>
                        ))}
                      </div>

                      <div style={{ marginTop: '12px' }}>
                        <strong>Fitur yang digunakan:</strong>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px', marginTop: '6px' }}>
                          {clusterData.features_used.map(f => <Badge key={f}>{f}</Badge>)}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>Gagal memuat data clustering.</div>
                  )}
                </Section>

                {/* ═══════════════════════════════════════════════════ */}
                {/* SECTION 4: ARCHITECTURE                              */}
                {/* ═══════════════════════════════════════════════════ */}
                <Section title="⚙️ Arsitektur Sistem" color="#F59E0B">
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 2 }}>
                    <div><strong>1. NLP (Rasa)</strong> → extract: need, preference, constraint, entity</div>
                    <div><strong>2. Query Builder</strong> → convert: weight_dict, hard_filters, soft_signals</div>
                    <div><strong>3. Clustering</strong> → optional bias (soft constraint via INDEX_CLUSTER_MATCH)</div>
                    <div><strong>4. VIKOR Engine</strong> → solve: conflicting multi-objective optimization</div>
                    <div><strong>5. Relaxation Strategy</strong> → Brand → Powertrain → Budget +30% (last resort)</div>
                  </div>
                </Section>

                {/* ═══════════════════════════════════════════════════ */}
                {/* SECTION 5: HISTORY — ENRICHED                        */}
                {/* ═══════════════════════════════════════════════════ */}
                <Section title="🕒 Riwayat Rekomendasi Terakhir" color="#E11D48">
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                    {historyData.length === 0 ? (
                      <div style={{ textAlign: 'center', padding: '20px', background: 'var(--bg-secondary)', borderRadius: '10px' }}>Belum ada riwayat percakapan. Mulai tanya Otobot!</div>
                    ) : (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        {historyData.slice(0, 5).map((h) => (
                          <div key={h.id} style={{ padding: '16px', borderRadius: '12px', background: 'var(--bg-card)', border: '1px solid var(--border-color)', boxShadow: '0 4px 12px rgba(0,0,0,0.05)', position: 'relative' }}>
                            {/* Delete Button */}
                            <button
                              onClick={(e) => { e.stopPropagation(); deleteHistory(h.id); }}
                              style={{ position: 'absolute', top: '12px', right: '12px', background: 'rgba(225, 29, 72, 0.1)', color: '#E11D48', border: 'none', borderRadius: '6px', padding: '6px 8px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.7rem', fontWeight: 600, transition: 'all 0.2s' }}
                              onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(225, 29, 72, 0.2)'}
                              onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(225, 29, 72, 0.1)'}
                              title="Hapus riwayat ini"
                            >
                              <HiTrash size={14} /> Hapus
                            </button>

                            <div style={{ fontWeight: 800, fontSize: '0.9rem', marginBottom: '12px', color: 'var(--text-primary)', paddingRight: '60px' }}>
                              <span style={{ color: 'var(--text-muted)', fontSize: '0.7rem', display: 'block', fontWeight: 500, marginBottom: '2px' }}>{new Date(h.timestamp).toLocaleString('id-ID', { dateStyle: 'medium', timeStyle: 'short' })}</span>
                              💬 &quot;{h.user_message}&quot;
                            </div>
                            
                            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: '12px', marginBottom: '12px' }}>
                              {/* NLP Sub-module */}
                              <div style={{ background: 'rgba(64,144,247,0.04)', padding: '10px', borderRadius: '8px', border: '1px solid rgba(64,144,247,0.1)' }}>
                                <div style={{ color: '#4090F7', fontWeight: 700, marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>🧠 Pemahaman NLP</div>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '0.75rem' }}>
                                  <div><span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Cari:</span> {h.nlp_needs?.length ? h.nlp_needs.join(', ') : '-'}</div>
                                  <div><span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Syarat Khusus:</span> {h.nlp_entities?.length ? h.nlp_entities.join(', ') : '-'}</div>
                                  <div><span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Preferensi:</span> {h.nlp_preferences?.length ? h.nlp_preferences.join(', ') : '-'}</div>
                                </div>
                              </div>

                              {/* Clustering Sub-module */}
                              <div style={{ background: 'rgba(139,92,246,0.04)', padding: '10px', borderRadius: '8px', border: '1px solid rgba(139,92,246,0.1)' }}>
                                <div style={{ color: '#8B5CF6', fontWeight: 700, marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>📊 Targeting Klaster</div>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '0.75rem' }}>
                                  <div><span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Klaster Utama:</span> {h.cluster_name || 'Global (Seluruh Data)'}</div>
                                  <div><span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Penyaringan Populasi:</span> <br/>{h.cars_total} mobil awal → <strong>{h.cars_after_constraint}</strong> kandidat lolos syarat.</div>
                                </div>
                              </div>
                            </div>

                            {/* Weight Dict Used */}
                            {h.weight_dict_used && Object.keys(h.weight_dict_used).length > 0 && (
                              <div style={{ background: 'rgba(245,158,11,0.04)', padding: '10px 12px', borderRadius: '8px', border: '1px solid rgba(245,158,11,0.1)', marginBottom: '12px' }}>
                                <div style={{ color: '#F59E0B', fontWeight: 700, marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem' }}>⚖️ Bobot VIKOR Ternormalisasi</div>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                                  {Object.entries(h.weight_dict_used)
                                    .sort(([, a], [, b]) => b - a)
                                    .slice(0, 8)
                                    .map(([key, val]) => (
                                      <span key={key} style={{
                                        fontSize: '0.62rem', padding: '2px 7px', borderRadius: '4px',
                                        background: val > 0.1 ? 'rgba(245,158,11,0.12)' : 'var(--bg-secondary)',
                                        color: val > 0.1 ? '#F59E0B' : 'var(--text-muted)',
                                        fontWeight: val > 0.1 ? 700 : 500,
                                        border: `1px solid ${val > 0.1 ? 'rgba(245,158,11,0.25)' : 'var(--border-color)'}`,
                                      }}>
                                        {INDEX_SHORT[key] || key.replace('INDEX_', '')} {(val * 100).toFixed(1)}%
                                      </span>
                                    ))}
                                </div>
                              </div>
                            )}

                            {/* VIKOR Sub-module */}
                            <div style={{ background: 'rgba(0,187,119,0.04)', padding: '10px 12px', borderRadius: '8px', border: '1px solid rgba(0,187,119,0.1)' }}>
                              <div style={{ color: '#00BB77', fontWeight: 700, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '4px' }}>🏆 Ranking VIKOR (Top 3)</div>
                              
                              {h.top_recommendations?.length === 0 ? (
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>Tidak ada kandidat memadai ditemukan.</div>
                              ) : (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                                  {h.top_recommendations?.slice(0, 3).map((car: CarRecommendation, idx: number) => (
                                    <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '6px 8px', background: 'var(--bg-secondary)', borderRadius: '6px', fontSize: '0.75rem' }}>
                                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <span style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: '20px', height: '20px', borderRadius: '50%', background: idx === 0 ? '#00BB77' : 'var(--border-color)', color: idx === 0 ? '#fff' : 'var(--text-secondary)', fontWeight: 800, fontSize: '0.6rem' }}>{idx+1}</span>
                                        <strong style={{ color: 'var(--text-primary)' }}>{car.BRAND} {car.MODEL}</strong>
                                      </div>
                                      <div style={{ textAlign: 'right', display: 'flex', flexDirection: 'column' }}>
                                        <span style={{ fontWeight: 700, color: '#00BB77' }}>Q: {car.VIKOR_Q?.toFixed(4) ?? '-'}</span>
                                        <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>(S: {car.VIKOR_S?.toFixed(3) ?? '-'} | R: {car.VIKOR_R?.toFixed(3) ?? '-'}) — {car.VIKOR_STATUS?.split(' ')[0]}</span>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </Section>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}

/* ── Reusable sub-components ── */

function Section({ title, color, children }: { title: string; color: string; children: React.ReactNode }) {
  return (
    <div style={{ padding: '16px', borderRadius: '14px', background: 'var(--bg-secondary)', border: `1px solid ${color}25` }}>
      <div style={{ fontSize: '0.78rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em', color, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
        {title}
      </div>
      {children}
    </div>
  );
}

function FormulaBlock({ label, formula, desc }: { label: string; formula: string; desc: string }) {
  return (
    <div style={{ marginBottom: '12px', padding: '10px 12px', borderRadius: '10px', background: 'rgba(0,187,119,0.05)', border: '1px solid rgba(0,187,119,0.12)' }}>
      <div style={{ fontWeight: 700, marginBottom: '2px', color: 'var(--text-primary)' }}>{label}</div>
      <code style={{ fontSize: '0.82rem', color: '#00BB77', display: 'block', padding: '4px 0', fontFamily: "'Space Mono', monospace" }}>{formula}</code>
      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{desc}</div>
    </div>
  );
}

function MetricCard({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div style={{ padding: '12px', borderRadius: '10px', background: `${color}08`, border: `1px solid ${color}20`, textAlign: 'center' }}>
      <div style={{ fontSize: '1.2rem', fontWeight: 800, color, fontFamily: "'Space Grotesk', sans-serif" }}>{value}</div>
      <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginTop: '3px' }}>{label}</div>
    </div>
  );
}

function Badge({ children }: { children: React.ReactNode }) {
  return (
    <span style={{ fontSize: '0.65rem', fontWeight: 700, padding: '2px 8px', borderRadius: '5px', background: 'rgba(64,144,247,0.1)', color: '#4090F7', border: '1px solid rgba(64,144,247,0.2)', letterSpacing: '0.03em' }}>
      {children}
    </span>
  );
}
