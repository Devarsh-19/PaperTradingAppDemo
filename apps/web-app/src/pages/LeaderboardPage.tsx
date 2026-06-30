import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Award } from 'lucide-react';

export const LeaderboardPage: React.FC = () => {
  const [loading, setLoading] = useState(true);

  // Mock data
  const mockLeaderboard = [
    { rank: 1, username: 'WallStreetPro', return: 15.4, isMe: false },
    { rank: 2, username: 'DiamondHands', return: 12.1, isMe: false },
    { rank: 3, username: 'OptionsKing', return: 8.5, isMe: false },
    { rank: 4, username: 'Developer', return: 5.43, isMe: true }, // current user mock
    { rank: 5, username: 'BuyHighSellLow', return: -15.2, isMe: false },
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
          <h1 className="page-title" style={{ marginBottom: 'var(--space-xs)' }}>Leaderboard</h1>
          <p className="text-secondary">Global ranking by portfolio return.</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 16px', background: 'var(--accent-amber-dim)', borderRadius: 'var(--radius-full)', color: 'var(--accent-amber)', fontWeight: 600 }}>
          <Award size={20} /> Current Rank: #4
        </div>
      </div>

      <Card noPadding>
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ width: '80px', textAlign: 'center' }}>Rank</th>
              <th>Trader</th>
              <th className="text-right">Total Return</th>
            </tr>
          </thead>
          <tbody>
            {mockLeaderboard.map((user) => {
              const isProfit = user.return >= 0;
              return (
                <tr key={user.rank} style={user.isMe ? { background: 'var(--accent-blue-dim)' } : {}}>
                  <td style={{ textAlign: 'center', fontWeight: 700, fontSize: '1.2rem', color: user.rank <= 3 ? 'var(--accent-amber)' : 'var(--text-secondary)' }}>
                    #{user.rank}
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div style={{ width: 40, height: 40, borderRadius: '50%', background: 'var(--bg-tertiary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 600 }}>
                        {user.username.substring(0, 2).toUpperCase()}
                      </div>
                      <div style={{ fontWeight: user.isMe ? 700 : 500, color: user.isMe ? 'var(--accent-blue)' : 'var(--text-primary)' }}>
                        {user.username}
                        {user.isMe && <Badge className="ml-2" style={{ marginLeft: 8 }} variant="info">You</Badge>}
                      </div>
                    </div>
                  </td>
                  <td className="text-right">
                    <Badge variant={isProfit ? 'success' : 'danger'}>
                      {isProfit ? '+' : ''}{user.return.toFixed(2)}%
                    </Badge>
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
