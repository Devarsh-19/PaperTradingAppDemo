import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Activity, Trash2, Plus } from 'lucide-react';
import { watchlistApi } from '../api/watchlist';
import { marketApi } from '../api/market';
import { Button } from '../components/ui/Button';

export const WatchlistPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [watchlistId, setWatchlistId] = useState<string | null>(null);
  const [items, setItems] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [newSymbol, setNewSymbol] = useState('');

  const fetchWatchlist = async () => {
    try {
      setLoading(true);
      const lists = await watchlistApi.getAll();
      if (lists && lists.length > 0) {
        const defaultList = lists[0];
        setWatchlistId(defaultList.id);
        
        // Fetch quotes for the symbols
        if (defaultList.symbols && defaultList.symbols.length > 0) {
          const quotesResponse = await marketApi.getBatchQuotes(defaultList.symbols.map((s: any) => s.symbol));
          const itemsWithQuotes = defaultList.symbols.map((item: any) => {
            const quote = quotesResponse.quotes ? quotesResponse.quotes.find((q: any) => q.symbol === item.symbol) : null;
            return {
              ...item,
              price: quote?.price || 0,
              change: quote?.change || 0,
              changePct: quote?.change_percent || 0,
              name: item.symbol // Yahoo finance may not give company name easily here, just use symbol
            };
          });
          setItems(itemsWithQuotes);
        } else {
          setItems([]);
        }
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load watchlist');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWatchlist();
  }, []);

  const handleRemove = async (symbol: string) => {
    if (!watchlistId) return;
    try {
      await watchlistApi.removeSymbol(watchlistId, symbol);
      fetchWatchlist();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to remove symbol');
    }
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!watchlistId || !newSymbol.trim()) return;
    
    try {
      await watchlistApi.addSymbol(watchlistId, newSymbol.trim().toUpperCase());
      setNewSymbol('');
      fetchWatchlist();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to add symbol');
    }
  };

  if (loading && items.length === 0) {
    return <div className="page-container"><div className="skeleton" style={{ height: '400px' }} /></div>;
  }

  if (error) {
    return <div className="page-container text-red">{error}</div>;
  }

  return (
    <div className="page-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
        <div>
          <h1 className="page-title" style={{ marginBottom: 'var(--space-xs)' }}>Watchlist</h1>
          <p className="text-secondary">Keep an eye on potential opportunities.</p>
        </div>
        <form onSubmit={handleAdd} style={{ display: 'flex', gap: '8px' }}>
          <input 
            type="text" 
            placeholder="Add symbol..." 
            className="input-field" 
            style={{ width: '150px', padding: '0.5rem 1rem' }}
            value={newSymbol}
            onChange={(e) => setNewSymbol(e.target.value)}
          />
          <Button type="submit" size="sm">
            <Plus size={16} style={{ marginRight: 4 }} /> Add
          </Button>
        </form>
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
            {items.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-center text-muted" style={{ padding: 'var(--space-lg)' }}>
                  Your watchlist is empty
                </td>
              </tr>
            ) : (
              items.map((item) => {
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
                      <button className="icon-btn text-muted" style={{ padding: 4 }} onClick={() => handleRemove(item.symbol)}>
                        <Trash2 size={16} />
                      </button>
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
