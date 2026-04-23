'use client';

import { useState, useEffect } from 'react';
import { getNLPBaselineEval, getNLPMappingEval } from '@/lib/api';
import { NLPBaselineData, NLPMappingData } from '@/types';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  HiChartBar, 
  HiCheckCircle, 
  HiXCircle, 
  HiExclamationTriangle,
  HiBeaker,
  HiArrowLeft,
  HiArrowPath,
  HiBolt,
  HiMagnifyingGlass
} from 'react-icons/hi2';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Cell
} from 'recharts';
import Link from 'next/link';
import styles from './page.module.css';

export default function DebugNLUPage() {
  const [baselineData, setBaselineData] = useState<NLPBaselineData | null>(null);
  const [mappingData, setMappingData] = useState<NLPMappingData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'intents' | 'entities' | 'errors' | 'mapping'>('overview');

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [baseline, mapping] = await Promise.all([
        getNLPBaselineEval(),
        getNLPMappingEval()
      ]);
      setBaselineData(baseline);
      setMappingData(mapping);
    } catch (err: any) {
      console.error("Error fetching NLU data:", err);
      setError("Gagal memuat data evaluasi. Pastikan backend berjalan dan hasil 'rasa test nlu' sudah ada.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className={styles.loading}>
        <motion.div 
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        >
          <HiArrowPath size={48} className={styles.spinIcon} />
        </motion.div>
        <p style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Menganalisis kualitas NLP...</p>
      </div>
    );
  }

  if (error || !baselineData) {
    return (
      <div className={styles.errorState}>
        <HiXCircle size={64} style={{ color: 'var(--danger)' }} />
        <h1 style={{ fontSize: '1.5rem', fontWeight: 800 }}>Error</h1>
        <p style={{ color: 'var(--text-muted)', maxWidth: '400px' }}>{error}</p>
        <button onClick={fetchData} className={styles.errorStateBtn}>
          <HiArrowPath size={20} /> Coba Lagi
        </button>
      </div>
    );
  }

  const intentChartData = Object.entries(baselineData.intent.per_class).map(([name, metrics]) => ({
    name,
    f1: metrics.f1 * 100,
    support: metrics.support
  })).sort((a, b) => b.f1 - a.f1);

  const entityChartData = Object.entries(baselineData.entity.per_class).map(([name, metrics]) => ({
    name,
    f1: metrics.f1 * 100,
    support: metrics.support
  })).sort((a, b) => b.f1 - a.f1);

  return (
    <div className={styles.container}>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <div className={styles.headerLeft}>
            <Link href="/" className={styles.backBtn}>
              <HiArrowLeft size={24} />
            </Link>
            <div>
              <h1 className={styles.headerTitle}>
                <HiBeaker style={{ color: 'var(--jade)' }} /> NLU Quality Dashboard
              </h1>
              <p className={styles.headerSubtitle}>Debug Mode • Bahasa Indonesia</p>
            </div>
          </div>
          <div className={styles.headerRight}>
            <div className={styles.statusBadge}>
              <div className={styles.statusDot} />
              Backend Connected
            </div>
            <button onClick={fetchData} className={styles.refreshBtn} title="Refresh Data">
              <HiArrowPath size={20} />
            </button>
          </div>
        </div>
      </header>

      <main className={styles.main}>
        {/* Navigation Tabs */}
        <div className={styles.tabs}>
          {[
            { id: 'overview', label: 'Ringkasan', icon: HiChartBar },
            { id: 'intents', label: 'Intent', icon: HiBolt },
            { id: 'entities', label: 'Entity', icon: HiMagnifyingGlass },
            { id: 'errors', label: 'Kesalahan', icon: HiExclamationTriangle },
            { id: 'mapping', label: 'Mapping', icon: HiCheckCircle },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`${styles.tab} ${activeTab === tab.id ? styles.tabActive : ''}`}
            >
              <tab.icon size={18} />
              {tab.label}
            </button>
          ))}
        </div>

        <AnimatePresence mode="wait">
          {activeTab === 'overview' && (
            <motion.div 
              key="overview"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}
            >
              {/* Score Cards */}
              <div className={styles.grid4}>
                <ScoreCard 
                  title="Intent Accuracy" 
                  value={`${(baselineData.intent.accuracy * 100).toFixed(1)}%`} 
                  subtitle="Ketepatan Klasifikasi"
                  color="var(--jade)"
                />
                <ScoreCard 
                  title="Intent F1-Score" 
                  value={`${(baselineData.intent.weighted_f1 * 100).toFixed(1)}%`} 
                  subtitle="Weighted Average"
                  color="var(--cobalt-light)"
                />
                <ScoreCard 
                  title="Entity Accuracy" 
                  value={`${(baselineData.entity.accuracy * 100).toFixed(1)}%`} 
                  subtitle="Ketepatan Ekstraksi"
                  color="var(--warning)"
                />
                <ScoreCard 
                  title="Mapping Accuracy" 
                  value={`${((mappingData?.overall_accuracy || 0) * 100).toFixed(1)}%`} 
                  subtitle="Logic Translation"
                  color="#8B5CF6"
                />
              </div>

              {/* Confusion Matrices */}
              <div className={styles.grid2}>
                <div className={styles.card}>
                  <h3 className={styles.cardTitle}>
                    <div style={{ width: '4px', height: '24px', background: 'var(--jade)', borderRadius: '4px' }} />
                    Intent Confusion Matrix
                  </h3>
                  <div className={styles.matrixImgWrapper}>
                    <img 
                      src="http://localhost:8000/rasa-results/intent_confusion_matrix.png" 
                      alt="Intent Confusion Matrix"
                      className={styles.matrixImg}
                    />
                  </div>
                </div>
                <div className={styles.card}>
                  <h3 className={styles.cardTitle}>
                    <div style={{ width: '4px', height: '24px', background: 'var(--warning)', borderRadius: '4px' }} />
                    Entity Confusion Matrix
                  </h3>
                  <div className={styles.matrixImgWrapper}>
                    <img 
                      src="http://localhost:8000/rasa-results/DIETClassifier_confusion_matrix.png" 
                      alt="Entity Confusion Matrix"
                      className={styles.matrixImg}
                    />
                  </div>
                </div>
              </div>

              {/* Gaps / Research Opportunities */}
              <div className={styles.card}>
                <h3 className={styles.cardTitle}>
                  <HiExclamationTriangle style={{ color: 'var(--warning)' }} /> Research Gaps & Issues
                </h3>
                <div className={styles.gapList}>
                  {baselineData.gaps.map((gap, i) => (
                    <div key={i} className={`${styles.gapItem} ${gap.severity === 'critical' ? styles.gapItemCritical : styles.gapItemWarning}`}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <span className={`${styles.gapBadge} ${gap.severity === 'critical' ? styles.gapBadgeCritical : styles.gapBadgeWarning}`}>
                          {gap.severity}
                        </span>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700 }}>{gap.component}</span>
                      </div>
                      <h4 style={{ fontWeight: 800, marginBottom: '4px', fontSize: '1rem', color: 'var(--text-primary)' }}>{gap.issue}</h4>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '12px' }}>{gap.detail}</p>
                      <div style={{ fontSize: '0.75rem', color: 'var(--jade-dark)', fontWeight: 700, padding: '8px', background: 'rgba(0,187,119,0.1)', borderRadius: '8px', border: '1px solid rgba(0,187,119,0.2)' }}>
                        💡 Research Opp: {gap.research_opportunity}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'intents' && (
            <motion.div 
              key="intents"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}
            >
              <div className={styles.card}>
                <h3 className={styles.cardTitle}>Intent Performance Breakdown</h3>
                <div className={styles.chartContainer}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={intentChartData} layout="vertical" margin={{ left: 40, right: 40 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" horizontal={false} />
                      <XAxis type="number" domain={[0, 100]} hide />
                      <YAxis 
                        dataKey="name" 
                        type="category" 
                        stroke="var(--text-muted)" 
                        fontSize={12} 
                        width={120}
                        axisLine={false}
                        tickLine={false}
                      />
                      <Tooltip 
                        contentStyle={{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '8px', color: 'var(--text-primary)' }}
                        itemStyle={{ color: 'var(--jade)' }}
                      />
                      <Bar dataKey="f1" radius={[0, 4, 4, 0]} barSize={24}>
                        {intentChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.f1 > 90 ? 'var(--jade)' : entry.f1 > 70 ? 'var(--cobalt-light)' : 'var(--danger)'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className={styles.tableWrapper}>
                <table className={styles.table}>
                  <thead>
                    <tr>
                      <th>Intent Name</th>
                      <th>Precision</th>
                      <th>Recall</th>
                      <th>F1-Score</th>
                      <th>Support</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(baselineData.intent.per_class).map(([name, metrics]) => (
                      <tr key={name}>
                        <td style={{ fontWeight: 800 }}>{name}</td>
                        <td style={{ fontFamily: 'monospace' }}>{(metrics.precision * 100).toFixed(1)}%</td>
                        <td style={{ fontFamily: 'monospace' }}>{(metrics.recall * 100).toFixed(1)}%</td>
                        <td>
                          <span className={`${styles.f1Badge} ${metrics.f1 > 0.9 ? styles.f1High : metrics.f1 > 0.7 ? styles.f1Mid : styles.f1Low}`}>
                            {(metrics.f1 * 100).toFixed(1)}%
                          </span>
                        </td>
                        <td style={{ color: 'var(--text-muted)', fontWeight: 600 }}>{metrics.support}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          )}

          {activeTab === 'entities' && (
            <motion.div 
              key="entities"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}
            >
              <div className={styles.card}>
                <h3 className={styles.cardTitle}>Entity Performance Breakdown</h3>
                <div className={styles.chartContainer}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={entityChartData} layout="vertical" margin={{ left: 40, right: 40 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" horizontal={false} />
                      <XAxis type="number" domain={[0, 100]} hide />
                      <YAxis 
                        dataKey="name" 
                        type="category" 
                        stroke="var(--text-muted)" 
                        fontSize={12} 
                        width={120}
                        axisLine={false}
                        tickLine={false}
                      />
                      <Tooltip 
                        contentStyle={{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '8px', color: 'var(--text-primary)' }}
                        itemStyle={{ color: 'var(--warning)' }}
                      />
                      <Bar dataKey="f1" radius={[0, 4, 4, 0]} barSize={24}>
                        {entityChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.f1 > 80 ? 'var(--warning)' : entry.f1 > 50 ? 'var(--cobalt-light)' : 'var(--danger)'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className={styles.tableWrapper}>
                <table className={styles.table}>
                  <thead>
                    <tr>
                      <th>Entity Name</th>
                      <th>Precision</th>
                      <th>Recall</th>
                      <th>F1-Score</th>
                      <th>Support</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(baselineData.entity.per_class).map(([name, metrics]) => (
                      <tr key={name}>
                        <td style={{ fontWeight: 800 }}>{name}</td>
                        <td style={{ fontFamily: 'monospace' }}>{(metrics.precision * 100).toFixed(1)}%</td>
                        <td style={{ fontFamily: 'monospace' }}>{(metrics.recall * 100).toFixed(1)}%</td>
                        <td>
                          <span className={`${styles.f1Badge} ${metrics.f1 > 0.8 ? styles.f1High : metrics.f1 > 0.5 ? styles.f1Mid : styles.f1Low}`}>
                            {(metrics.f1 * 100).toFixed(1)}%
                          </span>
                        </td>
                        <td style={{ color: 'var(--text-muted)', fontWeight: 600 }}>{metrics.support}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          )}

          {activeTab === 'errors' && (
            <motion.div 
              key="errors"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}
            >
              <div className={styles.grid2}>
                <div className={styles.card} style={{ background: 'rgba(239, 68, 68, 0.05)', borderColor: 'rgba(239, 68, 68, 0.2)' }}>
                  <div style={{ color: 'var(--danger)', fontSize: '2.5rem', fontWeight: 900, marginBottom: '8px' }}>{baselineData.errors.intent_errors.length}</div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Total Intent Errors</div>
                </div>
                <div className={styles.card} style={{ background: 'rgba(245, 158, 11, 0.05)', borderColor: 'rgba(245, 158, 11, 0.2)' }}>
                  <div style={{ color: 'var(--warning)', fontSize: '2.5rem', fontWeight: 900, marginBottom: '8px' }}>{baselineData.errors.entity_errors_count}</div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Total Entity Errors</div>
                </div>
              </div>

              <div className={styles.card} style={{ padding: 0, overflow: 'hidden' }}>
                <div style={{ padding: '24px', borderBottom: '1px solid var(--border-color)' }}>
                  <h3 className={styles.cardTitle} style={{ marginBottom: '8px' }}>Intent Misclassifications</h3>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Kalimat yang diprediksi salah oleh model.</p>
                </div>
                <div>
                  {baselineData.errors.intent_errors.map((err, i) => (
                    <div key={i} className={styles.errorItem}>
                      <p className={styles.errorText}>"{err.text}"</p>
                      <div className={styles.errorMeta}>
                        <div className={styles.errorBlock}>
                          <span className={styles.errorLabel}>True Intent</span>
                          <span className={styles.errorValueTrue}>{err.intent}</span>
                        </div>
                        <div className={styles.divider} />
                        <div className={styles.errorBlock}>
                          <span className={styles.errorLabel}>Predicted</span>
                          <span className={styles.errorValuePred}>{err.intent_prediction.name}</span>
                        </div>
                        <div style={{ marginLeft: 'auto', padding: '6px 12px', background: 'var(--bg-secondary)', borderRadius: '99px', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span style={{ fontSize: '0.65rem', fontWeight: 900, textTransform: 'uppercase', color: 'var(--text-muted)' }}>Confidence</span>
                          <span style={{ fontSize: '0.85rem', fontWeight: 800, color: err.intent_prediction.confidence > 0.8 ? 'var(--danger)' : 'var(--text-primary)', fontFamily: 'monospace' }}>
                            {(err.intent_prediction.confidence * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'mapping' && (
            <motion.div 
              key="mapping"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}
            >
              <div className={styles.grid3}>
                <MappingStatCard 
                  label="Preference → Index" 
                  value={mappingData?.mapping_tables.preference_index_count || 0} 
                  sub="Rules defined"
                  color="var(--jade)"
                />
                <MappingStatCard 
                  label="Preference → Cluster" 
                  value={mappingData?.mapping_tables.preference_cluster_count || 0} 
                  sub="Categorization rules"
                  color="var(--cobalt-light)"
                />
                <MappingStatCard 
                  label="Need → Cluster" 
                  value={mappingData?.mapping_tables.need_cluster_count || 0} 
                  sub="Utility-based rules"
                  color="#8B5CF6"
                />
              </div>

              <div className={styles.card} style={{ padding: 0, overflow: 'hidden' }}>
                <div style={{ padding: '24px', borderBottom: '1px solid var(--border-color)' }}>
                  <h3 className={styles.cardTitle} style={{ marginBottom: '8px' }}>Logic Mapping Validation</h3>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Memastikan kata kunci di-map ke kriteria VIKOR yang tepat.</p>
                </div>
                <div className={styles.tableWrapper} style={{ border: 'none', borderRadius: 0 }}>
                  <table className={styles.table}>
                    <thead>
                      <tr>
                        <th>Input Keyword</th>
                        <th>Map Type</th>
                        <th>Expected</th>
                        <th>Actual</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {mappingData?.test_results.map((res, i) => (
                        <tr key={i}>
                          <td style={{ fontWeight: 800 }}>"{res.input}"</td>
                          <td style={{ fontSize: '0.75rem', fontFamily: 'monospace', color: 'var(--text-muted)' }}>{res.type}</td>
                          <td style={{ color: 'var(--text-secondary)' }}>{res.expected}</td>
                          <td style={{ color: 'var(--text-primary)' }}>{res.actual}</td>
                          <td>
                            {res.correct ? (
                              <HiCheckCircle style={{ color: 'var(--success)' }} size={24} />
                            ) : (
                              <HiXCircle style={{ color: 'var(--danger)' }} size={24} />
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <footer className={styles.footer}>
        <div className={styles.footerContent}>
          <div className={styles.footerLeft}>
            <HiBeaker style={{ color: 'var(--jade)' }} size={32} />
            <div>
              <div style={{ fontWeight: 800, color: 'var(--text-primary)' }}>CarRec AI Debugger</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>© 2026 Advanced NLP Evaluation System</div>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '32px' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.65rem', fontWeight: 900, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '4px' }}>Architecture</div>
              <div style={{ fontSize: '0.85rem', fontWeight: 800, color: 'var(--text-primary)' }}>Rasa + DIET + VIKOR</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.65rem', fontWeight: 900, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '4px' }}>Epochs</div>
              <div style={{ fontSize: '0.85rem', fontWeight: 800, color: 'var(--text-primary)' }}>200</div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

function ScoreCard({ title, value, subtitle, color }: { title: string, value: string, subtitle: string, color: string }) {
  return (
    <div className={styles.scoreCard}>
      <div 
        style={{
          position: 'absolute', top: '-20px', right: '-20px', width: '120px', height: '120px',
          background: color, opacity: 0.1, filter: 'blur(30px)', borderRadius: '50%'
        }}
      />
      <div className={styles.scoreCardTitle}>{title}</div>
      <div className={styles.scoreCardValue} style={{ color }}>{value}</div>
      <div className={styles.scoreCardSubtitle}>{subtitle}</div>
    </div>
  );
}

function MappingStatCard({ label, value, sub, color }: { label: string, value: number, sub: string, color: string }) {
  return (
    <div className={styles.card}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div className={styles.mappingIcon} style={{ background: `${color}15` }}>
          <HiBolt style={{ color }} size={24} />
        </div>
        <span style={{ fontSize: '2rem', fontWeight: 900, color: 'var(--text-primary)' }}>{value}</span>
      </div>
      <div style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '4px' }}>{label}</div>
      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{sub}</div>
    </div>
  );
}
