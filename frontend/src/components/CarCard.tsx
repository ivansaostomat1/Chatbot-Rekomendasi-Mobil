'use client';

import { useState, useEffect } from 'react';
import { CarRecommendation, NLPMappingData, VikorSensitivityData, ClusterDetailData } from '@/types';
import styles from './CarCard.module.css';
import SpotlightCard from './SpotlightCard';
import { useScientificMode } from '@/lib/ScientificModeContext';

interface Props {
  car: CarRecommendation;
  rank: number;
  expanded?: boolean;
  onToggleExpand?: () => void;
}

const RANK_CONFIG = [
  {
    emoji: '🥇', label: '#1 Terbaik', shortLabel: 'WINNER',
    color: '#F5A623', bg: 'rgba(245,166,35,0.08)', border: 'rgba(245,166,35,0.5)',
    glow: '0 0 30px rgba(245,166,35,0.2), 0 8px 32px rgba(245,166,35,0.15)',
    accentGrad: 'linear-gradient(135deg, #F5A623, #FF9900)',
  },
  {
    emoji: '🥈', label: '#2 Runner-up', shortLabel: 'RUNNER UP',
    color: '#B0BAC6', bg: 'rgba(176,186,198,0.08)', border: 'rgba(176,186,198,0.45)',
    glow: '0 0 24px rgba(176,186,198,0.15), 0 6px 24px rgba(176,186,198,0.1)',
    accentGrad: 'linear-gradient(135deg, #B0BAC6, #848D96)',
  },
  {
    emoji: '🥉', label: '#3 Pilihan', shortLabel: 'PILIHAN',
    color: '#C98A60', bg: 'rgba(201,138,96,0.08)', border: 'rgba(201,138,96,0.45)',
    glow: '0 0 24px rgba(201,138,96,0.15), 0 6px 24px rgba(201,138,96,0.1)',
    accentGrad: 'linear-gradient(135deg, #C98A60, #A0643A)',
  },
  {
    emoji: '4️⃣', label: '#4', shortLabel: 'KANDIDAT',
    color: '#4090F7', bg: 'rgba(64,144,247,0.06)', border: 'rgba(64,144,247,0.35)',
    glow: '0 0 20px rgba(64,144,247,0.12), 0 4px 16px rgba(64,144,247,0.08)',
    accentGrad: 'linear-gradient(135deg, #4090F7, #1E6FD9)',
  },
  {
    emoji: '5️⃣', label: '#5', shortLabel: 'KANDIDAT',
    color: '#00A693', bg: 'rgba(0,166,147,0.06)', border: 'rgba(0,166,147,0.35)',
    glow: '0 0 20px rgba(0,166,147,0.12), 0 4px 16px rgba(0,166,147,0.08)',
    accentGrad: 'linear-gradient(135deg, #00BB77, #00A693)',
  },
];

const CLUSTER_COLORS: Record<string, { color: string; bg: string }> = {
  'City Car':    { color: '#00BB77', bg: 'rgba(0,187,119,0.10)' },
  'Family Car':  { color: '#00A693', bg: 'rgba(0,166,147,0.10)' },
  'Offroad':     { color: '#1E6FD9', bg: 'rgba(30,111,217,0.10)' },
  'Performance': { color: '#F59E0B', bg: 'rgba(245,158,11,0.10)' },
  'Luxury':      { color: '#8B5CF6', bg: 'rgba(139,92,246,0.10)' },
};

const CLUSTER_PROFILES: Record<string, string> = {
  'City Car':    'Efficiency + Price + Popularity',
  'Family Car':  'Space + Passenger Comfort + Safety',
  'Offroad':     'Off-road + Performance',
  'Performance': 'Performance + Fun to Drive',
  'Luxury':      'Luxury + Technology + Driver Comfort',
};

const INDEX_LABELS: Record<string, string> = {
  INDEX_POWER:               '⚡ Power',
  INDEX_HANDLING:            '🛞 Handling',
  INDEX_EFFICIENCY:          '⛽ Efficiency',
  INDEX_SAFETY:              '🛡 Safety',
  INDEX_DRIVER_COMFORT:      '🧑‍✈️ Driver Comfort',
  INDEX_PASSENGER_COMFORT:   '🛋 Passenger Comfort',
  INDEX_TECH:                '📡 Technology',
  INDEX_SPACE:               '📦 Space',
  INDEX_OFFROAD:             '🏔 Off-road',
  INDEX_LUXURY:              '💎 Luxury',
  INDEX_LIFECYCLE_SAFE:      '⏳ Lifecycle Safe',
  INDEX_BRAND_STRENGTH:      '📈 Brand Strength',
  INDEX_PRICE:               '💰 Value for Money',
};

const SCENARIO_LABELS: Record<string, { label: string; emoji: string; color: string }> = {
  'A_efficiency_heavy': { label: 'Efisiensi', emoji: '⛽', color: '#00BB77' },
  'B_performance_heavy': { label: 'Performa', emoji: '⚡', color: '#F59E0B' },
  'C_equal_weights': { label: 'Equal', emoji: '⚖️', color: '#4090F7' },
};

