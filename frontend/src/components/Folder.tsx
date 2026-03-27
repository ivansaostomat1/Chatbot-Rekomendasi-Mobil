'use client';

import React, { useState } from 'react';

interface FolderProps {
  color?: string;
  size?: number;
  items?: React.ReactNode[];
  className?: string;
  onClick?: () => void;
}

const darkenColor = (hex: string, percent: number): string => {
  let color = hex.startsWith('#') ? hex.slice(1) : hex;
  if (color.length === 3) {
    color = color
      .split('')
      .map(c => c + c)
      .join('');
  }
  const num = parseInt(color, 16);
  let r = (num >> 16) & 0xff;
  let g = (num >> 8) & 0xff;
  let b = num & 0xff;
  r = Math.max(0, Math.min(255, Math.floor(r * (1 - percent))));
  g = Math.max(0, Math.min(255, Math.floor(g * (1 - percent))));
  b = Math.max(0, Math.min(255, Math.floor(b * (1 - percent))));
  return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase();
};

const Folder: React.FC<FolderProps> = ({ color = '#bd8100ff', size = 1, items = [], className = '', onClick }) => {
  const maxItems = 3;
  const papers = items.slice(0, maxItems);
  while (papers.length < maxItems) {
    papers.push(null);
  }

  const [hovered, setHovered] = useState(false);

  const folderBackColor = darkenColor(color, 0.08);
  const paper1 = darkenColor('#ffffff', 0.1);
  const paper2 = darkenColor('#ffffff', 0.05);
  const paper3 = '#ffffff';

  const handleClick = (e: React.MouseEvent) => {
    // Saat diklik, lepaskan status hover agar tampilannya kembali ke semula (state awal)
    setHovered(false);
    if (onClick) {
      onClick();
    }
  };

  const getPaperSize = (index: number, isHovered: boolean) => {
    if (index === 0) return { width: '70%', height: '80%' };
    if (index === 1) return isHovered ? { width: '80%', height: '80%' } : { width: '80%', height: '70%' };
    if (index === 2) return isHovered ? { width: '90%', height: '80%' } : { width: '90%', height: '60%' };
    return { width: '70%', height: '70%' };
  };

  return (
    <div style={{ transform: `scale(${size})` }} className={className}>
      <div
        style={{
          position: 'relative',
          transition: 'all 200ms ease-in',
          cursor: 'pointer',
          transform: hovered ? 'translateY(-8px)' : undefined,
        }}
        onClick={handleClick}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
      >
        <div
          style={{
            position: 'relative',
            width: '100px',
            height: '80px',
            borderRadius: '0 10px 10px 10px',
            backgroundColor: folderBackColor,
          }}
        >
          {/* Folder tab */}
          <span
            style={{
              position: 'absolute',
              zIndex: 0,
              bottom: '98%',
              left: 0,
              width: '30px',
              height: '10px',
              borderRadius: '5px 5px 0 0',
              backgroundColor: folderBackColor,
            }}
          />

          {/* Papers */}
          {papers.map((item, i) => {
            const paperSize = getPaperSize(i, hovered);

            return (
              <div
                key={i}
                style={{
                  position: 'absolute',
                  zIndex: 20,
                  bottom: '10%',
                  left: '50%',
                  transition: 'all 300ms ease-in-out',
                  transform: hovered ? 'translateX(-50%) translateY(0%)' : 'translateX(-50%) translateY(10%)',
                  ...paperSize,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundColor: i === 0 ? paper1 : i === 1 ? paper2 : paper3,
                  borderRadius: '10px',
                }}
              >
                {item}
              </div>
            );
          })}

          {/* Front folder flaps */}
          <div
            style={{
              position: 'absolute',
              zIndex: 30,
              width: '100%',
              height: '100%',
              transformOrigin: 'bottom',
              transition: 'all 300ms ease-in-out',
              backgroundColor: color,
              borderRadius: '5px 10px 10px 10px',
              transform: hovered ? 'skew(15deg) scaleY(0.6)' : undefined,
            }}
          />
          <div
            style={{
              position: 'absolute',
              zIndex: 30,
              width: '100%',
              height: '100%',
              transformOrigin: 'bottom',
              transition: 'all 300ms ease-in-out',
              backgroundColor: color,
              borderRadius: '5px 10px 10px 10px',
              transform: hovered ? 'skew(-15deg) scaleY(0.6)' : undefined,
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default Folder;
