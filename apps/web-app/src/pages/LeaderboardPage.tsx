import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Award } from 'lucide-react';
import { leaderboardApi } from '../api/leaderboard';
import { LeaderboardEntry } from '../types/api';
import { useAuthStore } from '../stores/authStore';

export const LeaderboardPage: React.FC = () => {
  const { user } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [myRank, setMyRank] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [topData, meData] = await Promise.all([
          leaderboardApi.getTop(100),
          leaderboardApi.getMe().catch(() => null)
        ]);
        
        setLeaderboard(topData.entries || topData);
        if (meData) {
          setMyRank(meData.rank);
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load leaderboard');
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

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
          <h1 className="page-title" style={{ marginBottom: 'var(--space-xs)' }}>Leaderboard</h1>
          <p className="text-secondary">Global ranking by portfolio return.</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 16px', background: 'var(--accent-amber-dim)', borderRadius: 'var(--radius-full)', color: 'var(--accent-amber)', fontWeight: 600 }}>
          <Award size={20} /> Current Rank: {myRank ? `#${myRank}` : 'Unranked'}
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
            {leaderboard.length === 0 ? (
              <tr>
                <td colSpan={3} className="text-center text-muted" style={{ padding: 'var(--space-lg)' }}>
                  No data available
                </td>
              </tr>
            ) : (
              leaderboard.map((entry) => {
                const isProfit = entry.total_return >= 0;
                const isMe = entry.user_id === user?.id;
                return (
                  <tr key={entry.user_id} style={isMe ? { background: 'var(--accent-blue-dim)' } : {}}>
                    <td style={{ textAlign: 'center', fontWeight: 700, fontSize: '1.2rem', color: entry.rank <= 3 ? 'var(--accent-amber)' : 'var(--text-secondary)' }}>
                      #{entry.rank}
                    </td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{ width: 40, height: 40, borderRadius: '50%', background: 'var(--bg-tertiary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 600 }}>
                          {entry.username.substring(0, 2).toUpperCase()}
                        </div>
                        <div style={{ fontWeight: isMe ? 700 : 500, color: isMe ? 'var(--accent-blue)' : 'var(--text-primary)' }}>
                          {entry.username}
                          {isMe && <Badge className="ml-2" style={{ marginLeft: 8 }} variant="info">You</Badge>}
                        </div>
                      </div>
                    </td>
                    <td className="text-right">
                      <Badge variant={isProfit ? 'success' : 'danger'}>
                        {isProfit ? '+' : ''}{entry.total_return.toFixed(2)}%
                      </Badge>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </Card>
    </div>
  );
};
