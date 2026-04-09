'use client';

import { useState } from 'react';
import ElasticSlider from './ElasticSlider';
import BorderGlow from './BorderGlow';
import { HiCheck, HiAdjustmentsHorizontal } from 'react-icons/hi2';
import { motion } from 'framer-motion';

interface ManualWeightInputProps {
  initialWeights: Record<string, number>;
  onSubmit: (weights: Record<string, number>) => void;
  disabled?: boolean;
}

const CRITERIA_MAP = [
  { key: 'INDEX_POWER', label: 'Tenaga & Akselerasi', desc: 'Prioritas pada mobil yang kencang, responsif, dan kuat menanjak.', color: '#F59E0B', icon: '⚡' },
  { key: 'INDEX_HANDLING', label: 'Stabilitas & Kelincahan', desc: 'Fokus pada mobil yang stabil di tikungan dan minim limbung.', color: '#EF4444', icon: '🛞' },
  { key: 'INDEX_EFFICIENCY', label: 'Efisiensi BBM', desc: 'Memprioritaskan mobil dengan konsumsi bensin yang paling hemat.', color: '#10B981', icon: '⛽' },
  { key: 'INDEX_DRIVER_COMFORT', label: 'Kenyamanan Pengemudi', desc: 'Cari mobil dengan posisi duduk ergonomis dan fitur setir lengkap.', color: '#6366F1', icon: '🧑‍✈️' },
  { key: 'INDEX_PASSENGER_COMFORT', label: 'Kenyamanan Penumpang', desc: 'Prioritas kabin kedap, bantalan empuk, dan fitur pelengkap baris belakang.', color: '#8B5CF6', icon: '🛋' },
  { key: 'INDEX_SAFETY', label: 'Fitur Keamanan', desc: 'Mencari mobil dengan Advanced Driver Assistance (ADAS) & Airbag banyak.', color: '#00BB77', icon: '🛡' },
  { key: 'INDEX_TECH', label: 'Teknologi & Fitur Modern', desc: 'Mobil canggih dengan layar besar, kamera 360, & integrasi smartphone.', color: '#06B6D4', icon: '📡' },
  { key: 'INDEX_SPACE', label: 'Keluasan Kabin & Bagasi', desc: 'Memprioritaskan mobil yang lega untuk membawa banyak barang / keluarga.', color: '#3B82F6', icon: '📦' },
  { key: 'INDEX_OFFROAD', label: 'Keandalan Jalan Rusak', desc: 'Aman untuk jalur berlubang, banjir, atau jalanan rusak (Ground Clearance tinggi).', color: '#84CC16', icon: '🏔' },
  { key: 'INDEX_LUXURY', label: 'Kesan Mewah & Premium', desc: 'Mobil dengan interior kulit asli, sunroof, panoramic, atau kursi pijat.', color: '#D946EF', icon: '💎' },
  { key: 'INDEX_LIFECYCLE_SAFE', label: 'Model Aman (Anti-Discontinue)', desc: 'Menghindari mobil yang sudah stop produksi / penjualannya mati di akhir tahun.', color: '#F97316', icon: '⏳' },
  { key: 'INDEX_BRAND_STRENGTH', label: 'Reputasi & Jaringan Merek', desc: 'Pilih merek dengan populasi terbanyak, rasio depresiasi minim, & bengkel luas.', color: '#F43F5E', icon: '📈' },
  { key: 'INDEX_PRICE', label: 'Value for Money', desc: 'Mencari harga paling masuk akal (murah) dengan kualitas maksimal.', color: '#14B8A6', icon: '💰' }
];

