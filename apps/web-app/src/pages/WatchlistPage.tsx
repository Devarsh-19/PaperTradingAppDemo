import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Activity, Trash2 } from 'lucide-react';

export const WatchlistPage: React.FC = () => {
  const [loading, setLoading] = useState(true);

  // Mock data
  const mockWatchlist = [
    { symbol: 'NVDA', name: 'NVIDIA Corp', price: 450.25, change: 12.50, changePct: 2.85 },
    { symbol: 'META', name: 'Meta Platforms', price: 315.40, change: -4.20, changePct: -1.31 },
    { symbol: 'AMZN', name: 'Amazon.com', price: 132.50, change: 1.10, changePct: 0.84 },
  ];

  useEffect(() => {
    setTimeout(() => setLoading(false), 300);
  }, []);

  if (loading) {
    return <div className="page-container"><div className="skeleton" style={{ height: '400px' }} /></div>;
  }

  return (
    <div className="page-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
        <div>
          <h1 className="page-title" style={{ marginBottom: 'var(--space-xs)' }}>Watchlist</h1>
          <p className="text-secondary">Keep an eye on potential opportunities.</p>
        </div>
      </div>

      <Card noPadding>
        <table className="data-table">
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Name</th>
              <th className="text-right">Price</th>
              <th className="text-right">Change</th>
              <th className="text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            {mockWatchlist.map((item) => {
              const isPositive = item.change >= 0;
              return (
                <tr key={item.symbol}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'var(--bg-tertiary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Activity size={16} className="text-blue" />
                      </div>
                      <div style={{ fontWeight: 600 }}>{item.symbol}</div>
                    </div>
                  </td>
                  <td className="text-secondary">{item.name}</td>
                  <td className="text-right font-mono font-medium">${item.price.toFixed(2)}</td>
                  <td className="text-right">
                    <Badge variant={isPositive ? 'success' : 'danger'}>
                      {isPositive ? '+' : ''}{item.changePct.toFixed(2)}%
                    </Badge>
                  </td>
                  <td className="text-right">
                    <button className="icon-btn text-muted" style={{ padding: 4 }}>
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </Card>
    </div>
  );
};
