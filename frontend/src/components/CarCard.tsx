'use client';

import { useState } from 'react';
import { CarRecommendation } from '@/types';
import styles from './CarCard.module.css';
import SpotlightCard from './SpotlightCard';

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
  const [localExpanded, setLocalExpanded] = useState(false);
  const expanded = propExpanded !== undefined ? propExpanded : localExpanded;
  const toggleExpanded = onToggleExpand || (() => setLocalExpanded(p => !p));
  
  const cfg  = RANK_CONFIG[Math.min(rank - 1, 4)];
  const vq   = getVikorQuality(car.VIKOR_Q);
  const clr  = car.CLUSTER_NAME ? (CLUSTER_COLORS[car.CLUSTER_NAME] ?? { color: '#00A693', bg: 'rgba(0,166,147,0.10)' }) : { color: '#00A693', bg: 'rgba(0,166,147,0.10)' };
  const isTop = rank === 1;

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
          {car.BATTERY && car.BATTERY > 0 ? (
            <SpecItem icon="🔋" label="Baterai" value={`${car.BATTERY} kWh`} />
          ) : (
            <SpecItem icon="🚀" label="Mesin" value={car.CC ? `${Math.round(car.CC)} cc${car.IS_TURBO ? ' Turbo' : ''}` : '-'} />
          )}
          
          <SpecItem icon="⚙️" label="Penggerak" value={car.DRIVE_SYS || '-'} />
          
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

        <div className={styles.vikorSection}>
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
        </div>

        {/* ══════════════════════════════════════════════════ */}
        {/* EXPAND: FULL BREAKDOWN + SCIENTIFIC EVALUATION     */}
        {/* (Scientific Mode Only)                             */}
        {/* ══════════════════════════════════════════════════ */}
        <button
          onClick={toggleExpanded}
          style={{ width: '100%', background: 'none', border: 'none', cursor: 'pointer', padding: '12px 0 0', color: cfg.color, fontSize: '0.72rem', fontWeight: 800, letterSpacing: '0.05em', display: 'flex', alignItems: 'center', gap: '5px', justifyContent: 'center', textTransform: 'uppercase' }}
        >
          {expanded ? '▲ Sembunyikan Rincian' : '▼ Lihat Skor Kriteria Lengkap'}
        </button>

        {expanded && (
          <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: `1px dashed var(--border-color)` }}>
            <div style={{ fontSize: '0.68rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: '12px' }}>
              📊 Analisis Kriteria Spesifik
            </div>
            {Object.entries(INDEX_LABELS).map(([key, label]) => {
              const val = car[key as keyof CarRecommendation] as number | undefined;
              return <IndexBar key={key} label={label} value={val} />;
            })}
          </div>
        )}
      </div>
    </SpotlightCard>
  );
}
