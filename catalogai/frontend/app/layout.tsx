import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './laptop-fixed.css';
import './navbar-fix.css';
import './emergency-navbar-fix.css';
import { Navbar } from './components/Navbar';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'CatalogAI - Authenticity Detection',
  description: 'AI-powered image authenticity detection for product catalogs',
};

export default function RootLayout({
  children,
}: {
  children: any;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen">
          <Navbar />
          <main 
            style={{
              paddingTop: '80px',
              position: 'relative',
              zIndex: 1
            }}
          >
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}