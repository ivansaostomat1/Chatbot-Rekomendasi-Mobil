import type { Metadata } from 'next';
import './globals.css';
import { Providers } from './providers';

export const metadata: Metadata = {
  title: 'CarRec AI – Sistem Rekomendasi Mobil Cerdas',
  description: 'Chatbot rekomendasi mobil berbasis VIKOR, Agglomerative Clustering, dan NLP (Rasa). Temukan mobil terbaik sesuai kebutuhan Anda.',
  keywords: ['rekomendasi mobil', 'chatbot', 'VIKOR', 'clustering', 'NLP'],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id" suppressHydrationWarning>
      <body>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
