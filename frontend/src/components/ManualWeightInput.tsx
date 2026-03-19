'use client';

import { useState } from 'react';
import styles from './ManualWeightInput.module.css';
import { HiCheck, HiAdjustmentsHorizontal } from 'react-icons/hi2';

interface ManualWeightInputProps {
  initialWeights: Record<string, number>;
  onSubmit: (weights: Record<string, number>) => void;
  disabled?: boolean;
}

const CRITERIA_MAP = [
  { key: 'INDEX_PERFORMANCE', label: 'Performa (Kencang)' },
  { key: 'INDEX_FUN_TO_DRIVE', label: 'Fun to Drive (Handling)' },
  { key: 'INDEX_EFFICIENCY', label: 'Efisiensi BBM (Irit)' },
  { key: 'INDEX_DRIVER_COMFORT', label: 'Kenyamanan Pengemudi' },
  { key: 'INDEX_PASSENGER_COMFORT', label: 'Kenyamanan Penumpang' },
  { key: 'INDEX_SAFETY', label: 'Keamanan (Safety)' },
  { key: 'INDEX_TECH', label: 'Teknologi & Fitur' },
  { key: 'INDEX_SPACE', label: 'Luas Kabin & Bagasi' },
  { key: 'INDEX_OFFROAD', label: 'Kemampuan Offroad' },
  { key: 'INDEX_LUXURY', label: 'Kemewahan (Luxury)' },
  { key: 'INDEX_POPULARITY', label: 'Popularitas Merek' },
  { key: 'INDEX_PRICE', label: 'Value for Money' }
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
    <div className={styles.container}>
      <div className={styles.header}>
        <HiAdjustmentsHorizontal size={18} />
        <span>Sesuaikan Bobot Preferensi</span>
      </div>
      <div className={styles.desc}>
        Atur bobot kriteria (0-10) untuk memprioritaskan rekomendasi berdasarkan apa yang paling penting bagi Anda.
      </div>
      
      <div className={styles.grid}>
        {CRITERIA_MAP.map(crit => (
          <div key={crit.key} className={styles.row}>
            <div className={styles.labelGroup}>
              <span className={styles.label}>{crit.label}</span>
              <span className={styles.value}>{weights[crit.key] || 0}</span>
            </div>
            <input 
              type="range"
              min="0"
              max="10"
              step="1"
              value={weights[crit.key] || 0}
              onChange={(e) => handleChange(crit.key, parseInt(e.target.value))}
              disabled={disabled}
              className={styles.slider}
            />
          </div>
        ))}
      </div>

      <button onClick={handleSubmit} disabled={disabled} className={styles.submitBtn}>
        <HiCheck size={16} /> Terapkan & Cari Rekomendasi
      </button>
    </div>
  );
}
