
'use client';

import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';
import { HiMoon, HiSun, HiXMark, HiTrash, HiArrowLeft, HiMicrophone, HiAdjustmentsHorizontal, HiChartBar, HiClipboardDocumentCheck, HiMagnifyingGlassCircle, HiBeaker } from 'react-icons/hi2';
import Link from 'next/link';
import Folder from './Folder';
import styles from './Navbar.module.css';
import { useScientificMode } from '@/lib/ScientificModeContext';
import {
  CarRecommendation,
  NLPMappingData,
  VikorSensitivityData,
  ClusterDetailData,
  NLPBaselineData,
  NLPGap,
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

const INDEX_SHORT: Record<string, string> = {
  INDEX_POWER: '⚡ Power',
  INDEX_HANDLING: '🛞 Hndl',
  INDEX_EFFICIENCY: '⛽ Eff',
  INDEX_SAFETY: '🛡 Safe',
  INDEX_DRIVER_COMFORT: '🧑‍✈️ DrvCmf',
  INDEX_PASSENGER_COMFORT: '🛋 PsgCmf',
  INDEX_TECH: '📡 Tech',
  INDEX_SPACE: '📦 Space',
  INDEX_OFFROAD: '🏔 Offrd',
  INDEX_LUXURY: '💎 Lux',
  INDEX_LIFECYCLE_SAFE: '⏳ Safe',
  INDEX_BRAND_STRENGTH: '📈 Brand',
  INDEX_PRICE: '💰 Val',
  INDEX_CLUSTER_MATCH: '🎯 Cluster',
};

type EvalViewMode = 'history_list' | 'chat_detail' | 'system_metrics';
type ChatDetailTab = 'nlp' | 'filter' | 'vikor' | 'trace';

export default function Navbar() {
  const { theme, setTheme } = useTheme();
  const { isScientific, toggleScientific } = useScientificMode();
  const [mounted, setMounted] = useState(false);
  const [evalOpen, setEvalOpen] = useState(false);

  // States for new UI redesign
  const [viewMode, setViewMode] = useState<EvalViewMode>('history_list');
  const [selectedChat, setSelectedChat] = useState<HistoryItem | null>(null);
  const [chatTab, setChatTab] = useState<ChatDetailTab>('nlp');

  // Evaluation Data
  const [clusterData, setClusterData] = useState<ClusterEval | null>(null);
  const [historyData, setHistoryData] = useState<HistoryItem[]>([]);
  const [nlpMapping, setNlpMapping] = useState<NLPMappingData | null>(null);
  const [nlpBaseline, setNlpBaseline] = useState<NLPBaselineData | null>(null);
  const [vikorSensitivity, setVikorSensitivity] = useState<VikorSensitivityData | null>(null);
  const [clusterDetail, setClusterDetail] = useState<ClusterDetailData | null>(null);
  const [loadingEval, setLoadingEval] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const toggleTheme = () => setTheme(theme === 'dark' ? 'light' : 'dark');

  const openEvalWindow = async () => {
    setEvalOpen(true);
    setViewMode('history_list');
    setLoadingEval(true);
    try {
      const [clusterRes, historyRes, nlpRes, nlpBaselineRes, vikorRes, clusterDetailRes] = await Promise.all([
        fetch('http://localhost:8000/evaluasi/clustering'),
        fetch('http://localhost:8000/history'),
        fetch('http://localhost:8000/evaluasi/nlp/mapping'),
        fetch('http://localhost:8000/evaluasi/nlp/baseline'),
        fetch('http://localhost:8000/evaluasi/vikor/sensitivity'),
        fetch('http://localhost:8000/evaluasi/clustering/detail'),
      ]);
      if (clusterRes.ok) setClusterData(await clusterRes.json());
      if (historyRes.ok) setHistoryData(await historyRes.json());
      if (nlpRes.ok) setNlpMapping(await nlpRes.json());
      if (nlpBaselineRes.ok) setNlpBaseline(await nlpBaselineRes.json());
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
      const res = await fetch(`http://localhost:8000/history/${id}`, { method: 'DELETE' });
      if (res.ok) setHistoryData(prev => prev.filter(h => h.id !== id));
    } catch (err) {
      console.error('Error deleting history:', err);
    }
  };

  const openChatDetail = (chat: HistoryItem) => {
    setSelectedChat(chat);
    setChatTab('nlp');
    setViewMode('chat_detail');
  };

  return (
    <>
      <nav className={styles.navbar}>
        <div className={styles.inner}>
          <a href="/" className={styles.logo}>
            <div className={styles.logoWordmark}>
              <span className={styles.logoMain}>Otobot</span>
              <span className={styles.logoSub}>Otomotif Bot</span>
            </div>
          </a>
          <div style={{ flex: 1 }} />
          <div className={styles.actions}>
            {/* Scientific Mode Toggle */}
            <button
              onClick={toggleScientific}
              title={isScientific ? 'Debug Mode aktif — klik untuk Mode Normal' : 'Mode Normal aktif — klik untuk Debug Mode'}
              aria-label="Toggle Scientific Mode"
              style={{
                display: 'flex', alignItems: 'center', gap: '6px',
                padding: '5px 12px', borderRadius: '20px', cursor: 'pointer',
                fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.02em',
                border: `1.5px solid ${isScientific ? 'rgba(139,92,246,0.5)' : 'var(--border-color)'}`,
                background: isScientific ? 'rgba(139,92,246,0.12)' : 'var(--bg-secondary)',
                color: isScientific ? '#8B5CF6' : 'var(--text-muted)',
                transition: 'all 0.3s ease', marginRight: '4px',
              }}
            >
              <span style={{ display: 'inline-block', width: '28px', height: '16px', borderRadius: '10px', background: isScientific ? '#8B5CF6' : 'var(--border-color)', position: 'relative', transition: 'background 0.3s ease' }}>
                <span style={{ position: 'absolute', top: '2px', left: isScientific ? '14px' : '2px', width: '12px', height: '12px', borderRadius: '50%', background: '#fff', transition: 'left 0.3s ease', boxShadow: '0 1px 3px rgba(0,0,0,0.2)' }} />
              </span>
              🔬 {isScientific ? 'Debug Mode' : 'Normal'}
            </button>

            {isScientific && (
              <>
                <Link
                  href="/debug-nlu"
                  title="Buka Dashboard Kualitas NLU (Visual)"
                  style={{
                    display: 'flex', alignItems: 'center', gap: '6px',
                    padding: '5px 12px', borderRadius: '20px', cursor: 'pointer',
                    fontSize: '0.72rem', fontWeight: 700,
                    border: '1.5px solid rgba(0,187,119,0.5)',
                    background: 'rgba(0,187,119,0.1)',
                    color: '#00BB77',
                    transition: 'all 0.3s ease', marginRight: '6px',
                  }}
                >
                  <HiBeaker size={14} /> NLU
                </Link>
                <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', marginRight: '6px' }} title="Evaluasi Sistem">
                  <Folder size={0.25} color="#f79809ff" onClick={openEvalWindow} />
                </div>
              </>
            )}
            <button className={styles.themeToggle} onClick={toggleTheme} aria-label="Toggle theme">
              {mounted ? (theme === 'dark' ? <HiSun size={17} /> : <HiMoon size={17} />) : <span style={{ width: 17, height: 17 }} />}
            </button>
          </div>
        </div>
      </nav>

      {/* FULL SYSTEM EVALUATION MODAL */}
      {evalOpen && (
        <div
          style={{ position: 'fixed', inset: 0, zIndex: 300, background: 'rgba(0,0,0,0.65)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px', animation: 'fadeIn 0.2s ease' }}
          onClick={() => setEvalOpen(false)}
        >
          <div
            onClick={e => e.stopPropagation()}
            style={{
              background: 'var(--bg-card)', borderRadius: '20px',
              width: '100%', maxWidth: '900px', maxHeight: '92vh', height: '100%',
              overflow: 'hidden', padding: '0',
              boxShadow: '0 24px 64px rgba(0,0,0,0.4)',
              border: '1px solid var(--border-color)',
              display: 'flex', flexDirection: 'column',
              animation: 'fadeUp 0.3s ease', position: 'relative',
            }}
          >
            {/* Modal Header */}
            <div style={{ padding: '24px 28px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-card)', zIndex: 20 }}>
              <div>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 800, margin: 0, fontFamily: "'Space Grotesk', sans-serif", color: 'var(--text-primary)' }}>
                  {viewMode === 'history_list' && '💬 Riwayat Konsultasi'}
                  {viewMode === 'chat_detail' && '🔍 Rincian Analisis AI'}
                  {viewMode === 'system_metrics' && '📐 Metrik Sistem Keseluruhan'}
                </h2>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: '6px 0 0' }}>
                  {viewMode === 'history_list' && 'Pilih obrolan Anda untuk melihat logika bagaimana AI memberikan rekomendasi.'}
                  {viewMode === 'chat_detail' && 'Membedah bagaimana pesan Anda diproses secara matematis.'}
                  {viewMode === 'system_metrics' && 'Data akurasi NLP, stabilitas Clustering, dan sensitivitas MCDM.'}
                </p>
              </div>
              <button
                onClick={() => setEvalOpen(false)}
                style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: '8px', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '1.2rem', width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                aria-label="Tutup"
              >
                <HiXMark />
              </button>
            </div>

            {/* Modal Body / Scrollable Area */}
            <div style={{ flex: 1, overflowY: 'auto' }}>
              {loadingEval ? (
                <div style={{ textAlign: 'center', padding: '100px 0', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  <div style={{ fontSize: '2rem', marginBottom: '12px' }}>⏳</div>
                  Memuat log percakapan...
                </div>
              ) : (
                <div style={{ padding: '24px 28px' }}>

                  {/* LAYER 1: HISTORY LIST */}
                  {viewMode === 'history_list' && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                      {historyData.length === 0 ? (
                        <EmptyState text="Belum ada riwayat konsultasi. Silakan cari mobil terlebih dahulu." />
                      ) : (
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '12px' }}>
                          {historyData.map(h => (
                            <div
                              key={h.id}
                              onClick={() => openChatDetail(h)}
                              style={{ padding: '16px 20px', borderRadius: '12px', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', cursor: 'pointer', position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'space-between', transition: 'all 0.2s ease', boxShadow: '0 2px 8px rgba(0,0,0,0.03)' }}
                              onMouseEnter={(e) => e.currentTarget.style.borderColor = '#4090F7'}
                              onMouseLeave={(e) => e.currentTarget.style.borderColor = 'var(--border-color)'}
                            >
                              <div style={{ flex: 1 }}>
                                <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: 600 }}>
                                  {new Date(h.timestamp).toLocaleString('id-ID', { dateStyle: 'long', timeStyle: 'short' })}
                                </div>
                                <div style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                                  "{h.user_message}"
                                </div>
                              </div>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                <button
                                  onClick={(e) => { e.stopPropagation(); deleteHistory(h.id); }}
                                  style={{ padding: '6px', background: 'transparent', border: 'none', color: '#EF4444', cursor: 'pointer', borderRadius: '6px' }}
                                  title="Hapus History"
                                >
                                  <HiTrash size={16} />
                                </button>
                                <div style={{ background: 'rgba(64,144,247,0.1)', color: '#4090F7', padding: '6px 12px', borderRadius: '8px', fontSize: '0.72rem', fontWeight: 700 }}>
                                  Lihat Keputusan →
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}

                      <div style={{ marginTop: '20px', paddingTop: '24px', borderTop: '1px dashed var(--border-color)', textAlign: 'center' }}>
                        <button
                          onClick={() => setViewMode('system_metrics')}
                          style={{ background: 'rgba(139,92,246,0.08)', color: '#8B5CF6', border: '1px solid rgba(139,92,246,0.25)', padding: '10px 20px', borderRadius: '10px', fontSize: '0.8rem', fontWeight: 700, cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '8px', transition: 'all 0.25s ease' }}
                          onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(139,92,246,0.15)'}
                          onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(139,92,246,0.08)'}
                        >
                          <HiChartBar size={16} /> Buka Laporan Teknis Keseluruhan Sistem
                        </button>
                        <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: '8px 0 0' }}>Data Baseline NLP, Uji Sensitivitas VIKOR, dan Cluster Distribution.</p>
                      </div>
                    </div>
                  )}

                  {/* LAYER 2: CHAT DETAIL VIEW */}
                  {viewMode === 'chat_detail' && selectedChat && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                      <button onClick={() => setViewMode('history_list')} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', background: 'transparent', border: 'none', cursor: 'pointer', padding: '0', alignSelf: 'flex-start' }}>
                        <HiArrowLeft size={14} /> Kembali ke Daftar Chat
                      </button>

                      {/* Chat Input Bubble */}
                      <div style={{ padding: '20px', background: 'rgba(64,144,247,0.08)', border: '1px solid rgba(64,144,247,0.2)', borderRadius: '12px', display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
                        <div style={{ background: '#4090F7', color: '#fff', borderRadius: '50%', width: '36px', height: '36px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem', boxShadow: '0 4px 12px rgba(64,144,247,0.3)' }}>User</div>
                        <div>
                          <div style={{ fontSize: '0.7rem', color: '#4090F7', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>Input Pengguna</div>
                          <div style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)' }}>"{selectedChat.user_message}"</div>
                        </div>
                      </div>

                      {/* TABS FOR DETAILS */}
                      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1fr) minmax(0,1fr) minmax(0,1fr) minmax(0,1fr)', gap: '8px', padding: '4px', background: 'var(--bg-secondary)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                        <button onClick={() => setChatTab('nlp')} style={{ padding: '10px', borderRadius: '8px', border: 'none', background: chatTab === 'nlp' ? 'var(--bg-card)' : 'transparent', color: chatTab === 'nlp' ? '#4090F7' : 'var(--text-muted)', fontWeight: 800, fontSize: '0.75rem', cursor: 'pointer', transition: 'all 0.2s ease', boxShadow: chatTab === 'nlp' ? '0 2px 8px rgba(0,0,0,0.05)' : 'none', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '6px' }}>
                          <HiMicrophone size={16} /> 1. NLP Pemahaman
                        </button>
                        <button onClick={() => setChatTab('filter')} style={{ padding: '10px', borderRadius: '8px', border: 'none', background: chatTab === 'filter' ? 'var(--bg-card)' : 'transparent', color: chatTab === 'filter' ? '#8B5CF6' : 'var(--text-muted)', fontWeight: 800, fontSize: '0.75rem', cursor: 'pointer', transition: 'all 0.2s ease', boxShadow: chatTab === 'filter' ? '0 2px 8px rgba(0,0,0,0.05)' : 'none', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '6px' }}>
                          <HiAdjustmentsHorizontal size={16} /> 2. Kategori Filter
                        </button>
                        <button onClick={() => setChatTab('vikor')} style={{ padding: '10px', borderRadius: '8px', border: 'none', background: chatTab === 'vikor' ? 'var(--bg-card)' : 'transparent', color: chatTab === 'vikor' ? '#00BB77' : 'var(--text-muted)', fontWeight: 800, fontSize: '0.75rem', cursor: 'pointer', transition: 'all 0.2s ease', boxShadow: chatTab === 'vikor' ? '0 2px 8px rgba(0,0,0,0.05)' : 'none', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '6px' }}>
                          <HiChartBar size={16} /> 3. Skoring VIKOR
                        </button>
                        <button onClick={() => setChatTab('trace')} style={{ padding: '10px', borderRadius: '8px', border: 'none', background: chatTab === 'trace' ? 'var(--bg-card)' : 'transparent', color: chatTab === 'trace' ? '#F59E0B' : 'var(--text-muted)', fontWeight: 800, fontSize: '0.75rem', cursor: 'pointer', transition: 'all 0.2s ease', boxShadow: chatTab === 'trace' ? '0 2px 8px rgba(0,0,0,0.05)' : 'none', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '6px' }}>
                          <HiClipboardDocumentCheck size={16} /> 4. Execution Trace Log
                        </button>
                      </div>


                      {/* TAB CONTENTS (SIMPLIFIED TERMS) */}
                      <div style={{ padding: '20px', border: '1px solid var(--border-color)', borderRadius: '12px', background: 'var(--bg-card)' }}>
                        {/* NLP TAB */}
                        {chatTab === 'nlp' && (
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', animation: 'fadeIn 0.2s ease' }}>
                            <div style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                              <div style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>📐 NLU Processing Math (DIET Classifier)</div>
                              <div style={{ fontSize: '0.75rem', color: '#4090F7', fontFamily: "'Fira Code', 'Courier New', monospace" }}>L_total = L_intent + L_entity + L_mask</div>
                              <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                                Ekstraksi makna dan entitas bahasa alami melalui Dual Intent & Entity Transformer architecture dengan sparse (TF-IDF/ngram) dan dense (ConveRT) featurizers.
                              </div>
                            </div>

                            <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '12px' }}>
                              <div style={{ padding: '14px', borderRadius: '10px', background: 'var(--bg-card)', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                <div style={{ fontSize: '0.7rem', fontWeight: 800, color: '#4090F7', textTransform: 'uppercase' }}>Classification Tensor: Y_pred (Intent)</div>
                                <div style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-primary)', fontFamily: "'Fira Code', 'Courier New', monospace", padding: '10px', background: 'rgba(64,144,247,0.08)', borderRadius: '8px', border: '1px solid rgba(64,144,247,0.2)' }}>
                                  {"P(y|x) = softmax( W_2 · GELU(W_1 · h_{CLS} + b_1) + b_2 )"}<br /><br />
                                  {"argmax(P) ➔ "} [ {selectedChat.nlp_needs?.length > 0 ? selectedChat.nlp_needs.map(n => `"${n}"`).join(', ') : 'Ø (Fallback)'} ]
                                </div>
                              </div>

                              <div style={{ padding: '14px', borderRadius: '10px', background: 'var(--bg-card)', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                <div style={{ fontSize: '0.7rem', fontWeight: 800, color: '#EF4444', textTransform: 'uppercase' }}>Sequence Tagging: CRF Layer (Entities)</div>
                                <div style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-primary)', fontFamily: "'Fira Code', 'Courier New', monospace", padding: '10px', background: 'rgba(239,68,68,0.08)', borderRadius: '8px', border: '1px solid rgba(239,68,68,0.2)' }}>
                                  {"arg max_y P(y|X) ∝ exp( Σ_{i} Φ(y_{i-1}, y_i, X, i) )"}<br /><br />
                                  {"X_entities ➔ "} [ {selectedChat.nlp_entities?.length > 0 ? selectedChat.nlp_entities.map(e => `"${e}"`).join(', ') : 'Ø'} ]
                                </div>
                              </div>

                              <div style={{ padding: '14px', borderRadius: '10px', background: 'var(--bg-card)', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                <div style={{ fontSize: '0.7rem', fontWeight: 800, color: '#F59E0B', textTransform: 'uppercase' }}>Semantic Lexicon Vector (Mapping Matrix)</div>
                                <div style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-primary)', fontFamily: "'Fira Code', 'Courier New', monospace", padding: '10px', background: 'rgba(245,158,11,0.08)', borderRadius: '8px', border: '1px solid rgba(245,158,11,0.2)' }}>
                                  {"f_{map} : X_{lex} ➔ V_{MCDM}"}<br /><br />
                                  {"V_mapped ➔ "} [ {selectedChat.nlp_preferences?.length > 0 ? selectedChat.nlp_preferences.map(p => `"${p}"`).join(', ') : 'Ø'} ]
                                </div>
                              </div>
                            </div>
                          </div>
                        )}
                        {/* FILTER & CLUSTER TAB */}
                        {chatTab === 'filter' && (
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', animation: 'fadeIn 0.2s ease' }}>
                            <div style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                              <div style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>📐 Sub-space Filtering (HAC Ward&apos;s Method)</div>
                              <div style={{ fontSize: '0.75rem', color: '#8B5CF6', fontFamily: "'Fira Code', 'Courier New', monospace" }}>{"Δ(A, B) = || x_A - x_B ||²"}</div>
                              <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                                Reduksi dimensi data mobil (Boolean Array Filter) sebelum MCDM dimulai. Hanya mobil yang memenuhi hard constraint (Ω_c) dan centroid klaster terkait yang lolos.
                              </div>
                            </div>

                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
                              <div style={{ padding: '20px', borderRadius: '12px', background: 'var(--bg-card)', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
                                <div style={{ fontSize: '0.75rem', fontWeight: 800, color: '#8B5CF6', marginBottom: '12px', textTransform: 'uppercase' }}>Target Cluster Set (C_k)</div>
                                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)', fontFamily: "'Space Grotesk', sans-serif" }}>
                                  {selectedChat.cluster_name || 'C_Global (All)'}
                                </div>
                                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '8px' }}>Centroid pencarian dipersempit.</div>
                              </div>

                              <div style={{ padding: '20px', borderRadius: '12px', background: 'var(--bg-card)', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
                                <div style={{ fontSize: '0.75rem', fontWeight: 800, color: '#1E6FD9', marginBottom: '12px', textTransform: 'uppercase' }}>Boolean Constraint Set (Ω)</div>
                                <div style={{ width: '100%', display: 'flex', justifyContent: 'space-around', alignItems: 'center' }}>
                                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 800 }}>Awal (N)</span>
                                    <span style={{ fontSize: '1.4rem', color: '#EF4444', fontWeight: 800, fontFamily: "'Fira Code', 'Courier New', monospace" }}>{selectedChat.cars_total}</span>
                                  </div>
                                  <span style={{ fontSize: '1.5rem', color: 'var(--text-muted)' }}>➔</span>
                                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 800 }}>Lolos (N&apos;)</span>
                                    <span style={{ fontSize: '1.8rem', color: '#00BB77', fontWeight: 800, fontFamily: "'Fira Code', 'Courier New', monospace" }}>{selectedChat.cars_after_constraint}</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        )}
                        {/* VIKOR TAB */}
                        {chatTab === 'vikor' && (
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', animation: 'fadeIn 0.2s ease' }}>
                            <div style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                               <div style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>⚖️ MCDM Calculation (VIKOR Core)</div>
                               <div style={{ fontSize: '0.75rem', color: '#00BB77', fontFamily: "'Fira Code', 'Courier New', monospace" }}>{"Q_j = v * ((S_j - S^*) / (S^- - S^*)) + (1-v) * ((R_j - R^*) / (R^- - R^*))"}</div>
                               <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                                  Dimana v = 0.5 merepresentasikan 'Majority of Criteria' (Utility kompromi berimbang). Nilai Q yang lebih kecil menunjukkan kedekatan terhadap solusi ideal positif (Positive Ideal Solution).
                               </div>
                            </div>
                            
                            <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '16px' }}>
                              <div style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '12px', textTransform: 'uppercase' }}>Weight Vector Array (W_j)</div>
                              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', background: 'var(--bg-secondary)', padding: '12px', borderRadius: '8px', border: '1px dashed var(--border-color)' }}>
                                {selectedChat.weight_dict_used ? Object.entries(selectedChat.weight_dict_used).sort(([, a], [, b]) => b - a).slice(0, 8).map(([k, v]) => (
                                  <span key={k} style={{ fontSize: '0.72rem', padding: '6px 10px', borderRadius: '6px', background: v > 0.15 ? 'rgba(0,187,119,0.15)' : 'var(--bg-card)', color: v > 0.15 ? '#00BB77' : 'var(--text-muted)', fontWeight: v > 0.15 ? 800 : 600, border: `1px solid ${v > 0.15 ? 'rgba(0,187,119,0.4)' : 'var(--border-color)'}`, fontFamily: "'Fira Code', 'Courier New', monospace" }}>
                                     {INDEX_SHORT[k] || k.replace('INDEX_', '')}: {v.toFixed(3)}
                                  </span>
                                )) : <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>w_j = 1/n (Uniform / Unweighted)</div>}
                              </div>
                            </div>

                            <div style={{ border: '1px solid var(--border-color)', borderRadius: '12px', overflow: 'hidden' }}>
                              <div style={{ padding: '14px 16px', background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-color)' }}>
                                <div style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-primary)' }}>Matriks S, R, Q (Output Peringkat)</div>
                              </div>
                              <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
                                {selectedChat.top_recommendations?.slice(0, 3).map((car, idx) => (
                                  <div key={idx} style={{ padding: '14px 16px', background: 'var(--bg-card)', borderBottom: idx !== 2 ? '1px dashed var(--border-color)' : 'none', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                                      <div style={{ background: idx === 0 ? '#00BB77' : 'var(--bg-secondary)', color: idx === 0 ? '#fff' : 'var(--text-secondary)', width: '32px', height: '32px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: '0.85rem' }}>{idx + 1}</div>
                                      <div>
                                        <div style={{ fontWeight: 800, color: 'var(--text-primary)', fontSize: '0.9rem' }}>{car.BRAND} {car.MODEL}</div>
                                        <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', fontFamily: "'Fira Code', 'Courier New', monospace", marginTop: '4px' }}>
                                          Utility S: {car.VIKOR_S?.toFixed(4) || 'N/A'} <span style={{ opacity: 0.5 }}>|</span> Regret R: {car.VIKOR_R?.toFixed(4) || 'N/A'}
                                        </div>
                                      </div>
                                    </div>
                                    <div style={{ textAlign: 'right' }}>
                                      <div style={{ fontWeight: 800, fontSize: '0.7rem', color: '#00BB77', textTransform: 'uppercase' }}>Nilai Q</div>
                                      <div style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)', fontFamily: "'Fira Code', 'Courier New', monospace" }}>{car.VIKOR_Q?.toFixed(4) || 'N/A'}</div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                            
                            {selectedChat.top_recommendations && selectedChat.top_recommendations.length >= 2 && selectedChat.top_recommendations[0] && selectedChat.top_recommendations[1] && (
                          <div style={{ padding: '16px', marginTop: '4px', background: 'rgba(0,187,119,0.06)', border: '1px solid rgba(0,187,119,0.2)', borderRadius: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                            <div style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>📐 Pembuktian Matematis (Acceptable Advantage)</div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontFamily: "'Fira Code', 'Courier New', monospace", display: 'flex', flexDirection: 'column', gap: '6px' }}>
                              <div style={{ background: 'var(--bg-card)', padding: '6px 12px', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
                                {"Batas Mutlak DQ = 1 / (N - 1) = "} <strong style={{ color: 'var(--text-primary)' }}>{(1 / (selectedChat.cars_after_constraint - 1 || 1)).toFixed(4)}</strong>
                              </div>
                              <div style={{ background: 'var(--bg-card)', padding: '6px 12px', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
                                {"Delta Juara: Q(a_2) - Q(a_1) = "} <strong style={{ color: 'var(--text-primary)' }}>{((selectedChat.top_recommendations[1].VIKOR_Q || 0) - (selectedChat.top_recommendations[0].VIKOR_Q || 0)).toFixed(4)}</strong>
                              </div>
                            </div>

                            <div style={{ fontSize: '0.75rem', fontWeight: 800, marginTop: '4px', color: ((selectedChat.top_recommendations[1].VIKOR_Q || 0) - (selectedChat.top_recommendations[0].VIKOR_Q || 0)) >= (1 / (selectedChat.cars_after_constraint - 1 || 1)) ? '#00BB77' : '#F59E0B' }}>
                              {((selectedChat.top_recommendations[1].VIKOR_Q || 0) - (selectedChat.top_recommendations[0].VIKOR_Q || 0)) >= (1 / (selectedChat.cars_after_constraint - 1 || 1)) ? 'Status: Condition 1 Satisfied ✅ (Murni Terbaik)' : 'Status: Condition 1 Failed ⚠️ (Perlu Kompromi)'}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                        {/* TRACE TAB */}
                        {chatTab === 'trace' && (
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', animation: 'fadeIn 0.2s ease', background: '#0f172a', borderRadius: '12px', padding: '16px', border: '1px solid #1e293b' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#4ade80', marginBottom: '8px' }}>
                              <HiClipboardDocumentCheck size={18} />
                              <span style={{ fontSize: '0.8rem', fontWeight: 800, fontFamily: "'Fira Code', monospace" }}>SYSTEM_EXECUTION_TRACE_LOG</span>
                            </div>
                            
                            <div style={{ color: '#94a3b8', fontSize: '0.75rem', fontFamily: "'Fira Code', monospace", display: 'flex', flexDirection: 'column', gap: '8px', lineHeight: 1.5 }}>
                              <div><span style={{ color: '#4ade80' }}>$</span> SYSTEM_INIT: <span style={{ color: '#e2e8f0' }}>Receiving User Input...</span></div>
                              <div style={{ paddingLeft: '14px', color: '#38bdf8' }}>"{selectedChat.user_message}"</div>
                              
                              <div><span style={{ color: '#4ade80' }}>$</span> NLU_DIET: <span style={{ color: '#e2e8f0' }}>Extracting Intent & Preferences...</span></div>
                              <div style={{ paddingLeft: '14px', color: '#fcd34d' }}>Found Preferences: [{selectedChat.nlp_preferences?.join(', ') || 'Ø'}]</div>
                              <div style={{ paddingLeft: '14px', color: '#fcd34d' }}>Found Target Needs: [{selectedChat.nlp_needs?.join(', ') || 'Ø'}]</div>
                              
                              <div><span style={{ color: '#4ade80' }}>$</span> NLU_CRF: <span style={{ color: '#e2e8f0' }}>Extracting Named Entities...</span></div>
                              <div style={{ paddingLeft: '14px', color: '#fcd34d' }}>Found Constraints (X_Entities): [{selectedChat.nlp_entities?.join(', ') || 'Ø'}]</div>
                              
                              <div><span style={{ color: '#4ade80' }}>$</span> PIPELINE_HAC: <span style={{ color: '#e2e8f0' }}>Sub-space Clustering (Ward&apos;s Method)...</span></div>
                              <div style={{ paddingLeft: '14px', color: '#a78bfa' }}>Target Cluster Set: C_k = {selectedChat.cluster_name || 'C_Global (All)'}</div>
                              
                              <div><span style={{ color: '#4ade80' }}>$</span> PIPELINE_BOOL: <span style={{ color: '#e2e8f0' }}>Applying Ω Hard Constraints...</span></div>
                              <div style={{ paddingLeft: '14px', color: '#a78bfa' }}>Active Logic: {Object.entries(selectedChat.hard_filters_applied || {}).map(([k,v]) => `${k}=${v}`).join(' & ') || 'None'}</div>
                              <div style={{ paddingLeft: '14px', color: '#a78bfa' }}>Sub-space dimension reduction: N={selectedChat.cars_total} ➔ N&apos;={selectedChat.cars_after_constraint}</div>
                              
                              <div><span style={{ color: '#4ade80' }}>$</span> VIKOR_MCDM: <span style={{ color: '#e2e8f0' }}>Building Decision Matrix & Weights...</span></div>
                              <div style={{ paddingLeft: '14px', color: '#fb923c' }}>Weights V_w: {selectedChat.weight_dict_used ? Object.keys(selectedChat.weight_dict_used).length + " parameters applied" : "Uniform 1/n"}</div>
                              <div style={{ paddingLeft: '14px', color: '#fb923c' }}>Computing PIS (f*) and NIS (f-)... Done.</div>
                              <div style={{ paddingLeft: '14px', color: '#fb923c' }}>Calculating Utility S_j and Regret R_j... Done.</div>
                              <div style={{ paddingLeft: '14px', color: '#fb923c' }}>Calculating Q_j (v=0.5)... Done.</div>
                              <div style={{ paddingLeft: '14px', color: '#fb923c' }}>Verifying Condition 1 & 2 (Acceptable Advantage & Stability)... Done.</div>
                              
                              <div><span style={{ color: '#4ade80' }}>$</span> SYSTEM_RETURN: <span style={{ color: '#e2e8f0' }}>Sending JSON Response...</span></div>
                              <div style={{ paddingLeft: '14px', color: '#4ade80', fontWeight: 'bold' }}>Success! Top 1 ➔ {selectedChat.top_recommendations?.[0]?.BRAND} {selectedChat.top_recommendations?.[0]?.MODEL}</div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

            {/* LAYER 3: SYSTEM METRICS (SCIENCE DASHBOARD) */}
            {viewMode === 'system_metrics' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '28px', animation: 'fadeIn 0.2s ease' }}>
                <button onClick={() => setViewMode('history_list')} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', background: 'transparent', border: 'none', cursor: 'pointer', padding: '0', alignSelf: 'flex-start' }}>
                  <HiArrowLeft size={14} /> Kembali ke Riwayat
                </button>

                <SectionContainer title="🧠 1. NLU Research Dashboard (Baseline Results)" color="#EF4444" id="nlp-baseline">
                  <div style={{ marginBottom: '16px', textAlign: 'right' }}>
                    <Link 
                      href="/debug-nlu" 
                      style={{ 
                        display: 'inline-flex', alignItems: 'center', gap: '6px', 
                        fontSize: '0.75rem', fontWeight: 700, color: '#fff', 
                        background: '#00BB77', padding: '6px 14px', borderRadius: '8px',
                        boxShadow: '0 4px 12px rgba(0,187,119,0.2)'
                      }}
                    >
                      <HiBeaker size={14} /> Buka Dashboard NLU Full (Visual)
                    </Link>
                  </div>
                  <NLPBaselineSection data={nlpBaseline} isScientific={isScientific} />
                </SectionContainer>
                <SectionContainer title="🎯 2. NLP Strategic Decision Mapping" color="#4090F7" id="nlp-mapping">
                  <NLPMappingSection data={nlpMapping} />
                </SectionContainer>
                <SectionContainer title="🏆 3. VIKOR Sensitivity & MCDM Stability" color="#00BB77" id="vikor">
                  <VikorSection data={vikorSensitivity} />
                </SectionContainer>
                <SectionContainer title="📊 4. Hierarchical Clustering (HAC) Validation" color="#8B5CF6" id="clustering">
                  <ClusteringSection clusterData={clusterData} clusterDetail={clusterDetail} />
                </SectionContainer>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  </div>
)}
    </>
  );
}


/* ═══════════════════════════════════════════════════════════════ */
/*  REUSABLE UI COMPONENTS (SCIENTIFIC BLOCKS WITH MATH PROOFS)   */
/* ═══════════════════════════════════════════════════════════════ */

function MathBlock({ formula, desc }: { formula: string, desc?: string }) {
  return (
    <div style={{ padding: '12px 18px', background: '#0D1117', border: '1px solid #30363D', borderRadius: '8px', margin: '10px 0', fontFamily: "'Fira Code', 'Courier New', monospace" }}>
      <div style={{ color: '#58A6FF', fontSize: '0.95rem', fontWeight: 600, letterSpacing: '0.05em' }}>
        {formula}
      </div>
      {desc && <div style={{ color: '#8B949E', fontSize: '0.7rem', marginTop: '6px', fontStyle: 'italic' }}>{desc}</div>}
    </div>
  );
}

function SectionContainer({ title, color, children, id }: { title: string; color: string; children: React.ReactNode; id?: string }) {
  return (
    <div id={id} style={{ display: 'flex', flexDirection: 'column', gap: '20px', background: 'var(--bg-card)', padding: '28px', borderRadius: '16px', border: '1px solid var(--border-color)', boxShadow: '0 4px 16px rgba(0,0,0,0.02)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', borderBottom: `1.5px solid ${color}30`, paddingBottom: '16px' }}>
        <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-primary)', fontFamily: "'Space Grotesk', sans-serif" }}>
          {title}
        </h3>
      </div>
      <div>{children}</div>
    </div>
  );
}

function NLPBaselineSection({ data, isScientific }: { data: NLPBaselineData | null; isScientific: boolean }) {
  if (!data) return <EmptyState text="Gagal memuat data baseline NLP." />;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>

      {/* Math Proof */}
      <div style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 800, marginBottom: '4px', textTransform: 'uppercase' }}>Dasar Evaluasi NLP (DIETClassifier)</div>
        <MathBlock formula="F1 = 2 × (Precision × Recall) / (Precision + Recall)" desc="Harmonic mean dari ketepatan (Precision) dan sensitivitas (Recall) ekstraksi intent & entitas mesin." />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
        <BigMetric label="Akurasi Intent" value={`${(data.intent.accuracy * 100).toFixed(1)}%`} color="#4090F7" />
        <BigMetric label="Akurasi Entity" value={`${(data.entity.accuracy * 100).toFixed(1)}%`} color="#EF4444" />
        <BigMetric label="Macro F1 (NLU)" value={data.intent.macro_f1.toFixed(3)} color="#8B5CF6" />
        <BigMetric label="Entity Error" value={String(data.errors.entity_errors_count)} color="#F59E0B" />
      </div>

      <div>
        <div style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <HiClipboardDocumentCheck size={16} color="#4090F7" /> Laporan Per-Kelas Intent (F1-Score Breakdown)
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {Object.entries(data.intent.per_class).map(([name, m]) => (
            <div key={name} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ fontSize: '0.68rem', fontWeight: 800, minWidth: '100px', color: m.f1 < 0.6 ? '#EF4444' : 'var(--text-primary)' }}>{name}</div>
              <div style={{ flex: 1, height: '8px', background: 'var(--bg-secondary)', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${m.f1 * 100}%`, background: m.f1 > 0.8 ? '#00BB77' : m.f1 > 0.5 ? '#F59E0B' : '#EF4444', borderRadius: '4px' }} />
              </div>
              <div style={{ fontSize: '0.68rem', fontWeight: 800, minWidth: '40px', textAlign: 'right', color: m.f1 > 0.8 ? '#00BB77' : 'var(--text-muted)' }}>{(m.f1 * 100).toFixed(0)}%</div>
            </div>
          ))}
        </div>
      </div>

      {data.errors.high_confidence_errors.length > 0 && (
        <div style={{ padding: '16px', borderRadius: '12px', background: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.2)' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 800, color: '#F59E0B', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <HiMagnifyingGlassCircle size={18} /> Deteksi Overconfidence (False Positives)
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {data.errors.high_confidence_errors.slice(0, 3).map((err, i) => (
              <div key={i} style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', lineHeight: 1.5, background: 'var(--bg-card)', padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                🚨 "<em>{err.text}</em>" diprediksi <strong>{err.predicted}</strong> (conf: {err.confidence.toFixed(2)}) padahal seharusnya <strong>{err.true_intent}</strong>.
              </div>
            ))}
          </div>
        </div>
      )}

      {data.gaps.length > 0 && (
        <div style={{ marginTop: '10px' }}>
          <h4 style={{ margin: '0 0 10px', fontSize: '0.9rem', color: 'var(--text-primary)' }}>🔍 Identifikasi Gap Riset (Thesis Opportunity)</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {data.gaps.map((gap, i) => <GapCard key={i} gap={gap} isScientific={isScientific} />)}
          </div>
        </div>
      )}
    </div>
  );
}

function NLPMappingSection({ data }: { data: NLPMappingData | null }) {
  if (!data) return <EmptyState text="Gagal memuat akurasi Mapping NLP." />;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
        <BigMetric label="Mapping Accuracy" value={`${(data.overall_accuracy * 100).toFixed(1)}%`} color="#00BB77" />
        <BigMetric label="Preference Dict" value={String(data.mapping_tables.preference_index_count)} color="#8B5CF6" />
        <BigMetric label="Cluster Mapping" value={String(data.mapping_tables.preference_cluster_count)} color="#4090F7" />
      </div>
      <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', lineHeight: 1.6, textAlign: 'center' }}>
        Kalkulasi kecocokan konversi Semantic Lexicon (Natural Language Keywords) menjadi vektor fitur matematis mesin.
      </p>
    </div>
  );
}

function VikorSection({ data }: { data: VikorSensitivityData | null }) {
  if (!data) return <EmptyState text="Gagal memuat uji VIKOR Sensitivity." />;

  const scnA = data.scenarios['A_efficiency_heavy'];
  const scnB = data.scenarios['B_performance_heavy'];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>

      {/* Sensitivitas Konklusi */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', padding: '20px', borderRadius: '12px', background: data.is_sensitive ? 'rgba(0,187,119,0.08)' : 'rgba(239,68,68,0.08)', border: `1px solid ${data.is_sensitive ? 'rgba(0,187,119,0.25)' : 'rgba(239,68,68,0.25)'}` }}>
        <span style={{ fontSize: '2.5rem' }}>{data.is_sensitive ? '📈' : '⚠️'}</span>
        <div>
          <div style={{ fontWeight: 800, fontSize: '1rem', color: data.is_sensitive ? '#00BB77' : '#EF4444', marginBottom: '4px' }}>
            {data.is_sensitive ? 'Stabilitas MCDM: Sistem Terbukti Dinamis' : 'Stabilitas MCDM: Sistem Kaku'}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{data.sensitivity_proof}</div>
        </div>
      </div>

      {/* Math Proof */}
      <div style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-primary)', fontWeight: 800, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>📐 Pembuktian Matematis VIKOR</div>
        <MathBlock formula="S_j = Σ [ w_i × (f_i^* - f_{ij}) / (f_i^* - f_i^⁻) ]" desc="Perhitungan Utility Measure (Sj) murni berdasarkan bobot preferensi (w)." />
        <MathBlock formula="Q_j = v × (S_j - S^*) / (S^⁻ - S^*) + (1-v) × (R_j - R^*) / (R^⁻ - R^*)" desc="Perhitungan Nilai Kompromi (Qj). Nilai minimal = Ranking Terbaik." />
        <MathBlock formula="Q(a_2) - Q(a_1) ≥ 1 / (N - 1)" desc="Condition 1: Acceptable Advantage (Batas Keunggulan Tepat)." />
      </div>

      {/* Tabel Komparasi Aktual (Backend Data) */}
      {scnA && scnB && (
        <div style={{ border: '1px solid var(--border-color)', borderRadius: '12px', overflow: 'hidden' }}>
          <div style={{ background: 'var(--bg-secondary)', padding: '12px 16px', fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-primary)', borderBottom: '1px solid var(--border-color)' }}>
            Perbandingan Aktual Nilai Q (Skenario A vs B)
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1fr) minmax(0,1fr)' }}>

            {/* Skenario A */}
            <div style={{ padding: '16px', borderRight: '1px dashed var(--border-color)' }}>
              <div style={{ fontSize: '0.7rem', color: '#00BB77', fontWeight: 800, textTransform: 'uppercase', marginBottom: '12px' }}>Skenario A (Bobot Efisiensi Tinggi)</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {scnA.top_5.slice(0, 3).map(car => (
                  <div key={car.rank} style={{ background: 'var(--bg-card)', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <span style={{ fontSize: '0.65rem', padding: '2px 6px', background: '#00BB77', color: '#fff', borderRadius: '4px', fontWeight: 800, marginRight: '6px' }}>#{car.rank}</span>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-primary)' }}>{car.brand} {car.model}</span>
                    </div>
                    <div style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-primary)', fontFamily: "'Space Grotesk', sans-serif" }}>Q: {car.VIKOR_Q.toFixed(4)}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Skenario B */}
            <div style={{ padding: '16px' }}>
              <div style={{ fontSize: '0.7rem', color: '#EF4444', fontWeight: 800, textTransform: 'uppercase', marginBottom: '12px' }}>Skenario B (Bobot Performa Tinggi)</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {scnB.top_5.slice(0, 3).map(car => (
                  <div key={car.rank} style={{ background: 'var(--bg-card)', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <span style={{ fontSize: '0.65rem', padding: '2px 6px', background: '#EF4444', color: '#fff', borderRadius: '4px', fontWeight: 800, marginRight: '6px' }}>#{car.rank}</span>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-primary)' }}>{car.brand} {car.model}</span>
                    </div>
                    <div style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-primary)', fontFamily: "'Space Grotesk', sans-serif" }}>Q: {car.VIKOR_Q.toFixed(4)}</div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>
      )}
    </div>
  );
}

function ClusteringSection({ clusterData, clusterDetail }: { clusterData: ClusterEval | null; clusterDetail: ClusterDetailData | null }) {
  if (!clusterData || !clusterDetail) return <EmptyState text="Gagal memuat evaluasi Clustering." />;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>

      {/* Math Proof */}
      <div style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-primary)', fontWeight: 800, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>📐 Evaluasi Matematis HAC (Agglomerative)</div>
        <MathBlock formula="s(i) = [b(i) - a(i)] / max[a(i), b(i)]" desc="Silhouette Measurement: Kalkulasi kohesi intenal a(i) vs separasi antar-cluster b(i)." />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
        <BigMetric label="Silhouette" value={clusterDetail.stability.current_silhouette.toFixed(3)} color="#8B5CF6" />
        <BigMetric label="Cluster (K)" value={String(clusterData.n_clusters)} color="#00BB77" />
        <BigMetric label="Features" value={String(clusterData.features_used.length)} color="#4090F7" />
        <BigMetric label="Stability" value={clusterDetail.stability.current_silhouette > 0.4 ? 'Stable' : 'Weak'} color="#EF4444" />
      </div>

      {/* Stability Sequence K=3..7 */}
      <div style={{ border: '1px solid var(--border-color)', borderRadius: '12px', overflow: 'hidden' }}>
        <div style={{ background: 'var(--bg-secondary)', padding: '12px 16px', fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-primary)', borderBottom: '1px solid var(--border-color)' }}>
          Kalkulasi Kepadatan (Silhoutte ∀ K ∈ {"{3..7}"})
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0' }}>
          {clusterDetail.stability.silhouette_per_k.map(s => (
            <div key={s.k} style={{ flex: '1 1 auto', padding: '12px', textAlign: 'center', borderRight: '1px dashed var(--border-color)', background: s.k === clusterDetail.stability.best_k.k ? 'rgba(139,92,246,0.1)' : 'transparent' }}>
              <div style={{ fontSize: '0.65rem', color: s.k === clusterDetail.stability.best_k.k ? '#8B5CF6' : 'var(--text-muted)', fontWeight: 800, marginBottom: '4px' }}>{s.k === clusterDetail.stability.best_k.k && '⭐'} K={s.k}</div>
              <div style={{ fontSize: '0.9rem', fontWeight: 800, color: s.k === clusterDetail.stability.best_k.k ? '#8B5CF6' : 'var(--text-primary)', fontFamily: "'Space Grotesk', sans-serif" }}>{s.silhouette?.toFixed(4) || 'N/A'}</div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <div style={{ fontSize: '0.72rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '4px' }}>📌 Validasi Fitur Semantic Grup:</div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
          {clusterData.features_used.map(f => (
            <span key={f} style={{ fontSize: '0.65rem', padding: '4px 10px', background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '6px', color: 'var(--text-secondary)' }}>{f}</span>
          ))}
        </div>
      </div>
    </div>
  );
}

function EmptyState({ text }: { text: string }) {
  return (
    <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)', background: 'var(--bg-card)', borderRadius: '12px', border: '1px dashed var(--border-color)' }}>
      <div style={{ fontSize: '1.5rem', marginBottom: '8px' }}>⚠️</div>
      <div style={{ fontSize: '0.8rem' }}>{text}</div>
    </div>
  );
}

function BigMetric({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div style={{ padding: '16px 10px', borderRadius: '12px', background: `${color}0A`, border: `1px solid ${color}20`, textAlign: 'center' }}>
      <div style={{ fontSize: '1.4rem', fontWeight: 800, color, fontFamily: "'Space Grotesk', sans-serif" }}>{value}</div>
      <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em', marginTop: '6px' }}>{label}</div>
    </div>
  );
}

function GapCard({ gap, isScientific }: { gap: NLPGap; isScientific: boolean }) {
  const isCritical = gap.severity === 'critical';
  const accentColor = isCritical ? '#EF4444' : '#F59E0B';
  return (
    <div style={{ padding: '14px', borderRadius: '10px', background: `${accentColor}06`, border: `1px solid ${accentColor}20` }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
        <span style={{ fontSize: '0.65rem', padding: '4px 8px', borderRadius: '4px', background: `${accentColor}1A`, color: accentColor, fontWeight: 800, textTransform: 'uppercase' }}>
          {isScientific ? (isCritical ? 'CRITICAL GAP' : 'WARNING') : 'Saran Perbaikan'}
        </span>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 800, fontSize: '0.85rem', color: 'var(--text-primary)', marginBottom: '4px' }}>[{gap.component}] {gap.issue}</div>
          <div style={{ fontSize: '0.75rem', padding: '8px 12px', borderRadius: '8px', background: 'var(--bg-secondary)', color: 'var(--text-secondary)', lineHeight: 1.5, border: '1px solid var(--border-color)' }}>
            <strong>💡 Research Item:</strong> {gap.research_opportunity}
          </div>
        </div>
      </div>
    </div>
  );
}