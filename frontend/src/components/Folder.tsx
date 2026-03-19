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
  return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).padStart(6, '0').toUpperCase();
};

const Folder: React.FC<FolderProps> = ({ color = '#5227FF', size = 1, items = [], className = '', onClick }) => {
  const maxItems = 3;
  const papers = items.slice(0, maxItems);
  while (papers.length < maxItems) {
    papers.push(null);
  }

  const [open, setOpen] = useState(false);
  const [hovered, setHovered] = useState(false);
  const [paperOffsets, setPaperOffsets] = useState<{ x: number; y: number }[]>(
    Array.from({ length: maxItems }, () => ({ x: 0, y: 0 }))
  );

  const folderBackColor = darkenColor(color, 0.08);
  const paper1 = darkenColor('#ffffff', 0.1);
  const paper2 = darkenColor('#ffffff', 0.05);
  const paper3 = '#ffffff';

  const handleClick = () => {
    setOpen(prev => !prev);
    if (open) {
      setPaperOffsets(Array.from({ length: maxItems }, () => ({ x: 0, y: 0 })));
    }
    if (onClick) {
      onClick();
    }
  };

  const handlePaperMouseMove = (e: React.MouseEvent<HTMLDivElement, MouseEvent>, index: number) => {
    if (!open) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const offsetX = (e.clientX - centerX) * 0.15;
    const offsetY = (e.clientY - centerY) * 0.15;
    setPaperOffsets(prev => {
      const newOffsets = [...prev];
      newOffsets[index] = { x: offsetX, y: offsetY };
      return newOffsets;
    });
  };

  const handlePaperMouseLeave = (_e: React.MouseEvent<HTMLDivElement, MouseEvent>, index: number) => {
    setPaperOffsets(prev => {
      const newOffsets = [...prev];
      newOffsets[index] = { x: 0, y: 0 };
      return newOffsets;
    });
  };

  const getOpenTransform = (index: number) => {
    if (index === 0) return 'translate(-120%, -70%) rotate(-15deg)';
    if (index === 1) return 'translate(10%, -70%) rotate(15deg)';
    if (index === 2) return 'translate(-50%, -100%) rotate(5deg)';
    return '';
  };

  const getPaperSize = (index: number, isOpen: boolean) => {
    if (index === 0) return { width: '70%', height: '80%' };
    if (index === 1) return isOpen ? { width: '80%', height: '80%' } : { width: '80%', height: '70%' };
    if (index === 2) return isOpen ? { width: '90%', height: '80%' } : { width: '90%', height: '60%' };
    return { width: '70%', height: '70%' };
  };

  return (
    <div style={{ transform: `scale(${size})` }} className={className}>
      <div
        style={{
          position: 'relative',
          transition: 'all 200ms ease-in',
          cursor: 'pointer',
          transform: open ? 'translateY(-8px)' : hovered ? 'translateY(-8px)' : undefined,
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
            const paperSize = getPaperSize(i, open);
            const transformStyle = open
              ? `${getOpenTransform(i)} translate(${paperOffsets[i].x}px, ${paperOffsets[i].y}px)`
              : hovered
                ? 'translateX(-50%) translateY(0%)'
                : 'translateX(-50%) translateY(10%)';

            return (
              <div
                key={i}
                onMouseMove={e => handlePaperMouseMove(e, i)}
                onMouseLeave={e => handlePaperMouseLeave(e, i)}
                style={{
                  position: 'absolute',
                  zIndex: 20,
                  bottom: '10%',
                  left: '50%',
                  transition: 'all 300ms ease-in-out',
                  transform: transformStyle,
                  ...paperSize,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundColor: i === 0 ? paper1 : i === 1 ? paper2 : paper3,
                  borderRadius: '10px',
                  ...(open && hovered ? { scale: '1.1' } : {}),
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
              transform: open || hovered ? 'skew(15deg) scaleY(0.6)' : undefined,
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
              transform: open || hovered ? 'skew(-15deg) scaleY(0.6)' : undefined,
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default Folder;