function formatPrice(price?: number): string {
  if (!price) return 'N/A';
  if (price >= 1_000_000_000) return `Rp ${(price / 1_000_000_000).toFixed(1)} M`;
  if (price >= 1_000_000)     return `Rp ${(price / 1_000_000).toFixed(0)} Juta`;
  return `Rp ${price.toLocaleString('id-ID')}`;
}

function getVikorQuality(score?: number): { label: string; color: string; pct: number } {
  if (score === undefined) return { label: '-', color: '#9BA3AF', pct: 0 };
  const pct = Math.round((1 - score) * 100);
  if (score <= 0.20) return { label: 'Optimal', color: '#00BB77', pct };
  if (score <= 0.45) return { label: 'Baik', color: '#00A693', pct };
  if (score <= 0.70) return { label: 'Cukup', color: '#F59E0B', pct };
  return { label: 'Rendah', color: '#EF4444', pct };
}

function IndexBar({ label, value }: { label: string; value?: number }) {
  if (value === undefined || value === null) return null;
  const pct = Math.min(100, Math.max(0, Math.round(value * 100)));
  const color = value >= 0.7 ? '#00BB77' : value >= 0.4 ? '#F59E0B' : '#EF4444';
  return (
    <div style={{ marginBottom: '7px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.71rem', marginBottom: '3px', color: 'var(--text-secondary)' }}>
        <span>{label}</span>
        <span style={{ fontWeight: 700, color }}>{value.toFixed(3)}</span>
      </div>
      <div style={{ height: '5px', borderRadius: '3px', background: 'var(--border-color)' }}>
        <div style={{ height: '100%', width: `${pct}%`, borderRadius: '3px', background: `linear-gradient(90deg, ${color}99, ${color})`, transition: 'width 0.6s ease' }} />
      </div>
    </div>
  );
}

/* ── Reusable sub-components for evaluation ── */

function EvalSection({ title, color, children }: { title: string; color: string; children: React.ReactNode }) {
  return (
    <div style={{ marginTop: '14px', padding: '12px', borderRadius: '10px', background: `${color}06`, border: `1px solid ${color}18` }}>
      <div style={{ fontSize: '0.7rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em', color, marginBottom: '8px' }}>
        {title}
      </div>
      {children}
    </div>
  );
}

function FormulaLine({ label, formula, desc }: { label: string; formula: string; desc: string }) {
  return (
    <div style={{ marginBottom: '8px', padding: '6px 10px', borderRadius: '6px', background: 'var(--bg-secondary)', fontSize: '0.7rem' }}>
      <strong style={{ color: 'var(--text-primary)' }}>{label}</strong>
      <code style={{ display: 'block', padding: '2px 0', color: '#00BB77', fontFamily: "'Space Mono', monospace", fontSize: '0.72rem' }}>{formula}</code>
      <span style={{ color: 'var(--text-muted)', fontSize: '0.65rem' }}>{desc}</span>
    </div>
  );
}

function SmallMetric({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div style={{ textAlign: 'center', padding: '8px', borderRadius: '8px', background: `${color}08`, border: `1px solid ${color}18` }}>
      <div style={{ fontSize: '1rem', fontWeight: 800, color, fontFamily: "'Space Grotesk', sans-serif" }}>{value}</div>
      <div style={{ fontSize: '0.58rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', marginTop: '2px' }}>{label}</div>
    </div>
  );
}

function Badge({ children }: { children: React.ReactNode }) {
  return (
    <span style={{ fontSize: '0.6rem', fontWeight: 700, padding: '1px 6px', borderRadius: '4px', background: 'rgba(64,144,247,0.1)', color: '#4090F7', border: '1px solid rgba(64,144,247,0.2)' }}>
      {children}
    </span>
  );
}

function SpecItem({ icon, label, value, fullWidth }: { icon: string; label: string; value: string | number; fullWidth?: boolean }) {
  return (
    <div className={`${styles.specItem} ${fullWidth ? styles.specFullWidth : ''}`}>
      <span className={styles.specIcon}>{icon}</span>
      <div className={styles.specDetails}>
        <span className={styles.specLabel}>{label}</span>
        <span className={styles.specValue} title={String(value)}>{value}</span>
      </div>
    </div>
  );
}


function DetailBadge({ label, icon, type }: { label: string; icon: string; type: 'safety' | 'tech' | 'comfort' | 'accent' }) {
  const typeClass = {
    safety: styles.badgeSafety,
    tech: styles.badgeTech,
    comfort: styles.badgeComfort,
    accent: styles.badgeAccent
  }[type];

  return (
    <div className={`${styles.badge} ${typeClass}`}>
      <span>{icon}</span>
      <span>{label}</span>
    </div>
  );
}


