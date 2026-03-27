'use client';

import React, { useEffect, useRef, useState } from 'react';
import { animate, motion, useMotionValue, useMotionValueEvent, useTransform } from 'framer-motion';

const MAX_OVERFLOW = 50;

interface ElasticSliderProps {
  defaultValue?: number;
  startingValue?: number;
  maxValue?: number;
  className?: string;
  isStepped?: boolean;
  stepSize?: number;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  onChange?: (val: number) => void;
  color?: string;
}

const ElasticSlider: React.FC<ElasticSliderProps> = ({
  defaultValue = 50,
  startingValue = 0,
  maxValue = 100,
  className = '',
  isStepped = false,
  stepSize = 1,
  leftIcon = <span style={{fontSize: '0.8rem', opacity: 0.5}}>-</span>,
  rightIcon = <span style={{fontSize: '0.8rem', opacity: 0.5}}>+</span>,
  onChange,
  color = '#4090F7'
}) => {
  return (
    <div 
      className={className}
      style={{
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '16px',
        width: '100%',
        minWidth: '100px'
      }}
    >
      <Slider
        defaultValue={defaultValue}
        startingValue={startingValue}
        maxValue={maxValue}
        isStepped={isStepped}
        stepSize={stepSize}
        leftIcon={leftIcon}
        rightIcon={rightIcon}
        onChange={onChange}
        color={color}
      />
    </div>
  );
};

interface SliderProps {
  defaultValue: number;
  startingValue: number;
  maxValue: number;
  isStepped: boolean;
  stepSize: number;
  leftIcon: React.ReactNode;
  rightIcon: React.ReactNode;
  onChange?: (val: number) => void;
  color: string;
}

const Slider: React.FC<SliderProps> = ({
  defaultValue,
  startingValue,
  maxValue,
  isStepped,
  stepSize,
  leftIcon,
  rightIcon,
  onChange,
  color
}) => {
  const [value, setValue] = useState<number>(defaultValue);
  const sliderRef = useRef<HTMLDivElement>(null);
  const [region, setRegion] = useState<'left' | 'middle' | 'right'>('middle');
  const clientX = useMotionValue(0);
  const overflow = useMotionValue(0);
  const scale = useMotionValue(1);

  // Use a local state for the tooltip so it doesn't continuously render while dragging but we need immediate visual feedback
  // Framer motion uses standard React state fine here for value.

  useEffect(() => {
    setValue(defaultValue);
  }, [defaultValue]);

  const handleChange = (newVal: number) => {
    setValue(newVal);
    if (onChange) onChange(newVal);
  };

  useMotionValueEvent(clientX, 'change', (latest: number) => {
    if (sliderRef.current) {
      const { left, right } = sliderRef.current.getBoundingClientRect();
      let newValue: number;
      if (latest < left) {
        setRegion('left');
        newValue = left - latest;
      } else if (latest > right) {
        setRegion('right');
        newValue = latest - right;
      } else {
        setRegion('middle');
        newValue = 0;
      }
      overflow.jump(decay(newValue, MAX_OVERFLOW));
    }
  });

  const handlePointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (e.buttons > 0 && sliderRef.current) {
      const { left, width } = sliderRef.current.getBoundingClientRect();
      let newValue = startingValue + ((e.clientX - left) / width) * (maxValue - startingValue);
      if (isStepped) {
        newValue = Math.round(newValue / stepSize) * stepSize;
      }
      newValue = Math.min(Math.max(newValue, startingValue), maxValue);
      
      if (newValue !== value) {
        handleChange(newValue);
      }
      clientX.jump(e.clientX);
    }
  };

  const handlePointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    handlePointerMove(e);
    e.currentTarget.setPointerCapture(e.pointerId);
  };

  const handlePointerUp = () => {
    animate(overflow, 0, { type: 'spring', bounce: 0.5 });
  };

  const getRangePercentage = (): number => {
    const totalRange = maxValue - startingValue;
    if (totalRange === 0) return 0;
    return ((value - startingValue) / totalRange) * 100;
  };

  return (
    <>
      <motion.div
        onHoverStart={() => animate(scale, 1.05)}
        onHoverEnd={() => animate(scale, 1)}
        onTouchStart={() => animate(scale, 1.05)}
        onTouchEnd={() => animate(scale, 1)}
        style={{
          scale,
          opacity: useTransform(scale, [1, 1.05], [0.8, 1]),
          display: 'flex',
          width: '100%',
          touchAction: 'none',
          userSelect: 'none',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '12px'
        }}
      >
        <motion.div
          animate={{
            scale: region === 'left' ? [1, 1.3, 1] : 1,
            transition: { duration: 0.25 }
          }}
          style={{
            x: useTransform(() => (region === 'left' ? -overflow.get() / scale.get() : 0))
          }}
        >
          {leftIcon}
        </motion.div>

        <div
          ref={sliderRef}
          onPointerMove={handlePointerMove}
          onPointerDown={handlePointerDown}
          onPointerUp={handlePointerUp}
          style={{
            position: 'relative',
            display: 'flex',
            width: '100%',
            maxWidth: '320px',
            flexGrow: 1,
            cursor: 'grab',
            touchAction: 'none',
            userSelect: 'none',
            alignItems: 'center',
            paddingTop: '16px',
            paddingBottom: '16px'
          }}
        >
          <motion.div
            style={{
              scaleX: useTransform(() => {
                if (sliderRef.current) {
                  const { width } = sliderRef.current.getBoundingClientRect();
                  return 1 + Math.abs(overflow.get()) / width;
                }
                return 1;
              }),
              scaleY: useTransform(useTransform(overflow, v => Math.abs(v)), [0, MAX_OVERFLOW], [1, 0.7]),
              transformOrigin: useTransform(() => {
                if (sliderRef.current) {
                  const { left, width } = sliderRef.current.getBoundingClientRect();
                  return clientX.get() < left + width / 2 ? 'right' : 'left';
                }
                return 'center';
              }),
              height: useTransform(scale, [1, 1.05], [6, 10]),
              display: 'flex',
              flexGrow: 1
            }}
          >
            <div style={{
              position: 'relative',
              height: '100%',
              flexGrow: 1,
              overflow: 'hidden',
              borderRadius: '9999px',
              backgroundColor: 'rgba(156, 163, 175, 0.15)',
            }}>
              <div style={{
                position: 'absolute',
                height: '100%',
                backgroundColor: color,
                borderRadius: '9999px',
                width: `${getRangePercentage()}%`,
                boxShadow: `0 0 12px ${color}80`
              }} />
            </div>
          </motion.div>
        </div>

        <motion.div
          animate={{
            scale: region === 'right' ? [1, 1.3, 1] : 1,
            transition: { duration: 0.25 }
          }}
          style={{
            x: useTransform(() => (region === 'right' ? overflow.get() / scale.get() : 0))
          }}
        >
          {rightIcon}
        </motion.div>
      </motion.div>

      {/* Value Tooltip */}
      <p style={{
        position: 'absolute',
        top: '6px',
        color: scale.get() > 1 ? color : 'var(--text-muted)',
        transform: 'translateY(-100%)',
        fontSize: '0.8rem',
        fontWeight: 800,
        letterSpacing: '0.025em',
        pointerEvents: 'none',
        transition: 'color 0.2s'
      }}>
        {Math.round(value)}
      </p>
    </>
  );
};

function decay(value: number, max: number): number {
  if (max === 0) {
    return 0;
  }
  const entry = value / max;
  const sigmoid = 2 * (1 / (1 + Math.exp(-entry)) - 0.5);
  return sigmoid * max;
}

export default ElasticSlider;
