'use client';

import { ThemeProvider } from 'next-themes';
import { ScientificModeProvider } from '@/lib/ScientificModeContext';
import { ReactNode } from 'react';

export function Providers({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider attribute="data-theme" defaultTheme="dark" enableSystem={false}>
      <ScientificModeProvider>
        {children}
      </ScientificModeProvider>
    </ThemeProvider>
  );
}