export default function CarCard({ car, rank, expanded: propExpanded, onToggleExpand }: Props) {
  const { isScientific } = useScientificMode();
  const [localExpanded, setLocalExpanded] = useState(false);
  const expanded = propExpanded !== undefined ? propExpanded : localExpanded;
  const toggleExpanded = onToggleExpand || (() => setLocalExpanded(p => !p));
  
  const [evalTab, setEvalTab] = useState<'index' | 'nlp' | 'vikor' | 'cluster'>('index');

  // Evaluation data (fetched once when expanded)
  const [nlpData, setNlpData] = useState<NLPMappingData | null>(null);
  const [vikorData, setVikorData] = useState<VikorSensitivityData | null>(null);
  const [clusterData, setClusterData] = useState<ClusterDetailData | null>(null);
  const [evalLoaded, setEvalLoaded] = useState(false);

  const cfg  = RANK_CONFIG[Math.min(rank - 1, 4)];
  const vq   = getVikorQuality(car.VIKOR_Q);
  const clr  = car.CLUSTER_NAME ? (CLUSTER_COLORS[car.CLUSTER_NAME] ?? { color: '#00A693', bg: 'rgba(0,166,147,0.10)' }) : { color: '#00A693', bg: 'rgba(0,166,147,0.10)' };
  const isTop = rank === 1;

  // Compromise gap analysis
  const isCompromise = car.VIKOR_IS_COMPROMISE;
  const Q1 = car.VIKOR_Q1;
  const Q2 = car.VIKOR_Q2;
  const DQ = car.VIKOR_DQ;
  const advantageOk = Q1 != null && Q2 != null && DQ != null ? (Q2 - Q1) >= DQ : null;

  // Fetch evaluation data on first expand
  useEffect(() => {
    if (expanded && !evalLoaded) {
      setEvalLoaded(true);
      Promise.all([
        fetch('http://localhost:8000/evaluasi/nlp/mapping').then(r => r.ok ? r.json() : null),
        fetch('http://localhost:8000/evaluasi/vikor/sensitivity').then(r => r.ok ? r.json() : null),
        fetch('http://localhost:8000/evaluasi/clustering/detail').then(r => r.ok ? r.json() : null),
      ]).then(([nlp, vikor, cluster]) => {
        setNlpData(nlp);
        setVikorData(vikor);
        setClusterData(cluster);
      }).catch(err => console.error('Failed to fetch eval data:', err));
    }
  }, [expanded, evalLoaded]);

  return (
    <SpotlightCard
      className={`${styles.card} ${isTop ? styles.cardTop : ''}`}
      style={{ '--rank-color': cfg.color, '--rank-border': cfg.border } as React.CSSProperties}
      spotlightColor={`${cfg.color}15` as `rgba(${number}, ${number}, ${number}, ${number})`}
    >
      {/* Gradient top accent line */}
      <div className={styles.accentLine} style={{ background: cfg.accentGrad }} />

      {/* Ambient glow blob (top-only for rank 1) */}
      {isTop && (
        <div className={styles.glowBlob} style={{ background: `radial-gradient(ellipse at 50% 0%, ${cfg.color}22 0%, transparent 70%)` }} />
      )}

      <div className={styles.body}>
        {/* ── Header Row ── */}
        <div className={styles.headerRow}>
          <div className={styles.medallion} style={{ background: cfg.accentGrad, boxShadow: cfg.glow }}>
            <span className={styles.medallionEmoji}>{cfg.emoji}</span>
          </div>
          <div className={styles.carInfo}>
            <span className={styles.brandLabel}>{car.BRAND}</span>
            <span className={styles.modelName}>{car.MODEL}</span>
            <span className={styles.varianName}>{car.VARIAN}</span>
          </div>
          <div className={styles.rankChip} style={{ background: cfg.bg, borderColor: cfg.border, color: cfg.color }}>
            {cfg.shortLabel}
          </div>
        </div>

        {/* ── Price Banner ── */}
        <div className={styles.priceBanner} style={{ borderColor: `${cfg.color}25` }}>
          <div className={styles.priceInner}>
            <span className={styles.priceEyebrow}>Harga OTR</span>
            <span className={styles.priceAmount} style={{ color: cfg.color }}>{formatPrice(car.HARGAOTR)}</span>
          </div>
          {car.CLUSTER_NAME && (
            <span className={styles.clusterPill} style={{ background: clr.bg, color: clr.color, borderColor: `${clr.color}40` }}>
              {car.CLUSTER_NAME}
            </span>
          )}
        </div>

        {/* ── Specs Grid ── */}
        <div className={styles.specsGrid}>
          <SpecItem icon="🏷️" label="Tipe Bodi" value={car.BODY_TYPE ? car.BODY_TYPE.toUpperCase() : '-'} />
          <SpecItem icon="⚙️" label="Transmisi" value={car.TRANSMISSION || '-'} />
          <SpecItem icon="⛽" label="Bahan Bakar" value={car.FUEL ? car.FUEL.toUpperCase() : '-'} />
          <SpecItem icon="👥" label="Kapasitas" value={car.SEAT ? `${car.SEAT} Kursi` : '-'} />
          
          {/* Engine / Battery Row */}
          {car.CC ? (
            <SpecItem icon="🚀" label="Mesin" value={`${Math.round(car.CC)} cc${car.IS_TURBO ? ' Turbo' : ''}`} />
          ) : car.BATTERY ? (
            <SpecItem icon="🔋" label="Baterai" value={`${car.BATTERY} kWh`} />
          ) : (
            <SpecItem icon="⚙️" label="Penggerak" value={car.POWERTRAIN || '-'} />
          )}
          
          {/* Performance */}
          <SpecItem icon="🐎" label="Tenaga" value={car.HORSE_POWER ? `${Math.round(car.HORSE_POWER)} HP` : '-'} />
          
          {/* Dimensional & Clearance */}
          <SpecItem icon="🏔️" label="Ground Clearance" value={car.GROUND_CLEARANCE ? `${car.GROUND_CLEARANCE} mm` : '-'} />
          <SpecItem icon="📏" label="Dimensi (PxLxT)" value={car.LONG ? `${car.LONG} x ${car.WIDTH} x ${car.HEIGHT} mm` : '-'} fullWidth />
        </div>

        {/* ── Features Highlights (Brochure Style) ── */}
        <div className={styles.featureSection}>
          {/* Group 1: Keselamatan & ADAS */}
          <div className={styles.featureGroup}>
            <div className={styles.categoryLabel}>🛡️ Keselamatan & ADAS</div>
            <div className={styles.featureList}>
              {car.LEVEL_ADAS && car.LEVEL_ADAS !== "Dasar" && <DetailBadge label={`ADAS ${car.LEVEL_ADAS}`} icon="🤖" type="safety" />}
              {car.AIRBAGS && car.AIRBAGS > 0 && <DetailBadge label={`${car.AIRBAGS} Airbags`} icon="🎈" type="safety" />}
              {car.ABS === 1 && <DetailBadge label="ABS+EBD" icon="🛑" type="safety" />}
              {car.ESC === 1 && <DetailBadge label="Stability Control" icon="🛞" type="safety" />}
              {car.RCTA === 1 && <DetailBadge label="RCTA" icon="🚨" type="safety" />}
            </div>
          </div>

          {/* Group 2: Tech & Entertainment */}
          <div className={styles.featureGroup}>
            <div className={styles.categoryLabel}>📱 Teknologi & Hiburan</div>
            <div className={styles.featureList}>
              {car.APPLE_CARPLAY && car.APPLE_CARPLAY !== "Tidak Ada" && <DetailBadge label={`CarPlay ${car.APPLE_CARPLAY}`} icon="🍎" type="tech" />}
              {car.ANDROID_AUTO && car.ANDROID_AUTO !== "Tidak Ada" && <DetailBadge label={`Android Auto ${car.ANDROID_AUTO}`} icon="🤖" type="tech" />}
              {car.WIRELESS_CHARGER === "Ada" && <DetailBadge label="Wireless Charger" icon="⚡" type="tech" />}
              {car.CAMERA_360 === "Ada" && <DetailBadge label="Camera 360°" icon="🎥" type="tech" />}
              {car.HEAD_UP_DISPLAY === "Ada" && <DetailBadge label="HUD" icon="👓" type="tech" />}
            </div>
          </div>

          {/* Group 3: Kenyamanan & Interior */}
          <div className={styles.featureGroup}>
            <div className={styles.categoryLabel}>✨ Kenyamanan & Interior</div>
            <div className={styles.featureList}>
              {car.SUNROOF && car.SUNROOF !== "Tidak Ada" && <DetailBadge label={`Tipe Sunroof: ${car.SUNROOF}`} icon="☀️" type="comfort" />}
              {car.POWER_TAILGATE === "Ada" && <DetailBadge label="Bagasi: Power Tailgate" icon="🚪" type="comfort" />}
              {car.AUTO_HOLD === "Ada" && <DetailBadge label="Auto Hold" icon="🅿️" type="comfort" />}
              {car.LEATHER_SEAT && !["Fabric", "Kain (Fabric)", "Kain"].includes(car.LEATHER_SEAT) && (
                <DetailBadge label={`Jok ${car.LEATHER_SEAT}`} icon="🛋️" type="comfort" />
              )}
              {car.AMBIENT_LIGHT === "Ada" && <DetailBadge label="Ambient Light" icon="🌈" type="comfort" />}
            </div>
          </div>
        </div>

        {/* Cluster Semantic Profile (Scientific Only) */}
        {isScientific && car.CLUSTER_NAME && CLUSTER_PROFILES[car.CLUSTER_NAME] && (
          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', padding: '4px 0', fontStyle: 'italic', letterSpacing: '0.02em' }}>
            📎 Cluster = {CLUSTER_PROFILES[car.CLUSTER_NAME]}
          </div>
        )}

        {/* ── VIKOR Score ── */}
        {car.VIKOR_Q !== undefined && (
          <div className={styles.vikorSection}>
            {/* Simplified view for Awam mode */}
            {!isScientific ? (
              <>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)' }}>Kecocokan</span>
                  <span style={{ fontSize: '0.85rem', fontWeight: 800, color: vq.color }}>{vq.pct}% — {vq.label}</span>
                </div>
                <div className={styles.vikorTrack}>
                  <div
                    className={styles.vikorBar}
                    style={{ width: `${vq.pct}%`, background: `linear-gradient(90deg, ${cfg.color}bb, ${cfg.color})` }}
                  />
                </div>
              </>
            ) : (
              <>
                {/* Full scientific VIKOR display */}
                <div className={styles.vikorHeader}>
                  <span className={styles.vikorLabel}>VIKOR Score</span>
                  <span className={styles.vikorQuality} style={{ color: vq.color }}>{vq.label}</span>
                </div>

                <div className={styles.vikorTrack}>
                  <div
                    className={styles.vikorBar}
                    style={{ width: `${vq.pct}%`, background: `linear-gradient(90deg, ${cfg.color}bb, ${cfg.color})` }}
                  />
                </div>

                <div className={styles.vikorMeta}>
                  <span className={styles.vikorQ}>Q = {car.VIKOR_Q.toFixed(4)}</span>
                  <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                    {car.VIKOR_S !== undefined && `S = ${car.VIKOR_S.toFixed(3)}`}
                    {car.VIKOR_R !== undefined && `  R = ${car.VIKOR_R.toFixed(3)}`}
                  </span>
                  <span className={styles.vikorPct}>{vq.pct}% skor</span>
                </div>

                {/* Rank Gap (Compromise Analysis) */}
                {rank === 1 && Q1 != null && Q2 != null && DQ != null && (
                  <div style={{ marginTop: '8px', padding: '8px 10px', borderRadius: '8px', background: advantageOk ? 'rgba(0,187,119,0.07)' : 'rgba(245,158,11,0.07)', border: `1px solid ${advantageOk ? 'rgba(0,187,119,0.25)' : 'rgba(245,158,11,0.25)'}`, fontSize: '0.7rem' }}>
                    <div style={{ fontWeight: 700, marginBottom: '4px', color: advantageOk ? '#00BB77' : '#F59E0B' }}>
                      {advantageOk ? '✅ Kondisi Advantage Terpenuhi' : '⚠️ Multiple Compromise Solution'}
                    </div>
                    <div style={{ color: 'var(--text-muted)', lineHeight: 1.8 }}>
                      Q₁ = {Q1.toFixed(4)} &nbsp;|&nbsp; Q₂ = {Q2.toFixed(4)} &nbsp;|&nbsp; DQ = {DQ.toFixed(4)}<br/>
                      Q₂ − Q₁ = {(Q2 - Q1).toFixed(4)} {advantageOk ? '≥' : '<'} DQ
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* ── Status (Scientific Only) ── */}
        {isScientific && car.VIKOR_STATUS && (
          <div className={styles.statusRow} style={{ borderColor: `${cfg.color}20` }}>
            <span className={styles.statusDot} style={{ background: vq.color }} />
            <span className={styles.statusText}>{car.VIKOR_STATUS}</span>
          </div>
        )}

        {/* ══════════════════════════════════════════════════ */}
        {/* EXPAND: FULL BREAKDOWN + SCIENTIFIC EVALUATION     */}
        {/* (Scientific Mode Only)                             */}
        {/* ══════════════════════════════════════════════════ */}
        {isScientific && (
          <button
            onClick={toggleExpanded}
            style={{ width: '100%', background: 'none', border: 'none', cursor: 'pointer', padding: '6px 0 0', color: 'var(--text-muted)', fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.05em', display: 'flex', alignItems: 'center', gap: '5px', justifyContent: 'center', textTransform: 'uppercase' }}
          >
            {expanded ? '▲ Sembunyikan Evaluasi' : '▼ Lihat Breakdown & Evaluasi Debug'}
          </button>
        )}

        {expanded && (
          <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: `1px dashed var(--border-color)` }}>

            {/* Tab navigation */}
            <div style={{ display: 'flex', gap: '4px', marginBottom: '12px', flexWrap: 'wrap' }}>
              {([
                { key: 'index', label: '📊 INDEX' },
                { key: 'nlp', label: '🧠 NLP' },
                { key: 'vikor', label: '🏆 VIKOR' },
                { key: 'cluster', label: '📎 Cluster' },
              ] as { key: 'index' | 'nlp' | 'vikor' | 'cluster'; label: string }[]).map(tab => (
                <button
                  key={tab.key}
                  onClick={() => setEvalTab(tab.key)}
                  style={{
                    padding: '5px 12px', borderRadius: '6px', fontSize: '0.68rem', fontWeight: 700,
                    border: `1px solid ${evalTab === tab.key ? cfg.color + '50' : 'var(--border-color)'}`,
                    background: evalTab === tab.key ? cfg.color + '12' : 'var(--bg-secondary)',
                    color: evalTab === tab.key ? cfg.color : 'var(--text-muted)',
                    cursor: 'pointer', transition: 'all 0.2s',
                  }}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* ═══ TAB: INDEX BREAKDOWN ═══ */}
            {evalTab === 'index' && (
              <div>
                <div style={{ fontSize: '0.68rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: '10px' }}>
                  📊 Breakdown Kriteria Multi-Objektif
                </div>
                {Object.entries(INDEX_LABELS).map(([key, label]) => {
                  const val = car[key as keyof CarRecommendation] as number | undefined;
                  return <IndexBar key={key} label={label} value={val} />;
                })}
              </div>
            )}

            {/* ═══ TAB: NLP EVALUATION ═══ */}
            {evalTab === 'nlp' && (
              <div>
                {nlpData ? (
                  <>
                    {/* Pipeline */}
                    <EvalSection title="🔧 Pipeline NLP (Rasa DIETClassifier)" color="#4090F7">
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-secondary)', lineHeight: 1.8 }}>
                        <div style={{ marginBottom: '6px' }}>
                          <strong>Bahasa:</strong> {nlpData.pipeline_config.language} &nbsp;|&nbsp;
                          <strong>Pipeline:</strong> {nlpData.pipeline_config.pipeline.length} komponen
                        </div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '3px', marginBottom: '8px' }}>
                          {nlpData.pipeline_config.pipeline.map((p, i) => (
                            <span key={i} style={{ fontSize: '0.58rem', padding: '2px 6px', borderRadius: '4px', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
                              {p}
                            </span>
                          ))}
                        </div>
                        <div>
                          <strong>Entity Types:</strong>{' '}
                          {nlpData.pipeline_config.entity_types.map(e => <Badge key={e}>{e}</Badge>)}
                        </div>
                      </div>
                    </EvalSection>

                    {/* NLP Mapping Accuracy */}
                    <EvalSection title="🎯 NLP → Decision Mapping Accuracy" color="#00BB77">
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-secondary)' }}>
                        <FormulaLine
                          label="Mapping Accuracy"
                          formula="Accuracy = mapping_benar / total_test"
                          desc="Mengukur ketepatan pemetaan preferensi user ke INDEX dan Cluster yang benar."
                        />

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '6px', margin: '8px 0' }}>
                          <SmallMetric label="Overall Accuracy" value={`${(nlpData.overall_accuracy * 100).toFixed(1)}%`} color="#00BB77" />
                          <SmallMetric label="Benar / Total" value={`${nlpData.correct}/${nlpData.total}`} color="#4090F7" />
                          <SmallMetric label="Mapping Tables" value={`${nlpData.mapping_tables.preference_index_count + nlpData.mapping_tables.preference_cluster_count + nlpData.mapping_tables.need_cluster_count}`} color="#8B5CF6" />
                        </div>

                        {/* Per-type bars */}
                        <div style={{ marginTop: '8px' }}>
                          <strong>Per-Type:</strong>
                          {Object.entries(nlpData.per_type_accuracy).map(([type, stats]) => (
                            <div key={type} style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '5px' }}>
                              <span style={{ fontSize: '0.6rem', minWidth: '90px', color: 'var(--text-muted)' }}>{type.replace(/_/g, ' ')}</span>
                              <div style={{ flex: 1, height: '5px', borderRadius: '3px', background: 'var(--border-color)' }}>
                                <div style={{ height: '100%', width: `${stats.accuracy * 100}%`, borderRadius: '3px', background: stats.accuracy === 1 ? '#00BB77' : '#F59E0B', transition: 'width 0.6s' }} />
                              </div>
                              <span style={{ fontSize: '0.6rem', fontWeight: 700, color: stats.accuracy === 1 ? '#00BB77' : '#F59E0B', minWidth: '45px', textAlign: 'right' }}>
                                {(stats.accuracy * 100).toFixed(0)}%
                              </span>
                            </div>
                          ))}
                        </div>

                        {/* Test table */}
                        <div style={{ maxHeight: '180px', overflowY: 'auto', marginTop: '10px', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
                          <table style={{ width: '100%', fontSize: '0.62rem', borderCollapse: 'collapse' }}>
                            <thead>
                              <tr style={{ background: 'var(--bg-secondary)', position: 'sticky', top: 0 }}>
                                <th style={{ padding: '4px 6px', textAlign: 'left' }}>Input</th>
                                <th style={{ padding: '4px 6px', textAlign: 'left' }}>Expected</th>
                                <th style={{ padding: '4px 6px', textAlign: 'left' }}>Actual</th>
                                <th style={{ padding: '4px 6px', textAlign: 'center' }}>✓</th>
                              </tr>
                            </thead>
                            <tbody>
                              {nlpData.test_results.map((r, i) => (
                                <tr key={i} style={{ borderTop: '1px solid var(--border-color)', background: r.correct ? 'rgba(0,187,119,0.03)' : 'rgba(239,68,68,0.03)' }}>
                                  <td style={{ padding: '3px 6px', fontWeight: 600 }}>{r.input}</td>
                                  <td style={{ padding: '3px 6px' }}>{r.expected}</td>
                                  <td style={{ padding: '3px 6px', color: r.correct ? '#00BB77' : '#EF4444', fontWeight: 600 }}>{r.actual}</td>
                                  <td style={{ padding: '3px 6px', textAlign: 'center' }}>{r.correct ? '✅' : '❌'}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </EvalSection>
                  </>
                ) : (
                  <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-muted)', fontSize: '0.75rem' }}>Memuat data NLP evaluasi...</div>
                )}
              </div>
            )}

            {/* ═══ TAB: VIKOR EVALUATION ═══ */}
            {evalTab === 'vikor' && (
              <div>
                {/* Formulas */}
                <EvalSection title="📐 Formula VIKOR (Multi-Criteria Decision Making)" color="#00BB77">
                  <FormulaLine label="S (Group Utility)" formula="S = Σ (wⱼ × Dᵢⱼ)" desc="Total jarak tertimbang alternatif terhadap solusi ideal." />
                  <FormulaLine label="R (Individual Regret)" formula="R = max (wⱼ × Dᵢⱼ)" desc="Jarak maksimum (worst-case) satu alternatif." />
                  <FormulaLine label="Q (Compromise Index)" formula="Q = v(S−S*) / (S⁻−S*) + (1−v)(R−R*) / (R⁻−R*)" desc="Indeks kompromi akhir. v=0.5 (balanced). Semakin kecil Q → semakin baik." />
                  <FormulaLine label="DQ (Acceptable Advantage)" formula="DQ = 1 / (m − 1)" desc="Threshold jarak Q₁ dan Q₂ agar rank #1 sebagai pemenang mutlak." />
                </EvalSection>

                {/* Compromise status for this car */}
                <EvalSection title="🔍 Compromise Validation (Mobil Ini)" color="#F59E0B">
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-secondary)', lineHeight: 1.8 }}>
                    <div><strong>VIKOR Q =</strong> {car.VIKOR_Q?.toFixed(4) ?? '-'} &nbsp;|&nbsp; <strong>S =</strong> {car.VIKOR_S?.toFixed(3) ?? '-'} &nbsp;|&nbsp; <strong>R =</strong> {car.VIKOR_R?.toFixed(3) ?? '-'}</div>
                    <div><strong>Status:</strong> {car.VIKOR_STATUS || '-'}</div>
                    {Q1 != null && Q2 != null && DQ != null && (
                      <div style={{ marginTop: '4px', padding: '6px 8px', borderRadius: '6px', background: advantageOk ? 'rgba(0,187,119,0.07)' : 'rgba(245,158,11,0.07)', border: `1px solid ${advantageOk ? 'rgba(0,187,119,0.2)' : 'rgba(245,158,11,0.2)'}` }}>
                        Q₂ − Q₁ = {(Q2 - Q1).toFixed(4)} {advantageOk ? '≥' : '<'} DQ ({DQ.toFixed(4)}) → <strong style={{ color: advantageOk ? '#00BB77' : '#F59E0B' }}>{advantageOk ? 'Solusi Mutlak' : 'Solusi Kompromi'}</strong>
                      </div>
                    )}
                  </div>
                </EvalSection>

                {/* Sensitivity Analysis */}
                {vikorData ? (
                  <EvalSection title="🔬 Sensitivity Analysis (3 Skenario Bobot)" color="#8B5CF6">
                    <div style={{ fontSize: '0.68rem', color: 'var(--text-secondary)' }}>
                      <FormulaLine
                        label="Uji Sensitivitas"
                        formula="∂Q / ∂w < 0 → ranking berubah sesuai bobot preferensi"
                        desc="Jika ranking berubah saat bobot diubah, maka sistem terbukti sensitif terhadap preferensi user."
                      />

                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px' }}>
                        <strong>Hasil:</strong>
                        <span style={{
                          padding: '2px 8px', borderRadius: '12px', fontSize: '0.6rem', fontWeight: 800,
                          background: vikorData.is_sensitive ? 'rgba(0,187,119,0.12)' : 'rgba(239,68,68,0.12)',
                          color: vikorData.is_sensitive ? '#00BB77' : '#EF4444',
                          border: `1px solid ${vikorData.is_sensitive ? 'rgba(0,187,119,0.3)' : 'rgba(239,68,68,0.3)'}`,
                        }}>
                          {vikorData.is_sensitive ? '✅ SENSITIF' : '⚠️ TIDAK SENSITIF'}
                        </span>
                      </div>
                      <p style={{ fontSize: '0.62rem', color: 'var(--text-muted)', fontStyle: 'italic', marginBottom: '10px' }}>
                        {vikorData.sensitivity_proof}
                      </p>

                      {/* Scenario cards */}
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '6px' }}>
                        {Object.entries(vikorData.scenarios).map(([key, sc]) => {
                          const meta = SCENARIO_LABELS[key] || { label: key, emoji: '📊', color: '#888' };
                          return (
                            <div key={key} style={{ padding: '8px', borderRadius: '8px', background: `${meta.color}06`, border: `1px solid ${meta.color}15` }}>
                              <div style={{ fontWeight: 800, fontSize: '0.65rem', color: meta.color, marginBottom: '6px', textAlign: 'center' }}>
                                {meta.emoji} {meta.label}
                              </div>
                              {sc.top_5.slice(0, 3).map((c, i) => (
                                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '2px 0', fontSize: '0.58rem', borderTop: i > 0 ? '1px solid var(--border-color)' : 'none' }}>
                                  <span style={{ fontWeight: 600, maxWidth: '65px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{i+1}. {c.model}</span>
                                  <span style={{ fontWeight: 700, color: meta.color }}>{c.VIKOR_Q.toFixed(3)}</span>
                                </div>
                              ))}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </EvalSection>
                ) : (
                  <div style={{ textAlign: 'center', padding: '16px', color: 'var(--text-muted)', fontSize: '0.72rem' }}>Memuat data sensitivity...</div>
                )}
              </div>
            )}

            {/* ═══ TAB: CLUSTERING EVALUATION ═══ */}
            {evalTab === 'cluster' && (
              <div>
                {clusterData ? (
                  <>
                    {/* Silhouette Score */}
                    <EvalSection title="📊 Silhouette Score (Validitas Cluster)" color="#8B5CF6">
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-secondary)' }}>
                        <FormulaLine
                          label="Silhouette Coefficient"
                          formula="s(i) = (b(i) − a(i)) / max(a(i), b(i))"
                          desc="a(i) = jarak intra-cluster, b(i) = jarak inter-cluster terdekat. Skor [-1, 1]."
                        />

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', margin: '8px 0' }}>
                          <SmallMetric label="Silhouette Score" value={clusterData.stability.current_silhouette.toFixed(4)} color="#8B5CF6" />
                          <SmallMetric label="Interpretasi" value={clusterData.stability.current_silhouette > 0.5 ? '✅ Bagus' : clusterData.stability.current_silhouette > 0.2 ? '⚠️ Cukup' : '❌ Lemah'} color={clusterData.stability.current_silhouette > 0.5 ? '#00BB77' : '#F59E0B'} />
                        </div>

                        <div style={{ padding: '6px 8px', borderRadius: '6px', background: 'var(--bg-secondary)', fontSize: '0.62rem', color: 'var(--text-muted)', marginTop: '6px' }}>
                          {clusterData.stability.interpretation}
                        </div>
                      </div>
                    </EvalSection>

                    {/* Stability per k */}
                    <EvalSection title="🔬 Stabilitas Cluster (k = 3..7)" color="#4090F7">
                      <div style={{ display: 'flex', alignItems: 'flex-end', gap: '6px', height: '70px', fontSize: '0.6rem' }}>
                        {clusterData.stability.silhouette_per_k.map(item => {
                          const pct = item.silhouette != null ? Math.max(15, item.silhouette * 180) : 15;
                          const isCurrent = item.k === clusterData.stability.current_k;
                          return (
                            <div key={item.k} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '3px' }}>
                              <span style={{ fontSize: '0.55rem', fontWeight: 700, color: isCurrent ? '#8B5CF6' : 'var(--text-muted)' }}>
                                {item.silhouette?.toFixed(3) ?? '-'}
                              </span>
                              <div style={{
                                width: '100%', height: `${pct}%`, borderRadius: '3px',
                                background: isCurrent ? 'linear-gradient(180deg, #8B5CF6, #6D28D9)' : 'var(--border-color)',
                                border: isCurrent ? '1px solid #8B5CF6' : 'none',
                              }} />
                              <span style={{ fontSize: '0.55rem', fontWeight: isCurrent ? 800 : 500, color: isCurrent ? '#8B5CF6' : 'var(--text-muted)' }}>
                                k={item.k}
                              </span>
                            </div>
                          );
                        })}
                      </div>
                      <div style={{ fontSize: '0.58rem', color: 'var(--text-muted)', marginTop: '4px', textAlign: 'center' }}>
                        Best k = {clusterData.stability.best_k.k} (sil={clusterData.stability.best_k.silhouette.toFixed(4)}) | Digunakan: k = {clusterData.stability.current_k}
                      </div>
                    </EvalSection>

                    {/* Semantic Validation */}
                    <EvalSection title="🧬 Validasi Semantik (Cluster = Meaningful)" color="#00BB77">
                      <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)' }}>
                        <div style={{ marginBottom: '6px', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                          Setiap cluster menghasilkan profil fitur berbeda → semantic validity terbukti.
                        </div>
                        {Object.entries(clusterData.semantic_validation).map(([cname, profile]) => {
                          const cColor = {
                            'City Car': '#00BB77', 'Family Car': '#00A693',
                            'Offroad': '#1E6FD9', 'Performance': '#F59E0B',
                            'Luxury': '#8B5CF6',
                          }[cname] || '#00A693';
                          const isThis = car.CLUSTER_NAME === cname;
                          return (
                            <div key={cname} style={{
                              padding: '6px 8px', borderRadius: '6px', marginBottom: '5px',
                              background: isThis ? `${cColor}10` : 'var(--bg-secondary)',
                              border: `1px solid ${isThis ? cColor + '30' : 'var(--border-color)'}`,
                            }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ fontWeight: 800, color: cColor, fontSize: '0.65rem' }}>
                                  {isThis ? '→ ' : ''}{cname}
                                </span>
                                <span style={{ fontSize: '0.55rem', color: 'var(--text-muted)' }}>{profile.count} mobil</span>
                              </div>
                              <div style={{ fontSize: '0.58rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                                <strong style={{ color: 'var(--text-secondary)' }}>{profile.character_summary}</strong>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </EvalSection>

                    {/* Dendrogram Visualization */}
                    {clusterData.dendrogram_url && (
                      <EvalSection title="🌳 Hierarchical Dendrogram" color="#F59E0B">
                        <div style={{ display: 'flex', justifyContent: 'center', background: 'var(--bg-card)', padding: '10px', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
                          <img 
                            src={`http://localhost:8000${clusterData.dendrogram_url}`} 
                            alt="HAC Dendrogram" 
                            style={{ maxWidth: '100%', height: 'auto', borderRadius: '4px' }}
                          />
                        </div>
                        <div style={{ fontSize: '0.58rem', color: 'var(--text-muted)', marginTop: '6px', textAlign: 'center' }}>
                          Dendrogram dipotong (truncated) pada 30 node terakhir.
                        </div>
                      </EvalSection>
                    )}
                  </>
                ) : (
                  <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-muted)', fontSize: '0.75rem' }}>Memuat data clustering evaluasi...</div>
                )}
              </div>
            )}

          </div>
        )}
      </div>
    </SpotlightCard>
  );
}