export default function ManualWeightInput({ initialWeights, onSubmit, disabled = false }: ManualWeightInputProps) {
  const [weights, setWeights] = useState<Record<string, number>>(() => {
    const mapped: Record<string, number> = {};
    CRITERIA_MAP.forEach(c => {
      mapped[c.key] = initialWeights[c.key] || 0;
    });
    return mapped;
  });

  const handleChange = (key: string, value: number) => {
    if (disabled) return;
    setWeights(prev => ({ ...prev, [key]: value }));
  };

  const handleSubmit = () => {
    if (disabled) return;
    onSubmit(weights);
  };

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95, y: 10 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      style={{
        background: 'rgba(30, 41, 59, 0.4)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        border: '1px solid rgba(255, 255, 255, 0.05)',
        borderRadius: '24px',
        padding: '24px',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.15)',
        color: 'var(--text-primary)',
        width: '100%',
        margin: '16px auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '24px'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '16px' }}>
        <div style={{ padding: '10px', background: 'rgba(64,144,247,0.1)', borderRadius: '12px', color: '#4090F7' }}>
          <HiAdjustmentsHorizontal size={24} />
        </div>
        <div>
          <h3 style={{ margin: 0, fontSize: '1.05rem', fontWeight: 800, letterSpacing: '0.02em', color: 'var(--text-primary)' }}>Tuning Preferensi Mesin VIKOR</h3>
          <p style={{ margin: '4px 0 0', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Sesuaikan prioritas kriteria rekomendasi klaster Anda (0-10) dengan menggeser slider elastis di bawah ini.
          </p>
        </div>
      </div>
      
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
        gap: '20px'
      }}>
        {CRITERIA_MAP.map(crit => (
          <div key={crit.key} style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            borderRadius: '16px',
            padding: '16px',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
            boxShadow: '0 2px 10px rgba(0,0,0,0.02)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', paddingBottom: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                <span style={{ fontSize: '1.4rem', filter: `drop-shadow(0 2px 4px ${crit.color}40)`, marginTop: '2px' }}>{crit.icon}</span>
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-primary)' }}>{crit.label}</span>
                  <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '2px', lineHeight: 1.3 }}>{crit.desc}</span>
                </div>
              </div>
            </div>
            
            <div style={{ flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <ElasticSlider
                startingValue={0}
                defaultValue={weights[crit.key] || 0}
                maxValue={10}
                isStepped={true}
                stepSize={1}
                color={crit.color}
                onChange={(val) => handleChange(crit.key, val)}
                leftIcon={<span style={{fontSize:'0.75rem', fontWeight: 600, color: 'var(--text-muted)'}}>0</span>}
                rightIcon={<span style={{fontSize:'0.75rem', fontWeight: 600, color: 'var(--text-muted)'}}>10</span>}
              />
            </div>
          </div>
        ))}
      </div>

      <BorderGlow
        edgeSensitivity={10}
        glowColor="158 100% 37%" // Jade (#00BB77)
        backgroundColor="var(--bg-card)"
        borderRadius={16}
        glowRadius={40}
        glowIntensity={2}
        coneSpread={50}
        animated={disabled}
        colors={['#00BB77', '#00A693', '#1E6FD9']}
        style={{
           marginTop: '16px',
           width: '100%',
           maxWidth: '340px',
           alignSelf: 'center',
           opacity: disabled ? 0.6 : 1,
        }}
      >
        <motion.button 
          whileHover={{ scale: disabled ? 1 : 1.02 }}
          whileTap={{ scale: disabled ? 1 : 0.98 }}
          onClick={handleSubmit} 
          disabled={disabled} 
          style={{
             padding: '18px 24px',
             background: 'transparent',
             color: 'var(--text-primary)',
             border: 'none',
             fontWeight: 800,
             fontSize: '0.95rem',
             cursor: disabled ? 'not-allowed' : 'pointer',
             display: 'flex',
             alignItems: 'center',
             justifyContent: 'center',
             gap: '10px',
             width: '100%',
             height: '100%'
          }}
        >
          <HiCheck size={20} /> Terapkan & Cari Rekomendasi
        </motion.button>
      </BorderGlow>
    </motion.div>
  );
}
