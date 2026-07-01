import React from 'react';

interface CardProps {
  title?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  noPadding?: boolean;
}

export const Card: React.FC<CardProps> = ({ title, children, className = '', noPadding = false }) => {
  return (
    <div className={`glass-card ${className}`}>
      {title && (
        <div style={{ padding: 'var(--space-md) var(--space-lg)', borderBottom: '1px solid var(--border-primary)' }}>
          <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600 }}>{title}</h3>
        </div>
      )}
      <div style={{ padding: noPadding ? 0 : 'var(--space-lg)' }}>
        {children}
      </div>
    </div>
  );
};
