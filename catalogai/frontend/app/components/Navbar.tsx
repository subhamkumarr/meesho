'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Search, BarChart3, Settings, Sparkles } from 'lucide-react';

const navigation = [
  { name: 'Upload', href: '/', icon: Search, description: 'Analyze Images' },
  { name: 'Scans', href: '/scans', icon: BarChart3, description: 'View History' },
  { name: 'Admin', href: '/admin', icon: Settings, description: 'Settings' },
];

export function Navbar() {
  const pathname = usePathname();

  return (
    <nav 
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 999999,
        width: '100vw',
        height: '80px',
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(20px)',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.2)'
      }}
    >
      <div 
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 2rem',
          height: '100%',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          position: 'relative',
          zIndex: 999999
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <Link 
            href="/" 
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '12px', 
              textDecoration: 'none',
              transition: 'transform 0.3s ease'
            }}
          >
            <div style={{
              background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
              padding: '10px',
              borderRadius: '16px',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 15px rgba(59, 130, 246, 0.3)',
              width: '48px',
              height: '48px'
            }}>
              <Search style={{ width: '24px', height: '24px' }} />
            </div>
            <div>
              <div style={{
                fontSize: '20px',
                fontWeight: '800',
                background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                lineHeight: '1.2'
              }}>
                CatalogAI
              </div>
              <div style={{
                fontSize: '12px',
                color: '#6b7280',
                fontWeight: '500',
                lineHeight: '1'
              }}>
                Authenticity Detection
              </div>
            </div>
          </Link>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            
            return (
              <Link
                key={item.name}
                href={item.href}
                style={{
                  padding: '8px 16px',
                  borderRadius: '12px',
                  color: isActive ? '#3730a3' : '#6b7280',
                  fontWeight: '600',
                  textDecoration: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  background: isActive ? '#eef2ff' : 'rgba(255, 255, 255, 0.1)',
                  backdropFilter: 'blur(10px)',
                  border: `1px solid ${isActive ? '#c7d2fe' : 'rgba(255, 255, 255, 0.2)'}`,
                  fontSize: '14px',
                  transition: 'all 0.3s ease'
                }}
              >
                <Icon style={{ width: '16px', height: '16px' }} />
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                  <span style={{ fontSize: '14px', fontWeight: '500' }}>{item.name}</span>
                  <span style={{ fontSize: '12px', opacity: '0.75' }}>
                    {item.description}
                  </span>
                </div>
              </Link>
            );
          })}
        </div>

        <div style={{ display: 'flex', alignItems: 'center' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            background: 'rgba(255, 255, 255, 0.6)',
            backdropFilter: 'blur(10px)',
            borderRadius: '9999px',
            padding: '8px 16px',
            boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)',
            border: '1px solid rgba(255, 255, 255, 0.3)'
          }}>
            <div style={{
              width: '8px',
              height: '8px',
              background: '#10b981',
              borderRadius: '50%',
              animation: 'pulse 2s infinite'
            }}></div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Sparkles style={{ width: '12px', height: '12px', color: '#3b82f6' }} />
              <span style={{ fontSize: '12px', fontWeight: '600', color: '#1f2937' }}>
                AI-Powered
              </span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}