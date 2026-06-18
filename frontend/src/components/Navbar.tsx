'use client';

import { useState, useEffect } from 'react';
import { useTheme } from 'next-themes';
import Link from 'next/link';
import { HiSun, HiMoon, HiArrowPath, HiTableCells } from 'react-icons/hi2';
import { RiRobot2Fill } from 'react-icons/ri';
import styles from './Navbar.module.css';

interface NavbarProps {
  onReset?: () => void;
}

export default function Navbar({ onReset }: NavbarProps) {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const toggleTheme = () => setTheme(theme === 'dark' ? 'light' : 'dark');

  return (
    <nav className={styles.navbar}>
      <div className={styles.inner}>
        {/* ── Left: Bot avatar + name ── */}
        <a href="/" className={styles.leftGroup}>
          <div className={styles.botAvatar}>
            <RiRobot2Fill size={16} />
          </div>
          <span className={styles.logoMain}>Otobot</span>
        </a>

        <div style={{ flex: 1 }} />

        {/* ── Right: Navigation + Reset + Theme toggle ── */}
        <div className={styles.actions}>
          <Link href="/spesifikasi" className={styles.actionBtn} title="Katalog Spesifikasi" aria-label="Katalog Spesifikasi">
            <HiTableCells size={17} />
          </Link>
          {onReset && (
            <button
              className={`${styles.actionBtn} ${styles.resetBtn}`}
              onClick={onReset}
              title="Reset Sesi"
              aria-label="Reset Sesi"
            >
              <HiArrowPath size={16} />
            </button>
          )}
          <button className={styles.actionBtn} onClick={toggleTheme} aria-label="Toggle theme">
            {mounted ? (theme === 'dark' ? <HiSun size={16} /> : <HiMoon size={16} />) : <span style={{ width: 16, height: 16 }} />}
          </button>
        </div>
      </div>
    </nav>
  );
}