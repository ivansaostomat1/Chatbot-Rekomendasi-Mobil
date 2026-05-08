'use client';

import { useState, useEffect } from 'react';
import { useTheme } from 'next-themes';
import { HiSun, HiMoon } from 'react-icons/hi2';
import styles from './Navbar.module.css';

export default function Navbar() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const toggleTheme = () => setTheme(theme === 'dark' ? 'light' : 'dark');

  return (
    <nav className={styles.navbar}>
      <div className={styles.inner}>
        <a href="/" className={styles.logo}>
          <div className={styles.logoWordmark}>
            <span className={styles.logoMain}>Otobot</span>
            <span className={styles.logoSub}>Otomotif Bot</span>
          </div>
        </a>
        <div style={{ flex: 1 }} />
        <div className={styles.actions}>
          <button className={styles.themeToggle} onClick={toggleTheme} aria-label="Toggle theme">
            {mounted ? (theme === 'dark' ? <HiSun size={17} /> : <HiMoon size={17} />) : <span style={{ width: 17, height: 17 }} />}
          </button>
        </div>
      </div>
    </nav>
  );
}