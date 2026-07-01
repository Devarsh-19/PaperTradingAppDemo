import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { useAuthStore } from '../stores/authStore';
import { portfolioApi } from '../api/portfolio';
import { Position, PortfolioSummary } from '../types/api';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

export const PortfolioPage: React.FC = () => {
  const { user } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [positions, setPositions] = useState<Position[]>([]);
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [positionsData, summaryData] = await Promise.all([
          portfolioApi.getPositions(),
          portfolioApi.getSummary()
        ]);
        setPositions(positionsData);
        setSummary(summaryData);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load portfolio data');
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  const pieData = positions.map(p => ({
    name: p.symbol,
    value: p.total_value || (p.quantity * (p.current_price || p.average_price))
  }));
  if (summary) {
    pieData.push({ name: 'Cash', value: summary.cash_balance });
  }

  const COLORS = ['#2979ff', '#00e676', '#ff5252', '#ffab40', '#94a3b8'];

  if (loading) {
    return <div className="page-container"><div className="skeleton" style={{ height: '400px' }} /></div>;
  }

  if (error) {
    return <div className="page-container text-red">{error}</div>;
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
                {positions.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="text-center text-muted" style={{ padding: 'var(--space-lg)' }}>
                      No open positions
                    </td>
                  </tr>
                ) : (
                  positions.map((pos) => {
                    const totalValue = pos.total_value || (pos.quantity * (pos.current_price || pos.average_price));
                    const pnl = pos.unrealized_pnl || 0;
                    const pnlPct = pos.unrealized_pnl_percent || 0;
                    const isProfit = pnl >= 0;
                    
                    return (
                      <tr key={pos.symbol}>
                        <td>
                          <div style={{ fontWeight: 600 }}>{pos.symbol}</div>
                        </td>
                        <td className="text-right">{pos.quantity}</td>
                        <td className="text-right font-mono">${pos.average_price.toFixed(2)}</td>
                        <td className="text-right font-mono">${pos.current_price?.toFixed(2) || '---'}</td>
                        <td className="text-right font-mono">${totalValue.toFixed(2)}</td>
                        <td className={`text-right font-mono ${isProfit ? 'text-green' : 'text-red'}`}>
                          {isProfit ? '+' : '-'}${Math.abs(pnl).toFixed(2)} ({isProfit ? '+' : ''}{pnlPct.toFixed(2)}%)
                        </td>
                      </tr>
                    );
                  })
                )}
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
