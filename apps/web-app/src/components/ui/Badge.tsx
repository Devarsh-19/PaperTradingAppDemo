import React from 'react';

type BadgeVariant = 'success' | 'danger' | 'warning' | 'info' | 'default';

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'default', className = '' }) => {
  const getStyles = () => {
    switch (variant) {
      case 'success':
        return { background: 'var(--accent-green-dim)', color: 'var(--accent-green)' };
      case 'danger':
        return { background: 'var(--accent-red-dim)', color: 'var(--accent-red)' };
      case 'warning':
        return { background: 'var(--accent-amber-dim)', color: 'var(--accent-amber)' };
      case 'info':
        return { background: 'var(--accent-blue-dim)', color: 'var(--accent-blue)' };
      default:
        return { background: 'var(--bg-tertiary)', color: 'var(--text-secondary)' };
    }
  };

  return (
    <span 
      className={className}
      style={{
        ...getStyles(),
        padding: '2px 8px',
        borderRadius: 'var(--radius-sm)',
        fontSize: '0.75rem',
        fontWeight: 600,
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {children}
    </span>
  );
};
