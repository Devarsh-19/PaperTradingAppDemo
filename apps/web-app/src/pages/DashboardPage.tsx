import React, { useEffect, useState } from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { useAuthStore } from '../stores/authStore';
import { portfolioApi } from '../api/portfolio';
import { TrendingUp, TrendingDown, DollarSign, Wallet, Activity } from 'lucide-react';
import { PortfolioSummary, Trade } from '../types/api';

export const DashboardPage: React.FC = () => {
  const { user } = useAuthStore();
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [recentTrades, setRecentTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const summaryData = await portfolioApi.getSummary();
        setSummary(summaryData);
        
        const tradesData = await portfolioApi.getTrades(1, 5);
        setRecentTrades(tradesData.items || tradesData);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="page-container">
        <h1 className="page-title">Dashboard</h1>
        <div className="grid-4" style={{ marginBottom: 'var(--space-xl)' }}>
          {[1, 2, 3, 4].map(i => <div key={i} className="skeleton" style={{ height: 120 }}></div>)}
        </div>
      </div>
    );
  }

  if (error) {
    return <div className="page-container text-red">{error}</div>;
  }

  const isProfit = (summary?.total_pnl ?? 0) >= 0;
  const isTodayProfit = (summary?.today_pnl ?? 0) >= 0;

  return (
    <div className="page-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
        <div>
          <h1 className="page-title" style={{ marginBottom: 'var(--space-xs)' }}>Dashboard</h1>
          <p className="text-secondary">Welcome back, {user?.username}. Here's your portfolio overview.</p>
        </div>
          <Badge variant={isProfit ? 'success' : 'danger'}>
          {isProfit ? '+' : ''}{summary?.total_pnl_percent?.toFixed(2)}% All Time
        </Badge>
      </div>

      {/* ── Summary Cards ── */}
      <div className="grid-4" style={{ marginBottom: 'var(--space-xl)' }}>
        <Card className="animate-slide-up" style={{ animationDelay: '0ms' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <p className="text-secondary text-sm">Portfolio Value</p>
              <h2 style={{ fontSize: '1.8rem', marginTop: 'var(--space-xs)' }}>
                ${summary?.total_value?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </h2>
            </div>
            <div style={{ padding: '8px', background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)' }}>
              <DollarSign size={20} className="text-blue" />
            </div>
          </div>
        </Card>

        <Card className="animate-slide-up" style={{ animationDelay: '50ms' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <p className="text-secondary text-sm">Today's P&L</p>
              <h2 style={{ fontSize: '1.8rem', marginTop: 'var(--space-xs)', color: isTodayProfit ? 'var(--accent-green)' : 'var(--accent-red)' }}>
                {isTodayProfit ? '+' : '-'}${Math.abs(summary?.today_pnl || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </h2>
              <p className="text-sm" style={{ color: isTodayProfit ? 'var(--accent-green)' : 'var(--accent-red)', marginTop: '4px' }}>
                {isTodayProfit ? <TrendingUp size={14} style={{display: 'inline', verticalAlign: 'text-bottom'}}/> : <TrendingDown size={14} style={{display: 'inline', verticalAlign: 'text-bottom'}}/>}
                {' '} {Math.abs(summary?.today_pnl_percent || 0).toFixed(2)}%
              </p>
            </div>
            <div style={{ padding: '8px', background: isTodayProfit ? 'var(--accent-green-dim)' : 'var(--accent-red-dim)', borderRadius: 'var(--radius-md)' }}>
              <Activity size={20} className={isTodayProfit ? 'text-green' : 'text-red'} />
            </div>
          </div>
        </Card>

        <Card className="animate-slide-up" style={{ animationDelay: '100ms' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <p className="text-secondary text-sm">Total P&L</p>
              <h2 style={{ fontSize: '1.8rem', marginTop: 'var(--space-xs)', color: isProfit ? 'var(--accent-green)' : 'var(--accent-red)' }}>
                {isProfit ? '+' : '-'}${Math.abs(summary?.total_pnl || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </h2>
            </div>
            <div style={{ padding: '8px', background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)' }}>
              {isProfit ? <TrendingUp size={20} className="text-green" /> : <TrendingDown size={20} className="text-red" />}
            </div>
          </div>
        </Card>

        <Card className="animate-slide-up" style={{ animationDelay: '150ms' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <p className="text-secondary text-sm">Available Cash</p>
              <h2 style={{ fontSize: '1.8rem', marginTop: 'var(--space-xs)' }}>
                ${summary?.cash_balance?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </h2>
            </div>
            <div style={{ padding: '8px', background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)' }}>
              <Wallet size={20} className="text-blue" />
            </div>
          </div>
        </Card>
      </div>

      {/* ── Main Content Area ── */}
      <div className="grid-3">
        <div style={{ gridColumn: 'span 2' }}>
          <Card title="Equity Curve" className="animate-slide-up" style={{ animationDelay: '200ms', height: '400px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
              [Chart Component Placeholder]
            </div>
          </Card>
        </div>
        
        <div>
          <Card title="Recent Activity" className="animate-slide-up" noPadding style={{ animationDelay: '250ms', height: '400px' }}>
            <table className="data-table">
              <tbody>
                {recentTrades.length === 0 ? (
                  <tr>
                    <td colSpan={2} className="text-center text-muted" style={{ padding: 'var(--space-lg)' }}>
                      No recent activity
                    </td>
                  </tr>
                ) : (
                  recentTrades.map((trade) => (
                    <tr key={trade.id}>
                      <td>
                        <div style={{ fontWeight: 600 }}>{trade.symbol}</div>
                        <div className="text-xs text-muted">
                          {trade.side === 'BUY' ? 'Bought' : 'Sold'} {trade.quantity} shares
                        </div>
                      </td>
                      <td className={`text-right font-mono ${trade.side === 'BUY' ? 'text-red' : 'text-green'}`}>
                        {trade.side === 'BUY' ? '-' : '+'}${trade.total_value.toFixed(2)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </Card>
        </div>
      </div>
    </div>
  );
};
