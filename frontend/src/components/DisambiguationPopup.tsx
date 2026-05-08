import React from 'react';

interface CarMatch {
  brand: string;
  model: string;
  varian: string;
  varian_count?: number;
  harga?: number;
  harga_min?: number;
  harga_max?: number;
  body_type: string;
}

interface DisambiguationPopupProps {
  matches: CarMatch[];
  query: string;
  onSelect: (match: CarMatch) => void;
  onCancel?: () => void;
}

export default function DisambiguationPopup({ matches, query, onSelect, onCancel }: DisambiguationPopupProps) {
  return (
    <div style={{
      background: 'var(--bg-card)',
      borderRadius: '20px',
      width: '100%',
      maxWidth: '500px',
      display: 'flex',
      flexDirection: 'column',
      boxShadow: 'var(--shadow-xs)',
      border: '1px solid var(--border-color)',
      overflow: 'hidden',
      animation: 'fadeUp 0.3s ease',
      marginTop: '8px',
      marginLeft: '40px'
    }}>
      <div style={{
        padding: '14px 18px',
        borderBottom: '1px solid var(--border-color)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'var(--bg-secondary)'
      }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            Persempit Pencarian Anda
          </h3>
          <p style={{ margin: '4px 0 0', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
            Ditemukan {matches.length} model untuk "{query}". Pilih yang paling tepat:
          </p>
        </div>
      </div>
      
      <div style={{
        padding: '12px',
        maxHeight: '300px',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        scrollbarWidth: 'thin'
      }}>
        {matches.map((match, i) => (
          <button
            key={i}
            onClick={() => onSelect(match)}
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '12px 14px',
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-color)',
              borderRadius: '12px',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={e => {
              e.currentTarget.style.borderColor = 'var(--jade)';
              e.currentTarget.style.transform = 'translateX(4px)';
              e.currentTarget.style.background = 'rgba(0,187,119,0.05)';
            }}
            onMouseLeave={e => {
              e.currentTarget.style.borderColor = 'var(--border-color)';
              e.currentTarget.style.transform = 'none';
              e.currentTarget.style.background = 'var(--bg-secondary)';
            }}
          >
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                {match.brand} {match.model} {match.varian}
              </span>
              <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                {match.body_type} {match.varian_count ? `• ${match.varian_count} VARIAN` : ''}
              </span>
            </div>
            <div style={{ fontSize: '0.82rem', fontWeight: 800, color: 'var(--jade)', textAlign: 'right' }}>
              {match.harga_min && match.harga_max ? (
                match.harga_min === match.harga_max 
                  ? `Rp${(match.harga_min / 1000000).toLocaleString('id-ID')} Jt`
                  : `Rp${(match.harga_min / 1000000).toLocaleString('id-ID')} - ${(match.harga_max / 1000000).toLocaleString('id-ID')} Jt`
              ) : match.harga ? (
                `Rp${(match.harga / 1000000).toLocaleString('id-ID')} Jt`
              ) : ''}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
