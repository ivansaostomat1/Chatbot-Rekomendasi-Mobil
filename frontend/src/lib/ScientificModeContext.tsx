'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface ScientificModeContextType {
  isScientific: boolean;
  toggleScientific: () => void;
}

const ScientificModeContext = createContext<ScientificModeContextType>({
  isScientific: false,
  toggleScientific: () => {},
});

export function ScientificModeProvider({ children }: { children: ReactNode }) {
  const [isScientific, setIsScientific] = useState(false);

  // Persist to localStorage
  useEffect(() => {
    const stored = localStorage.getItem('otobot_scientific_mode');
    if (stored === 'true') setIsScientific(true);
  }, []);

  const toggleScientific = () => {
    setIsScientific(prev => {
      const next = !prev;
      localStorage.setItem('otobot_scientific_mode', String(next));
      return next;
    });
  };

  return (
    <ScientificModeContext.Provider value={{ isScientific, toggleScientific }}>
      {children}
    </ScientificModeContext.Provider>
  );
}

export function useScientificMode() {
  return useContext(ScientificModeContext);
}
