import React, { useEffect, useState } from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { useAuthStore } from '../stores/authStore';
import { portfolioApi } from '../api/portfolio';
import { TrendingUp, TrendingDown, DollarSign, Wallet, Activity } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { user } = useAuthStore();
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Mock data for initial UI dev
  useEffect(() => {
    // In a real app, we'd fetch this from portfolioApi
    setTimeout(() => {
      setSummary({
        totalValue: 105432.50,
        cashBalance: 45432.50,
        investedAmount: 60000.00,
        todayPnl: 1250.75,
        todayPnlPercent: 1.2,
        totalPnl: 5432.50,
        totalPnlPercent: 5.43,
      });
      setLoading(false);
    }, 500);
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

  const isProfit = summary?.totalPnl >= 0;
  const isTodayProfit = summary?.todayPnl >= 0;

  return (
    <div className="page-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
        <div>
          <h1 className="page-title" style={{ marginBottom: 'var(--space-xs)' }}>Dashboard</h1>
          <p className="text-secondary">Welcome back, {user?.username}. Here's your portfolio overview.</p>
        </div>
        <Badge variant={isProfit ? 'success' : 'danger'}>
          {isProfit ? '+' : ''}{summary?.totalPnlPercent.toFixed(2)}% All Time
        </Badge>
      </div>

      {/* ── Summary Cards ── */}
      <div className="grid-4" style={{ marginBottom: 'var(--space-xl)' }}>
        <Card className="animate-slide-up" style={{ animationDelay: '0ms' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <p className="text-secondary text-sm">Portfolio Value</p>
              <h2 style={{ fontSize: '1.8rem', marginTop: 'var(--space-xs)' }}>
                ${summary?.totalValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
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
                {isTodayProfit ? '+' : '-'}${Math.abs(summary?.todayPnl).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </h2>
              <p className="text-sm" style={{ color: isTodayProfit ? 'var(--accent-green)' : 'var(--accent-red)', marginTop: '4px' }}>
                {isTodayProfit ? <TrendingUp size={14} style={{display: 'inline', verticalAlign: 'text-bottom'}}/> : <TrendingDown size={14} style={{display: 'inline', verticalAlign: 'text-bottom'}}/>}
                {' '} {Math.abs(summary?.todayPnlPercent).toFixed(2)}%
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
                {isProfit ? '+' : '-'}${Math.abs(summary?.totalPnl).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
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
                ${summary?.cashBalance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
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
                <tr>
                  <td>
                    <div style={{ fontWeight: 600 }}>AAPL</div>
                    <div className="text-xs text-muted">Bought 10 shares</div>
                  </td>
                  <td className="text-right font-mono">
                    $150.25
                  </td>
                </tr>
                <tr>
                  <td>
                    <div style={{ fontWeight: 600 }}>TSLA</div>
                    <div className="text-xs text-muted">Sold 5 shares</div>
                  </td>
                  <td className="text-right font-mono text-green">
                    $245.10
                  </td>
                </tr>
                <tr>
                  <td>
                    <div style={{ fontWeight: 600 }}>MSFT</div>
                    <div className="text-xs text-muted">Bought 20 shares</div>
                  </td>
                  <td className="text-right font-mono">
                    $330.00
                  </td>
                </tr>
              </tbody>
            </table>
          </Card>
        </div>
      </div>
    </div>
  );
};
