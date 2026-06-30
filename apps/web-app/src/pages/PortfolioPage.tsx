import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { useAuthStore } from '../stores/authStore';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

export const PortfolioPage: React.FC = () => {
  const { user } = useAuthStore();
  const [loading, setLoading] = useState(true);

  // Mock data
  const mockPositions = [
    { symbol: 'AAPL', quantity: 50, avgPrice: 150.00, currentPrice: 171.50 },
    { symbol: 'MSFT', quantity: 20, avgPrice: 320.00, currentPrice: 335.20 },
    { symbol: 'TSLA', quantity: 15, avgPrice: 210.00, currentPrice: 245.10 },
    { symbol: 'GOOGL', quantity: 30, avgPrice: 130.00, currentPrice: 135.40 },
  ];

  const pieData = mockPositions.map(p => ({
    name: p.symbol,
    value: p.quantity * p.currentPrice
  }));
  pieData.push({ name: 'Cash', value: 45432.50 });

  const COLORS = ['#2979ff', '#00e676', '#ff5252', '#ffab40', '#94a3b8'];

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
          <h1 className="page-title" style={{ marginBottom: 'var(--space-xs)' }}>Portfolio</h1>
          <p className="text-secondary">Your current holdings and allocation.</p>
        </div>
      </div>

      <div className="grid-3" style={{ marginBottom: 'var(--space-xl)' }}>
        <div style={{ gridColumn: 'span 2' }}>
          <Card title="Positions" noPadding>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Asset</th>
                  <th className="text-right">Quantity</th>
                  <th className="text-right">Avg Price</th>
                  <th className="text-right">Current Price</th>
                  <th className="text-right">Total Value</th>
                  <th className="text-right">P&L</th>
                </tr>
              </thead>
              <tbody>
                {mockPositions.map((pos) => {
                  const totalValue = pos.quantity * pos.currentPrice;
                  const pnl = (pos.currentPrice - pos.avgPrice) * pos.quantity;
                  const pnlPct = ((pos.currentPrice - pos.avgPrice) / pos.avgPrice) * 100;
                  const isProfit = pnl >= 0;
                  
                  return (
                    <tr key={pos.symbol}>
                      <td>
                        <div style={{ fontWeight: 600 }}>{pos.symbol}</div>
                      </td>
                      <td className="text-right">{pos.quantity}</td>
                      <td className="text-right font-mono">${pos.avgPrice.toFixed(2)}</td>
                      <td className="text-right font-mono">${pos.currentPrice.toFixed(2)}</td>
                      <td className="text-right font-mono">${totalValue.toFixed(2)}</td>
                      <td className={`text-right font-mono ${isProfit ? 'text-green' : 'text-red'}`}>
                        {isProfit ? '+' : '-'}${Math.abs(pnl).toFixed(2)} ({isProfit ? '+' : ''}{pnlPct.toFixed(2)}%)
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </Card>
        </div>

        <div>
          <Card title="Allocation" style={{ height: '100%', minHeight: '350px' }}>
            <div style={{ height: '280px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    stroke="none"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value: number) => `$${value.toFixed(2)}`}
                    contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-primary)', color: 'var(--text-primary)' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', justifyContent: 'center' }}>
              {pieData.map((entry, index) => (
                <div key={entry.name} style={{ display: 'flex', alignItems: 'center', fontSize: '0.8rem' }}>
                  <div style={{ width: 10, height: 10, backgroundColor: COLORS[index % COLORS.length], borderRadius: '50%', marginRight: 4 }} />
                  {entry.name}
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
