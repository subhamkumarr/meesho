'use client';

import { cn } from '../lib/utils';
import { getLabelColor, getLabelText } from '../api';
import { Shield, Eye, Sparkles, AlertTriangle } from 'lucide-react';

interface ScoreBadgeProps {
  label: string;
  score: number;
  className?: string;
}

export function ScoreBadge({ label, score, className }: ScoreBadgeProps) {
  const displayText = getLabelText(label);
  
  const getBadgeStyles = (label: string) => {
    switch (label) {
      case 'authentic':
        return 'badge-success';
      case 'suspicious':
        return 'badge-warning';
      case 'synthetic':
        return 'badge-danger';
      default:
        return 'badge-neutral';
    }
  };

  const getBadgeIcon = (label: string) => {
    switch (label) {
      case 'authentic':
        return <Sparkles className="w-4 h-4" />;
      case 'suspicious':
        return <Eye className="w-4 h-4" />;
      case 'synthetic':
        return <Shield className="w-4 h-4" />;
      default:
        return <AlertTriangle className="w-4 h-4" />;
    }
  };
  
  return (
    <div className={cn('inline-flex items-center space-x-3', className)}>
      <div className={cn('badge flex items-center space-x-2', getBadgeStyles(label))}>
        {getBadgeIcon(label)}
        <span className="font-semibold">{displayText}</span>
      </div>
      <div className="text-lg font-bold text-neutral-900">
        {(score * 100).toFixed(1)}%
      </div>
    </div>
  );
}

interface ScoreBarProps {
  score: number;
  thresholds?: {
    auth: number;
    syn: number;
  };
  className?: string;
}

export function ScoreBar({ score, thresholds = { auth: 0.15, syn: 0.70 }, className }: ScoreBarProps) {
  const getFillVariant = () => {
    if (score < thresholds.auth) return 'score-bar__fill--auth';
    if (score < thresholds.syn) return 'score-bar__fill--mid';
    return 'score-bar__fill--syn';
  };

  return (
    <div className={cn('score-bar', className)}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#4b5563', marginBottom: '8px' }}>
        <span>Authentic</span>
        <span>Synthetic</span>
      </div>
      <div className="score-bar__track">
        <div className="score-bar__bg"></div>
        <div className="score-bar__marker" style={{ left: `${thresholds.auth * 100}%` }} />
        <div className="score-bar__marker" style={{ left: `${thresholds.syn * 100}%` }} />
        <div className={cn('score-bar__fill', getFillVariant())} style={{ width: `${score * 100}%` }} />
        <div className="score-bar__indicator" style={{ left: `${Math.max(0, Math.min(100, score * 100))}%` }} />
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#6b7280', marginTop: '8px' }}>
        <span>{(thresholds.auth * 100).toFixed(0)}% threshold</span>
        <span>{(thresholds.syn * 100).toFixed(0)}% threshold</span>
      </div>
    </div>
  );
}